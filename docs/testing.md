# Testing and evidence / 测试与证据

## Current evidence boundary

Documentation restructuring started from public PR #1 head
`2c2c7c99da4b2d9cfb8e05045a516f180f8c6e69` on `refactor/espressif-sdk-structure`.
The working tree may include parallel test/packaging changes; record the actual tested commit and diff.
This repository's Linux verification is recorded in [standalone verification](verification.md):
all four ESP-IDF 6.0.2 examples, Debug/Release host suites, real package archives,
a clean package consumer and the five API snippets were actually compiled/tested.
No device flash, paired-device run, local Windows run or official restoration was performed.
A workflow file or successful static check is not evidence that that workflow has run successfully.
Historical counts in [history](../history/README.md) and host READMEs belong to their original revisions.

中文：本地 Linux 真实执行结果见独立验证记录；Windows、平台安装和实机仍单独列为未验证，历史数字不冒充本次结果。

## Record identity first (repository root)

```sh
git rev-parse HEAD
git status --short
git diff --check
```

Record OS/compiler/CMake versions and dependency revisions as well. Archive untracked-tree patch identity
when testing before commit. Do not commit generated logs, downloaded dependencies or screenshots.

## Firmware build matrix (activated ESP-IDF 6.0.2 terminal)

Run from repository root, each in a clean dedicated output directory:

```sh
idf.py --version
idf.py -C examples/body -B examples/body/build-verification build
idf.py -C examples/head -B examples/head/build-verification build
idf.py -C examples/robot -B examples/robot/build-verification build
idf.py -C examples/hardware_check -B examples/hardware_check/build-verification build
```

Require every configure and build to succeed. Expected binaries are `watcher_hw_body.bin`,
`watcher_hw_head.bin`, `watcher_hw_robot.bin`, `watcher_hw_hardware_check.bin` under each project's
`build-verification/`; retain configure/build logs, resolved dependency versions and generated flash
arguments outside Git. Never reuse upstream build artifacts as this repository's evidence.
These commands build only; no flashing or erase is part of test automation.

## Host suites

Install CMake 3.20+ and a working C/C++ compiler. The example-internal common suite needs no ESP-IDF.
From repository root (choose an unused build directory):

```sh
cmake -S examples/common/test_support/host -B ../watcher-common-release -DCMAKE_BUILD_TYPE=Release
cmake --build ../watcher-common-release --config Release --parallel
ctest --test-dir ../watcher-common-release -C Release --output-on-failure --no-tests=error
```

Repeat in a separate `../watcher-common-debug` directory with Debug. This is one suite, not the full
repository matrix. Discover the component `test_support/host` (and MCU UART) CMake projects too;
missing dependencies and zero discovered tests are failures, not skips claimed as passes.
The [real LVGL host guide](../examples/hardware_check/test_support/host/README.md) provides pinned
LVGL source acquisition, configure/build/CTest commands, Debug/Release instructions and snapshot limits.
Suites that consume cJSON need the real pinned source, not invented stubs or a renamed version.
The checked-in unified runner discovers all `host`/`uart_host` CMake suites under components/examples.
It requires Python, CMake/CTest with JUnit support and Ninja, real LVGL 8.4.0 and real cJSON 1.7.19
sources. Install these outside the repository or use the pinned dependency checkout configured by CI.
Replace the absolute-path placeholders below; run from repository root:

```sh
python3 tools/run_host_tests.py --help
python3 tools/run_host_tests.py --config Debug --lvgl-source <ABSOLUTE_LVGL_SOURCE> --cjson-source <ABSOLUTE_CJSON_SOURCE>
python3 tools/run_host_tests.py --config Release --lvgl-source <ABSOLUTE_LVGL_SOURCE> --cjson-source <ABSOLUTE_CJSON_SOURCE>
python3 tools/check_docs.py
```

Expected reports: `.host-build/Debug/report.json` and `.host-build/Release/report.json`, with per-suite
`runner.log` and `ctest.xml` beneath each configuration. Missing real dependencies, zero tests, failed
or skipped test results cause failure. Windows requires a configured compiler development terminal;
use `python` instead of `python3` if that is its Python executable. The default generator is Ninja.
Run `python3 tools/check_docs.py --check-source` after the maintainer updates SOURCE.json's current
paths/hashes; pending inventory changes are not silently ignored. Local full-suite results
are linked in [standalone verification](verification.md); attach actual runner output/report identity to each PR.


## Reports and acceptance

- CTest: `<build-dir>/Testing/Temporary/LastTest.log` (overwritten on each run), and configure/build logs.
- Real LVGL snapshots: the suite build's `snapshots/*.ppm` with `HOST_WRITE_PPM=ON`; software-rendered,
  not LCD photographs. Keep Debug/Release outputs separate.
- GitHub: the exact PR/check run URL, tested head SHA and downloadable logs/artifacts. See the repository
  **Actions** and PR **Checks** tabs, not old-repository CI. A pending or missing run is unverified.
- Static docs: check local Markdown targets/anchors, moved provenance destinations/current hashes and
  `git diff --check`. SOURCE changes are maintained separately; do not alter immutable source hashes.
- Hardware: follow [manual hardware check](hardware-check.md), record board/paired-firmware identity,
  operator observations and recovery evidence. RAM-only check results reset on reboot; save externally.

## Not established by software tests

Physical position, stop timing, mechanical limits, edge touch, JPEG/acoustic quality, repeated teardown,
long combined operation and complete official restore/pairing remain hardware acceptance work. Servos
have no feedback; reference moves can be large; manual power cut is necessary when software stop cannot
be delivered. Prepare backups and a verified complete official recovery bundle before any custom flash.
An untested hardware item must remain untested, never automatically pass.
