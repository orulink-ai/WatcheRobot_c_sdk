# Display: LVGL, panel and touch handles

Board display initialization and LVGL integration, with borrowed low-level handles and explicit locking.

Public contract: [`watcher_hw_display.h`](../../components/sdk/watcher_hw_display/include/watcher_hw_display.h).
This guide uses the checked-in header, not an invented convenience API. Use the complete source checkout;
no published Registry install command is offered. Snippets illustrate ownership/lifecycle and are compile-checked in an isolated ESP-IDF consumer;
they are not executed on a robot or physical acceptance tests. See [verification](../testing.md).

## Minimal lifecycle / 最小生命周期

```c
#include "watcher_hw_display.h"

esp_err_t inspect_display_lifecycle(void) {
    esp_err_t err = watcher_hw_display_init();
    if (err != ESP_OK) {
        (void)watcher_hw_display_close(); /* Report/retry cleanup failure in real app. */
        return err;
    }
    if (watcher_hw_display_lock(1000)) {
        lv_obj_t *label = lv_label_create(lv_scr_act());
        if (label) {
            lv_label_set_text(label, "WatcheRobot SDK");
            lv_obj_del(label); /* Clean up before this lifecycle-only sample closes. */
        } else {
            err = ESP_ERR_NO_MEM;
        }
        watcher_hw_display_unlock();
    } else {
        err = ESP_ERR_TIMEOUT;
    }
    esp_err_t closed = watcher_hw_display_close();
    return err != ESP_OK ? err : closed;
}
```

Check every return value in the application. A first-operation error and a cleanup error are distinct;
log both in production and do not assume failed cleanup released hardware.

## Lifetime and LVGL ownership

Use a single application owner for lifecycle. `lvgl()`, `panel()` and `touch()` return borrowed handles,
valid only until close. Do not free them or keep using them after teardown. The SDK owns LVGL flushing:
never independently draw to the panel while LVGL is active. Protect all application LVGL access with
`lock(timeout_ms)`/`unlock()`, check lock failure, and never close while holding the lock, from an LVGL
callback, or while another task still uses borrowed handles. Quiesce other users first.

Use LVGL 8.4.0 with the matching head defaults (RGB565/swap, fonts and octal PSRAM). This API does not
promise LVGL 9 compatibility. A software snapshot cannot certify the real LCD, touch edges or the
board's IDF6 touch patch. See the [manual check](../hardware-check.md) for physical acceptance.

中文：显示/触控句柄为借用，关闭前停止所有使用者；LVGL 操作必须加锁，锁内或回调内不能关闭。
软件截图不是 LCD/边缘触摸验收。


## Dependencies and examples

Direct CMake dependencies: watcher_hw_core, sensecap-watcher, esp_lvgl_port, lvgl. Use the matching example defaults, partitions and manifest; headers
alone do not supply the transitive dependency closure. [Dependency details](../dependencies.md).

- [Runnable head example](../../examples/head/README.md)
- [Combined robot](../../examples/robot/README.md)
- [Build, paired firmware, backups and full recovery](../getting-started.md)
- [API/documentation index](../README.md)
