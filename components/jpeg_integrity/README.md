# 检查 JPEG 是否完整

检查图像是否有正确的开头和结尾、是否带有多余尾部数据，并读取或核对图像尺寸。适合排查收到图片却无法解码的问题。

## 最短接入路径

普通应用先使用[拍照与取图使用指南](../../docs/api/camera.md)中的初始化、操作与清理流程；无需为了使用这个功能单独初始化本层。只有维护底层实现时，再从下方头文件查找真实接口。

## 维护时的约定与限制

normalize 返回检查结果与可用长度，不表示重新拍摄或修复图像内容。结构、尺寸检查通过，也不能证明画面正常、清晰或曝光合适；仍需实际查看照片。

- 底层接口：[`hal_camera_jpeg_integrity.h`](include/hal_camera_jpeg_integrity.h)
- [架构与资源配合](../../docs/development.md#architecture) · [依赖与本地适配](../../docs/development.md#dependencies)
- [测试与实际验证范围](../../docs/development.md#testing)

使用完整源码与匹配的示例配置、依赖清单（ESP-IDF 6.0.2）；不承诺本层可从组件仓库独立安装。不要绕过公开接口同时占用共享硬件。已有署名和依赖许可证保持不变。
