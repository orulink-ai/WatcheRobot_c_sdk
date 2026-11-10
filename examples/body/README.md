# body: Touch-controlled lights / 触摸控制灯光

Touch the body to request green lights; release clears the green light and sends a stop request.
The example logs touch events and does **not** automatically start servo movement.
触摸身体时请求亮绿灯，松手时清除绿灯并请求停止；日志记录触摸事件，不会自动启动舵机运动。

## Build / 构建

Install Git and **ESP-IDF 6.0.2**; activate IDF and run from the **repository root**:
安装 Git 和 **ESP-IDF 6.0.2**，激活 IDF 后在**仓库根目录**执行：

```sh
idf.py --version
idf.py -C examples/body build
```

The build should produce `examples/body/build/watcher_hw_body.bin` and the IDF flash files.
Dependency downloads need network access; building does not write to a device.
预期生成上述应用文件及配套烧录文件；下载依赖需要网络，构建不会写入设备。

Target: ESP32-S3, 16 MB flash and custom partitions. No official application source, cloud, model or
Python SDK is needed to build. / 目标为 ESP32-S3、16 MB flash 和自定义分区；构建不需要官方应用源码、云服务、模型或 Python SDK。

Compatible STM32 firmware for body motion, lights and touch is required to run this example.
body defaults do not enable PSRAM. / 运行需要兼容的 STM32 身体固件；body 默认不启用 PSRAM。

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

Before any servo movement, clear the entire possible travel and keep manual power disconnection available.
The application cannot read the angle a servo actually reaches; even a reference move can travel far
from an unknown starting point. ACK/DONE (command received/completion reported), requested angles and
software STOP do not prove actual position or physical stopping. A disconnected ESP32 cannot guarantee stop delivery.
任何舵机运动前清空整个可能行程并保留人工断电；应用不能读取舵机实际转到的角度，
起点未知时，转到参考位置也可能移动很远。ACK/DONE（收到命令／报告命令完成）、目标角度和
软件 STOP 都不证明实际角度或机械已停；ESP32 断连后无法保证停止命令送达。

## Try it / 体验功能

Touch the body: the green light should turn on, then turn off when you release. The serial log should
show the matching `touch=... code=...` events; `light:` and the release-triggered `stop:` should return
`ESP_OK`. A successful request does not prove that the mechanism has physically stopped.
触摸时应亮绿灯，松手后绿灯应熄灭；串口应记录对应的 `touch=... code=...` 事件，
`light:` 和松手后的 `stop:` 请求应返回 `ESP_OK`。请求成功不证明机械已经停止。

For a structured manual pass/fail session, use [hardware_check](../hardware_check/README.md).
Untested is not passed. / 需要逐项验收请使用硬件体检；未测不算通过。

## Change the application / 修改应用

Edit [`main/app_main.c`](main/app_main.c) and rebuild. Keep [`sdkconfig.defaults`](sdkconfig.defaults),
[`partitions.csv`](partitions.csv) and [`main/idf_component.yml`](main/idf_component.yml) together.
For supported versions and configuration, see [dependencies](../../docs/development.md#dependencies).
修改应用入口后重新构建，配套保留配置、分区与依赖清单，不随意替换依赖版本。

## If something fails / 故障处理

Keep error logs and `git rev-parse HEAD`. Check power, cables and matching firmware first; do not force
unready hardware. Missing touch events or incorrect light behavior means this check has not passed.
保留错误日志和源码版本，先检查供电、线缆与固件配套，不强行操作未就绪的硬件；触摸事件缺失或灯光不符不能通过。

If the log reports lost body events, stop operating the controls and investigate power, connections
and firmware. Do not keep touching to unlock controls or automatically retry old actions. Reconnecting
or clearing queued events does not clear the fault. If you write recovery logic, cancel pending actions
and follow the complete [body API recovery procedure](../../docs/api/body.md). Movement afterward
requires a **new user action**; do not separately poll the SDK-managed connection.
日志报告身体事件丢失时，先停止操作，排查供电、连接和固件；不要反复触摸尝试解锁，也不要自动重试旧动作。
重连或清空待处理事件不能解除故障。自行编写恢复逻辑时，取消待执行动作并按身体 API 的完整恢复步骤处理；
重新动作需要**新的用户操作**，不要另行轮询 SDK 已管理的连接。

To return to official firmware, follow the [full official recovery procedure](https://wiki.orulink.ai/docs/flashing#full) and
verify startup/pairing afterward. / 返回官方固件须按 [Wiki 完整恢复](https://wiki.orulink.ai/docs/flashing#full)，再检查启动与配对。

[Examples / 示例](../README.md) · [API guides](../../docs/README.md) · [Tests and evidence](../../docs/development.md#testing)
