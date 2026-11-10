# 按需求查找接口

先选择你要完成的事情，再打开对应页面。每页先说明最短使用步骤，后面保留任务配合、数据有效期和出错恢复要求。

| 你想做什么？ | 使用指南 |
| --- | --- |
| 控制转动、灯光，接收触摸和连接变化 | [机身控制](body.md) |
| 拍一张照片或连续获取图像 | [拍照与取图](camera.md) |
| 从麦克风录音或通过扬声器播放 | [录音与播放](audio.md) |
| 在屏幕上显示文字、按钮和界面 | [屏幕显示](display.md) |
| 理解设备状态，或暂存并按顺序读取事件 | [状态与事件](core.md) |

这五页对应源码中的五个 `watcher_hw_*` 公开头文件。应用优先使用这些接口，不必直接管理底层通信或共享硬件。SDK 不包含官方应用的完整行为策略，也不自动提供模型识别、联网等功能。

使用完整源码与匹配示例接入；这里不提供未经验证的组件仓库安装方式。代码片段说明用法，不是固件烧录或真机验收证据。

**转动前先读[运动注意事项](../servo-open-loop_zh.md)**：当前硬件不能实测舵机角度，收到 ACK/DONE 不能证明已经到位或停稳；必须保留人工断电手段。配套固件、备份及恢复见[文档导航](../README.md)。

## English: choose a task

Start with what you want to do, not an internal component name:

| Task | Guide |
| --- | --- |
| Move the body, set lights or receive touch events | [Motion, lights and touch](body.md) |
| Take a photo or receive camera frames | [Camera](camera.md) |
| Record or play sound | [Audio](audio.md) |
| Draw text, buttons and screens | [Display](display.md) |
| Read status or store events in order | [Status and events](core.md) |

Each page includes working interface names, a short C example and English usage precautions.
Use the complete source examples first. Registry installation and hardware acceptance are not implied.
Before movement, read [motion precautions](../servo-open-loop.md); before flashing, follow
[backup and recovery preparation](../build-and-flash.md).
