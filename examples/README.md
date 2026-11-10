# Examples / 示例

Choose what you want to try. Each project can be built independently.
按功能选择，每个工程都能独立构建。接口调用见[中文使用指南](../docs/getting-started_zh.md) / [API usage](../docs/getting-started.md)。

| I want to… / 我想…… | Project / 工程 |
| --- | --- |
| Touch the body to change lights / 触摸身体改变灯光 | [body](body/README.md) |
| Take pictures, record/play sound and use screen controls / 拍照、录音播放、操作屏幕 | [head](head/README.md) |
| Combine both / 组合以上功能 | [robot](robot/README.md) |
| Check hardware with operator confirmation / 逐项人工硬件体检 | [hardware_check](hardware_check/README.md) |

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

All examples select ESP32-S3, 16 MB flash and custom partitions. head/robot/hardware_check enable
80 MHz octal PSRAM and LVGL 8.4.0. Body control needs compatible STM32 firmware; camera use needs
matching Himax PTL firmware. / 所有示例选择 ESP32-S3、16 MB flash 和自定义分区；头部相关工程启用
八线 PSRAM。身体与摄像功能分别需要兼容的 STM32 和 Himax PTL 固件。

Edit the project's `main/app_main.c`; keep its defaults, partitions and dependency manifest together.
The body and robot examples do not automatically start servo movement.
修改所选工程的 `main/app_main.c`，配套保留配置、分区与依赖清单。body/robot 不会自动启动舵机运动。

## Before flash or movement / 烧录或运动前

Verify the ESP32 **SERIAL-B** port (not the STM32/Himax port), compatible paired firmware, its version and image hashes, and
backups and a complete official restore bundle. Full custom flash overwrites official `agentcfg` (0x12000–0x20000);
app-only restoration is insufficient. Stop if compatibility or recovery assets are unknown. Do not guess offsets, write an app-only image at `0x0`, or use `erase-flash` for troubleshooting.
Return to official firmware using the [Wiki full recovery procedure](https://wiki.orulink.ai/docs/flashing#full), then verify official startup and pairing. A handshake or filename alone does not prove compatibility.
Servos have no physical position feedback; reference movement can be large. Clear the entire travel
and keep manual power disconnection available. ACK/DONE/software STOP do not prove physical stopping.

先核实 ESP32 的 **SERIAL-B** 接口及实际端口，不要使用 STM32/Himax 端口。记录板卡与配套固件版本、镜像哈希；文件名或握手成功不证明兼容。
准备备份与已核实的完整官方恢复包；缺少时停止。完整自定义烧录会覆盖官方 `agentcfg`（0x12000–0x20000），只刷应用不足以恢复官方布局。
不要猜偏移、从 `0x0` 写入应用单文件，或用 `erase-flash` 排障。
返回官方固件按 [Wiki 完整恢复流程](https://wiki.orulink.ai/docs/flashing#full)，不是只刷应用；恢复后检查官方启动与配对。
资料不明时停止。舵机无物理位置反馈，参考动作也可能大行程；清空整个行程并保留人工断电，不能靠软件完成状态判断机械停止。

For writing and monitoring a built example, follow the official [ESP-IDF flash/monitor instructions](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/get-started/index.html#flash-onto-the-device) with that example as the project. Full custom flash uses its generated bootloader, partition table and application.
App-only updates are appropriate **only after verifying the device already uses the same custom partition layout**; local files alone do not prove the device layout.
烧录与串口监视按乐鑫官方流程对所选工程操作；完整自定义烧录使用该工程生成的引导程序、分区表和应用。仅在核实设备已采用相同自定义分区后才可单独更新应用；不确定或刷回过官方固件时重新做上述检查。

## Shared code and further reading / 共享代码与参考

[common](common/README.md) contains shared example code, **not** an independent project or public SDK API.
Do not run `idf.py -C examples/common build`.
common 不是独立工程或公开 SDK 接口，不要单独构建。

[API guides](../docs/README.md) · [Tests and evidence](../docs/development.md#testing) · [Dependencies](../docs/development.md#dependencies)
