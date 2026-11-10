# Update an application using the old API names / 更新使用旧接口名的应用

For applications written against `watche_hw_*`. Current development-preview APIs
use `watcher_hw_*`; old aliases are not provided. The rename does not change the
MCU (paired microcontroller) protocol or board branding. Event-loss and status
handling have separate behavior changes, described below.

本页面向仍使用 `watche_hw_*` 的应用。当前开发预览统一使用 `watcher_hw_*`，不保留旧名别名。
改名本身不改变配套微控制器通信协议或产品名称；丢事件及状态处理另有行为变化，必须同时检查。

## 1. Update names and rebuild / 改名并重新构建

| Before / 原名称 | Now / 新名称 |
| --- | --- |
| `watche_hw_{core,body,camera,audio,display}` components | `watcher_hw_{core,body,camera,audio,display}` |
| `watche_hw_body.h` and other hardware headers / 硬件头文件 | `watcher_hw_body.h` and matching headers / 对应新头文件 |
| `watche_hw_*` functions/types / 函数与类型 | `watcher_hw_*` |
| `WATCHE_HW_*` constants / 常量 | `WATCHER_HW_*` |
| `watche_hw_check_idf()` | `watcher_hw_check_idf()` |
| `watche_hw_{body,head,robot}.bin` outputs / 输出文件 | `watcher_hw_{body,head,robot}.bin` |

1. Pin the updated SDK revision with its matching examples. Update includes,
   functions, types, constants, CMake component dependencies and the top-level
   IDF-version check. Use ESP-IDF 6.0.2.
2. From **your application's project directory**, use a new build directory:

先固定新版 SDK 与对应示例，修改头文件引用、函数、类型、常量、CMake 依赖及顶层版本检查。
激活 ESP-IDF 6.0.2，在**你自己的应用工程目录**用新目录构建：

```sh
idf.py -B build-watcher build
```

Expected: the application compiles with the new names and produces a new binary.
Do not rename an old binary or hand-edit generated CMake/flash files.
Example directories `body`, `head`, `robot` and existing developer-script names/
parameters remain unchanged. `watcher_sdk`, an interface requiring official
services, is separate from this hardware API rename.

预期应用使用新名称编译并生成新固件，不能给旧固件改名或手改生成文件。示例目录与开发脚本
名称、参数不变；依赖官方服务的另一套 `watcher_sdk` 接口不属于本次改名。

## 2. Handle lost events and status / 处理丢事件与状态

An overflow means the event queue lost information. On `WATCHER_HW_EVENT_OVERFLOW`
(payload: `watcher_hw_body_event_loss_t`), cancel **all pending application actions**.
Body controls stay locked even after HELLO (the connection handshake).
Do not resume from a cached LINK READY or a drained FIFO (arrival-order event queue).
Query status, then recover outside event dispatch/callbacks: close/init, resubscribe,
wait for a fresh READY and obtain a new user action. A best-effort stop submission
is not physical-stop confirmation.

溢出表示事件队列丢失信息。收到上述事件后取消**全部待执行动作**；重新握手或读空队列都
不会解除故障，不能使用缓存的 LINK READY。查询状态，在事件分发与回调外显式关闭并初始化、
重新订阅，等待新的 READY 与用户操作。提交停止命令不证明机械已停。

Camera status now also reports faults from the connected device. For every API,
`status()` returning `ESP_OK` means the query succeeded, not that the device is READY;
inspect `state` and `last_error`. See the [API guides](README.md) and
[original correction record](../history/AUDIT.md).

相机状态也会报告连接设备的故障；`status()` 成功不等于就绪，仍需检查 `state` 和 `last_error`。
具体见接口指南和原修正记录。

## 3. Verify before using hardware / 使用硬件前验证

Run [software tests](testing.md), then follow [setup, backups and recovery](getting-started.md)
before any flashing. Use generated flash arguments or the documented example flash command.
Read [servo safety](servo-open-loop.md) before moving the body.
Successful builds establish source consistency, not physical sound, image or motion quality.
[Historical results](../history/VALIDATION.md) retain the old tested names and hashes.

先运行[软件测试](testing.md)，烧录前完成[上手、备份与恢复准备](getting-started_zh.md)，
使用构建生成的参数或示例规定命令；运动前阅读[舵机安全](servo-open-loop_zh.md)。
构建通过不等于声音、画面或机械验收，历史记录保留当时的固件名称和哈希。
