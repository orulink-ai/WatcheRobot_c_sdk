English | [简体中文](getting-started_zh.md)

# How to use the WatcheRobot C SDK

| [Display & touch](#display--touch) | [Audio](#audio) | [Camera](#camera) | [Lights & body touch](#lights--body-touch) | [Body movement](#body-movement) |
| --- | --- | --- | --- | --- |

## Overview

Find a feature, initialize its hardware, then perform the operation. No knowledge of internal components or communication protocols is needed first.
To run the code, see [examples](../examples/README.md). Install the environment using the [official ESP-IDF guide](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/get-started/index.html).

The C blocks below are application functions, not terminal commands. Use the [combined example](../examples/robot/README.md) for project configuration and call the functions from an application task.
Do not initialize the same hardware alongside the existing demo. Sections are independent usage patterns, not a program to run in order.

## General usage

- Use **ESP-IDF 6.0.2 / ESP32-S3** and **LVGL 8.4.0**.
- `init()` opens hardware and `close()` closes it. Check every result; `ESP_OK` means that call succeeded.
- A successful status query does not mean the device is ready. Check `state`; body initialization can still be connecting.
- Declarations and parameters are defined in the [public headers](../components/sdk); these interfaces do not require direct pin or communication-bus control.

## Display & touch

### Display text

Initialization prepares the screen, touch and LVGL. Lock before changing the interface, then unlock afterward to prevent concurrent changes.

```c
#include "watcher_hw_display.h"
#include "esp_log.h"

esp_err_t show_message(void) {
    esp_err_t err = watcher_hw_display_init();
    if (err != ESP_OK) goto cleanup;
    if (!watcher_hw_display_lock(1000)) {
        err = ESP_ERR_TIMEOUT;
        goto cleanup;
    }
    lv_obj_t *label = lv_label_create(lv_scr_act());
    if (label) {
        lv_label_set_text(label, "Hello, WatcheRobot!");
        lv_obj_center(label);
    }
    watcher_hw_display_unlock();
    if (label) return ESP_OK;
    err = ESP_ERR_NO_MEM;

cleanup: {
    esp_err_t closed = watcher_hw_display_close();
    if (closed != ESP_OK)
        ESP_LOGE("guide", "Display cleanup failed: %s", esp_err_to_name(closed));
    return err;
}
}
```

The text should be visible after success; the display stays open. Use LVGL buttons and events for screen touch.
Stop other screen users before `watcher_hw_display_close()` and **do not hold the lock while closing**.
On failure, the example releases any acquired lock before attempting cleanup and preserves the original error. If cleanup fails, the application task responsible for the hardware lifecycle must continue cleanup; do not reinitialize or hand the display to another task until cleanup succeeds.
See [display details](api/display.md#english-draw-text-buttons-and-screens).

## Audio

### Record a short sound and play it back

PCM means uncompressed sound samples; this interface does not open MP3 or WAV files directly.
Record about 0.1 seconds at 16 kHz, 16-bit mono, then replay it. Run all sound operations in the same task.

```c
#include "watcher_hw_audio.h"
#include "esp_log.h"

esp_err_t record_and_play(void) {
    static int16_t pcm[1600];
    esp_err_t err = watcher_hw_audio_init(16000, 30);
    if (err == ESP_OK) err = watcher_hw_audio_read(pcm, sizeof(pcm));
    if (err == ESP_OK) err = watcher_hw_audio_write(pcm, sizeof(pcm));
    if (err == ESP_OK) err = watcher_hw_audio_drain(1000);
    esp_err_t closed = watcher_hw_audio_close();
    if (closed != ESP_OK)
        ESP_LOGE("guide", "Audio cleanup failed: %s", esp_err_to_name(closed));
    return err != ESP_OK ? err : closed;
}
```

Start at low volume and listen. `drain()` waits for submitted samples to be sent before closing; completed progress does not prove good sound.
Playback memory must be writable; `sizeof(pcm)` counts bytes. Do not run these calls in hardware callbacks, interrupts or while holding the screen lock.
If close fails, finish cleanup before another user takes the hardware. See [audio details](api/audio.md#english-record-and-play-sound).

## Camera

### Take a photo

The camera needs matching Himax firmware. JPEG bytes are delivered to the receiving function:

```c
#include "watcher_hw_camera.h"
#include "esp_log.h"

static void receive_photo(const uint8_t *jpeg, size_t size,
                          uint32_t timestamp_ms, void *context) {
    (void)jpeg; (void)timestamp_ms; (void)context;
    ESP_LOGI("guide", "JPEG received: %u bytes", (unsigned)size);
    /* Copy jpeg[0..size) here if the application needs to keep the photo. */
}

esp_err_t take_photo(void) {
    esp_err_t err = watcher_hw_camera_init();
    if (err == ESP_OK) err = watcher_hw_camera_capture(receive_photo, NULL);
    esp_err_t closed = watcher_hw_camera_close();
    if (closed != ESP_OK)
        ESP_LOGE("guide", "Camera cleanup failed: %s", esp_err_to_name(closed));
    return err != ESP_OK ? err : closed;
}
```

On success the serial log reports the photo size. This snippet logs data; it does not save or display a photo.
Bytes are valid only until the receiver returns. Copy them first to keep them; do not stop or close the camera from the receiver.
Finish failed cleanup before starting another camera controller.

### Receive a stream

For streaming, initialize → start the stream → stop → close. After initialization, call `watcher_hw_camera_stream(fps, receive_photo, NULL)` to receive frames in the same function.
`fps` is the requested frame rate. End the stream from the application task with `watcher_hw_camera_stop()`, check success, then close.
See [frame-rate limits and recovery](api/camera.md#english-take-photos-and-receive-images).

## Lights & body touch

### Initialize and check readiness

Lights, touch and movement share one body initialization. Call `watcher_hw_body_init()` at startup, then query until `WATCHER_HW_READY` before operating. Retry later while STARTING; stop and investigate FAULT instead of retrying forever.
Call this check in your application loop; wait when not ready instead of forcing requests.

```c
#include "watcher_hw_body.h"

esp_err_t check_body_ready(void) {
    watcher_hw_status_t status;
    esp_err_t err = watcher_hw_body_status(&status);
    if (err != ESP_OK) return err;
    if (status.state == WATCHER_HW_READY) return ESP_OK;
    return status.last_error != ESP_OK ? status.last_error : ESP_ERR_INVALID_STATE;
}
```

### Set side lights to green

```c
esp_err_t set_side_light(void) {
    esp_err_t err = check_body_ready();
    if (err != ESP_OK) return err;
    mcu_led_request_t light = {
        .mode = MCU_LED_MODE_STATIC,
        .zone = MCU_LED_ZONE_SIDE,
        .primary_green = 128,
        .brightness = 64,
    };
    return watcher_hw_body_light(&light);
}
```

The side lights should turn green. Color and brightness values are 0–255. Use `MCU_LED_ZONE_BOTTOM` for the dock,
`MCU_LED_ZONE_ALL` for all lights and `MCU_LED_MODE_OFF` to turn them off. A successful request still needs visual confirmation.

### Read body touch

Read events to identify press, release or long press. Do not combine direct reads with callback dispatch.

```c
#include <string.h>
#include "esp_log.h"

esp_err_t read_body_event(void) {
    watcher_hw_event_t event;
    esp_err_t err = watcher_hw_body_next_event(&event);
    if (err != ESP_OK) return err;
    if (event.type == WATCHER_HW_EVENT_OVERFLOW) {
        ESP_LOGE("guide", "Events lost: cancel pending actions and recover before continuing");
        return ESP_ERR_INVALID_STATE;
    }
    if (event.type == WATCHER_HW_EVENT_TOUCH && event.size == sizeof(mcu_touch_state_t)) {
        mcu_touch_state_t touch;
        memcpy(&touch, event.payload, sizeof(touch));
        ESP_LOGI("guide", "Touch %u: event=%d", touch.touch_id, touch.event_code);
    }
    return ESP_OK;
}
```

`ESP_ERR_NOT_FOUND` means no new event yet. Touch logs report `event=1` for press, `2` for release and `3` for long press.
On event loss, cancel pending actions and follow the [body recovery procedure](api/body.md#english-motion-lights-and-touch):
close/init outside callbacks, resubscribe and wait for readiness. Logging an error alone is insufficient.
Do not replay old actions after recovery; require a new user operation.

## Body movement

### Submit a movement request

First initialize the body as described above and reuse its `check_body_ready()` helper.

**Read [movement precautions](api/body.md#motion-safety-english) first.** Clear the entire possible travel area and keep manual power disconnection available.
The program cannot read the angle a servo actually reaches. Even a reference move may travel far from an unknown starting point.
This function does not run automatically; call it only in response to the user's current intended action.

```c
esp_err_t request_move(int x_degrees, int y_degrees, uint32_t duration_ms) {
    esp_err_t err = check_body_ready();
    if (err != ESP_OK) return err;
    uint32_t sequence;
    return watcher_hw_body_move(x_degrees, y_degrees, duration_ms, &sequence);
}
```

See [movement parameters](api/body.md#english-motion-lights-and-touch) for angle/duration limits.
Success does not prove arrival; acknowledgement/completion reports do not prove physical stopping.
`watcher_hw_body_stop()` requests a stop but may not reach a disconnected controller; it is not an emergency-stop device.
When finished, call `watcher_hw_body_close()` and check its result. Handle failed cleanup without retrying old movements automatically.

## Complete examples and further reading

- [Touch-controlled lights](../examples/body/README.md) · [Screen, camera and audio](../examples/head/README.md) · [Combined application](../examples/robot/README.md).
- [Examples](../examples/README.md): project configuration, builds and device precautions; [official restoration](https://wiki.orulink.ai/docs/flashing#full).
- [Complete API guides](api/README.md#english-choose-a-task): parameters, tasks, error recovery and cleanup.
- [Manual hardware checks](../examples/hardware_check/README.md).

This page covers the current SDK interfaces; it does not offer dedicated SD-card, battery or USB APIs. Compilation does not replace hardware acceptance.

Organization follows the [ESP-BSP API guide](https://github.com/espressif/esp-bsp/blob/master/docu/how_to_use.md); the code uses WatcheRobot public interfaces.
