# 控制转动、灯光与读取触摸事件

需要发送转动指令、设置机身灯光，或接收触摸和连接变化时，使用这一组接口。SDK 统一负责与机身控制芯片通信，应用不必自己收发消息。

**当前硬件无法实测舵机角度。** 软件收到“已接收”或“已完成”，也不能证明机器人已经到位或停稳。

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

## 发送指令前：不要把指令角度当作实测角度

`watcher_hw_body_move(x_degrees, y_degrees, duration_ms, &sequence)` 接受 X 0–180°、Y 100–140°、时长 1–65535 ms。这些是接口允许发送的范围，不是机器人实际位置的测量结果，也不保证整个行程都没有障碍。返回的 `sequence` 只用于关联这条指令，不代表动作已经完成。

- `watcher_hw_body_request_position()` 始终返回 `ESP_ERR_NOT_SUPPORTED`，不会发送查询，也不会生成位置事件。
- 例如 X90/Y120 只是一个目标：机器人如果正停在另一端，移到这里仍可能走很远，不能把它当作无风险“回中”。不要为了验证初始化就发送演示动作。
- `ACK` 表示对端对指令的应答，`DONE` 表示对端报告这条指令结束；两者以及报告中的最终角度都不是角度传感器实测，**不证明已经到位或停止**。运动事件里的角度字段以 0.1° 为单位。
- 确保整个可能运动的区域内没有人手、线缆或障碍，并始终保留人工断电手段。与控制芯片断连后，软件停止指令无法送到；`watcher_hw_body_stop()` 成功也不等于物理急停验收。

`watcher_hw_body_light(const mcu_led_request_t *)` 设置灯光；颜色分量与亮度是 0–255。区域、模式、效果及请求字段见[灯光接口头文件](../../components/mcu_led_service/include/mcu_led_service.h)。这些请求仍经过同一个机身连接，不要另外启动底层通信。

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
- 使用完整源码与示例匹配的配置、分区和依赖清单；当前为开发预览，不提供未经验证的组件仓库安装命令。仅复制头文件不能补齐所有依赖。
- 直接 CMake 依赖：watcher_hw_core、mcu_runtime、mcu_motion_service、mcu_led_service、mcu_sensor_service；私有依赖 freertos、esp_timer、motion_arbiter。详见[依赖与本地适配](../development.md#dependencies)。
- [可运行的 body 示例](../../examples/body/README.md) · [组合示例](../../examples/robot/README.md)
- [构建、配套固件、备份与恢复](../../examples/README.md) · [文档导航](README.md)

代码片段用于说明接口和使用顺序，不是对机器人执行过的验收记录。已有验证与真机检查边界见[测试说明](../development.md#testing)。

## English: Motion, lights and touch

Send movement and light requests, and read touch or connection events. The SDK manages the connection to the body controller.
Initialize, check READY, handle events or request an intended action, then close. Initialization may still be connecting when it returns.

- The program cannot read the servos' actual angles. Command targets, ACK/DONE and reported final angles do not prove arrival or stopping. Clear the entire travel area and keep manual power disconnection available; a disconnected ESP32 cannot deliver Stop.
- Use one application task to read events and change subscriptions. Choose queued reads or callback dispatch, not both; do not open or poll a second body connection.
- Copy event data before its callback returns. Keep callback context alive until dispatch returns, even after unsubscribe. Do not dispatch recursively or initialize/close from a callback.
- After lost events, cancel pending actions; close/init outside callbacks, resubscribe, wait for a new READY, and require a new user action. Reconnection or an empty queue must not replay old motion.
- Check operation and cleanup results separately. Retry failed cleanup before treating resources as released.


## Motion safety


本页面向编写运动控制或运行硬件体检的人。应用能要求舵机转到某个角度，
但不能读取它实际上转到了哪里。例如，发出“转到 90 度”的命令后，应用无法确认
舵机是否真的到了 90 度，也无法确认它是否卡住或已经停止。启用运动前先阅读本页。

### 烧录或运动前：先留出安全空间

- 核实配套 STM32 固件兼容性。SDK 不更新 STM32 或 Himax 固件；兼容性未知或
  缺少完整官方恢复包时**禁止继续烧录**。先准备[备份与官方恢复](../../examples/README.md)。
- **每次**运动前清空**整个可能行程**，不能只为预期的小动作留空间。操作者应随时能够人工断电。
- 体检先命令 **X90/Y120**，再 **X93/Y120** 或 **X90/Y123**。实际起点未知，
  即使要求转到参考位置，也可能从另一端移动很远。这不是归零、标定或实测三度位移；
  退出时也不会自动回中。

### 停止：软件报告不等于实物已停

软件 STOP 不是急停装置；ESP32 断连后无法保证停止命令送达。ACK 表示收到命令，
DONE 表示报告命令完成，都不证明舵机已经到位、没有卡住或机械已经停止。
**必须亲眼确认实物停住；运动不安全或停止命令无法送达时，人工断电。**
不要等待软件消息来证明安全，仍需配套 STM32 安全机制和操作者断电措施。

### 出问题时：先停操作，再排查原因

1. 停止继续操作；有危险先人工断电。保留错误日志，排查供电、连接和配套固件。
2. 取消待执行运动，不要反复触摸尝试解锁，**禁止自动重放旧运动**。
   重连、命令完成或清空待处理事件都不等于故障解除或机械安全。
3. 自行编写恢复逻辑时，按[身体 API 的完整恢复步骤](body.md)处理。
   恢复后重新动作必须由**新的用户操作**发起，不能因为连接恢复就继续旧动作。

### 确认真正的动作结果

方向、整个可运动范围与实际停止必须由人工或未来独立测试装置观察。
记录配套固件版本、公开源码／构建哈希及逐项结果。电脑上的主机测试只检查软件状态与顺序；
历史上的位置测量和标定不是当前前提，也不能代替实物观察。

下一步：[人工硬件体检](../../examples/hardware_check/README_zh.md)。

### 开发接口说明：保留兼容接口不代表能测量角度

以下供修改应用时查阅；精确调用与恢复顺序见[身体 API](body.md)。

| 结果或接口 | 能得出什么结论 |
| --- | --- |
| `watcher_hw_body_request_position()` | 返回 `ESP_ERR_NOT_SUPPORTED`，不能测量实际角度 |
| 注册非空的位置回调 | 返回 `ESP_ERR_NOT_SUPPORTED`；用空回调取消订阅仍可重复执行 |
| 历史 `POSITION` 帧或保留编号 | 仅为兼容旧接口保留，不是当前测得的实际角度 |
| ACK/NACK | 收到命令／拒绝命令，不证明实际移动 |
| DONE/FAULT | 报告命令完成／故障，不证明实际角度、没有卡住或机械已停 |
| 命令坐标或 PWM 推算角度 | 是要求值而非测量值；PWM 指发给舵机的电脉冲信号 |

命令角度限制、主动锁定／释放和 STOP 仍保留。不能用旧位置消息、命令确认或目标角度
判断行程已清空、限位已恢复或身体已停止。


## Motion safety (English)


For anyone writing motion controls or running the hardware check. The application
can request an angle but cannot read where the servo actually ends up. For example,
after requesting **90 degrees**, it cannot confirm that the servo reached 90 degrees,
is not stuck, or has stopped. Read this page before enabling motion.

### Before flashing or moving: clear the space

- Verify paired STM32 firmware compatibility. This SDK does not update STM32 or
  Himax firmware. Unknown compatibility or a missing complete official restore
  bundle is a **do-not-flash** blocker. Prepare [backups and official recovery](../../examples/README.md).
- Before **every** motion, clear the **entire possible travel**, not just the expected
  small move. Keep operator-controlled power disconnection available.
- The hardware check first commands **X90/Y120**, then **X93/Y120** or **X90/Y123**.
  The actual starting position is unknown: even a reference move can travel far
  from the other end. This is not homing, calibration or a measured three-degree
  move. The example does not automatically return to center when you exit.

### Stopping: a software report is not a physical stop

Software STOP is not an emergency-stop device; a disconnected ESP32 cannot guarantee
stop delivery. ACK means the command was received; DONE reports command completion.
Neither proves that the servo reached the angle, is not stuck, or physically stopped.
**Observe the body stop. If motion is unsafe or the stop command cannot arrive,
use operator-controlled power disconnection.** Do not wait for a software message
as proof of safety. Paired STM32 safety and an operator power cut remain necessary.

### When something goes wrong: stop operating, then investigate

1. Stop operating the controls; disconnect power manually if unsafe. Keep error
   logs and check power, connections and paired firmware.
2. Cancel pending motion. Do not keep touching to unlock controls, and **never
   replay old motion automatically**. Reconnecting, command completion or clearing
   queued events does not clear the fault or establish mechanical safety.
3. If you write recovery logic, follow the complete [body API recovery procedure](body.md).
   Movement afterward requires a **new user action**; a restored connection must
   not resume an old action.

### Check the physical result

A human or independent future test fixture must observe direction, the entire
range of movement and actual stop. Record paired-firmware versions, public
source/build hashes and each result. Host tests only check software state and
sequencing; historical position measurement/calibration is not a current
prerequisite or a replacement for physical observation.

Continue with the [manual hardware check](../../examples/hardware_check/README.md).

### Developer interface notes: compatibility does not provide angle measurements

Use this section when changing the application. Exact calls and recovery order
belong in the [body API](body.md).

| Result / interface | What you can conclude |
| --- | --- |
| `watcher_hw_body_request_position()` | Returns `ESP_ERR_NOT_SUPPORTED`; it cannot measure the actual angle |
| Registering a non-null position callback | Returns `ESP_ERR_NOT_SUPPORTED`; cancelling the subscription with a null callback is still safe to repeat |
| Historical `POSITION` frames or reserved identifiers | Retained for compatibility, not current measurements of actual angles |
| ACK/NACK | Command received/rejected, not proof of physical movement |
| DONE/FAULT | Command completion/fault report, not proof of actual angle, lack of stall or physical stopping |
| Requested coordinates or PWM-derived angles | Command values, not measured angles; PWM is the electrical pulse signal sent to a servo |

Command angle limits, explicit lock/release and STOP remain available. Never use
old position messages, acknowledgements or requested angles to decide that travel
is clear, limits have been recovered or the body has stopped.
