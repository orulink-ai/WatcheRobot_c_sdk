# 功能、代码入口与文档对照 / Feature map

先从[上手教程](getting-started_zh.md)运行一个示例，再按本表找接口。此表列出应用接口、进阶视觉、内部组件及板级入口，便于查找功能和源码。

应用开发优先使用公开 SDK 和完整示例；内部组件与板级入口供进阶开发参考。配套要求见[硬件兼容性](hardware-compatibility.md)。

English: this map separates public application APIs, advanced PTL vision, internal components and board entry points. Start with the [English tutorial](getting-started.md), then check [compatibility](hardware-compatibility.md).

## 公开SDK

| 功能 / Feature | 代码入口 / Entry | 文档 / Documentation |
| --- | --- | --- |
| 屏幕初始化、关闭与状态查询 | [`watcher_hw_display_init`](../bsp/watche_robot/watcher_hw_display/watcher_hw_display.c) | [docs/api/display.md](../docs/api/display.md) |
| LVGL绘制文字/按钮与界面刷新 | [`watcher_hw_display_lvgl`](../bsp/watche_robot/watcher_hw_display/watcher_hw_display.c) | [docs/api/display.md](../docs/api/display.md) |
| 屏幕触摸接入 | [`watcher_hw_display_touch`](../bsp/watche_robot/watcher_hw_display/watcher_hw_display.c) | [docs/api/display.md](../docs/api/display.md) |
| 界面加锁/解锁及句柄有效期 | [`watcher_hw_display_lock`](../bsp/watche_robot/watcher_hw_display/watcher_hw_display.c) | [docs/api/display.md](../docs/api/display.md) |
| 音频初始化、关闭与状态查询 | [`watcher_hw_audio_init`](../bsp/watche_robot/watcher_hw_audio/watcher_hw_audio.c) | [docs/api/audio.md](../docs/api/audio.md) |
| PCM麦克风录音 | [`watcher_hw_audio_read`](../bsp/watche_robot/watcher_hw_audio/watcher_hw_audio.c) | [docs/api/audio.md](../docs/api/audio.md) |
| PCM扬声器播放 | [`watcher_hw_audio_write`](../bsp/watche_robot/watcher_hw_audio/watcher_hw_audio.c) | [docs/api/audio.md](../docs/api/audio.md) |
| 16/24 kHz采样率与录放音双向通路 | [`watcher_hw_audio_init`](../bsp/watche_robot/watcher_hw_audio/watcher_hw_audio.c) | [docs/api/audio.md](../docs/api/audio.md) |
| 音量、静音及解除静音 | [`watcher_hw_audio_volume`](../bsp/watche_robot/watcher_hw_audio/watcher_hw_audio.c) | [docs/api/audio.md](../docs/api/audio.md) |
| 等待播放缓冲送出 drain | [`watcher_hw_audio_drain`](../bsp/watche_robot/watcher_hw_audio/watcher_hw_audio.c) | [docs/api/audio.md](../docs/api/audio.md) |
| 音频独占、失败清理与资源交接 | [`watcher_hw_audio_close`](../bsp/watche_robot/watcher_hw_audio/watcher_hw_audio.c) | [docs/api/audio.md](../docs/api/audio.md) |
| 相机初始化、关闭、状态和恢复 | [`watcher_hw_camera_init`](../bsp/watche_robot/watcher_hw_camera/watcher_hw_camera.c) | [docs/api/camera.md](../docs/api/camera.md) |
| 拍摄单张JPEG | [`watcher_hw_camera_capture`](../bsp/watche_robot/watcher_hw_camera/watcher_hw_camera.c) | [docs/api/camera.md](../docs/api/camera.md) |
| 连续JPEG取流与停止 | [`watcher_hw_camera_stream`](../bsp/watche_robot/watcher_hw_camera/watcher_hw_camera.c) | [docs/api/camera.md](../docs/api/camera.md) |
| 相机回调、图像生命周期与资源互斥 | [`watcher_hw_camera_capture`](../bsp/watche_robot/watcher_hw_camera/watcher_hw_camera.c) | [docs/api/camera.md](../docs/api/camera.md) |
| 机身初始化、关闭与状态查询 | [`watcher_hw_body_init`](../bsp/watche_robot/watcher_hw_body/watcher_hw_body.c) | [docs/api/body.md](../docs/api/body.md) |
| X/Y目标角度与动作时长控制 | [`watcher_hw_body_move`](../bsp/watche_robot/watcher_hw_body/watcher_hw_body.c) | [docs/api/body.md](../docs/api/body.md) |
| 请求停止动作 | [`watcher_hw_body_stop`](../bsp/watche_robot/watcher_hw_body/watcher_hw_body.c) | [docs/api/body.md](../docs/api/body.md) |
| 身体触摸按下/释放；长按取决于传感器及固件支持 | [`watcher_hw_body_next_event`](../bsp/watche_robot/watcher_hw_body/watcher_hw_body.c) | [docs/api/body.md](../docs/api/body.md) |
| 灯光区域、RGB颜色、亮度、关闭 | [`watcher_hw_body_light`](../bsp/watche_robot/watcher_hw_body/watcher_hw_body.c) | [docs/api/body.md](../docs/api/body.md) |
| 灯光闪烁效果 | [`watcher_hw_body_light`](../bsp/watche_robot/watcher_hw_body/watcher_hw_body.c) | [docs/api/body.md](../docs/api/body.md) |
| 灯光呼吸效果 | [`watcher_hw_body_light`](../bsp/watche_robot/watcher_hw_body/watcher_hw_body.c) | [docs/api/body.md](../docs/api/body.md) |
| 灯光彩虹效果 | [`watcher_hw_body_light`](../bsp/watche_robot/watcher_hw_body/watcher_hw_body.c) | [docs/api/body.md](../docs/api/body.md) |
| 灯光状态脉冲效果 | [`watcher_hw_body_light`](../bsp/watche_robot/watcher_hw_body/watcher_hw_body.c) | [docs/api/body.md](../docs/api/body.md) |
| 灯效周期；重复次数和双色字段未编码到当前发送请求 | [`watcher_hw_body_light`](../bsp/watche_robot/watcher_hw_body/watcher_hw_body.c) | [docs/api/body.md](../docs/api/body.md) |
| 主动读取事件与订阅/分发事件 | [`watcher_hw_body_next_event`](../bsp/watche_robot/watcher_hw_body/watcher_hw_body.c) | [docs/api/body.md](../docs/api/body.md) |
| 丢事件计数、OVERFLOW故障锁定与恢复 | [`watcher_hw_body_dropped_events`](../bsp/watche_robot/watcher_hw_body/watcher_hw_body.c) | [docs/api/body.md](../docs/api/body.md) |
| 设备状态与事件公共数据类型 | [`WATCHER_HW_CLOSED`](../bsp/watche_robot/watcher_hw_core/include/watcher_hw_core.h) | [docs/api/core.md](../docs/api/core.md) |
| FIFO事件队列、容量和溢出规则 | [`watcher_hw_event_queue_init`](../bsp/watche_robot/watcher_hw_core/watcher_hw_core.c) | [docs/api/core.md](../docs/api/core.md) |

## 底层视觉

| 功能 / Feature | 代码入口 / Entry | 文档 / Documentation |
| --- | --- | --- |
| 查询当前模型和已安装模型列表 | [`hal_camera_list_models`](../components/hal_camera/src/hal_camera_ptl.c) | [docs/api/vision.md](../docs/api/vision.md) |
| 模型槽位CRC与身份核验 | [`hx_model_identity_verified`](../components/hal_camera/include/hx_model_identity.h) | [docs/api/vision.md](../docs/api/vision.md) |
| Person Detection（模型推理类别） | [`s_model_names`](../components/hal_camera/src/hal_camera_ptl.c) | [docs/api/vision.md](../docs/api/vision.md) |
| Pet Detection（模型推理类别） | [`s_model_names`](../components/hal_camera/src/hal_camera_ptl.c) | [docs/api/vision.md](../docs/api/vision.md) |
| Gesture Detection（模型推理类别） | [`s_model_names`](../components/hal_camera/src/hal_camera_ptl.c) | [docs/api/vision.md](../docs/api/vision.md) |
| Face Detection（模型推理类别） | [`s_model_names`](../components/hal_camera/src/hal_camera_ptl.c) | [docs/api/vision.md](../docs/api/vision.md) |
| 选择已安装模型 | [`hal_camera_set_active_model`](../components/hal_camera/src/hal_camera_ptl.c) | [docs/api/vision.md](../docs/api/vision.md) |
| 启动/停止持续推理及调用方归属保护 | [`hal_camera_start_inference_ex`](../components/hal_camera/src/hal_camera_ptl.c) | [docs/api/vision.md](../docs/api/vision.md) |
| 检测框、类别、分数、序号回调 | [`inference_task`](../components/hal_camera/src/hal_camera_ptl.c) | [docs/api/vision.md](../docs/api/vision.md) |
| 推理预览图、图框配对与JPEG-only模式 | [`inference_task`](../components/hal_camera/src/hal_camera_ptl.c) | [docs/api/vision.md](../docs/api/vision.md) |
| 相机/推理诊断和统计 | [`hal_camera_get_diagnostics`](../components/hal_camera/src/hal_camera_ptl.c) | [docs/api/vision.md](../docs/api/vision.md) |
| 相机输出尺寸配置 | [`hal_camera_configure`](../components/hal_camera/src/hal_camera_ptl.c) | [docs/api/vision.md](../docs/api/vision.md) |
| SSCMA兼容后端与通用推理调用 | [`hal_camera_start_inference_ex`](../components/hal_camera/src/hal_camera.c) | [components/sscma_client/README.md](../components/sscma_client/README.md) |

## 内部组件

| 功能 / Feature | 代码入口 / Entry | 文档 / Documentation |
| --- | --- | --- |
| 速度点动 | [`mcu_motion_jog`](../components/mcu_motion_service/src/mcu_motion_service.c) | [头文件参考；无专门教程](../components/mcu_motion_service/include/mcu_motion_service.h) |
| 直接目标运动 | [`mcu_motion_submit_direct_target`](../components/mcu_motion_service/src/mcu_motion_service.c) | [头文件参考；无专门教程](../components/mcu_motion_service/include/mcu_motion_service.h) |
| 多段、分块与跟踪动作序列 | [`mcu_motion_submit_chunked_sequence`](../components/mcu_motion_service/src/mcu_motion_service.c) | [头文件参考；无专门教程](../components/mcu_motion_service/include/mcu_motion_service.h) |
| 动作完成/STOP观察令牌 | [`mcu_motion_submit_observed_stop`](../components/mcu_motion_service/src/mcu_motion_service.c) | [头文件参考；无专门教程](../components/mcu_motion_service/include/mcu_motion_service.h) |
| 舵机PWM锁定/释放 | [`mcu_motion_pwm_unlock`](../components/mcu_motion_service/src/mcu_motion_service.c) | [头文件参考；无专门教程](../components/mcu_motion_service/include/mcu_motion_service.h) |
| 多个动作来源的控制权仲裁 | [`motion_arbiter_acquire`](../components/motion_arbiter/src/motion_arbiter.c) | [components/motion_arbiter/README.md](../components/motion_arbiter/README.md) |
| 机身5V供电开关 | [`mcu_power_set_5v_enabled`](../components/mcu_power_service/src/mcu_power_service.c) | [components/mcu_power_service/README.md](../components/mcu_power_service/README.md) |
| 磁场/航向和IMU数据接收与缓存 | [`mcu_sensor_service_apply_frame`](../components/mcu_sensor_service/src/mcu_sensor_service.c) | [components/mcu_sensor_service/README.md](../components/mcu_sensor_service/README.md) |
| 机身连接、协议收发和串口维护互斥 | [`mcu_link_init`](../components/mcu_link/src/mcu_link.c) | [components/mcu_link/README.md](../components/mcu_link/README.md) |
| 机身消息分发和初始同步 | [`mcu_runtime_dispatch`](../components/mcu_runtime/mcu_runtime.c) | [components/mcu_runtime/README.md](../components/mcu_runtime/README.md) |
| 旋钮/按钮输入路由与作用域切换 | [`watcher_input_router_set_scope`](../components/watcher_input_router/src/watcher_input_router.c) | [components/watcher_input_router/README.md](../components/watcher_input_router/README.md) |
| Himax PTL传输、模式控制与通信资源归属 | [`watcher_hx_control_init`](../components/watcher_hx_ptl/watcher_hx_control.c) | [components/watcher_hx_ptl/README.md](../components/watcher_hx_ptl/README.md) |
| 图像编号、时间和完整性校验 | [`hx_media_frame_validate`](../components/hx_media_protocol/hx_media_protocol.c) | [components/hx_media_protocol/README.md](../components/hx_media_protocol/README.md) |
| PTL消息解析、JPEG包检查与重新同步 | [`hx_ptl_validate_jpeg_packet`](../components/hx_ptl_protocol/hx_ptl_protocol.c) | [components/hx_ptl_protocol/README.md](../components/hx_ptl_protocol/README.md) |
| JPEG结构和尺寸检查 | [`hal_camera_jpeg_normalize`](../components/jpeg_integrity/jpeg_integrity.c) | [components/jpeg_integrity/README.md](../components/jpeg_integrity/README.md) |
| 底层音频PCM及资源管理 | [`hal_audio_init`](../components/hal_audio/src/hal_audio.c) | [components/hal_audio/README.md](../components/hal_audio/README.md) |
| Opus上行编码与编码器重置 | [`hal_opus_encode`](../components/hal_audio/src/hal_opus.c) | [头文件参考；无专门教程](../components/hal_audio/include/hal_opus.h) |
| 只播放准备、输入暂停、采集状态通知 | [`hal_audio_capture_pause`](../components/hal_audio/src/hal_audio.c) | [头文件参考；无专门教程](../components/hal_audio/include/hal_audio.h) |
| 外部音频独占使用权和空闲释放 | [`hal_audio_external_lease_acquire`](../components/hal_audio/src/hal_audio.c) | [头文件参考；无专门教程](../components/hal_audio/include/hal_audio.h) |

## 板级接口

| 功能 / Feature | 代码入口 / Entry | 文档 / Documentation |
| --- | --- | --- |
| 实体按钮初始化、单击/多击、长按及释放 | [`bsp_knob_btn_init`](../bsp/watche_robot/sensecap-watcher/sensecap-watcher.c) | [头文件参考；无专门教程](../bsp/watche_robot/sensecap-watcher/include/sensecap-watcher.h) |
| LCD背光亮度调节 | [`bsp_lcd_brightness_set`](../bsp/watche_robot/sensecap-watcher/sensecap-watcher.c) | [头文件参考；无专门教程](../bsp/watche_robot/sensecap-watcher/include/sensecap-watcher.h) |
| 板载RGB灯控制 | [`bsp_rgb_set`](../bsp/watche_robot/sensecap-watcher/sensecap-watcher.c) | [头文件参考；无专门教程](../bsp/watche_robot/sensecap-watcher/include/sensecap-watcher.h) |
| 电池电压、百分比与充电/待机/存在状态 | [`bsp_battery_get_voltage`](../bsp/watche_robot/sensecap-watcher/sensecap-watcher.c) | [头文件参考；无专门教程](../bsp/watche_robot/sensecap-watcher/include/sensecap-watcher.h) |
| RTC时间读取、设置与定时器 | [`bsp_rtc_get_time`](../bsp/watche_robot/sensecap-watcher/sensecap-watcher.c) | [头文件参考；无专门教程](../bsp/watche_robot/sensecap-watcher/include/sensecap-watcher.h) |
| 深睡眠、唤醒、重启与关机 | [`bsp_system_deep_sleep`](../bsp/watche_robot/sensecap-watcher/sensecap-watcher.c) | [头文件参考；无专门教程](../bsp/watche_robot/sensecap-watcher/include/sensecap-watcher.h) |
| SD卡检测、状态、挂载/卸载 | [`bsp_sdcard_init`](../bsp/watche_robot/sensecap-watcher/sensecap-watcher.c) | [头文件参考；无专门教程](../bsp/watche_robot/sensecap-watcher/include/sensecap-watcher.h) |
| SPIFFS文件系统挂载 | [`bsp_spiffs_init`](../bsp/watche_robot/sensecap-watcher/sensecap-watcher.c) | [头文件参考；无专门教程](../bsp/watche_robot/sensecap-watcher/include/sensecap-watcher.h) |
| I2C/SPI/UART总线初始化与I2C探测 | [`bsp_i2c_bus_init`](../bsp/watche_robot/sensecap-watcher/sensecap-watcher.c) | [头文件参考；无专门教程](../bsp/watche_robot/sensecap-watcher/include/sensecap-watcher.h) |
| IO扩展输入读取和输出控制 | [`bsp_exp_io_set_level`](../bsp/watche_robot/sensecap-watcher/sensecap-watcher.c) | [头文件参考；无专门教程](../bsp/watche_robot/sensecap-watcher/include/sensecap-watcher.h) |
| I2S发送参考回调、溢出计数和Codec停启 | [`bsp_i2s_set_tx_reference_callback`](../bsp/watche_robot/sensecap-watcher/sensecap-watcher.c) | [头文件参考；无专门教程](../bsp/watche_robot/sensecap-watcher/include/sensecap-watcher.h) |

## 示例与工具

| 功能 / Feature | 代码入口 / Entry | 文档 / Documentation |
| --- | --- | --- |
| body：触摸控制绿灯、松手熄灯并请求stop | [`app_main`](../examples/body/main/app_main.c) | [examples/body/README.md](../examples/body/README.md) |
| head：照片、录音回放与扬声器测试界面 | [`app_main`](../examples/head/main/app_main.c) | [examples/head/README.md](../examples/head/README.md) |
| robot：媒体界面与身体触摸灯光组合 | [`app_main`](../examples/robot/main/app_main.c) | [examples/robot/README.md](../examples/robot/README.md) |
| hardware_check：8组26细项、人工确认与报告 | [`check_app_start`](../examples/hardware_check/main/check_app.c) | [examples/hardware_check/README_zh.md](../examples/hardware_check/README_zh.md) |
| 静默串口验证和diag命令 | [`diag`](../examples/hardware_check/verify.py) | [examples/hardware_check/README_zh.md](../examples/hardware_check/README_zh.md) |
| 示例构建、固件配套和恢复前提 | [`## Build`](../examples/README.md) | [examples/README.md](../examples/README.md) |
| 主机测试、文档链接和源码哈希检查 | [`def check_source`](../tools/check_docs.py) | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| 本地组件打包和独立consumer构建 | [`def prepare`](../tools/package_components.py) | [tools/packaging/README.md](../tools/packaging/README.md) |

## 明确限制

| 功能 / Feature | 代码入口 / Entry | 文档 / Documentation |
| --- | --- | --- |
| 实际舵机位置查询/反馈 | [`不提供：旧查询及回调已删除`](../bsp/watche_robot/watcher_hw_body/watcher_hw_body.c) | [docs/api/body.md](../docs/api/body.md) |
| PTL模型元数据写入：不支持 | [`hal_camera_set_model_info`](../components/hal_camera/src/hal_camera_ptl.c) | [视觉限制](api/vision.md) |
| Opus下行解码 | [`hal_opus_decode`](../components/hal_audio/src/hal_opus.c) | [头文件参考；无专门教程](../components/hal_audio/include/hal_opus.h) |
| PTL推理耗时字段：未填写，不可当性能数据 | [`inference_task`](../components/hal_camera/src/hal_camera_ptl.c) | [结果字段](api/vision.md#结果字段和数据有效期) |
| 检测框 x/y 原点约定、各模型类别表：尚未形成完整契约 | [透传字段](../components/watcher_hx_ptl/watcher_hx_control.c) | [结果字段与限制](api/vision.md#结果字段和数据有效期) |
| 配对预览与检测框：绘制时需处理坐标转换 | [`inference_task`](../components/hal_camera/src/hal_camera_ptl.c) | [可选预览](api/vision.md#可选预览与配置边界) |

## 新增上手示例

| 功能 | 代码入口 | 文档 |
| --- | --- | --- |
| 最小显示应用 | [app_main](../examples/hello_display/main/app_main.c) | [hello_display](../examples/hello_display/README.md) |
| 模型目录与人脸检测 | [app_main](../examples/face_detection/main/app_main.c) | [中文教程](../examples/face_detection/README_zh.md) / [English](../examples/face_detection/README.md) / [视觉契约](api/vision.md) |
| 人脸模型获取、校验与安装（独立发布包工具） | [Releases](https://github.com/orulink-ai/WatcheRobot-public/releases) 中兼容所用 SDK 的 Himax 包，非 C-SDK 模型选择 API | [模型获取与安装](model-deployment.md) |

文档放置与同步规则见[贡献指南](../CONTRIBUTING.md#documentation-locations--文档归属)。不在根目录或组件目录重复放置同一份教程。
