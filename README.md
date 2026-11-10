English | [简体中文](README_zh.md)

# WatcheRobot C SDK

Build your own ESP32-S3 robot application with `watcher_hw_*` for body motion, lights, camera,
audio and display. No Python SDK or official application source is required.
**Development preview: complete paired-device and restoration acceptance remains pending.**

## Quick start from source

Install Git and [ESP-IDF 6.0.2 for ESP32-S3](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/get-started/index.html),
then activate its environment in this terminal; check `idf.py --version`.
For first-time setup or errors, use the [setup guide](docs/getting-started.md).
Run in the directory where you want to keep the project:

```sh
git clone https://github.com/orulink-ai/WatcheRobot_c_sdk.git
cd WatcheRobot_c_sdk
idf.py -C examples/robot build
```

Expected output: `examples/robot/build/watcher_hw_robot.bin` and associated flash files.
Component downloads need network access. This builds only; it does not write to a device.
Next, edit [`examples/robot/main/app_main.c`](examples/robot/main/app_main.c) and repeat the build.
Record `git rev-parse HEAD` and pin a reviewed public revision as explained in the setup guide.
These are source workflow instructions, not a claim that this documentation task built the firmware;
see [testing and evidence](docs/testing.md).

**Before flashing:** verify the ESP32 port, paired STM32/Himax firmware and a complete official recovery
bundle. A full custom flash overwrites official configuration; back up required data and stop if the
pair or recovery bundle is unverified. Servos have **no physical position feedback**, reference moves
can be large, and ACK/DONE does not establish measured position or physical stopping. Clear the full
travel, keep manual power disconnection available and follow the [safe recovery guide](docs/getting-started.md).

## Compatibility and actual configuration

| Item | Checked-in contract |
| --- | --- |
| Target | ESP32-S3 |
| ESP-IDF | Exactly 6.0.2; other versions are rejected by the build entry |
| LVGL | 8.4.0 in head/display examples; no LVGL 9 compatibility claim |
| Flash | All four examples select 16 MB and custom partitions; not a measured minimum |
| PSRAM | head/robot/hardware_check enable octal PSRAM at 80 MHz; body defaults do not enable it |
| Paired firmware | Body needs compatible STM32; camera needs matching Himax PTL, verified separately |

## Capabilities

| Module | Provides | Usage |
| --- | --- | --- |
| body | Motion commands, lights, touch/link events; no physical position feedback | [Body API](docs/api/body.md) |
| camera | Paired PTL JPEG capture/stream; no model or network policy | [Camera API](docs/api/camera.md) |
| audio | 16/24 kHz signed 16-bit mono PCM record/playback | [Audio API](docs/api/audio.md) |
| display | LVGL display, borrowed panel/touch handles and locking | [Display API](docs/api/display.md) |
| core | Lifecycle status types, events and caller-owned bounded FIFO | [Core API](docs/api/core.md) |

## Choose an example

Each is an independent ESP-IDF project. Replace `robot` in the build command with its project name.

| Goal | Project |
| --- | --- |
| Body lights and touch events | [body](examples/body/README.md) |
| Camera, audio and display | [head](examples/head/README.md) |
| Combine body and head | [robot](examples/robot/README.md) |
| Check hardware one item at a time | [hardware_check](examples/hardware_check/README.md) · [operator guide](docs/hardware-check.md) |

`hardware_check` requires human observation; untested does not mean passed, and it is not an automatic
unit test. [common](examples/common/README.md) contains example-internal code, not a fifth application.

## Developer documentation

- [Documentation index](docs/README.md) · [Architecture](docs/architecture.md) · [Dependencies](docs/dependencies.md)
- [Open-loop motion safety](docs/servo-open-loop.md) · [Old API migration](docs/migration.md)
- [Contributing](docs/contributing.md) · [Testing/reports](docs/testing.md) · [Provenance](docs/provenance.md)
- [Component packaging status](docs/registry-publishing.md): no verified published Registry installation yet; use source builds.
- Building a computer-side application on existing firmware? Use the separate [Python SDK](https://github.com/orulink-ai/WatcheRobot_python_sdk).

## License

First-party code is [Apache-2.0](LICENSE). Third-party components and assets retain their own licenses and attribution.
