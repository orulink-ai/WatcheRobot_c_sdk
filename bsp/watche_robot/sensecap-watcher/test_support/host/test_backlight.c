#include <stdio.h>
#include <stdlib.h>
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #x); exit(1); } } while (0)
#include <stdbool.h>
#include <stdint.h>
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL -1
#define BIT(x) (1u << (x))
#define BSP_LCD_GPIO_BL 8
#define LEDC_LOW_SPEED_MODE 0
#define DRV_LCD_LEDC_CH 1
#define LEDC_INTR_DISABLE 0
#define LEDC_TIMER_1 1
#define DRV_LCD_LEDC_DUTY_RES 10
#define LEDC_AUTO_CLK 0
#define BSP_ERROR_CHECK_RETURN_ERR(call) do { int r = (call); if (r) return r; } while (0)
typedef struct { int gpio_num, speed_mode, channel, intr_type, timer_sel, duty, hpoint; } ledc_channel_config_t;
typedef struct { int speed_mode, duty_resolution, timer_num, freq_hz, clk_cfg; } ledc_timer_config_t;
static bool s_backlight_initialized;
static int timer_calls, channel_calls, timer_error, channel_error, brightness_error;
static int ledc_timer_config(const ledc_timer_config_t *p) { (void)p; ++timer_calls; return timer_error; }
static int ledc_channel_config(const ledc_channel_config_t *p) { CHECK(p->gpio_num == 8); ++channel_calls; return channel_error; }
static int bsp_lcd_brightness_set(int p) { CHECK(p == 0); return brightness_error; }
#include "backlight.inc"
int main(void) {
    timer_error = ESP_FAIL;
    CHECK(bsp_lcd_backlight_init() == ESP_FAIL && channel_calls == 0);
    timer_error = 0; channel_error = ESP_FAIL;
    CHECK(bsp_lcd_backlight_init() == ESP_FAIL);
    channel_error = 0; brightness_error = ESP_FAIL;
    CHECK(bsp_lcd_backlight_init() == ESP_FAIL);
    int channels = channel_calls, timers = timer_calls;
    brightness_error = 0;
    CHECK(bsp_lcd_backlight_init() == ESP_OK);
    CHECK(channel_calls == channels && timer_calls == timers);
    /* Reopen reuses the board-owned channel; no duplicate GPIO reservation. */
    CHECK(bsp_lcd_backlight_init() == ESP_OK);
    CHECK(channel_calls == channels && timer_calls == timers);
    return 0;
}
