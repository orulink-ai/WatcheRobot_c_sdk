# robot: Pictures, sound and touch-controlled lights / 拍照、声音与触摸灯光

Combine the photo/audio screen with touch-controlled body lights. This example does **not**
automatically start servo movement.
将拍照、录放音界面与身体触摸灯光组合；不会自动启动舵机运动。

## Build / 构建

Install Git and **ESP-IDF 6.0.2**; activate IDF and run from the **repository root**:
安装 Git 和 **ESP-IDF 6.0.2**，激活 IDF 后在**仓库根目录**执行：

```sh
idf.py --version
idf.py -C examples/robot build
```

The build should produce `examples/robot/build/watcher_hw_robot.bin` and the IDF flash files.
Dependency downloads need network access; building does not write to a device.
预期生成上述应用文件及配套烧录文件；下载依赖需要网络，构建不会写入设备。

Target: ESP32-S3, 16 MB flash and custom partitions. No official application source, cloud, model or
Python SDK is needed to build. / 目标为 ESP32-S3、16 MB flash 和自定义分区；构建不需要官方应用源码、云服务、模型或 Python SDK。

Compatible STM32 body firmware and matching Himax PTL camera firmware are required.
This project enables 80 MHz octal PSRAM and LVGL 8.4.0.
运行需要兼容的 STM32 身体固件和 Himax PTL 摄像固件；工程启用 80 MHz 八线 PSRAM 与 LVGL 8.4.0。

## Before flashing / 烧录前

Complete the [English safety checklist and recovery guide](../../docs/build-and-flash.md) /
[中文安全检查与恢复指南](../../docs/build-and-flash_zh.md). Verify the ESP32 port, compatible paired
firmware, backups and a complete official restore bundle. Full custom flash overwrites official
configuration; an app-only flash cannot restore the official partition layout. Unknown compatibility
or missing recovery assets means stop. Do not guess offsets, write an app-only binary at `0x0` or use
`erase-flash` as troubleshooting. Then use the guide's flash/monitor commands with **`robot`** as the project name.

先核实 ESP32 端口、兼容配套固件、备份与完整官方恢复包；完整自定义烧录会覆盖官方配置，
只刷应用无法恢复官方分区。条件不明时停止，不猜偏移、不从 `0x0` 写应用单文件、不用整片擦除排障。
完成检查后，使用指南中的烧录、监视命令，工程名改为 **`robot`**。

Before any servo movement, clear the entire possible travel and keep manual power disconnection available.
The application cannot read the angle a servo actually reaches; even a reference move can travel far
from an unknown starting point. ACK/DONE (command received/completion reported), requested angles and
software STOP do not prove actual position or physical stopping. A disconnected ESP32 cannot guarantee stop delivery.
任何舵机运动前清空整个可能行程并保留人工断电；应用不能读取舵机实际转到的角度，
起点未知时，转到参考位置也可能移动很远。ACK/DONE（收到命令／报告命令完成）、目标角度和
软件 STOP 都不证明实际角度或机械已停；ESP32 断连后无法保证停止命令送达。

## Try it / 体验功能

Use Photo, then Record and Play; check the picture and listen to the sound. Touch the body to request
green lights; release clears the green light and requests stop. Check the touch/light/stop logs.
Disabled controls, playback progress and ACK/DONE logs are not physical acceptance.
拍照并录音回放，亲自检查照片和声音；触摸身体请求绿灯，松手清除绿灯并请求停止，同时查看日志。
禁用控件、播放进度和 ACK/DONE 都不能当作实机通过。

For a structured manual pass/fail session, use [hardware_check](../hardware_check/README.md).
Untested is not passed. / 需要逐项验收请使用硬件体检；未测不算通过。

## Change the application / 修改应用

Edit [`main/app_main.c`](main/app_main.c) and rebuild. Keep [`sdkconfig.defaults`](sdkconfig.defaults),
[`partitions.csv`](partitions.csv) and [`main/idf_component.yml`](main/idf_component.yml) together.
For supported versions and configuration, see [dependencies](../../docs/dependencies.md).
修改应用入口后重新构建，配套保留配置、分区与依赖清单，不随意替换依赖版本。

## If something fails / 故障处理

Keep error logs and `git rev-parse HEAD`. Check power, cables and matching firmware first; do not force
unready hardware. No image or audible sound is not a pass.
保留错误日志和源码版本，先检查供电、线缆与固件配套，不强行操作未就绪的硬件；没有图片或声音不能通过。

If the log reports lost body events, stop operating the controls and investigate power, connections
and firmware. Do not keep touching to unlock controls or automatically retry old actions. Reconnecting
or clearing queued events does not clear the fault. If you write recovery logic, cancel pending actions
and follow the complete [body API recovery procedure](../../docs/api/body.md); movement afterward
requires a **new user action**. Do not separately poll the SDK-managed connection.
The photo/audio demo does not automatically retry or support shutdown while running; do not start
a second instance controlling the same devices. For modifications, see the
[camera/audio/display guides](../../docs/README.md).
日志报告身体事件丢失时，先停止操作，排查供电、连接和固件；不要反复触摸尝试解锁，也不要自动重试旧动作。
重连或清空待处理事件不能解除故障。自行编写恢复逻辑时，取消待执行动作并按身体 API 的完整恢复步骤处理；
重新动作需要**新的用户操作**，不要另行轮询 SDK 已管理的连接。
拍照音频示例不自动重试，也不支持运行中关闭；不要启动另一个控制同一硬件的实例。修改时参阅相机、音频和屏幕 API。

To return to official firmware, follow the setup guide's **full official recovery** procedure and
verify startup/pairing afterward. / 返回官方固件须按上手指南完整恢复，再检查启动与配对。

[Examples / 示例](../README.md) · [API guides](../../docs/README.md) · [Tests and evidence](../../docs/testing.md)
