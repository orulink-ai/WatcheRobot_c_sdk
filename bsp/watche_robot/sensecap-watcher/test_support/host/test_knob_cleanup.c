#include <stdio.h>
#include <stdlib.h>
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #x); exit(1); } } while (0)
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_ERR_INVALID_ARG -2
#define GPIO_INTR_DISABLE 0
#define GPIO_MODE_INPUT 1
#define GPIO_PULLDOWN_DISABLE 0
#define GPIO_PULLUP_DISABLE 0
#define ESP_LOGD(...) ((void)0)
#define KNOB_CHECK(a, str, err) do { if (!(a)) return (err); } while (0)
typedef void *knob_handle_t;
typedef struct Knob { void *encoder_a, *encoder_b, *usr_data[8]; struct Knob *next; } knob_dev_t;
typedef struct { int intr_type, mode; uint64_t pin_bit_mask; int pull_down_en, pull_up_en; } gpio_config_t;
static knob_dev_t *s_head_handle;
static bool s_is_timer_running = true;
static void *s_knob_timer_handle;
static int fail_pin, calls_a, calls_b, invalid, frees, timer_deletes;
static int gpio_config(const gpio_config_t *p) {
    int pin = p->pin_bit_mask == (1ULL << 41) ? 41 : p->pin_bit_mask == (1ULL << 42) ? 42 : -1;
    if (pin == 41) ++calls_a; else if (pin == 42) ++calls_b; else ++invalid;
    return pin == -1 || pin == fail_pin ? ESP_FAIL : ESP_OK;
}
static int esp_timer_stop(void *p) { (void)p; return 0; }
static int esp_timer_delete(void *p) { (void)p; ++timer_deletes; return 0; }
static void counted_free(void *p) { ++frees; free(p); }
#define free counted_free
#include "knob_gpio.inc"
#include "knob_delete.inc"
#undef free
int main(int argc, char **argv) {
    CHECK(argc == 2);
    fail_pin = atoi(argv[1]);
    knob_dev_t *knob = calloc(1, sizeof(*knob));
    knob->encoder_a = (void *)(intptr_t)41; knob->encoder_b = (void *)(intptr_t)42;
    s_head_handle = knob;
    int ret = iot_knob_delete(knob);
    if (fail_pin) {
        CHECK(ret != ESP_OK && frees == 0 && timer_deletes == 0 && s_head_handle == knob);
        fail_pin = 0;
        CHECK(iot_knob_delete(knob) == ESP_OK);
    } else CHECK(ret == ESP_OK);
    CHECK(invalid == 0 && calls_a >= 1 && calls_b >= 1);
    CHECK(frees == 1 && timer_deletes == 1 && s_head_handle == NULL);
    return 0;
}
