# 向机身灯光发送设置

把灯区、颜色、亮度和闪烁等效果转换成机身控制芯片可接收的请求。维护灯光行为或查看请求字段时阅读。

内部实现组件（internal implementation）。公开 SDK 入口为 [`watcher_hw_body`](../../sdk/watcher_hw_body/README.md)。

## 接口与依赖

- 接口：[`mcu_led_service.h`](include/mcu_led_service.h)
- 依赖：[`mcu_link`](../../protocols/mcu_link/README.md) 和 FreeRTOS。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

应用通过公开机身接口提交灯光请求，区域、模式、效果的真实枚举与字段在下方头文件。不要为灯光另外初始化或轮询通信连接。请求成功不代替实际观察灯光效果。

许可见仓库 [LICENSE](../../../LICENSE)；依赖保留各自许可证。
