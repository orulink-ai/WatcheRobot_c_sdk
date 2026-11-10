# watcher_hw_audio — 录音与播放

公开 SDK 组件（public SDK）。从麦克风读取 PCM 或向扬声器写入 PCM；不直接打开 MP3/WAV 文件。

## 接口与依赖

- 接口：[`watcher_hw_audio.h`](include/watcher_hw_audio.h)；参数与错误处理见[使用指南](../../../docs/api/audio.md)。
- 依赖：`watcher_hw_core`、[`hal_audio`](../../hal/hal_audio/README.md)，内部使用 FreeRTOS。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 使用约束

- 由同一应用任务顺序执行初始化、读写、drain、调音量与关闭。调用会阻塞，不能在中断、硬件回调或持有 LVGL 锁时执行。
- 使用有符号、小端、16 位单声道 PCM，采样率仅支持 16000 或 24000 Hz。长度按字节计算，须为正偶数且不超过 `INT_MAX`；播放缓冲区必须可写，软件音量处理可能修改数据。
- 报告播放完成、改音量或关闭前，先 drain 并检查结果。送出数据不证明实际有声或音质合格。
- 打开后独占声音芯片和总线。初始化或关闭失败后，分别检查操作与清理错误；必要时重试 close，确认释放后才能交给其他使用者。

## English

Public SDK for mono PCM recording/playback. Use one owner task, writable playback buffers and checked drain/close; failed cleanup may retain the exclusive hardware lease.

第一方代码遵循仓库 [LICENSE](../../../LICENSE)；依赖保留各自许可证。
