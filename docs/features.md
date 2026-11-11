# 功能与调用入口 / Feature guide

按要实现的功能查找接口和使用说明。首次使用请先完成[上手教程](getting-started_zh.md)；完整工程见[示例目录](../examples/README.md)。

Find an API and guide for the feature you want to build. Start with the [first-run tutorial](getting-started.md), or choose a runnable project from [examples](../examples/README.md).

## 应用接口 / Application APIs

| 功能 / Feature | 主要调用入口 / API entry | 使用说明 / Guide |
| --- | --- | --- |
| 屏幕文字、按钮与触摸 / Display and screen touch | `watcher_hw_display_init()`、`watcher_hw_display_lvgl()`、`watcher_hw_display_lock()` | [屏幕界面 / Display](api/display.md) |
| 拍摄 JPEG、连续取图与停止 / JPEG capture and streaming | `watcher_hw_camera_capture()`、`watcher_hw_camera_stream()`、`watcher_hw_camera_stop()` | [相机 / Camera](api/camera.md) |
| PCM 录音、播放与等待播放完成 / PCM recording and playback | `watcher_hw_audio_read()`、`watcher_hw_audio_write()`、`watcher_hw_audio_drain()` | [音频 / Audio](api/audio.md) |
| 音量与静音 / Volume and mute | `watcher_hw_audio_volume()` | [音频 / Audio](api/audio.md) |
| X/Y 转动与停止请求 / Pan, tilt and stop | `watcher_hw_body_move()`、`watcher_hw_body_stop()` | [身体控制 / Body](api/body.md) |
| 身体短按、连接与动作事件 / Short presses and body events | `watcher_hw_body_next_event()`，或 `watcher_hw_body_subscribe()` + `watcher_hw_body_dispatch_events()` | [事件接收 / Body events](api/body.md#接收触摸连接与动作事件) |
| 侧边、底座灯光及闪烁、呼吸、彩虹等效果 / Lights and effects | `watcher_hw_body_light()` | [身体控制 / Body](api/body.md) |
| 设备状态与事件队列 / Status and event queues | 各模块的 `status()`；`watcher_hw_event_queue_init()`、`watcher_hw_event_push()`、`watcher_hw_event_pop()` | [状态与事件 / Core](api/core.md) |

各指南包含初始化、关闭、参数、错误处理和头文件链接。运动前阅读[运动注意事项](api/body.md#motion-safety)。

Each guide covers initialization, cleanup, parameters, errors and header references. Read [motion precautions](api/body.md#motion-safety-english) before moving the robot.

## 视觉与模型 / Vision and models

视觉推理使用 `hal_camera` 进阶接口，需要配套 Himax 固件及已安装模型。模型目录中的可用项以设备实际返回为准。

Vision uses the advanced `hal_camera` API with compatible Himax firmware and installed models. Available models come from the device catalog.

| 功能 / Feature | 主要调用入口 / API entry | 使用说明 / Guide |
| --- | --- | --- |
| 获取与安装模型 / Install a model | 配套发布包中的安装工具 / Tools in the firmware package | [模型安装 / Provisioning](model-deployment.md) |
| 读取目录与选择模型 / List and select models | `hal_camera_list_models()`、`hal_camera_set_active_model()` | [模型选择 / Model selection](api/vision.md#模型选择) |
| 人脸检测与结果回调 / Face detection | `hal_camera_start_inference()`、`hal_camera_stop_inference_owned()` | [视觉接口 / Vision](api/vision.md) |
| 配对预览与 JPEG-only / Paired preview and JPEG-only | `hal_camera_start_inference_ex()` | [预览配置 / Preview options](api/vision.md#可选预览与配置边界) |
| 推理统计与诊断 / Statistics and diagnostics | `hal_camera_get_inference_stats()`、`hal_camera_get_diagnostics()` | [统计与错误 / Diagnostics](api/vision.md#首帧等待统计与错误) |
