[English](README.md) | 简体中文

# WatcheRobot C SDK（开发预览）

使用 `watcher_hw_*` 编写自己的 `app_main`；不需要官方应用、Python SDK、Daemon、
服务端、SD 卡或模型。本仓库是纯硬件源码交付快照，**不是稳定发布或完整配对实机验收**。

## 从这里开始

1. [固定公开版本、安装 ESP-IDF 6.0.2 并构建](docs/getting-started_zh.md)。
2. [执行 8 组／26 细项硬件体检](docs/hardware-check_zh.md)。
3. 修改 `examples/robot/main/app_main.c`，在公开仓库根目录执行
   `idf.py -C examples/robot build`。

烧录会替换自定义 ESP32 应用／分区并可能覆盖存储，先确认实际 ESP32 端口和
STM32/Himax 配对镜像。首次准备、日常自定义烧录、官方恢复与预期结果见上手指南。
当前舵机**没有物理位置反馈**；从未知起点到 X90/Y120 参考姿态可能是大行程，
ACK/DONE 不等于位置测量或机械停止证明。

## 你想做什么？

| 目标 | 入口 |
| --- | --- |
| 一次一个细项地安全检查实物 | [硬件体检](docs/hardware-check_zh.md) |
| 构建／烧录／恢复／创建自己的工程 | [上手指南](docs/getting-started_zh.md) |
| 迁移旧名称 | [命名与丢事件迁移](MIGRATION.md) |
| 理解无反馈运动 | [当前硬件合同](docs/servo-open-loop_zh.md) |
| 阅读公共头文件 | `components/sdk/watcher_hw_{core,body,camera,audio,display}/include/` |
| 了解所有权、锁与事件溢出 | 头文件、[审计](AUDIT.md)、[上手](docs/getting-started_zh.md) |
| 查看真实证据 | [历史验收](VALIDATION.md)、[历史公开同步记录](SYNC_VALIDATION.md) |
| 在电脑上开发现有官方固件应用 | [Python SDK](https://github.com/orulink-ai/WatcheRobot_python_sdk/blob/main/README.zh-CN.md)，与 C 路线分开 |

`examples/body`、`head`、`robot`、`hardware_check` 是四个独立 ESP-IDF 工程。
`examples/common` 包含共享 UI、纯状态机、开环身体适配器及 CC0 测试语音。
不能 include 官方固件顶层工程。

## 来源、公开边界与许可

[SOURCE.json](SOURCE.json) 固定上游 ESP32
`e23bee2a642f6c90753b370cb18c46815e0c8f58`，记录逐文件来源与输出哈希。
公开 checkout commit 才是交付版本；内部 SHA 仅用于追溯，不要求读者访问私库。
本独立仓库仅迁入原先已经公开的 SDK 快照，没有额外公开内部源码。历史导出工具
未随本次源码导入迁入，也不是构建前提。迁移基线、文件哈希含义及分支／PR 贡献方式见
[仓库开发流程与来源](docs/repository-workflow.md)。
不导出官方应用／云／语音业务服务、模型、凭据、固件二进制或下载／生成目录。

第一方代码采用 [Apache-2.0](LICENSE)。
Seeed、SSCMA、codec、expander、Espressif 等保留原版权与许可，注册表依赖维持各自许可。
这是交付快照而非独立维护分叉，修复应回流上游。历史名称与哈希按原记录保留，
不能冒充改名后重新实测。完整实机配对、机械安全与恢复验收仍未完成，
不宣称稳定 v1，不更新生产。本仓库尚未建立自己的 CI；历史 CI 记录不代表
当前独立仓库已通过自动验证。
