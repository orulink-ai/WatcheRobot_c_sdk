# 检查图像的编号、时间和完整性

为传来的图像附上编号、时间和校验信息，并检查收到的数据是否符合约定。需要排查丢帧、重复帧或损坏数据时，阅读这一层。

内部实现组件（internal implementation）。由摄像头传输实现使用；公开 SDK 入口为 [`watcher_hw_camera`](../../bsp/watche_robot/watcher_hw_camera/README.md)。

## 接口与依赖

- 接口：[`hx_media_protocol.h`](include/hx_media_protocol.h)
- 依赖：本组件未声明其他组件依赖；与 [`hx_ptl_protocol`](../hx_ptl_protocol/README.md) 配合使用。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

协议是两端对消息格式的约定。这里处理随图像发送的 16 字节附加头；多字节数字按低字节在前的顺序存放。图像类型与长度仍由 PTL 的基础消息头负责。校验和可用于发现传输损坏，不是图像清晰度验收。

许可见仓库 [LICENSE](../../LICENSE)；依赖保留各自许可证。
