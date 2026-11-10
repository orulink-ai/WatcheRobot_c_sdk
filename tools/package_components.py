#!/usr/bin/env python3
"""Prepare real, coordinated ESP-IDF component packages, without uploading.

Source bytes come only from tracked files at an immutable public-repository Git
revision. The source checkout is never changed. Requires PyYAML (install packaging/requirements.txt); use compote 2.5.2 for --pack.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import tarfile
from urllib.parse import quote, unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/orulink-ai/WatcheRobot_c_sdk"
VERSION = "0.1.0-preview.1"
# Explicit public component allowlist. Never discover managed_components or
# export another repository. Edges include public header and CMake requirements.
LOCAL = {
    "watcher_hw_core": ("components/sdk/watcher_hw_core", []),
    "watcher_hw_body": ("components/sdk/watcher_hw_body", ["watcher_hw_core", "mcu_runtime", "mcu_motion_service", "mcu_led_service", "mcu_sensor_service", "motion_arbiter"]),
    "watcher_hw_audio": ("components/sdk/watcher_hw_audio", ["watcher_hw_core", "hal_audio"]),
    "watcher_hw_camera": ("components/sdk/watcher_hw_camera", ["watcher_hw_core", "hal_camera"]),
    "watcher_hw_display": ("components/sdk/watcher_hw_display", ["watcher_hw_core", "sensecap-watcher", "esp_lvgl_port"]),
    "mcu_link": ("components/protocols/mcu_link", []),
    "mcu_runtime": ("components/services/mcu_runtime", ["mcu_link", "mcu_motion_service", "mcu_led_service", "mcu_sensor_service", "mcu_power_service"]),
    "mcu_motion_service": ("components/services/mcu_motion_service", ["mcu_link", "motion_arbiter"]),
    "mcu_led_service": ("components/services/mcu_led_service", ["mcu_link"]),
    "mcu_sensor_service": ("components/services/mcu_sensor_service", ["mcu_link"]),
    "mcu_power_service": ("components/services/mcu_power_service", ["mcu_link"]),
    "motion_arbiter": ("components/services/motion_arbiter", []),
    "watcher_input_router": ("components/services/watcher_input_router", []),
    "hal_audio": ("components/hal/hal_audio", ["esp_codec_dev", "sensecap-watcher", "media_lib_sal"]),
    "hal_camera": ("components/hal/hal_camera", ["sensecap-watcher", "sscma_client", "watcher_hx_ptl", "hx_media_protocol", "hx_ptl_protocol", "jpeg_integrity"]),
    "esp_codec_dev": ("components/esp_codec_dev", []),
    "esp_lvgl_port": ("components/esp_lvgl_port", ["watcher_input_router"]),
    "sensecap-watcher": ("components/sensecap-watcher", ["esp_io_expander_pca95xx_16bit", "esp_lvgl_port", "sscma_client", "esp_codec_dev"]),
    "sscma_client": ("components/sscma_client", []),
    "esp_io_expander_pca95xx_16bit": ("components/esp_io_expander_pca95xx_16bit", []),
    "watcher_hx_ptl": ("components/watcher_hx_ptl", ["hx_media_protocol", "hx_ptl_protocol", "sensecap-watcher"]),
    "hx_media_protocol": ("components/hx_media_protocol", []),
    "hx_ptl_protocol": ("components/hx_ptl_protocol", ["hx_media_protocol"]),
    "jpeg_integrity": ("components/jpeg_integrity", []),
    "media_lib_sal": ("components/media_lib_sal", []),
}
PINS = {"lvgl/lvgl": "8.4.0", "espressif/esp_audio_codec": "2.4.1",
        "espressif/cjson": "1.7.19", "espressif/esp_io_expander": "1.0.1",
        "espressif/esp_lcd_spd2010": "1.0.1", "espressif/esp_lcd_touch_spd2010": "0.0.1",
        "espressif/esp_lcd_touch": "1.1.1", "espressif/cmake_utilities": "0.5.3",
        "espressif/led_strip": "2.5.4", "espressif/button": "3.2.3", "espressif/knob": "0.1.4"}
EXTERNAL = {
    "watcher_hw_display": ["lvgl/lvgl"], "hal_audio": ["espressif/esp_audio_codec"],
    "esp_lvgl_port": ["lvgl/lvgl", "espressif/button", "espressif/knob"],
    "sensecap-watcher": ["lvgl/lvgl", "espressif/esp_lcd_spd2010", "espressif/esp_lcd_touch_spd2010", "espressif/esp_lcd_touch", "espressif/cmake_utilities", "espressif/esp_io_expander", "espressif/led_strip", "espressif/button", "espressif/knob"],
    "sscma_client": ["espressif/cjson", "espressif/esp_io_expander"],
    "esp_io_expander_pca95xx_16bit": ["espressif/esp_io_expander"],
    "watcher_hx_ptl": ["espressif/esp_io_expander"],
}
BLOCKED = {"build", "managed_components", "test_support", ".git", "__pycache__", "dist", "node_modules"}
BAD_SUFFIXES = {".o", ".a", ".so", ".bin", ".elf", ".pyc", ".pem", ".key"}
SECRET = re.compile(rb"-----BEGIN (?:[A-Z ]*PRIVATE KEY)-----|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}")


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def write(path: Path, data: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.encode() if isinstance(data, str) else data)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def release_documentation(data: bytes, source: str, prefix: str, commit: str) -> bytes:
    """Keep component-local links; pin repository-external navigation to source."""
    def replace(match):
        target = match.group(2)
        url = urlsplit(target)
        if url.scheme or url.netloc or not url.path or target.startswith('#'):
            return match.group(0)
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(url.path)))
        if resolved == prefix or resolved.startswith(prefix + '/'):
            return match.group(0)
        if resolved.startswith('../') or resolved == '..':
            raise ValueError(f'documentation escapes public repository: {source}: {target}')
        suffix = ('?' + url.query if url.query else '') + ('#' + url.fragment if url.fragment else '')
        absolute = REPOSITORY + '/blob/' + commit + '/' + quote(resolved, safe='/') + suffix
        return match.group(1) + absolute + match.group(3)
    text = data.decode('utf-8')
    # Fenced examples remain literal examples, not links to rewrite.
    parts = re.split(r'(```[\s\S]*?```|~~~[\s\S]*?~~~)', text)
    return ''.join(part if index % 2 else re.sub(r'(!?\[[^\]]*\]\()([^\s)]+)([^)]*\))', replace, part)
                   for index, part in enumerate(parts)).encode('utf-8')


def prepare(output: Path, namespace: str, version: str, revision: str) -> dict:
    if not re.fullmatch(r"[a-z][a-z0-9_]{1,39}", namespace) or namespace in {"espressif", "lvgl"}:
        raise ValueError("use your explicitly authorized namespace (not an upstream namespace)")
    if not re.fullmatch(r"\d+\.\d+\.\d+-[a-zA-Z][a-zA-Z0-9.-]*", version):
        raise ValueError("local preparation requires an explicit prerelease version")
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError("output must be outside the source repository")
    if output.exists():
        raise ValueError("output must not exist; refusing to overwrite files")
    commit = git("rev-parse", "--verify", revision + "^{commit}").decode().strip()
    paths = git("ls-tree", "-r", "--name-only", commit).decode().splitlines()
    records = []
    output.mkdir(parents=True)
    for name, (prefix, dependencies) in LOCAL.items():
        component = output / "components" / name
        original_manifest = None
        original_manifest_sha256 = None
        for source in paths:
            if not source.startswith(prefix + "/"):
                continue
            relative = Path(source).relative_to(prefix)
            if BLOCKED.intersection(relative.parts) or relative.suffix.lower() in BAD_SUFFIXES or relative.name.startswith(".env"):
                continue
            # Git symlinks may otherwise escape the allowlist at consumption.
            mode = git("ls-tree", commit, "--", source).decode().split()[0]
            if mode != "100644" and mode != "100755":
                raise ValueError(f"non-regular tracked source: {source}")
            data = git("show", f"{commit}:{source}")
            if SECRET.search(data):
                raise ValueError(f"secret signature in public input: {source}")
            if relative.as_posix() == "idf_component.yml":
                original_manifest = yaml.safe_load(data)
                original_manifest_sha256 = digest(data)
                continue
            else:
                target = component / relative
            # Only this hard-coded legacy codec alias is changed. Source code
            # and all third-party licenses remain byte-for-byte identical.
            if relative.as_posix() == "patches.cmake" and name == "sensecap-watcher":
                # Keep only the already-public standalone patch behavior. In
                # installed components ../.. is the consumer, not the old app.
                text = data.decode().split("if(DEFINED PYTHON)", 1)[0]
                text = re.sub(r'get_filename_component\(_official_project[^\n]*\n', '', text)
                text = text.replace('if(NOT PROJECT_DIR STREQUAL _official_project)', 'if(TRUE)')
                data = text.encode()
            if relative.as_posix() == "CMakeLists.txt":
                data_out = data.replace(b"espressif__esp_codec_dev", f"{namespace}__esp_codec_dev".encode())
                # Keep camera flags aligned with the verified source build.
                # IDF 6 mbedTLS4 declares private-access compatibility itself;
                # forcing the macro to 1 causes a -Werror redefinition failure.
                data = data_out
            if relative.suffix.lower() == '.md':
                data = release_documentation(data, source, prefix, commit)
            write(target, data)
            records.append({"source": source, "destination": str(target.relative_to(output)),
                            "source_sha256": digest(git("show", f"{commit}:{source}")), "sha256": digest(data)})
        if not (component / "CMakeLists.txt").is_file():
            raise ValueError(f"missing component at public revision: {prefix}")
        # Preserve original metadata as inert JSON provenance, never as a
        # second active manifest carrying old wildcards or override_path.
        deps: dict[str, dict] = {"idf": {"version": "==6.0.2"}}
        deps.update({f"{namespace}/{n}": {"version": f"=={version}", "public": True} for n in dependencies})
        deps.update({n: {"version": "==" + PINS[n], "public": True} for n in EXTERNAL.get(name, [])})
        manifest = {"version": version, "description": f"WatcheRobot preview: {name} (coordinated local source)",
                    "url": REPOSITORY, "targets": ["esp32s3"], "dependencies": deps}
        write(component / "idf_component.yml", yaml.safe_dump(manifest, sort_keys=False))
        if not any("license" in p.name.lower() for p in component.iterdir()):
            write(component / "LICENSE", git("show", f"{commit}:LICENSE"))
        if not (component / "README.md").is_file() or not (component / "README.md").stat().st_size:
            write(component / "README.md", f"# {name}\n\nUnpublished coordinated SDK preview for ESP32-S3 / ESP-IDF 6.0.2.\nSee RELEASE_PROVENANCE.json for origin and local transformations.\nNo device or physical hardware acceptance is implied.\n")
        write(component / "RELEASE_PROVENANCE.json", json.dumps({
            "source_repository": REPOSITORY, "source_commit": commit, "source_path": prefix,
            "upstream_manifest": original_manifest, "upstream_manifest_sha256": original_manifest_sha256,
            "transformations": ["generated exact dependency manifest", "preserved local patched sources and license files", "legacy codec alias rewritten to selected namespace", "repository-external documentation links pinned to public source commit"],
            "files": [r for r in records if r["destination"].startswith(f"components/{name}/")]}, indent=2) + "\n")
    # Compatibility that previously lived only in examples/sdk.cmake. Scope
    # deferred changes to this consumer project; no global installed SDK edits.
    compatibility = '''\n# Generated release bridge for the pinned legacy third-party IDF6 drivers.\nfunction(watcher_release_idf6_links)\n  foreach(name button knob)\n    if(TARGET __idf_espressif__${name})\n      target_link_libraries(__idf_espressif__${name} PUBLIC idf::esp_driver_gpio)\n    endif()\n  endforeach()\n  if(TARGET __idf_espressif__led_strip)\n    target_link_libraries(__idf_espressif__led_strip PUBLIC idf::esp_driver_rmt idf::esp_driver_spi idf::esp_hal_gpspi idf::heap)\n  endif()\nendfunction()\ncmake_language(DEFER DIRECTORY "${CMAKE_SOURCE_DIR}" CALL watcher_release_idf6_links)\n'''
    board = output / "components/sensecap-watcher/CMakeLists.txt"
    write(board, board.read_bytes() + compatibility.encode())
    # Finalize transformed-source hashes before serializing provenance.
    for record in records:
        record["sha256"] = digest((output / record["destination"]).read_bytes())
    for name in LOCAL:
        provenance_path = output / "components" / name / "RELEASE_PROVENANCE.json"
        provenance = json.loads(provenance_path.read_text())
        provenance["files"] = [r for r in records if r["destination"].startswith(f"components/{name}/")]
        provenance["transformations"].append("BSP standalone-only dependency patches and deferred IDF6 links")
        write(provenance_path, json.dumps(provenance, indent=2) + "\n")
    make_consumer(output, namespace)
    report = {"source_repository": REPOSITORY, "source_commit": commit, "namespace": namespace,
              "version": version, "publication": "NOT UPLOADED", "files": records,
              "components": {n: {"source": p, "local_dependencies": d, "external_dependencies": EXTERNAL.get(n, [])} for n, (p, d) in LOCAL.items()},
              "external_pins": PINS}
    # Hash the final generated tree too, including manifests, bridges, consumer.
    report["output_hashes"] = {str(p.relative_to(output)): digest(p.read_bytes()) for p in sorted(output.rglob("*")) if p.is_file()}
    write(output / "release.json", json.dumps(report, indent=2) + "\n")
    return report


def make_consumer(output: Path, namespace: str) -> None:
    consumer = output / "consumer"
    write(consumer / "CMakeLists.txt", 'cmake_minimum_required(VERSION 3.24)\nset(COMPONENTS main)\nset(IDF_TARGET esp32s3 CACHE STRING "")\ninclude($ENV{IDF_PATH}/tools/cmake/project.cmake)\nproject(watcher_registry_consumer)\n')
    modules = ["watcher_hw_" + n for n in ("core", "body", "audio", "camera", "display")]
    write(consumer / "main/CMakeLists.txt", 'idf_component_register(SRCS "main.c" INCLUDE_DIRS "." REQUIRES ' + ' '.join(f'{namespace}__{n}' for n in modules) + ')\n')
    write(consumer / "main/main.c", '\n'.join(f'#include "{n}.h"' for n in modules) + '\n\n/* Link/compile smoke only: no robot commands or hardware initialization. */\nvoid app_main(void) {}\n')
    write(consumer / "sdkconfig.defaults", 'CONFIG_SPIRAM=y\nCONFIG_SPIRAM_MODE_OCT=y\nCONFIG_FREERTOS_HZ=1000\nCONFIG_WATCHER_CAMERA_BACKEND_PTL=y\nCONFIG_LV_COLOR_DEPTH_16=y\nCONFIG_LV_COLOR_16_SWAP=y\nCONFIG_LV_FONT_MONTSERRAT_16=y\nCONFIG_LV_FONT_MONTSERRAT_20=y\nCONFIG_LV_FONT_MONTSERRAT_48=y\n')


def pack(output: Path, namespace: str, compote: str) -> None:
    """Exercise the real Component Manager packer, then consume its archives."""
    archives = output / "archives"
    archives.mkdir()
    for name in LOCAL:
        subprocess.run([compote, "component", "pack", "--project-dir", str(output / "components" / name),
                        "--name", name, "--dest-dir", str(archives)], check=True)
    consumer_components = output / "consumer/components"
    consumer_components.mkdir()
    # Extract ONLY actual compote output, never fall back to source directories.
    archive_records = {}
    for archive in sorted(archives.iterdir()):
        if not archive.is_file():
            continue
        archive_records[archive.name] = digest(archive.read_bytes())
        with tarfile.open(archive) as tf:
            members = tf.getmembers()
            manifests = [m for m in members if Path(m.name).name == "idf_component.yml"]
            if len(manifests) != 1:
                raise ValueError(f"not a component archive: {archive}")
            manifest_data = yaml.safe_load(tf.extractfile(manifests[0]).read())
            # compote 2.5.2 encodes name_version.tgz (no namespace).
            name = next((n for n in LOCAL if archive.name.startswith(f"{n}_") and archive.name[len(n) + 1].isdigit()), None)
            if name is None:
                raise ValueError(f"unexpected archive filename {archive.name}")
            destination = consumer_components / f"{namespace}__{name}"
            destination.mkdir()
            for m in members:
                if Path(m.name).is_absolute() or ".." in Path(m.name).parts or m.issym() or m.islnk():
                    raise ValueError(f"unsafe archive member {m.name}")
                if m.isdir():
                    continue
                if not m.isfile():
                    raise ValueError(f"unsupported archive member {m.name}")
                stream = tf.extractfile(m)
                assert stream is not None
                write(destination / m.name, stream.read())
            if manifest_data["dependencies"]["idf"]["version"] != "==6.0.2":
                raise ValueError("archive changed IDF pin")
    if len(archive_records) != len(LOCAL):
        raise ValueError("incomplete archive set")
    # Consumer-only overrides: all referenced paths are INSIDE this clean
    # project, never in distributable component manifests or original repo.
    overrides = {f"{namespace}/{n}": {"path": f"../components/{namespace}__{n}"} for n in LOCAL}
    write(output / "consumer/main/idf_component.yml", yaml.safe_dump({"dependencies": overrides}, sort_keys=False))
    write(output / "archives.sha256.json", json.dumps(archive_records, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", required=True, help="local rehearsal name; NOT proof of Registry authorization")
    parser.add_argument("--version", default=VERSION)
    parser.add_argument("--revision", default="HEAD", help="immutable public Git source revision (resolved to SHA)")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--pack", action="store_true", help="run real compote pack and build a consumer from archives")
    parser.add_argument("--compote", default="compote")
    args = parser.parse_args()
    try:
        report = prepare(args.output, args.namespace, args.version, args.revision)
        if args.pack:
            pack(args.output.resolve(), args.namespace, args.compote)
    except (ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"packaging failed: {exc}\n")
    print(json.dumps({"components": len(report["components"]), "output": str(args.output.resolve()), "uploaded": False}))


if __name__ == "__main__":
    main()
