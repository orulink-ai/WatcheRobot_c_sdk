# 识别并检查传来的图像消息

从摄像头传来的数据中识别一张图像的边界，检查消息和 JPEG，并在边界丢失时重新寻找下一条消息的开头。排查传输格式问题时使用。

内部实现组件（internal implementation）。由摄像头传输实现使用；公开 SDK 入口为 [`watcher_hw_camera`](../sdk/watcher_hw_camera/README.md)。

## 接口与依赖

- 接口：[`hx_ptl_protocol.h`](include/hx_ptl_protocol.h)
- 依赖：[`hx_media_protocol`](../hx_media_protocol/README.md)。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

PTL 是两颗芯片共同遵守的图像传输规则，不是图像识别功能。这里包含基础消息头、JPEG 数据包检查、重新寻找消息边界和控制消息解析工具。检查消息合法不能证明照片清晰或实际摄像头已经验收。解析得到的图像指针引用输入数据，使用期间必须保留输入内存。

许可见仓库 [LICENSE](../../LICENSE)；依赖保留各自许可证。
