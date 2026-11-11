"""The managed dependency fix must survive clean builds and reject drift."""
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BSP = ROOT / 'bsp/watche_robot/sensecap-watcher'
CMAKE = shutil.which('cmake')
pytestmark = pytest.mark.skipif(not CMAKE, reason='cmake required')


def patch(path):
    return subprocess.run([CMAKE, f'-DKNOB_SOURCE={path}', '-P',
                           str(BSP / 'patch_knob_cleanup.cmake')], capture_output=True)


def test_patch_repeatable(tmp_path):
    source = tmp_path / 'iot_knob.c'
    shutil.copyfile(BSP / 'test_support/host/iot_knob_0_1_4.fixture', source)
    assert patch(source).returncode == 0
    fixed = source.read_bytes()
    assert b'(int)(knob->usr_data)' not in fixed
    assert b'(intptr_t)knob->encoder_a' in fixed
    assert b'(intptr_t)knob->encoder_b' in fixed
    assert patch(source).returncode == 0
    assert source.read_bytes() == fixed


def test_unknown_source_is_unchanged(tmp_path):
    source = tmp_path / 'iot_knob.c'
    original = (BSP / 'test_support/host/iot_knob_0_1_4.fixture').read_bytes()
    original = original.replace(b'(int)(knob->usr_data)', b'unknown_gpio')
    source.write_bytes(original)
    assert patch(source).returncode != 0
    assert source.read_bytes() == original
