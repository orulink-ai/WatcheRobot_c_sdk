# 设备状态与事件队列

需要理解设备是否就绪、判断收到的事件类型，或在自己的代码中按到达顺序暂存事件时，阅读这一页。这里只提供公共数据类型和队列工具，不会启动任何硬件。

队列像一个有容量限制的收件箱：先放入的先取出，这种顺序也叫 FIFO。最短用法是准备队列变量 → 初始化它 → 放入事件 → 取出事件；不需要关闭接口。

## 最短用法

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

队列由应用保存，不需要关闭。多任务使用时必须自行加锁或限制到一个任务。满时保留旧事件、丢弃新事件；这不替代机身模块的丢事件安全恢复。

## 必须保留的使用要求

只提供共享状态/事件类型与先到先取的队列（FIFO），不存在硬件初始化或关闭接口。解释事件数据前核对类型和长度，再复制到对齐的结构体；先停止所有使用者，再让队列变量离开作用域。

完整参数、错误恢复与限制见[使用指南](../../../docs/api/core.md)，公开符号见[`watcher_hw_core.h`](include/watcher_hw_core.h)。代码用于说明使用顺序，不是硬件验收记录；实际验证范围见[测试说明](../../../docs/development.md#testing)。

## 接入项目

当前为开发预览。使用完整源码和 `examples/sdk.cmake`，不要假定可从组件仓库独立安装。示例使用 ESP-IDF 6.0.2 / ESP32-S3；显示示例使用 LVGL 8.4.0。配置、分区和依赖清单要与示例匹配。

- [可运行的 body 示例](../../../examples/body/README.md)
- [依赖与本地适配](../../../docs/development.md#dependencies)

第一方代码遵循仓库[许可证](../../../LICENSE)；依赖保留各自许可证。

## English: Read status and queue events

Shared types describe whether hardware is starting, ready or in error, and let an application store events in arrival order. This is supporting software, not an extra robot feature.

- A successful status query only means the query worked. Check the returned state and error before using hardware.
- The event queue has limited capacity and is stored in memory supplied by the application. Keep that memory alive while in use, and coordinate access if multiple tasks share it.
- Check push/pop results; do not treat missing events or a full queue as successful processing.
- The short example above only puts an event into a local queue and reads it back; it does not initialize or move hardware.
