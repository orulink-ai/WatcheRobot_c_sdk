# How the SDK fits your application / SDK 如何配合你的应用

Use this page when you are deciding where to put application logic or investigating
conflicting access to hardware. For build commands, start with [setup](getting-started.md).
本页面向开发应用和排查硬件访问冲突的人；构建步骤见[中文上手](getting-started_zh.md)。

## Choose what your application needs / 按需要选择能力

| Your goal / 你想做什么 | Public API / 公开接口 | What your application supplies / 应用负责什么 |
| --- | --- | --- |
| Move the body, control lights, read touch / 控制运动、灯光和触摸 | `watcher_hw_body` | User permission, event handling and safe recovery / 用户确认、事件处理与安全恢复 |
| Take photos or receive camera frames / 拍照或接收画面 | `watcher_hw_camera` | Image use, UI and network policy / 图片用途、界面与联网策略 |
| Record or play sound / 录音或播放 | `watcher_hw_audio` | When to record/play and how to react to errors / 录放时机与出错处理 |
| Draw a screen / 绘制界面 | `watcher_hw_display` | Interface contents and interaction / 页面内容与交互 |
| Share status and event handling / 处理公共状态与事件 | `watcher_hw_core` | A bounded event queue owned by the caller / 由调用方管理、容量有限的事件队列 |

Each example is an independent ESP-IDF project. `examples/sdk.cmake` selects local
source directories through `HW_BODY`/`HW_HEAD`; it does not download Registry packages.
`examples/common` contains shared example UI/media behavior, not a public API.
The repository does not supply the official product application or STM32/Himax firmware.

每个示例独立构建。`examples/sdk.cmake` 按 `HW_BODY`/`HW_HEAD` 选择本地源码，
不从组件平台下载 SDK。`examples/common` 供示例复用界面和音视频逻辑，不是公开接口。
官方产品应用及 STM32/Himax 固件不随本仓库提供。

## Assign one owner before adding callbacks / 先明确谁负责硬件

An **owner task** is the application task responsible for opening, using and closing
a resource. A **callback** runs when an event arrives; it is not a place to start blocking work.
“负责硬件的任务”是统一打开、使用、关闭该资源的应用任务；“回调”是事件到达时调用的函数，
不应在其中执行需要等待的工作。

1. Give body control one process-wide MCU connection. MCU means the paired
   microcontroller (STM32). Do not initialize or poll the same connection elsewhere.
   Choose either FIFO polling (reading queued events in arrival order) or synchronous
   subscription dispatch from one task, never both.
2. Serialize camera open/use/close in one task. JPEG image bytes are borrowed only
   for the duration of a callback; copy them if you need them afterward.
3. Keep blocking audio calls in one task, outside body/camera callbacks and outside
   an LVGL lock. LVGL is the screen's graphics library; its lock protects UI changes.
4. Let display control screen flushing. Do not draw independently to its panel.
   Use its borrowed handles only until close, lock LVGL changes and close outside the lock.

中文步骤：身体连接只能有一个管理任务，事件队列读取与同步订阅分发二选一；相机生命周期
由一个任务串行管理，回调结束前复制要保留的 JPEG；录放音在独立任务执行，不占用回调或
界面锁；显示接口统一刷新屏幕，句柄仅在关闭前有效，修改界面要加锁，关闭时不能持锁。

## Recognize ready and recover safely / 判断就绪并安全恢复

`status()` returning `ESP_OK` means the query succeeded. Check `state` and
`last_error` before using the device; query success is not READY.
Body event overflow latches FAULT: cancel pending application actions, close/init
outside callbacks, resubscribe, wait for a fresh READY and require a new user action.
Reconnect or draining the queue must not resume old motion.

`status()` 返回 `ESP_OK` 只表示查询成功，还要检查 `state` 和 `last_error`。
身体事件队列溢出后会锁定故障：取消待执行动作，在回调外关闭并初始化、重新订阅，
等待新的 READY 和用户操作。重连或读空队列不能自动重放旧运动。

Expected result: one clear owner per resource, no borrowed data used after its
lifetime, and no automatic motion after recovery.
预期：每个资源只有一个管理者，不使用失效数据，恢复后不自动运动。

For implementation dependencies see [dependencies](dependencies.md); before motion
read [servo safety](servo-open-loop.md) / [舵机安全](servo-open-loop_zh.md)。
