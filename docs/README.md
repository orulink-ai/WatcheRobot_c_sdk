# Documentation / 文档索引

Start from the public source checkout. This SDK is a **development preview**, with no verified
Registry installation release and no new paired-hardware acceptance implied by these documents.

| I want to… / 我想… | Guide / 入口 |
| --- | --- |
| Build, flash safely, recover / 构建、烧录、恢复 | [English](getting-started.md) · [中文](getting-started_zh.md) |
| Choose a runnable example / 选择示例 | [Examples / 示例](../examples/README.md) |
| Control motion/lights or receive touch / 身体、灯光与触摸 | [Body API](api/body.md) |
| Capture JPEG via paired PTL camera / 配套 PTL 摄像头 | [Camera API](api/camera.md) |
| Record/play PCM / 录放音 | [Audio API](api/audio.md) |
| Use LVGL / 显示与触控 | [Display API](api/display.md) |
| Understand status/events / 状态与事件 | [Core API](api/core.md) |
| Perform manual hardware checks / 人工体检 | [English](hardware-check.md) · [中文](hardware-check_zh.md) |
| Understand open-loop movement / 无反馈运动限制 | [English](servo-open-loop.md) · [中文](servo-open-loop_zh.md) |
| Understand the layers / 架构 | [Architecture](architecture.md) · [Dependencies](dependencies.md) |
| Migrate an older application / 迁移旧接口 | [Migration](migration.md) |
| Contribute with reproducible evidence / 贡献与验证 | [Contributing](contributing.md) · [Testing](testing.md) |
| Trace imports and licenses / 追溯来源与许可 | [Provenance](provenance.md) |
| Inspect packaging status / 打包发布状态 | [Registry publishing](registry-publishing.md) |
| Read original design/reviews / 历史设计与审查 | [Design](design/README.md) · [History](../history/README.md) |

Hardware safety: there is no physical servo position feedback. Reference moves can traverse a large
range; ACK/DONE and software STOP are not measured position or physical stopping. Clear the whole travel,
keep manual power disconnection available, and stop before flashing if paired firmware, backups or a
verified complete official restore bundle is missing. / 无反馈、大行程、人工断电、备份和配对恢复前置条件不可省略。
