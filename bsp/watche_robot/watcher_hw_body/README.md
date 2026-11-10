# watcher_hw_body — 机身转动、灯光与触摸

公开 SDK 组件（public SDK）。统一管理与机身控制芯片的连接，提供运动、灯光请求及触摸、连接和动作事件。

## 接口与依赖

- 接口：[`watcher_hw_body.h`](include/watcher_hw_body.h)；参数与错误处理见[使用指南](../../../docs/api/body.md)。
- 依赖：[`mcu_runtime`](../../services/mcu_runtime/README.md)、`mcu_motion_service`、`mcu_led_service`、`mcu_sensor_service` 和 `watcher_hw_core`；内部使用 FreeRTOS、`esp_timer`、`motion_arbiter`。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 使用约束

- 进程内只有一个机身 runtime；初始化返回后可能仍在连接中，操作前检查 READY。禁止另行初始化或轮询 MCU 链路。
- 一个应用任务负责事件消费和订阅变化；主动取事件与回调分发共用 FIFO，二选一。回调中事件仅为借用，需留存则先复制；即使取消订阅，上下文也必须存活到 dispatch 返回。不能递归 dispatch，不能在回调中阻塞等待音频或初始化/关闭 runtime；init/close 会清空订阅。
- 事件丢失锁定 FAULT，拒绝运动和灯光请求；链路就绪时仍可请求 stop。取消所有待执行动作，在回调外 close/init、重新订阅，等待新的 READY 和用户新指令。排空队列或重新连接不会清除此故障，也不得重放旧动作。
- **当前硬件无法实测舵机角度。** 目标值、ACK/DONE、报告的最终角度和 stop 提交成功均不能证明到位或停稳。断开连接的 ESP32 无法发送 Stop；留出完整运动空间并保留人工断电手段。
- 分别检查操作和清理结果；清理失败后重试，不能将错误返回当作资源已释放。

## English

Public SDK for body motion, lights and events. No physical servo-position feedback: ACK/DONE is not proof of arrival or stopping. Keep a single event consumer and require close/init plus fresh user intent after event loss.

第一方代码遵循仓库 [LICENSE](../../../LICENSE)；依赖保留各自许可证。
