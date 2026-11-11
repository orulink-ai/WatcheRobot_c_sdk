"""Checkout byte stability must not depend on a contributor's Git configuration."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_autocrlf_checkout_preserves_source_hashes_and_binary_bytes(tmp_path):
    source = tmp_path / 'origin'
    source.mkdir()

    def git(*args, cwd=source):
        return subprocess.run(['git', *args], cwd=cwd, capture_output=True,
                              encoding='utf-8', check=True)

    git('init')
    git('config', 'core.autocrlf', 'false')
    git('config', 'user.email', 'fixture@example.invalid')
    git('config', 'user.name', 'Fixture')
    payload = b'/* imported source */\nint value;\n'
    binary = b'\x00\xff\r\n\x01\n'
    (source / 'actual.c').write_bytes(payload)
    (source / 'image.bin').write_bytes(binary)
    (source / 'README.md').write_bytes(b'# SDK\nFixture description.\n')
    entries = [{'destination': name, 'sha256': hashlib.sha256(data).hexdigest()}
               for name, data in [('actual.c', payload), ('image.bin', binary)]]
    (source / 'SOURCE.json').write_text(json.dumps({'files': entries}), encoding='utf-8')
    attributes = ROOT / '.gitattributes'
    if attributes.exists():
        (source / '.gitattributes').write_bytes(attributes.read_bytes())
    git('add', '.')
    git('commit', '-m', 'checkout fixture')
    checkout = tmp_path / 'checkout'
    git('clone', '--no-checkout', str(source), str(checkout))
    git('config', 'core.autocrlf', 'true', cwd=checkout)
    git('checkout', 'HEAD', cwd=checkout)
    result = subprocess.run([sys.executable, str(ROOT / 'tools/check_docs.py'),
                             '--root', str(checkout), '--check-source'],
                            capture_output=True, encoding='utf-8')
    assert result.returncode == 0, result.stdout + result.stderr
    assert (checkout / 'actual.c').read_bytes() == payload
    assert (checkout / 'image.bin').read_bytes() == binary
