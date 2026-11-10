# 检查 JPEG 是否完整

检查图像是否有正确的开头和结尾、是否带有多余尾部数据，并读取或核对图像尺寸。适合排查收到图片却无法解码的问题。

内部实现组件（internal implementation）。由摄像头实现使用；公开 SDK 入口为 [`watcher_hw_camera`](../../bsp/watche_robot/watcher_hw_camera/README.md)。

## 接口与依赖

- 接口：[`hal_camera_jpeg_integrity.h`](include/hal_camera_jpeg_integrity.h)
- 依赖：本组件未声明其他组件依赖。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

normalize 返回检查结果与可用长度，不表示重新拍摄或修复图像内容。结构、尺寸检查通过，也不能证明画面正常、清晰或曝光合适；仍需实际查看照片。

许可见仓库 [LICENSE](../../LICENSE)；依赖保留各自许可证。
