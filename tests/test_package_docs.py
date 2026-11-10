from pathlib import Path
import importlib.util
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def test_release_readmes_do_not_require_parent_repository_files(tmp_path):
    spec = importlib.util.spec_from_file_location('sdk_package_docs', ROOT / 'tools/package_components.py')
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    out = tmp_path / 'release'
    module.prepare(out, 'preview_test', '0.1.0-preview.1', 'HEAD')
    for component in module.LOCAL:
        for readme in (out / 'components' / component).glob('README*.md'):
            for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)', readme.read_text()):
                url = urlsplit(target)
                if url.scheme or not url.path:
                    continue
                resolved = (readme.parent / url.path).resolve()
                assert resolved.is_relative_to(out / 'components' / component), (
                    f'Packaged README must not link outside the distributed component: {component}: {target}'
                )
