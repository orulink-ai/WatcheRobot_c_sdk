# Provenance and public scope / 来源与公开范围

## Scope / 范围

This is the standalone public **WatcheRobot C SDK** repository. Build and usage
commands run from its root unless a guide explicitly names a different directory.
The repository contains hardware SDK components and four independent ESP-IDF
examples, not the official ESP32 application, STM32/Himax implementations, cloud
services, models or production firmware packages.

这里是独立的 **WatcheRobot C SDK** 公开仓库。除非文档明确指定其他位置，构建与使用
命令均从本仓库根目录执行。只维护现有公开硬件 SDK 和四个独立示例，不额外导出内部源码。
官方固件下载、烧录工具和 Python SDK 是外部产品资料，不要求克隆它们才能构建本 SDK。

- [English setup and safety](getting-started.md)
- [中文上手与安全说明](getting-started_zh.md)
- [Python SDK repository / Python SDK 仓库](https://github.com/orulink-ai/WatcheRobot_python_sdk)
- [Official flashing / 官方烧录与恢复](https://wiki.orulink.ai/docs/flashing)

Existing hardware-check preview binaries remain in their original external Release.
They are not this repository's Releases and must not be assumed to match an arbitrary
C SDK commit. Follow that Release's own source/manifest/hashes, and stop before
flashing if paired firmware or a complete recovery bundle cannot be verified.

现有体检预览固件仍在外部原 Release，不是本仓库的发布，也不自动对应本仓库任意提交。
必须按该 Release 的来源、清单及哈希核对，配套固件或完整恢复包不明确时停止烧录。

## Import baseline and file hashes / 导入基线与文件哈希

The initial public import commit is
[`85c6af84c93db63db335d4b93f2a114ba66cd7f1`](https://github.com/orulink-ai/WatcheRobot_c_sdk/commit/85c6af84c93db63db335d4b93f2a114ba66cd7f1).
Its entire Git tree exactly matches the already-public `firmware/sdk` subtree at
[the original materials commit](https://github.com/orulink-ai/WatcheRobot-public/tree/eb78c212999374c9afd48de9c160c73991e646ae/firmware/sdk).
This is provenance, **not an instruction to clone the old repository**. No private
history or additional upstream files were imported. The initial import still has
old documentation paths; use a reviewed documentation-adapted revision for current
instructions.

首次导入提交与原资料仓库指定公开提交中的 SDK 子树完全一致。旧链接仅用于来源追溯，
不是当前克隆入口；未迁入私库历史或额外源码。首次导入文档尚有旧路径，当前操作应使用
经审阅、完成文档适配的版本。

[`SOURCE.json`](../SOURCE.json) records the original allowlisted upstream paths,
immutable upstream commit and source-file hashes. Its `sha256` fields describe
tracked output files, not a signed release manifest or build/device proof. When
repository documentation changes a listed output file, retain `source_sha256`,
record the original imported output hash/transform, update that file's output hash
and describe the documentation-only transform. Do not rewrite upstream source paths,
hashes or historical acceptance claims to pretend they originated here.
Public-only files absent from that original inventory remain tracked by Git.
The existing public software-rendered illustration at
`docs/images/hardware-check-motion-safety.png` was copied without modification
from [the original public image](https://github.com/orulink-ai/WatcheRobot-public/blob/eb78c212999374c9afd48de9c160c73991e646ae/docs/images/embedded-sdk/hardware-check-motion-safety.png) in the same original
materials commit. Its Git blob is `214f26b9eb254164c4f6ae15ead3a11d15658f36`.
It is documentation artwork, not a robot photograph or newly exported SDK source.

`SOURCE.json` 中上游路径、提交与 `source_sha256` 是原始来源记录，不能为消除旧字符串而改写。
`sha256` 表示清单内文件的输出哈希，不是签名发布清单或构建／实机证明。修改清单覆盖的
文档时保留原导入输出哈希与转换说明，更新当前输出哈希并注明文档适配；未列入原导出清单
的公开文件由 Git 跟踪。当前未附带历史导出工具，也不需要访问内部上游才能构建。
体检指南的配图从同一原公开提交原样迁入，避免读取文档还依赖旧仓库图片；
它是既有的软件渲染示意，不是实机照片，也不是额外导出的源码。

Historical records (`history/VALIDATION.md`, `history/SYNC_VALIDATION.md`, `history/AUDIT.md`, `history/REVIEW.md`,
`history/UX_REVIEW.md`, and `history/UPSTREAM_VALIDATION.md`) retain their original dates,
results, old repository references, names and firmware hashes. Design/product
records also describe upstream prototypes that are not shipped in this repository.
Preserving those facts is intentional; it does not claim fresh acceptance or an
installed test environment. Dependency READMEs describe upstream libraries, not
extra bundled applications; retain their attribution and licenses.

历史验收／审查保留原日期、结果、仓库引用、命名和固件哈希；设计／产品说明中的上游网页
原型不随本仓库交付。第三方 README 介绍的是各自组件，不表示本 SDK 附带其测试应用；
版权与许可证保持不变。本次文档整理不升级接口、依赖或固件，不触发设备操作或生产发布。

Current paths are indexed in [history](../history/README.md) and [design](design/README.md). The source inventory must distinguish immutable upstream source paths/hashes, original imported destination/hash, and current destination/hash after a documentation move. Neither this page nor SOURCE.json is a signed release or hardware certificate.
