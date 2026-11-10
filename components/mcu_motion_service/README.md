# 发送动作并跟踪指令应答

把转动请求发给机身控制芯片，并提供“已接收”“已结束”或故障等指令状态。需要维护动作提交与状态关联时阅读。

内部实现组件（internal implementation）。公开 SDK 入口为 [`watcher_hw_body`](../../bsp/watche_robot/watcher_hw_body/README.md)。

## 接口与依赖

- 接口：[`mcu_motion_service.h`](include/mcu_motion_service.h)
- 依赖：[`mcu_link`](../mcu_link/README.md) 和 [`motion_arbiter`](../motion_arbiter/README.md)。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

ACK/DONE 是对端的指令应答，不是实际角度或物理停止测量；当前硬件无法实测舵机位置，旧位置查询返回 ESP_ERR_NOT_SUPPORTED。观察令牌用于关联一条动作或停止请求：检查状态并释放令牌后再提交下一条，未收到 DONE 不能当作完成。停止观察完成仅表示匹配的成功 ACK，不是实际停稳。底层动作回调在通信任务中执行，必须不阻塞，且不能在回调内注册/注销自身。始终保留人工断电手段。

许可见仓库 [LICENSE](../../LICENSE)；依赖保留各自许可证。
