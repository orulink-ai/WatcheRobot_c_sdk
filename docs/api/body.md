# Body: motion, lights and touch

One process-wide MCU runtime exposes motion commands, LED requests and queued link/touch/motion events. Physical servo position feedback is not available.

Public contract: [`watcher_hw_body.h`](../../components/sdk/watcher_hw_body/include/watcher_hw_body.h).
This guide uses the checked-in header, not an invented convenience API. Use the complete source checkout;
no published Registry install command is offered. Snippets illustrate ownership/lifecycle and are compile-checked in an isolated ESP-IDF consumer;
they are not executed on a robot or physical acceptance tests. See [verification](../testing.md).

## Minimal lifecycle / 最小生命周期

```c
#include "watcher_hw_body.h"

/* Run on an application owner task, not in a hardware callback. */
esp_err_t inspect_body(void) {
    esp_err_t err = watcher_hw_body_init();
    if (err != ESP_OK) {
        (void)watcher_hw_body_close(); /* Report/retry cleanup failure in real app. */
        return err;
    }
    watcher_hw_status_t status;
    err = watcher_hw_body_status(&status);
    if (err == ESP_OK && status.state != WATCHER_HW_READY)
        err = status.last_error != ESP_OK ? status.last_error : ESP_ERR_INVALID_STATE;
    /* Deliberately no move/light request in this lifecycle sample. */
    esp_err_t closed = watcher_hw_body_close();
    return err != ESP_OK ? err : closed;
}
```

Check every return value in the application. A first-operation error and a cleanup error are distinct;
log both in production and do not assume failed cleanup released hardware.

## Control and event contract

`watcher_hw_body_move(x_degrees, y_degrees, duration_ms, &sequence)` accepts X 0–180°, Y 100–140°,
and duration 1–65535 ms. These are command bounds, not guaranteed physical limits. The returned sequence
identifies submission, not completion. Never send a demonstration move just to check initialization.
`watcher_hw_body_request_position()` always returns `ESP_ERR_NOT_SUPPORTED` and emits no query/event.
Reference X90/Y120 can be a large move from an unknown actual position. ACK/DONE and reported final
angles are protocol evidence, not measured position or physical stopping. Clear the whole travel and
keep manual power disconnection available; a disconnected peer cannot receive a software stop.

`watcher_hw_body_light(const mcu_led_request_t *)` uses the existing LED zone/effect enums; RGB and
brightness are 0–255. Inspect [the service header](../../components/services/mcu_led_service/include/mcu_led_service.h)
for the request fields. It is not a separate link owner.

Use `next_event()` polling **or** `subscribe()` + `dispatch_events()`, not both: they consume the same
FIFO. One application task owns subscription changes/dispatch; up to four subscribers are supported.
Callbacks run synchronously on the dispatch caller, outside the MCU mutex. The event is borrowed until
callback return. Copy payloads after checking type/size, keep context alive until dispatch returns even
after unsubscribe, and do not recursively dispatch, block on audio or close the runtime from callbacks.
No other code may initialize/poll the MCU link while this runtime is open.

`WATCHER_HW_EVENT_OVERFLOW` precedes retained FIFO events. Its payload is
`watcher_hw_body_event_loss_t` with cumulative `dropped` and best-effort `stop_result`; this is **not** a
physical-stop acknowledgment. A loss latches FAULT/ESP_ERR_NO_MEM and rejects moves/lights; stop remains
available on a ready link. Cancel pending application actions, close/init outside callbacks, resubscribe,
wait for fresh READY and obtain new user intent. Draining FIFO or receiving another HELLO does not clear
the latch. Init/close clear subscriptions. Check `dropped_events()` as a diagnostic.

中文：身体模块独占 MCU 链路，订阅分发与轮询二选一；无位置反馈，丢事件后必须显式恢复，
不能重放旧动作。运动边界不等于物理测量，大行程和人工断电防护不可省略。


## Dependencies and examples

Direct CMake dependencies: watcher_hw_core, mcu_runtime, mcu_motion_service, mcu_led_service, mcu_sensor_service; private freertos, esp_timer, motion_arbiter. Use the matching example defaults, partitions and manifest; headers
alone do not supply the transitive dependency closure. [Dependency details](../dependencies.md).

- [Runnable body example](../../examples/body/README.md)
- [Combined robot](../../examples/robot/README.md)
- [Build, paired firmware, backups and full recovery](../getting-started.md)
- [API/documentation index](../README.md)
