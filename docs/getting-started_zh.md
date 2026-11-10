[English](getting-started.md) | 简体中文

# 如何使用 WatcheRobot C SDK

| [屏幕与触摸](#屏幕与触摸) | [录音与播放](#录音与播放) | [拍照与连续画面](#拍照与连续画面) | [灯光与身体触摸](#灯光与身体触摸) | [身体运动](#身体运动) |
| --- | --- | --- | --- | --- |

## 概述

本页按功能介绍接口：先初始化硬件，再调用需要的操作。不需要先了解内部组件或通信协议。
首次使用请先完成[环境准备与编译](build-and-flash_zh.md)；烧录、备份和恢复也在该页说明。

下面的 C 代码是应用函数，不是终端命令，可参考[组合示例](../examples/robot/README.md)的工程配置接入。
由应用任务调用，不要与原有演示同时初始化同一硬件。各节是独立用法，不要求全部运行。

## 通用用法

- 开发环境：**ESP-IDF 6.0.2、ESP32-S3**；界面库为 **LVGL 8.4.0**。
- `init()` 打开硬件，`close()` 关闭硬件；检查每个函数的返回值，`ESP_OK` 表示本次调用成功。
- 查询状态成功不等于设备已就绪，仍需检查 `state`。机身初始化后可能还在连接，见下方示例。
- 函数声明和参数以[公开头文件](../components/sdk)为准；使用这些接口无需直接操作硬件引脚或底层通信总线。

## 屏幕与触摸

### 显示文字

初始化会准备屏幕、触摸和 LVGL。修改界面前先加锁，完成后解锁，避免同时改动界面。

```c
#include "watcher_hw_display.h"

esp_err_t show_message(void) {
    esp_err_t err = watcher_hw_display_init();
    if (err != ESP_OK) return err;
    if (!watcher_hw_display_lock(1000)) return ESP_ERR_TIMEOUT;
    lv_obj_t *label = lv_label_create(lv_scr_act());
    if (label) {
        lv_label_set_text(label, "Hello, WatcheRobot!");
        lv_obj_center(label);
    }
    watcher_hw_display_unlock();
    return label ? ESP_OK : ESP_ERR_NO_MEM;
}
```

调用成功后应显示文字，屏幕保持打开；可用 LVGL 的按钮和事件处理屏幕触摸。
不再使用时先停止其他任务访问界面，再在**没有持锁**的地方调用 `watcher_hw_display_close()`。
初始化或后续操作失败也要检查关闭结果，清理失败时重试，不能直接假定资源已释放。
[完整显示接口与注意事项](api/display.md)。

## 录音与播放

### 录制一小段声音并回放

接口使用 PCM，即未压缩的声音采样，不是直接打开 MP3 或 WAV 文件。
以下按 16 kHz、16 位单声道录制约 0.1 秒，再回放；所有声音操作在同一个任务中依次执行。

```c
#include "watcher_hw_audio.h"
#include "esp_log.h"

esp_err_t record_and_play(void) {
    static int16_t pcm[1600];
    esp_err_t err = watcher_hw_audio_init(16000, 30);
    if (err == ESP_OK) err = watcher_hw_audio_read(pcm, sizeof(pcm));
    if (err == ESP_OK) err = watcher_hw_audio_write(pcm, sizeof(pcm));
    if (err == ESP_OK) err = watcher_hw_audio_drain(1000);
    esp_err_t closed = watcher_hw_audio_close();
    if (closed != ESP_OK)
        ESP_LOGE("guide", "Audio cleanup failed: %s", esp_err_to_name(closed));
    return err != ESP_OK ? err : closed;
}
```

先用较低音量，亲耳确认结果。`drain()` 等待已提交的声音数据送出，之后才关闭；进度完成不证明声音正常。
播放数据必须可修改，`sizeof(pcm)` 是字节数。不要在硬件回调、中断或屏幕锁内调用这些函数。
关闭失败时须继续处理清理，再交给其他代码使用；[完整音频用法](api/audio.md)。

## 拍照与连续画面

### 拍一张照片

摄像头需要配套的 Himax 固件。照片以 JPEG 数据交给下面的接收函数：

```c
#include "watcher_hw_camera.h"
#include "esp_log.h"

static void receive_photo(const uint8_t *jpeg, size_t size,
                          uint32_t timestamp_ms, void *context) {
    (void)jpeg; (void)timestamp_ms; (void)context;
    ESP_LOGI("guide", "JPEG received: %u bytes", (unsigned)size);
    /* Copy jpeg[0..size) here if the application needs to keep the photo. */
}

esp_err_t take_photo(void) {
    esp_err_t err = watcher_hw_camera_init();
    if (err == ESP_OK) err = watcher_hw_camera_capture(receive_photo, NULL);
    esp_err_t closed = watcher_hw_camera_close();
    if (closed != ESP_OK)
        ESP_LOGE("guide", "Camera cleanup failed: %s", esp_err_to_name(closed));
    return err != ESP_OK ? err : closed;
}
```

成功时串口记录照片字节数。此片段只接收和记录，不保存或显示照片。
图片数据只在接收函数返回前有效；要留用必须先复制，不要在接收函数里停止或关闭摄像头。
关闭失败时先完成清理，不要启动第二套摄像头控制。

### 连续取图

连续取图的流程是：初始化 → 启动取图 → 停止 → 关闭。初始化后调用 `watcher_hw_camera_stream(fps, receive_photo, NULL)`，每张图交给相同的接收函数；
`fps` 是请求帧率。需要结束时由应用任务调用 `watcher_hw_camera_stop()`，检查成功后再关闭。
[帧率限制、停止与出错处理](api/camera.md)。

## 灯光与身体触摸

### 初始化身体并检查是否就绪

灯光、身体触摸和运动共用同一次机身初始化。应用启动时调用 `watcher_hw_body_init()`；
之后重复查询状态，等 `WATCHER_HW_READY` 再操作。处于 `WATCHER_HW_STARTING` 时可以稍后再查；处于 `WATCHER_HW_FAULT` 时停止操作并排查，不要一直重试。下面的检查函数可在应用循环中调用，未就绪时先等待，不要强行发指令。

```c
#include "watcher_hw_body.h"

esp_err_t check_body_ready(void) {
    watcher_hw_status_t status;
    esp_err_t err = watcher_hw_body_status(&status);
    if (err != ESP_OK) return err;
    if (status.state == WATCHER_HW_READY) return ESP_OK;
    return status.last_error != ESP_OK ? status.last_error : ESP_ERR_INVALID_STATE;
}
```

### 设置侧边绿灯

```c
esp_err_t set_side_light(void) {
    esp_err_t err = check_body_ready();
    if (err != ESP_OK) return err;
    mcu_led_request_t light = {
        .mode = MCU_LED_MODE_STATIC,
        .zone = MCU_LED_ZONE_SIDE,
        .primary_green = 128,
        .brightness = 64,
    };
    return watcher_hw_body_light(&light);
}
```

预期侧边灯呈绿色。颜色和亮度范围为 0–255；底座灯用 `MCU_LED_ZONE_BOTTOM`，全部灯用 `MCU_LED_ZONE_ALL`。
关灯时使用 `MCU_LED_MODE_OFF`。返回成功表示请求成功，实际效果仍需观察。

### 读取身体触摸

应用可主动取出事件，识别按下、松手或长按。不要同时使用主动读取和回调分发两种方式。

```c
#include <string.h>
#include "esp_log.h"

esp_err_t read_body_event(void) {
    watcher_hw_event_t event;
    esp_err_t err = watcher_hw_body_next_event(&event);
    if (err != ESP_OK) return err;
    if (event.type == WATCHER_HW_EVENT_OVERFLOW) {
        ESP_LOGE("guide", "Events lost: cancel pending actions and recover before continuing");
        return ESP_ERR_INVALID_STATE;
    }
    if (event.type == WATCHER_HW_EVENT_TOUCH && event.size == sizeof(mcu_touch_state_t)) {
        mcu_touch_state_t touch;
        memcpy(&touch, event.payload, sizeof(touch));
        ESP_LOGI("guide", "Touch %u: event=%d", touch.touch_id, touch.event_code);
    }
    return ESP_OK;
}
```

没有事件时返回 `ESP_ERR_NOT_FOUND`，这是“暂时没有新输入”。触摸时应看到对应日志：`event=1` 为按下，`2` 为松手，`3` 为长按。
若事件丢失，应用必须取消待执行动作，按[机身接口的恢复步骤](api/body.md)重新初始化、订阅并等待就绪；
仅打印错误不够，恢复后也不得重放旧动作，必须等用户新的操作。

## 身体运动

### 发送运动请求

先完成上节的机身初始化，并复用 `check_body_ready()` 检查函数。

**先读[运动注意事项](servo-open-loop_zh.md)**：清空整个可能运动的区域，保证可随时人工断电。
程序不能读取舵机实际转到的角度；即使移到参考位置，也可能从另一端移动很远。
下面的函数不会自动运行，仅在应用根据当前用户操作明确调用时发出指令。

```c
esp_err_t request_move(int x_degrees, int y_degrees, uint32_t duration_ms) {
    esp_err_t err = check_body_ready();
    if (err != ESP_OK) return err;
    uint32_t sequence;
    return watcher_hw_body_move(x_degrees, y_degrees, duration_ms, &sequence);
}
```

角度和时间范围见[运动接口](api/body.md)。请求成功不表示已经到位；收到命令确认或完成报告，也不证明机械已经停止。
停止请求使用 `watcher_hw_body_stop()`；断线时请求可能无法送达，它不是物理急停装置。
不再使用身体控制时调用 `watcher_hw_body_close()` 并检查关闭结果；关闭失败须继续清理，不能自动重试旧运动。

## 完整示例与进一步阅读

- [触摸控制灯光](../examples/body/README.md) · [屏幕、拍照与声音](../examples/head/README.md) · [组合应用](../examples/robot/README.md)。
- [编译、烧录与恢复](build-and-flash_zh.md)：工具安装、端口、备份、运行与恢复。
- [完整 API 指南](api/README.md)：参数、任务配合、错误恢复和关闭规则。
- [人工硬件体检](hardware-check_zh.md) · [已有验证结果](verification.md)。

本页只介绍当前 SDK 提供的接口；SD 卡、电池、USB 等硬件不在本页的专用接口范围内。代码编译通过不代替实机验收。

文档结构参考 [ESP-BSP API 使用指南](https://github.com/espressif/esp-bsp/blob/master/docu/how_to_use.md)，代码使用 WatcheRobot 自己的公开接口。
