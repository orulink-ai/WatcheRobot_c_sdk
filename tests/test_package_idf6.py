from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def test_package_camera_matches_successful_source_build_mbedtls_flags(tmp_path):
    spec = importlib.util.spec_from_file_location('sdk_package_idf6', ROOT / 'tools/package_components.py')
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = tmp_path / 'release'
    module.prepare(output, 'preview_test', '0.1.0-preview.1', 'HEAD')
    text = (output / 'components/hal_camera/CMakeLists.txt').read_text()
    assert 'target_compile_definitions(${COMPONENT_LIB} PRIVATE MBEDTLS_DECLARE_PRIVATE_IDENTIFIERS)' not in text, (
        'Do not add an unneeded -D=1 macro to packaged camera: IDF6 mbedTLS4 defines it empty '
        'in private_access.h and -Werror rejects the redefinition; source build works without it.'
    )
