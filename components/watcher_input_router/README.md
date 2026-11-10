# 决定旋钮和按键交给哪个界面或功能

根据当前使用场景，把旋转、按下、短按和长按交给界面、应用或系统，避免一个操作被多个功能同时解释。维护按键与界面切换时阅读。

内部实现组件（internal implementation）。这是输入策略辅助层，不是公开屏幕按键订阅接口；公开显示入口为 [`watcher_hw_display`](../../bsp/watche_robot/watcher_hw_display/README.md)。

## 接口与依赖

- 接口：[`watcher_input_router.h`](include/watcher_input_router.h)
- 依赖：内部使用 FreeRTOS；不直接接管硬件输入驱动。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

场景与 owner 表示这次输入应该由谁处理，不是硬件资源转让。例如按下后切换界面，松开时不能不加判断地当作新界面的点击。维护时保留作用域校验和取消事件逻辑；这只是输入辅助层，不是新的机器人应用或公开屏幕按键订阅接口。

许可见仓库 [LICENSE](../../LICENSE)；依赖保留各自许可证。
