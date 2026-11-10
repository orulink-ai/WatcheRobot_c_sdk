# Hardware check / 硬件体检

An operator-guided ESP-IDF application for checking real hardware one item at a time, **not an
automatic unit-test runner**. A human must observe and confirm each item; untested is not passed.

## Build / 构建

Use ESP-IDF 6.0.2 / ESP32-S3, 16 MB flash, 80 MHz octal PSRAM and LVGL 8.4.0 as selected by this project's
defaults. Verify compatible STM32 motion/LED/touch and Himax PTL firmware separately.
From the **WatcheRobot_c_sdk repository root**, with the IDF environment activated:

```sh
idf.py -C examples/hardware_check build
```

Expected output: `examples/hardware_check/build/watcher_hw_hardware_check.bin` and generated flash files.
Source build success does not certify the paired hardware. Before any flash, identify the ESP32 port,
back up required official configuration/data and prepare a verified complete official restore bundle.
Custom full flash overwrites official storage; app-only restoration is insufficient. Stop if paired
firmware or complete recovery assets are unknown. Use only the exact guide commands, not guessed offsets.

## Operate and observe / 操作与观察

- [English: 26-item check](../../docs/hardware-check.md)
- [中文：26 项体检](../../docs/hardware-check_zh.md)
- [English build, flash and full recovery](../../docs/getting-started.md)
- [中文构建、烧录与完整恢复](../../docs/getting-started_zh.md)

Expected startup shows **Hardware check**, with `Hardware check v2 | curved zones` in the log. Follow
operator prompts and record actual sound/image/touch/mechanical observations. Results are RAM-only and
reset on reboot; save them externally. Missing observations, disabled/unrun items or software progress
must never be marked passed. Preserve failure logs and device/source/paired-image identity.

Servos have **no physical position feedback**; confirming X90/Y120 may cause a **large** movement from
an unknown position. Clear the entire travel and keep manual power disconnection available. ACK/DONE,
command coordinates and a successful STOP submission do not prove measured position or physical stop.
Do not rely on disconnected ESP32 software to stop the peer.

中文：逐项人工体检，不是自动通过的单元测试；未测不通过，结果重启丢失应另行保存。
参考位置可能大行程，无反馈，清空整个行程并保持人工断电可用；协议完成不等于机械停止。
先完成配套、备份和完整恢复前置检查，缺资料停止烧录。

For host-only UI regression (not LCD evidence), see the [real LVGL suite](test_support/host/README.md).
For errors/recovery use the setup guide and [evidence boundary](../../docs/testing.md); do not remove
operator confirmation or silently substitute an old firmware image.
