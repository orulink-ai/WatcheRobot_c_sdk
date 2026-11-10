# 避免多个功能同时发出动作

在不同动作来源之间决定当前由谁发指令，例如人工控制与自动跟随不能同时争抢控制。维护多来源动作协调时使用。

内部实现组件（internal implementation）。公开 SDK 入口为 [`watcher_hw_body`](../../bsp/watche_robot/watcher_hw_body/README.md)。

## 接口与依赖

- 接口：[`motion_arbiter.h`](include/motion_arbiter.h)
- 依赖：FreeRTOS。
- 构建声明：[`CMakeLists.txt`](CMakeLists.txt)。

## 实现约束

这里的 owner（使用者）只是软件约定的当前控制方。获得控制权不表示电机已经停止，也不提供角度测量；释放控制权不是物理急停。公开机身接口打开时不要另行夺取底层控制。实际安全仍依赖运动空间隔离和人工断电。

许可见仓库 [LICENSE](../../LICENSE)；依赖保留各自许可证。
