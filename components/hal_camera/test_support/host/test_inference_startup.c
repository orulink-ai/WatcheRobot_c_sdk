#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <setjmp.h>
#include "hal_camera.h"
#include "watcher_hx_control.h"
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #x); exit(1); } } while (0)
typedef void *SemaphoreHandle_t;
typedef void *TaskHandle_t;
#define portMAX_DELAY 0
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
#define TAG "test"
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define HX_MEDIA_SOURCE_WIDTH 640
#define HX_MEDIA_SOURCE_HEIGHT 480
#include "context.inc"
static hal_camera_ptl_context_t s_ctx;
static int64_t now;
static jmp_buf finished;
typedef struct { int code; uint32_t generation, sequence; int64_t us; } input_t;
static input_t inputs[4];
static unsigned input_count, input_next, callbacks;
static int64_t esp_timer_get_time(void) { return now; }
static int xSemaphoreTake(void *p, unsigned t) { (void)p; (void)t; return 1; }
static int xSemaphoreGive(void *p) { (void)p; return 1; }
static void vTaskDelay(unsigned t) { (void)t; if (input_next == input_count) s_ctx.inference_stop = true; }
static int ulTaskNotifyTake(int p, unsigned t) { (void)p; (void)t; longjmp(finished, 1); }
esp_err_t watcher_hx_control_boxes(watcher_hx_result_t *r) {
    CHECK(input_next < input_count);
    input_t i = inputs[input_next++]; now = i.us;
    *r = (watcher_hx_result_t){.generation=i.generation,.sequence=i.sequence,.width=320,.height=240};
    return i.code;
}
esp_err_t watcher_hx_control_status(watcher_hx_state_t *s) {
    *s = (watcher_hx_state_t){.generation=inputs[input_next-1].generation,.mode=2,.model=4};
    return ESP_OK;
}
typedef struct { uint32_t sequence; const uint8_t *jpeg; size_t jpeg_size; } watcher_hx_ptl_frame_t;
typedef struct { uint16_t x,y,width,height,score,target; } wff_box_t;
typedef struct { uint32_t generation,sequence; uint16_t width,height; uint8_t count; wff_box_t boxes[8]; } wff_frame_t;
static int watcher_hx_ptl_read(watcher_hx_ptl_frame_t *f, unsigned t) { (void)f;(void)t; return ESP_FAIL; }
static bool wff_unpack(const uint8_t *p,size_t n,wff_frame_t *f) { (void)p;(void)n;(void)f;return false; }
static bool hal_camera_jpeg_dimensions_match(const uint8_t *p,size_t n,unsigned w,unsigned h) { (void)p;(void)n;(void)w;(void)h;return false; }
static int mbedtls_base64_encode(unsigned char *d,size_t dn,size_t *out,const unsigned char *s,size_t sn) { (void)d;(void)dn;(void)out;(void)s;(void)sn;return -1; }
typedef struct { uint64_t started_us; } hx_photo_warmup_t;
static bool hx_photo_warmup_observe(hx_photo_warmup_t *w,uint64_t t,bool valid) { (void)w;(void)t;return valid; }
static void callback(const hal_camera_inference_frame_t *f, void *ctx) { (void)ctx; CHECK(f->sequence != 0); ++callbacks; }
#include "inference_task.inc"
int main(int argc,char **argv) {
    CHECK(argc == 2);
    s_ctx.inference_generation = 1; s_ctx.inference_cb = callback;
    unsigned failures = 0, expected_callbacks = 0;
    esp_err_t expected_status = ESP_OK;
    if (!strcmp(argv[1],"initial")) {
        inputs[0]=(input_t){ESP_ERR_NOT_FINISHED,1,0,50000};
        inputs[1]=(input_t){ESP_ERR_NOT_FINISHED,1,0,90000};
        inputs[2]=(input_t){ESP_OK,1,1,150000}; input_count=3; expected_callbacks=1;
    } else if (!strcmp(argv[1],"after_frame")) {
        inputs[0]=(input_t){ESP_OK,1,1,100000};
        inputs[1]=(input_t){ESP_ERR_NOT_FINISHED,1,0,200000}; input_count=2; failures=1;expected_callbacks=1;
        expected_status = ESP_ERR_INVALID_RESPONSE;
    } else if (!strcmp(argv[1],"timeout") || !strcmp(argv[1],"boundary")) {
        inputs[0]=(input_t){ESP_ERR_NOT_FINISHED,1,0,!strcmp(argv[1],"boundary") ? 5000000 : 6000000};
        input_count=1;failures=1;expected_status=ESP_ERR_TIMEOUT;
    } else if (!strcmp(argv[1],"recovery")) {
        inputs[0]=(input_t){ESP_ERR_NOT_FINISHED,1,0,6000000};
        inputs[1]=(input_t){ESP_OK,1,1,6100000};input_count=2;failures=1;expected_callbacks=1;
    } else if (!strcmp(argv[1],"wrong_generation")) {
        inputs[0]=(input_t){ESP_ERR_NOT_FINISHED,2,0,50000};input_count=1;failures=1;
        expected_status=ESP_ERR_INVALID_RESPONSE;
    } else {
        inputs[0]=(input_t){ESP_ERR_INVALID_RESPONSE,1,0,50000};input_count=1;failures=1;
        expected_status=ESP_ERR_INVALID_RESPONSE;
    }
    if (!setjmp(finished)) inference_task(NULL);
    CHECK(s_ctx.inference_stats.parse_failures == failures);
    CHECK(callbacks == expected_callbacks);
    CHECK(s_ctx.inference_status == expected_status);
    CHECK(s_ctx.inference_generation_lost == !strcmp(argv[1],"wrong_generation"));
    return 0;
}
