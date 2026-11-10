# 拍照与连续取图

需要拍一张照片，或连续收到 JPEG 图像时，使用这一组接口。照片通过回调交给应用；保存、显示、上传或 AI 识别由应用另行处理。

最短流程：确认摄像头固件匹配 → 初始化 → 拍照并在回调内处理图像 → 关闭。下面收到图像后直接返回，不保存照片；要留存图像，必须在回调返回前复制数据。

## 最短用法

```c
#include "watcher_hw_camera.h"
#include "esp_log.h"

static void receive_jpeg(const uint8_t *jpeg, size_t size,
                         uint32_t timestamp_ms, void *ctx) {
    /* Borrowed only here: copy to caller-owned storage before returning if needed. */
    (void)jpeg; (void)size; (void)timestamp_ms; (void)ctx;
}
esp_err_t capture_once(void) {
    esp_err_t err = watcher_hw_camera_init();
    if (err != ESP_OK) {
        esp_err_t cleanup = watcher_hw_camera_close();
        ESP_LOGE("sdk_example", "init failed: %s; cleanup: %s",
                 esp_err_to_name(err), esp_err_to_name(cleanup));
        return err;
    }
    err = watcher_hw_camera_capture(receive_jpeg, NULL);
    esp_err_t closed = watcher_hw_camera_close();
    if (err != ESP_OK || closed != ESP_OK)
        ESP_LOGE("sdk_example", "operation: %s; close: %s",
                 esp_err_to_name(err), esp_err_to_name(closed));
    return err != ESP_OK ? err : closed;
}
```

示例分别记录操作错误与关闭错误。真实应用必须继续处理清理失败，必要时重试关闭；不要以一次错误返回作为资源已释放的依据。

## 必须保留的使用要求

由一个应用任务顺序管理打开、拍照、连续取图、停止和关闭。图像是临时借用的数据，只在回调内有效，要保存就先复制；回调中不能启动、停止或关闭摄像头。连续取图先成功停止再关闭。摄像头独立固件必须匹配；双方使用的图像传输规则称为 PTL，需启用对应配置。

完整参数、错误恢复与限制见[使用指南](../../../docs/api/camera.md)，公开符号见[`watcher_hw_camera.h`](include/watcher_hw_camera.h)。代码用于说明使用顺序，不是硬件验收记录；实际验证范围见[测试说明](../../../docs/development.md#testing)。

## 接入项目

当前为开发预览。使用完整源码和 `examples/sdk.cmake`，不要假定可从组件仓库独立安装。示例使用 ESP-IDF 6.0.2 / ESP32-S3；显示示例使用 LVGL 8.4.0。配置、分区和依赖清单要与示例匹配。

- [可运行的 head 示例](../../../examples/head/README.md)
- [依赖与本地适配](../../../docs/development.md#dependencies)

第一方代码遵循仓库[许可证](../../../LICENSE)；依赖保留各自许可证。

## English: Take photos and receive images

Capture one JPEG photo or receive a sequence of JPEG frames. Compatible camera firmware is required; image recognition and network upload are application features, not part of this interface.
Initialize, request a capture or start streaming, stop streaming when finished, then close.

- Use one task to coordinate opening, use and closing. Do not open another camera connection in parallel.
- Image bytes are valid only during their callback. Copy them before returning if the application needs them later.
- Do not block the image callback or close the camera from inside it. Stop/close from the coordinating task, check the result, and retry cleanup if it has not finished.
- A successful build or transfer is not evidence of a clear, current image; inspect actual photos and video on the device.
