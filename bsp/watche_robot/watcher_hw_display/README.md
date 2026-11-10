# watcher_hw_display — 屏幕界面与触摸

公开 SDK 组件（public SDK）。通过 LVGL 绘制界面、接入屏幕触摸，由 SDK 管理刷新、屏幕和触摸对象。

## 接口与依赖

- 接口：[`watcher_hw_display.h`](include/watcher_hw_display.h)；参数与错误处理见[使用指南](../../../docs/api/display.md)。
- 依赖：`watcher_hw_core`、`sensecap-watcher`、`esp_lvgl_port` 和 `lvgl`。使用仓库配套的 LVGL 8.4.0 配置，不承诺 LVGL 9 兼容。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 使用约束

- 一个应用任务负责初始化与关闭。操作 LVGL 对象前加锁并检查成功，结束后解锁。
- 返回的显示、屏幕和触摸句柄是临时借用，不能自行释放，也不能在关闭后使用。关闭前停止所有使用者。
- 不得在持有 LVGL 锁、LVGL 回调内或其他任务仍使用借用句柄时关闭。不要绕过 SDK/LVGL 并行向 panel 直接绘图。
- 分别检查操作和关闭结果；清理失败时重试，不能据错误返回认定资源已释放。

## English

Public SDK for an LVGL 8.4.0 display and touch. Lock LVGL access, retain no handles after close, and stop all users before checked cleanup outside locks and callbacks.

第一方代码遵循仓库 [LICENSE](../../../LICENSE)；依赖保留各自许可证。
