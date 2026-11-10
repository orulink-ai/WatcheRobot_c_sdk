# SDK development guide / SDK 开发指南

For contributors changing the SDK itself. To build an application, start with the
[examples](../examples/README.md) and [API usage](getting-started.md).
本页供修改 SDK 的开发者使用；应用开发从[示例](../examples/README.md)和[功能用法](getting-started_zh.md)开始。

## Architecture

| Layer / 层次 | Location / 位置 | Responsibility / 用途 |
| --- | --- | --- |
| Board support and public API / 板级支持与公开接口 | [`bsp/watche_robot`](../bsp/watche_robot) | `watcher_hw_*`: body, camera, audio, display and shared status/events / 机身、相机、音频、显示及公共状态事件 |
| Implementation / 内部实现 | [`components`](../components) | Services, transport, hardware adapters and vendor components / 服务、通信、硬件适配与厂商组件 |
| Applications / 示例应用 | [`examples`](../examples) | Independent ESP-IDF projects; `common` contains shared example code / 独立工程及示例共享代码 |
| Validation / 验证 | [`tests`](../tests), [`tools`](../tools), component `test_support` directories | Tool regressions, host tests, source/link checks and local package generation / 工具回归、主机测试、来源链接检查与本地打包 |

`examples/sdk.cmake` selects the local components; it does not install this SDK from Registry.
`bsp/watche_robot` groups the existing public API and board-support components without merging them;
`components` contains one independent component per direct subdirectory. Keep the shared CMake entry.
共享构建入口选择本地组件，不从组件平台安装 SDK；目录范式参考乐鑫，不机械改写现有构建。

Give each hardware resource one application owner. Do not open or poll the SDK-managed body
connection separately. Choose either event polling or dispatch, not both; copy borrowed callback
payloads before retaining them. Serialize camera/audio lifecycle operations, lock LVGL changes,
and close outside the display lock. The [API reference](api/README.md) defines the exact contracts.
每项硬件由明确的任务管理；不要重复初始化机身连接、混用事件消费方式、保留失效回调数据，
或持屏幕锁执行关闭/阻塞音频。发生事件丢失后取消旧动作，恢复须等待新的 READY 和用户操作。

## Dependencies

- Target **ESP32-S3**, **ESP-IDF 6.0.2**; version checking is in [`examples/sdk.cmake`](../examples/sdk.cmake).
- Display uses **LVGL 8.4.0** and local **esp_lvgl_port 1.4.0-custom.1**.
- All four examples configure **16 MB flash** and custom partitions. This is an example configuration,
  not a measured device capacity. Head/robot/hardware_check enable 80 MHz octal PSRAM; body does not.
- Body operation requires compatible STM32 firmware; camera operation requires matching Himax PTL
  firmware. Those paired firmware images are not built or supplied here.
- Framework components come from ESP-IDF. External versions come from all component manifests and
  example lock files; use the complete checkout, not just the five public API directories.

目标和版本以仓库配置为准；配套固件版本需要单独核实。ESP-IDF 的安装、激活方法直接参考
[官方文档](https://docs.espressif.com/projects/esp-idf/zh_CN/v6.0.2/esp32s3/get-started/index.html)。

Before upgrading dependencies, inspect public `REQUIRES` versus `PRIV_REQUIRES` and exposed types.
Preserve the local SPD2010 touch, button/knob/LED-strip IDF6 linkage, LVGL and audio adaptations.
`hal_audio` requires the locally adapted `espressif__esp_codec_dev` target. Do not replace it with
an official same-name package without checking differences. Rebuild affected examples and the
independent package consumer after any dependency/build change.
升级前核对公开类型和依赖可见性，保留触控、按键、旋钮、灯带、LVGL、音频适配；同名上游包
不一定可直接替换本地版本。完整依赖以清单和锁文件为准，打包版本图以
[`LOCAL` and `EXTERNAL` definitions](../tools/package_components.py)及生成的 `release.json` 为准。

## Contributing

- Work on a focused branch and submit a PR to this repository's `main`; do not push changes directly
  to `main`. Review `git diff` and staged paths before committing. Use a fork if needed.
- Keep English and Chinese usage aligned. Preserve safety, licenses and attribution. Avoid adding
  duplicate framework installation tutorials or delivery/review reports to the source tree.
- Do not commit builds, downloaded components, generated configs, logs, device backups, credentials
  or newly exported private source. Keep existing work intact when switching branches.
- Report checks actually run and their limits. A pending workflow or a previous revision's green
  result is not evidence for a new change. Maintainers make the final merge/release decision.

使用工作分支和 PR；同步中英文，只提交必要改动。验证结果附在 PR/CI 中，不为每次整理新增验收文档。
凭据、设备备份、构建日志及私有源码不能提交。真实检查与未测范围必须分清。

## Testing

Run commands below from the **repository root**. Tool tests need Python with the pinned
[`tools/packaging/requirements.txt`](../tools/packaging/requirements.txt) dependencies installed in an isolated environment.
在**仓库根目录**运行以下命令；工具测试使用隔离 Python 环境，并安装上述固定依赖。

```sh
python3 -m pytest tests -q
python3 tools/check_docs.py --check-source
git diff --check
```

Expected: all tests pass, `Documentation validation: 0 error(s)`, no whitespace errors.
`--check-source` checks current imported files; removed historical documents retain their original
identities in `SOURCE.json` and are retrieved from their recorded Git revision instead.
The link checker is offline; verify external links and example code separately.
预期全部测试通过、文档零错误、无格式错误。外链与代码示例需另行核对，不能只靠本地链接检查。

### Example builds / 示例构建

Activate ESP-IDF **6.0.2** with ESP32-S3 tools. Use separate fresh output directories:
激活固定版本 IDF；使用独立、新的构建目录：

```sh
idf.py -C examples/body -B examples/body/build-verification build
idf.py -C examples/head -B examples/head/build-verification build
idf.py -C examples/robot -B examples/robot/build-verification build
idf.py -C examples/hardware_check -B examples/hardware_check/build-verification build
```

Expected: each project builds its `watcher_hw_<example>.bin`, bootloader and partition/flash files.
These commands do not flash hardware. Keep logs and resolved dependencies outside Git.
预期各工程完成编译、链接并生成配套产物；构建不烧录，也不证明画面、声音或运动质量。

### Host tests / 主机测试

Use Python, CMake 3.20+, CTest with JUnit support, Ninja and a C/C++ compiler. The unified runner needs
real LVGL **8.4.0** and cJSON **1.7.19** source trees outside the repository, not substitutes.
[CI](../.github/workflows/ci.yml) shows the pinned downloads. Replace the absolute-path placeholders:
主机测试不连接 ESP32；准备真实固定版本依赖后，将占位符替换为本机绝对路径：

```sh
python3 tools/run_host_tests.py --config Debug --lvgl-source <ABSOLUTE_LVGL_SOURCE> --cjson-source <ABSOLUTE_CJSON_SOURCE>
python3 tools/run_host_tests.py --config Release --lvgl-source <ABSOLUTE_LVGL_SOURCE> --cjson-source <ABSOLUTE_CJSON_SOURCE>
```

Expected: `.host-build/Debug/report.json` and `.host-build/Release/report.json`, plus suite logs and
JUnit results. Missing dependencies, zero discovered tests, skipped or failed suites are failures.
Windows requires a configured compiler terminal; use `python` if that is its executable name.
预期两个配置均发现并通过测试；缺少依赖、零测试、跳过或失败都不能算通过。

Save source revision, dirty diff/untracked-input identities, tool versions and test artifacts with
results in PR/CI. Check the [latest Actions](https://github.com/orulink-ai/WatcheRobot_c_sdk/actions)
for the exact tested commit. Host snapshots are software-rendered, not device photographs.
For hardware, use the [hardware_check example](../examples/hardware_check/README.md), record paired
firmware, actual observations and full recovery results. Save RAM-only results before reboot.
记录实际版本、环境与产物；主机测试、进度条、命令确认不代替实机观察、机械停止或完整恢复验收。

## Packaging

The SDK is **not published to ESP Component Registry**. This workflow generates local packages and
an independent compile/link project; it does not upload or authorize a namespace.
目前未上架乐鑫组件平台。以下仅供维护者验证分发包，不是用户安装方式，也不执行正式发布。

Use a reviewed public Git revision and a **new output directory outside the repository**.
The exporter reads tracked files from that revision, not working-tree edits. All 25 components use
one exact preview version; stable versions and upstream namespaces are refused.
`preview_test` is a local rehearsal label only. Install the pinned packaging requirements into a
Python virtual environment; set the example executable paths below to that environment if different.
使用经审阅的公开提交，输出必须在仓库外且此前不存在；本地命名空间不代表平台授权。

```sh
python3 -m venv /tmp/watcher-package-tools
/tmp/watcher-package-tools/bin/python -m pip install -r tools/packaging/requirements.txt
/tmp/watcher-package-tools/bin/python tools/package_components.py \
  --revision HEAD --namespace preview_test --version 0.1.0-preview.1 \
  --output /tmp/watcher-registry-rehearsal \
  --pack --compote /tmp/watcher-package-tools/bin/compote
```

Expected: 25 real archives, `release.json`, `archives.sha256.json` and `consumer/`. Compote **2.5.2**
has `component pack`, not `component lint`. On repeated runs choose a new output directory.
The consumer unpacks actual archives and uses project-internal path overrides; release manifests
must contain no local paths. Activate IDF 6.0.2 and build the generated project:
预期真实归档和独立工程生成成功；独立工程的内部路径覆盖不应泄漏到分发清单。激活 IDF 后执行：

```sh
idf.py -C /tmp/watcher-registry-rehearsal/consumer set-target esp32s3
idf.py -C /tmp/watcher-registry-rehearsal/consumer build
```

Expected: all five public headers and dependencies compile/link without a sibling source checkout.
The consumer does not initialize hardware. Local pack/build success is not Registry upload/install
or hardware acceptance. Any future release needs namespace approval, coordinated lower-level
packages, license review, clean builds and behavioral checks; do not publish only the five APIs.
预期不依赖原源码目录即可编译链接；测试入口不操作硬件。平台上传/安装与实机仍需独立验收。

Preserve local vendor source and nested licenses byte-for-byte. Generated-only adaptations include
the namespaced codec target, standalone touch/LED-strip fixes and deferred IDF6 linkage. Do not add
`MBEDTLS_DECLARE_PRIVATE_IDENTIFIERS=1`: its generated definition conflicts with mbedTLS4.
Keep source-build camera flags consistent. The exporter rejects tracked symlinks and known secrets,
excludes tests/builds/caches/downloaded dependencies, and never overwrites existing nested licenses.
Generated README links escaping an archive must resolve to the immutable public revision.
保留本地适配与嵌套许可；构建变换只作用于生成副本，实际独立构建是验收门槛。模式扫描不能替代人工许可与敏感信息审阅。

## Source and licenses

First-party code uses [Apache-2.0](../LICENSE). Retain third-party licenses, copyright notices and
attribution, including the nested ZL38063 license and the [speaker-sample source](../examples/common/assets/README.md).
[Product images](images/product/README.md) and trademarks are not automatically relicensed by the code license.
第一方代码、第三方组件、声音素材、图片与商标的许可边界不同，不能因清理说明而删除原署名或许可证。
The hardware-check motion illustration is copied unchanged from the [original public image](https://github.com/orulink-ai/WatcheRobot-public/blob/eb78c212999374c9afd48de9c160c73991e646ae/docs/images/embedded-sdk/hardware-check-motion-safety.png); it is software-rendered, not a device photograph.
体检运动配图保留原公开来源，属于软件示意图而非实物照片。

[`SOURCE.json`](../SOURCE.json) preserves original public source paths, commits and hashes;
`files` describes currently retained imported files. Update their current destination/hash after a
move or edit, never their immutable `source_sha256`. `removed_files` retains the original records
for deleted historical documents and a Git revision/path where their last content can be retrieved.
构建不需要历史文档。历史设计、审查、迁移和交付报告仅在 Git 历史追溯，不复制到新的归档目录。
校验清单不是签名发布证明，也不证明设备已实测。未列入初始导入清单的新文件由 Git 跟踪。
