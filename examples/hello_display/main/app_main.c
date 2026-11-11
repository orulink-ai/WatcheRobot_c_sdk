#include "esp_log.h"
#include "watcher_hw_display.h"

void app_main(void) {
    esp_err_t err = watcher_hw_display_init();
    if (err == ESP_OK) {
        if (watcher_hw_display_lock(1000)) {
            lv_obj_t *label = lv_label_create(lv_scr_act());
            if (label != NULL) {
                lv_label_set_text(label, "Hello, WatcheRobot!");
                lv_obj_center(label);
            } else {
                err = ESP_ERR_NO_MEM;
            }
            watcher_hw_display_unlock();
        } else {
            err = ESP_ERR_TIMEOUT;
        }
    }
    if (err != ESP_OK) {
        esp_err_t closed = watcher_hw_display_close();
        ESP_LOGE("hello", "Display failed: %s; cleanup: %s", esp_err_to_name(err), esp_err_to_name(closed));
        /* No retry or second owner is started after failed cleanup. */
        return;
    }
    ESP_LOGI("hello", "Text displayed; LVGL keeps running after app_main returns");
}
