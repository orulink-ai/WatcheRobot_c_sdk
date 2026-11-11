# 控制转动、灯光与读取触摸事件

需要发送转动指令、设置机身灯光，或接收触摸和连接变化时，使用这一组接口。SDK 统一负责与机身控制芯片通信，应用不必自己收发消息。

调用运动接口前，先阅读[运动注意事项](#motion-safety)。

最短流程：初始化 → 检查是否就绪 → 根据当前用户操作处理事件、设置灯光或发送运动指令 → 关闭。下面只查看状态，不演示转动；初始化返回后可能仍在连接中。

## 示例：检查初始化与关闭

```c
#include "watcher_hw_body.h"
#include "esp_log.h"

/* Run on an application owner task, not in a hardware callback. */
esp_err_t inspect_body(void) {
    esp_err_t err = watcher_hw_body_init();
    if (err != ESP_OK) {
        esp_err_t cleanup = watcher_hw_body_close();
        ESP_LOGE("sdk_example", "init failed: %s; cleanup: %s",
                 esp_err_to_name(err), esp_err_to_name(cleanup));
        return err;
    }
    watcher_hw_status_t status;
    err = watcher_hw_body_status(&status);
    if (err == ESP_OK && status.state != WATCHER_HW_READY)
        err = status.last_error != ESP_OK ? status.last_error : ESP_ERR_INVALID_STATE;
    /* Deliberately no move/light request in this lifecycle sample. */
    esp_err_t closed = watcher_hw_body_close();
    if (err != ESP_OK || closed != ESP_OK)
        ESP_LOGE("sdk_example", "operation: %s; close: %s",
                 esp_err_to_name(err), esp_err_to_name(closed));
    return err != ESP_OK ? err : closed;
}
```

刚初始化时可能还在连接中，因此本片段返回 `ESP_ERR_INVALID_STATE` 不一定表示设备故障。若想观察实际效果，请运行下方链接的触摸灯光示例，查看触摸日志及灯光变化；本片段不会自动转动机器人。

示例记录操作和清理两个结果，返回值优先保留操作错误。真实应用还必须处理清理失败（例如重试关闭），不能记录后就把资源交给别的使用者。

## 转动、灯光与触摸

`watcher_hw_body_move(x_degrees, y_degrees, duration_ms, &sequence)` 接受 X 0–180°、Y 100–140°、时长 1–65535 ms。返回的 `sequence` 用于关联指令及后续事件。

`ACK` 表示对端应答，`DONE` 表示对端报告指令结束；事件中的角度字段以 0.1° 为单位。实际位置反馈和 STOP 的使用边界见[运动注意事项](#motion-safety)。

`watcher_hw_body_light(const mcu_led_request_t *)` 设置灯光；颜色分量与亮度是 0–255。区域、模式、效果及请求字段见[灯光接口头文件](../../components/mcu_led_service/include/mcu_led_service.h)。这些请求仍经过同一个机身连接，不要另外启动底层通信。

| 字段 | 当前调用含义 |
| --- | --- |
| `zone` | `ALL`、`SIDE`、`BOTTOM`，分别是全部、侧边、底座 |
| `mode` | `OFF` 关闭、`STATIC` 常亮、`EFFECT` 灯效 |
| `primary_red/green/blue`、`brightness` | 0–255；亮度在发送前缩放主颜色 |
| `effect_id` | BLINK、BREATHING、RAINBOW、STATUS_PULSE |
| `period_ms` | 灯效周期，EFFECT 模式必须非零；静态模式不把它用作持续时间 |
| `secondary_*`、`repeat_count` | 结构中保留，但当前发送实现不将它们编码到灯效请求；不能据此承诺双色或有限次数重复 |

修改点见 [body 示例入口](../../examples/body/main/app_main.c)。先等 READY，再用 `watcher_hw_body_light()` 发送完整请求。

身体触摸目前仅支持短按，应用通过按下和释放事件响应触摸。协议保留的长按事件尚待确认，不应作为应用流程的触发条件。完整事件消费方式见 [body 示例](../../examples/body/README.md)。

## 接收触摸、连接与动作事件

SDK 把事件按到达顺序暂存，应用选择一种方式取出：

1. 主动调用 `watcher_hw_body_next_event()`；没有事件时返回 `ESP_ERR_NOT_FOUND`。
2. 注册 `watcher_hw_body_subscribe()`，再由应用调用 `watcher_hw_body_dispatch_events()` 执行回调；最多四个订阅者。

两种方式消耗的是同一个队列（FIFO，先到先取），不能混用。让一个应用任务负责取事件、订阅变化与分发；初始化、关闭、状态与控制调用由 SDK 内部串行化。SDK 打开期间，不允许其他代码初始化或轮询机身控制芯片（MCU）的连接。

分发回调直接在调用 dispatch 的应用任务上执行，不持有 MCU 互斥锁。事件内存只在回调返回前有效：要保留内容，先检查类型和长度，再复制数据。即使已取消订阅，上下文内存也必须保留到本次 dispatch 返回，因为它可能已被本次分发记录。回调中不要再次分发、阻塞等待音频，或初始化/关闭机身运行任务。

`dispatch_events(max_events, &dispatched)` 的 `max_events` 必须大于 0，`dispatched` 必须非空；返回成功可以表示本次没有事件，实际数量看 `dispatched`。`status()` 成功只表示读取到状态，还要检查 `state == WATCHER_HW_READY`。`init()` 成功后通常先处于 STARTING，要等与对端完成连接确认。

## 丢事件后必须重新确认操作意图

例如“按下”事件收到、而“松手”事件丢失，应用就可能误以为用户还在要求转动。因此 SDK 不会在丢事件后照常接受新动作。

`WATCHER_HW_EVENT_OVERFLOW` 会优先于队列里保留下来的事件送出，不占普通队列容量。其数据是 `watcher_hw_body_event_loss_t`：

- `dropped`：本次初始化以来累计丢失数量；后续丢失会更新它。
- `stop_result`：SDK 第一次丢事件后尝试发送一次停止请求的结果，**不是实际停稳确认**。断连或发送失败时，不会自动重放这次停止。
- 事件的 `received_us` 是第一次丢失的时间，`sequence` 为 0。

丢失会使对外状态锁定为 `WATCHER_HW_FAULT` / `ESP_ERR_NO_MEM`，拒绝转动和灯光请求；连接就绪时仍可请求 stop。处理步骤：取消应用积压的动作 → 在回调外 close 并检查结果 → init → 重新订阅 → 等待新的 READY → 获得用户新的明确操作意图。不要重放旧动作。

仅仅清空队列，或者重新收到对端连接问候消息（HELLO），都不能解除这个故障锁定。重新初始化和关闭会清除订阅，诊断丢失数量可用 `watcher_hw_body_dropped_events()`。关闭超时要重试，不能当成后台任务已退出；关闭还可能报告停止请求或发送等待失败，即使资源已清理也不能据此宣称物理停止。

## 接入与完整示例

- 公开头文件：[`watcher_hw_body.h`](../../bsp/watche_robot/watcher_hw_body/include/watcher_hw_body.h)。接口名称和参数以此为准。
- 从完整仓库构建示例，保留工程的配置与依赖文件。
- 直接 CMake 依赖：watcher_hw_core、mcu_runtime、mcu_motion_service、mcu_led_service、mcu_sensor_service；私有依赖 freertos、esp_timer、motion_arbiter。详见[依赖与本地适配](../../examples/README.md#requirements--环境要求)。
- [可运行的 body 示例](../../examples/body/README.md) · [组合示例](../../examples/robot/README.md)
- [构建、配套固件、备份与恢复](../../examples/README.md) · [文档导航](README.md)

## English: Motion, lights and touch

Send movement and light requests, and read touch or connection events. The SDK manages the connection to the body controller.
Initialize, check READY, handle events or request an intended action, then close. Initialization may still be connecting when it returns.

- Read [motion precautions](#motion-safety-english) before sending movement requests.
- Use one application task to read events and change subscriptions. Choose queued reads or callback dispatch, not both; do not open or poll a second body connection.
- Body touch currently supports short presses through press and release events. Support for the protocol's long-press event remains unconfirmed; do not depend on it to advance an application flow.
- Copy event data before its callback returns. Keep callback context alive until dispatch returns, even after unsubscribe. Do not dispatch recursively or initialize/close from a callback.
- After lost events, cancel pending actions; close/init outside callbacks, resubscribe, wait for a new READY, and require a new user action. Reconnection or an empty queue must not replay old motion.
- Check operation and cleanup results separately. Retry failed cleanup before treating resources as released.


## Motion safety

舵机没有实际位置反馈，目标角度、ACK 和 DONE 都不是测量结果。SDK 不提供实际位置查询或位置回调。

- 运动前清空整个可能行程，并保留人工断电手段；起点未知时，回到参考位置也可能产生较大动作。
- 软件 STOP 不是急停装置，断连后可能无法送达。运动异常或停止无效时直接断电。
- 发生故障后取消积压动作，按上文恢复流程重新初始化。连接恢复后，由新的用户操作发起运动，不自动重放旧动作。

使用 [hardware_check](../../examples/hardware_check/README_zh.md) 可分别体验 X、Y 轴和 STOP。

## Motion safety (English)

Servos have no actual-position feedback. Target angles, ACK and DONE are not measurements; the SDK provides no actual-position query or callback.

- Clear the entire travel and keep manual power disconnection available. Moving to a reference position can travel far from an unknown starting point.
- Software STOP is not an emergency stop and may not arrive after disconnection. Cut power if movement is unsafe or stopping fails.
- Cancel queued actions after a fault and use the recovery procedure above. Resume movement only on a new user action.

Try individual X, Y and STOP operations with [hardware_check](../../examples/hardware_check/README.md).

Lighting uses OFF/STATIC/EFFECT modes and ALL/SIDE/BOTTOM zones. Primary RGB and brightness are 0–255; EFFECT requires a nonzero period. The sender does not encode secondary_* or repeat_count.
