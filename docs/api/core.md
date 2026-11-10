# Core: shared status and bounded events

Status/event types and a caller-owned bounded FIFO shared by the hardware wrappers; no hardware initialization API.

Public contract: [`watcher_hw_core.h`](../../components/sdk/watcher_hw_core/include/watcher_hw_core.h).
This guide uses the checked-in header, not an invented convenience API. Use the complete source checkout;
no published Registry install command is offered. Snippets illustrate ownership/lifecycle and are compile-checked in an isolated ESP-IDF consumer;
they are not executed on a robot or physical acceptance tests. See [verification](../testing.md).

## Minimal lifecycle / 最小生命周期

```c
#include "watcher_hw_core.h"

esp_err_t local_queue_roundtrip(void) {
    watcher_hw_event_queue_t queue;
    watcher_hw_event_queue_init(&queue);
    watcher_hw_event_t input = {.type = WATCHER_HW_EVENT_LINK};
    esp_err_t err = watcher_hw_event_push(&queue, &input);
    if (err != ESP_OK) return err;
    watcher_hw_event_t output;
    return watcher_hw_event_pop(&queue, &output);
    /* Caller-owned stack queue needs no close/free operation. */
}
```

Check every return value in the application. A first-operation error and a cleanup error are distinct;
log both in production and do not assume failed cleanup released hardware.

## Status and queue contract

`watcher_hw_status_t` has `state` (CLOSED, STARTING, READY, FAULT) and `last_error`. It is returned by
module-specific status functions, not by a global core init/status API. Check the state as well as the
function return value. An event's `received_us` is the copied monotonic ESP timer publication timestamp,
not wall-clock time. Match type and size before interpreting payload; use `memcpy` into aligned typed
storage rather than blindly casting the byte array.

A queue stores 32 events with 48-byte maximum payloads. The caller owns storage/lifetime and must
serialize standalone access; SDK modules do their own serialization. On overflow, older events stay,
the newest is dropped and `dropped` increments. This FIFO primitive does not itself implement the body
runtime's safety latch/recovery policy. There is no queue destructor: stop users before storage expires.
The snippet needs no hardware and deliberately publishes no fabricated device position.

中文：core 只提供共享类型和有界队列，不存在 core_init/core_close；队列由调用者持有，
独立使用需自行串行化。通用 FIFO 溢出规则不能替代 body 的故障锁定恢复合同。


## Dependencies and examples

Direct CMake dependencies: No additional components declared; ESP-IDF provides esp_err.h. Use the matching example defaults, partitions and manifest; headers
alone do not supply the transitive dependency closure. [Dependency details](../dependencies.md).

- [Runnable body example](../../examples/body/README.md)
- [Combined robot](../../examples/robot/README.md)
- [Build, paired firmware, backups and full recovery](../getting-started.md)
- [API/documentation index](../README.md)
