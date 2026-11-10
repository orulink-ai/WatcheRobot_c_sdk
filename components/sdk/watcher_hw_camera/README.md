# watcher_hw_camera

JPEG capture/streaming through the PTL HAL; no model/AI, network or UI dependency is part of this API.

- Public header: [`include/watcher_hw_camera.h`](include/watcher_hw_camera.h)
- [Usage, lifecycle sample, ownership and limitations](../../../docs/api/camera.md)
- [Example](../../../examples/head/README.md) · [Dependencies/configuration](../../../docs/dependencies.md)

## Minimal usage / 最小用法

One task serializes lifecycle. JPEG bytes are borrowed only during callbacks (capture caller/stream worker); copy before return. Do not recursively start/stop/close in a callback. Requires matching Himax PTL firmware and PTL configuration.

```c
#include "watcher_hw_camera.h"

static void receive_jpeg(const uint8_t *jpeg, size_t size,
                         uint32_t timestamp_ms, void *ctx) {
    /* Borrowed only here: copy to caller-owned storage before returning if needed. */
    (void)jpeg; (void)size; (void)timestamp_ms; (void)ctx;
}
esp_err_t capture_once(void) {
    esp_err_t err = watcher_hw_camera_init();
    if (err != ESP_OK) {
        (void)watcher_hw_camera_close(); /* Report/retry cleanup failure in real app. */
        return err;
    }
    err = watcher_hw_camera_capture(receive_jpeg, NULL);
    esp_err_t closed = watcher_hw_camera_close();
    return err != ESP_OK ? err : closed;
}
```

These lifecycle snippets have not been compiled by the documentation task. Check operation and cleanup errors independently; do not assume hardware release after failed cleanup. Complete behavior and module limits are in the linked API guide.

## Integration / 集成

Development preview; use with the full source checkout and `examples/sdk.cmake`, not an unverified
Registry install. ESP-IDF 6.0.2 / ESP32-S3 is the example contract; display/head uses LVGL 8.4.0.
Direct dependencies: watcher_hw_core, hal_camera (PTL required). See the linked usage guide for the actual minimal init/operation/cleanup
snippet (core is caller-owned FIFO/types, without a hardware lifecycle).

中文：随完整源码示例使用，未提供已发布组件安装命令。真实 API 用法、任务所有权、错误处理及限制见上方使用指南。
Do not use a lifecycle sample as a motion, acoustic, camera or LCD acceptance test.

First-party code follows the repository [license](../../../LICENSE); dependencies retain their own licenses.
