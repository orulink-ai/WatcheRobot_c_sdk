# Audio: blocking PCM record and playback

Full-duplex signed little-endian 16-bit mono PCM at 16000 or 24000 Hz with an exclusive bus/codec lease.

Public contract: [`watcher_hw_audio.h`](../../components/sdk/watcher_hw_audio/include/watcher_hw_audio.h).
This guide uses the checked-in header, not an invented convenience API. Use the complete source checkout;
no published Registry install command is offered. Snippets illustrate ownership/lifecycle and are compile-checked in an isolated ESP-IDF consumer;
they are not executed on a robot or physical acceptance tests. See [verification](../testing.md).

## Minimal lifecycle / 最小生命周期

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

Check every return value in the application. A first-operation error and a cleanup error are distinct;
log both in production and do not assume failed cleanup released hardware.

## Ownership, format and completion

All init/read/write/drain/volume/close calls belong to one owner task. They block: never call from an
ISR, MCU/camera callback or while holding an LVGL lock. `read(void *, bytes)` fills caller-owned memory;
`write(void *, bytes)` needs **writable** memory because codec software volume can modify it. Use PCM
frames, not MP3/WAV file bytes. Wake-word and idle policies are not included.

`volume(percent)` accepts 0–100 on the codec's dB curve, not perceived loudness. BSP caps output at 95
to limit distortion; PCM amplitude also affects level. Init/volume check PA power; zero mutes and nonzero
output unmutes. Start physical tests conservatively and judge sound manually; do not equate a progress
bar with audibility. The lifecycle sample above is deliberately muted.

`drain(timeout_ms)` needs a positive timeout on the same owner task. Drain before reporting completion,
changing volume or closing: successful write alone can leave PCM in DMA. Drain proves delivery, not
sound quality, and does not release the lease. After init/close failure, retry close before handing
ownership to another user; failed hardware cleanup can retain the lease. Production applications must
record/retry cleanup failures rather than treating the original error return as proof of release.
Use the example defaults/codec dependencies; inspect [dependencies](../dependencies.md) for target-name
resolution and local adaptations before substituting a Registry codec.

中文：单一任务独占 codec，16 位单声道 PCM，读写阻塞且写缓冲必须可修改；drain 不等于声音验收。
清理失败需重试 close，不可直接交出硬件所有权。


## Dependencies and examples

Direct CMake dependencies: watcher_hw_core, hal_audio; private freertos. Use the matching example defaults, partitions and manifest; headers
alone do not supply the transitive dependency closure. [Dependency details](../dependencies.md).

- [Runnable head example](../../examples/head/README.md)
- [Combined robot](../../examples/robot/README.md)
- [Build, paired firmware, backups and full recovery](../getting-started.md)
- [API/documentation index](../README.md)
