[English](README.md) | 简体中文

# WatcheRobot C SDK

在 ESP32-S3 上使用 `watcher_hw_*` 编写自己的机器人应用，控制身体、灯光、摄像头、音频与显示。
无需 Python SDK 或官方应用源码。**开发预览：配对实机与完整恢复验收仍未完成。**

## 从源码开始

安装 Git 与 [ESP-IDF 6.0.2（ESP32-S3）](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/get-started/index.html)，
在已激活 IDF 的终端检查 `idf.py --version`。首次安装或报错先看[上手指南](docs/getting-started_zh.md)。
在准备存放工程的目录执行：

```sh
git clone https://github.com/orulink-ai/WatcheRobot_c_sdk.git
cd WatcheRobot_c_sdk
idf.py -C examples/robot build
```

预期生成 `examples/robot/build/watcher_hw_robot.bin` 与配套烧录文件。组件下载需要网络；此命令只构建，不写入设备。
修改 [`examples/robot/main/app_main.c`](examples/robot/main/app_main.c) 后重复构建。
复现或反馈时记录 `git rev-parse HEAD`，按[指南](docs/getting-started_zh.md)固定经过审阅的公开提交。
构建与测试证据及实机验收边界见[测试说明](docs/testing.md)。

**烧录前必须确认：**ESP32 端口、配套 STM32/Himax 固件及完整官方恢复包。
首次完整自定义烧录会覆盖官方配置，先备份所需数据；配套或恢复资料不明时停止。
舵机**没有物理位置反馈**，参考动作可能是大行程；ACK/DONE 不证明真实位置或停止。
清空整个行程，保持人工断电可用，遵循[安全烧录与恢复指南](docs/getting-started_zh.md)。

## 兼容与实际配置

| 项目 | 当前源码合同 |
| --- | --- |
| 目标 | ESP32-S3 |
| ESP-IDF | 精确 6.0.2，其他版本由构建入口拒绝 |
| LVGL | 头部/显示示例固定 8.4.0；不承诺 LVGL 9 |
| Flash | 四个示例均配置 16 MB 和自定义分区；不是测得的最小容量 |
| PSRAM | head/robot/hardware_check 启用 80 MHz 八线 PSRAM；body 默认不启用 |
| 配套 | 身体需兼容 STM32；摄像头需匹配 Himax PTL，须单独核验 |

## 能力

| 模块 | 提供什么 | 使用说明 |
| --- | --- | --- |
| body | 运动命令、灯光、触摸/链路事件；无物理位置反馈 | [Body API](docs/api/body.md) |
| camera | 配套 PTL JPEG 拍照/流；无模型或网络策略 | [Camera API](docs/api/camera.md) |
| audio | 16/24 kHz、16 位单声道 PCM 录放音 | [Audio API](docs/api/audio.md) |
| display | LVGL 显示、面板/触控借用句柄及锁 | [Display API](docs/api/display.md) |
| core | 生命周期状态类型、事件与调用者持有的有界 FIFO | [Core API](docs/api/core.md) |

## 选择示例

每个目录都是独立 ESP-IDF 工程，在上述命令中替换 `robot` 即可。

| 目标 | 工程 |
| --- | --- |
| 身体灯光与触摸事件 | [body](examples/body/README.md) |
| 摄像头、音频与显示 | [head](examples/head/README.md) |
| 身体与头部组合 | [robot](examples/robot/README.md) |
| 逐项人工硬件体检 | [hardware_check](examples/hardware_check/README.md) · [操作指南](docs/hardware-check_zh.md) |

`hardware_check` 需人工观察；未测不算通过，不是自动通过的单元测试。
[common](examples/common/README.md) 是示例内部共享代码，不是第五个应用。

## 开发导航

- [文档索引](docs/README.md) · [架构](docs/architecture.md) · [依赖](docs/dependencies.md)
- [无反馈运动安全](docs/servo-open-loop_zh.md) · [旧 API 迁移](docs/migration.md)
- [贡献](docs/contributing.md) · [测试与报告](docs/testing.md) · [来源](docs/provenance.md)
- [组件打包状态](docs/registry-publishing.md)：尚无已验证正式发布的 Registry 安装入口，当前使用源码流程。
- 在电脑上基于现有固件开发？使用独立的 [Python SDK](https://github.com/orulink-ai/WatcheRobot_python_sdk)。

## 许可

第一方代码采用 [Apache-2.0](LICENSE)。第三方组件和资源保留各自的许可证与署名。
