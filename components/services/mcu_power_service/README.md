# 请求开关机身的 5V 供电

向机身控制芯片发送 5V 开关请求，并标记请求来自哪一类使用者。只有维护底层供电控制时才直接使用。

内部实现组件（internal implementation）。公开 SDK 的 [`watcher_hw_body`](../../sdk/watcher_hw_body/README.md) 不提供 5V 开关；维护本层需先确定唯一通信管理方。

## 接口与依赖

- 接口：[`mcu_power_service.h`](include/mcu_power_service.h)
- 依赖：[`mcu_link`](../../protocols/mcu_link/README.md)。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

这是底层接口；公开机身接口没有对应的 5V 开关函数，不能据此推断可直接在公开接口上调用。消息发送成功不等于电路已物理断开，更不能替代操作人员可立即执行的人工断电。不要与公开机身接口争用底层连接。

许可见仓库 [LICENSE](../../../LICENSE)；依赖保留各自许可证。
