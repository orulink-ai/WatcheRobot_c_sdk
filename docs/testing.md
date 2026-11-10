# Check a change / 验证修改

For contributors checking a change before review. Choose the checks that match
your change and save results with the exact source revision. These commands run
on a development computer; they do not flash hardware.
本页面向提交前验证修改的开发者。按修改范围选择检查，把结果与实际源码版本关联；以下命令不烧录设备。

| Change / 修改 | What to run / 检查入口 |
| --- | --- |
| Documentation / 文档 | Documentation checks below / 下方文档检查 |
| Firmware or dependencies / 固件或依赖 | Affected example builds and host suites / 相关示例构建与主机测试 |
| Shared hardware code / 公共硬件代码 | All affected examples; unified Debug and Release suites / 受影响示例及统一双配置测试 |
| Package generation / 打包 | [Packaging tests and clean consumer / 打包测试与独立构建](registry-publishing.md) |
| Real hardware behavior / 真实硬件行为 | [Manual check](hardware-check.md) / [人工体检](hardware-check_zh.md) |

## 1. Record what you tested / 记录被测版本

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

## 2. Check documentation / 检查文档

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

## 3. Build examples / 构建示例

Activate **ESP-IDF 6.0.2** with ESP32-S3 tools as described in
[setup](getting-started.md) / [中文上手](getting-started_zh.md).
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

## 4. Run tests on your computer / 在电脑上运行测试

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

## 5. Save useful evidence / 保存可核验结果

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

## Existing results and hardware limits / 已有结果与实机范围

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
prepare backups and a complete verified [official recovery bundle](getting-started.md).
Servos have no position feedback: read [motion safety](servo-open-loop.md).

软件检查不证明真实位置、停止时间、机械限位、边缘触摸、画面声音质量、反复设备启停、长时间组合
运行或完整恢复。Linux 记录不代表已完成烧录、配套实机、Windows 本地运行或官方恢复。
自定义烧录前准备备份及[完整官方恢复包](getting-started_zh.md)，运动前阅读[安全说明](servo-open-loop_zh.md)。
未测项目必须保持未测。
