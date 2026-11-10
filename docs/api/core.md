# 查看设备状态与暂存事件

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

队列不占用硬件；所有 push/pop 返回值仍需检查。

## 读取状态与解释事件

`watcher_hw_status_t` 的 `state` 有 CLOSED（关闭）、STARTING（启动中）、READY（就绪）、FAULT（故障），`last_error` 记录相应错误。状态由各硬件接口的 status 函数返回；不存在全局 core 初始化或状态查询函数。函数返回成功只是查询成功，设备是否可用还要看状态。

`watcher_hw_event_t` 包含类型、序号、时间和一段数据。`received_us` 是事件发布时复制的 ESP 单调计时值，单位微秒，用于判断先后和间隔，不是日期时间。解释数据前先核对 `type` 和 `size`，用 `memcpy` 复制到对齐的对应结构体变量，不要直接把字节数组强制转换成结构体指针。

## 队列容量、内存与并发

队列最多保留 32 个事件，每个事件的数据最多 48 字节。队列变量和它的存活时间由应用管理，这就是 caller-owned：SDK 不替你分配或释放这个变量。单独使用时，应用必须防止多个任务同时读写，例如只让一个任务使用或自行加锁；SDK 内部使用的队列由相应模块自行保护。

- push 会复制事件；队列满时保留旧事件、丢弃新事件，`dropped` 增加并返回 `ESP_ERR_NO_MEM`。
- 空队列 pop 返回 `ESP_ERR_NOT_FOUND`；传入空指针、或 push 的事件数据超长，返回 `ESP_ERR_INVALID_ARG`。
- 没有队列析构/关闭接口；在局部变量离开作用域或释放存储前，先停止所有使用者。

这个通用队列本身不负责机身模块的“丢事件后禁止动作”策略。使用机身 API 时，仍必须执行[机身丢事件恢复流程](body.md)。上面的代码只测试内存中的放入/取出，没有访问硬件，也没有伪造设备位置。

## 接入与完整示例

- 公开头文件：[`watcher_hw_core.h`](../../components/sdk/watcher_hw_core/include/watcher_hw_core.h)。接口名称和参数以此为准。
- 使用完整源码与示例匹配的配置、分区和依赖清单；当前为开发预览，不提供未经验证的组件仓库安装命令。仅复制头文件不能补齐所有依赖。
- 直接 CMake 依赖：没有额外声明组件；esp_err.h 由 ESP-IDF 提供。详见[依赖与本地适配](../development.md#dependencies)。
- [可运行的 body 示例](../../examples/body/README.md) · [组合示例](../../examples/robot/README.md)
- [构建、配套固件、备份与恢复](../../examples/README.md) · [文档导航](README.md)

代码片段用于说明接口和使用顺序，不是对机器人执行过的验收记录。已有验证与真机检查边界见[测试说明](../development.md#testing)。

## English: Read status and queue events

Shared types describe whether hardware is starting, ready or in error, and let an application store events in arrival order. This is supporting software, not an extra robot feature.

- A successful status query only means the query worked. Check the returned state and error before using hardware.
- The event queue has limited capacity and is stored in memory supplied by the application. Keep that memory alive while in use, and coordinate access if multiple tasks share it.
- Check push/pop results; do not treat missing events or a full queue as successful processing.
- The short example above only puts an event into a local queue and reads it back; it does not initialize or move hardware.
