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


def test_release_tree_has_closed_real_components(tmp_path):
    output = tmp_path / "release"
    run = generate(output)
    assert run.returncode == 0, run.stdout + run.stderr
    components = output / "components"
    names = {p.name for p in components.iterdir()}
    assert "watcher_hw_body" in names and "esp_codec_dev" in names
    for component in components.iterdir():
        assert (component / "CMakeLists.txt").is_file()
        manifest = yaml.safe_load((component / "idf_component.yml").read_text())
        assert manifest["version"] == "0.1.0-preview.1"
        assert manifest["targets"] == ["esp32s3"]
        for name, requirement in manifest["dependencies"].items():
            assert "path" not in requirement and "override_path" not in requirement
            if name.startswith("preview_test/"):
                assert name.split("/")[1] in names
                assert requirement["version"] == "==0.1.0-preview.1"
    report = json.loads((output / "release.json").read_text())
    assert report["source_repository"] == "https://github.com/orulink-ai/WatcheRobot_c_sdk"
    assert report["files"]
    assert not list(components.rglob("test_support"))
    codec = components / "esp_codec_dev"
    assert (codec / "device/zl38063/LICENSE.txt").is_file()
    assert "espressif__esp_codec_dev" not in (components / "hal_audio/CMakeLists.txt").read_text()
    assert (output / "consumer/main/main.c").is_file()


def test_real_compote_packages_and_consumer_are_closed(tmp_path):
    compote = shutil.which("compote")
    if not compote:
        pytest.fail("compote required: install packaging/requirements.txt and put its bin on PATH")
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


def test_release_patch_is_self_contained_and_final_hashes_match(tmp_path):
    import hashlib
    output = tmp_path / "release"
    run = generate(output)
    assert run.returncode == 0, run.stdout + run.stderr
    component = output / "components/sensecap-watcher"
    patch = (component / "patches.cmake").read_text()
    assert "../../scripts" not in patch
    assert "_official_project" not in patch
    assert "esp_lcd_panel_io_rx_param(tp->io, -1, data_p, len)" in patch
    report = json.loads((output / "release.json").read_text())
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
    assert marker.read_text() == "keep"
