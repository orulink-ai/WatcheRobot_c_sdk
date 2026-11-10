# hx_ptl_protocol

PTL base-header/JPEG packet validation, resynchronization and control-codec helpers used by the paired-camera path. Protocol validation is not a physical image-quality test.

- Low-level header: [`include/hx_ptl_protocol.h`](include/hx_ptl_protocol.h)
- Application entry: [public SDK usage](../../docs/api/camera.md)
- [Architecture](../../docs/architecture.md) · [Dependencies and local adaptations](../../docs/dependencies.md)
- [Testing/evidence](../../docs/testing.md)

Use the full pinned source checkout and the matching example defaults/manifests with ESP-IDF 6.0.2.
This description does not assert independent Registry availability or package dependency closure.
Do not bypass the public wrapper's shared-resource ownership when integrating these lower layers.
Existing source attribution and all dependency license terms remain unchanged.

中文：现有支持层导航，应用优先使用 watcher_hw_*；不承诺独立发布，不改变已有署名、许可证和硬件安全限制。
