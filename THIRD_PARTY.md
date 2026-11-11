# 第三方代码与许可 / Third-party code and licenses

本仓库按代码职责组织目录，不按作者归属另建 `third_party/`。下表标明随仓库携带的第三方组件及本地适配；组件内的原许可证、文件署名和嵌套许可仍适用，本清单不替代它们。

## 仓库内的第三方组件 / Bundled components

版本取自各组件的 `idf_component.yml`，用于识别本地副本，**不代表与同版本上游逐字节一致或可以直接替换**。除明确列出的修订外，上游精确提交尚未记录；旧仓库导入来源见 [SOURCE.json](SOURCE.json)，它不是各第三方项目的原始提交证明。

| 本地目录 / Directory | 上游来源 / Upstream | 版本依据 / Version evidence | 许可 / License | 本地维护边界 / Local integration |
| --- | --- | --- | --- | --- |
| [`bsp/watche_robot/sensecap-watcher/`](bsp/watche_robot/sensecap-watcher) | [Seeed Studio SenseCAP-Watcher](https://github.com/Seeed-Studio/SenseCAP-Watcher)；头文件保留 Seeed 署名 | [清单](bsp/watche_robot/sensecap-watcher/idf_component.yml)：1.0.0 | [Apache-2.0](bsp/watche_robot/sensecap-watcher/license.txt) | WatcheRobot 板级集成；包含 IDF6 触控、旋钮清理、显示初始化和资源释放适配，不能直接换成上游板包。 |
| [`components/esp_lvgl_port/`](components/esp_lvgl_port) | [Espressif esp-bsp](https://github.com/espressif/esp-bsp/tree/master/components/esp_lvgl_port) | [清单](components/esp_lvgl_port/idf_component.yml)：1.4.0-custom.1 | Apache-2.0，见[源码 SPDX 声明](components/esp_lvgl_port/esp_lvgl_port.c#L1-L5) | 本地定制版本，含输入回调、DMA 暂存及关闭失败重试适配。 |
| [`components/esp_codec_dev/`](components/esp_codec_dev) | [Espressif esp-adf](https://github.com/espressif/esp-adf/tree/d2613ac466375f34711bf88ab49b5ed047b8df79/components/esp_codec_dev) | [清单](components/esp_codec_dev/idf_component.yml)：1.2.0，记录上游修订 `d2613ac466375f34711bf88ab49b5ed047b8df79` | [Apache-2.0](components/esp_codec_dev/LICENSE)，另含下述 MIT 子目录 | 使用仓库内驱动及构建接入；板级依赖通过 override 选择此副本，升级前核对音频适配。清单中的修订是来源记录，不是当前副本完全一致的声明。 |
| [`components/esp_io_expander_pca95xx_16bit/`](components/esp_io_expander_pca95xx_16bit) | Espressif 原始实现、Seeed 贡献；见[源码署名](components/esp_io_expander_pca95xx_16bit/esp_io_expander_pca95xx_16bit.c#L1-L7)及[清单上游链接](components/esp_io_expander_pca95xx_16bit/idf_component.yml) | 清单：1.0.0 | [Apache-2.0](components/esp_io_expander_pca95xx_16bit/license.txt) | 随板级组件携带的本地 IO 扩展驱动副本，不以组件同名认定可直接替换。 |
| [`components/sscma_client/`](components/sscma_client) | [Seeed Studio SenseCAP-Watcher](https://github.com/Seeed-Studio/SenseCAP-Watcher/tree/main/components/sscma_client) | [清单](components/sscma_client/idf_component.yml)：1.0.2 | [Apache-2.0](components/sscma_client/license.txt) | SSCMA 客户端本地副本，含命令和传感器响应解析及主机回归。其 README 是组件参考，不是当前 PTL 相机教程。 |
| [`components/media_lib_sal/`](components/media_lib_sal) | [Espressif esp-webrtc-solution](https://github.com/espressif/esp-webrtc-solution/tree/main/components/media_lib_sal) | [清单](components/media_lib_sal/idf_component.yml)：0.9.0 | [Espressif Modified MIT](components/media_lib_sal/LICENSE) | 媒体系统抽象层；**仅限结合 Espressif 产品使用，禁止为非 Espressif 产品再分发使用；不是普通 MIT。** 文件内原有许可声明同时保留。 |

### 嵌套代码与测试副本 / Nested code and test copies

- [`components/esp_codec_dev/device/zl38063/`](components/esp_codec_dev/device/zl38063)：包含 Microsemi 的 API/示例代码，保留其 [MIT 许可证](components/esp_codec_dev/device/zl38063/LICENSE.txt)与逐文件声明；不能用父组件 Apache-2.0 一概覆盖。
- [`iot_knob_0_1_4.fixture`](bsp/watche_robot/sensecap-watcher/test_support/host/iot_knob_0_1_4.fixture)：Espressif knob 0.1.4 源码测试副本，文件头保留 Apache-2.0 声明；用于验证本地清理补丁，不参与固件编译。
- 组件旁的 `test_support/host/` 是电脑端测试入口，可能包含项目新增测试，也可能引用第三方测试素材；目录存在不代表整个组件都是自研或都是未修改的上游代码。

## 构建时下载的依赖 / Build-time dependencies

ESP-IDF 框架及 Component Manager 获取的 LVGL、cJSON、显示/触控驱动、button、knob、led_strip、音频编解码等不在本仓库重复存放源码。实际启用范围和版本以以下文件为准，不在本页维护第二套版本表：

- 示例的依赖声明与锁文件，例如 [`hello_display/main/idf_component.yml`](examples/hello_display/main/idf_component.yml)、[`hello_display/dependencies.lock`](examples/hello_display/dependencies.lock)。其他示例使用各自的清单与锁文件。
- 本地组件自己的 `idf_component.yml`，以及[共享构建入口](examples/sdk.cmake)中的组件选择和链接适配。
- [本地打包工具](tools/package_components.py)定义的分发依赖及生成的 `release.json`；工具环境的 Python 依赖见 [requirements.txt](tools/packaging/requirements.txt)。

下载后的 `managed_components/` 和工具环境不提交到仓库。分发产物时仍需保留实际依赖的许可证；本地补丁不改变上游的许可条件。

## 素材与维护 / Assets and maintenance

- 产品图：[`docs/images/product/`](docs/images/product) 中三张 JPEG 摘自或宇连接《WatcheRobot 产品手册 V1.1》，是产品渲染图，归或宇连接所有，不是 SDK 实机测试照片。产品图和商标的权利不随代码 Apache-2.0 许可授予。
- 运动安全配图：[`hardware-check-motion-safety.png`](docs/images/hardware-check-motion-safety.png) 沿用[原公开示意图](https://github.com/orulink-ai/WatcheRobot-public/blob/eb78c212999374c9afd48de9c160c73991e646ae/docs/images/embedded-sdk/hardware-check-motion-safety.png)，是 LVGL 软件渲染界面，不是实物照片；本记录不额外授予素材许可。
- 语音样本：CC0 许可及来源见[素材说明](examples/common/assets/README.md)。

Product JPEGs come from Orulink's *WatcheRobot Product Manual V1.1*, are owned by Orulink, and are renders rather than device-test photographs. The motion-safety illustration is retained from the immutable public source linked above and is an LVGL software rendering, not a device photograph. Code licensing does not grant rights to product artwork or trademarks; these source records do not create a separate artwork license grant.

新增或替换第三方组件时，更新本清单并保留上游地址、可追溯版本/修订、原始许可和本地适配说明；不要因根目录已有 [LICENSE](LICENSE) 而删除组件自己的许可。未列入第三方表的项目代码不因“缺少独立 license 文件”自动证明为自研；发现额外来源时继续补录。

## English

Directories follow component responsibilities, not authorship. The table identifies bundled third-party code and locally maintained integration; manifest versions do not certify an unmodified upstream copy. Unrecorded exact upstream commits are explicitly left unknown. `SOURCE.json` tracks the old public-repository import, not a complete upstream authorship audit.

Retain each component's notices and nested licenses. In particular, **media_lib_sal uses Espressif Modified MIT with Espressif-product restrictions**, and Microsemi code under `esp_codec_dev/device/zl38063` has its own MIT license. The knob fixture retains its Apache-2.0 header. Host tests are not firmware and may be project additions beside third-party code.

Downloaded dependencies are defined by component/example manifests and each example's lock file, not a duplicate version table here. Review local patches before upgrading, preserve applicable licenses in distributed packages, and update this inventory when adding or replacing third-party code. Audio assets and product artwork have separate licensing boundaries.
