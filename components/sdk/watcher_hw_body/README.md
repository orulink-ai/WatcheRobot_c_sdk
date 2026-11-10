# 机身转动、灯光与触摸

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

示例分别记录操作错误与关闭错误。真实应用必须继续处理清理失败，必要时重试关闭；不要以一次错误返回作为资源已释放的依据。

## 必须保留的使用要求

一个应用任务负责事件消费和订阅变化；主动取事件与回调分发二选一。SDK 独占与机身控制芯片的连接。事件丢失后取消旧动作，在回调外 close/init 并重新订阅，等新的 READY 和用户新指令。ACK/DONE 不能证明实际停稳；留出整个运动空间并保留人工断电手段。

完整参数、错误恢复与限制见[使用指南](../../../docs/api/body.md)，公开符号见[`watcher_hw_body.h`](include/watcher_hw_body.h)。代码用于说明使用顺序，不是硬件验收记录；实际验证范围见[测试说明](../../../docs/testing.md)。

## 接入项目

当前为开发预览。使用完整源码和 `examples/sdk.cmake`，不要假定可从组件仓库独立安装。示例使用 ESP-IDF 6.0.2 / ESP32-S3；显示示例使用 LVGL 8.4.0。配置、分区和依赖清单要与示例匹配。

- [可运行的 body 示例](../../../examples/body/README.md)
- [依赖与本地适配](../../../docs/dependencies.md)

第一方代码遵循仓库[许可证](../../../LICENSE)；依赖保留各自许可证。

## English: Motion, lights and touch

Send movement and light requests, and read touch or connection events. The SDK manages the connection to the body controller.
Initialize, check READY, handle events or request an intended action, then close. Initialization may still be connecting when it returns.

- The program cannot read the servos' actual angles. Command targets, ACK/DONE and reported final angles do not prove arrival or stopping. Clear the entire travel area and keep manual power disconnection available; a disconnected ESP32 cannot deliver Stop.
- Use one application task to read events and change subscriptions. Choose queued reads or callback dispatch, not both; do not open or poll a second body connection.
- Copy event data before its callback returns. Keep callback context alive until dispatch returns, even after unsubscribe. Do not dispatch recursively or initialize/close from a callback.
- After lost events, cancel pending actions; close/init outside callbacks, resubscribe, wait for a new READY, and require a new user action. Reconnection or an empty queue must not replay old motion.
- Check operation and cleanup results separately. Retry failed cleanup before treating resources as released.
