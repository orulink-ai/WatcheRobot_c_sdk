# Trace sources and releases / 查源码与发布来源

For developers checking where files came from, and maintainers preparing a source
or firmware release. Start here when you need to distinguish the original import,
current edits and an external firmware download.
本页供核对文件来源及准备发布的人使用，帮助区分首次导入、当前修改和外部固件下载。

## What this checkout provides / 本仓库提供什么

The standalone **WatcheRobot C SDK** contains hardware APIs and four independent
ESP-IDF examples. Build from its own root; no private or old-materials checkout is
needed. The official product application, STM32/Himax implementations, cloud
services, models and production firmware bundles are not supplied here.

本仓库提供硬件接口和四个独立 ESP-IDF 示例，可直接在根目录构建，不依赖私库或旧资料仓库。
不提供官方产品应用、STM32/Himax 实现、云服务、模型或生产固件包。

- Build, backups and recovery / 构建、备份与恢复：[English](../examples/README.md) · [中文](../examples/README.md)
- Official flashing and recovery / 官方烧录与恢复：<https://wiki.orulink.ai/docs/flashing>
- Separate Python SDK / 独立 Python SDK：<https://github.com/orulink-ai/WatcheRobot_python_sdk>

External hardware-check preview binaries stay in their original Release; they
are not releases of this repository and do not automatically match your checkout.
Before flashing, match that Release's source, manifest and hashes. Stop if paired
firmware compatibility or a complete official recovery bundle cannot be verified.

外部体检预览固件仍归原 Release，不是本仓库发布，也不自动对应当前版本。烧录前核对该
Release 的源码、清单与哈希；配套兼容性或完整官方恢复包无法核实时停止操作。

## Check the original import / 核对首次导入

The initial public commit
[`85c6af84c93db63db335d4b93f2a114ba66cd7f1`](https://github.com/orulink-ai/WatcheRobot_c_sdk/commit/85c6af84c93db63db335d4b93f2a114ba66cd7f1)
has the same Git tree as the public
[`firmware/sdk` subtree at the original materials commit](https://github.com/orulink-ai/WatcheRobot-public/tree/eb78c212999374c9afd48de9c160c73991e646ae/firmware/sdk).
No private history or additional upstream files were imported. That first commit
still uses old documentation paths; use a reviewed documentation-adapted revision
for current instructions. The old-repository link is for comparison, not setup.

首次导入与链接中的原公开 SDK 子树完全一致，未迁入私有历史或额外源码。首次导入仍有旧文档
路径，当前操作请使用经审阅、完成文档适配的版本；旧仓库链接只供追溯，不是安装步骤。

## Read or update file hashes / 阅读与维护文件哈希

A **hash** is a file-content fingerprint. [`SOURCE.json`](../SOURCE.json) records
allowlisted upstream files, their immutable source commit/paths and source hashes.
Its output `sha256` checks the listed current file bytes; it is not a signed
release manifest or proof of a build/device test.

哈希是文件内容的指纹。`SOURCE.json` 保存允许导出的上游文件、固定提交、路径与来源哈希；
输出 `sha256` 用于核对当前文件，不是签名发布清单或构建、实机证明。

When documentation moves or changes, the inventory maintainer should:
文档移动或修改后，由清单维护者：

1. Retain upstream source paths and `source_sha256` unchanged.
   保留上游来源路径及 `source_sha256`。
2. Retain the original imported destination/output hash and describe the transformation.
   保留最初导入目标、输出哈希并说明转换。
3. Record the current destination and compute its output hash from actual bytes.
   记录当前目标路径，根据真实文件计算输出哈希。
4. Run `python3 tools/check_docs.py --check-source` from repository root.
   在仓库根目录执行该检查；预期路径、链接与当前文件哈希均匹配。

Public files absent from the original inventory remain tracked by Git. No historical
export tool or access to private upstream code is needed to build the SDK.
原清单未覆盖的公开文件由 Git 跟踪；构建不需要历史导出工具或私有上游访问权限。

## Images, history and licenses / 图片、历史与许可证

`docs/images/hardware-check-motion-safety.png` was copied unchanged from the
[original public image](https://github.com/orulink-ai/WatcheRobot-public/blob/eb78c212999374c9afd48de9c160c73991e646ae/docs/images/embedded-sdk/hardware-check-motion-safety.png)
at the same materials commit. Its Git blob is
`214f26b9eb254164c4f6ae15ead3a11d15658f36`. It is software-rendered artwork, not a robot photograph.
体检配图来自同一原公开提交，保持原样；上述 Git blob 用于追溯，它是软件渲染示意而非实拍。

The product overview uses selected hardware facts and three product renders from
Orulink's product manual V1.1 (2026-11-08), supplied by the product owner for this
README. See [product-image attribution and hashes](images/product/README.md).
The internal manual and its other attachments were not copied into this repository.
产品概述另按负责人提供的产品手册摘取必要硬件信息及三张外观图；来源与校验值见链接，
未导出内部手册全文或其他附件。产品规格与 SDK 实际支持范围分别说明。

[Historical records](../history/README.md) retain original dates, test results,
names, repository references and firmware hashes. [Design records](design/README.md)
also describe prototypes not shipped here. Dependency READMEs describe their own
upstream libraries; preserve their attribution and license files.

历史记录保留原日期、测试结论、名称、仓库引用和固件哈希；设计记录包含未交付的原型。
依赖 README 介绍各自上游库，不代表本 SDK 提供额外应用；原署名及许可证应保留。

For current executed checks, see [verification](verification.md); for preparing a
new release, see [local packaging](development.md#packaging).
当前执行结果见验证记录；准备分发包见本地打包指南。
