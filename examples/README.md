# Examples / 示例

Choose what you want to try. Each project can be built independently.
按功能选择，每个工程都能独立构建。首次使用先看[中文上手](../docs/getting-started_zh.md) / [English setup](../docs/getting-started.md)。

| I want to… / 我想…… | Project / 工程 |
| --- | --- |
| Touch the body to change lights / 触摸身体改变灯光 | [body](body/README.md) |
| Take pictures, record/play sound and use screen controls / 拍照、录音播放、操作屏幕 | [head](head/README.md) |
| Combine both / 组合以上功能 | [robot](robot/README.md) |
| Check hardware with operator confirmation / 逐项人工硬件体检 | [hardware_check](hardware_check/README.md) |

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

Follow the [English safety checklist and recovery](../docs/getting-started.md) /
[中文安全检查与恢复](../docs/getting-started_zh.md). Verify the ESP32 port, compatible paired firmware,
backups and a complete official restore bundle. Full custom flash overwrites official configuration;
app-only restoration is insufficient. Stop if compatibility or recovery assets are unknown.
Servos have no physical position feedback; reference movement can be large. Clear the entire travel
and keep manual power disconnection available. ACK/DONE/software STOP do not prove physical stopping.

先核实 ESP32 端口、兼容固件、备份与完整官方恢复包；完整自定义烧录会覆盖官方配置，只刷应用不足以恢复。
资料不明时停止。舵机无物理位置反馈，参考动作也可能大行程；清空整个行程并保留人工断电，不能靠软件完成状态判断机械停止。

## Shared code and further reading / 共享代码与参考

[common](common/README.md) contains shared example code, **not** an independent project or public SDK API.
Do not run `idf.py -C examples/common build`.
common 不是独立工程或公开 SDK 接口，不要单独构建。

[API guides](../docs/README.md) · [Tests and evidence](../docs/testing.md) · [Dependencies](../docs/dependencies.md)
