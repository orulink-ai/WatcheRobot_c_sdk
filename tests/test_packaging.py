"""Local Registry preparation: never upload or depend on a private checkout."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/package_components.py"


def generate(output, *args):
    return subprocess.run([sys.executable, str(SCRIPT), "--namespace", "preview_test",
                           "--output", str(output), *args], capture_output=True, text=True)


def test_migrated_component_roots_preserve_release_contract(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location('migrated_packager', SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    names = {
        'watcher_hw_core', 'watcher_hw_body', 'watcher_hw_audio',
        'watcher_hw_camera', 'watcher_hw_display', 'mcu_link', 'mcu_runtime',
        'mcu_motion_service', 'mcu_led_service', 'mcu_sensor_service',
        'mcu_power_service', 'motion_arbiter', 'watcher_input_router',
        'hal_audio', 'hal_camera', 'esp_codec_dev', 'esp_lvgl_port',
        'sensecap-watcher', 'sscma_client', 'esp_io_expander_pca95xx_16bit',
        'watcher_hx_ptl', 'hx_media_protocol', 'hx_ptl_protocol',
        'jpeg_integrity', 'media_lib_sal',
    }
    assert set(module.LOCAL) == names
    board = {'watcher_hw_' + n for n in ('core', 'body', 'audio', 'camera', 'display')} | {'sensecap-watcher'}
    for name, (source, _) in module.LOCAL.items():
        assert source == ('bsp/watche_robot/' if name in board else 'components/') + name
    output = tmp_path / 'migrated'
    report = module.prepare(output, 'preview_test', module.VERSION, 'HEAD')
    assert report['version'] == '0.1.0-preview.1'
    assert set(report['components']) == names
    for name in board - {'sensecap-watcher'}:
        header = f'include/{name}.h'
        original = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'HEAD:{module.LOCAL[name][0]}/{header}'])
        assert (output / 'components' / name / header).read_bytes() == original
        assert f'#include "{name}.h"' in (output / 'consumer/main/main.c').read_text(encoding='utf-8')


def test_release_tree_has_closed_real_components(tmp_path):
    output = tmp_path / "release"
    run = generate(output)
    assert run.returncode == 0, run.stdout + run.stderr
    components = output / "components"
    names = {p.name for p in components.iterdir()}
    assert "watcher_hw_body" in names and "esp_codec_dev" in names
    for component in components.iterdir():
        assert (component / "CMakeLists.txt").is_file()
        manifest = yaml.safe_load((component / "idf_component.yml").read_text(encoding='utf-8'))
        assert manifest["version"] == "0.1.0-preview.1"
        assert manifest["targets"] == ["esp32s3"]
        for name, requirement in manifest["dependencies"].items():
            assert "path" not in requirement and "override_path" not in requirement
            if name.startswith("preview_test/"):
                assert name.split("/")[1] in names
                assert requirement["version"] == "==0.1.0-preview.1"
    report = json.loads((output / "release.json").read_text(encoding='utf-8'))
    assert report["source_repository"] == "https://github.com/orulink-ai/WatcheRobot_c_sdk"
    assert report["files"]
    assert not list(components.rglob("test_support"))
    codec = components / "esp_codec_dev"
    assert (codec / "device/zl38063/LICENSE.txt").is_file()
    assert "espressif__esp_codec_dev" not in (components / "hal_audio/CMakeLists.txt").read_text(encoding='utf-8')
    assert (output / "consumer/main/main.c").is_file()


def test_real_compote_packages_and_consumer_are_closed(tmp_path):
    compote = shutil.which("compote")
    if not compote:
        pytest.fail("compote required: install tools/packaging/requirements.txt and put its bin on PATH")
    output = tmp_path / "packed"
    run = generate(output, "--pack", "--compote", compote)
    assert run.returncode == 0, run.stdout + run.stderr
    archives = list((output / "archives").glob("*.tgz"))
    assert len(archives) == 25
    for archive in archives:
        with tarfile.open(archive) as tf:
            assert "CMakeLists.txt" in {str(Path(n)) for n in tf.getnames()}
            manifests = [n for n in tf.getnames() if str(Path(n)) == "idf_component.yml"]
            assert len(manifests) == 1
            stream = tf.extractfile(manifests[0])
            assert stream is not None
            manifest = yaml.safe_load(stream.read())
            assert all("path" not in d and "override_path" not in d for d in manifest["dependencies"].values())
    assert len(list((output / "consumer/components").iterdir())) == len(archives)


@pytest.mark.parametrize("windows_paths", [False, True], ids=["native", "windows-paths"])
def test_every_component_provenance_is_complete_and_matches_real_archive(tmp_path, windows_paths):
    import hashlib
    import importlib.util
    from pathlib import PureWindowsPath

    spec = importlib.util.spec_from_file_location('provenance_packager', SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class WindowsSerializationPath(type(tmp_path)):
        """Use real host I/O but Windows semantics at the serialization boundary.

        relative_to() supplies genuine PureWindowsPath objects, whose str()
        uses backslashes. Joining persisted strings accepts backslashes just
        as Windows does, so Linux reaches provenance filtering, not an I/O error.
        """
        def relative_to(self, *args):
            return PureWindowsPath(super().relative_to(*args).as_posix())

        def __truediv__(self, other):
            if isinstance(other, str):
                other = other.replace('\\', '/')
            return super().__truediv__(other)

    output = tmp_path / 'provenance'
    prepare_output = WindowsSerializationPath(output) if windows_paths else output
    report = module.prepare(prepare_output, 'preview_test', module.VERSION, 'HEAD')
    persisted = json.loads((output / 'release.json').read_text(encoding='utf-8'))
    assert persisted == report
    tracked = subprocess.check_output(
        ['git', '-C', str(ROOT), 'ls-tree', '-r', '--name-only', report['source_commit']],
        text=True,
    ).splitlines()
    all_records = []
    for name, (prefix, _) in module.LOCAL.items():
        provenance = json.loads((output / 'components' / name / 'RELEASE_PROVENANCE.json').read_text(encoding='utf-8'))
        records = provenance['files']
        assert records, f'{name}: component provenance must not be empty'
        expected_sources = set()
        for source in tracked:
            if not source.startswith(prefix + '/'):
                continue
            relative = Path(source[len(prefix) + 1:])
            if (module.BLOCKED.intersection(relative.parts)
                    or relative.suffix.lower() in module.BAD_SUFFIXES
                    or relative.name.startswith('.env')
                    or relative.as_posix() == 'idf_component.yml'):
                continue
            expected_sources.add(source)
        assert {r['source'] for r in records} == expected_sources, name
        assert len(records) == len(expected_sources), name
        for record in records:
            assert record['destination'] == f"components/{name}/" + record['source'][len(prefix) + 1:]
            assert '\\' not in record['destination']
        all_records.extend(records)
    assert sorted(all_records, key=lambda r: r['source']) == sorted(report['files'], key=lambda r: r['source'])
    expected_hashes = {
        p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in output.rglob('*') if p.is_file() and p != output / 'release.json'
    }
    assert report['output_hashes'] == expected_hashes

    compote = shutil.which('compote')
    assert compote, 'compote required: install tools/packaging/requirements.txt'
    module.pack(output, 'preview_test', compote)
    archives = list((output / 'archives').glob('*.tgz'))
    assert len(archives) == len(module.LOCAL) == 25
    for name in module.LOCAL:
        archive = output / 'archives' / f'{name}_{module.VERSION}.tgz'
        with tarfile.open(archive) as tf:
            members = {Path(member.name).as_posix(): member for member in tf.getmembers() if member.isfile()}
            provenance_stream = tf.extractfile(members['RELEASE_PROVENANCE.json'])
            assert provenance_stream is not None
            archived = json.load(provenance_stream)
            staged = json.loads((output / 'components' / name / 'RELEASE_PROVENANCE.json').read_text(encoding='utf-8'))
            assert archived == staged
            for record in archived['files']:
                relative = record['destination'].removeprefix(f'components/{name}/')
                stream = tf.extractfile(members[relative])
                assert stream is not None
                data = stream.read()
                assert hashlib.sha256(data).hexdigest() == record['sha256']
                assert data == (output / record['destination']).read_bytes()
                assert data == (output / 'consumer/components' / f'preview_test__{name}' / relative).read_bytes()


def test_release_patch_is_self_contained_and_final_hashes_match(tmp_path):
    import hashlib
    output = tmp_path / "release"
    run = generate(output)
    assert run.returncode == 0, run.stdout + run.stderr
    component = output / "components/sensecap-watcher"
    patch = (component / "patches.cmake").read_text(encoding='utf-8')
    assert "../../scripts" not in patch
    assert "_official_project" not in patch
    assert "esp_lcd_panel_io_rx_param(tp->io, -1, data_p, len)" in patch
    report = json.loads((output / "release.json").read_text(encoding='utf-8'))
    for record in report["files"]:
        path = output / record["destination"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]


@pytest.mark.parametrize("args", [["--version", "1.0.0"], ["--namespace", "espressif"]])
def test_rejects_nonpreview_or_upstream_namespace(tmp_path, args):
    output = tmp_path / "unsafe"
    result = generate(output, *args)
    assert result.returncode != 0
    assert not output.exists()


def test_refuses_existing_output(tmp_path):
    output = tmp_path / "existing"
    output.mkdir()
    marker = output / "do-not-delete"
    marker.write_text("keep")
    run = generate(output)
    assert run.returncode != 0
    assert marker.read_text(encoding='utf-8') == "keep"
