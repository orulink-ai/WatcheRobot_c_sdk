# Local component packaging / 本地组件打包

Run commands from the repository root. / 以下命令在仓库根目录执行。

The SDK is **not published to ESP Component Registry**. This workflow generates local packages and
an independent compile/link project; it does not upload or authorize a namespace.
目前未上架乐鑫组件平台。以下仅供维护者验证分发包，不是用户安装方式，也不执行正式发布。

Use a reviewed public Git revision and a **new output directory outside the repository**.
The exporter reads tracked files from that revision, not working-tree edits. All 25 components use
one exact preview version; stable versions and upstream namespaces are refused.
`preview_test` is a local rehearsal label only. Install the pinned packaging requirements into a
Python virtual environment; set the example executable paths below to that environment if different.
使用经审阅的公开提交，输出必须在仓库外且此前不存在；本地命名空间不代表平台授权。

```sh
python3 -m venv /tmp/watcher-package-tools
/tmp/watcher-package-tools/bin/python -m pip install -r tools/packaging/requirements.txt
/tmp/watcher-package-tools/bin/python tools/package_components.py \
  --revision HEAD --namespace preview_test --version 0.1.0-preview.1 \
  --output /tmp/watcher-registry-rehearsal \
  --pack --compote /tmp/watcher-package-tools/bin/compote
```

Expected: 25 real archives, `release.json`, `archives.sha256.json` and `consumer/`. Compote **2.5.2**
has `component pack`, not `component lint`. On repeated runs choose a new output directory.
The consumer unpacks actual archives and uses project-internal path overrides; release manifests
must contain no local paths. Activate IDF 6.0.2 and build the generated project:
预期真实归档和独立工程生成成功；独立工程的内部路径覆盖不应泄漏到分发清单。激活 IDF 后执行：

```sh
idf.py -C /tmp/watcher-registry-rehearsal/consumer set-target esp32s3
idf.py -C /tmp/watcher-registry-rehearsal/consumer build
```

Expected: all five public headers and dependencies compile/link without a sibling source checkout.
The consumer does not initialize hardware. Local pack/build success is not Registry upload/install
or hardware acceptance. Any future release needs namespace approval, coordinated lower-level
packages, license review, clean builds and behavioral checks; do not publish only the five APIs.
预期不依赖原源码目录即可编译链接；测试入口不操作硬件。平台上传/安装与实机仍需独立验收。

Preserve local vendor source and nested licenses byte-for-byte. Generated-only adaptations include
the namespaced codec target, standalone touch/LED-strip fixes and deferred IDF6 linkage. Do not add
`MBEDTLS_DECLARE_PRIVATE_IDENTIFIERS=1`: its generated definition conflicts with mbedTLS4.
Keep source-build camera flags consistent. The exporter rejects tracked symlinks and known secrets,
excludes tests/builds/caches/downloaded dependencies, and never overwrites existing nested licenses.
Generated README links escaping an archive must resolve to the immutable public revision.
保留本地适配与嵌套许可；构建变换只作用于生成副本，实际独立构建是验收门槛。模式扫描不能替代人工许可与敏感信息审阅。
