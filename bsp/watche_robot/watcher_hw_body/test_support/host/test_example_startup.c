/* Execute each real app_main with injected SDK failures. No hardware or worker tasks. */
#include "watcher_hw_body.h"
#include "freertos/task.h"
#include <assert.h>
#include <setjmp.h>
#include <string.h>
#ifdef _MSC_VER
#include <crtdbg.h>
#include <stdlib.h>
#endif

static jmp_buf first_iteration;
static esp_err_t init_result, subscribe_result, close_result, head_result;
static unsigned init_calls, subscribe_calls, close_calls, head_calls, dispatch_calls;
static char order[16];
static unsigned order_size;
static void record(char operation) {
    assert(order_size + 1 < sizeof(order));
    order[order_size++] = operation;
}

#define app_main example_app_main
#include WATCHER_BODY_EXAMPLE_SOURCE
#undef app_main

esp_err_t watcher_hw_body_init(void) {
    ++init_calls;
    record('I');
    return init_result;
}
esp_err_t watcher_hw_body_subscribe(watcher_hw_body_event_cb_t callback, void *context) {
    assert(callback != NULL && context == NULL);
    ++subscribe_calls;
    record('S');
    return subscribe_result;
}
esp_err_t watcher_hw_body_close(void) {
    ++close_calls;
    record('C');
    return close_result;
}
esp_err_t head_demo_start(void) {
    ++head_calls;
    record('H');
    return head_result;
}
esp_err_t watcher_hw_body_dispatch_events(uint32_t maximum, uint32_t *dispatched) {
    assert(maximum == 32 && dispatched != NULL);
    ++dispatch_calls;
    record('D');
    *dispatched = 0;
    return ESP_OK;
}
esp_err_t watcher_hw_body_dropped_events(uint32_t *dropped) {
    *dropped = 0;
    return ESP_OK;
}
esp_err_t watcher_hw_body_light(const mcu_led_request_t *request) {
    (void)request;
    assert(0 && "startup must not send light commands");
    return ESP_FAIL;
}
esp_err_t watcher_hw_body_stop(void) {
    assert(0 && "startup must not send actuator commands");
    return ESP_FAIL;
}
void vTaskDelay(TickType_t ticks) {
    assert(ticks == pdMS_TO_TICKS(10));
    longjmp(first_iteration, 1);
}

int main(int argc, char **argv) {
#ifdef _MSC_VER
    _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_FILE);
    _CrtSetReportFile(_CRT_ASSERT, _CRTDBG_FILE_STDERR);
    _set_abort_behavior(0, _WRITE_ABORT_MSG | _CALL_REPORTFAULT);
#endif
    assert(argc == 2);
    const char *expected;
    if (strcmp(argv[1], "init_failure") == 0) {
        init_result = ESP_FAIL;
        expected = "I"; /* init owns its failure cleanup; do not close a foreign runtime. */
    } else if (strcmp(argv[1], "subscribe_failure") == 0) {
        subscribe_result = ESP_ERR_NO_MEM;
        expected = "ISC";
    } else if (strcmp(argv[1], "cleanup_failure") == 0) {
        subscribe_result = ESP_ERR_NO_MEM;
        close_result = ESP_ERR_TIMEOUT;
        expected = "ISC";
    } else if (strcmp(argv[1], "head_failure") == 0) {
        head_result = ESP_FAIL;
        expected = "ISHC";
    } else {
        assert(strcmp(argv[1], "success") == 0);
#ifdef WATCHER_EXAMPLE_HAS_HEAD
        expected = "ISHD";
#else
        expected = "ISD";
#endif
    }
    if (setjmp(first_iteration) == 0)
        example_app_main();
    assert(strcmp(order, expected) == 0 && "failed startup must not enter dependent operations or the event loop");
    assert(init_calls == 1);
    assert(subscribe_calls == (init_result == ESP_OK ? 1u : 0u));
    assert(dispatch_calls == (strcmp(argv[1], "success") == 0 ? 1u : 0u));
    assert(close_calls == (strchr(expected, 'C') != NULL ? 1u : 0u));
    assert(head_calls == (strchr(expected, 'H') != NULL ? 1u : 0u));
    return 0;
}
