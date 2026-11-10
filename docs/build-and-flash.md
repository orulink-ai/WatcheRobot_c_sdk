English | [简体中文](build-and-flash_zh.md)

# Build, flash and restore

Build an application for the robot's ESP32-S3, then try pictures, recording/playback and
touch-controlled lights. No official application source, Python SDK, server, SD card or model is
needed. For computer-side development on existing firmware, use the separate [Python SDK](https://github.com/orulink-ai/WatcheRobot_python_sdk).
**This is a development preview; full paired-device and official-recovery acceptance is pending.**

## 1. Install the tools and build

Install Git and [ESP-IDF 6.0.2 with ESP32-S3 tools](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/get-started/index.html).
Activate IDF in each new terminal: on Linux/macOS, source `export.sh` from your actual IDF installation;
on Windows, use the ESP-IDF PowerShell terminal. `idf.py --version` must report 6.0.2; the build rejects other versions.

```sh
git clone https://github.com/orulink-ai/WatcheRobot_c_sdk.git
cd WatcheRobot_c_sdk
idf.py --version
idf.py -C examples/robot build
```

All following commands run from **this repository root in the activated IDF terminal**.
Dependencies download over the network. The build should produce
`examples/robot/build/watcher_hw_robot.bin`, a bootloader, a partition table and flash arguments.
It does not write to a device or prove hardware behavior. If the build fails, fix the reported error
before continuing. When reporting a problem, include `git rev-parse HEAD`, `idf.py --version` and the error log.

## 2. Choose what to try

| Goal | Project | File to edit |
| --- | --- | --- |
| Touch-controlled body lights | `body` | `examples/body/main/app_main.c` |
| Pictures, recording/playback and screen controls | `head` | `examples/head/main/app_main.c` |
| Combine both | `robot` | `examples/robot/main/app_main.c` |
| Guided hardware checks | `hardware_check` | `examples/hardware_check/main/app_main.c` |

Replace `robot` in the commands with your chosen project. All examples select ESP32-S3, 16 MB flash and
custom partitions. head/robot/hardware_check enable 80 MHz octal PSRAM and LVGL 8.4.0; body defaults do
not enable PSRAM. Keep each project's configuration, partitions and dependency manifest together.
See [example instructions](../examples/README.md) and [supported dependencies](dependencies.md).

Edit `app_main.c` and rebuild to change application behavior. The body and robot examples respond to
touch with lights and a stop request on release; they do not automatically start servo movement.

## 3. Safety checklist — before any flash or movement

- **Compatible firmware:** body control needs compatible STM32 firmware supporting motion, lights and
  touch; camera use needs matching Himax **PTL** firmware. Record board/firmware versions and image
  hashes. Product Releases, filenames, a successful handshake or a successful build do not establish
  compatibility. If the pair is unverified, stop and request a compatibility record from maintainers.
- **Backup and recovery:** prepare a verified, complete official restore bundle and back up required
  settings/data. First full custom flashing overwrites the official `agentcfg` region
  **0x12000–0x20000**. Returning to official firmware needs a **full restore**, not an app-only flash.
  A backup alone does not restore the partition layout. Missing recovery assets means stop.
- **Correct port:** the ESP32 connector is **SERIAL-B**; verify the actual port in Device Manager or
  `/dev/serial/by-id/`. Do not use the STM32/Himax port. Close other serial monitors.
- **Movement:** the application **cannot read the angle a servo actually reaches**. Even a reference move to X90/Y120 can
  travel a large distance from an unknown starting position. Clear the whole travel and keep manual
  power disconnection available. ACK/DONE and software STOP do not prove actual position or physical
  stopping. A disconnected ESP32 cannot guarantee delivery of a stop; STM32 safety and an operator
  power cut remain necessary. Read [movement safety](servo-open-loop.md) before motion checks.

Use the [official flashing guide](https://wiki.orulink.ai/en/docs/flashing) for initial preparation or
restoration with a verified complete bundle, not for everyday custom application updates. This SDK
supplies no unverified STM32/Himax replacement image.

## 4. Flash and observe

Only after completing the checklist, replace `<PORT>` below with the **verified ESP32 port** on your
machine (for example `COM7` or `/dev/ttyACM0`, if actually identified there):

```sh
idf.py -C examples/robot -p <PORT> flash
idf.py -C examples/robot -p <PORT> monitor
```

`flash` writes the custom ESP32 bootloader, partition table and application; it does not flash
STM32/Himax. Do **not** run `erase-flash`, guess offsets, or write an application-only `.bin` at `0x0`.
Expected: esptool verifies writes, then the robot example shows photo/audio controls and logs body
initialization and touch events. Try Photo, then Record and Play; check the picture and sound yourself.
Touching the body requests green lights; release requests stop. Disabled controls are not a pass.
Exit the monitor with **Ctrl+]**.

For `hardware_check`, the screen should show **Hardware check** and the log
`Hardware check v2 | curved zones`. Follow the [26-item operator guide](hardware-check.md).
Results are RAM-only and reset on reboot; save observations externally. Untested items are not passed.

For later app-only updates, use `idf.py -C examples/robot -p <PORT> app-flash` **only if the connected
device already has the same custom partition layout**. Matching local files alone do not prove this.
After official firmware or an unknown device layout, use full custom `flash` after the checklist.

Optional wrappers provide the same build/flash/monitor actions:

```sh
bash examples/hardware-sdk.sh robot build
```

```powershell
./examples/hardware-sdk.ps1 robot build
```

They accept body/head/robot/hardware_check and build/flash/monitor; flash/monitor require the explicit
port as the third argument. They do not scan ports, flash paired chips or erase the device.

## 5. Restore official firmware

Stop the custom application and close serial monitors. Select a verified complete **official** bundle
and follow the [full restore procedure](https://wiki.orulink.ai/en/docs/flashing#full), using that bundle's
exact ports and images. Restoration replaces the custom ESP32 application and may replace storage and
paired firmware. Verify official startup and pairing afterward. To resume SDK work, build and flash the
custom project again. If recovery assets or their source are unknown, stop rather than guessing offsets.

## Troubleshooting

- Wrong IDF version: activate 6.0.2 in this terminal; do not bypass the check.
- Missing dependency: check the full checkout, network and project manifest; do not add official application sources.
- Body not ready or event loss reported: stop operating the controls and check power, cables and
  compatible firmware. Do not keep touching to unlock controls or automatically retry old actions.
  Reconnecting or clearing queued events does not clear this fault. If you write recovery code,
  cancel pending actions and follow the complete [body API recovery procedure](api/body.md);
  movement afterward requires a **new user action**.
- No picture: verify the matching PTL camera firmware and keep timeout/error logs; no image is not a pass.
- No sound: try Test speaker voice/tone. Default output is 90, capped at 95; playback progress does not
  prove audibility. The simple head demo has no automatic retry or dynamic shutdown; do not create a
  second task controlling the same audio/camera devices to recover.

## When you extend the application

Keep audio operations in one task; do not call blocking audio functions inside hardware callbacks,
interrupts or while holding the display lock. Copy camera callback images before retaining them and
lock LVGL access. See the [API guides](README.md) for exact interfaces and ownership rules.
For a separate ESP-IDF project, follow the existing example CMake/configuration and
[dependency guide](dependencies.md); copying headers alone is insufficient. Keep a known SDK revision
for reproducible builds. [Migration](migration.md) covers older `watche_hw_*` applications.

## Optional: prebuilt test firmware and evidence

The external [hardware-check preview Release](https://github.com/orulink-ai/WatcheRobot-public/releases/tag/hardware-check-preview-20261030)
is not an official stable product release and is not required for source builds. Follow its exact
asset, source/hash and installation instructions; its binaries need not match this checkout.
Download packages require Python 3.10+ and their documented esptool dependency. Use the complete flash
set at its documented offsets, never an app-only binary at `0x0`. Missing assets mean contact maintainers,
not substitute a similarly named file. The safety checklist still applies.

Software tests do not certify motion limits, stop timing, touch edges, image/sound quality, repeated
shutdown or long-duration combined operation. See [tests and evidence](testing.md),
[historical validation](../history/VALIDATION.md) and [source provenance](provenance.md).
Documentation is not a new build, flash or hardware acceptance result.
