# 录音与播放声音

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

示例记录操作和清理两个结果，返回值优先保留操作错误。真实应用还必须处理清理失败（例如重试关闭），不能记录后就把资源交给别的使用者。

## 任务与数据要求

所有初始化、读写、等待播放送出、调音量和关闭操作，交给同一个应用任务顺序执行。SDK 打开音频后独占声音芯片和共享总线，直到成功释放；这就是接口注释中的 lease（独占使用权）。其他录放音逻辑不能同时直接使用底层硬件。

这些调用会等待操作完成，不要放在中断处理函数（ISR）、机身或摄像头回调中，也不要在持有界面锁时调用。

- 格式是带符号、低字节在前的 16 位单声道采样，采样率仅支持 16000 或 24000 Hz；硬件支持录音与播放双向通路。
- `watcher_hw_audio_read(pcm, bytes)` 把声音写入应用提供的内存。
- `watcher_hw_audio_write(pcm, bytes)` 的内存也必须**可修改**：声音芯片的软件音量处理可能改写采样值。不要传只读数组。
- `bytes` 是字节数，必须为正、是 2 的倍数且不大于 `INT_MAX`；不是采样点数。不能直接传入带文件头的 WAV 数据或压缩后的 MP3 数据。
- SDK 不提供唤醒词检测或空闲休眠策略。

## 音量、完成与出错后的清理

`watcher_hw_audio_volume(percent)` 接受 0–100，但这个数字按芯片的分贝曲线转换，不代表人耳感到的等比例响度。板级支持将输出上限设为 95 以减少失真，采样本身的幅度也影响响度。初始化和调音量会检查功放电源；0 为静音，非零输出解除静音。真机测试从保守音量开始，亲耳检查，不要把进度条走完当成声音正常。

`watcher_hw_audio_drain(timeout_ms)` 等待已提交的采样离开硬件传输缓冲区（DMA）。必须在同一音频任务中调用，超时必须大于 0。报告播放完成、改音量或关闭前先 drain，并检查返回值；write 成功时仍可能有数据未送出。drain 成功只说明数据送出，不保证声音质量，也不释放音频使用权。

初始化或关闭失败后，先重试 `watcher_hw_audio_close()` 并记录清理错误，再把硬件交给别的使用者。清理失败可能仍保留独占使用权，不能只凭原操作的错误返回认定硬件已经释放。使用示例配套的音频依赖与配置；替换声音芯片库前，核对[依赖与本地适配](../development.md#dependencies)。

## 接入与完整示例

- 公开头文件：[`watcher_hw_audio.h`](../../bsp/watche_robot/watcher_hw_audio/include/watcher_hw_audio.h)。接口名称和参数以此为准。
- 使用完整源码与示例匹配的配置、分区和依赖清单；当前为开发预览，不提供未经验证的组件仓库安装命令。仅复制头文件不能补齐所有依赖。
- 直接 CMake 依赖：watcher_hw_core、hal_audio；私有依赖 freertos。详见[依赖与本地适配](../development.md#dependencies)。
- [可运行的 head 示例](../../examples/head/README.md) · [组合示例](../../examples/robot/README.md)
- [构建、配套固件、备份与恢复](../../examples/README.md) · [文档导航](README.md)

代码片段用于说明接口和使用顺序，不是对机器人执行过的验收记录。已有验证与真机检查边界见[测试说明](../development.md#testing)。

## English: Record and play sound

Read microphone samples or play samples prepared by the application. The interface uses uncompressed PCM samples; it does not open MP3 or WAV files directly. The example above sends silence and is not a speaker test.

- Keep initialization, read/write, waiting for playback, volume and close calls in the same task. These calls wait for work to finish; do not run them in interrupts, hardware callbacks or while holding the screen lock.
- Use signed, little-endian 16-bit mono samples at 16000 or 24000 Hz. Buffer lengths are byte counts, must be positive multiples of two, and must not exceed INT_MAX. Playback memory must be writable because software volume processing may modify it.
- Wait with drain and check its result before reporting completion, changing volume or closing. Sent data does not prove audible sound or good quality.
- Check cleanup errors separately. A failed close may still hold exclusive hardware access; retry cleanup before handing the audio hardware to other code.
