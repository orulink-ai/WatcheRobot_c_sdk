"""Offline documentation validator regression tests."""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/check_docs.py'


def check(root, *args):
    return subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), *args],
                          capture_output=True, text=True)


def test_missing_link_is_rejected_with_diagnostic(tmp_path):
    (tmp_path / 'README.md').write_text('# SDK\n[missing](docs/absent.md)\n')
    result = check(tmp_path)
    assert result.returncode == 1
    assert 'missing local target: docs/absent.md' in result.stdout


def test_nested_markdown_anchors_references_code_fences_and_source_lines(tmp_path):
    docs = tmp_path / 'docs/deep'
    docs.mkdir(parents=True)
    (tmp_path / 'source.c').write_text('int main(void) { return 0; }\n')
    (docs / 'a.md').write_text('''# Hello, 世界!
# Duplicate
# Duplicate
[a](#hello-世界)
[b](#duplicate-1)
[source](../../source.c#L1-L2)
[ref][target]
[target]: <../../source.c#L1>
~~~md
[ignored](not-there.md)
~~~
```markdown
[also ignored](missing.md)
```
''', encoding='utf-8')
    assert check(tmp_path).returncode == 0
    with (docs / 'a.md').open('a', encoding='utf-8') as stream:
        stream.write('\n[broken](#absent)\n')
    result = check(tmp_path)
    assert result.returncode == 1
    assert 'missing anchor: #absent' in result.stdout


def test_reference_links_and_inline_source_paths_are_checked(tmp_path):
    (tmp_path / 'README.md').write_text('''# SDK
[bad][missing]
[missing]: docs/no.md
Source: `components/no/include/missing.h`.
''')
    result = check(tmp_path)
    assert result.returncode == 1
    assert 'missing local target: docs/no.md' in result.stdout
    assert 'missing source path: components/no/include/missing.h' in result.stdout


def test_component_and_example_readmes_require_descriptive_body(tmp_path):
    for directory in ['components/sdk/foo', 'examples/hello']:
        folder = tmp_path / directory
        folder.mkdir(parents=True)
        (folder / 'CMakeLists.txt').write_text('project(foo)')
        (folder / 'README.md').write_text('# Foo\n')
    result = check(tmp_path)
    assert result.returncode == 1
    assert result.stdout.count('missing or empty description') == 2


def test_no_markdown_is_a_failure(tmp_path):
    assert check(tmp_path).returncode == 1


def test_source_hash_verification_uses_destination_current_hash(tmp_path):
    import hashlib
    import json
    payload = b'transformed current source\n'
    (tmp_path / 'README.md').write_text('# SDK\nDescription\n')
    (tmp_path / 'actual.c').write_bytes(payload)
    (tmp_path / 'SOURCE.json').write_text(json.dumps({'files': [{
        'source': 'old.c', 'destination': 'actual.c',
        'source_sha256': '0' * 64, 'sha256': hashlib.sha256(payload).hexdigest(),
    }]}))
    assert check(tmp_path, '--check-source').returncode == 0
    (tmp_path / 'actual.c').write_text('tampered')
    result = check(tmp_path, '--check-source')
    assert result.returncode == 1
    assert 'SOURCE hash mismatch: actual.c' in result.stdout


def test_external_links_are_offline_and_escaped_paths_are_rejected(tmp_path):
    (tmp_path / 'README.md').write_text('# SDK\n[x](https://invalid.example/not-real#heading)\n')
    assert check(tmp_path).returncode == 0
    (tmp_path / 'README.md').write_text('# SDK\n[escape](../outside.md)\n')
    assert 'escapes repository' in check(tmp_path).stdout


def test_build_artifact_literals_are_not_source_but_artifact_links_must_exist(tmp_path):
    (tmp_path / 'README.md').write_text('# SDK\nOutput: `examples/robot/build/robot.bin`.\n')
    assert check(tmp_path).returncode == 0
    (tmp_path / 'README.md').write_text('# SDK\n[download](examples/robot/build/robot.bin)\n')
    assert check(tmp_path).returncode == 1


def test_source_ledger_empty_or_traversal_is_rejected(tmp_path):
    import json
    (tmp_path / 'README.md').write_text('# SDK\nDescription\n')
    for files in ([], [{'destination': '../outside', 'sha256': '0' * 64}]):
        (tmp_path / 'SOURCE.json').write_text(json.dumps({'files': files}))
        assert check(tmp_path, '--check-source').returncode == 1
