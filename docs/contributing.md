# Contributing / 贡献指南

Work only on the standalone public SDK; do not export private sources or modify the old product repository as a side effect. / 仅维护独立公开 SDK，不额外导出内部源码，不顺带修改旧资料仓库。

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
- See [testing](testing.md) for executable checks and current evidence; workflow presence alone is not proof of a passing run.
- Stage only intended source/documentation files. Never stage `build*`,
  `managed_components`, generated SDK configurations, screenshots, logs, device
  backups, credentials or newly exported private source.

中英文用户说明同步更新；写清命令运行位置、前置条件和预期结果。检查链接和真实文件路径，
提交前执行 `git diff --check` 并审阅差异。代码改动应提供受影响示例构建与 Debug/Release
主机测试证据；纯文档改动不冒充固件或实机验收。测试入口与证据见 [testing](testing.md)，不把旧仓库结果或工作流文件存在当成当前 PR 结果。只暂存本次目标文件，
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


See [provenance](provenance.md), [testing](testing.md) and [documentation index](README.md).
