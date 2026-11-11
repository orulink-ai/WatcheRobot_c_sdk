# watcher_hw_camera — 拍照与连续取图

公开 SDK 组件（public SDK）。通过回调交付单张或连续 JPEG 图像；保存、显示、上传和 AI 识别由应用负责。

## 接口与依赖

- 接口：[`watcher_hw_camera.h`](include/watcher_hw_camera.h)；参数与错误处理见[使用指南](../../../docs/api/camera.md)。
- 依赖：`watcher_hw_core` 和 [`hal_camera`](../../../components/hal_camera/README.md)。必须启用 `CONFIG_WATCHER_CAMERA_BACKEND_PTL` 并配套匹配的 Himax 摄像头固件。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 使用约束

- 一个应用任务顺序管理初始化、拍照、连续取图、停止与关闭；不得并行打开另一条摄像头连接。
- JPEG 字节仅在回调内有效，需留存则在返回前复制。回调不得阻塞，也不得递归启动、停止或关闭摄像头。
- 连续取图先成功停止再关闭；检查操作与清理结果，清理未完成时重试，不能直接转交资源。
- 状态查询返回成功仅表示取得状态，仍需检查 READY 和错误。照片与实时画面的使用方法见相机指南。

## English

Public SDK for JPEG capture and streaming with paired PTL firmware. Frames are borrowed only during callbacks. Serialize lifecycle operations, stop streaming before close, and check cleanup failures.

第一方代码遵循仓库 [LICENSE](../../../LICENSE)；依赖保留各自许可证。
