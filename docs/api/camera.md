# 拍照与连续获取图像

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

示例记录操作和清理两个结果，返回值优先保留操作错误。真实应用还必须处理清理失败（例如重试关闭），不能记录后就把资源交给别的使用者。

## 运行前确认摄像头固件匹配

摄像头有独立的 Himax 处理芯片。两边必须按相同的图像传输规则发送和接收数据；这里把这套配套规则称为 **PTL 协议**。协议只是双方理解消息格式的约定，不是额外的拍照功能。

启用 `CONFIG_WATCHER_CAMERA_BACKEND_PTL=y`，并确认外部 Himax 固件与当前代码匹配。公开接口只支持这一条摄像头通路，不能因源码中还有其他实现就认为可直接替换。采用 head 示例配套配置、八线 PSRAM 和依赖清单；编译成功不能证明摄像头固件匹配，固件文件名或 HELLO 消息也不能替代实际成像检查。

## 图像何时可以使用

用同一个应用任务顺序管理初始化、拍照、连续取图、停止和关闭：

- `watcher_hw_camera_capture(callback, ctx)` 在调用它的任务中执行图像回调。
- `watcher_hw_camera_stream(fps, callback, ctx)` 在摄像头工作任务中执行回调，支持参数 1–30 fps，但不保证实际帧率。
- 图像指针指向 SDK 的暂存内存，**仅在回调期间有效**。这就是头文件中的 borrowed（临时借用）：应用不能释放它，也不能回调返回后继续使用；需要保留时必须复制到应用自己的内存。不能直接让长期显示的 LVGL 图片引用这块内存。
- 回调中不要重新启动、停止或关闭摄像头。需要停流时，通知应用管理任务去调用 `watcher_hw_camera_stop()`，检查成功后再 close。停止失败不能证明工作任务已经退出。

初始化或关闭失败仍需检查并重试清理，不能让其他使用者立即接管底层摄像头。

## 状态查询与恢复

`watcher_hw_camera_status()` 会报告底层查询失败、连接异常或设备故障，即使本地曾成功打开摄像头。返回 `ESP_OK` 表示读到了状态，不代表摄像头是 READY；还要检查 `state` 与 `last_error`。没有连续取图时也可以 READY，不要求正在 streaming。

临时查询故障在下一次健康查询后可消失；初始化/关闭等生命周期故障仍需 close 后重新初始化。真机无图或图像损坏都不能算通过摄像头验收，参见[硬件检查](../../examples/hardware_check/README.md)。

## 接入与完整示例

- 公开头文件：[`watcher_hw_camera.h`](../../components/sdk/watcher_hw_camera/include/watcher_hw_camera.h)。接口名称和参数以此为准。
- 使用完整源码与示例匹配的配置、分区和依赖清单；当前为开发预览，不提供未经验证的组件仓库安装命令。仅复制头文件不能补齐所有依赖。
- 直接 CMake 依赖：watcher_hw_core、hal_camera（必须启用 PTL）。详见[依赖与本地适配](../development.md#dependencies)。
- [可运行的 head 示例](../../examples/head/README.md) · [组合示例](../../examples/robot/README.md)
- [构建、配套固件、备份与恢复](../../examples/README.md) · [文档导航](README.md)

代码片段用于说明接口和使用顺序，不是对机器人执行过的验收记录。已有验证与真机检查边界见[测试说明](../development.md#testing)。

## English: Take photos and receive images

Capture one JPEG photo or receive a sequence of JPEG frames. Compatible camera firmware is required; image recognition and network upload are application features, not part of this interface.
Initialize, request a capture or start streaming, stop streaming when finished, then close.

- Use one task to coordinate opening, use and closing. Do not open another camera connection in parallel.
- Image bytes are valid only during their callback. Copy them before returning if the application needs them later.
- Do not block the image callback or close the camera from inside it. Stop/close from the coordinating task, check the result, and retry cleanup if it has not finished.
- A successful build or transfer is not evidence of a clear, current image; inspect actual photos and video on the device.
