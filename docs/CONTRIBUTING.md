# Contributing / 贡献指南

For changes to the SDK itself; application users should start with the [examples](../examples/README.md).
本页只说明如何提交 SDK 修改及验证，不是应用开发教程。

## Submit a change / 提交修改

- Use a focused branch or fork and open a PR against `main`; describe the change, checks actually run and untested scope.
- Keep English and Chinese usage aligned. Do not commit builds, downloaded components, device backups, logs, credentials or private source.
- Preserve public API contracts, safety requirements, third-party copyright and licenses. When editing imported files, retain original source hashes in [`SOURCE.json`](../SOURCE.json) and refresh current destination hashes.
- Submit test evidence in the PR/CI, not as another delivery report in the source tree.

使用工作分支和 PR，说明修改及实际检查；同步中英文，保留来源、署名和许可，不提交生成物或敏感资料。

## Checks / 修改后检查

Run from the **repository root** using an isolated Python environment with
[`tools/packaging/requirements.txt`](../tools/packaging/requirements.txt) installed:
在**仓库根目录**、已安装上述依赖的隔离 Python 环境执行：

```sh
python3 -m pytest tests -q
python3 tools/check_docs.py --check-source
git diff --check
```

Expected: all tests pass, documentation reports zero errors, and no whitespace errors.
Documentation-only changes also need review of external links and code snippets; the link checker is offline.
预期全部通过、文档零错误、无格式错误；外链和代码片段需另行验证。

For code or dependency changes, activate **ESP-IDF 6.0.2 / ESP32-S3**, rebuild affected
[examples](../examples/README.md), and run Debug and Release host tests with Python, CMake 3.20+,
CTest, Ninja, a C/C++ compiler, real **LVGL 8.4.0** and **cJSON 1.7.19** sources.
The [CI workflow](../.github/workflows/ci.yml) specifies pinned dependency downloads and the full matrix.
代码或依赖修改还需构建受影响示例，并运行双配置主机测试；固定依赖获取方式见 CI。
替换下面占位符为真实源码的绝对路径：

```sh
python3 tools/run_host_tests.py --config Debug --lvgl-source <ABSOLUTE_LVGL_SOURCE> --cjson-source <ABSOLUTE_CJSON_SOURCE>
python3 tools/run_host_tests.py --config Release --lvgl-source <ABSOLUTE_LVGL_SOURCE> --cjson-source <ABSOLUTE_CJSON_SOURCE>
```

Expected: reports under `.host-build/Debug/` and `.host-build/Release/`; missing dependencies,
zero tests, failed or skipped suites do not count as success. Windows needs a configured compiler terminal.
预期两种配置均发现并通过测试；软件渲染、构建及命令确认不代替实机观察或完整恢复验收。

Preserve local touch, IDF6 linkage, LVGL and codec adaptations; do not substitute same-name upstream
packages without testing public dependency visibility and behavior. The [API reference](api/README.md)
defines ownership, borrowed-data lifetimes and fault recovery. Dependency versions are defined by manifests and locks.
修改底层依赖时保留本地适配及接口约束，不以库名相同认定可直接替换。

Changes to packaging require [real archive generation and an independent consumer build](../tools/packaging/README.md).
Maintain all lower-level packages and licenses; local validation is not authorization to publish.
打包修改必须实际生成归档并独立构建；发布与合并仍需维护者确认。
