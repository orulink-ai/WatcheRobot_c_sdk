# body: Touch-controlled lights / 触摸控制灯光

## Overview / 概述

Touch the body to request green lights; release clears the green light and requests stop.
The example logs touch events and does **not** automatically start servo movement.
触摸身体请求绿灯，松手清除绿灯并请求停止；记录触摸事件，**不会自动启动舵机运动**。

## Requirements / 要求

- Git and **ESP-IDF 6.0.2**; environment setup: [official IDF instructions](../README.md#requirements--环境要求).
  Git 与 **ESP-IDF 6.0.2**；环境安装与激活见上述官方文档入口。
- ESP32-S3, **16 MB flash**, custom partitions and compatible **STM32 body firmware** for lights/touch/motion.
  ESP32-S3、**16 MB flash**、自定义分区及兼容的 **STM32 身体固件**，用于灯光、触摸与运动。
- Body defaults do not enable PSRAM. / body 默认不启用 PSRAM。

## Build and run / 构建与运行

Run in an activated **ESP-IDF 6.0.2** terminal from the **repository root**. Replace PORT with the ESP32 SERIAL-B port. Flashing replaces the app and partitions; back up needed data first.
在已激活 **ESP-IDF 6.0.2** 的终端、**仓库根目录**执行。PORT 替换为 ESP32 的 SERIAL-B 端口；首次烧录会替换原应用及分区，需保留的数据请先备份。

```sh
idf.py --version
idf.py -C examples/body build
idf.py -C examples/body -p PORT flash monitor
```

Expected output: `examples/body/build/watcher_hw_body.bin` and IDF flash files.
预期产物为上述应用文件及 IDF 配套烧录文件；依赖下载需要网络，构建不会写入设备。
Dependency downloads need network access; building does not write to a device.

For port setup and recovery, see the [first-run guide](../../docs/getting-started.md) / [上手教程](../../docs/getting-started_zh.md)。
If adding motion, read [motion safety](../../docs/api/body.md#motion-safety-english) /
[运动安全](../../docs/api/body.md#motion-safety) before moving.

## Expected behavior / 预期行为

Touch: green light on; release: green light off and a stop request.
Check `touch=... code=...` events and `light:` / release-triggered `stop:` results (`ESP_OK` on success).
触摸应亮绿灯，松手应熄灯并请求停止；检查对应触摸日志及灯光、停止请求结果。
A successful request does not prove physical stopping. / 请求成功不证明机械已停。
For a guided hardware walkthrough, use [hardware_check](../hardware_check/README.md)。逐项体验硬件功能可运行硬件体检。

## Troubleshooting / 故障处理

If something fails, check the error log, power, connections and matching firmware.
出现问题时查看错误日志，先查供电、连接与固件配套。
If events are lost, stop operating; do not repeatedly touch to unlock or automatically replay old actions.
Reconnection or clearing queued events does not clear the fault. Cancel pending actions and follow the
[complete body API recovery contract](../../docs/api/body.md): close/init outside callbacks, resubscribe,
wait for a new READY and require a **new user action**. Do not separately poll the SDK-managed connection.
丢事件后先停操作，不反复触摸解锁、不自动重放旧动作；重连或清空队列不能解除故障。
取消积压动作，按身体 API 完整契约在回调外关闭并检查结果、初始化、重新订阅，等待新的 READY；
重新动作须有**新的用户操作**，不要另行轮询 SDK 管理的连接。
Return to official firmware: [Wiki full recovery](https://wiki.orulink.ai/docs/flashing#full), then verify startup/pairing.
返回官方固件直接按 [Wiki 完整恢复](https://wiki.orulink.ai/docs/flashing#full)，再检查启动与配对。
