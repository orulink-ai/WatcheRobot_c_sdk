# 硬件与配套固件 / Hardware and firmware

本 SDK 的 C 应用运行在头部 ESP32-S3。身体控制和摄像头分别使用独立的 STM32、Himax 固件；运行相应功能前需安装配套固件。

## 运行条件

| 使用的功能 | 需要准备 |
| --- | --- |
| 所有示例 | WatcheRobot 头部、USB 数据线、ESP-IDF 6.0.2 和 ESP32-S3 工具链 |
| 屏幕、音频与摄像头 | 使用示例自带的 PSRAM、驱动及 LVGL 配置 |
| 身体触摸、灯光和运动 | 已连接并供电的身体，以及支持相应功能的 STM32 固件 |
| 拍照与实时画面 | 与 SDK 配套的 Himax PTL 固件 |
| 人脸检测 | 配套 Himax 固件和人脸模型，见[模型安装](model-deployment.md) |

配套固件从 [Releases](https://github.com/orulink-ai/WatcheRobot-public/releases) 获取，按发布说明选择适用版本。完整头部和身体的首次安装见[官方烧录指南](https://wiki.orulink.ai/docs/flashing)。

## 备份与分区检查

SDK 示例使用自己的分区布局。首次完整烧录会替换原应用和分区表，可能覆盖原设备配置；需要保留的数据请先备份。

如需保存完整 ESP32 Flash，可在 IDF 终端执行以下命令，将 PORT 替换为 ESP32 的 SERIAL-B 端口：

```sh
python -m esptool --chip esp32s3 --port PORT -b 460800 read-flash 0 ALL device-backup.bin
```

备份可能包含配网和账号信息，请自行妥善保管。加密设备按其专用备份流程操作。

日常构建和烧录使用[上手教程](getting-started_zh.md)中的 idf.py 命令，由工程自动提供烧录地址。只有设备已采用相同分区布局时，才使用 app-flash 单独更新应用。

恢复官方功能请按[完整恢复流程](https://wiki.orulink.ai/docs/flashing#full)操作；仅写回旧应用不能恢复被替换的分区表和配置。

## English

C applications run on the head's ESP32-S3. Body control requires connected, powered hardware and matching STM32 firmware; camera functions require Himax PTL firmware, and face detection also needs the [model](model-deployment.md). Use the example's supplied board and dependency configuration.

Choose compatible firmware from [Releases](https://github.com/orulink-ai/WatcheRobot-public/releases). Full SDK flashing replaces the installed application and partition table and may overwrite configuration. Back up needed data first; the optional command above saves ESP32 Flash through SERIAL-B.

Use the [first-run tutorial](getting-started.md) for build and flash commands. App-only updates require an unchanged partition layout. To restore official functionality, follow the [complete recovery guide](https://wiki.orulink.ai/docs/flashing#full).
