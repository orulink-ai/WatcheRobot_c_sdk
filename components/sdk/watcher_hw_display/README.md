# watcher_hw_display

Board display initialization and LVGL integration, with borrowed low-level handles and explicit locking.

- Public header: [`include/watcher_hw_display.h`](include/watcher_hw_display.h)
- [Usage, lifecycle sample, ownership and limitations](../../../docs/api/display.md)
- [Example](../../../examples/head/README.md) · [Dependencies/configuration](../../../docs/dependencies.md)

## Minimal usage / 最小用法

Single lifecycle owner; lock/unlock all LVGL access. Handles are borrowed until close. Quiesce users before teardown and never close inside a callback or with the LVGL lock held. SDK owns panel flushing.

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

These lifecycle snippets have not been compiled by the documentation task. Check operation and cleanup errors independently; do not assume hardware release after failed cleanup. Complete behavior and module limits are in the linked API guide.

## Integration / 集成

Development preview; use with the full source checkout and `examples/sdk.cmake`, not an unverified
Registry install. ESP-IDF 6.0.2 / ESP32-S3 is the example contract; display/head uses LVGL 8.4.0.
Direct dependencies: watcher_hw_core, sensecap-watcher, esp_lvgl_port, lvgl. See the linked usage guide for the actual minimal init/operation/cleanup
snippet (core is caller-owned FIFO/types, without a hardware lifecycle).

中文：随完整源码示例使用，未提供已发布组件安装命令。真实 API 用法、任务所有权、错误处理及限制见上方使用指南。
Do not use a lifecycle sample as a motion, acoustic, camera or LCD acceptance test.

First-party code follows the repository [license](../../../LICENSE); dependencies retain their own licenses.
