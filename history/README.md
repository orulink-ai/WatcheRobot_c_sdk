# Find earlier reviews and test results / 查阅历史审查与测试

Use these records to understand earlier fixes or compare results. Read the date,
source revision and firmware identity inside each record before applying a conclusion.
They describe the versions tested then, not acceptance of your current build.
本目录用于追溯问题和对比结果。阅读时先核对日期、源码版本和固件标识；历史结论不代表当前构建通过验收。

| Your question / 你想查什么 | Record / 记录 |
| --- | --- |
| Which API/runtime issues were reviewed and corrected? / 审查并修正过哪些接口或运行问题？ | [AUDIT](AUDIT.md) |
| How was the implementation reviewed? / 如何审查实现？ | [REVIEW](REVIEW.md) |
| Which usability issues were identified? / 发现过哪些易用性问题？ | [UX_REVIEW](UX_REVIEW.md) |
| What was tested and what remained? / 当时验证了什么、还缺什么？ | [VALIDATION](VALIDATION.md) |
| How was the public copy checked against its source? / 如何检查公开副本与来源一致？ | [SYNC_VALIDATION](SYNC_VALIDATION.md) |
| What earlier upstream results were retained? / 保留了哪些上游验证结果？ | [UPSTREAM_VALIDATION](UPSTREAM_VALIDATION.md) |

Original dates, names, commit IDs, hashes, counts and conclusions are preserved;
local Markdown paths were adjusted when records moved.
原日期、名称、提交、哈希、数量及结论保留，移动时仅调整本地 Markdown 链接。

For a new change, follow [testing](../docs/testing.md) and save new results against
its actual revision. For source and import hashes, see [provenance](../docs/provenance.md).
验证新修改请按测试指南记录新结果；来源与导入哈希的含义见来源说明。
