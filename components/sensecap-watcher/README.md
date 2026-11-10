# sensecap-watcher board support

Checked-in board support used by the head/display/audio/camera dependency graph. This is not a new
board family, an application or a claim of independent Registry consumption.

- Public low-level header: [`include/sensecap-watcher.h`](include/sensecap-watcher.h)
- Application-facing display guide: [watcher_hw_display](../../docs/api/display.md)
- [Architecture and ownership](../../docs/architecture.md) · [Dependencies/local adaptations](../../docs/dependencies.md)

Use the complete pinned source examples with ESP-IDF 6.0.2 / ESP32-S3, LVGL 8.4.0 and their actual
flash/PSRAM defaults. Existing CMake invokes the checked-in SPD2010 IDF6 touch adaptation through
`patches.cmake`; do not remove it or substitute same-named upstream libraries without regression evidence.
Public SDK wrappers own shared resources: do not initialize/poll/draw independently while they are open.

This page adds navigation only. Existing source attribution and third-party license terms are unchanged.
中文：这里是现有板级支持层，不是新增板型或独立发布承诺；应用优先使用 watcher_hw_*，避免资源冲突。
