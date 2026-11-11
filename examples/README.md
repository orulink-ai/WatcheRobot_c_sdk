# Examples / 示例

Choose what you want to try. Each project can be built independently.
按功能选择，每个工程都能独立构建。接口调用见[中文使用指南](../docs/getting-started_zh.md) / [API usage](../docs/getting-started.md)。

| I want to… / 我想…… | Project / 工程 |
| --- | --- |
| Display my first text / 显示第一行文字 | [hello_display](hello_display/README.md) |
| Touch the body to change lights / 触摸身体改变灯光 | [body](body/README.md) |
| Take pictures, record/play sound and use screen controls / 拍照、录音播放、操作屏幕 | [head](head/README.md) |
| Combine both / 组合以上功能 | [robot](robot/README.md) |
| Check hardware with operator confirmation / 逐项人工硬件体检 | [hardware_check](hardware_check/README.md) |
| Read model catalog and detect faces / 模型目录与人脸检测 | [English](face_detection/README.md) / [中文教程](face_detection/README_zh.md) |

New users: follow the [first-run tutorial](../docs/getting-started.md) / [完整上手教程](../docs/getting-started_zh.md). Firmware/layout conditions live in [compatibility](../docs/hardware-compatibility.md); function/source/document locations live in the [feature map](../docs/features.md).

## Requirements / 环境要求

Use **ESP-IDF 6.0.2** with ESP32-S3 tools and Git; installation and terminal activation follow the official
[English](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/get-started/index.html) /
[中文](https://docs.espressif.com/projects/esp-idf/zh_CN/v6.0.2/esp32s3/get-started/index.html) instructions.
Use a complete checkout of this repository; no private application source is needed.
安装和激活环境直接参考乐鑫文档；获取本仓库的完整源码即可，不需要私有应用。

## Build / 构建

Run from the **repository root**, in an activated **ESP-IDF 6.0.2** terminal:
在**仓库根目录**、已激活 **ESP-IDF 6.0.2** 的终端运行：

```sh
idf.py -C examples/body build
```

Replace `body` with the chosen project. Output goes to its `build/` directory, including
`watcher_hw_body.bin` for body and the IDF flash files. Building downloads dependencies over the network
and does not write to a device. / 将 `body` 换成所选工程；构建产物位于该工程的 `build/`。
依赖下载需要网络，构建不会写入设备。

All examples select ESP32-S3, 16 MB flash and custom partitions. Head/display/vision examples enable
80 MHz octal PSRAM and LVGL 8.4.0. Body control needs compatible STM32 firmware; camera use needs
matching Himax PTL firmware. / 所有示例选择 ESP32-S3、16 MB flash 和自定义分区；头部相关工程启用
八线 PSRAM。身体与摄像功能分别需要兼容的 STM32 和 Himax PTL 固件。

Edit the project's `main/app_main.c`; keep its defaults, partitions and dependency manifest together.
The body and robot examples do not automatically start servo movement.
修改所选工程的 `main/app_main.c`，配套保留配置、分区与依赖清单。body/robot 不会自动启动舵机运动。

## Before flash or movement / 烧录或运动前

Connect the head's USB data port and choose **SERIAL-B (ESP32)**. First flashing replaces the installed application and partition table; back up data you need. Run from the repository root, replacing body with your example and PORT with its ESP32 port:
连接头部数据 USB，选择 **SERIAL-B（ESP32）**。首次烧录会替换原应用和分区，需保留的数据请先备份。在仓库根目录运行，将 body 换为所选示例，PORT 换为实际端口：

```sh
idf.py -C examples/body -p PORT flash monitor
```

Press Ctrl+] to leave the monitor. For setup and recovery, see [first run](../docs/getting-started.md) / [上手教程](../docs/getting-started_zh.md).

Before moving, clear the full travel area and keep power disconnection available. Servos have no actual-position feedback; software STOP cannot replace an emergency power cut. See [motion safety](../docs/api/body.md#motion-safety-english).
运动前清空完整行程并保留人工断电手段。舵机没有实际位置反馈，软件 STOP 不代替断电急停；详见[运动注意事项](../docs/api/body.md#motion-safety)。

## Shared code and further reading / 共享代码与参考

[common](common/README.md) contains shared example code, **not** an independent project or public SDK API.
Do not run `idf.py -C examples/common build`.
common 不是独立工程或公开 SDK 接口，不要单独构建。

[API guides](../docs/api/README.md) · [Contributing](../CONTRIBUTING.md) · [Dependencies](README.md#requirements--环境要求)
