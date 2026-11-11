# 在电脑上测试体检界面

运行这些测试可以检查体检界面的布局、触摸操作和软件绘制结果，不需要连接机器人或安装 ESP-IDF。

测试使用真实 LVGL 8.4.0，编译当前界面代码；仅替代电脑上不存在的 ESP 内存、显示锁、输入队列和图片释放接口。

## 在独立 C SDK 仓库运行

先安装 Git、CMake 3.20+ 和可用 C/C++ 编译器（Windows 使用已配置 MSVC 的开发者终端）。
若已有 LVGL 8.4.0 源码，
可在本目录执行下列命令；将占位符替换为源码绝对路径，含空格时保留引号：

```text
cmake -S . -B build "-DLVGL_SOURCE_DIR=<LVGL_SOURCE_ABSOLUTE_PATH>" -DCMAKE_BUILD_TYPE=Release -DHOST_WRITE_PPM=ON
cmake --build build --config Release --target check_view_tests --parallel
ctest --test-dir build -C Release --output-on-failure --no-tests=error
```

单配置生成器还应在 configure 时传 `-DCMAKE_BUILD_TYPE=Release`；Windows 可显式传 `-G "Visual Studio 17 2022" -A x64`。

固件 `main/idf_component.yml` / `dependencies.lock` 使用 **LVGL 8.4.0**，主机测试也使用该版本。

没有 LVGL 源码时，在 **WatcheRobot_c_sdk 仓库根目录**执行下列准备和回归命令。
依赖放在相邻目录，避免混入提交；示例目标目录必须尚不存在，否则先检查原目录而非覆盖。
`$PWD` 写法在 PowerShell 与 macOS/Linux Shell 均可使用。以下提交对应 LVGL 8.4.0；完整检查说明见[贡献指南](../../../../CONTRIBUTING.md#checks--修改后检查)。

```text
git clone --no-checkout https://github.com/lvgl/lvgl.git ../WatcheRobot-c-sdk-lvgl
git -C ../WatcheRobot-c-sdk-lvgl checkout --detach 4495f428630cc1741bd8bfd977f080e8460e8e8d
cmake -S examples/hardware_check/test_support/host -B ../WatcheRobot-c-sdk-host-build-release -DLVGL_SOURCE_DIR="$PWD/../WatcheRobot-c-sdk-lvgl" -DCMAKE_BUILD_TYPE=Release -DHOST_WRITE_PPM=ON
cmake --build ../WatcheRobot-c-sdk-host-build-release --config Release --target check_view_tests --parallel
ctest --test-dir ../WatcheRobot-c-sdk-host-build-release -C Release --output-on-failure --no-tests=error
```

构建产生 `check_view_tests`，CTest 应报告 0 失败。每条命令成功后再执行下一条。
可归档构建目录中的 `snapshots/*.ppm` 与 `Testing/Temporary/LastTest.log`。
Debug 验证使用单独的 `../WatcheRobot-c-sdk-host-build-debug` 目录，并将配置值改为 Debug。

`lv_conf.h` 开启 RGB565、snapshot 和 Montserrat 14/16/18/20/24/48。所有测试源通过 `#ifdef NDEBUG / #error` 防止断言失效；MSVC 用 `/UNDEBUG`，其他编译器用 `-UNDEBUG`，Release 同样执行断言。新增测试和 mock 目标使用 `/W4 /WX`（其他编译器 `-Wall -Wextra -Werror`）；生产代码与 LVGL 是独立依赖目标，保留警告而不要求上游库零警告。注意字体名的 px 大小不等于其 `line_height`（18px 的行高实际为 21）。

## 验证合同

| 场景 | 实际检查 |
| --- | --- |
| config | 真库版本、RGB565、6 个字体的实际 glyph、412×412 snapshot |
| geometry_oracle | 独立椭圆/圆屏解析 oracle 与生产 hit/span API 全像素一致，越界和中央空白无命中 |
| nav_geometry | 两个 178×124 区域在 (0,288)/(234,288)，真实 `lv_obj_hit_test` 和 `LV_EVENT_HIT_TEST` 全像素一致；输入驱动实际点击 |
| nav_pixels | 隐藏导航字形后对 y288..411 所有像素核对左灰、右浅绿与背景；圆屏外/弧外/中央空白无绘制 |
| labels | 左右中心 (108,340)/(304,340)，常态 18px，主动作深字；Not OK/Next 同中心 |
| content/status | 标题 y80/中心 x206，常态 visual 中心 (206,188)，实际控制器状态 y260、bottom≤280，互不重叠 |
| running_content | 各步骤运行时所有可见内容不与 status 重叠，包括 Screen 第三个触点 |
| report/detail_tail | 两页报告和所有详情页的真实行/字形边界，41px 行高；短列表在 y114..277 的 164px 区间居中；Lights 末页两行单独回归，无标题/导航重叠 |
| stop | STOP 20px、红色/按下深红、真实点击产生右意图；取消等待仍红且 disabled，返回 idle 恢复常态 |
| stopping | STOP_TEST 保持 RUNNING，新增 stopping 只增加右侧 disable 条件；仍为红 STOP，输入 model.status 为 Stop requested; waiting，显示文案为 Stopping \| waiting for result，无重复点击入队；ACK 后恢复 review 的 Next |
| pressed/native_input | 普通按下仍浅绿、释放恢复；弧内滑到弧外/空白/圆屏外无误触，按住后变 disabled 无入队，解除禁用后各产生一次意图 |
| release_outside | 按下右区后，下一个 pointer 样本直接在弧外/中央空白/圆屏外 release；计数断言恰好两个样本，不能插入 pressing 移动样本 |
| release_disabled | 按住后原地 render 成 disabled，然后直接 release；render 期间不调用 timer，不允许中间 pressing 样本掩盖缺陷；覆盖 setting_pending、cancelling、stopping |
| busy | 所有步骤 running/cancelling、setting_pending、welcome 的禁用状态与真实输入，禁用浅灰，音量 slider 禁用 |
| photo/live_image | 移交所有权，thumbnail 224×126，放大 320×180；真实变换和 snapshot 图像像素边界中心 (206,188)，不碰 eyebrow/状态/导航；放大隐藏大标题，保留指定 eyebrow，返回与 Next 意图合同不变 |
| stale_image | 无图、跨 attempt、换步骤不得假放大；本轮图替换释放旧数据，Together 仍允许同轮 retained 图 |
| image_arrival_attempt | shown 仍为旧 attempt，直接调用固定新 API `check_view_image(image, new_attempt)`，随后 render 新 attempt 必须显示新照片；迟到旧 attempt 不能显示 |

生产 geometry 的独立 oracle 使用像素中心：圆心 (205.5,205.5)、半径 206；左椭圆 rx112/ry100，右侧镜像 `411-x`，左区域面积 11043 像素。oracle 不调用生产 predicate 来推导期望值。

图像源使用已解码的 320×180 RGB565 洋红色数据。thumbnail 由真实整数 zoom 和软件采样得到，允许 1px 采样量化边缘；放大 1:1 为 (46,98)..(365,277)。原始 LVGL img 对象仍可能是源图尺寸，测试同时检查真实 transformed area 和 snapshot 可见像素，避免把源图对象尺寸误当作缩略图尺寸。

## 软件截图

`HOST_WRITE_PPM=ON` 时测试程序直接写 `build/snapshots/<scenario>.ppm`，失败也会保存当时画面。也可运行 `build/Release/check_view_tests photo --ppm <文件路径>`（单配置生成器的程序在 build 根目录）。构建产物和 PPM 均在本目录忽略，不提交。
