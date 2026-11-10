from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_ci_installs_relocated_requirements_without_changing_matrix():
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8'))
    jobs = workflow['jobs']
    for name in ('python-and-docs', 'package-validation'):
        commands = '\n'.join(step.get('run', '') for step in jobs[name]['steps'])
        assert '-r tools/packaging/requirements.txt' in commands
        assert '-r packaging/requirements.txt' not in commands
    assert jobs['host']['strategy']['matrix'] == {
        'os': ['ubuntu-latest', 'windows-latest'], 'config': ['Debug', 'Release']}
    assert jobs['idf-examples']['strategy']['matrix']['example'] == ['body', 'head', 'robot', 'hardware_check']
    assert set(jobs) == {'python-and-docs', 'host', 'idf-examples', 'package-validation'}


def test_feature_branches_are_validated_once_through_pull_requests():
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8'))
    triggers = workflow.get('on', workflow.get(True))
    assert triggers['push'] == {'branches': ['main']}, 'Avoid duplicate push + PR matrices on feature branches'
    assert 'pull_request' in triggers


def test_container_packaging_trusts_only_the_checked_out_workspace():
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8'))
    setup = workflow['jobs']['package-validation']['steps'][1]['run']
    assert 'git config --global --add safe.directory "$GITHUB_WORKSPACE"' in setup
    assert 'safe.directory "*"' not in setup


def test_job_level_environment_uses_supported_github_contexts():
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8'))
    for name, job in workflow['jobs'].items():
        assert '${{ runner.' not in str(job.get('env', {})), (
            f'{name}: runner context is unavailable in jobs.<job_id>.env and prevents all jobs from starting'
        )


def test_validator_matrix_covers_windows_native_encoding_and_checkout():
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8'))
    job = workflow['jobs']['python-and-docs']
    assert job['runs-on'] == '${{ matrix.os }}'
    assert job['strategy']['matrix']['os'] == ['ubuntu-latest', 'windows-latest']
    commands = '\n'.join(step.get('run', '') for step in job['steps'])
    assert 'python -m pytest tests -v' in commands
    assert 'python tools/check_docs.py --check-source' in commands
    assert 'git config --global core.autocrlf true' in commands
    assert job.get('env', {}).get('PYTHONUTF8') != '1', 'Do not mask native locale decoding bugs'
