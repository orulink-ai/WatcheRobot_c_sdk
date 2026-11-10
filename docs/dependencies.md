# Dependencies and configuration / 依赖与配置

This describes checked-in CMake/manifests/defaults, not a claim that every dependency closure has been
built or packaged independently. Source builds require the complete pinned checkout and network access
for declared Component Manager downloads. Do not replace local libraries merely because Registry has a
newer component with the same name.

## Supported configuration, not a broad compatibility promise

| Item | Checked-in contract |
| --- | --- |
| Target | ESP32-S3; `examples/sdk.cmake` defaults target and rejects IDF other than 6.0.2 |
| ESP-IDF | Exactly 6.0.2 |
| LVGL | 8.4.0 for head/display applications; host view suite also checks real 8.4.0 |
| Flash | All four example defaults select 16 MB and their custom `partitions.csv`; not a measured minimum |
| PSRAM | head/robot/hardware_check enable octal PSRAM at 80 MHz; body defaults do not enable it |
| Camera | `CONFIG_WATCHER_CAMERA_BACKEND_PTL=y`, matching external Himax PTL firmware |
| Display | RGB565 (`CONFIG_LV_COLOR_DEPTH_16`, `CONFIG_LV_COLOR_16_SWAP`) and selected fonts in head defaults |

## Direct API-layer CMake dependencies

| API | Public REQUIRES | Private dependencies |
| --- | --- | --- |
| core | None declared (uses IDF `esp_err.h`) | None declared |
| body | core, mcu_runtime, mcu_motion_service, mcu_led_service, mcu_sensor_service | freertos, esp_timer, motion_arbiter |
| camera | core, hal_camera | None declared |
| audio | core, hal_audio | freertos |
| display | core, sensecap-watcher, esp_lvgl_port, lvgl | None declared |

Names abbreviated as core/body/etc. above denote the `watcher_hw_*` components. See their actual
[CMake files](../components/sdk) before changing visibility: public headers expose service/LVGL/touch types.

## Dependency classes and transitive edges

- **IDF built-ins:** FreeRTOS, driver buses, timers, memory/PSRAM, LCD, filesystems and mbedTLS, selected by
  existing CMake dependencies. These are not separately vendored Registry packages.
- **First-party local layers:** `services/`, `protocols/mcu_link/`, `hal/`, PTL transport/protocol/media,
  JPEG integrity and SDK wrappers. The body wrapper owns the link; `mcu_runtime` supplies stateless
  baseline/dispatch helpers to its polling owner. `hal_camera` selects PTL at configuration.
- **Checked-in board/vendor libraries:** `sensecap-watcher`, `esp_lvgl_port`, `esp_codec_dev`,
  `esp_io_expander_pca95xx_16bit`, `sscma_client`, `media_lib_sal`; retain their own attribution/license files.
  Their README feature lists describe upstream libraries, not extra SDK-shipped applications.
- **Pinned managed dependencies:** head's `main/idf_component.yml` specifies `esp_jpeg` 1.3.1, LVGL 8.4.0,
  cJSON 1.7.19, `esp_audio_codec` 2.4.1, `esp_lcd_touch` 1.1.1 and `cmake_utilities` 0.5.3.
  Other component manifests add board/driver requirements; inspect all manifests and generated resolution,
  rather than assuming this short list is the complete closure.
- **External paired firmware:** compatible STM32 motion/LED/touch firmware and Himax PTL firmware are
  hardware prerequisites, not C SDK source dependencies and not supplied as replacement images here.

## Local adaptations that must not be silently dropped

`sensecap-watcher/patches.cmake` invokes its checked-in SPD2010 IDF6 touch fix during configuration.
`examples/sdk.cmake` includes IDF6 link adjustments for button/knob/led_strip and enables
`MBEDTLS_DECLARE_PRIVATE_IDENTIFIERS`. Local `esp_lvgl_port`/codec changes and their host test support
must be compared with their upstream baseline before replacement; a matching name is not equivalence.
`hal_audio` requires the `espressif__esp_codec_dev` target name; verify how that name resolves in each
consumer/package instead of assuming the checked-in directory alone closes the dependency graph.
This documentation does not assert Registry-package closure or a successful consumer build.

中文：固定版本不等于已验证所有环境；16 MB/八线 PSRAM 是示例实际配置，不宣称最小容量。
保留本地触控、LVGL、codec 与 IDF6 适配，不能同名替换或升级后沿用旧验收。
完整构建与打包状态见 [testing](testing.md) 和 [publishing](registry-publishing.md)。
