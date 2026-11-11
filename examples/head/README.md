# head: Pictures, recording and playback / 拍照与录音播放

## Overview / 概述

Use the screen controls to take a photo, record microphone audio, play it back and test the speaker.
用屏幕上的 Photo 拍照、Record 录音、Play 回放，也可测试扬声器；本示例不驱动身体运动。
This example does not drive body motion.

## Requirements / 要求

- Git and **ESP-IDF 6.0.2**; environment setup: [official IDF instructions](../README.md#requirements--环境要求).
  Git 与 **ESP-IDF 6.0.2**；环境安装与激活见上述官方文档入口。
- ESP32-S3, **16 MB flash**, custom partitions and **80 MHz octal PSRAM**; LVGL **8.4.0** is selected.
  ESP32-S3、**16 MB flash**、自定义分区与 **80 MHz 八线 PSRAM**；工程选用 LVGL **8.4.0**。
- The camera requires matching **Himax PTL firmware**. / 摄像需要匹配的 **Himax PTL 固件**。

## Build and run / 构建与运行

Run in an activated **ESP-IDF 6.0.2** terminal from the **repository root**. Replace PORT with the ESP32 SERIAL-B port. Flashing replaces the app and partitions; back up needed data first.
在已激活 **ESP-IDF 6.0.2** 的终端、**仓库根目录**执行。PORT 替换为 ESP32 的 SERIAL-B 端口；首次烧录会替换原应用及分区，需保留的数据请先备份。

```sh
idf.py --version
idf.py -C examples/head build
idf.py -C examples/head -p PORT flash monitor
```

Expected output: `examples/head/build/watcher_hw_head.bin` and IDF flash files.
预期产物为上述应用文件及 IDF 配套烧录文件；依赖下载需要网络，构建不会写入设备。
Dependency downloads need network access; building does not write to a device.

For port setup and recovery, see the [first-run guide](../../docs/getting-started.md) / [上手教程](../../docs/getting-started_zh.md)。

## Expected behavior / 预期行为

Use Photo and inspect the displayed picture; use Record, then Play and listen to the recording.
Try Test speaker voice/tone if needed. Controls are disabled while busy or unavailable.
用 Photo 查看照片，Record 录音后 Play 回放并亲自听声音；必要时尝试 Test speaker 的 voice/tone。
忙碌或不可用时控件会禁用。
For a guided hardware walkthrough, use [hardware_check](../hardware_check/README.md)。逐项体验硬件功能可运行硬件体检。

## Troubleshooting / 故障处理

If something fails, check the error log, power, connections and matching firmware.
查看错误日志，先查供电、连接与固件配套；没有图片或声音不能通过。
The demo does not automatically retry or support shutdown while running; do not start a second instance.
本示例不自动重试，也不支持运行中关闭；不要启动另一个实例控制相同硬件。
When modifying it, use one coordinating task for camera operations and one owner task for all audio calls;
copy callback images before retaining them and lock LVGL access. Follow the full ownership/cleanup contracts:
[camera](../../docs/api/camera.md), [audio](../../docs/api/audio.md), [display](../../docs/api/display.md).
修改时，由同一管理任务顺序操作摄像头，所有音频调用交给同一音频任务；留用回调图片前先复制，
访问 LVGL 时加锁。资源管理与失败后清理须遵守上述相机、音频、屏幕 API 的完整契约。
Return to official firmware: [Wiki full recovery](https://wiki.orulink.ai/docs/flashing#full), then verify startup/pairing.
返回官方固件直接按 [Wiki 完整恢复](https://wiki.orulink.ai/docs/flashing#full)，再检查启动与配对。
