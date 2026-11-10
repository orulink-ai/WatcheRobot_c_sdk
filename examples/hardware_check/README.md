# Hardware check / 硬件体检

Check movement, lights, touch, pictures, recording/playback and screen operation one item at a time.
A person must observe and confirm the result: **untested is not passed**. This is not an automatic unit test.
逐项检查运动、灯光、触摸、摄像、录音播放和屏幕；必须人工观察、确认，**未测不算通过**。

## Build / 构建

Use **ESP-IDF 6.0.2**. Activate IDF and run from the **repository root**:
使用 **ESP-IDF 6.0.2**，激活环境后在**仓库根目录**执行：

```sh
idf.py -C examples/hardware_check build
```

The build should produce `examples/hardware_check/build/watcher_hw_hardware_check.bin` and its flash
files. It downloads dependencies over the network, but does not write to a device.
预期生成上述应用文件与配套烧录文件；下载依赖需要网络，不会写入设备。

The project selects ESP32-S3, 16 MB flash, 80 MHz octal PSRAM and LVGL 8.4.0. Running needs compatible
STM32 body firmware and matching Himax PTL camera firmware; a build cannot verify this pairing.
工程选择 ESP32-S3、16 MB flash、80 MHz 八线 PSRAM 与 LVGL 8.4.0；运行需要兼容的 STM32 和 Himax PTL 固件，构建不能证明配套正确。

## Safety before flashing or movement / 烧录或运动前的安全检查

Follow [English setup, safety and recovery](../../docs/build-and-flash.md) /
[中文上手、安全检查与恢复](../../docs/build-and-flash_zh.md), using **hardware_check** as the project name.
Verify the ESP32 port, compatible firmware, backups and a complete official recovery bundle.
Full custom flash overwrites official configuration; app-only restoration is insufficient.
Unknown compatibility or recovery assets means stop. Never guess flash offsets or write an app-only binary at `0x0`.

Servos have **no physical position feedback**. Confirming X90/Y120 can cause a **large movement** from an
unknown starting point. Clear the entire travel and keep manual power disconnection available.
ACK/DONE, command coordinates and software STOP do not prove actual position or physical stopping.
Do not rely on disconnected ESP32 software to deliver a stop.

按上手指南完成检查，工程名使用 **hardware_check**：核实 ESP32 端口、兼容固件、备份与完整官方恢复包。
完整自定义烧录会覆盖官方配置，只刷应用不足以恢复；条件不明时停止，不猜偏移、不从 `0x0` 写应用单文件。
舵机无物理位置反馈，确认 X90/Y120 可能大行程；清空整个行程，保留人工断电。
软件完成状态不证明机械停止，断连后不能依靠 ESP32 保证停止命令送达。

## Operate and observe / 操作与观察

- [English: 26-item operator guide](../../docs/hardware-check.md)
- [中文：26 项操作指南](../../docs/hardware-check_zh.md)

After flashing, the screen should show **Hardware check**, with `Hardware check v2 | curved zones` in
the log. Follow the prompts; record actual movement, lights, touch, pictures and sound. Results are
RAM-only and reset on reboot, so save observations externally. Disabled/unrun items and software
progress are not passes. Keep failure logs and board/source/paired-firmware versions.

烧录后应看到 **Hardware check**，日志包含上述版本文字。按提示观察真实运动、灯光、触摸、照片和声音。
结果仅保存在 RAM、重启清空，应另行记录。禁用、未运行或仅进度完成不能算通过，故障时保留日志和软硬件版本。

For errors and official restoration, use the setup guide above; keep operator confirmation enabled.
For computer-only screen regression, see [host tests](test_support/host/README.md): these are not LCD
hardware evidence. / 排障与恢复见上手指南，不能取消人工确认；电脑端界面测试不证明实机屏幕效果。

[Tests and evidence / 测试与证据](../../docs/testing.md)
