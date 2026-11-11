#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <setjmp.h>
#include "hal_camera.h"
#include "watcher_hx_control.h"
#include "watcher_face_frame.h"
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
static bool preview_fallback;
static hal_camera_inference_frame_t first_frame, last_frame;
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
    *s = (watcher_hx_state_t){.generation=inputs[input_next-1].generation,
                            .mode=s_ctx.inference_jpeg_only ? 1 : 2,.model=4};
    return ESP_OK;
}
typedef struct { uint32_t sequence; const uint8_t *jpeg; size_t jpeg_size; } watcher_hx_ptl_frame_t;
static int watcher_hx_ptl_read(watcher_hx_ptl_frame_t *f, unsigned t) {
    (void)t;
    if (preview_fallback && input_next == 1) return ESP_ERR_TIMEOUT; /* BOXES consumes the next input. */
    CHECK(input_next < input_count);
    input_t i = inputs[input_next++]; now = i.us;
    if (i.code != ESP_OK) return i.code;
    static const uint8_t jpeg[] = {255, 216, 255, 217};
    static uint8_t packed[128];
    *f = (watcher_hx_ptl_frame_t){.sequence=i.sequence,.jpeg=jpeg,.jpeg_size=sizeof(jpeg)};
    if (!s_ctx.inference_jpeg_only) {
        wff_frame_t paired = {.generation=i.generation,.sequence=i.sequence,.width=640,.height=480,.count=1,
                             .boxes={{400,100,80,60,90,0}}};
        f->jpeg_size = wff_pack(packed, sizeof(packed), jpeg, sizeof(jpeg), &paired);
        CHECK(f->jpeg_size != 0);
        f->jpeg = packed;
    }
    return ESP_OK;
}
/* Image codec behavior is independent of the result routing under test. */
static bool hal_camera_jpeg_dimensions_match(const uint8_t *p,size_t n,unsigned w,unsigned h) { (void)p;(void)n;return w==640 && h==480; }
static int mbedtls_base64_encode(unsigned char *d,size_t dn,size_t *out,const unsigned char *s,size_t sn) { (void)d;(void)dn;(void)s;(void)sn;*out=4;return 0; }
typedef struct { uint64_t started_us; } hx_photo_warmup_t;
static bool hx_photo_warmup_observe(hx_photo_warmup_t *w,uint64_t t,bool valid) { (void)w;(void)t;return valid; }
static void callback(const hal_camera_inference_frame_t *f, void *ctx) {
    (void)ctx;
    CHECK(f->sequence != 0);
    if (!callbacks) first_frame=*f;
    last_frame=*f;
    ++callbacks;
}
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
    } else if (!strcmp(argv[1],"jpeg_timeout") || !strcmp(argv[1],"jpeg_recovery")) {
        static char image[8]; s_ctx.inference_image=image; s_ctx.inference_jpeg_only=true;
        inputs[0]=(input_t){ESP_ERR_TIMEOUT,1,0,100000};input_count=1;failures=1;
        expected_status=ESP_ERR_TIMEOUT;
        if (!strcmp(argv[1],"jpeg_recovery")) {
            inputs[1]=(input_t){ESP_OK,1,1,200000};input_count=2;expected_callbacks=1;expected_status=ESP_OK;
        }
    } else if (!strcmp(argv[1],"paired") || !strcmp(argv[1],"paired_fallback")) {
        static char image[8]; s_ctx.inference_image=image;
        preview_fallback=!strcmp(argv[1],"paired_fallback");
        inputs[0]=(input_t){ESP_OK,1,1,100000};input_count=1;expected_callbacks=1;
        if (preview_fallback) {
            inputs[1]=(input_t){ESP_OK,1,2,200000};input_count=2;expected_callbacks=2;
        }
    } else {
        CHECK(!strcmp(argv[1],"error"));
        inputs[0]=(input_t){ESP_ERR_INVALID_RESPONSE,1,0,50000};input_count=1;failures=1;
        expected_status=ESP_ERR_INVALID_RESPONSE;
    }
    if (!setjmp(finished)) inference_task(NULL);
    CHECK(s_ctx.inference_stats.parse_failures == failures);
    CHECK(callbacks == expected_callbacks);
    CHECK(s_ctx.inference_status == expected_status);
    CHECK(s_ctx.inference_generation_lost == !strcmp(argv[1],"wrong_generation"));
    if (!strcmp(argv[1],"paired") || !strcmp(argv[1],"jpeg_recovery")) {
        CHECK(last_frame.frame_width == 640 && last_frame.frame_height == 480);
        CHECK(last_frame.preview_image_base64 != NULL && last_frame.preview_image_size == 4);
        if (!strcmp(argv[1],"paired")) CHECK(last_frame.box_count == 1 && last_frame.boxes[0].x == 400);
        else CHECK(last_frame.box_count == 0);
    } else if (preview_fallback) {
        CHECK(first_frame.frame_width == 640 && first_frame.frame_height == 480);
        CHECK(first_frame.preview_image_base64 != NULL && first_frame.preview_image_size == 4);
        CHECK(last_frame.frame_width == 320 && last_frame.frame_height == 240);
        CHECK(last_frame.preview_image_base64 == NULL && last_frame.preview_image_size == 0);
    }
    return 0;
}
