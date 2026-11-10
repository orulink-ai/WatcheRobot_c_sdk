# Public API guides / 公开 API

These guides describe the five checked-in `watcher_hw_*` headers. They do not invent a Registry
installation or add official-app/model/network policy. Source snippets illustrate task ownership;
they are not new firmware-build or hardware-acceptance evidence.

| Module | Guide |
| --- | --- |
| Body | [Motion command, lights, touch, events and overflow recovery](body.md) |
| Camera | [PTL capture/stream and borrowed JPEG lifetime](camera.md) |
| Audio | [Blocking PCM, owner task, codec lease and drain](audio.md) |
| Display | [LVGL locking, borrowed handles and close](display.md) |
| Core | [Status/event types and caller-owned FIFO](core.md) |

中文：以实际公开头文件为准，示例片段说明所有权而非验收；无反馈/配对/备份/人工断电等限制见
[文档导航](../README.md) 与 [safety](../servo-open-loop.md)。
