#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #x); exit(1); } } while (0)
#include <stdlib.h>
typedef int esp_err_t;
#define ESP_OK 0
typedef struct { void *knob_handle, *btn_handle; } lvgl_port_encoder_ctx_t;
typedef struct { void *user_data; } lv_indev_drv_t;
typedef struct { lv_indev_drv_t *driver; } lv_indev_t;
static int knob_error, button_error, knobs, buttons, indevs, freed;
static int iot_knob_delete(void *p) { CHECK(p); ++knobs; return knob_error; }
static int iot_button_delete(void *p) { CHECK(p); ++buttons; return button_error; }
static void lv_indev_delete(lv_indev_t *p) { CHECK(p); ++indevs; }
static void tracked_free(void *p) { CHECK(p); ++freed; }
#define free tracked_free
#include "lcd_remove_encoder.inc"
#undef free
int main(void) {
    lvgl_port_encoder_ctx_t ctx = {(void *)1, (void *)2};
    lv_indev_drv_t drv = {&ctx}; lv_indev_t indev = {&drv};
    knob_error = 17;
    CHECK(lvgl_port_remove_encoder(&indev) == 17);
    CHECK(ctx.knob_handle && buttons == 0 && indevs == 0 && freed == 0);
    knob_error = 0; button_error = 23;
    CHECK(lvgl_port_remove_encoder(&indev) == 23);
    CHECK(ctx.knob_handle == NULL && ctx.btn_handle && indevs == 0);
    int knob_calls = knobs;
    button_error = 0;
    CHECK(lvgl_port_remove_encoder(&indev) == ESP_OK);
    CHECK(knobs == knob_calls && buttons == 2 && indevs == 1 && freed == 1);
    return 0;
}
