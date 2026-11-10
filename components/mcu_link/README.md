# 与机身控制芯片收发消息

负责让主芯片与机身控制芯片建立连接、发送命令并接收应答。只有维护底层通信或排查连接问题时才需要直接使用。

内部实现组件（internal implementation）。公开 SDK 入口为 [`watcher_hw_body`](../../bsp/watche_robot/watcher_hw_body/README.md)，应用不应直接另开链路。

## 接口与依赖

- 接口：[`mcu_link.h`](include/mcu_link.h)
- 依赖：ESP-IDF `driver`、`esp_timer` 和 `esp_driver_uart`。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

MCU 指机身控制芯片。通信协议规定消息的格式；分帧用于区分一条条消息，CRC 用于检测传输损坏，COBS 用于避免消息内容与分隔符混淆。公开机身接口已经负责读取消息，不要再启动第二个初始化或轮询者。维护升级使用的 UART 串口与运行通信共享；begin_ota 成功后的 finish/abort 必须由获得升级使用权的同一任务执行，不能从其他任务结束别人的升级。

许可见仓库 [LICENSE](../../LICENSE)；依赖保留各自许可证。
