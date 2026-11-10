from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_ci_installs_relocated_requirements_without_changing_matrix():
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text())
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
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text())
    triggers = workflow.get('on', workflow.get(True))
    assert triggers['push'] == {'branches': ['main']}, 'Avoid duplicate push + PR matrices on feature branches'
    assert 'pull_request' in triggers


def test_container_packaging_trusts_only_the_checked_out_workspace():
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text())
    setup = workflow['jobs']['package-validation']['steps'][1]['run']
    assert 'git config --global --add safe.directory "$GITHUB_WORKSPACE"' in setup
    assert 'safe.directory "*"' not in setup


def test_job_level_environment_uses_supported_github_contexts():
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text())
    for name, job in workflow['jobs'].items():
        assert '${{ runner.' not in str(job.get('env', {})), (
            f'{name}: runner context is unavailable in jobs.<job_id>.env and prevents all jobs from starting'
        )
