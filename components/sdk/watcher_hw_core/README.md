# watcher_hw_core

Status/event types and a caller-owned bounded FIFO shared by the hardware wrappers; no hardware initialization API.

- Public header: [`include/watcher_hw_core.h`](include/watcher_hw_core.h)
- [Usage, lifecycle sample, ownership and limitations](../../../docs/api/core.md)
- [Example](../../../examples/body/README.md) · [Dependencies/configuration](../../../docs/dependencies.md)

## Minimal usage / 最小用法

Caller owns queue storage and serializes standalone access. No hardware init/close exists for core. FIFO retains older events and drops the newest on overflow; the body safety latch is a separate module policy.

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

These lifecycle snippets have not been compiled by the documentation task. Check operation and cleanup errors independently; do not assume hardware release after failed cleanup. Complete behavior and module limits are in the linked API guide.

## Integration / 集成

Development preview; use with the full source checkout and `examples/sdk.cmake`, not an unverified
Registry install. ESP-IDF 6.0.2 / ESP32-S3 is the example contract; display/head uses LVGL 8.4.0.
Direct dependencies: No additional components declared; ESP-IDF provides esp_err.h. See the linked usage guide for the actual minimal init/operation/cleanup
snippet (core is caller-owned FIFO/types, without a hardware lifecycle).

中文：随完整源码示例使用，未提供已发布组件安装命令。真实 API 用法、任务所有权、错误处理及限制见上方使用指南。
Do not use a lifecycle sample as a motion, acoustic, camera or LCD acceptance test.

First-party code follows the repository [license](../../../LICENSE); dependencies retain their own licenses.
