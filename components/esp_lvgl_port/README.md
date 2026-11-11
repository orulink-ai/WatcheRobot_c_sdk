# esp_lvgl_port

Local LVGL display/input adapter used by WatcheRobot: **1.4.0-custom.1**, with **LVGL 8.4.0**.
WatcheRobot 使用的本地界面适配组件，负责图形刷新和输入接入；不是未经修改的上游版本。

## Usage / 使用

Applications normally use [`watcher_hw_display`](../../bsp/watche_robot/watcher_hw_display/README.md).
Do not start a second display stack while the public display API owns the hardware.
应用通过公开显示接口使用本组件；不要在 SDK 已管理屏幕时重复初始化或另起刷新任务。

For board integration, see [`esp_lvgl_port.h`](include/esp_lvgl_port.h) and
[`CMakeLists.txt`](CMakeLists.txt). Use the matching source configuration rather than substituting a
same-name Registry component. Lock LVGL changes, retain borrowed display objects only while open,
and close outside the display lock. See the [display API contract](../../docs/api/display.md).
板级集成以头文件和构建声明为准；保留本地 DMA 暂存与释放适配，相关回归在 `test_support/host`。

Upstream project: [Espressif esp-bsp / esp_lvgl_port](https://github.com/espressif/esp-bsp/tree/master/components/esp_lvgl_port).
Existing copyright notices and licensing in the source remain applicable.
原作者署名和源码许可保持适用；本地适配不代表可直接替换为最新上游版本。
