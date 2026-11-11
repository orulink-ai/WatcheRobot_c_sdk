# 检测人脸与读取模型目录 / On-device vision

需要知道摄像头前有没有人脸时，先运行 [face_detection 教程](../../examples/face_detection/README_zh.md)：读取设备上已安装的模型，检测人脸，在屏幕上观察人脸数和帧号。模型在 Himax 上推理，ESP32 应用通过回调取得结果；不需要云服务。

| 目标 | 入口 | 能得到什么 |
| --- | --- | --- |
| 拍照、连续获取画面 | [`watcher_hw_camera`](camera.md) | JPEG 字节，由应用保存、显示或上传 |
| 读取模型、选择模型、取得检测结果 | 本页的 PTL `hal_camera` 进阶接口 | 模型身份信息、检测框数量和字段 |
| 边检测边取得配对 JPEG | 本页的可选预览接口 | 同一生命周期中的结果与可选预览 |

人脸检测不提供人物身份、注册人脸或持续跟踪 ID。公开接口没有 `watcher_hw_vision` 组件；推理入口在 [hal_camera.h](../../components/hal_camera/include/hal_camera.h)，由 [PTL 实现](../../components/hal_camera/src/hal_camera_ptl.c)提供。

运行条件见[配套硬件与固件](../hardware-compatibility.md)。同一时间只运行一个相机应用。

设备没有匹配的人脸模型时，先按[模型获取与安装](../model-deployment.md)下载、校验和准备 Himax；本页的模型选择函数不会烧录模型。

## 调用顺序与入口

完整代码见 [app_main.c](../../examples/face_detection/main/app_main.c)，工程直接依赖见 [main/CMakeLists.txt](../../examples/face_detection/main/CMakeLists.txt)。初始化和目录读取失败时，不继续选择或启动推理。

| 步骤 | 函数 | 约束 |
| --- | --- | --- |
| 初始化 | `hal_camera_init()` | 查询目录也会调用初始化；失败后检查清理结果 |
| 读取目录 | `hal_camera_list_models(models, 4, &count)` | 缓冲容量至少 4；当前为四个槽位，不下载模型 |
| 查询当前选择 | `hal_camera_get_model_info()` | 返回本地选择及身份信息，不证明模型正在推理 |
| 选择已安装模型 | `hal_camera_set_active_model(id)` | id 1–4；不能在拍照、取流或推理占用时切换 |
| 启动 | `hal_camera_start_inference(callback, ctx)` | 默认只回传检测结果，不传 JPEG；成功不代表已产生首帧 |
| 消费结果 | `hal_camera_inference_frame_t` | 回调在推理任务中运行；只做快速复制/通知 |
| 诊断 | `hal_camera_get_diagnostics()`、`hal_camera_get_inference_stats()` | 读取成功后还须检查诊断 `status` |
| 停止并释放 | `hal_camera_stop_inference_owned(callback, ctx)` → `hal_camera_deinit()` | 生命周期任务中执行；清理失败保留回调上下文并重试 |

首次集成沿用示例的三个职责：`app_main()` 负责启动和清理；`receive_result()` 只复制数据到队列；主任务读取队列并更新显示。默认接口不传 JPEG，复制结构体即可保留检测元数据；开启预览后，复制结构体不能保留指针指向的图像内容。

`hal_camera_stop_inference()` 停止当前推理，适用于确定自己是唯一管理者的代码；多使用者协调时用匹配回调/上下文的 owned stop。`hal_camera_inference_owned_by()` 只是观察，不是锁，不能“先查归属再无条件停止”。`hal_camera_inference_owner_status()` 是零等待查询：OK 表示归属有效，INVALID_STATE 表示已知失去，TIMEOUT 表示当前无法确定。

## 模型选择

| 槽位 | CRC 匹配时的名称 | 对应场景 |
| --- | --- | --- |
| 1 | Person Detection | 人体检测 |
| 2 | Pet Detection | 宠物检测 |
| 3 | Gesture Detection | 手势检测 |
| 4 | Face Detection | 人脸检测；示例观察有脸/无脸及移动，不进行身份识别 |

名称来源于 SDK 的[槽位 CRC 身份表](../../components/hal_camera/include/hx_model_identity.h)，不是只看槽位号猜测。`verified=false` 时名称为 `Unverified model`；不要因为 id=4 就当作人脸模型。
此核验表不保证任意新模型兼容。`hal_camera_set_active_model()` 只选择，**不会安装或上传模型**；PTL 的 `hal_camera_set_model_info()` 返回 `ESP_ERR_NOT_SUPPORTED`。

这里的 `verified` 表示槽位 CRC 与 SDK 已知表匹配，用于识别 SDK 已知模型。`contains_face_class` 也是依据该身份表生成，不是实时查询模型标签。选择接口只检查 ID 和占用状态，不替应用做身份验证；人脸示例明确检查这两个标志。

## 结果字段和数据有效期

| 字段 | PTL 含义与使用要求 |
| --- | --- |
| `sequence` | 结果序号，HAL 过滤重复序号；不保证每个结果都交给界面，不用于直接计算 FPS。 |
| `timestamp_ms` | ESP32 取数边界的单调毫秒时间，不是传感器曝光时间。 |
| `frame_width`、`frame_height` | 普通模型推理结果的坐标尺寸为 320×240，不是 JPEG 预览尺寸。 |
| `box_count`、`boxes[]` | 当前结果最多 8 个框；只有已核验人脸模型时，示例才把框数标为 Faces。 |
| 框的 `x/y/width/height` | 按协议透传的位置及尺寸。当前仓库未明确 x/y 是中心还是左上角；绘框前需依据配套固件的坐标定义转换。 |
| 框的 `score`、`target` | 分数范围 0–100；类别编号依模型解释，不是人物 ID。仓库尚无完整的各模型标签对照表。 |
| `preview_image_base64`、`preview_image_size` | 可选 base64 JPEG 视图及长度；使用默认启动接口时不传图像，使用前检查指针和长度。 |
| `preprocess_ms/inference_ms/postprocess_ms` | 当前 PTL 未填写，不能用零值推断耗时。 |

- 帧结构和可选图像指针均借用到回调返回为止。留用时复制到应用缓冲区；不要把借用指针交给持续显示的 LVGL 对象。
- 回调中不进行停止、关闭、模型切换或阻塞式界面操作。示例通过单元素队列传给主任务，宁可覆盖旧显示帧，也不阻塞推理任务。
- 停止成功前保持回调上下文有效。示例仅在停止和 deinit 均成功后删除队列；复制框数据不意味着可以提前释放队列。

## 首帧等待、统计与错误

Himax 进入推理模式后，首帧生成前可能返回零序号、零尺寸、零框快照。HAL 只在**同一代推理、尚未接到首帧、启动 5 秒内**将其视为等待，不增加 `parse_failures`。超时、出帧后重新出现空快照、畸形响应仍计错。真实传输错误也可能计入这个历史名称字段，因此它不是单纯的语法错误数。

HAL 还会等待曝光稳定（至少 12 个有效帧且经过 1.2 秒）再交付回调，故 frame_count 增加而 callback_count 暂为 0 可以是正常启动过程。

| 统计字段 | 含义 |
| --- | --- |
| `frame_count` | HAL 接收的新有效结果数，包括曝光稳定前的结果。 |
| `callback_count` | 已交付的回调次数；界面队列可能继续丢弃旧显示结果。 |
| `valid_box_count` | 已交付结果的累计框数，不是独立人物数量。 |
| `parse_failures` | 累计错误数，也可能包含传输错误；不是仅统计语法错误。 |
| `last_interval_ms/max_interval_ms/interval_total_ms` | 当前 PTL 未填写，不用于帧率或延迟结论。 |

诊断 `status` 保留最近的运行错误，后续有效帧可恢复 OK；累计错误计数不因此清零。启动成功后，从回调获取检测结果。

先检查 `hal_camera_get_diagnostics()` 的返回值，再读 `status`；模型查询情况另见 `model_status`、`model_available`。示例遇到运行错误就退出，不自动重试整轮推理；HAL 可以恢复状态，不等于示例会继续运行。

| 返回值或现象 | 常见触发条件与处理 |
| --- | --- |
| `ESP_ERR_INVALID_ARG` | 目录缓冲区不足 4 项、空指针或模型 ID 不在 1–4；按各接口签名检查参数。 |
| `ESP_ERR_INVALID_STATE` | 相机被拍照、取流、预曝光或推理占用时切换模型；先由原管理者完成停止和清理。 |
| `ESP_ERR_NOT_SUPPORTED` | PTL 写模型元数据，或示例未找到已核验的人脸模型；不要强行绕过身份检查。 |
| 传输超时或无效响应 | 保留首次错误日志，核对供电、配套协议和是否有另一个控制器；不能只看最终模式或累计帧数。 |
| 停止或 deinit 失败 | 保留上下文，检查重试结果；尚未证明可以释放内存或让另一个应用接管。 |

按屏幕提示排查，见[教程常见问题](../../examples/face_detection/README_zh.md#常见问题)。完整错误来源还包括 BSP、内存分配和底层传输，上表不穷举所有返回码。

## 可选预览与配置边界

`hal_camera_start_inference_ex()` 可设置 `include_preview_image=true`，通过同一生命周期取得配对 JPEG 预览。图像验证失败时检测框仍可能可用，图像指针为空；不要拼接上一帧图像和当前框。此路径需要独立检查图像、检测框及对齐效果，基础人脸计数测试不覆盖它。

`jpeg_only=true` 必须同时启用 `include_preview_image`，使用无模型的 JPEG 模式，并非人脸推理。PTL JPEG 固定 640×480；`hal_camera_configure()` 仅接受该尺寸，忽略 quality。检测结果和预览尺寸不同；绘框还涉及坐标原点、裁切、旋转与显示缩放，不能把简单缩放当作已验证的对齐方案。

源码保留 SSCMA 后端供维护，不构成板级公开 API 的替代兼容承诺。应用不要在 PTL 运行时直接打开另一个 UART/SPI 摄像控制器。

## English

Use the advanced PTL HAL for catalog/select/inference; the public camera wrapper exposes JPEG capture/streaming. Follow the [runnable example](../../examples/face_detection/README.md): list four slots, require a verified face identity, select, start, copy callback metadata to an application queue, stop the matching owner, then deinitialize.

Catalog labels are CRC-based: Person, Pet, Gesture and Face correspond to known slot identities. Face detection does not provide identity recognition. Selection does not upload models; PTL metadata writes are unsupported.

Detection coordinates are 320×240, preview JPEGs 640×480; at most eight boxes, with scores 0–100. The repository does not yet specify whether x/y mean center or top-left, or provide a complete per-model class map. Use the paired firmware's coordinate definition when drawing overlays. Callbacks borrow all data until return. Do not stop/close or block on UI work in the callback. Retain storage until cleanup succeeds. JPEG-only delivers images without model inference.

Exact empty snapshots are tolerated only before the first frame, for the same generation, within five seconds. Real errors remain counted; diagnostics can recover on a valid frame while cumulative failures remain. Exposure warmup also delays callbacks. Timing/interval fields not populated by PTL are not performance measurements. Keep the full lifecycle under one owner and do not combine this example with an independently initialized camera demo.

Check both the diagnostics call result and its `status` field. The example exits on a reported error instead of waiting for recovery. CRC verification means a known slot identity, not a signature or accuracy guarantee; the low-level selection call does not enforce identity checks. For runnable steps, modification points and symptom-based troubleshooting, use the [English tutorial](../../examples/face_detection/README.md).
