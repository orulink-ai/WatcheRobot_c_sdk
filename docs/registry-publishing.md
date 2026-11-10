# Prepare local distribution packages / 准备本地分发包

For maintainers checking whether the SDK can be distributed as ESP-IDF components.
This workflow creates real archives and a separate test project; **it does not
publish anything**. The SDK is not published to ESP Component Registry (the online
component catalogue). Keep using the source examples for normal development.

本页面向准备分发 SDK 的维护者：先生成真实归档，再用独立工程验证构建。**不执行发布**；
SDK 尚未上架 ESP 组件平台，日常开发继续使用源码示例。

## Before you start / 开始前

- Use a reviewed **public Git revision**. The tool reads tracked files from that
  commit, not your working-tree edits or untracked files. It does not commit,
  push, fetch another repository or export private sources.
- Choose a new output directory **outside this repository**; existing output is
  refused. Keep the Python environment and downloaded dependencies outside Git too.
- `preview_test` below is only a local label, not a registered/authorized namespace.
  All 25 packages use one exact preview version. Stable versions and upstream
  `espressif`/`lvgl` namespaces are refused.

使用经审阅的**公开提交**；工具不读取未提交修改，不替你提交、推送或导出私有源码。
输出目录必须是仓库外的新目录；Python 环境与下载依赖也不提交。示例命名空间仅用于本地标记，
不代表有平台授权；25 个包统一使用精确预览版本，不允许稳定版或冒用上游命名空间。

## 1. Test and generate archives / 测试并生成归档

Requires Python 3, Git and network access to install the pinned packaging tools.
Run from **this SDK repository root**. Choose different output names on repeated runs:
需要 Python 3、Git 及安装工具所需网络。在 **SDK 仓库根目录**执行；重复时换新的输出目录：

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

Expected: tests pass and `--pack` runs the real Component Manager (`compote`) for
each component. Compote **2.5.2** supports `component pack`, not `component lint`;
there is no separate lint command to run. On Windows these shell commands need
adaptation to your Python environment's executable paths; a local Windows consumer
build is not established by the Linux verification record.

预期测试通过，`--pack` 逐个调用真实打包工具。固定版本 **2.5.2** 没有 `component lint`，
不能声称运行过该命令。以上为 shell 路径写法，Windows 需按本地 Python 环境调整；Linux 验证不代表 Windows 已验证。

| Output under the new directory / 输出 | What to inspect / 核对内容 |
| --- | --- |
| `release.json` | Public source SHA, dependency graph, versions and source/output hashes / 公开提交、依赖、版本及哈希 |
| `components/<name>/` | 25 generated component directories / 25 个生成的组件目录 |
| `archives/<name>_<version>.tgz` | Actual compote archives / 真实工具生成的归档 |
| `archives.sha256.json` | Archive SHA256 fingerprints / 归档内容指纹 |
| `consumer/` | Independent compile/link test project / 独立编译链接工程 |

Each component includes `CMakeLists.txt`, a manifest, README, licenses and
`RELEASE_PROVENANCE.json`. Provenance records original public paths/commit, source
hashes, transformations and the original manifest metadata/hash. That saved metadata
is inert JSON, not an extra active manifest.

每个组件有构建文件、清单、说明、许可证及来源记录。来源记录保留原路径、提交、哈希和转换说明；
原清单仅作为 JSON 留档，不会再次参与依赖解析。

## 2. Build only from the archives / 仅从归档构建

Activate **ESP-IDF 6.0.2** and its ESP32-S3 tools, then run:
激活 **ESP-IDF 6.0.2** 与 ESP32-S3 工具后执行：

```sh
cd /tmp/watcher-registry-rehearsal/consumer
idf.py --version
idf.py set-target esp32s3
idf.py build
```

Expected: all five public headers and their dependencies compile/link without a
sibling SDK source checkout. `consumer/components/<namespace>__<name>/` contains
extracted real archives. Its `main/idf_component.yml` has consumer-only path overrides
pointing **inside this project**. Release archives contain no `path`/`override_path`
dependencies; the local overrides let you test unpublished packages without claiming
that they are downloadable from Registry.

预期五个公开接口及其依赖独立编译、链接通过，不依赖旁边的 SDK 源码。测试工程从真实归档解包，
只在自身清单中用项目内部路径覆盖；分发清单没有本地路径依赖。这是未上架组件的本地验证，
不代表可从平台下载安装。

The consumer's `app_main` does nothing: no hardware initialization, motion, flash,
serial port or paired-firmware operations. It is a build check, not a hardware demo.
Full source examples are not advertised as standalone Registry examples.
测试入口不操作硬件、不烧录；它只检查构建，不是实机示例，也不代表平台已提供可创建的示例。

## 3. Decide whether a release is ready / 判断是否可以发布

See [verification](verification.md) for actual local results: 25 real archives,
a clean ESP-IDF consumer and five API documentation snippets were built on Linux.
Still unverified: Registry upload/install, Registry-created examples, Windows
consumer build, physical behavior, paired firmware and complete official restore.

实际本地结果见验证记录；平台上传安装、平台示例、Windows、实机、配套固件及完整官方恢复仍未验证。

Before any future publication, maintainers must approve namespace authorization,
names/version, license/provenance review, clean IDF builds and behavioral checks.
Publish the coordinated lower-level packages as well as the five API packages;
the five APIs alone do not include everything needed by consumers. This guide
contains no upload, token, staging or namespace-creation steps.

未来发布前须确认命名空间授权、名称版本、许可证与来源、独立构建及行为检查。下层依赖必须
协调发布，不能只上传五个公开接口包。本指南不提供上传、凭据、暂存平台或创建命名空间步骤。

## Advanced: what is packaged / 进阶：打包范围

A **component** is an ESP-IDF build unit; a **dependency graph** lists which units
need others. Five API directories alone are not self-contained: public headers
also need services, protocols, board support (BSP) and patched vendor code.
The chosen boundary preserves **25 separate components**, coordinated at one version.
One aggregate component was not selected because it would require a broader CMake,
header visibility, Kconfig (build configuration) and source-list rewrite.

“组件”是 ESP-IDF 构建单元，“依赖图”表示它需要哪些其他单元。五个接口目录不能单独使用，
因此保留 25 个组件并统一版本；不把所有代码合成一个包，以免连带重构构建配置与公开头文件。
工具不在源码树新增会影响现有示例的分发清单；源码示例继续使用 `examples/sdk.cmake`。

### Local dependency graph / 本地依赖图

The `LOCAL` table in `tools/package_components.py` is authoritative. Local manifest
edges use exact namespaced versions and conservatively public visibility because
some public headers expose dependency types. Existing CMake `REQUIRES` (public) and
`PRIV_REQUIRES` (private) declarations stay intact. `core` below means `watcher_hw_core`.
依赖以工具中的 `LOCAL` 表为准；本地依赖锁定命名空间与精确版本，清单按公开依赖处理，原 CMake 公私声明保留。

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

ESP-IDF built-ins (scheduler, drivers, timers, filesystems, networking, encryption,
PSRAM/heap support) remain framework requirements under **IDF ==6.0.2** and ESP32-S3.
框架内置的调度、驱动、网络、加密等不另行导出；目标仍限于固定框架版本与 ESP32-S3。

### External versions / 外部版本

Existing constraints become exact versions, not upgrades:
将现有约束固定为精确版本，不升级到上游最新版：

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

`esp_jpeg` 1.3.1 belongs to head/robot/hardware_check application code, not this
five-API consumer; it is not forced on every package. Inspect the generated
consumer lock after real IDF resolution for the full transitive graph (dependencies
of dependencies). Pack success alone does not establish that resolution.
`esp_jpeg` 属于应用，不强加给所有包。完整间接依赖需检查独立工程实际解析出的锁定文件；打包成功不代替解析与构建。

### Preserve patches and licenses / 保留修改与许可证

- Package local `esp_lvgl_port` and `esp_codec_dev` from the public Git revision,
  not current official replacements. Existing C/H sources and license files are
  copied byte-for-byte, including nested ZL38063 licensing.
  使用本地修改版；现有 C/H 与许可证保持原样，包括嵌套的 ZL38063 许可。
- Only in generated release copies, rewrite `espressif__esp_codec_dev` to
  `<namespace>__esp_codec_dev` so the patched codec is selected.
  仅改生成副本中的构建目标名，确保仍使用本地音频代码。
- Keep standalone SPD2010 touch (`cmd -1`) and LED-strip heap-include fixes in
  generated `patches.cmake`. Remove unreachable original-application branches and
  their `../../scripts` calls: those scripts are not in a consumer package.
  保留触控和灯带修复；去除消费者无法访问的旧应用分支与脚本调用。
- Carry the IDF6 button/knob GPIO and LED-strip driver/HAL link adjustments in a
  deferred BSP CMake function, so the consumer does not need `sdk.cmake`.
  生成的板级构建代码保留 IDF6 链接适配，不依赖父仓库入口。
- Keep camera flags aligned with source builds. Do not reintroduce generated
  `MBEDTLS_DECLARE_PRIVATE_IDENTIFIERS=1`: it conflicted with mbedTLS4's empty
  compatibility macro in the clean IDF6 consumer; a regression test covers this.
  相机编译选项保持一致，避免重新加入与 mbedTLS4 冲突的宏定义；已有回归覆盖。
- Rewrite links escaping a component archive to the immutable public revision;
  retain internal links and attribution. Installed docs must not need a sibling checkout.
  包外文档链接指向固定公开提交，包内链接与署名保留。

These are generated manifest/CMake adaptations, not runtime C fixes. The independent
consumer build is their acceptance gate.
以上仅为生成清单与构建文件的适配，不改运行时代码；必须通过独立工程验证。

### Export checks / 导出检查

The exporter reads one revision through `git ls-tree`/`git show` with an explicit
component allowlist. It rejects tracked symlinks and known secret signatures and
excludes test_support, builds, managed_components, Git metadata, caches,
node_modules, dist, private-key suffixes and compiled artifacts. The pattern scan
is limited: review licenses and sensitive content manually too. The root Apache
license fills only missing top-level licenses; existing and nested licenses are
not overwritten. IDF downloads upstream components separately, never from a
maintainer's `managed_components` directory.

导出器只读取固定提交的允许目录，拒绝符号链接及已知凭据特征，排除测试辅助、构建、下载依赖、
缓存、私钥后缀及编译产物。模式扫描有局限，仍需人工审查敏感内容和许可。根 Apache 许可证
只补充缺失的顶层许可证，不覆盖现有或嵌套许可；上游组件由 IDF 另行下载。
