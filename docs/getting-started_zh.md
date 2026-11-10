[English](getting-started.md) | 简体中文

# C SDK 上手指南

为机器人 ESP32-S3 编写应用，体验拍照、录音播放和触摸灯光。不需要官方应用源码、Python SDK、
服务端、SD 卡或模型。在电脑上基于现有固件开发，请使用独立的 [Python SDK](https://github.com/orulink-ai/WatcheRobot_python_sdk)。
**当前为开发预览，完整配对实机与官方恢复验收仍未完成。**

## 1. 安装工具并构建

安装 Git 与 [ESP-IDF 6.0.2（含 ESP32-S3 工具）](https://docs.espressif.com/projects/esp-idf/zh_CN/v6.0.2/esp32s3/get-started/index.html)。
每个新终端都要激活 IDF：Linux/macOS 加载实际安装目录下的 `export.sh`，Windows 使用
ESP-IDF PowerShell 终端。`idf.py --version` 必须显示 6.0.2，构建会拒绝其他版本。

```sh
git clone https://github.com/orulink-ai/WatcheRobot_c_sdk.git
cd WatcheRobot_c_sdk
idf.py --version
idf.py -C examples/robot build
```

**后续命令均在本仓库根目录、已激活 IDF 的终端执行。**
下载依赖需要网络。预期生成 `examples/robot/build/watcher_hw_robot.bin`、bootloader、分区表和烧录参数。
构建不会写入设备，也不证明实机功能。失败时先解决报错，再继续。反馈问题请附上
`git rev-parse HEAD`、`idf.py --version` 和错误日志。

## 2. 选择要体验的功能

| 目标 | 工程名 | 修改文件 |
| --- | --- | --- |
| 触摸控制身体灯光 | `body` | `examples/body/main/app_main.c` |
| 拍照、录音播放和屏幕操作 | `head` | `examples/head/main/app_main.c` |
| 组合以上功能 | `robot` | `examples/robot/main/app_main.c` |
| 引导式硬件体检 | `hardware_check` | `examples/hardware_check/main/app_main.c` |

将命令中的 `robot` 换成所选工程。全部示例选择 ESP32-S3、16 MB flash 和自定义分区。
head/robot/hardware_check 启用 80 MHz 八线 PSRAM 与 LVGL 8.4.0，body 默认不启用 PSRAM。
每个工程的配置、分区和依赖清单需配套保留，见[示例说明](../examples/README.md)和[依赖说明](dependencies.md)。

修改 `app_main.c` 后重新构建。body 和 robot 示例收到触摸时请求设置灯光、松手时请求停止，
不会自动启动舵机运动。

## 3. 安全检查——任何烧录或运动之前

- **兼容固件：**身体控制需要支持运动、灯光、触摸的兼容 STM32 固件；摄像需要匹配的
  Himax **PTL** 固件。记录板卡、固件版本与镜像哈希。产品 Release、文件名、握手成功或构建成功
  都不能证明兼容。配套未经核实，先停止并向维护者索取兼容记录。
- **备份与恢复：**准备已核实的完整官方恢复包，备份所需设置和数据。首次完整自定义烧录会覆盖
  官方 `agentcfg` **0x12000–0x20000** 区域。回到官方固件必须**完整恢复**，不能只刷应用。
  仅有备份无法恢复官方分区布局。缺少恢复包时停止。
- **正确端口：**ESP32 接口为 **SERIAL-B**，仍须在设备管理器或 `/dev/serial/by-id/` 核实实际端口。
  不要使用 STM32/Himax 端口；关闭其他串口监视器。
- **运动：**应用**不能读取舵机实际转到的角度**。实际起点未知，即使要求转到 X90/Y120 参考位置，也可能从另一端移动很远。
  清空整个行程，保持人工断电可用。ACK/DONE 和软件 STOP 不证明实际位置或机械停止。
  断连后 ESP32 无法保证停止命令到达，仍需 STM32 安全机制和操作者断电。运动检查前阅读
  [运动安全](servo-open-loop_zh.md)。

首次准备或恢复，使用已核实的整套镜像并遵循[官方烧录指南](https://wiki.orulink.ai/docs/flashing)；
该指南不是日常更新自定义应用的入口。SDK 不提供未经验证的 STM32/Himax 替换镜像。

## 4. 烧录并观察

完成上述检查后，将 `<PORT>` 替换为本机已核实的 **ESP32 端口**，如实际识别到的
`COM7` 或 `/dev/ttyACM0`：

```sh
idf.py -C examples/robot -p <PORT> flash
idf.py -C examples/robot -p <PORT> monitor
```

`flash` 写入自定义 ESP32 bootloader、分区表和应用，不刷 STM32/Himax。
**不要执行 `erase-flash`，不要猜偏移，不要把应用单独 `.bin` 从 `0x0` 写入。**
预期 esptool 写入校验成功，随后 robot 示例显示拍照、音频操作界面，并记录身体初始化和触摸事件。
尝试 Photo，再 Record、Play，亲自检查照片和声音。触摸身体时请求绿灯，松手时请求停止。
控件禁用不算通过。用 **Ctrl+]** 退出 monitor。

若选 `hardware_check`，屏幕应显示 **Hardware check**，日志包含 `Hardware check v2 | curved zones`。
按 [26 项操作指南](hardware-check_zh.md)检查。结果只保存在 RAM，重启清空，应另行记录；未测不算通过。

后续仅更新应用时，**只有确认连接设备已经使用相同自定义分区布局**，才可执行
`idf.py -C examples/robot -p <PORT> app-flash`。本地文件相同不能证明设备布局相同。
设备布局未知或中途刷过官方固件时，重新完成安全检查，使用完整自定义 `flash`。

可选便捷脚本提供同样的 build/flash/monitor 操作：

```sh
bash examples/hardware-sdk.sh robot build
```

```powershell
./examples/hardware-sdk.ps1 robot build
```

支持 body/head/robot/hardware_check 和 build/flash/monitor；flash/monitor 必须以第三个参数传入真实端口。
脚本不会扫描端口、烧录配套芯片或擦除设备。

## 5. 恢复官方固件

停止自定义应用，关闭串口监视器。选择已核实的**完整官方**恢复包，按
[完整恢复流程](https://wiki.orulink.ai/docs/flashing#full)使用该包对应的准确端口和镜像。
恢复会替换自定义 ESP32 应用，也可能替换存储和配套固件。之后检查官方启动和配对。
返回 SDK 开发时重新构建、烧录自定义工程。恢复资产或来源不明时停止，不能猜偏移。

## 常见问题

- IDF 版本错误：在当前终端激活 6.0.2，不绕过版本检查。
- 缺少依赖：检查完整仓库、网络和工程依赖清单，不要引入官方应用源码。
- 身体未就绪或日志报告事件丢失：先停止操作，排查供电、线缆和兼容固件。不要反复触摸尝试解锁，
  不要自动重试旧动作；重连或清空待处理事件也不能解除这一故障。自行编写恢复逻辑时，
  取消待执行动作并按[身体 API 的完整恢复步骤](api/body.md)处理；重新动作必须由**新的用户操作**发起。
- 没有照片：核实 PTL 摄像头固件配套，保留超时或错误日志；没有图片不能通过。
- 没有声音：尝试 Test speaker 的 voice/tone。默认输出 90、上限 95；进度完成不证明可听。
  简单头部示例没有自动重试或动态关闭流程，不能再创建一个控制同一音频、摄像头的任务来恢复。

## 扩展应用时再看

音频操作交给同一任务；不要在硬件回调、中断或持有屏幕锁时调用阻塞音频函数。
摄像头回调图片需复制后留用，访问 LVGL 要加锁。精确接口与使用规则见 [API 指南](README.md)。
独立 ESP-IDF 工程可参考现有示例的 CMake、配置与[依赖说明](dependencies.md)，不能只复制头文件。
保留已知 SDK 版本以便复现；旧 `watche_hw_*` 应用见[迁移指南](migration.md)。

## 可选：预编译测试固件与验证记录

外部[硬件体检预览 Release](https://github.com/orulink-ai/WatcheRobot-public/releases/tag/hardware-check-preview-20261030)
不是官方整机稳定版，源码构建不需要先下载它。按照该 Release 的资产、来源/哈希和安装说明操作，
不要默认其二进制来自当前仓库版本。下载包需要 Python 3.10+ 和说明中的 esptool 依赖。
使用完整文件集及其文档指定偏移，不要把应用单独文件写入 `0x0`。资产缺失时联系维护者，不能找相似文件替代。
前述安全检查仍然适用。

软件测试不证明机械限位、停止时延、边缘触摸、图像/声音质量、反复关闭或长期组合运行稳定性。
见[测试与证据](testing.md)、[历史验收](../history/VALIDATION.md)及[来源说明](provenance.md)。
文档不是新完成的构建、烧录或实机验收结果。
