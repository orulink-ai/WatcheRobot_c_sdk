# head: Pictures, recording and playback / 拍照与录音播放

Try Photo, record microphone audio, play it back and test the speaker through the screen controls.
用屏幕上的 Photo 拍照、Record 录音、Play 回放，也可测试扬声器。

## Build / 构建

Install Git and **ESP-IDF 6.0.2**; activate IDF and run from the **repository root**:
安装 Git 和 **ESP-IDF 6.0.2**，激活 IDF 后在**仓库根目录**执行：

```sh
idf.py --version
idf.py -C examples/head build
```

The build should produce `examples/head/build/watcher_hw_head.bin` and the IDF flash files.
Dependency downloads need network access; building does not write to a device.
预期生成上述应用文件及配套烧录文件；下载依赖需要网络，构建不会写入设备。

Target: ESP32-S3, 16 MB flash and custom partitions. No official application source, cloud, model or
Python SDK is needed to build. / 目标为 ESP32-S3、16 MB flash 和自定义分区；构建不需要官方应用源码、云服务、模型或 Python SDK。

This project enables 80 MHz octal PSRAM and LVGL 8.4.0. The camera needs matching Himax PTL firmware.
本工程启用 80 MHz 八线 PSRAM 与 LVGL 8.4.0；摄像需要匹配的 Himax PTL 固件。

## Before flashing / 烧录前

Complete the [English safety checklist and recovery guide](../README.md) /
[中文安全检查与恢复指南](../README.md). Verify the ESP32 port, compatible paired
firmware, backups and a complete official restore bundle. Full custom flash overwrites official
configuration; an app-only flash cannot restore the official partition layout. Unknown compatibility
or missing recovery assets means stop. Do not guess offsets, write an app-only binary at `0x0` or use
`erase-flash` as troubleshooting. Use the official ESP-IDF flash/monitor workflow for this project after completing the checks.

先核实 ESP32 端口、兼容配套固件、备份与完整官方恢复包；完整自定义烧录会覆盖官方配置，
只刷应用无法恢复官方分区。条件不明时停止，不猜偏移、不从 `0x0` 写应用单文件、不用整片擦除排障。
完成检查后，按乐鑫官方烧录与监视流程对本工程操作。

This example does not drive body motion. If you add motion yourself, first read the
[movement safety guide](../../docs/servo-open-loop.md).
本示例不驱动身体运动。若自行加入运动，请先阅读[运动安全指南](../../docs/servo-open-loop_zh.md)。

## Try it / 体验功能

Use Photo and check the displayed picture. Use Record, then Play and listen to the recording.
Try Test speaker voice/tone if needed. Controls are disabled while busy or unavailable. A completed
progress bar does not prove image or sound quality.
查看照片，录音后回放并亲自听声音；必要时尝试 Test speaker 的 voice/tone。
忙碌或不可用时控件会禁用；进度完成不代表图像或声音质量通过。

For a structured manual pass/fail session, use [hardware_check](../hardware_check/README.md).
Untested is not passed. / 需要逐项验收请使用硬件体检；未测不算通过。

## Change the application / 修改应用

Edit [`main/app_main.c`](main/app_main.c) and rebuild. Keep [`sdkconfig.defaults`](sdkconfig.defaults),
[`partitions.csv`](partitions.csv) and [`main/idf_component.yml`](main/idf_component.yml) together.
For supported versions and configuration, see [dependencies](../../docs/development.md#dependencies).
修改应用入口后重新构建，配套保留配置、分区与依赖清单，不随意替换依赖版本。

## If something fails / 故障处理

Keep error logs and `git rev-parse HEAD`. Check power, cables and matching firmware first; do not force
unready hardware. No image or audible sound is not a pass.
保留错误日志和源码版本，先检查供电、线缆与固件配套，不强行操作未就绪的硬件；没有图片或声音不能通过。

Save the error log; do not repeatedly start another instance controlling the same hardware.
This simple demo does not automatically retry or support shutdown while running.
保存错误日志，不要重复启动另一个实例控制相同硬件；简单示例不自动重试，也不支持运行中关闭。

To return to official firmware, follow the [full official recovery procedure](https://wiki.orulink.ai/docs/flashing#full) and
verify startup/pairing afterward. / 返回官方固件须按 [Wiki 完整恢复](https://wiki.orulink.ai/docs/flashing#full)，再检查启动与配对。

### When modifying the example / 修改示例时注意

Keep audio operations in one task. Copy camera callback images before retaining them, and lock LVGL
access. Follow the ownership and shutdown rules in the [camera](../../docs/api/camera.md),
[audio](../../docs/api/audio.md) and [display](../../docs/api/display.md) API guides.
音频操作交给同一任务；需要留用摄像头回调图片时先复制，访问 LVGL 时加锁。
设备由谁管理、如何关闭，以相机、音频和屏幕 API 的完整使用规则为准。

[Examples / 示例](../README.md) · [API guides](../../docs/README.md) · [Tests and evidence](../../docs/development.md#testing)
