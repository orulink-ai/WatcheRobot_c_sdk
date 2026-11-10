# 屏幕界面与触摸

需要在屏幕上创建文字、按钮等界面，并接入触摸时，使用这一组接口。界面通过 LVGL 图形库绘制，SDK 负责把画面更新到屏幕。

最短流程：初始化 → 加锁 → 操作界面 → 解锁 → 不再使用时关闭。下面创建后立即删除一条文字，只演示资源的打开和关闭；要看到持续显示的界面，请运行 head 示例。

## 最短用法

```c
#include "watcher_hw_display.h"
#include "esp_log.h"

esp_err_t inspect_display_lifecycle(void) {
    esp_err_t err = watcher_hw_display_init();
    if (err != ESP_OK) {
        esp_err_t cleanup = watcher_hw_display_close();
        ESP_LOGE("sdk_example", "init failed: %s; cleanup: %s",
                 esp_err_to_name(err), esp_err_to_name(cleanup));
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
    if (err != ESP_OK || closed != ESP_OK)
        ESP_LOGE("sdk_example", "operation: %s; close: %s",
                 esp_err_to_name(err), esp_err_to_name(closed));
    return err != ESP_OK ? err : closed;
}
```

示例分别记录操作错误与关闭错误。真实应用必须继续处理清理失败，必要时重试关闭；不要以一次错误返回作为资源已释放的依据。

## 必须保留的使用要求

一个应用任务负责打开和关闭；操作 LVGL 界面前加锁并检查成功，结束后解锁。SDK 管理的屏幕和触摸对象只允许临时引用（借用句柄），不能自行释放或在关闭后使用。关闭前停止所有使用者，不得在锁内或 LVGL 回调内关闭；不要绕过 LVGL 同时直接绘图。

完整参数、错误恢复与限制见[使用指南](../../../docs/api/display.md)，公开符号见[`watcher_hw_display.h`](include/watcher_hw_display.h)。代码用于说明使用顺序，不是硬件验收记录；实际验证范围见[测试说明](../../../docs/testing.md)。

## 接入项目

当前为开发预览。使用完整源码和 `examples/sdk.cmake`，不要假定可从组件仓库独立安装。示例使用 ESP-IDF 6.0.2 / ESP32-S3；显示示例使用 LVGL 8.4.0。配置、分区和依赖清单要与示例匹配。

- [可运行的 head 示例](../../../examples/head/README.md)
- [依赖与本地适配](../../../docs/dependencies.md)

第一方代码遵循仓库[许可证](../../../LICENSE)；依赖保留各自许可证。

## English: Draw text, buttons and screens

Use the LVGL graphics library to draw the interface and handle screen touch. The display example above checks setup and cleanup; its label is removed before closing, so it is not a persistent UI demo.

- Initialize first. Lock before reading or changing LVGL objects, then unlock after the change. Do not call close while holding this lock.
- One application task coordinates initialization and closing. Handles returned by the SDK are temporary references, not objects the application may free; stop using them before closing.
- Do not draw to the panel independently of the SDK. Stop other screen users before cleanup, check close results, and retry failed cleanup.
- Follow the checked-in LVGL 8.4.0 configuration; this guide does not claim LVGL 9 support.
