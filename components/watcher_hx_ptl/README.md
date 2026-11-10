# 从摄像头芯片接收图像并查看传输故障

在主芯片一侧接收、检查摄像头图像，并记录超时、损坏和丢帧等诊断数据。排查图像传输问题时阅读。

内部实现组件（internal implementation）。由 [`hal_camera`](../hal_camera/README.md) 使用；公开 SDK 入口为 [`watcher_hw_camera`](../../bsp/watche_robot/watcher_hw_camera/README.md)。

## 接口与依赖

- 接口：[`watcher_hx_ptl.h`](include/watcher_hx_ptl.h)
- 依赖：ESP-IDF GPIO/SPI/UART 驱动、`esp_timer`、FreeRTOS、`heap`、`log`，以及 `esp_io_expander`、`sensecap-watcher`、[`hx_media_protocol`](../hx_media_protocol/README.md) 和 [`hx_ptl_protocol`](../hx_ptl_protocol/README.md)。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

摄像头独立固件必须另外配套；这里不包含 Himax 芯片端固件。PTL 是两端的图像传输规则。本层读取返回的 JPEG 引用只保持到下次读取或关闭，公开摄像头回调则要求返回前复制。与 SSCMA 摄像头通路不能同时使用；控制串口 UART1 与维护烧录互斥，切换模式前先停止读图。控制停止失败时仍可能保留清理责任，不能直接转交使用权。

许可见仓库 [LICENSE](../../LICENSE)；依赖保留各自许可证。
