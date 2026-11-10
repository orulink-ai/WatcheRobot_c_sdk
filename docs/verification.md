# Standalone verification / 独立仓库验证记录

## Scope and identity / 范围与身份

This record covers the standalone-repository restructuring on 2026-11-10, starting
from public PR #1 commit `2c2c7c99da4b2d9cfb8e05045a516f180f8c6e69`.
The first-party/third-party runtime C/C++ source, pre-existing CMake files, dependency
locks and license files were verified byte-for-byte against the original public
import; no runtime behavior or hardware pairing was changed. New Python validators,
CI and packaging transformations were exercised separately. This is not the old
materials repository's acceptance record.

本记录属于独立仓库本次整理，不沿用旧仓库验收数字。原运行源码、构建文件、依赖锁和许可
逐文件保持不变；新增验证工具和发行树生成逻辑单独测试。测试在 Linux 执行，无设备连接、
串口、烧录、运动或生产部署。PR 的远端检查结果以对应 head 的 Actions 为准。

## Actual local execution / 本次真实执行

| Gate | Actual result | Boundary |
| --- | --- | --- |
| Python validators and packaging regressions | 25 tests passed | Includes real compote packaging; not firmware/hardware acceptance |
| Documentation | Offline Markdown targets/anchors and SOURCE output hashes passed; `git diff --check` passed | External availability is not inferred from local checks |
| Host Debug | 19 actual suites, 58 CTests passed | No missing/skipped/zero-test suite treated as success |
| Host Release | 19 actual suites, 58 CTests passed | Assertions remain enabled |
| ESP-IDF 6.0.2 / body | Configure and firmware build passed | No flash |
| ESP-IDF 6.0.2 / head | Configure and firmware build passed | No flash |
| ESP-IDF 6.0.2 / robot | Configure and firmware build passed | No flash |
| ESP-IDF 6.0.2 / hardware_check | Configure and firmware build passed | No flash or manual observations |
| Component package rehearsal | 25 real compote component archives created | Local rehearsal namespace only, not uploaded |
| Clean package consumer | ESP-IDF 6.0.2 configure, compile and link passed using extracted archives | No source-checkout component path; Registry install not tested |
| Five API documentation snippets | Compiled in the separate package consumer | Functions were not executed; no hardware observations |
| Windows | Not run locally | Separate CI jobs are configured; consult exact remote checks |
| Registry publication/install | Not performed | Namespace ownership, account access and publication approval remain gates |
| Paired hardware and full recovery | Not performed | Still requires qualified firmware, backups and operator acceptance |

Local host environment: Linux x86-64, Python 3.11.15, GNU C 11.4.0,
CMake/CTest 4.4.4 and Ninja 1.13.2. Actual LVGL 8.4.0 source was fetched from
`4495f428630cc1741bd8bfd977f080e8460e8e8d`; cJSON 1.7.19 from
`c859b25da02955fef659d658b8f324b5cde87be3`.
Firmware builds used the official ESP-IDF v6.0.2 archive with its exact relevant
public submodules, Xtensa GCC 15.2.0 and IDF's CMake 4.0.3. The archive lacks Git
metadata; IDF reports v6.0.2 from its own source version constants, with a Git-version
warning. No invented Git tag or private toolchain snapshot was used.
Packaging used actual Component Manager 2.5.2; the installed IDF environment's
Component Manager was 3.1.2. These are separate tested tools, not an untested promise
of compatibility with every intervening version.

## Regressions caught before delivery / 交付前发现并修正

- The first independent component-consumer build rejected a generated
  `MBEDTLS_DECLARE_PRIVATE_IDENTIFIERS=1` flag: IDF6 mbedTLS4 defines the compatibility
  macro without a value and `-Werror` rejected its redefinition. A failing regression
  test was added, the unnecessary generated flag removed, then the test and actual
  consumer build passed. The checked-in production camera source was not changed.
- A package-documentation regression exposed links that escaped the component archive
  into a nonexistent parent SDK checkout. Generated documentation now pins those
  cross-component/repository links to the exact public source commit. Source-tree
  local links and attribution remain intact.
- The wrapper/host test work retained real dependency, zero-test, missing-result and
  failure checks; tests do not become successful by silently skipping unavailable code.

## Evidence and reproduction / 证据与复现

[Testing instructions](testing.md) describe the current CLI entry points.
The host runner writes per-suite compiler details, logs and JUnit results plus
Debug/Release JSON reports. The package tool writes source/output provenance and
actual archive SHA256 values. CI uploads per-job reports and build evidence; its
existence alone is not a passing run. Download results from this repository's
Actions/PR checks for the exact reviewed head, not the historical repository.

本地结果不代替远端 Windows 矩阵，也不代替真正从乐鑫平台安装。正式发布前必须确认公司
命名空间与版本、许可/来源审阅、平台安装及示例消费。任何代码/打包变更后需重新运行相关
验证；仅修改本记录不能产生新的通过结果。软件构建不证明机械停止、位置、声音、画面、
长期稳定性或完整恢复。详见[安全上手](getting-started_zh.md)和[无反馈运动](servo-open-loop_zh.md)。
