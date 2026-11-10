# Repository workflow and provenance / 仓库开发流程与来源

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

## Before making changes / 修改前

Install Git. For firmware builds, install and activate ESP-IDF **6.0.2** with ESP32-S3
tools as described in the setup guide. Documentation-only edits do not require
ESP-IDF. Clone this repository in a new terminal and work from its root:

先安装 Git；构建固件另需按上手指南安装并激活 ESP-IDF **6.0.2** 与 ESP32-S3 工具。
纯文档修改不需要 IDF。在新终端执行以下命令，之后保持在仓库根目录：

```sh
git clone https://github.com/orulink-ai/WatcheRobot_c_sdk.git
cd WatcheRobot_c_sdk
git switch main
git pull --ff-only origin main
git status --short
git switch -c docs/describe-your-change
```

Expected: the pull fast-forwards or is already up to date, status is empty, and a new
branch is created. The branch name is an example; choose a descriptive `docs/`,
`fix/` or `feat/` name. For an existing checkout, start with `git status --short`.
If it is not clean, save your work before switching or pulling; never discard it
automatically. A detached checkout used for reproducible builds is not a working
branch: create your branch from updated `main` before editing.

预期拉取成功、状态为空并创建分支。示例分支名请按实际修改命名，可用 `docs/`、`fix/`、
`feat/` 前缀。已有工作区先检查状态；有未提交修改时先保存，不自动覆盖或清理。
用于复现构建的 detached checkout 不是开发分支，开发应从更新后的 `main` 建分支。

## Validate, commit and open a PR / 验证、提交与 PR

- Update English and Chinese user-facing guides together; state each command's
  working directory, prerequisites and expected result. Use repository-relative
  paths for local SDK files and explicit public URLs for external products.
- Keep safety, licensing and preview limits intact. Never replace historical test
  results with inferred results for a new revision.
- Check every changed Markdown link, referenced source path and example command.
  Review `git diff --check` and `git diff` before committing.
- For runtime/build changes, build all affected examples using the pinned IDF;
  run relevant host tests in Debug and Release. The [LVGL host guide](../examples/hardware_check/test_support/host/README.md)
  provides one concrete host suite. Record actual results and any missing environment.
- This repository currently has **no CI workflow or root `tools/tests` / npm test
  entry point**. Do not claim old-repository CI passed for a new PR. Establishing
  standalone CI is separate work; until then, provide reproducible local evidence.
- Stage only intended source/documentation files. Never stage `build*`,
  `managed_components`, generated SDK configurations, screenshots, logs, device
  backups, credentials or newly exported private source.

中英文用户说明同步更新；写清命令运行位置、前置条件和预期结果。检查链接和真实文件路径，
提交前执行 `git diff --check` 并审阅差异。代码改动应提供受影响示例构建与 Debug/Release
主机测试证据；纯文档改动不冒充固件或实机验收。本仓库暂未迁入独立 CI，也没有根目录
`tools/tests` 或 npm 测试入口；不把旧仓库结果当成当前 PR 结果。只暂存本次目标文件，
不要提交构建产物、下载依赖、生成配置、日志、设备备份或凭据。

For example, after changing only the Chinese README, run from repository root:

例如仅修改中文 README 后，在仓库根目录执行：

```sh
git diff --check
git diff -- README_zh.md
git add README_zh.md
git diff --cached
git commit -m "docs: clarify standalone SDK setup"
git push -u origin HEAD
```

Expected: a new commit is pushed to your branch, not `main`. On GitHub, open a PR
from that branch to **this repository's `main`**. Explain the scope, actual validation
and remaining limitations. Wait for review and maintainer approval before merging;
do not push directly to `main` or update the product-materials repository as part
of an unrelated SDK change. Without push permission, use a public fork and open a
PR to the same base. Remove the work branch only after the PR is merged and its
latest changes are accounted for.

预期新提交推送到当前工作分支，而不是 `main`。在 GitHub 创建到**本仓库 `main`** 的 PR，
说明范围、真实验证及未覆盖项，审阅和维护者确认后再合并。不直推主分支，不顺带修改
旧资料仓库。无推送权限时使用公开 fork 提交 PR；合并并确认无遗漏后再清理工作分支。

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
from `docs/images/embedded-sdk/hardware-check-motion-safety.png` in the same original
materials commit. Its Git blob is `214f26b9eb254164c4f6ae15ead3a11d15658f36`.
It is documentation artwork, not a robot photograph or newly exported SDK source.

`SOURCE.json` 中上游路径、提交与 `source_sha256` 是原始来源记录，不能为消除旧字符串而改写。
`sha256` 表示清单内文件的输出哈希，不是签名发布清单或构建／实机证明。修改清单覆盖的
文档时保留原导入输出哈希与转换说明，更新当前输出哈希并注明文档适配；未列入原导出清单
的公开文件由 Git 跟踪。当前未附带历史导出工具，也不需要访问内部上游才能构建。
体检指南的配图从同一原公开提交原样迁入，避免读取文档还依赖旧仓库图片；
它是既有的软件渲染示意，不是实机照片，也不是额外导出的源码。

Historical records (`VALIDATION.md`, `SYNC_VALIDATION.md`, `AUDIT.md`, `REVIEW.md`,
`UX_REVIEW.md`, and `history/UPSTREAM_VALIDATION.md`) retain their original dates,
results, old repository references, names and firmware hashes. Design/product
records also describe upstream prototypes that are not shipped in this repository.
Preserving those facts is intentional; it does not claim fresh acceptance or an
installed test environment. Dependency READMEs describe upstream libraries, not
extra bundled applications; retain their attribution and licenses.

历史验收／审查保留原日期、结果、仓库引用、命名和固件哈希；设计／产品说明中的上游网页
原型不随本仓库交付。第三方 README 介绍的是各自组件，不表示本 SDK 附带其测试应用；
版权与许可证保持不变。本次文档整理不升级接口、依赖或固件，不触发设备操作或生产发布。
