# sensecap-watcher board support / 板级支持

Board wiring and initialization for the display, touch, audio and camera used by WatcheRobot.
本地板级支持组件，负责硬件引脚、总线与设备初始化；普通应用通过公开硬件接口使用它。

## Usage / 使用

- Display / 屏幕：[`watcher_hw_display`](../sdk/watcher_hw_display/README.md)
- Audio / 声音：[`watcher_hw_audio`](../sdk/watcher_hw_audio/README.md)
- Camera / 相机：[`watcher_hw_camera`](../sdk/watcher_hw_camera/README.md)

Do not initialize shared hardware separately while those APIs own it. In particular, do not draw
directly to the panel alongside LVGL. Stop users and close the owning API before handing resources over.
公开接口打开期间不要重复初始化共享硬件，也不要绕过 LVGL 并行绘图；先停止使用、正确关闭再交接。

## Board integration / 板级适配

Use [`sensecap-watcher.h`](include/sensecap-watcher.h), [`Kconfig`](Kconfig) and
[`CMakeLists.txt`](CMakeLists.txt) with the complete source checkout. Current examples target
ESP32-S3, ESP-IDF 6.0.2 and LVGL 8.4.0; their flash/PSRAM settings must remain matched.
[`patches.cmake`](patches.cmake) preserves the SPD2010 touch IDF6 adaptation; keep this and the
shared example linkage adjustments until equivalent behavior has been verified.
维护时保留触控适配和配套构建设置，不按目录名称直接替换上游组件。修改后构建受影响示例并运行主机回归。

See the existing [license](license.txt) and source copyright notices.
原有署名及许可保留；此组件不是额外板型或已发布的独立平台安装入口。
