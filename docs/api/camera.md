# Camera: paired PTL JPEG capture

JPEG capture/streaming through the PTL HAL; no model/AI, network or UI dependency is part of this API.

Public contract: [`watcher_hw_camera.h`](../../components/sdk/watcher_hw_camera/include/watcher_hw_camera.h).
This guide uses the checked-in header, not an invented convenience API. Use the complete source checkout;
no published Registry install command is offered. Snippets illustrate ownership/lifecycle and are compile-checked in an isolated ESP-IDF consumer;
they are not executed on a robot or physical acceptance tests. See [verification](../testing.md).

## Minimal lifecycle / 最小生命周期

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

Check every return value in the application. A first-operation error and a cleanup error are distinct;
log both in production and do not assume failed cleanup released hardware.

## Ownership and backend

Enable `CONFIG_WATCHER_CAMERA_BACKEND_PTL=y` and verify compatible external Himax PTL firmware before
running. Other camera backends are not supported by this public wrapper. Use head project defaults,
octal PSRAM and matching manifests; a successful build cannot verify the paired image.

Serialize init/capture/stream/stop/close in one application owner task. `capture(callback, ctx)` invokes
the callback on the calling task; `stream(fps, callback, ctx)` uses a camera worker; the wrapper accepts 1–30 fps (not a throughput guarantee). JPEG bytes are
borrowed **only during the callback**. Copy before return; never point a retained LVGL image at them.
Do not recursively start/stop/close from the callback. For streaming, stop first from the owner task,
check the stop result, then close; a failed stop is not proof the worker is gone.

`status()` includes current HAL/query/device faults even when locally open. Idle may be READY; streaming
is not required. ESP_OK means the query succeeded, not READY. Transient query faults clear after a
healthy query; lifecycle failures require close/re-init. Do not substitute a filename or HELLO for
pairing acceptance. No image or corrupt image means the hardware item is not passed.

中文：仅支持配套 PTL；JPEG 回调内借用，需留存必须复制；生命周期由单一任务串行控制，
回调中不可递归停流/关闭。状态查询成功不等于设备 READY。


## Dependencies and examples

Direct CMake dependencies: watcher_hw_core, hal_camera (PTL required). Use the matching example defaults, partitions and manifest; headers
alone do not supply the transitive dependency closure. [Dependency details](../dependencies.md).

- [Runnable head example](../../examples/head/README.md)
- [Combined robot](../../examples/robot/README.md)
- [Build, paired firmware, backups and full recovery](../getting-started.md)
- [API/documentation index](../README.md)
