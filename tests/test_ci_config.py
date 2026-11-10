from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_job_level_environment_uses_supported_github_contexts():
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text())
    for name, job in workflow['jobs'].items():
        assert '${{ runner.' not in str(job.get('env', {})), (
            f'{name}: runner context is unavailable in jobs.<job_id>.env and prevents all jobs from starting'
        )
