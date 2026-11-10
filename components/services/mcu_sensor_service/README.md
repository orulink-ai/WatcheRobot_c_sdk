# 保存机身触摸和传感器消息

处理机身传来的触摸、磁场和惯性传感器数据，并保存最新状态。需要维护消息解析或查阅底层数据结构时阅读。

内部实现组件（internal implementation）。公开 SDK 入口为 [`watcher_hw_body`](../../sdk/watcher_hw_body/README.md)。

## 接口与依赖

- 接口：[`mcu_sensor_service.h`](include/mcu_sensor_service.h)
- 依赖：[`mcu_link`](../../protocols/mcu_link/README.md)。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

最新状态可能被后续消息覆盖；处理触摸事件时要在下一次轮询前复制当前状态。公开机身接口只承诺其头文件中的事件，不因这里存在磁场/惯性结构体就自动增加公开订阅功能。这些传感器数据也不是舵机角度实测反馈。

许可见仓库 [LICENSE](../../../LICENSE)；依赖保留各自许可证。
