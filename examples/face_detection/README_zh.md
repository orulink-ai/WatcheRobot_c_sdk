[English](README.md) | 简体中文

# 使用已安装模型检测人脸

本例读取 Himax 模型目录，选择经过身份核验的人脸模型，在屏幕上显示**人脸数和结果帧号，运行 60 秒后停止**。C 程序运行在头部 ESP32-S3，模型推理在 Himax 上完成，无需联网或连接身体。

屏幕只显示文字，不显示摄像头画面或检测框。人脸检测回答画面中有没有脸；本例不识别人物身份、不录入人脸，也不追踪某个具体的人。

## 1. 准备设备并构建

首次使用先完成[上手教程](../../docs/getting-started_zh.md)中的源码获取、ESP-IDF 环境安装和串口识别。本例依赖[示例共享配置](../sdk.cmake)，请使用完整仓库，不单独复制示例文件夹。

- 使用 **ESP-IDF 6.0.2**、ESP32-S3 工具链及本工程配套配置和依赖。
- 准备通电的 WatcheRobot 头部和 USB 数据线，无需身体。
- Himax 已安装匹配的 PTL/WV1 固件和预期人脸模型；缺少时先完成[模型获取与安装](../../docs/model-deployment.md)。本例不上传模型，也不更新 Himax 固件。
- 配套固件要求见[兼容性说明](../../docs/hardware-compatibility.md)。

在已激活的 IDF 终端中，从**仓库根目录**执行：

```sh
idf.py --version
idf.py -C examples/face_detection build
```

应用产物为 `examples/face_detection/build/watcher_face_detection.bin`，不是从 0x0 写入的完整镜像。保留工程的 [sdkconfig.defaults](sdkconfig.defaults)、[partitions.csv](partitions.csv)、[依赖声明](main/idf_component.yml)和[锁文件](dependencies.lock)。

## 2. 烧录并查看日志

将 `PORT` 替换为实际识别出的 **CH342 SERIAL-B（ESP32）** 端口，不是 SERIAL-A（Himax）。关闭其他串口工具。

烧录会替换原应用和分区布局，可能覆盖配置。需要保留数据时先备份，详见[备份与恢复](../../docs/hardware-compatibility.md#备份与分区检查)。

```sh
idf.py -C examples/face_detection -p PORT -b 460800 flash monitor
```

若设备已经安装本示例，只查看日志时执行：

```sh
idf.py -C examples/face_detection -p PORT monitor
```

按 **Ctrl+]** 退出监视器；退出不会停止推理。按设备 RESET 会重新运行示例。本程序没有触摸按钮或串口测试命令。

## 3. 观察真实结果

| 屏幕文字 | 预期行为 |
| --- | --- |
| `Reading model catalog...` | 读取四个槽位，日志打印模型 ID、名称、verified 和 face 标志；可能需要数秒。 |
| `Face detection / Waiting for first result...` | 推理启动，等待首帧及曝光稳定。 |
| `Faces: … / Frame: …` | 显示最新检测框数量和结果序号。帧号允许跳号，不是 FPS。 |
| `Finished (60 seconds) / Reset to run again` | 正常定时结束；60 秒从启动接口成功返回起算，包含等待首个回调的时间。 |

在这一分钟内，让镜头前无人脸约 10 秒，再在正常光线下距离摄像头约 30–80 厘米正对镜头 10 秒，最后离开镜头 10 秒。预期 **Faces 0→1→0，Frame 持续增加**。建议距离用于基础检查，不是产品额定检测范围。脸在画面内时可缓慢左右移动，观察是否仍能检测。

日志会打印 `Model … verified=… face=…`、`Frame=… faces=…`，正常结束时打印 `Run result: ESP_OK`。

## 4. 找到调用入口并做一次修改

完整可构建代码在 [main/app_main.c](main/app_main.c)，入口为 `app_main()`；直接依赖在 [main/CMakeLists.txt](main/CMakeLists.txt)。

| 代码位置 | 作用 |
| --- | --- |
| `app_main()` 中的模型遍历 | 同时要求 `verified` 和 `contains_face_class`，再选择该模型。 |
| `hal_camera_start_inference(receive_result, queue)` | 启动只传检测结果的推理，不请求 JPEG 预览。 |
| `receive_result()` | 复制元数据到长度为 1 的队列，清空借用的预览指针；新结果可覆盖尚未显示的旧结果。 |
| `xQueueReceive()` 分支与 `show()` | 主任务接收结果，在显示锁内更新标签。 |
| 诊断与清理部分 | 同时检查查询返回值和 `diag.status`；停止匹配的回调所有者、释放相机，成功后才删除队列。 |

第一次修改：找到结果显示处的 `snprintf()`，将文字前缀 `Face detection\nFaces:` 改为 `My face demo\nFaces:`。重新构建并按上面的命令烧录，确认新标题出现，再做一次 0→1→0。

需要延长时间时，将 `end` 截止时间中的 `60000000` 改为 `120000000`（单位微秒），并将结束提示 `Finished (60 seconds)` 同步改为 120 秒。需要根据人脸结果触发应用行为时，在主任务中处理 `frame.box_count`，不要在推理回调中执行阻塞操作。连续检测到脸代表连续结果，不代表不断出现新人。

模型选择、字段含义、停止要求及可选预览见[视觉 API 指南](../../docs/api/vision.md)。只修改槽位号，不足以确认其他模型可用。

## 常见问题

| 现象 | 检查与处理 |
| --- | --- |
| 显示初始化失败或黑屏 | 保留启动日志，核对头部配置和 PSRAM，先运行 [hello_display](../hello_display/README.md) 排查显示。 |
| 读不到模型目录 | 核对供电、配套 Himax 固件及日志中的传输错误；不要同时启动另一套相机控制程序。 |
| `Unverified model`，随后 `ESP_ERR_NOT_SUPPORTED` | 没有选出已核验的人脸模型。按[模型安装说明](../../docs/model-deployment.md)安装配套人脸模型。 |
| `Waiting for first result...` | 短暂等待正常；持续无结果时保留日志，按[首帧诊断说明](../../docs/api/vision.md#首帧等待统计与错误)核查。 |
| 帧号增加但 Faces 一直为 0 | 检查光线、摄像头方向及脸是否完整入镜。必要时通过独立的 [head 示例](../head/README.md)拍照确认视野；切换应用前先结束当前程序。 |
| `Detection failed` | 查看此前错误及 `Run result`；示例遇到运行错误会退出。 |
| `Cleanup failed` | 三次清理后仍未确认停止，代码保留队列内存；保存日志，复位后再让其他应用接管摄像头。 |
| `Finished (60 seconds)` | 正常结束；按 RESET 重测，或按上文修改时长。 |
