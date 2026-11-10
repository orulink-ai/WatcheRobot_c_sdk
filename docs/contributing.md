# Make a change / 贡献指南

For contributors fixing bugs, adding features or improving documentation in this
standalone public SDK. The result should be a focused pull request (PR) with real
validation results. Do not export private sources or change the old product repository.
本页供修复问题、增加功能或改进文档的贡献者使用，目标是提交范围清楚、附真实验证结果的 PR；
不导出私有源码，不顺带修改旧产品仓库。

## 1. Prepare a working branch / 准备工作分支

Install Git. Firmware work also needs activated ESP-IDF **6.0.2** and ESP32-S3 tools:
[setup](getting-started.md) / [中文上手](getting-started_zh.md).
Documentation-only changes do not need ESP-IDF.
先安装 Git；涉及固件另需按上手指南准备开发环境。纯文档修改不需要 ESP-IDF。

For a new checkout, run in a terminal:
新克隆可在终端执行：

```sh
git clone https://github.com/orulink-ai/WatcheRobot_c_sdk.git
cd WatcheRobot_c_sdk
git switch main
git pull --ff-only origin main
git status --short
git switch -c docs/describe-your-change
```

Expected: update succeeds, status is empty and a working branch is created.
Choose a descriptive `docs/`, `fix/` or `feat/` branch name.
For an existing checkout, check `git status --short` first; save unfinished work
before switching or pulling. Never discard another change automatically. If you
used a detached checkout for a reproducible build, create a working branch from
updated `main` before editing.

预期更新成功、工作区干净并创建分支；按实际目标使用 `docs/`、`fix/` 或 `feat/` 名称。
已有工作区先检查状态并保存未完成修改，不能自动丢弃。用于复现构建的 detached checkout
（未处于工作分支）不宜直接开发，请从更新后的 `main` 建分支。

## 2. Make and check the change / 修改并检查

- Keep English and Chinese user guides aligned. Explain who a command is for,
  where to run it, its prerequisites and expected result.
- Keep safety contracts, recovery links, attribution and licenses. Preserve the
  original facts in historical records; new tests need their own result.
- Follow [testing](testing.md): check docs/links for documentation; build affected
  examples and run relevant Debug/Release host tests for code. State any missing environment.
- Review from repository root:

中英文用户说明同步；命令写清对象、位置、前提及结果。保留安全约定、恢复链接、署名与许可证，
不改写历史测试事实。按测试指南执行与改动相符的检查，缺少环境就如实说明。在仓库根目录检查：

```sh
python3 tools/check_docs.py
git diff --check
git diff
```

Expected: documentation validation reports no errors, whitespace checks succeed
and the diff contains only your intended changes. Inventory hashes in `SOURCE.json`
are maintained separately; ask the maintainer to refresh affected output hashes.
预期文档检查无错误、格式检查通过、差异仅含目标修改。涉及来源清单内文件时，请维护者另行更新输出哈希。

## 3. Submit only intended files / 仅提交本次文件

Do not stage builds, `managed_components`, generated SDK configs, screenshots,
logs, device backups, credentials or newly exported private source.
For a change to the two READMEs, run from repository root:
不要暂存构建、下载依赖、生成配置、截图、日志、设备备份、凭据或新增导出的私有源码。
例如修改中英 README 后，在仓库根目录执行：

```sh
git add README.md README_zh.md
git diff --cached
git commit -m "docs: clarify SDK setup"
git push -u origin HEAD
```

Expected: a new commit is pushed to your working branch, not `main`.
Open a PR to **this repository's `main`**, describe the change, actual checks and
remaining limits, and wait for maintainer review before merging. If you cannot
push here, use a public fork. Delete a work branch only after its changes are merged.

预期提交推送到工作分支，而不是 `main`。向**本仓库 `main`** 提 PR，说明修改、实际验证及
未覆盖项，等待维护者审阅再合并；无推送权限则用公开 fork。确认修改合并后再删除工作分支。

See [source records](provenance.md), [tests](testing.md) and [documentation](README.md).
