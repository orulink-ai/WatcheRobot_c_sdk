# Shared example internals / 示例内部共享代码

This is **not a standalone ESP-IDF project**, a fifth app or a published component.
Do not run `idf.py -C examples/common build`. It has no independent project/main/partition entry.

`head`/`robot` compile the shared head demo; `hardware_check` reuses applicable media/check helpers.
`head_demo_start()` starts one process-lifetime media-owner task and shared UI, with no dynamic shutdown
or automatic retry loop. It is an example helper, not part of the `watcher_hw_*` public API contract.

- `head_demo.*`: example UI and media-owner orchestration.
- `demo_audio.*`, `demo_record.*`, `demo_playback.*`, `demo_speech.*`: example audio/record/playback policy.
- `demo_image.*`, `demo_state.*`: image/state ownership helpers.
- `check_*`: shared check orchestration/layout/interaction support, not automatic physical acceptance.
- [assets](assets/README.md): bundled demonstration resource provenance and licensing.
- `test_support/host`: host CMake tests, invoked separately from IDF; [commands/reporting](../../docs/testing.md).

Use the owning [head](../head/README.md), [robot](../robot/README.md) or
[hardware_check](../hardware_check/README.md) project defaults, manifests and build/flash instructions.
No component Registry installation is promised for this directory.

Keep ownership intact: audio/camera lifecycle stays in the media-owner task; LVGL access is locked;
retained images must not reference a borrowed camera callback buffer. UI actions and playback progress
are not physical acceptance. Motion/no-feedback, manual power cut, pairing, backup and complete recovery
requirements remain those of the owning application.

中文：这里只是示例共享实现，不能独立 IDF 构建或当作第五个应用/公开 SDK 接口；从所属工程构建。
不得改变单任务媒体所有权、图像借用及 LVGL 锁合同，不以 UI 状态替代实际声音/图像/运动验收。
