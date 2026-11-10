# Registry packaging rehearsal (not published)

The SDK is **not published to ESP Component Registry**. A namespace supplied to
the tool is only a local dependency label, not proof that anyone controls it.
There are no component-page links, upload commands, tokens, staging uploads, or
namespace creation in this workflow. Source examples remain supported through
`examples/sdk.cmake`; packaging does not change their manifests or CMake files.

## Chosen distribution boundary

The five API directories are not independently self-contained components. Their
public headers and CMake requirements reach local services, protocols, a BSP,
and modified third-party code. Copying only these five directories, or zipping
the SDK root, would not produce a consumable Registry distribution.

Two options were assessed:

| Option | Benefits | Cost / decision |
| --- | --- | --- |
| Coordinated components | Preserve existing registrations, public includes, Kconfig, ownership, capability selection, and third-party boundaries | 25 release units must share one preview version; selected for local rehearsal |
| One aggregate hardware component | One upload/version | Requires rewriting many CMake registrations, public/private include visibility, Kconfig and source lists, codec aliases and conditional configuration. Would obscure local patches and be a broader production build refactor; not selected |

`tools/package_components.py` therefore generates **25 real ESP-IDF component
directories**, each with `CMakeLists.txt`, manifest, README, licenses, and
provenance. `--pack` invokes the actual Component Manager for every directory.
It does not implement its own SDK ZIP format. It intentionally does **not** add
source-tree manifests that could alter existing source builds.

All local packages use the selected `--namespace` and the same exact preview
version (default `0.1.0-preview.1`). Non-prerelease versions and upstream
`espressif` / `lvgl` namespaces are refused. Choose a namespace you control before
any future upload; `preview_test` in the examples below is an offline label only.

## Audited local dependency graph

The release tool's explicit `LOCAL` table is the machine-readable graph. All
local edges become exact versioned namespaced manifest dependencies. Dependencies
are conservatively public because several public headers re-export their types;
existing CMake `REQUIRES` / `PRIV_REQUIRES` remain intact.

| Component | Direct local release dependencies |
| --- | --- |
| watcher_hw_core | none |
| watcher_hw_body | core, mcu_runtime, mcu_motion_service, mcu_led_service, mcu_sensor_service, motion_arbiter |
| watcher_hw_audio | core, hal_audio |
| watcher_hw_camera | core, hal_camera |
| watcher_hw_display | core, sensecap-watcher, esp_lvgl_port |
| mcu_link | none |
| mcu_runtime | mcu_link, mcu_motion_service, mcu_led_service, mcu_sensor_service, mcu_power_service |
| mcu_motion_service | mcu_link, motion_arbiter |
| mcu_led_service | mcu_link |
| mcu_sensor_service | mcu_link |
| mcu_power_service | mcu_link |
| motion_arbiter | none |
| watcher_input_router | none |
| hal_audio | esp_codec_dev, sensecap-watcher, media_lib_sal |
| hal_camera | sensecap-watcher, sscma_client, watcher_hx_ptl, hx_media_protocol, hx_ptl_protocol, jpeg_integrity |
| esp_codec_dev | none |
| esp_lvgl_port | watcher_input_router |
| sensecap-watcher | esp_io_expander_pca95xx_16bit, esp_lvgl_port, sscma_client, esp_codec_dev |
| sscma_client | none |
| esp_io_expander_pca95xx_16bit | none |
| watcher_hx_ptl | hx_media_protocol, hx_ptl_protocol, sensecap-watcher |
| hx_media_protocol | none |
| hx_ptl_protocol | hx_media_protocol |
| jpeg_integrity | none |
| media_lib_sal | none |

Here `core` abbreviates `watcher_hw_core`. IDF facilities (FreeRTOS, esp_timer,
UART/I2C/SPI/I2S/GPIO drivers, LCD, FATFS, SPIFFS, mbedTLS, esp-tls, networking,
PSRAM/heap and related HALs) remain built-in requirements under **IDF ==6.0.2**.
Only ESP32-S3 is declared. This is not an expanded compatibility claim.

### External Registry pins

Existing BSP and example constraints are converted to exact versions; there is
no implicit upgrade to the newest upstream component:

| Dependency | Exact version |
| --- | --- |
| lvgl/lvgl | 8.4.0 |
| espressif/esp_audio_codec | 2.4.1 |
| espressif/cjson | 1.7.19 |
| espressif/esp_io_expander | 1.0.1 |
| espressif/esp_lcd_spd2010 | 1.0.1 |
| espressif/esp_lcd_touch_spd2010 | 0.0.1 |
| espressif/esp_lcd_touch | 1.1.1 |
| espressif/cmake_utilities | 0.5.3 |
| espressif/led_strip | 2.5.4 |
| espressif/button | 3.2.3 |
| espressif/knob | 0.1.4 |

`esp_jpeg 1.3.1` belongs to the head/robot/hardware-check application code,
not the five-API compile consumer; it is deliberately not imposed on every SDK
package. The clean consumer's generated dependency lock must still be inspected
after real IDF resolution: pack success is not evidence of a resolved complete
transitive external graph.

### Local patches and generated-only adaptations

- **esp_lvgl_port and esp_codec_dev are packaged from the public SDK Git tree**,
  never replaced by official current releases. Every distributed C/H source and
  pre-existing license is copied byte-for-byte. Nested ZL38063 licensing is kept.
- The old `espressif__esp_codec_dev` CMake requirement is rewritten only in the
  generated release copy to `<namespace>__esp_codec_dev` so the local patched
  codec remains selected.
- The BSP's existing standalone touch (`cmd -1`) and LED-strip heap include
  patches are retained in the generated copy of `patches.cmake`. The unreachable
  original application branch and its `../../scripts` calls are removed. Those
  scripts are outside the SDK package and must not be called from a consumer.
- The source example's IDF6 button/knob GPIO and LED-strip driver/HAL linkage
  bridge is carried by the generated BSP with a deferred CMake function; the
  consumer does not need the parent SDK's `sdk.cmake`.
- Camera compile flags stay aligned with the verified source build. A generated
  `MBEDTLS_DECLARE_PRIVATE_IDENTIFIERS=1` flag was removed after the clean IDF 6
  consumer exposed a redefinition against mbedTLS4's empty compatibility macro;
  the regression has a red/green automated test. No runtime source was changed.
- README navigation outside a component archive is rewritten to the immutable
  public repository revision; installed component docs never require a sibling
  SDK checkout. Component-internal links and upstream attribution are retained.
- These are **packaging CMake/manifest transformations**, not runtime C fixes.
  The independent IDF consumer build is the acceptance gate for them.

## Reproduce locally / CI entry

Run from this public SDK repository. Use an isolated Python environment:

```sh
python3 -m venv /tmp/watcher-package-tools
/tmp/watcher-package-tools/bin/python -m pip install -r packaging/requirements.txt
PATH=/tmp/watcher-package-tools/bin:$PATH \
  /tmp/watcher-package-tools/bin/python -m pytest tests/test_packaging.py -q

/tmp/watcher-package-tools/bin/python tools/package_components.py \
  --revision HEAD --namespace preview_test --version 0.1.0-preview.1 \
  --output /tmp/watcher-registry-rehearsal \
  --pack --compote /tmp/watcher-package-tools/bin/compote
```

`--output` must be a **new directory outside this repository**. The tool refuses
to overwrite an existing output, so select a different directory on repeat.
`--revision` is resolved to a commit SHA. Only files tracked in that exact public
Git revision are read, **not working-tree files or untracked additions**. Commit
approved public source changes before testing them as a release; the tool does
not stage, commit, push, fetch another repository or export private source.

Output layout:

```text
release.json                  source SHA, graph, pins, source/output hashes
components/<name>/            generated Registry-ready component directories
archives/<name>_<version>.tgz actual compote 2.5.2 archives (with --pack)
archives.sha256.json          SHA256 of each actual component archive
consumer/                     clean, source-independent compile/link project
consumer/components/<namespace>__<name>/  extracted actual archives
consumer/main/idf_component.yml           consumer-only local path overrides
```

Each component contains `RELEASE_PROVENANCE.json`, original public path/commit,
source hashes, transformation notices, and original manifest metadata/hash.
Original manifest metadata is inert JSON provenance, not another active manifest.
Release manifests contain **no `path` or `override_path` dependencies**. Consumer
local-path overrides are separate and point **inside the clean consumer project**;
they are not included in uploaded component archives. They permit offline local
package validation without pretending the unpublished names exist in Registry.

After loading **ESP-IDF 6.0.2** and its ESP32-S3 toolchain, the firmware CI step is:

```sh
# This project was assembled ONLY from actual compote output, not source dirs.
cd /tmp/watcher-registry-rehearsal/consumer
idf.py --version
idf.py set-target esp32s3
idf.py build
```

The consumer includes all five public headers and links their dependency graph.
`app_main` intentionally does nothing: no motor command, hardware initialization,
flash, serial port or paired-firmware operation is performed. It is a compilation
smoke test, not a usage example or hardware acceptance. It does not claim that
Registry `add-dependency` or `create-project-from-example` already works. Existing
full source examples are not embedded as misleading standalone Registry examples.

## Hygiene and validation boundaries

The exporter uses an explicit component prefix allowlist plus `git ls-tree` /
`git show` from one revision. It rejects tracked symlinks and known secret
signatures; excludes test_support, build, managed_components, .git, caches,
node_modules, dist, private-key suffixes and compiled artifacts; and preserves
existing licenses and in-source notices. This limited pattern scan does **not**
prove absence of every secret or replace human license review. The root Apache
license is copied only where no existing top-level license file exists; nested
third-party licenses are never overwritten. Downloaded upstream components are
resolved by IDF separately, not exported from a maintainer's managed_components.

Compote **2.5.2** provides `component pack` but **does not provide a `component
lint` command** (`No such command 'lint'`). Validation here means real compote
manifest/package validation plus automated closure, archive contents, provenance
hash and consumer tests; no nonexistent lint run is claimed. Packaging is not
compilation, publication, account authorization, or hardware validation.

### Verification status

See [standalone verification](verification.md) for the actual software results and
the regressions caught before delivery. All 25 real component archives were packed;
a source-independent consumer and five API documentation snippets were compiled
with ESP-IDF 6.0.2. This validates local packaging/compilation, not publication.

Still unverified: Registry upload/install, Registry-created examples, Windows
consumer build, hardware behavior, paired firmware and complete official restore.
No namespace ownership is inferred from the local rehearsal name.

Publication remains blocked until namespace authorization, final naming/version,
license/provenance review, clean IDF build and behavioral checks are approved.
The publisher must upload the coordinated lower-level versions as well as API
components; publishing only the five API components would leave unresolved
internal dependencies.
