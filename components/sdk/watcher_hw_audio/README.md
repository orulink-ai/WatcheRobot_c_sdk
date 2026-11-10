# watcher_hw_audio

Full-duplex signed little-endian 16-bit mono PCM at 16000 or 24000 Hz with an exclusive bus/codec lease.

- Public header: [`include/watcher_hw_audio.h`](include/watcher_hw_audio.h)
- [Usage, lifecycle sample, ownership and limitations](../../../docs/api/audio.md)
- [Example](../../../examples/head/README.md) · [Dependencies/configuration](../../../docs/dependencies.md)

## Minimal usage / 最小用法

Blocking operations belong to one audio-owner task, not ISR/callback/LVGL lock. Use writable 16-bit mono PCM buffers; drain before completion/volume/close. Cleanup failure may retain the exclusive codec lease; retry close before handover.

```c
#include "watcher_hw_audio.h"

/* Same application audio-owner task for all calls. Silent, writable PCM. */
esp_err_t play_silence(void) {
    int16_t pcm[160] = {0};
    esp_err_t err = watcher_hw_audio_init(16000, 0);
    if (err != ESP_OK) {
        (void)watcher_hw_audio_close(); /* Retry/report cleanup failure in real app. */
        return err;
    }
    err = watcher_hw_audio_write(pcm, sizeof(pcm));
    if (err == ESP_OK) err = watcher_hw_audio_drain(1000);
    esp_err_t closed = watcher_hw_audio_close();
    return err != ESP_OK ? err : closed;
}
```

These lifecycle snippets have not been compiled by the documentation task. Check operation and cleanup errors independently; do not assume hardware release after failed cleanup. Complete behavior and module limits are in the linked API guide.

## Integration / 集成

Development preview; use with the full source checkout and `examples/sdk.cmake`, not an unverified
Registry install. ESP-IDF 6.0.2 / ESP32-S3 is the example contract; display/head uses LVGL 8.4.0.
Direct dependencies: watcher_hw_core, hal_audio; private freertos. See the linked usage guide for the actual minimal init/operation/cleanup
snippet (core is caller-owned FIFO/types, without a hardware lifecycle).

中文：随完整源码示例使用，未提供已发布组件安装命令。真实 API 用法、任务所有权、错误处理及限制见上方使用指南。
Do not use a lifecycle sample as a motion, acoustic, camera or LCD acceptance test.

First-party code follows the repository [license](../../../LICENSE); dependencies retain their own licenses.
