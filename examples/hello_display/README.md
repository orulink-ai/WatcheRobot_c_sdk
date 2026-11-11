# hello_display: First screen / 第一个屏幕程序

Initialize the public display interface, lock LVGL, create a label, unlock, and leave the display running. No camera, audio or body runtime is started.
只初始化显示接口，加锁创建文字后解锁；LVGL 保持运行，不启动相机、音频或身体。

## Build and run / 构建与运行

Follow the complete [English tutorial](../../docs/getting-started.md) / [中文教程](../../docs/getting-started_zh.md), for environment setup and flashing. From the repository root in an activated ESP-IDF 6.0.2 terminal:

```sh
idf.py -C examples/hello_display build
```

Output: `build/watcher_hello_display.bin` within this project. Flashing is a separate operation described in the tutorial; this application binary is not a merged image.
产物在本工程 `build/`；烧录方式见教程，应用文件不是合并镜像。

## Observe and change / 观察与修改

Expect `Hello, WatcheRobot!` on screen and `Text displayed` in the log. Edit the string in [`main/app_main.c`](main/app_main.c), rebuild, then verify the changed text on the device.
屏幕应显示上述文字；改动字符串后重新构建、烧录，即可看到新文字。

The entry checks initialization and lock errors; failure attempts cleanup and does not start another owner. A cleanup error must be investigated before reinitializing. To add buttons, use LVGL events under the same lock; read the [display contract](../../docs/api/display.md).
入口检查初始化和加锁结果；失败时尝试清理，不继续启动另一实例。关闭失败须处理后再初始化。按钮和触摸用 LVGL 事件，访问界面仍需同一把锁。
