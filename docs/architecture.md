# Architecture / 架构

The repository follows three levels: source components, independent example applications, and developer
guides. It is not the official product application and does not include STM32/Himax implementations.

```text
Application owner tasks (body / head / robot / hardware_check)
  |-- watcher_hw_body ---- mcu_runtime + motion/LED/sensor services
  |                         + motion_arbiter -> mcu_link -> paired STM32
  |-- watcher_hw_camera -- hal_camera (PTL) -> watcher_hx_ptl
  |                         + hx_ptl_protocol/hx_media_protocol -> paired Himax
  |-- watcher_hw_audio --- hal_audio -> codec + media_lib_sal -> BSP/I2S
  |-- watcher_hw_display - sensecap-watcher + esp_lvgl_port + LVGL
  `-- watcher_hw_core ---- status/event types + bounded caller-owned FIFO
```

`examples/sdk.cmake` selects explicit local component directories with `HW_BODY`/`HW_HEAD`; it is not a
Registry resolver. Each example remains an independent ESP-IDF project, with its own defaults,
partitions and manifest. `examples/common` is example-internal UI/media policy, not public SDK API.
The camera API deliberately excludes AI/model, UI and networking policy. Audio owns a codec lease,
not wake-word policy. Display owns LVGL flushing; applications must not independently draw to its panel.

## Ownership and error boundaries

- Body has one process-wide MCU runtime; other code must not initialize/poll the same link.
  One application task chooses FIFO polling or synchronous subscription dispatch, never both.
- Camera lifecycle is serialized by one application task; JPEG bytes are borrowed only during callbacks.
- Audio is blocking and belongs to one owner task; never run it inside MCU/camera callbacks or an LVGL lock.
- Display handles are borrowed until close; lock LVGL mutations and never close while holding the lock.
- `status()` returning ESP_OK means status was obtained, not READY. Check `state` and `last_error`.
- Body overflow latches FAULT. Cancel application intent; explicitly close/init outside callbacks,
  resubscribe and wait for a fresh READY and new user action. Reconnect/draining alone does not recover.

中文：组件负责硬件生命周期与错误边界，示例负责 UI/录放音等策略。状态获取成功不等于 READY，
回调借用数据必须按生命周期使用；丢事件后必须取消业务意图并显式恢复，不能自动重放旧动作。

See [API guides](README.md), [dependency classification](dependencies.md) and [motion safety](servo-open-loop.md).
