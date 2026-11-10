# Work on this repository / 如何维护本仓库

Choose the task you need. All commands use this standalone public SDK checkout;
you do not need a private repository or the old materials checkout.
按目标进入对应指南；操作只需要当前公开 SDK 仓库，不需要私库或旧资料仓库。

| Goal / 目标 | Guide / 指南 | Expected result / 预期结果 |
| --- | --- | --- |
| Make a change / 修改代码或文档 | [Contributing / 贡献](contributing.md) | A focused branch and reviewed PR / 范围清晰的分支与经审阅的 PR |
| Find source history or license context / 查来源与许可证背景 | [Provenance / 来源](provenance.md) | Original source and current files are distinguishable / 分清原始来源与当前文件 |
| Check a change / 验证修改 | [Testing / 测试](testing.md) | Repeatable results tied to a revision / 可复现且对应具体版本的结果 |
| Prepare distribution packages / 准备分发包 | [Local packaging / 本地打包](registry-publishing.md) | Real archives and a clean build, not an upload / 真实归档和独立构建，不执行上传 |
| Build or use hardware / 构建与使用硬件 | [Documentation / 使用导航](README.md) | Find the relevant setup or API guide / 找到上手或接口指南 |

Keep changes on a working branch and submit a PR to this repository's `main`.
Record the checks actually run; use [historical records](../history/README.md) only
for background, not as a new test result.
请在工作分支修改并向本仓库 `main` 提交 PR。只记录本次实际运行的检查；历史记录仅供参考。
