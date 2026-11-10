English | [简体中文](README_zh.md)

# WatcheRobot C SDK

Build your own ESP32-S3 robot application with `watcher_hw_*` for body motion, lights,
camera, audio and display. No Python SDK or official application is required.
**Development preview: complete paired-device and restoration acceptance remains pending.**

## Quick start

Install Git and [ESP-IDF 6.0.2 for ESP32-S3](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/get-started/index.html),
then open a terminal with the IDF environment activated; `idf.py --version` must report 6.0.2.
For first-time setup or environment errors, start with the [setup guide](docs/getting-started.md).

Run in the directory where you want to keep the project:

```sh
git clone https://github.com/orulink-ai/WatcheRobot_c_sdk.git
cd WatcheRobot_c_sdk
idf.py -C examples/robot build
```

Expected output: `examples/robot/build/watcher_hw_robot.bin` and the associated flash files.
Component downloads require network access. This only builds; it does not write to a device.
For errors, see [troubleshooting](docs/getting-started.md#troubleshooting-and-acceptance-boundary).
Next, edit [`examples/robot/main/app_main.c`](examples/robot/main/app_main.c) and run the same build command.
Record `git rev-parse HEAD` when reproducing a result or reporting an issue; the setup guide explains version pinning.

**Before flashing:** verify the ESP32 port and paired STM32/Himax firmware, and prepare a
complete official recovery bundle. A full custom flash overwrites official configuration;
back up required data and do not flash without verified preparation. Servos have no physical
position feedback, reference moves can be large, and ACK/DONE does not establish physical stopping.
Clear the entire travel, keep manual power disconnection available, and follow the
[safe flashing and recovery guide](docs/getting-started.md).

## Choose an example

Each directory is an independent ESP-IDF project. Replace `robot` in the build command with its project name.

| Goal | Project |
| --- | --- |
| Body motion, lights and touch | [`body`](examples/body) |
| Camera, audio and display | [`head`](examples/head) |
| Build a combined application | [`robot`](examples/robot) |
| Check real hardware one item at a time | [`hardware_check`](examples/hardware_check) · [operator guide](docs/hardware-check.md) |

`hardware_check` requires human observations; it is not an automatically passing unit test.

## Developer documentation

- [Setup, flashing and recovery](docs/getting-started.md) · [open-loop motion and safety](docs/servo-open-loop.md)
- [Public API headers](components/sdk) · [old API migration](MIGRATION.md)
- [Branch/PR workflow and provenance](docs/repository-workflow.md)
- Building a computer-side application on existing firmware? Use the separate [Python SDK](https://github.com/orulink-ai/WatcheRobot_python_sdk).

## License

First-party code is [Apache-2.0](LICENSE). Third-party components and assets retain their own licenses.
