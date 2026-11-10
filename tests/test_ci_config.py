from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_feature_branches_are_validated_once_through_pull_requests():
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text())
    triggers = workflow.get('on', workflow.get(True))
    assert triggers['push'] == {'branches': ['main']}, 'Avoid duplicate push + PR matrices on feature branches'
    assert 'pull_request' in triggers


def test_job_level_environment_uses_supported_github_contexts():
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text())
    for name, job in workflow['jobs'].items():
        assert '${{ runner.' not in str(job.get('env', {})), (
            f'{name}: runner context is unavailable in jobs.<job_id>.env and prevents all jobs from starting'
        )
