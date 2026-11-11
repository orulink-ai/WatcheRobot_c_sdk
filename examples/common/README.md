# Shared example code / 示例共享代码

This directory supplies the photo/audio screen and reusable helpers for the examples.
It is **not a standalone application or public SDK component**. Build [head](../head/README.md),
[robot](../robot/README.md) or [hardware_check](../hardware_check/README.md) instead.
Do not run `idf.py -C examples/common build`.

这里存放示例共用的拍照、音频界面与辅助代码，不是独立应用或公开 SDK 组件；请从所属工程构建。

## If you change the shared code / 修改共享代码时

- One task controls the camera and audio. `head_demo_start()` starts it for the application's lifetime;
  the simple demo has no dynamic shutdown or automatic retry loop. Do not start a second task to recover.
- Lock LVGL access. Copy camera callback data before keeping an image for later display.
- A finished progress bar does not prove that sound was audible or that a picture was correct.
- Keep the owning project's firmware compatibility, backup, full recovery and motion-safety checks.

摄像与音频由一个任务统一操作，不要重复创建任务恢复故障。LVGL 访问要加锁，回调图片需复制后留用。
界面进度不代表实机通过；所属工程的配套、备份、恢复与运动安全条件仍然适用。

## Source map / 源码定位

These are implementation names, not additional SDK features or stable public interfaces.
以下名称仅供定位实现，不是额外功能或稳定公开接口。

| Files | Responsibility / 用途 |
| --- | --- |
| `head_demo.*` | Photo/audio screen and background task / 拍照音频界面与后台任务 |
| `demo_audio.*`, `demo_record.*`, `demo_playback.*`, `demo_speech.*` | Example recording/playback behavior / 示例录放音逻辑 |
| `demo_image.*`, `demo_state.*` | Picture storage and screen state / 图片保存与界面状态 |
| `check_*` | Guided checks and interaction / 引导式体检与交互 |
| [assets](assets/README.md) | Speaker-test sample and license / 扬声器测试样本与许可 |
| `test_support/host` | Computer-side tests / 电脑端测试，见 [commands and evidence](../../CONTRIBUTING.md#checks--修改后检查) |

Use the [API guides](../../docs/api/README.md) for application-facing interfaces. This directory is not a
separately published Component Registry package.
