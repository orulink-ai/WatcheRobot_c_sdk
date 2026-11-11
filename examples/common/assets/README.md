# Speaker-test sample / 扬声器测试样本

Use **Test speaker → Test voice** in the head/robot screen, or follow the hardware-check speaker prompts. The bundled sample says:

在 head/robot 的 **Test speaker → Test voice** 或硬件检查的扬声器项目中播放内置语音：

> This is the speaker test. One, two, three.

## Format and playback / 格式与播放

`speaker_pcm.inc` contains mono signed PCM16 audio at 16000 Hz, generated with the eSpeak NG `en-us` formant voice. No audio download or generation step is needed to run the example.

`speaker_pcm.inc` 是使用 eSpeak NG 的 `en-us` 合成语音生成的 16000 Hz、16 位有符号单声道 PCM。运行示例无需另行下载或生成音频。

The sample stays read-only in flash. Playback copies blocks into writable scratch memory for SDK volume processing. The **Output** setting adjusts playback level; recording **Replay** boost does not affect this sample.

样本以只读形式保存在 Flash 中，播放时分块复制到可写缓冲区供 SDK 处理音量。**Output** 调整播放音量，录音 **Replay** 的放大设置不影响此样本。

## License / 许可

The original test text and generated sample data are dedicated to the public domain under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). SPDX: `CC0-1.0`. This applies to the sample, not the surrounding SDK code.

测试文本与生成的语音数据采用 CC0 1.0，适用范围为该素材；SDK 代码的许可见仓库 LICENSE。

The sample was generated offline with eSpeak NG and FFmpeg. These tools are not linked into or distributed with the example. See the [GNU output FAQ](https://www.gnu.org/licenses/gpl-faq.html#GPLOutput) for tool-output licensing.
