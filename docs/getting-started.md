English | [简体中文](getting-started_zh.md)

# Run your first C application

Use [hello_display](../examples/hello_display/README.md) to show `Hello, WatcheRobot!`, change the text and rebuild. It starts no camera, recording or body movement. Commands run from the **repository root**; C runs on the ESP32-S3.

## 1. Prepare

Use a WatcheRobot head, USB data cable, stable power, Git and **ESP-IDF 6.0.2** with ESP32-S3 tools. Follow [Espressif's installation guide](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/get-started/index.html). Open the activated IDF terminal on Windows or activate the installation's `export.sh` on macOS/Linux. See [hardware and firmware requirements](hardware-compatibility.md).

## 2. Get the complete source

```sh
git clone https://github.com/orulink-ai/WatcheRobot_c_sdk.git
cd WatcheRobot_c_sdk
idf.py --version
```

Expect `ESP-IDF v6.0.2`. Do not copy just the example outside the checkout; it depends on `examples/sdk.cmake` and component relative paths.

## 3. Build

```sh
idf.py -C examples/hello_display build
```

The first build downloads dependencies. Outputs include `examples/hello_display/build/watcher_hello_display.bin`, a bootloader, partition table and `flash_args`. The application binary is **not** a complete image for address 0x0. Defaults select ESP32-S3, 16 MB flash configuration, 80 MHz octal PSRAM and LVGL 8.4.0. The project includes its board configuration and dependency files.

## 4. Connect and flash

Close competing serial tools, attach only the intended device, then run:

```sh
python -m serial.tools.list_ports -v
```

Choose **CH342 SERIAL-B (ESP32)**, not SERIAL-A (Himax); do not infer roles from COM numbers. Replace `PORT` with your actual port, such as `COM49` or a listed Unix device path.

Flashing writes the example's bootloader, partition table and application. It replaces the installed application and may overwrite configuration; back up data you need first. See [backup and recovery](hardware-compatibility.md#备份与分区检查).

```sh
idf.py -C examples/hello_display -p PORT -b 460800 flash monitor
```

Let IDF use the generated flash addresses. To return to official firmware, follow the [complete recovery procedure](https://wiki.orulink.ai/docs/flashing#full).

## 5. Observe and modify

Expect **Hello, WatcheRobot!** and the log `Text displayed; LVGL keeps running after app_main returns`. LVGL continues after `app_main()` returns. **Ctrl+]** closes the monitor, not the device application.

Change the string in [`main/app_main.c`](../examples/hello_display/main/app_main.c) to `My first robot app`, repeat build and flash monitor. The screen should show the new text.

| File | Responsibility |
| --- | --- |
| `main/app_main.c` | Entry and feature calls |
| `main/CMakeLists.txt` | Sources and direct dependencies |
| `main/idf_component.yml`, `dependencies.lock` | Dependency declarations and resolved versions |
| `CMakeLists.txt`, `../sdk.cmake` | Hardware selection and IDF setup; retain relative paths |
| `sdkconfig.defaults`, `partitions.csv` | Board configuration/layout, not universal defaults |

## 6. Add a feature

| Task | Guide | Runnable example |
| --- | --- | --- |
| Screen, buttons, touch | [Display](api/display.md) | [hello_display](../examples/hello_display/README.md), [head](../examples/head/README.md) |
| Photos and JPEG stream | [Camera](api/camera.md) | [head](../examples/head/README.md) |
| PCM recording/playback | [Audio](api/audio.md) | [head](../examples/head/README.md) |
| Body touch, lights, motion | [Body](api/body.md) | [body](../examples/body/README.md), [hardware_check](../examples/hardware_check/README.md) |
| Model catalog and faces | [Advanced PTL vision](api/vision.md) | [face_detection](../examples/face_detection/README.md) |

See the [feature/code/documentation map](features.md). Keep one lifecycle owner per resource, check initialization errors, and do not initialize hardware alongside an existing demo using it.

## Troubleshooting

- Missing/wrong `idf.py`: activate 6.0.2 rather than bypassing version checks.
- Download failure: fix network access; retain manifests/locks rather than blindly upgrading drivers.
- Serial failure: close competing tools and check SERIAL-B, cable and driver; do not erase flash as a generic workaround.
- Blank screen: preserve `Display failed` logs; check power, PSRAM and firmware before starting another instance.
- `Finished (60 seconds)` means the face example's timer ended. Press RESET to run again; see the [example](../examples/face_detection/README.md).
