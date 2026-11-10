# watcher_hw_core — 设备状态与事件队列

公开 SDK 组件（public SDK）。提供共享状态、事件类型和调用方持有的定长 FIFO 队列；不会启动任何硬件，也没有硬件初始化或关闭接口。

## 接口与依赖

- 接口：[`watcher_hw_core.h`](include/watcher_hw_core.h)；参数与错误处理见[使用指南](../../../docs/api/core.md)。
- 依赖：使用 ESP-IDF `esp_err.h` 和 C 标准类型；未声明其他组件依赖。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 使用约束

- 状态查询返回成功不等于设备就绪；检查返回的状态和错误。
- 队列内存由调用方提供；跨任务共享须自行串行化。先停止所有使用者，再让队列离开作用域；不需要 close/free 接口。
- 检查 push/pop 结果。队列满时保留旧事件、丢弃新事件并累加 dropped；这不替代机身模块的丢事件安全恢复。
- 解释 payload 前核对事件类型和长度，再复制到对齐的结构体。

## English

Public SDK shared types and caller-owned FIFO, not a hardware runtime. Serialize access, keep queue storage alive, check push/pop failures and validate event payloads.

第一方代码遵循仓库 [LICENSE](../../../LICENSE)；依赖保留各自许可证。
