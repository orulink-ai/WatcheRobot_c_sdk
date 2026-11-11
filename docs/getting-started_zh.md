[English](getting-started.md) | 简体中文

# 从源码运行第一个 C 应用

用最小 [hello_display 示例](../examples/hello_display/README.md)显示 `Hello, WatcheRobot!`，再修改文字并重新构建。它不启动摄像头、录音或身体运动。所有命令都在**仓库根目录**执行；C 程序运行在设备的 ESP32-S3 上。

## 1. 准备设备和环境

准备 WatcheRobot 头部、USB 数据线、稳定供电、Git 和带 ESP32-S3 工具链的 **ESP-IDF 6.0.2**。屏幕示例无需连接身体。安装按[乐鑫官方指南](https://docs.espressif.com/projects/esp-idf/zh_CN/v6.0.2/esp32s3/get-started/index.html)操作；Windows 打开安装器提供的 ESP-IDF 终端，macOS/Linux 激活安装目录中的 `export.sh`。

硬件和配套固件要求见[兼容性说明](hardware-compatibility.md)。

## 2. 获取完整仓库

```sh
git clone https://github.com/orulink-ai/WatcheRobot_c_sdk.git
cd WatcheRobot_c_sdk
idf.py --version
```

预期显示 `ESP-IDF v6.0.2`。

不要只把示例目录复制到仓库外：它依赖 `examples/sdk.cmake` 和组件相对路径。

## 3. 构建示例

```sh
idf.py -C examples/hello_display build
```

首次构建下载依赖；产物包括 `examples/hello_display/build/watcher_hello_display.bin`、引导程序、分区表及 `flash_args`。应用 `.bin` **不是从 0x0 写入的完整镜像**。

本工程默认 ESP32-S3、16 MB flash 配置、80 MHz 八线 PSRAM、LVGL 8.4.0。工程配置和依赖文件已随示例提供。

## 4. 连接设备并烧录

关闭其他串口工具，只连接目标设备：

```sh
python -m serial.tools.list_ports -v
```

选择 **CH342 SERIAL-B（ESP32）**，不是 SERIAL-A（Himax），不按 COM 号码大小判断。下文 `PORT` 必须替换成系统列出的 Windows COM 端口或 Unix 设备路径。

首次烧录会写入示例的引导程序、分区表和应用，替换原应用并可能覆盖原配置。需要保留的数据请先备份；备份与恢复见[烧录说明](hardware-compatibility.md#备份与分区检查)。

```sh
idf.py -C examples/hello_display -p PORT -b 460800 flash monitor
```

使用上述命令由 IDF 处理烧录地址；恢复官方固件时，按[完整恢复流程](https://wiki.orulink.ai/docs/flashing#full)操作。

## 5. 看见结果，再改一句文字

屏幕应显示 **Hello, WatcheRobot!**，日志出现 `Text displayed; LVGL keeps running after app_main returns`。`app_main()` 返回后 LVGL 继续刷新。按 **Ctrl+]** 退出串口监视器；这不会停止设备程序。

打开 [`main/app_main.c`](../examples/hello_display/main/app_main.c)，把字符串改成 `My first robot app`。重新执行 build 和 flash monitor，屏幕应显示新文字。

| 工程文件 | 职责 |
| --- | --- |
| `main/app_main.c` | 程序入口和功能调用 |
| `main/CMakeLists.txt` | 登记源文件和直接依赖 |
| `main/idf_component.yml`、`dependencies.lock` | 配套依赖声明和解析版本，随示例保留 |
| `CMakeLists.txt`、`../sdk.cmake` | 选择组件并载入 IDF，保留仓库相对路径 |
| `sdkconfig.defaults`、`partitions.csv` | 硬件配置及烧录布局，不是任意设备通用配置 |

## 6. 按功能继续

在[功能指南](features.md)中查找要添加的接口，或从[示例目录](../examples/README.md)选择完整工程。同一硬件由一个管理任务负责生命周期，初始化失败后不继续调用功能；不要让综合演示和自己的代码同时初始化同一硬件。

## 常见问题

- `idf.py` 不存在或版本不符：重新激活 6.0.2 环境，不绕过工程版本检查。
- 下载失败：解决网络问题，保留 manifest/lock，不随意升级同名驱动。
- 串口打不开：关闭占用软件，检查 SERIAL-B、线缆与驱动；不以整片擦除排障。
- 屏幕无字：保留 `Display failed` 日志，核对供电、PSRAM 和运行固件，不启动第二个显示实例。
- 人脸示例显示 `Finished (60 seconds)`：是定时结束，按 RESET 可重新运行，见[示例说明](../examples/face_detection/README_zh.md)。
