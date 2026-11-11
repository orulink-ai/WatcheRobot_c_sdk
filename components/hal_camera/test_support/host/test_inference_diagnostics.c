/* Exercise the actual diagnostics function with controlled coprocessor status. */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include "hal_camera.h"
#include "watcher_hx_control.h"
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #x); exit(1); } } while (0)
typedef void *SemaphoreHandle_t;
typedef void *TaskHandle_t;
#define portMAX_DELAY 0
#define pdTRUE 1
#define ESP_RETURN_ON_FALSE(c, e, ...) do { if (!(c)) return (e); } while (0)
static int xSemaphoreTake(void *p, unsigned t) { (void)p; (void)t; return 1; }
static int xSemaphoreGive(void *p) { (void)p; return 1; }
#include "context.inc"
static hal_camera_ptl_context_t s_ctx;
static bool s_catalog_valid;
static unsigned s_selected_model = 4;
static uint32_t s_model_crc[4];
static const char *const s_model_names[4] = {"Person", "Pet", "Gesture", "Face"};
static bool hx_model_identity_verified(unsigned id, uint32_t crc) { (void)id; (void)crc; return false; }
static watcher_hx_state_t remote;
static esp_err_t control_result = ESP_OK;
esp_err_t watcher_hx_control_status(watcher_hx_state_t *out) {
    *out = remote;
    return control_result;
}
#include "diagnostics.inc"
int main(int argc, char **argv) {
    CHECK(argc == 2);
    s_ctx.lock = &s_ctx;
    s_ctx.inferencing = true;
    s_ctx.inference_jpeg_only = true;
    s_ctx.inference_generation = 7;
    s_ctx.inference_status = ESP_ERR_TIMEOUT;
    remote = (watcher_hx_state_t){.mode = 1, .generation = 7};
    esp_err_t expected = ESP_OK;
    if (!strcmp(argv[1], "jpeg_timeout")) {
        expected = ESP_ERR_TIMEOUT;
    } else if (!strcmp(argv[1], "model_timeout")) {
        s_ctx.inference_jpeg_only = false;
        remote.mode = 2;
        expected = ESP_ERR_TIMEOUT;
    } else if (!strcmp(argv[1], "healthy")) {
        s_ctx.inference_status = ESP_OK;
    } else if (!strcmp(argv[1], "foreign_generation")) {
        remote.generation = 8;
    } else if (!strcmp(argv[1], "foreign_mode")) {
        remote.mode = 2;
    } else if (!strcmp(argv[1], "inactive")) {
        s_ctx.inferencing = false;
    } else if (!strcmp(argv[1], "remote_error")) {
        remote.error = 1;
        expected = ESP_FAIL;
    } else {
        CHECK(!strcmp(argv[1], "control_error"));
        control_result = ESP_ERR_INVALID_RESPONSE;
        expected = control_result;
    }
    hal_camera_diagnostics_t d;
    CHECK(hal_camera_get_diagnostics(&d) == ESP_OK);
    CHECK(d.status == expected);
    CHECK(d.connected == (control_result == ESP_OK));
    if (control_result == ESP_OK) {
        CHECK(d.streaming == (remote.mode == 1));
        CHECK(d.inferencing == (remote.mode == 2));
    }
    return 0;
}
