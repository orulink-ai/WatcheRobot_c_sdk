# Build requirements and dependency changes / 构建要求与依赖变更

Use this page to prepare a source build or review a dependency upgrade. For your
first build, follow [setup](getting-started.md) / [中文上手](getting-started_zh.md).
Use the complete pinned checkout and network access for declared downloads.
本页用于准备构建环境、检查依赖升级。请使用固定版本的完整仓库，并允许下载声明的依赖。

## Match the checked-in configuration / 按仓库配置准备环境

| Item / 项目 | Required configuration / 仓库配置 |
| --- | --- |
| Chip / 芯片 | ESP32-S3 |
| ESP-IDF / 开发框架 | Exactly 6.0.2; checked by `examples/sdk.cmake` / 固定 6.0.2，由构建入口检查 |
| Screen library / 界面库 | LVGL 8.4.0 for head/display and the real-LVGL host tests / 显示与真实界面测试使用 8.4.0 |
| Flash / 闪存 | All four examples select 16 MB and a custom partition table / 四个示例均配置 16 MB 与各自分区表 |
| PSRAM / 外部内存 | head/robot/hardware_check: octal, 80 MHz; body does not enable it / 前三者启用八线 80 MHz，body 不启用 |
| Camera / 相机 | `CONFIG_WATCHER_CAMERA_BACKEND_PTL=y`; matching Himax PTL firmware / 需配套 Himax PTL 固件 |
| Screen format / 显示格式 | RGB565: `CONFIG_LV_COLOR_DEPTH_16`, `CONFIG_LV_COLOR_16_SWAP`; fonts selected by head defaults / 字体见 head 默认配置 |

These are example settings, not measured minimum hardware requirements or a wider
compatibility guarantee. PTL is the camera transport used with the paired Himax device.
以上为示例实际配置，不代表最低硬件需求或其他平台兼容性。PTL 是与配套 Himax 相机通信的传输方式。

## Know where dependencies come from / 区分依赖来源

- **ESP-IDF supplies** the scheduler (FreeRTOS), buses, timers, LCD support, filesystems,
  memory support and encryption library mbedTLS. These are not separate local packages.
  **框架提供**任务调度、通信总线、定时器、显示、文件系统、内存与加密支持。
- **This repository supplies** hardware APIs, services, the STM32 connection and camera
  transport. The body API owns the STM32 connection; `mcu_runtime` provides helpers
  for its polling task rather than a second owner. `hal_camera` selects PTL at configuration.
  **仓库提供**硬件接口及内部通信代码；身体接口统一管理 STM32 连接，不能另起一套连接管理。
- **Checked-in board/vendor code** includes `sensecap-watcher`, `esp_lvgl_port`,
  `esp_codec_dev`, `esp_io_expander_pca95xx_16bit`, `sscma_client` and `media_lib_sal`.
  Keep their licenses and attribution. Board support code (BSP) describes board wiring;
  codec code handles sound conversion. Their upstream READMEs are not SDK application lists.
  **随仓库保存的板级与厂商代码**保留原许可证；BSP 指板级支持，codec 指音频编解码。
- **Downloaded components** are selected by `idf_component.yml` manifests. The head
  manifest pins `esp_jpeg` 1.3.1, LVGL 8.4.0, cJSON 1.7.19, `esp_audio_codec` 2.4.1,
  `esp_lcd_touch` 1.1.1 and `cmake_utilities` 0.5.3. Other manifests add requirements.
  Review the generated dependency lock for the complete resolved set.
  **下载依赖**以所有清单及构建生成的版本锁定文件为准，不能只看上述 head 直接依赖。
- **Paired STM32 and Himax firmware** is a device prerequisite, not code built here.
  **配套设备固件**不是本 SDK 构建产物，仓库不提供替换镜像。

## Review an upgrade / 升级前逐项检查

1. Compare [API CMake files](../components/sdk), manifests and the generated version
   lock. Public headers expose some service, touch and LVGL types, so moving a
   dependency from public `REQUIRES` to private `PRIV_REQUIRES` can break callers.
2. Preserve local adaptations: `sensecap-watcher/patches.cmake` applies the SPD2010
   IDF6 touch fix; `examples/sdk.cmake` adjusts button/knob/LED-strip linkage and
   enables `MBEDTLS_DECLARE_PRIVATE_IDENTIFIERS`.
3. Compare local `esp_lvgl_port` and codec changes and host-test support with their
   upstream versions. `hal_audio` expects `espressif__esp_codec_dev`; check that this
   build target resolves correctly rather than substituting a same-named package.
4. Rebuild affected examples and run [tests](testing.md). If distributing packages,
   also build the clean consumer in [packaging](registry-publishing.md).

中文步骤：先核对公开头文件、构建声明及锁定版本；保留触控、按键、旋钮、灯带、界面和音频
的本地适配；核实音频所需构建目标；最后重新构建和测试。同名或更新版本不代表可以直接替换。

Expected result: the selected versions and local fixes remain traceable, and the
actual application builds. A successful download or package operation alone is insufficient.
预期：依赖版本与本地修改可追溯，实际应用重新构建通过；下载成功或打包成功不代替构建。
