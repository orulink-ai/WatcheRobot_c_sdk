#include <inttypes.h>
#include <stdio.h>
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "hal_camera.h"
#include "watcher_hw_display.h"

static const char *TAG = "face_example";
static lv_obj_t *label;

/* The inference task only copies data. LVGL and lifecycle calls stay in app_main. */
static void receive_result(const hal_camera_inference_frame_t *frame, void *ctx) {
    hal_camera_inference_frame_t copy = *frame;
    copy.preview_image_base64 = NULL;
    copy.preview_image_size = 0;
    xQueueOverwrite((QueueHandle_t)ctx, &copy);
}

static void show(const char *text) {
    if (label != NULL && watcher_hw_display_lock(1000)) {
        lv_label_set_text(label, text);
        watcher_hw_display_unlock();
    }
}

void app_main(void) {
    esp_err_t err = watcher_hw_display_init();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Display init: %s; cleanup: %s", esp_err_to_name(err),
                 esp_err_to_name(watcher_hw_display_close()));
        return;
    }
    if (watcher_hw_display_lock(1000)) {
        label = lv_label_create(lv_scr_act());
        if (label != NULL) {
            lv_obj_set_width(label, 280);
            lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, 0);
            lv_obj_center(label);
            lv_label_set_text(label, "Reading model catalog...");
        }
        watcher_hw_display_unlock();
    }
    if (label == NULL) {
        ESP_LOGE(TAG, "Cannot create UI; cleanup: %s", esp_err_to_name(watcher_hw_display_close()));
        return;
    }
    QueueHandle_t queue = xQueueCreate(1, sizeof(hal_camera_inference_frame_t));
    if (queue == NULL) {
        show("Queue allocation failed");
        return;
    }
    hal_camera_model_info_t models[4];
    size_t count = 0;
    err = hal_camera_list_models(models, 4, &count);
    int face_model = 0;
    if (err == ESP_OK) {
        for (size_t i = 0; i < count; ++i) {
            ESP_LOGI(TAG, "Model %d: %s verified=%d face=%d", models[i].model_id, models[i].name,
                     models[i].verified, models[i].contains_face_class);
            if (models[i].verified && models[i].contains_face_class)
                face_model = models[i].model_id;
        }
        err = face_model ? hal_camera_set_active_model(face_model) : ESP_ERR_NOT_SUPPORTED;
    }
    if (err == ESP_OK)
        err = hal_camera_start_inference(receive_result, queue);
    if (err == ESP_OK) {
        show("Face detection\nWaiting for first result...");
        const int64_t end = esp_timer_get_time() + 60000000;
        while (esp_timer_get_time() < end) {
            hal_camera_inference_frame_t frame;
            if (xQueueReceive(queue, &frame, pdMS_TO_TICKS(200)) == pdTRUE) {
                char text[96];
                snprintf(text, sizeof(text), "Face detection\nFaces: %u\nFrame: %" PRIu32,
                         (unsigned)frame.box_count, frame.sequence);
                show(text);
                ESP_LOGI(TAG, "Frame=%" PRIu32 " faces=%u", frame.sequence, (unsigned)frame.box_count);
            }
            hal_camera_diagnostics_t diag;
            err = hal_camera_get_diagnostics(&diag);
            if (err == ESP_OK)
                err = diag.status;
            if (err != ESP_OK)
                break;
        }
    }
    ESP_LOGI(TAG, "Run result: %s", esp_err_to_name(err));
    esp_err_t closed = ESP_FAIL;
    for (unsigned attempt = 0; attempt < 3; ++attempt) {
        closed = hal_camera_stop_inference_owned(receive_result, queue);
        if (closed == ESP_OK)
            closed = hal_camera_deinit();
        if (closed == ESP_OK)
            break;
        ESP_LOGE(TAG, "Cleanup: %s", esp_err_to_name(closed));
        vTaskDelay(pdMS_TO_TICKS(100));
    }
    if (closed == ESP_OK) {
        vQueueDelete(queue);
        show(err == ESP_OK ? "Finished (60 seconds)\nReset to run again" : "Detection failed\nSee serial log");
    } else {
        /* Keep callback storage alive if shutdown could not be confirmed. */
        show("Cleanup failed\nSee serial log");
    }
}
