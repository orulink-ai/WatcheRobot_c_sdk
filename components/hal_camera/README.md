# 连接摄像头硬件

把拍照和连续取图请求接到摄像头硬件。应用只要获取 JPEG 图像即可，不需要自行管理底层传输。

内部实现组件（internal implementation）。由公开 SDK 的 [`watcher_hw_camera`](../../bsp/watche_robot/watcher_hw_camera/README.md) 使用；应用不应另开摄像头连接。

## 接口与依赖

- 接口：[`hal_camera.h`](include/hal_camera.h)
- 依赖：`sensecap-watcher`、`sscma_client`、`mbedtls`、`esp_timer`、[`watcher_hx_ptl`](../watcher_hx_ptl/README.md)、`hx_media_protocol`、`hx_ptl_protocol` 和 `jpeg_integrity`。构建按 `CONFIG_WATCHER_CAMERA_BACKEND_PTL` 选择实现。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

公开摄像头接口要求配套 Himax 固件，且启用 PTL：这是主芯片与摄像头芯片约定的图像传输规则。源码中的其他实现不构成公开接口兼容承诺。不要在公开接口打开时另外启动读图任务；图像数据的有效期与停止/关闭要求见[摄像头使用指南](../../docs/api/camera.md)。

许可见仓库 [LICENSE](../../LICENSE)；依赖保留各自许可证。
