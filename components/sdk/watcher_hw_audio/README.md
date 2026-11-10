# 录音与播放

需要从麦克风读取声音，或通过扬声器播放应用准备的声音时，使用这一组接口。它处理的是一串声音采样值（PCM），不是直接打开 MP3 或 WAV 文件。

最短流程：初始化 → 读入或写出采样数据 → 等待播放数据送出 → 关闭。下面播放一小段静音，不用于检查扬声器是否正常。

## 最短用法

```c
#include "watcher_hw_audio.h"
#include "esp_log.h"

/* Same application audio-owner task for all calls. Silent, writable PCM. */
esp_err_t play_silence(void) {
    int16_t pcm[160] = {0};
    esp_err_t err = watcher_hw_audio_init(16000, 0);
    if (err != ESP_OK) {
        esp_err_t cleanup = watcher_hw_audio_close();
        ESP_LOGE("sdk_example", "init failed: %s; cleanup: %s",
                 esp_err_to_name(err), esp_err_to_name(cleanup));
        return err;
    }
    err = watcher_hw_audio_write(pcm, sizeof(pcm));
    if (err == ESP_OK) err = watcher_hw_audio_drain(1000);
    esp_err_t closed = watcher_hw_audio_close();
    if (err != ESP_OK || closed != ESP_OK)
        ESP_LOGE("sdk_example", "operation: %s; close: %s",
                 esp_err_to_name(err), esp_err_to_name(closed));
    return err != ESP_OK ? err : closed;
}
```

示例分别记录操作错误与关闭错误。真实应用必须继续处理清理失败，必要时重试关闭；不要以一次错误返回作为资源已释放的依据。

## 必须保留的使用要求

所有读写、等待播放送出、调音量与关闭都由同一应用任务顺序执行；不能在中断、硬件回调或持有界面锁时调用。使用可修改的 16 位单声道 PCM 数据，采样率为 16000 或 24000 Hz。报告播放完成、改音量或关闭前先 drain。打开后独占声音芯片和总线，清理失败可能仍未释放。

完整参数、错误恢复与限制见[使用指南](../../../docs/api/audio.md)，公开符号见[`watcher_hw_audio.h`](include/watcher_hw_audio.h)。代码用于说明使用顺序，不是硬件验收记录；实际验证范围见[测试说明](../../../docs/testing.md)。

## 接入项目

当前为开发预览。使用完整源码和 `examples/sdk.cmake`，不要假定可从组件仓库独立安装。示例使用 ESP-IDF 6.0.2 / ESP32-S3；显示示例使用 LVGL 8.4.0。配置、分区和依赖清单要与示例匹配。

- [可运行的 head 示例](../../../examples/head/README.md)
- [依赖与本地适配](../../../docs/dependencies.md)

第一方代码遵循仓库[许可证](../../../LICENSE)；依赖保留各自许可证。

## English: Record and play sound

Read microphone samples or play samples prepared by the application. The interface uses uncompressed PCM samples; it does not open MP3 or WAV files directly. The example above sends silence and is not a speaker test.

- Keep initialization, read/write, waiting for playback, volume and close calls in the same task. These calls wait for work to finish; do not run them in interrupts, hardware callbacks or while holding the screen lock.
- Use signed, little-endian 16-bit mono samples at 16000 or 24000 Hz. Buffer lengths are byte counts, must be positive multiples of two, and must not exceed INT_MAX. Playback memory must be writable because software volume processing may modify it.
- Wait with drain and check its result before reporting completion, changing volume or closing. Sent data does not prove audible sound or good quality.
- Check cleanup errors separately. A failed close may still hold exclusive hardware access; retry cleanup before handing the audio hardware to other code.
