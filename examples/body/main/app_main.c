#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "watcher_hw_body.h"
#include <string.h>
static void on_body_event(const watcher_hw_event_t *received, void *context) {
    (void)context;
    watcher_hw_event_t event = *received;
    ESP_LOGI("example", "event=%d seq=%lu", event.type, (unsigned long)event.sequence);
    if (event.type == WATCHER_HW_EVENT_TOUCH && event.size == sizeof(mcu_touch_state_t)) {
        mcu_touch_state_t touch;
        memcpy(&touch, event.payload, sizeof(touch));
        ESP_LOGI("example", "touch=%u code=%d", touch.touch_id, touch.event_code);
        mcu_led_request_t light = {.mode = MCU_LED_MODE_STATIC,
                                   .zone = MCU_LED_ZONE_ALL,
                                   .primary_green = touch.active ? 128 : 0,
                                   .brightness = 64};
        ESP_LOGI("example", "light: %s", esp_err_to_name(watcher_hw_body_light(&light)));
        if (touch.event_code == MCU_TOUCH_EVENT_RELEASE) {
            ESP_LOGI("example", "stop: %s", esp_err_to_name(watcher_hw_body_stop()));
        }
    } else if (event.type == WATCHER_HW_EVENT_OVERFLOW) {
        ESP_LOGE("example", "Event loss: controls locked. Cancel actions, then close/init outside callbacks.");
    } else if (event.type == WATCHER_HW_EVENT_LINK) {
        /* A reconnect never replays an action. */
    } else if (event.type == WATCHER_HW_EVENT_MOTION && event.size == sizeof(mcu_motion_lifecycle_event_t)) {
        mcu_motion_lifecycle_event_t result;
        memcpy(&result, event.payload, sizeof(result));
        static const char *names[] = {"ACKED", "REJECTED", "DONE", "FAULT"};
        const char *name = (unsigned)result.type < 4 ? names[result.type] : "UNKNOWN";
        ESP_LOGI("motion", "%s seq=%lu result=%d reason=%u fault=%u final_x10=(%d,%d) ms=%u", name,
                 (unsigned long)result.ref_seq, result.result, result.reason, result.fault_code, result.final_x_deg_x10,
                 result.final_y_deg_x10, result.exec_ms);
    }
}
static void body_events(void) {
    uint32_t dispatched;
    (void)watcher_hw_body_dispatch_events(32, &dispatched);
    uint32_t dropped;
    if (watcher_hw_body_dropped_events(&dropped) == ESP_OK && dropped)
        ESP_LOGW("example", "dropped events: %lu", (unsigned long)dropped);
}
void app_main(void) {
    esp_err_t ret = watcher_hw_body_init();
    if (ret != ESP_OK) {
        ESP_LOGE("example", "Body init failed: %s; example not started", esp_err_to_name(ret));
        return;
    }
    ret = watcher_hw_body_subscribe(on_body_event, NULL);
    if (ret != ESP_OK) {
        esp_err_t closed = watcher_hw_body_close();
        ESP_LOGE("example", "Body subscribe failed: %s; close: %s; example not started",
                 esp_err_to_name(ret), esp_err_to_name(closed));
        return;
    }
    ESP_LOGI("example", "Body runtime started; waiting for connection and touch events");
    for (;;) {
        body_events();
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
