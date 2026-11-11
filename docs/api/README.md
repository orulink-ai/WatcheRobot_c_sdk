# 按需求查找接口

先选择你要完成的事情，再打开对应页面。每页先说明最短使用步骤，后面保留任务配合、数据有效期和出错恢复要求。

| 你想做什么？ | 使用指南 |
| --- | --- |
| 控制转动、灯光，接收触摸和连接变化 | [机身控制](body.md) |
| 拍一张照片或连续获取图像 | [拍照与取图](camera.md) |
| 从麦克风录音或通过扬声器播放 | [录音与播放](audio.md) |
| 在屏幕上显示文字、按钮和界面 | [屏幕显示](display.md) |
| 理解设备状态，或暂存并按顺序读取事件 | [状态与事件](core.md) |
| 读取模型目录、选择已安装模型、运行人脸检测 | [PTL 视觉进阶接口](vision.md) |

前五页对应五个 `watcher_hw_*` 公开头文件，应用优先使用这些接口。视觉推理另由 `hal_camera` 进阶接口提供，需要已安装模型及匹配固件；SDK 不包含官方应用的完整行为策略或自动联网功能。全部入口及文档位置见[功能对照表](../features.md)。

先运行完整仓库中的示例，再按对应页面接入自己的应用。

**转动前先读[运动注意事项](body.md#motion-safety)**：当前硬件不能实测舵机角度，收到 ACK/DONE 不能证明已经到位或停稳；必须保留人工断电手段。配套固件、备份及恢复见[兼容性说明](../hardware-compatibility.md)。

## English: choose a task

Start with what you want to do, not an internal component name:

| Task | Guide |
| --- | --- |
| Move the body, set lights or receive touch events | [Motion, lights and touch](body.md) |
| Take a photo or receive camera frames | [Camera](camera.md) |
| Record or play sound | [Audio](audio.md) |
| Draw text, buttons and screens | [Display](display.md) |
| Read status or store events in order | [Status and events](core.md) |
| Read model catalog and detect faces | [Advanced PTL vision](vision.md) |

Each page includes working interface names, a short C example and English usage precautions.
Run a complete source example first, then adapt its calls in your application.
Before movement, read [motion precautions](body.md#motion-safety-english); before flashing, follow
[backup and recovery preparation](../../examples/README.md).
