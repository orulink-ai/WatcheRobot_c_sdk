# Maintainer development guide / 维护者开发指南

Architecture, dependency review, contributions, validation and local packaging for
maintainers of the standalone public SDK. Application users should start with the
[documentation navigation](README.md) or [source examples](../examples/README.md).
These internal maintenance procedures are not required for normal SDK use.

本指南汇总维护者的架构、依赖、贡献与仓库流程、测试及本地打包信息；
普通用户从使用文档或源码示例进入，无须先阅读内部维护流程。

- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [Testing](#testing)
- [Packaging](#packaging)

## Architecture

Use this page when you are deciding where to put application logic or investigating
conflicting access to hardware. For build commands, start with [source examples](../examples/README.md).
本页面向开发应用和排查硬件访问冲突的人；构建步骤见[源码示例](../examples/README.md)。

### Choose what your application needs / 按需要选择能力

| Your goal / 你想做什么 | Public API / 公开接口 | What your application supplies / 应用负责什么 |
| --- | --- | --- |
| Move the body, control lights, read touch / 控制运动、灯光和触摸 | `watcher_hw_body` | User permission, event handling and safe recovery / 用户确认、事件处理与安全恢复 |
| Take photos or receive camera frames / 拍照或接收画面 | `watcher_hw_camera` | Image use, UI and network policy / 图片用途、界面与联网策略 |
| Record or play sound / 录音或播放 | `watcher_hw_audio` | When to record/play and how to react to errors / 录放时机与出错处理 |
| Draw a screen / 绘制界面 | `watcher_hw_display` | Interface contents and interaction / 页面内容与交互 |
| Share status and event handling / 处理公共状态与事件 | `watcher_hw_core` | A bounded event queue owned by the caller / 由调用方管理、容量有限的事件队列 |

Each example is an independent ESP-IDF project. `examples/sdk.cmake` selects local
source directories through `HW_BODY`/`HW_HEAD`; it does not download Registry packages.
`examples/common` contains shared example UI/media behavior, not a public API.
The repository does not supply the official product application or STM32/Himax firmware.

每个示例独立构建。`examples/sdk.cmake` 按 `HW_BODY`/`HW_HEAD` 选择本地源码，
不从组件平台下载 SDK。`examples/common` 供示例复用界面和音视频逻辑，不是公开接口。
官方产品应用及 STM32/Himax 固件不随本仓库提供。

### Assign one owner before adding callbacks / 先明确谁负责硬件

An **owner task** is the application task responsible for opening, using and closing
a resource. A **callback** runs when an event arrives; it is not a place to start blocking work.
“负责硬件的任务”是统一打开、使用、关闭该资源的应用任务；“回调”是事件到达时调用的函数，
不应在其中执行需要等待的工作。

1. Give body control one process-wide MCU connection. MCU means the paired
   microcontroller (STM32). Do not initialize or poll the same connection elsewhere.
   Choose either FIFO polling (reading queued events in arrival order) or synchronous
   subscription dispatch from one task, never both.
2. Serialize camera open/use/close in one task. JPEG image bytes are borrowed only
   for the duration of a callback; copy them if you need them afterward.
3. Keep blocking audio calls in one task, outside body/camera callbacks and outside
   an LVGL lock. LVGL is the screen's graphics library; its lock protects UI changes.
4. Let display control screen flushing. Do not draw independently to its panel.
   Use its borrowed handles only until close, lock LVGL changes and close outside the lock.

中文步骤：身体连接只能有一个管理任务，事件队列读取与同步订阅分发二选一；相机生命周期
由一个任务串行管理，回调结束前复制要保留的 JPEG；录放音在独立任务执行，不占用回调或
界面锁；显示接口统一刷新屏幕，句柄仅在关闭前有效，修改界面要加锁，关闭时不能持锁。

### Recognize ready and recover safely / 判断就绪并安全恢复

`status()` returning `ESP_OK` means the query succeeded. Check `state` and
`last_error` before using the device; query success is not READY.
Body event overflow latches FAULT: cancel pending application actions, close/init
outside callbacks, resubscribe, wait for a fresh READY and require a new user action.
Reconnect or draining the queue must not resume old motion.

`status()` 返回 `ESP_OK` 只表示查询成功，还要检查 `state` 和 `last_error`。
身体事件队列溢出后会锁定故障：取消待执行动作，在回调外关闭并初始化、重新订阅，
等待新的 READY 和用户操作。重连或读空队列不能自动重放旧运动。

Expected result: one clear owner per resource, no borrowed data used after its
lifetime, and no automatic motion after recovery.
预期：每个资源只有一个管理者，不使用失效数据，恢复后不自动运动。

For implementation dependencies see [dependencies](#dependencies); before motion
read [servo safety](servo-open-loop.md) / [舵机安全](servo-open-loop_zh.md)。

## Dependencies

Use this page to prepare a source build or review a dependency upgrade. For your
first build, follow [source examples](../examples/README.md) / [源码示例](../examples/README.md).
Use the complete pinned checkout and network access for declared downloads.
本页用于准备构建环境、检查依赖升级。请使用固定版本的完整仓库，并允许下载声明的依赖。

### Match the checked-in configuration / 按仓库配置准备环境

| Item / 项目 | Required configuration / 仓库配置 |
| --- | --- |
| Chip / 芯片 | ESP32-S3 |
| ESP-IDF / 开发框架 | Exactly 6.0.2; checked by `examples/sdk.cmake` / 固定 6.0.2，由构建入口检查 |
| Screen library / 界面库 | LVGL 8.4.0 for head/display and the real-LVGL host tests / 显示与真实界面测试使用 8.4.0 |
| Flash / 闪存 | All four examples select 16 MB and a custom partition table / 四个示例均配置 16 MB 与各自分区表 |
| PSRAM / 外部内存 | head/robot/hardware_check: octal, 80 MHz; body does not enable it / 前三者启用八线 80 MHz，body 不启用 |
| Camera / 相机 | `CONFIG_WATCHER_CAMERA_BACKEND_PTL=y`; matching Himax PTL firmware / 需配套 Himax PTL 固件 |
| Screen format / 显示格式 | RGB565: `CONFIG_LV_COLOR_DEPTH_16`, `CONFIG_LV_COLOR_16_SWAP`; fonts selected by head defaults / 字体见 head 默认配置 |

These are example settings, not measured minimum hardware requirements or a wider
compatibility guarantee. PTL is the camera transport used with the paired Himax device.
以上为示例实际配置，不代表最低硬件需求或其他平台兼容性。PTL 是与配套 Himax 相机通信的传输方式。

### Know where dependencies come from / 区分依赖来源

- **ESP-IDF supplies** the scheduler (FreeRTOS), buses, timers, LCD support, filesystems,
  memory support and encryption library mbedTLS. These are not separate local packages.
  **框架提供**任务调度、通信总线、定时器、显示、文件系统、内存与加密支持。
- **This repository supplies** hardware APIs, services, the STM32 connection and camera
  transport. The body API owns the STM32 connection; `mcu_runtime` provides helpers
  for its polling task rather than a second owner. `hal_camera` selects PTL at configuration.
  **仓库提供**硬件接口及内部通信代码；身体接口统一管理 STM32 连接，不能另起一套连接管理。
- **Checked-in board/vendor code** includes `sensecap-watcher`, `esp_lvgl_port`,
  `esp_codec_dev`, `esp_io_expander_pca95xx_16bit`, `sscma_client` and `media_lib_sal`.
  Keep their licenses and attribution. Board support code (BSP) describes board wiring;
  codec code handles sound conversion. Their upstream READMEs are not SDK application lists.
  **随仓库保存的板级与厂商代码**保留原许可证；BSP 指板级支持，codec 指音频编解码。
- **Downloaded components** are selected by `idf_component.yml` manifests. The head
  manifest pins `esp_jpeg` 1.3.1, LVGL 8.4.0, cJSON 1.7.19, `esp_audio_codec` 2.4.1,
  `esp_lcd_touch` 1.1.1 and `cmake_utilities` 0.5.3. Other manifests add requirements.
  Review the generated dependency lock for the complete resolved set.
  **下载依赖**以所有清单及构建生成的版本锁定文件为准，不能只看上述 head 直接依赖。
- **Paired STM32 and Himax firmware** is a device prerequisite, not code built here.
  **配套设备固件**不是本 SDK 构建产物，仓库不提供替换镜像。

### Review an upgrade / 升级前逐项检查

1. Compare [API CMake files](../components/sdk), manifests and the generated version
   lock. Public headers expose some service, touch and LVGL types, so moving a
   dependency from public `REQUIRES` to private `PRIV_REQUIRES` can break callers.
2. Preserve local adaptations: `sensecap-watcher/patches.cmake` applies the SPD2010
   IDF6 touch fix; `examples/sdk.cmake` adjusts button/knob/LED-strip linkage and
   enables `MBEDTLS_DECLARE_PRIVATE_IDENTIFIERS`.
3. Compare local `esp_lvgl_port` and codec changes and host-test support with their
   upstream versions. `hal_audio` expects `espressif__esp_codec_dev`; check that this
   build target resolves correctly rather than substituting a same-named package.
4. Rebuild affected examples and run [tests](#testing). If distributing packages,
   also build the clean consumer in [packaging](#packaging).

中文步骤：先核对公开头文件、构建声明及锁定版本；保留触控、按键、旋钮、灯带、界面和音频
的本地适配；核实音频所需构建目标；最后重新构建和测试。同名或更新版本不代表可以直接替换。

Expected result: the selected versions and local fixes remain traceable, and the
actual application builds. A successful download or package operation alone is insufficient.
预期：依赖版本与本地修改可追溯，实际应用重新构建通过；下载成功或打包成功不代替构建。

## Contributing

For contributors fixing bugs, adding features or improving documentation in this
standalone public SDK. The result should be a focused pull request (PR) with real
validation results. Do not export private sources or change the old product repository.
本页供修复问题、增加功能或改进文档的贡献者使用，目标是提交范围清楚、附真实验证结果的 PR；
不导出私有源码，不顺带修改旧产品仓库。

### Working branch and repository workflow / 工作分支与仓库流程

Use this standalone public SDK checkout; no private repository or old materials
checkout is needed. Before switching or updating, run `git status --short` from
repository root and save unfinished work. Never discard another change automatically.
Create a descriptive `docs/`, `fix/` or `feat/` branch from updated `main`; a detached
checkout used for reproducible builds is not a development branch.
Firmware work requires activated **ESP-IDF 6.0.2** and ESP32-S3 tools; see the
[source examples](../examples/README.md) and
[official IDF guide](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/get-started/index.html).
Documentation-only changes do not need ESP-IDF.
Expected: an up-to-date working branch with existing work preserved.

只使用当前公开 SDK 仓库。先检查并保存已有修改，从更新后的 `main` 创建目标明确的工作分支，
不自动丢弃任何人的修改；固件需固定版本 IDF 与 ESP32-S3 工具，纯文档不需要。
预期分支准备就绪且已有工作完整保留。

### 2. Make and check the change / 修改并检查

- Keep English and Chinese user guides aligned. Explain who a command is for,
  where to run it, its prerequisites and expected result.
- Keep safety contracts, recovery links, attribution and licenses. Preserve the
  original facts in historical records; new tests need their own result.
- Follow [testing](#testing): check docs/links for documentation; build affected
  examples and run relevant Debug/Release host tests for code. State any missing environment.
- Review from repository root:

中英文用户说明同步；命令写清对象、位置、前提及结果。保留安全约定、恢复链接、署名与许可证，
不改写历史测试事实。按测试指南执行与改动相符的检查，缺少环境就如实说明。在仓库根目录检查：

```sh
python3 tools/check_docs.py
git diff --check
git diff
```

Expected: documentation validation reports no errors, whitespace checks succeed
and the diff contains only your intended changes. Inventory hashes in `SOURCE.json`
are maintained separately; ask the maintainer to refresh affected output hashes.
预期文档检查无错误、格式检查通过、差异仅含目标修改。涉及来源清单内文件时，请维护者另行更新输出哈希。

### 3. Submit only intended files / 仅提交本次文件

Do not stage builds, `managed_components`, generated SDK configs, screenshots,
logs, device backups, credentials or newly exported private source.
Stage only explicitly reviewed paths; inspect `git diff --cached` from repository
root before committing/pushing the intended working-branch changes.
在仓库根目录仅暂存明确审阅过的路径，检查 `git diff --cached`，只提交和推送本次工作分支修改。

Expected: a new commit is pushed to your working branch, not `main`.
Open a PR to **this repository's `main`**, describe the change, actual checks and
remaining limits, and wait for maintainer review before merging. If you cannot
push here, use a public fork. Delete a work branch only after its changes are merged.

预期提交推送到工作分支，而不是 `main`。向**本仓库 `main`** 提 PR，说明修改、实际验证及
未覆盖项，等待维护者审阅再合并；无推送权限则用公开 fork。确认修改合并后再删除工作分支。

See [source records](development.md#source-and-licenses), [tests](#testing) and [documentation](README.md).

### Maintainer task routing / 维护工作分流

| Goal / 目标 | Guide / 指南 | Expected result / 预期结果 |
| --- | --- | --- |
| Make a change / 修改代码或文档 | [Contributing / 贡献](#contributing) | A focused branch and reviewed PR / 范围清晰的分支与经审阅的 PR |
| Find source history or license context / 查来源与许可证背景 | [Provenance / 来源](development.md#source-and-licenses) | Original source and current files are distinguishable / 分清原始来源与当前文件 |
| Check a change / 验证修改 | [Testing / 测试](#testing) | Repeatable results tied to a revision / 可复现且对应具体版本的结果 |
| Prepare distribution packages / 准备分发包 | [Local packaging / 本地打包](#packaging) | Real archives and a clean build, not an upload / 真实归档和独立构建，不执行上传 |
| Build or use hardware / 构建与使用硬件 | [Documentation / 使用导航](README.md) | Find the relevant setup or API guide / 找到上手或接口指南 |

Historical records are background, not a new test result.
历史记录只供背景参考，不能作为本次验证结果。

## Testing

For contributors checking a change before review. Choose the checks that match
your change and save results with the exact source revision. These commands run
on a development computer; they do not flash hardware.
本页面向提交前验证修改的开发者。按修改范围选择检查，把结果与实际源码版本关联；以下命令不烧录设备。

| Change / 修改 | What to run / 检查入口 |
| --- | --- |
| Documentation / 文档 | Documentation checks below / 下方文档检查 |
| Firmware or dependencies / 固件或依赖 | Affected example builds and host suites / 相关示例构建与主机测试 |
| Shared hardware code / 公共硬件代码 | All affected examples; unified Debug and Release suites / 受影响示例及统一双配置测试 |
| Package generation / 打包 | [Packaging tests and clean consumer / 打包测试与独立构建](#packaging) |
| Real hardware behavior / 真实硬件行为 | [Manual check](../examples/hardware_check/README.md) / [人工体检](../examples/hardware_check/README_zh.md) |

### 1. Record what you tested / 记录被测版本

From repository root:
在仓库根目录执行：

```sh
git rev-parse HEAD
git status --short
git diff --check
```

Record OS, compiler/CMake versions and dependency revisions. If testing uncommitted
changes, save the diff and identity of any untracked inputs outside Git with your
results. Do not commit generated logs, downloaded dependencies or screenshots.
记录系统、编译器、CMake 和依赖版本；未提交修改需一并保存差异及未跟踪输入的标识，
否则单个提交号不足以复现。日志、下载依赖和截图不提交到仓库。

### 2. Check documentation / 检查文档

Requires Python 3. From repository root:
需要 Python 3，在仓库根目录执行：

```sh
python3 tools/check_docs.py
git diff --check
```

Expected: `Documentation validation: 0 error(s)` and no whitespace errors.
The checker covers local Markdown targets/anchors and source references, not
external URL availability. Review external links and example commands separately.
After the inventory maintainer refreshes current paths/hashes in `SOURCE.json`, run:
预期文档检查零错误、无空白格式错误。工具检查本地链接、锚点和源码路径，不检查外部网址可用性；
外链与命令还需人工核对。清单维护者更新当前路径及哈希后，再执行：

```sh
python3 tools/check_docs.py --check-source
```

Expected: current file hashes match. Keep immutable upstream source hashes unchanged.
预期当前文件哈希匹配；不能改写固定的上游来源哈希。

### 3. Build examples / 构建示例

Activate **ESP-IDF 6.0.2** with ESP32-S3 tools using the
[official IDF guide](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/get-started/index.html);
see the [source examples](../examples/README.md) for project-specific instructions.
From repository root, choose new dedicated output directories:
按上手指南激活开发环境，在仓库根目录使用新的独立输出目录：

```sh
idf.py --version
idf.py -C examples/body -B examples/body/build-verification build
idf.py -C examples/head -B examples/head/build-verification build
idf.py -C examples/robot -B examples/robot/build-verification build
idf.py -C examples/hardware_check -B examples/hardware_check/build-verification build
```

Expected: each configure/build succeeds; each `build-verification/` contains its
`watcher_hw_body.bin`, `watcher_hw_head.bin`, `watcher_hw_robot.bin` or
`watcher_hw_hardware_check.bin`. Keep configure/build logs, resolved dependency
versions and generated flash arguments outside Git. Do not reuse old build artifacts.
预期四个工程配置并构建成功，各自生成对应 `.bin`；在 Git 外保存日志、解析后的依赖版本和
烧录参数。不用旧构建产物冒充本次结果；上述命令不执行烧录或擦除。

### 4. Run tests on your computer / 在电脑上运行测试

These **host tests** check software without an ESP32. Install Python 3, CMake 3.20+,
CTest with JUnit-report support, Ninja and a C/C++ compiler. The unified runner
requires real **LVGL 8.4.0** and **cJSON 1.7.19** source trees; it does not download
or substitute them. Get the exact dependency sources outside the repository, using
the [LVGL host guide](../examples/hardware_check/test_support/host/README.md) and
[CI configuration](../.github/workflows/ci.yml) as references.

“主机测试”是在电脑上、不连接 ESP32 的软件测试。准备以上工具及真实版本的界面库、JSON
解析库源码；统一运行器不会下载或用替身代替它们。源码放在仓库外，具体准备方式参考链接。

Replace the absolute-path placeholders and run from repository root:
替换绝对路径占位符，在仓库根目录执行：

```sh
python3 tools/run_host_tests.py --help
python3 tools/run_host_tests.py --config Debug --lvgl-source <ABSOLUTE_LVGL_SOURCE> --cjson-source <ABSOLUTE_CJSON_SOURCE>
python3 tools/run_host_tests.py --config Release --lvgl-source <ABSOLUTE_LVGL_SOURCE> --cjson-source <ABSOLUTE_CJSON_SOURCE>
```

The runner discovers `host`/`uart_host` CMake suites beneath components/examples.
Expected: `.host-build/Debug/report.json` and `.host-build/Release/report.json`, with
per-suite `runner.log` and `ctest.xml`. Missing dependencies, zero discovered tests,
failed tests and skipped results cause failure. Debug and Release use separate
builds; the default generator is Ninja. On Windows, use a compiler development
terminal and `python` if that is your executable name.

运行器发现组件与示例下的测试。预期生成两个配置的报告及每套测试的日志；缺少依赖、零用例、
失败或跳过均不算通过。Windows 需要已配置编译器的开发终端，可按实际使用 `python`。

For a smaller first run, the common example suite needs no ESP-IDF:
若先跑一套简单测试，公共示例测试不需要 ESP-IDF；在仓库根目录执行：

```sh
cmake -S examples/common/test_support/host -B ../watcher-common-release -DCMAKE_BUILD_TYPE=Release
cmake --build ../watcher-common-release --config Release --parallel
ctest --test-dir ../watcher-common-release -C Release --output-on-failure --no-tests=error
```

Expected: CTest discovers and passes its tests. Repeat using a new Debug directory
and Debug configuration when needed; this one suite does not replace the full matrix.
预期 CTest 发现并通过测试；需要时用另一个目录运行 Debug。这一套不代替全量矩阵。

### 5. Save useful evidence / 保存可核验结果

- Save reports and configure/build logs. CTest's `Testing/Temporary/LastTest.log`
  is overwritten on each run. Keep Debug/Release results separate.
  保存报告和构建日志；CTest 默认日志每次覆盖，双配置结果分开保存。
- With `HOST_WRITE_PPM=ON`, LVGL tests write `snapshots/*.ppm` in their build tree.
  These are software-rendered images, not photographs of the device.
  界面测试截图是软件渲染图，不是设备实拍。
- For GitHub checks, record the exact PR/run URL, tested head SHA and artifact links
  from this repository's Actions or PR Checks tabs. Pending/missing runs are unverified.
  GitHub 检查需记录本仓库的具体运行链接、版本及产物；未运行不算通过。
- For hardware, follow the manual check, record board and paired-firmware identity,
  operator observations and recovery evidence. Save RAM-only results before reboot.
  实机按人工体检记录板卡、配套固件、观察结果及恢复证据，重启前保存内存中的结论。

### Existing results and hardware limits / 已有结果与实机范围

Executed Linux results are recorded in [verification](verification.md), including
four example builds, Debug/Release suites, real archives, a clean package consumer
and five API snippets. Read that record for its tested revision and exact scope.
[Historical records](../history/README.md) and older host-README counts belong to
those original revisions. A workflow file alone does not prove a successful run.

当前已执行的 Linux 结果见验证记录，以其中版本及范围为准；历史记录和旧测试数量保留原含义。
有工作流文件不代表工作流已运行成功。

Software checks do not establish physical position, stop timing, mechanical limits,
edge touch, image/sound quality, repeated device teardown, long combined operation
or complete official restoration. No flashing, paired-device run, local Windows
run or official restore is established by the Linux record. Before custom flashing,
prepare backups and a complete verified [official recovery bundle](https://wiki.orulink.ai/docs/flashing#full).
Servos have no position feedback: read [motion safety](servo-open-loop.md).

软件检查不证明真实位置、停止时间、机械限位、边缘触摸、画面声音质量、反复设备启停、长时间组合
运行或完整恢复。Linux 记录不代表已完成烧录、配套实机、Windows 本地运行或官方恢复。
自定义烧录前准备备份及[完整官方恢复包](https://wiki.orulink.ai/docs/flashing#full)，运动前阅读[安全说明](servo-open-loop_zh.md)。
未测项目必须保持未测。

## Packaging

For maintainers checking whether the SDK can be distributed as ESP-IDF components.
This workflow creates real archives and a separate test project; **it does not
publish anything**. The SDK is not published to ESP Component Registry (the online
component catalogue). Keep using the source examples for normal development.

本页面向准备分发 SDK 的维护者：先生成真实归档，再用独立工程验证构建。**不执行发布**；
SDK 尚未上架 ESP 组件平台，日常开发继续使用源码示例。

### Before you start / 开始前

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

### 1. Test and generate archives / 测试并生成归档

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

### 2. Build only from the archives / 仅从归档构建

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

### 3. Decide whether a release is ready / 判断是否可以发布

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

### Advanced: what is packaged / 进阶：打包范围

A **component** is an ESP-IDF build unit; a **dependency graph** lists which units
need others. Five API directories alone are not self-contained: public headers
also need services, protocols, board support (BSP) and patched vendor code.
The chosen boundary preserves **25 separate components**, coordinated at one version.
One aggregate component was not selected because it would require a broader CMake,
header visibility, Kconfig (build configuration) and source-list rewrite.

“组件”是 ESP-IDF 构建单元，“依赖图”表示它需要哪些其他单元。五个接口目录不能单独使用，
因此保留 25 个组件并统一版本；不把所有代码合成一个包，以免连带重构构建配置与公开头文件。
工具不在源码树新增会影响现有示例的分发清单；源码示例继续使用 `examples/sdk.cmake`。

#### Local dependency graph / 本地依赖图

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

#### External versions / 外部版本

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

#### Preserve patches and licenses / 保留修改与许可证

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

#### Export checks / 导出检查

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


## Source and licenses


For developers checking where files came from, and maintainers preparing a source
or firmware release. Start here when you need to distinguish the original import,
current edits and an external firmware download.
本页供核对文件来源及准备发布的人使用，帮助区分首次导入、当前修改和外部固件下载。

## What this checkout provides / 本仓库提供什么

The standalone **WatcheRobot C SDK** contains hardware APIs and four independent
ESP-IDF examples. Build from its own root; no private or old-materials checkout is
needed. The official product application, STM32/Himax implementations, cloud
services, models and production firmware bundles are not supplied here.

本仓库提供硬件接口和四个独立 ESP-IDF 示例，可直接在根目录构建，不依赖私库或旧资料仓库。
不提供官方产品应用、STM32/Himax 实现、云服务、模型或生产固件包。

- Build, backups and recovery / 构建、备份与恢复：[English](../examples/README.md) · [中文](../examples/README.md)
- Official flashing and recovery / 官方烧录与恢复：<https://wiki.orulink.ai/docs/flashing>
- Separate Python SDK / 独立 Python SDK：<https://github.com/orulink-ai/WatcheRobot_python_sdk>

External hardware-check preview binaries stay in their original Release; they
are not releases of this repository and do not automatically match your checkout.
Before flashing, match that Release's source, manifest and hashes. Stop if paired
firmware compatibility or a complete official recovery bundle cannot be verified.

外部体检预览固件仍归原 Release，不是本仓库发布，也不自动对应当前版本。烧录前核对该
Release 的源码、清单与哈希；配套兼容性或完整官方恢复包无法核实时停止操作。

## Check the original import / 核对首次导入

The initial public commit
[`85c6af84c93db63db335d4b93f2a114ba66cd7f1`](https://github.com/orulink-ai/WatcheRobot_c_sdk/commit/85c6af84c93db63db335d4b93f2a114ba66cd7f1)
has the same Git tree as the public
[`firmware/sdk` subtree at the original materials commit](https://github.com/orulink-ai/WatcheRobot-public/tree/eb78c212999374c9afd48de9c160c73991e646ae/firmware/sdk).
No private history or additional upstream files were imported. That first commit
still uses old documentation paths; use a reviewed documentation-adapted revision
for current instructions. The old-repository link is for comparison, not setup.

首次导入与链接中的原公开 SDK 子树完全一致，未迁入私有历史或额外源码。首次导入仍有旧文档
路径，当前操作请使用经审阅、完成文档适配的版本；旧仓库链接只供追溯，不是安装步骤。

## Read or update file hashes / 阅读与维护文件哈希

A **hash** is a file-content fingerprint. [`SOURCE.json`](../SOURCE.json) records
allowlisted upstream files, their immutable source commit/paths and source hashes.
Its output `sha256` checks the listed current file bytes; it is not a signed
release manifest or proof of a build/device test.

哈希是文件内容的指纹。`SOURCE.json` 保存允许导出的上游文件、固定提交、路径与来源哈希；
输出 `sha256` 用于核对当前文件，不是签名发布清单或构建、实机证明。

When documentation moves or changes, the inventory maintainer should:
文档移动或修改后，由清单维护者：

1. Retain upstream source paths and `source_sha256` unchanged.
   保留上游来源路径及 `source_sha256`。
2. Retain the original imported destination/output hash and describe the transformation.
   保留最初导入目标、输出哈希并说明转换。
3. Record the current destination and compute its output hash from actual bytes.
   记录当前目标路径，根据真实文件计算输出哈希。
4. Run `python3 tools/check_docs.py --check-source` from repository root.
   在仓库根目录执行该检查；预期路径、链接与当前文件哈希均匹配。

Public files absent from the original inventory remain tracked by Git. No historical
export tool or access to private upstream code is needed to build the SDK.
原清单未覆盖的公开文件由 Git 跟踪；构建不需要历史导出工具或私有上游访问权限。

## Images, history and licenses / 图片、历史与许可证

`docs/images/hardware-check-motion-safety.png` was copied unchanged from the
[original public image](https://github.com/orulink-ai/WatcheRobot-public/blob/eb78c212999374c9afd48de9c160c73991e646ae/docs/images/embedded-sdk/hardware-check-motion-safety.png)
at the same materials commit. Its Git blob is
`214f26b9eb254164c4f6ae15ead3a11d15658f36`. It is software-rendered artwork, not a robot photograph.
体检配图来自同一原公开提交，保持原样；上述 Git blob 用于追溯，它是软件渲染示意而非实拍。

The product overview uses selected hardware facts and three product renders from
Orulink's product manual V1.1 (2026-11-08), supplied by the product owner for this
README. See [product-image attribution and hashes](images/product/README.md).
The internal manual and its other attachments were not copied into this repository.
产品概述另按负责人提供的产品手册摘取必要硬件信息及三张外观图；来源与校验值见链接，
未导出内部手册全文或其他附件。产品规格与 SDK 实际支持范围分别说明。

[Historical records](../history/README.md) retain original dates, test results,
names, repository references and firmware hashes. [Design records](design/README.md)
also describe prototypes not shipped here. Dependency READMEs describe their own
upstream libraries; preserve their attribution and license files.

历史记录保留原日期、测试结论、名称、仓库引用和固件哈希；设计记录包含未交付的原型。
依赖 README 介绍各自上游库，不代表本 SDK 提供额外应用；原署名及许可证应保留。

For current executed checks, see [verification](verification.md); for preparing a
new release, see [local packaging](development.md#packaging).
当前执行结果见验证记录；准备分发包见本地打包指南。
