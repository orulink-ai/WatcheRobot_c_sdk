# 连接麦克风和扬声器

把录音、播放等操作接到板上的声音芯片，并协调它们共用的硬件。只有排查声音硬件或维护底层驱动时，才需要直接阅读这一层。

内部实现组件（internal implementation）。由公开 SDK 的 [`watcher_hw_audio`](../../bsp/watche_robot/watcher_hw_audio/README.md) 使用；应用不应单独初始化本层。

## 接口与依赖

- 接口：[`hal_audio.h`](include/hal_audio.h)
- 依赖：`espressif__esp_codec_dev`；内部使用 `sensecap-watcher`、`esp_audio_codec` 和 `media_lib_sal`。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

底层还提供 PCM（声音采样）和 Opus（压缩声音）支持；公开录放音接口仍按自己的 PCM 格式工作。声音芯片与总线一次只交给一套使用者，不能在公开音频接口打开时另行初始化或操作。失败清理仍可能保留使用权，必须检查释放结果。

许可见仓库 [LICENSE](../../LICENSE)；依赖保留各自许可证。
