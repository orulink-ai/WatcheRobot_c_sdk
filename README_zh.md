[English](README.md) | 简体中文

# WatcheRobot C SDK

使用 `watcher_hw_*` 在 ESP32-S3 上开发自己的机器人应用，控制身体运动、灯光、摄像头、音频和屏幕。
不依赖 Python SDK 或官方应用。**当前为开发预览版，完整配对实机与恢复验收尚未完成。**

## 快速开始

先安装 Git 和 [ESP-IDF 6.0.2（ESP32-S3）](https://docs.espressif.com/projects/esp-idf/zh_CN/v6.0.2/esp32s3/get-started/index.html)，
打开已激活 IDF 环境的终端；`idf.py --version` 应显示 6.0.2。
首次安装或环境报错，请先看[上手指南](docs/getting-started_zh.md)。

在准备存放项目的目录执行：

```sh
git clone https://github.com/orulink-ai/WatcheRobot_c_sdk.git
cd WatcheRobot_c_sdk
idf.py -C examples/robot build
```

预期生成 `examples/robot/build/watcher_hw_robot.bin` 及配套烧录文件；构建需要联网下载组件。
这一步只编译，不写入设备。出错先看[排障说明](docs/getting-started_zh.md#排障与验收边界)。
之后修改 [`examples/robot/main/app_main.c`](examples/robot/main/app_main.c)，再执行同一构建命令。
复现或提交问题时，请记录 `git rev-parse HEAD`；固定版本的方法见上手指南。

**烧录前必读：**核对 ESP32 端口、STM32/Himax 配套固件并备好完整官方恢复包。
完整自定义烧录会覆盖官方配置区，先备份所需数据；准备不全时不要烧录。
当前舵机无物理位置反馈，参考动作可能产生大行程，ACK/DONE 不代表实物停止。
清空完整行程并保留人工断电条件，按[安全烧录与恢复指南](docs/getting-started_zh.md)操作。

## 选择示例

以下目录均为独立 ESP-IDF 工程；将构建命令中的 `robot` 换成对应工程名即可。

| 目标 | 工程 |
| --- | --- |
| 身体运动、灯光与触摸 | [`body`](examples/body) |
| 摄像头、音频与屏幕 | [`head`](examples/head) |
| 组合开发自己的应用 | [`robot`](examples/robot) |
| 在实物上逐项检查硬件 | [`hardware_check`](examples/hardware_check) · [操作指南](docs/hardware-check_zh.md) |

`hardware_check` 是需人工观察确认的体检应用，不是自动通过的单元测试。

## 开发文档

- [上手、烧录与恢复](docs/getting-started_zh.md) · [开环运动与安全限制](docs/servo-open-loop_zh.md)
- [公共 API 头文件](components/sdk) · [旧接口迁移](MIGRATION.md)
- [分支开发、PR 与来源记录](docs/repository-workflow.md)
- 在电脑端使用现有固件开发应用？请用独立的 [Python SDK](https://github.com/orulink-ai/WatcheRobot_python_sdk)。

## 许可

第一方代码采用 [Apache-2.0](LICENSE)，第三方组件与素材保留各自许可。
