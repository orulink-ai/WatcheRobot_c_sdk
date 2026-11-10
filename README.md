English | [简体中文](README_zh.md)

# WatcheRobot C SDK (Development Preview)

Write your own `app_main` with `watcher_hw_*`, independently of the official app,
Python SDK, Daemon, server, SD card and models. This is a hardware-only source
snapshot, **not a stable release or complete paired-device acceptance**.

## Start here

1. [Pin public source, install ESP-IDF 6.0.2 and build](docs/getting-started.md).
2. [Run the 8-group / 26-item hardware check](docs/hardware-check.md).
3. Edit `examples/robot/main/app_main.c`, then build from repository root:
   `idf.py -C examples/robot build`.

Flashing changes the ESP32 application/partitions and can overwrite storage.
Verify your ESP32 port and paired STM32/Himax images **before flashing**; setup,
custom flash, official recovery and expected results are in the first guide.
Current servos have **no physical position feedback**. Reference X90/Y120 can
require large movement from an unknown start. ACK/DONE is not a position sensor.

## What do you want to do?

| Goal | Entry |
| --- | --- |
| Check real hardware, safely and one item at a time | [Hardware check](docs/hardware-check.md) |
| Build/flash/restore or use your own project | [Getting started](docs/getting-started.md) |
| Migrate the old namespace | [Migration](MIGRATION.md) |
| Understand open-loop motion | [Current hardware contract](docs/servo-open-loop.md) |
| Inspect public headers | `components/sdk/watcher_hw_{core,body,camera,audio,display}/include/` |
| Understand ownership, locks and event overflow | Headers, [audit](AUDIT.md), [setup](docs/getting-started.md) |
| Review actual evidence, not assumptions | [Historical validation](VALIDATION.md), [historical public-sync evidence](SYNC_VALIDATION.md) |
| Develop on a computer with existing official firmware | [Python SDK](https://github.com/orulink-ai/WatcheRobot_python_sdk/blob/main/README.md) — separate route |

`examples/body`, `head`, `robot`, and `hardware_check` are independent ESP-IDF projects.
`examples/common` contains shared UI, pure flow, open-loop body adapter and CC0
speech assets. Do not include the official firmware top-level project.

## Provenance, scope and licensing

[SOURCE.json](SOURCE.json) pins upstream ESP32 commit
`e23bee2a642f6c90753b370cb18c46815e0c8f58` and inventories exported file hashes.
The public checkout commit is the delivery version; the private upstream is provenance
only, not a user prerequisite. This standalone repository was imported from the
already-public SDK snapshot; it does not expose additional upstream source.
The historical export tool is not bundled here and is not needed to build.
See [repository workflow and provenance](docs/repository-workflow.md) for the import
baseline, current file-hash semantics and branch/PR contribution process.
No official app/cloud/voice business services, models, credentials or firmware binaries
are exported. Downloaded managed dependencies/build outputs are excluded.

First-party snapshot code is licensed under [Apache-2.0](LICENSE). Seeed, SSCMA, codec, expander and Espressif files keep their
original copyright/licenses. Registry dependencies retain their own licenses.
This is a delivery snapshot, not an independently maintained fork; fixes should flow
upstream. Historical names/hashes in evidence remain untouched and do not prove
acceptance of this renamed snapshot. Complete physical pairing, safety and restoration
checks remain pending. No stable v1 or production deployment is claimed. This repository does not yet have
its own CI workflow; historical CI results are not current standalone-repository checks.
