# 把机身消息交给对应处理代码

把收到的连接、动作、灯光和传感器消息交给对应处理代码，并协助完成连接后的初始同步。用于维护消息处理流程，不是额外的后台任务。

内部实现组件（internal implementation）。由公开 SDK 的 [`watcher_hw_body`](../../bsp/watche_robot/watcher_hw_body/README.md) 管理读取和生命周期。

## 接口与依赖

- 接口：[`mcu_runtime.h`](include/mcu_runtime.h)
- 依赖：[`mcu_link`](../mcu_link/README.md) 及 `mcu_motion_service`、`mcu_led_service`、`mcu_sensor_service`、`mcu_power_service`。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

这些辅助函数不自己管理轮询或应用策略；公开机身接口负责统一的后台读取与资源管理。触摸数据必须在处理当前消息后、再次轮询前立即复制，避免被下一条消息覆盖。不能在公开机身接口之外再启动一个读取者。

许可见仓库 [LICENSE](../../LICENSE)；依赖保留各自许可证。
