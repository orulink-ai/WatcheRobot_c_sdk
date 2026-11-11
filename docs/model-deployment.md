# 获取与安装人脸模型 / Model provisioning

使用人脸检测前，需要在头部 Himax 芯片上安装配套模型。模型随 Himax 固件包提供；如果设备已能正常运行人脸检测，可直接进入 [face_detection 教程](../examples/face_detection/README_zh.md)。

## 1. 下载

打开 [Releases](https://github.com/orulink-ai/WatcheRobot-public/releases)，按发布说明选择适用于所用 SDK 的 **Himax-only / PTL 包**并解压。包内包含人脸模型、Himax 固件和安装工具。

在解压后的包根目录打开终端，使用包内说明要求的 Python 环境安装依赖：

```sh
python -m pip install -r requirements.txt
```

以下命令在**下载包目录**执行，不是在 C-SDK 仓库中执行。

## 2. 连接设备

接通头部电源，使用 USB 数据线连接电脑，关闭占用串口的 Desktop、浏览器或串口监视器。

```sh
python -m serial.tools.list_ports -v
```

在输出中找到同一台设备的两个端口：

| 端口名称 | 下方命令中的参数 |
| --- | --- |
| SERIAL-B / CH342 B（ESP32） | `ESP32_PORT` |
| SERIAL-A / CH342 A（Himax） | `HIMAX_PORT` |

将占位符替换为实际端口，例如 Windows 的 COM 端口名。按设备名称区分，不按编号大小判断。

## 3. 安装

在包根目录运行：

```sh
python tools/ptl_release.py flash --port ESP32_PORT --vision-port HIMAX_PORT
```

工具会自动检查文件、更新 Himax 固件并安装配套人脸模型，完成后重启设备。此命令适用于 **Himax-only 包**，会暂停 ESP32 应用，但不改写 ESP32 或身体固件。使用其他类型的发布包时，按该包说明操作。

保持供电和 USB 连接，等待终端提示 `Himax flash completed; ESP32 flash unchanged.`。已有匹配模型时工具会跳过模型写入；遇到其他模型会停止安装，保留原模型。若包内命令有调整，以随包说明为准。

## 4. 运行人脸示例

按照 [face_detection 教程](../examples/face_detection/README_zh.md)构建并运行示例。让脸进入镜头再离开，应看到帧号持续增加，`Faces` 从 0 变为 1，再回到 0。

## 常见问题

- **找不到端口或无法连接**：检查 USB 数据线、CH342 驱动，并关闭其他串口程序。
- **提示已有其他模型**：安装器不会覆盖自定义模型，按发布包的恢复说明处理。
- **安装失败**：保留错误日志，按包内故障说明排查；需要恢复原固件时，参见[官方烧录指南](https://wiki.orulink.ai/docs/flashing)。
- **希望使用其他模型**：需有对应的配套模型和安装支持，仅修改 SDK 中的模型编号不会下载或安装模型。

Seeed 原厂固件的用户可参考 [SenseCraft 模型部署指南](https://wiki.seeedstudio.com/visual_trigger_and_ai_flash/)。该流程面向 Seeed 原厂固件；本 SDK 的 PTL 固件使用上面的配套包工具。

## English

Download a compatible **Himax-only / PTL package** from [Releases](https://github.com/orulink-ai/WatcheRobot-public/releases) and extract it. The package includes the model, firmware and installation tools. If face detection already works, go directly to the [face detection tutorial](../examples/face_detection/README.md).

Run the commands above from the extracted package directory: install its requirements, list ports, then run the flash command. Replace `ESP32_PORT` with SERIAL-B and `HIMAX_PORT` with SERIAL-A. Close other serial applications and keep USB and power connected until completion.

The Himax-only installer checks files automatically, updates Himax firmware and installs the face model without writing ESP32 or body firmware. It skips an accepted model and preserves other installed models. Follow the package instructions if its commands differ. Afterward, run the example and observe Faces 0→1→0 as a face enters and leaves the camera view.
