"""Run the CLI against real small CMake/CTest suites (no tool mocks)."""
import json
from pathlib import Path
import subprocess
import sys

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/run_host_tests.py'


def run(root, *args):
    return subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), *args],
                          capture_output=True, text=True)


def test_discovery_preserves_all_migrated_repository_suites():
    import importlib.util
    root = SCRIPT.parents[1]
    spec = importlib.util.spec_from_file_location('host_runner', SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Baseline 00580fc's 19 suites, mapped to the new layout. No Git history
    # dependency: CI deliberately uses a shallow checkout.
    expected = {
        f'bsp/watche_robot/watcher_hw_{name}/test_support/host'
        for name in ('core', 'body', 'audio', 'camera', 'display')
    } | {
        f'components/{name}/test_support/host'
        for name in ('mcu_link', 'hx_media_protocol', 'esp_lvgl_port',
                     'mcu_led_service', 'mcu_sensor_service', 'sscma_client',
                     'hx_ptl_protocol', 'motion_arbiter', 'mcu_motion_service',
                     'esp_codec_dev', 'watcher_hx_ptl')
    } | {'components/mcu_link/test_support/uart_host',
         'examples/hardware_check/test_support/host',
         'examples/common/test_support/host'}
    assert len(expected) == 19
    assert {p.relative_to(root).as_posix() for p in module.discover(root)} == expected


def test_zero_suites_is_failure_with_json_report(tmp_path):
    report = tmp_path / 'result.json'
    result = run(tmp_path, '--report', str(report))
    assert result.returncode == 1
    data = json.loads(report.read_text(encoding='utf-8'))
    assert data['status'] == 'failed'
    assert 'No host suites' in data['error']


def make_suite(root, name='components/nested/test_support/host', *, tests=True, fail=False):
    source = root / name
    source.mkdir(parents=True)
    (source / 'main.c').write_text('int main(void) { return ' + ('1' if fail else '0') + '; }\n')
    (source / 'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.20)
project(real_runner_test C)
enable_testing()
add_executable(real_test main.c)
''' + ('add_test(NAME real_test COMMAND real_test)\n' if tests else ''))
    return source


def test_real_suites_debug_release_and_versions(tmp_path):
    make_suite(tmp_path)
    make_suite(tmp_path, 'examples/demo/test_support/uart_host')
    (tmp_path / 'components/no-suite').mkdir()
    for config in ('Debug', 'Release'):
        report = tmp_path / f'{config}.json'
        result = run(tmp_path, '--config', config, '--report', str(report))
        assert result.returncode == 0, result.stdout + result.stderr
        data = json.loads(report.read_text(encoding='utf-8'))
        assert data['status'] == 'passed'
        assert len(data['suites']) == 2
        assert data['versions']['cmake'].startswith('cmake version ')
        assert data['versions']['python']
        for suite in data['suites']:
            assert suite['status'] == 'passed'
            assert suite['tests'] == 1
            assert config in suite['build_dir']
            assert suite['compiler']['CMAKE_C_COMPILER_VERSION']
            assert Path(suite['log']).is_file()


def test_ctest_zero_tests_is_a_failure(tmp_path):
    make_suite(tmp_path, tests=False)
    report = tmp_path / 'report.json'
    result = run(tmp_path, '--report', str(report))
    assert result.returncode == 1
    data = json.loads(report.read_text(encoding='utf-8'))
    assert data['suites'][0]['status'] == 'failed'
    assert 'zero tests' in data['suites'][0]['error']


def test_failing_test_is_reported_and_remaining_suites_run(tmp_path):
    make_suite(tmp_path, fail=True)
    make_suite(tmp_path, 'examples/a/host')
    report = tmp_path / 'report.json'
    assert run(tmp_path, '--report', str(report)).returncode == 1
    data = json.loads(report.read_text(encoding='utf-8'))
    assert [suite['status'] for suite in data['suites']] == ['failed', 'passed']


def test_missing_real_dependency_is_explicit(tmp_path):
    source = make_suite(tmp_path)
    with (source / 'CMakeLists.txt').open('a') as stream:
        stream.write('\nset(LVGL_SOURCE_DIR "" CACHE PATH "real LVGL source")\n')
    report = tmp_path / 'report.json'
    assert run(tmp_path, '--report', str(report)).returncode == 1
    data = json.loads(report.read_text(encoding='utf-8'))
    assert 'LVGL_SOURCE_DIR' in data['error']
    assert 'missing' in data['error'].lower()
