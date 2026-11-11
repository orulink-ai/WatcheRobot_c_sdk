English | [简体中文](README_zh.md)

# Detect faces with the installed model

This example reads the Himax model catalog, selects a verified face model, and displays **face count and result sequence for 60 seconds**. It runs on the head's ESP32-S3; inference runs on Himax. No network service or body movement is required.

The screen shows text, not a camera image or bounding boxes. Face detection reports presence; this example does not recognize identities, enroll people or track an individual.

## 1. Prepare the device and build

Start with the [first-run tutorial](../../docs/getting-started.md) for source checkout, ESP-IDF setup and port identification. Use the complete repository: this project depends on [shared example configuration](../sdk.cmake), not just its own directory.

- Use ESP-IDF **6.0.2** with the ESP32-S3 toolchain and the project's pinned configuration/dependencies.
- Connect the powered WatcheRobot head with a USB data cable. The body is unnecessary.
- Himax must already have compatible PTL/WV1 firmware and the expected face model. If missing, follow [model provisioning](../../docs/model-deployment.md). This example neither installs models nor updates Himax.
- See [compatible hardware and firmware](../../docs/hardware-compatibility.md).

Run from the repository root in an activated IDF terminal:

```sh
idf.py --version
idf.py -C examples/face_detection build
```

The application binary is `examples/face_detection/build/watcher_face_detection.bin`. It is not a complete image for address 0x0. Keep [sdkconfig.defaults](sdkconfig.defaults), [partitions.csv](partitions.csv), [dependency manifest](main/idf_component.yml) and [lock file](dependencies.lock) together.

## 2. Flash and watch the log

Replace `PORT` with the detected **CH342 SERIAL-B (ESP32)** port, not SERIAL-A (Himax). Close other serial tools.

Flashing replaces the application and partition layout and may overwrite configuration. Back up data you need; see [backup and recovery](../../docs/hardware-compatibility.md#备份与分区检查).

```sh
idf.py -C examples/face_detection -p PORT -b 460800 flash monitor
```

If the matching example is already installed, open logs without flashing:

```sh
idf.py -C examples/face_detection -p PORT monitor
```

Press **Ctrl+]** to exit the monitor; this does not stop inference. RESET restarts the example. There are no touch controls or serial test commands in this program.

## 3. Check the visible result

| Screen | Expected behavior |
| --- | --- |
| `Reading model catalog...` | Read four slots; logs show model ID, name, verified and face flags. This can take several seconds. |
| `Face detection / Waiting for first result...` | Start inference and wait for exposure warmup. |
| `Faces: … / Frame: …` | Display the latest box count and result sequence. Sequence numbers may skip; they are not FPS. |
| `Finished (60 seconds) / Reset to run again` | Normal timed completion, measured from successful start, including first-result waiting. |

Within that minute, keep faces out of view for about 10 seconds, face the camera in normal light at roughly 30–80 cm for 10 seconds, then leave for 10 seconds. Expect **Faces 0→1→0**, with Frame continuing to advance. The suggested distance is a basic test setup, not a rated detection range. Move your face slowly while visible to check continued detection.

The serial log prints `Model … verified=… face=…`, `Frame=… faces=…` and finally `Run result: ESP_OK` on a normal run.

## 4. Find the calls and make a first change

The complete, buildable implementation is [main/app_main.c](main/app_main.c). Its entry is `app_main()`; [main/CMakeLists.txt](main/CMakeLists.txt) declares its direct dependencies.

| Code location | Role |
| --- | --- |
| `app_main()`: catalog loop | Require both `verified` and `contains_face_class`, then select the installed model. |
| `hal_camera_start_inference(receive_result, queue)` | Start metadata-only inference; no preview JPEG is requested. |
| `receive_result()` | Copy metadata into a one-element queue and discard borrowed preview pointers. New results may replace old display updates. |
| `xQueueReceive()` block and `show()` | Update the label from the main task under the display lock. |
| Diagnostics and cleanup blocks | Check query return and `diag.status`; stop the matching owner, deinitialize, and delete the queue only after cleanup succeeds. |

For a first change, replace the result label's `Face detection\nFaces:` prefix inside `snprintf()` with `My face demo\nFaces:`. Rebuild and flash using the commands above, then confirm the new title and repeat 0→1→0.

To extend the duration, change `60000000` in the `end` deadline to `120000000` (microseconds), and update the final `Finished (60 seconds)` text to match. For application behavior, consume `frame.box_count` in the main task, not in the inference callback. Rapidly repeated detections are separate results, not new people.

See the [vision API guide](../../docs/api/vision.md) for model selection, result fields, ownership and optional previews. Replacing a slot number alone does not establish compatibility with another model.

## Troubleshooting

| Symptom | Check / next action |
| --- | --- |
| Display initialization error or blank screen | Keep the startup log; verify the head configuration and PSRAM. First run [hello_display](../hello_display/README.md). |
| Catalog cannot be read | Check head power, paired Himax firmware and transport errors in the log. Do not open another camera controller concurrently. |
| `Unverified model`, then `ESP_ERR_NOT_SUPPORTED` | No verified face model was selected. Install the matching model using the [model provisioning guide](../../docs/model-deployment.md). |
| `Waiting for first result...` | A short startup wait is expected. If persistent, preserve the log and consult [startup diagnostics](../../docs/api/vision.md#首帧等待统计与错误). |
| Frames advance but Faces stays 0 | Check lighting, camera direction and that a face is fully visible. Capture a current photo using the separate [head example](../head/README.md) if needed; stop this program before changing camera applications. |
| `Detection failed` | Inspect the preceding error and `Run result`; the example exits on a reported runtime error. |
| `Cleanup failed` | Shutdown was not confirmed after three attempts. Queue memory is intentionally retained; preserve logs and reset before handing the camera to another application. |
| `Finished (60 seconds)` | Expected completion. RESET to repeat or change the duration as above. |
