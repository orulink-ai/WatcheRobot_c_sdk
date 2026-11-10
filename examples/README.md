# Examples / 示例

All commands below run from the **WatcheRobot_c_sdk repository root**, in an activated ESP-IDF 6.0.2
terminal. Target: ESP32-S3; all example defaults select 16 MB flash and a custom partition table.
Head-based examples also enable octal PSRAM and require paired Himax PTL firmware.

| Project | Purpose / 用途 | Selected layers |
| --- | --- | --- |
| [body](body/README.md) | Touch-driven lights, body event logs / 身体触摸与灯光 | `HW_BODY` |
| [head](head/README.md) | Camera/audio/display UI / 头部媒体界面 | `HW_HEAD` |
| [robot](robot/README.md) | Body + head integration / 组合 | Both |
| [hardware_check](hardware_check/README.md) | Operator-guided physical diagnosis / 人工体检 | Both |

```sh
idf.py -C examples/body build
```

Replace `body` with the desired project. Expected output is that project's `build/watcher_hw_<project>.bin`
and IDF flash files. Network access is required for pinned managed components. A source build is not a
hardware acceptance result. Inspect `main/app_main.c`, `sdkconfig.defaults`, `partitions.csv` and the
matching manifests before changing a project. `sdk.cmake` selects local components; it is not a Registry
installer. Keep the complete checkout pinned when using it in another application.

[common](common/README.md) is example-private UI/media/check logic, **not** an independent ESP-IDF project
or a separately promised public API. Do not build it with `idf.py -C examples/common`.

## Before connecting/flashing / 烧录前

Use [English setup/recovery](../docs/getting-started.md) or [中文上手与恢复](../docs/getting-started_zh.md).
Verify the ESP32 port, compatible STM32/Himax pair, backups and complete official restore bundle.
Custom flash overwrites official configuration. No physical servo feedback is available; reference moves
can be large. Clear the entire travel and keep manual power disconnection available. ACK/DONE/software
stop do not certify physical stopping. Missing pairing/recovery assets means stop before flashing.

中文：从仓库根目录运行；common 不能独立构建。先确认配套、备份与完整恢复包，无反馈/大行程
必须清空整个行程并保留人工断电。构建成功或协议完成不等于实机验收。

See [API guides](../docs/README.md), [testing evidence](../docs/testing.md) and [dependencies](../docs/dependencies.md).
