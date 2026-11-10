[English](README.md) | 简体中文

# WatcheRobot C SDK

WatcheRobot（小沃）是一款面向开发者和创作者的 AI 桌面机器人。C SDK 用于在机器人上编写自己的应用，
将屏幕、摄像头、麦克风、扬声器、身体运动和灯光组合成新的交互体验。

## 产品概述

<table>
<tr>
<td width="65%">
<p>WatcheRobot 由头部、身体和充电底座组成：</p>
<ul>
<li><b>头部</b>：ESP32-S3 主控、1.45 英寸触摸屏、摄像头、麦克风、扬声器和滚轮。</li>
<li><b>身体</b>：左右转动与上下俯仰、身体触摸、侧边灯光。</li>
<li><b>充电底座</b>：磁吸供电和环形氛围灯。</li>
</ul>
<p>你可以为它制作屏幕界面、拍照工具、声音交互或触摸灯光应用，也可以在此基础上设计自己的机器人动作。</p>
<p>本仓库提供设备端 C 接口和示例。若希望在电脑上通过 Python 控制现有机器人固件，请使用 <a href="https://github.com/orulink-ai/WatcheRobot_python_sdk">Python SDK</a>。</p>
</td>
<td width="35%" align="center">
<img src="docs/images/product/watche-robot-front.jpg" alt="WatcheRobot 产品正面渲染图" width="260" />
</td>
</tr>
</table>

## 硬件概览

| 部分 | 主要硬件 | 用途 |
| --- | --- | --- |
| 主控 | ESP32-S3，240 MHz，8 MB PSRAM | 运行你的 C 应用，连接屏幕、声音和相机 |
| 屏幕 | 1.45 英寸，412 × 412，电容触摸 | 显示文字、按钮和界面，响应屏幕操作 |
| 摄像头 | OV5647，Himax HX6538 视觉处理器 | 拍照和获取连续画面 |
| 声音 | 单麦克风、1 W 扬声器 | 录音与播放声音 |
| 身体 | CKS32F103C8T6、两个 SG90 舵机 | 左右转动、上下俯仰 |
| 触摸与灯光 | 身体触摸感应、侧边 RGB 灯、底座环形 RGB 灯 | 触摸互动、状态提示和氛围效果 |
| 接口 | USB-C、头部与身体连接口、底座磁吸接口 | 供电、开发连接及头部与身体通信 |

<table>
<tr>
<td align="center"><img src="docs/images/product/watche-robot-side.jpg" alt="WatcheRobot 侧面渲染图，可见扬声器与存储卡槽" width="250" /><br/>侧面</td>
<td align="center"><img src="docs/images/product/watche-robot-back.jpg" alt="WatcheRobot 背面渲染图，可见身体供电接口" width="250" /><br/>背面</td>
</tr>
</table>

产品图片与硬件信息摘自产品手册；[图片来源](docs/images/product/README.md)。硬件具有的能力不等于本 SDK 已提供对应接口，当前支持范围见下表。

## 功能与依赖

| 支持 | 功能 | 控制芯片或驱动 | 组件 | 版本 |
| --- | --- | --- | --- | --- |
| ✓ | 屏幕显示 | SPD2010 | [显示驱动](https://components.espressif.com/components/espressif/esp_lcd_spd2010/versions/1.0.1/readme) | 1.0.1 |
| ✓ | 屏幕触摸 | SPD2010 | [触摸驱动](https://components.espressif.com/components/espressif/esp_lcd_touch_spd2010/versions/0.0.1/readme) | 0.0.1，含本地适配 |
| ✓ | 界面绘制 | LVGL | [LVGL](https://components.espressif.com/components/lvgl/lvgl/versions/8.4.0/readme) · [界面适配](components/esp_lvgl_port/README.md) | 8.4.0 / 1.4.0-custom.1 |
| ✓ | 扬声器播放 | ES8311 | [音频组件](components/esp_codec_dev/README.md) · [使用指南](docs/api/audio.md) | 1.2.0，含本地适配 |
| ✓ | 麦克风录音 | ES7243 / ES7243E | [音频组件](components/esp_codec_dev/README.md) · [使用指南](docs/api/audio.md) | 1.2.0，含本地适配 |
| ✓ | 拍照与连续画面 | OV5647 / Himax HX6538 | [摄像接口](components/sdk/watcher_hw_camera/README.md) | 随本仓库源码提供 |
| ✓ | 身体转动 | 双舵机、机身控制芯片 | [运动接口](docs/api/body.md) | 随本仓库源码提供 |
| ✓ | 身体触摸 | TTP223 | [触摸事件](docs/api/body.md) | 随本仓库源码提供 |
| ✓ | 侧边与底座灯光 | WS2812B2020 | [灯光接口](docs/api/body.md) | 随本仓库源码提供 |

✓ 表示当前源码提供相应接口，不代表完成了整机实测。表内仓库组件尚未正式发布到乐鑫组件平台。
配套固件与完整依赖说明见[构建要求](docs/development.md#dependencies)。

## 示例

| 示例 | 可以体验什么 | 使用说明 |
| --- | --- | --- |
| 触摸灯光 | 触摸身体亮绿灯，松手后熄灭；记录触摸事件 | [body](examples/body/README.md) |
| 拍照、录音与屏幕 | 拍照、录音回放、扬声器测试和屏幕操作 | [head](examples/head/README.md) |
| 组合应用 | 将触摸灯光与拍照、声音、屏幕操作组合 | [robot](examples/robot/README.md) |
| 硬件体检 | 按屏幕提示逐项检查屏幕、声音、触摸、灯光和运动 | [hardware_check](examples/hardware_check/README.md) |

## 开发文档

开发环境为 **ESP-IDF 6.0.2 / ESP32-S3**，屏幕界面使用 **LVGL 8.4.0**。

- [接口使用指南](docs/getting-started_zh.md)：按功能查看初始化与调用示例。
- [按功能查接口](docs/api/README.md)：运动、灯光、触摸、拍照、声音与屏幕。
- [开发与贡献](docs/development.md)：供修改 SDK、测试和打包的维护者参考。

当前为开发预览。烧录会改写设备软件，开始前请按[示例注意事项](examples/README.md#before-flash-or-movement--烧录或运动前)准备备份和官方恢复包；运动前请阅读
[运动注意事项](docs/api/body.md#motion-safety)。编译通过不代表实机验收。

## 许可

第一方代码采用 [Apache-2.0](LICENSE)。第三方组件和素材保留各自的许可证与署名。
