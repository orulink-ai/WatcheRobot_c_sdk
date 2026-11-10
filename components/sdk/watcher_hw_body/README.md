# watcher_hw_body

One process-wide MCU runtime exposes motion commands, LED requests and queued link/touch/motion events. Physical servo position feedback is not available.

- Public header: [`include/watcher_hw_body.h`](include/watcher_hw_body.h)
- [Usage, lifecycle sample, ownership and limitations](../../../docs/api/body.md)
- [Example](../../../examples/body/README.md) · [Dependencies/configuration](../../../docs/dependencies.md)

## Minimal usage / 最小用法

One task owns event consumption/subscription; choose polling or dispatch. Runtime owns MCU link exclusively. No physical feedback; do not send a sample move. Overflow cancels pending intent and requires explicit close/init/resubscribe outside callbacks; fresh READY and new user intent are mandatory.

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

These lifecycle snippets have not been compiled by the documentation task. Check operation and cleanup errors independently; do not assume hardware release after failed cleanup. Complete behavior and module limits are in the linked API guide.

## Integration / 集成

Development preview; use with the full source checkout and `examples/sdk.cmake`, not an unverified
Registry install. ESP-IDF 6.0.2 / ESP32-S3 is the example contract; display/head uses LVGL 8.4.0.
Direct dependencies: watcher_hw_core, mcu_runtime, mcu_motion_service, mcu_led_service, mcu_sensor_service; private freertos, esp_timer, motion_arbiter. See the linked usage guide for the actual minimal init/operation/cleanup
snippet (core is caller-owned FIFO/types, without a hardware lifecycle).

中文：随完整源码示例使用，未提供已发布组件安装命令。真实 API 用法、任务所有权、错误处理及限制见上方使用指南。
Do not use a lifecycle sample as a motion, acoustic, camera or LCD acceptance test.

First-party code follows the repository [license](../../../LICENSE); dependencies retain their own licenses.
