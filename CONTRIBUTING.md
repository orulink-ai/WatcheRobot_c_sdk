# Contributing / 贡献指南

For changes to the SDK itself; application users should start with the [examples](examples/README.md).
本页只说明如何提交 SDK 修改及验证，不是应用开发教程。

## Submit a change / 提交修改

- Use a focused branch or fork and open a PR against `main`; describe the change, checks actually run and untested scope.
- Keep English and Chinese usage aligned. Do not commit builds, downloaded components, device backups, logs, credentials or private source.
- Preserve public API contracts, safety requirements, third-party copyright and licenses. When editing imported files, retain original source hashes in [`SOURCE.json`](SOURCE.json) and refresh current destination hashes.
- Submit test evidence in the PR/CI, not as another delivery report in the source tree.

使用工作分支和 PR，说明修改及实际检查；同步中英文，保留来源、署名和许可，不提交生成物或敏感资料。

## Documentation locations / 文档归属

| Location / 位置 | Owns / 唯一主要职责 |
| --- | --- |
| Root README files | Product overview, support boundaries and first-run links / 产品及入口 |
| `docs/getting-started*.md` | One continuous source-to-device tutorial / 完整上手步骤 |
| `docs/features.md` | User-facing feature → API → guide map / 面向应用开发的功能与调用入口 |
| `docs/hardware-compatibility.md` | Hardware/firmware requirements, backup and recovery / 配套条件与恢复 |
| `docs/model-deployment.md` | Model acquisition, package selection and provisioning procedure / 模型获取与安装流程 |
| `docs/api/` | Parameters, lifecycle, errors and advanced vision / 功能调用契约 |
| `examples/<name>/README.md` | Build, expected behavior and modification points for that application / 示例说明 |
| Component README files | Component scope and internal contracts; link to application guides / 内部组件说明 |
| `tools/packaging/README.md` | Maintainer package validation / 维护者打包流程 |

Keep raw logs, backups, review reports and transient plans outside the source tree or in CI/PR evidence. Avoid duplicate tutorials in component READMEs. New runnable tutorials belong in the IDF example matrix; code snippets must match a built example or have separate compile evidence. Keep English/Chinese entry points aligned and distinguish build, diagnostic and operator acceptance.
原始日志、备份和临时审查记录留在仓库外或 CI/PR，不另建零散报告目录。新增教程以实际构建示例为依据，不把链接检查通过写成实机通过。

Keep product release versions, versioned asset URLs, image hashes and dated verification results in release manifests and validation records. General tutorials focus on prerequisites, commands, expected results and common errors, linking to compatible releases. Leave integrity checks to the tools; do not make users manually audit manifests, hashes or CRCs as routine setup. Build dependencies remain defined by manifests and lock files.
通用教程围绕准备、操作、预期结果和常见问题编写，链接到适用的发布入口。产品版本、镜像哈希和单次测试结果留在发布清单与验证记录中；文件校验由工具完成，不把手工检查清单、哈希和 CRC 作为日常上手步骤。构建依赖以工程声明和锁文件为准。

Keep artwork provenance out of tutorial prose and preserve applicable licenses and attribution in their dedicated files. Maintain general motion precautions in one section and link to it near relevant operations.
配图来源说明不混入教程正文，许可与署名保留在对应文件。通用运动注意事项集中维护，在相关操作处链接引用。

- When adding or updating third-party code, update [THIRD_PARTY.md](THIRD_PARTY.md), preserve original notices and nested licenses, and record local adaptations. / 新增或更新第三方代码时，同步清单并保留原署名及嵌套许可。

## Checks / 修改后检查

Run from the **repository root** using an isolated Python environment with
[`tools/packaging/requirements.txt`](tools/packaging/requirements.txt) installed:
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
[examples](examples/README.md), and run Debug and Release host tests with Python, CMake 3.20+,
CTest, Ninja, a C/C++ compiler, real **LVGL 8.4.0** and **cJSON 1.7.19** sources.
The [CI workflow](.github/workflows/ci.yml) specifies pinned dependency downloads and the full matrix.
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
packages without testing public dependency visibility and behavior. The [API reference](docs/api/README.md)
defines ownership, borrowed-data lifetimes and fault recovery. Dependency versions are defined by manifests and locks.
修改底层依赖时保留本地适配及接口约束，不以库名相同认定可直接替换。

Changes to packaging require [real archive generation and an independent consumer build](tools/packaging/README.md).
Maintain all lower-level packages and licenses; local validation is not authorization to publish.
打包修改必须实际生成归档并独立构建；发布与合并仍需维护者确认。
