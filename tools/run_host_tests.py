#!/usr/bin/env python3
"""Discover every components/examples host or uart_host CMake suite and run it.

Requires real dependencies via --lvgl-source / --cjson-source (or the matching
LVGL_SOURCE_DIR / CJSON_SOURCE_DIR environment variables). Never downloads or
substitutes dependencies. Debug and Release have independent build trees.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET


def discover(root):
    return sorted(p.parent for folder in ('components', 'examples')
                  for p in (root / folder).rglob('CMakeLists.txt')
                  if p.parent.name in ('host', 'uart_host'))


def execute(command, log, timeout=600):
    """Run argument arrays, not a platform-specific shell, retaining real output."""
    log.write('$ ' + json.dumps(command) + '\n')
    log.flush()
    result = subprocess.run(command, capture_output=True, text=True, errors='replace', timeout=timeout)
    log.write(result.stdout + result.stderr)
    log.flush()
    if result.returncode:
        raise RuntimeError(f'Command failed ({result.returncode}): {command[0]} {command[1:]}')
    return result.stdout


def dependency_info(name, path):
    required = {'LVGL_SOURCE_DIR': ('lvgl.h', 'src/core/lv_obj.c', 'CMakeLists.txt'),
                'CJSON_SOURCE_DIR': ('cJSON.c', 'cJSON.h')}[name]
    if path is None or not all((path / file).is_file() for file in required):
        raise RuntimeError(f'Missing real dependency {name}: {path}; required files: {required}')
    header = (path / required[0 if name == 'LVGL_SOURCE_DIR' else 1]).read_text(encoding='utf-8')
    prefix = 'LVGL_VERSION' if name == 'LVGL_SOURCE_DIR' else 'CJSON_VERSION'
    parts = []
    for part in ('MAJOR', 'MINOR', 'PATCH'):
        match = re.search(r'^\s*#define\s+' + prefix + '_' + part + r'\s+(\d+)', header, re.M)
        if not match:
            raise RuntimeError(f'Cannot determine actual {name} version from headers')
        parts.append(match[1])
    info = {'path': str(path), 'version': '.'.join(parts)}
    git = subprocess.run(['git', '-C', str(path), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    if git.returncode == 0:
        info['commit'] = git.stdout.strip()
    return info


def compiler_info(build):
    info = {}
    for language in ('C', 'CXX'):
        for file in (build / 'CMakeFiles').glob(f'*/CMake{language}Compiler.cmake'):
            text = file.read_text(encoding='utf-8')
            for key, value in re.findall(r'set\((CMAKE_\w+_COMPILER(?:_ID|_VERSION)?) "([^"\n]+)"\)', text):
                info[key] = value
    return info


def run_suite(source, root, build_root, config, generator, dependencies, jobs):
    relative = source.relative_to(root)
    build = build_root / config / relative
    build.mkdir(parents=True, exist_ok=True)
    suite = {'source': relative.as_posix(), 'build_dir': str(build), 'status': 'failed',
             'tests': 0, 'test_results': [], 'log': str(build / 'runner.log')}
    started = time.monotonic()
    with (build / 'runner.log').open('w', encoding='utf-8') as log:
        try:
            command = ['cmake', '-S', str(source), '-B', str(build), '-G', generator,
                       f'-DCMAKE_BUILD_TYPE={config}']
            # Several imported tests execute actions inside assert(). Keep assertions
            # alive for every suite, including those lacking per-target -UNDEBUG.
            msvc = platform.system() == 'Windows' and not os.environ.get('CC', '').endswith(('gcc', 'clang'))
            assertion_flag = '/UNDEBUG' if msvc else '-UNDEBUG'
            optimization = ('/O2' if msvc else '-O2') if config == 'Release' else ('/Zi' if msvc else '-g')
            for language in ('C', 'CXX'):
                command.append(f'-DCMAKE_{language}_FLAGS_{config.upper()}={optimization} {assertion_flag}')
            command.extend(f'-D{name}={value["path"]}' for name, value in dependencies.items())
            execute(command, log)
            suite['compiler'] = compiler_info(build)
            execute(['cmake', '--build', str(build), '--config', config, '--parallel', str(jobs)], log)
            listing = json.loads(execute(['ctest', '--test-dir', str(build), '-C', config,
                                          '--show-only=json-v1'], log))
            suite['tests'] = len(listing.get('tests', []))
            if not suite['tests']:
                raise RuntimeError('CTest discovered zero tests')
            junit = build / 'ctest.xml'
            try:
                execute(['ctest', '--test-dir', str(build), '-C', config, '--output-on-failure',
                         '--no-tests=error', '--timeout', '60', '--output-junit', str(junit)], log)
            finally:
                if junit.is_file():
                    for case in ET.parse(junit).getroot().iter('testcase'):
                        status = 'failed' if case.find('failure') is not None else 'skipped' if case.find('skipped') is not None else 'passed'
                        suite['test_results'].append({'name': case.get('name'), 'status': status,
                                                       'seconds': float(case.get('time', 0))})
            if len(suite['test_results']) != suite['tests'] or any(t['status'] != 'passed' for t in suite['test_results']):
                raise RuntimeError('CTest results incomplete, failed or skipped')
            suite['status'] = 'passed'
        except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired, ET.ParseError) as exc:
            suite['error'] = str(exc)
            log.write('\nERROR: ' + str(exc) + '\n')
    suite['seconds'] = round(time.monotonic() - started, 3)
    print(f'{suite["status"]}: {suite["source"]} ({suite["tests"]} tests)', flush=True)
    return suite


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--config', choices=('Debug', 'Release'), default='Debug')
    parser.add_argument('--build-root', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--lvgl-source', type=Path, default=os.environ.get('LVGL_SOURCE_DIR'))
    parser.add_argument('--cjson-source', type=Path, default=os.environ.get('CJSON_SOURCE_DIR'))
    parser.add_argument('--generator', default='Ninja')
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args()
    root = args.root.resolve()
    build_root = (args.build_root or root / '.host-build').resolve()
    report_path = (args.report or build_root / args.config / 'report.json').resolve()
    report = {'schema_version': 1, 'status': 'failed', 'config': args.config,
              'started_at': datetime.now(timezone.utc).isoformat(), 'platform': platform.platform(),
              'versions': {'python': sys.version}, 'dependencies': {}, 'suites': []}
    try:
        sources = discover(root)
        if not sources:
            raise RuntimeError('No host suites discovered')
        if args.jobs < 1:
            raise RuntimeError('--jobs must be positive')
        for program in ('cmake', 'ctest', 'ninja'):
            version = subprocess.run([program, '--version'], capture_output=True, text=True, check=True)
            report['versions'][program] = version.stdout.splitlines()[0]
        combined = '\n'.join((p / 'CMakeLists.txt').read_text(encoding='utf-8') for p in sources)
        for name, path in [('LVGL_SOURCE_DIR', args.lvgl_source), ('CJSON_SOURCE_DIR', args.cjson_source)]:
            if name in combined:
                report['dependencies'][name] = dependency_info(name, path.resolve() if path else None)
        for source in sources:
            report['suites'].append(run_suite(source, root, build_root, args.config,
                                               args.generator, report['dependencies'], args.jobs))
        if all(suite['status'] == 'passed' for suite in report['suites']):
            report['status'] = 'passed'
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as exc:
        report['error'] = str(exc)
        print('ERROR: ' + str(exc), file=sys.stderr)
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'Report: {report_path}', flush=True)
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
