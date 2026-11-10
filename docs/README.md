# Documentation / 文档索引

Start by building an example; read the API guide when you want to change its behavior.
从构建示例开始，需要扩展功能时再查 API。当前为开发预览，完整配对实机与恢复验收仍未完成。

| I want to… / 我想…… | Guide / 入口 |
| --- | --- |
| Use hardware APIs by feature / 按功能学习接口用法 | [English](getting-started.md) · [中文](getting-started_zh.md) |
| Build, flash safely and restore / 构建、安全烧录与恢复 | [English](build-and-flash.md) · [中文](build-and-flash_zh.md) |
| Choose an example / 选择示例 | [Examples / 示例](../examples/README.md) |
| Move the body / 控制身体运动 | [Movement API](api/body.md) · [安全说明 / Safety](servo-open-loop_zh.md) · [English safety](servo-open-loop.md) |
| Control lights and respond to touch / 控制灯光与响应触摸 | [Lights and touch API](api/body.md) |
| Take pictures / 拍照与连续画面 | [Camera API](api/camera.md) |
| Record and play sound / 录音与播放 | [Audio API](api/audio.md) |
| Draw a screen interface / 显示界面与屏幕触摸 | [Display API](api/display.md) |
| Check hardware one item at a time / 逐项人工体检 | [English](hardware-check.md) · [中文](hardware-check_zh.md) |

## Development reference / 开发参考

- [Status and events / 状态与事件](api/core.md)
- [Architecture and component mapping / 架构与组件映射](architecture.md) · [Dependencies / 依赖](dependencies.md)
- [Migration / 旧接口迁移](migration.md)
- [Contributing / 贡献](contributing.md) · [Tests and evidence / 测试与证据](testing.md)
- [Source and licenses / 来源与许可](provenance.md)
- [Packaging status / 打包状态](registry-publishing.md): no verified published Registry installation; use source builds.
- [Original designs / 原始设计](design/README.md) · [Historical records / 历史记录](../history/README.md)

Before flashing or movement, use the build-and-flash safety checklist: verify compatible firmware,
backups and a complete restore bundle; clear the full travel and keep manual power disconnection
available. Servos have no physical position feedback; command completion does not prove physical stopping.
烧录或运动前按编译与烧录指南完成安全检查：确认配套、备份与完整恢复包，清空整个行程并保持人工断电可用；
舵机没有物理位置反馈，命令完成不等于机械停止。
