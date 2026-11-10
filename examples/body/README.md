# body / Body touch/light and protocol-event demonstration / 身体触摸、灯光与协议事件示例

## Requirements / 前置条件

ESP32-S3 Watcher hardware, ESP-IDF **6.0.2**, complete pinned public SDK checkout and network access.
All examples configure 16 MB flash/custom partitions. A compatible STM32 motion/LED/touch peer is required.

No official application source, cloud, model or Python SDK is required to build.

## Configure and build / 配置与构建

Run in the **WatcheRobot_c_sdk repository root**, with IDF activated:

```sh
idf.py --version
idf.py -C examples/body build
```

Expected output: `examples/body/build/watcher_hw_body.bin` plus generated bootloader, partition and
flash arguments. This is a build command, not an execution/acceptance claim. Inspect
[`main/app_main.c`](main/app_main.c), [`sdkconfig.defaults`](sdkconfig.defaults) and
[`main/idf_component.yml`](main/idf_component.yml). Keep defaults/manifests/partitions together; do not
silently change dependency versions. Configuration edits can use `idf.py -C examples/body menuconfig`
but must remain within the supported contract in [dependencies](../../docs/dependencies.md).

## Before flash / 烧录前

Read [English setup/flash/recovery](../../docs/getting-started.md) or
[中文构建、烧录与恢复](../../docs/getting-started_zh.md). Verify the actual ESP32 port and compatible
STM32/Himax firmware as applicable, back up required data and prepare a verified complete official
restore bundle. The first full custom flash overwrites official configuration; restoring just an app
bin does not restore the official partition layout. Stop if pair/recovery assets are unknown.
Do not guess flash offsets, use an application-only bin at 0x0, or erase the device as troubleshooting.
Only after these preconditions, use the guide's `flash`/`monitor` commands with this project's name.

Servos have no physical position feedback. Reference movement may span a large range; clear the entire
travel and keep manual power disconnection available. ACK/DONE, final command angles and successful
software stop submission are not measured position or proof of physical stopping.

## Observe / 观察结果

Touch events are logged with event/sequence and touch code. A touch sets the light request to green while active; release submits stop. It does not automatically start a position-relative move. Motion lifecycle logs, if present, remain protocol evidence, not measured position.

No dated hardware result is asserted here. For a structured manual pass/fail session use
[hardware_check](../hardware_check/README.md), where an untested item is not a pass.

## Failure and recovery / 失败兜底

Preserve return/error logs and the source commit. A non-READY status is not bypassed by forcing actions.
Check power/cables and paired firmware; no camera image or audible sound is not a pass. Body-event loss
requires canceling pending actions and explicit close/init outside callbacks, resubscription, fresh READY
and new user intent. Reconnect or FIFO drain does not unlock the latch. Do not independently poll a
link already owned by the body runtime.
Use the full official recovery procedure and verify startup/pairing when returning to official firmware.

中文：根目录运行构建，查看日志和实际图像/声音/触摸；不能把 ACK、DONE、进度或未测当通过。
烧录前必须核实配套固件、备份与完整恢复包；无物理反馈，参考动作可能大行程，人工断电必须可用。
异常时先停止业务并保留日志，不能靠强制动作或重复创建硬件所有者掩盖故障。

[Example index](../README.md) · [API guides](../../docs/README.md) · [Testing](../../docs/testing.md)
