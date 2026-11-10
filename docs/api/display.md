# 在屏幕上显示文字和界面

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

示例记录操作和清理两个结果，返回值优先保留操作错误。真实应用还必须处理清理失败（例如重试关闭），不能记录后就把资源交给别的使用者。

## 界面锁与资源有效期

由一个应用任务管理初始化和关闭。应用对 LVGL 的所有操作都要先 `watcher_hw_display_lock(timeout_ms)`，确认返回 true，操作结束后 `watcher_hw_display_unlock()`；加锁失败时不能继续操作界面。锁用于防止多个任务同时修改界面。

`watcher_hw_display_lvgl()`、`watcher_hw_display_panel()`、`watcher_hw_display_touch()` 返回的是 SDK 管理对象的引用（接口里称借用句柄），不是把对象交给应用管理：

- 只有设备就绪时才能取得有效句柄，未就绪时可能返回 NULL；即使拿到句柄也仍需遵守界面锁要求。
- 不要自行释放这些对象；关闭后不要保留或继续使用它们。
- SDK 负责将 LVGL 画面更新到屏幕，不要在 LVGL 运行时另外直接向屏幕绘图。
- 关闭前先停止所有使用者，包括其他任务和仍持有句柄的代码；不要在持有界面锁时、在 LVGL 回调中，或其他任务仍使用句柄时关闭。

初始化或关闭失败也要检查清理结果。不能认为函数返回错误就已经释放所有资源，必要时重试 close。

## 配置与实际屏幕检查

使用 LVGL 8.4.0 及 head 示例的配套配置，包括 RGB565 颜色格式/字节交换、字体和八线 PSRAM。本接口不承诺兼容 LVGL 9。

软件截图不能证明真机屏幕、边缘触摸或板级 IDF6 触摸适配正常。请按[硬件检查](../hardware-check.md)在实物上确认；最小代码只演示开关资源，不是 LCD 验收。

## 接入与完整示例

- 公开头文件：[`watcher_hw_display.h`](../../components/sdk/watcher_hw_display/include/watcher_hw_display.h)。接口名称和参数以此为准。
- 使用完整源码与示例匹配的配置、分区和依赖清单；当前为开发预览，不提供未经验证的组件仓库安装命令。仅复制头文件不能补齐所有依赖。
- 直接 CMake 依赖：watcher_hw_core、sensecap-watcher、esp_lvgl_port、lvgl。详见[依赖与本地适配](../dependencies.md)。
- [可运行的 head 示例](../../examples/head/README.md) · [组合示例](../../examples/robot/README.md)
- [构建、配套固件、备份与恢复](../build-and-flash.md) · [文档导航](../README.md)

代码片段用于说明接口和使用顺序，不是对机器人执行过的验收记录。已有验证与真机检查边界见[测试说明](../testing.md)。

## English: Draw text, buttons and screens

Use the LVGL graphics library to draw the interface and handle screen touch. The display example above checks setup and cleanup; its label is removed before closing, so it is not a persistent UI demo.

- Initialize first. Lock before reading or changing LVGL objects, then unlock after the change. Do not call close while holding this lock.
- One application task coordinates initialization and closing. Handles returned by the SDK are temporary references, not objects the application may free; stop using them before closing.
- Do not draw to the panel independently of the SDK. Stop other screen users before cleanup, check close results, and retry failed cleanup.
- Follow the checked-in LVGL 8.4.0 configuration; this guide does not claim LVGL 9 support.
