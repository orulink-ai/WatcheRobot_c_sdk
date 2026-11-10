# 验证结果 / Verification results

这里回答两个问题：软件检查通过了哪些项目？还有哪些事情需要真正连接机器人才能确认？

This page separates software checks from checks that need a real robot.

## 已通过的软件检查 / Passed software checks

以下结果对应提交 `84c59f2369d695d355149d47612a3c0e187dee97`，不是后续修改的自动保证。
完整日志和报告见[本次 GitHub Actions](https://github.com/orulink-ai/WatcheRobot_c_sdk/actions/runs/42764462326)。

These results apply to the commit above. Later changes need their own checks.

| 检查 / Check | 结果 / Result | 说明 / What it proves |
| --- | --- | --- |
| 文档与工具测试 / Documentation and tool tests | 25 项通过 / 25 passed | 检查工具、链接、文件校验和打包回归 / Validators, links, file hashes and packaging regressions |
| 主机测试 / Host tests | Linux、Windows 的 Debug、Release 均通过 / Both configurations passed on both systems | 在电脑上验证可独立测试的软件逻辑 / Checks software logic without a robot |
| 四个示例 / Four examples | ESP-IDF 6.0.2 编译通过 / Builds passed | 身体控制、头部功能、组合示例和硬件体检可以生成固件 / Firmware can be built for body, head, robot and hardware_check |
| 组件打包 / Component packaging | 25 个包生成成功 / 25 packages created | 用真实打包工具检查包结构 / Checked using the real packaging tool |
| 独立工程 / Separate application | 从组件包编译、链接成功 / Built and linked from packages | 不需要引用原 SDK 源码目录 / Does not depend on the SDK source checkout |

本地还完成了：Linux 的 Debug、Release 各 19 套测试、58 个测试项通过；五份 API 文档的代码片段编译通过。
代码片段只经过编译，没有执行机器人动作。

Local checks also passed 19 host suites and 58 tests per configuration on Linux,
and compiled the five API documentation snippets. The snippets were not executed
on hardware.

## 还没验证什么 / Not yet verified

- **机器人实际表现**：舵机是否按预期转动、图像与声音是否正常、长期使用是否稳定。
- **完整恢复**：刷回官方固件后，启动和设备配对是否正常。
- **乐鑫平台安装**：本次只在本地打包，没有上传，也没有验证从平台下载、安装和创建示例。

- **Real robot behavior:** motion, image/audio quality and long-running stability.
- **Full restoration:** startup and pairing after restoring official firmware.
- **Installation from Espressif Registry:** packages were built locally, not uploaded or installed from the service.

**编译通过不代表机器人实机测试通过。** 例如，程序可以发出转动指令，但不能据此确认舵机已经转到目标角度或停止。
开始连接设备前，请阅读[示例与设备要求](../examples/README.md)和[运动控制注意事项](servo-open-loop_zh.md)。

**A successful build is not hardware acceptance.** A sent command does not prove
that a servo reached its target or stopped. Read [getting started](../examples/README.md)
and [motion precautions](servo-open-loop.md) before connecting hardware.

## 如何复查 / How to reproduce

操作步骤见[测试指南](development.md#testing)，组件打包步骤见[发布准备](development.md#packaging)。
查看 PR 时，以该 PR 最新提交的检查结果为准；不要用上面旧提交的结果代替。

Use [testing](development.md#testing) and [package preparation](development.md#packaging).
For a PR, check the results for its latest commit, not only the run linked above.

## 维护者记录 / Maintainer details

以下是复现所需的技术记录，首次使用 SDK 不必先阅读。
These details are for maintainers reproducing the checks, not prerequisites for using the SDK.

- 本地环境 / Local tools: Linux x86-64, Python 3.11.15, GNU C 11.4.0, CMake/CTest 4.4.4, Ninja 1.13.2.
- 测试依赖 / Host dependencies: LVGL 8.4.0 (`4495f428630cc1741bd8bfd977f080e8460e8e8d`), cJSON 1.7.19 (`c859b25da02955fef659d658b8f324b5cde87be3`).
- 固件工具 / Firmware tools: official ESP-IDF v6.0.2 archive and matching public submodules, Xtensa GCC 15.2.0, IDF CMake 4.0.3. The source archive has no Git metadata; IDF identified its version from source constants and emitted a Git-version warning.
- 打包工具 / Packaging: Component Manager 2.5.2. The separate local IDF environment used Component Manager 3.1.2; this does not claim compatibility with every other version.
- 本次整理未改运行源码、原构建配置、依赖锁或许可；原公开导入中的 418 个非 Markdown、非 SOURCE 文件逐一核对未变。/ The 418 non-Markdown, non-SOURCE files from the public import were unchanged, including runtime code, original build settings, locks and licenses.
- 修复过的打包问题 / Packaging regressions fixed: an unnecessary generated mbedTLS macro prevented compilation, and README links led outside the package. Regression tests cover both. The fixes did not change production camera code.
- 测试报告 / Reports: the host runner writes per-suite logs and machine-readable results; packaging records input/output hashes and archive hashes. CI saves reports as downloadable artifacts. Missing dependencies, zero tests and failed suites are not treated as success.
