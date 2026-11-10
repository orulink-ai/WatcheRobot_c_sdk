#!/usr/bin/env python3
"""Validate all repository Markdown, local source references and descriptions offline.

External URLs are deliberately not fetched. Inline code that is exactly a repository
path (components/, examples/, docs/, tools/, tests/) is checked, but shell commands,
globs and placeholders are not treated as literal paths. Code fences are excluded.
"""
import argparse
import html
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

EXCLUDED = {'.git', '.venv', 'venv', 'node_modules', 'managed_components',
            '__pycache__', '.pytest_cache', '.host-build', 'build', 'dist', '.deps'}


def visible_text(text):
    """Remove fenced code and HTML comments, preserving line boundaries."""
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if fence:
            if re.match(r'^ {0,3}' + re.escape(fence[0]) + '{' + str(len(fence)) + r',}\s*$', line):
                fence = None
            lines.append('')
        elif match:
            fence = match[1]
            lines.append('')
        else:
            lines.append(line)
    return re.sub(r'<!--[\s\S]*?-->', '', '\n'.join(lines))


def anchors(text):
    """GitHub-style heading slugs, duplicates, setext headings and HTML IDs."""
    result = set(re.findall(r'\b(?:id|name)=[\"\']([^\"\']+)[\"\']', text))
    counts = {}
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r'^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$', line)
        title = match[1] if match else None
        if title is None and index + 1 < len(lines) and line.strip() and re.match(r'^ {0,3}(?:=+|-+)\s*$', lines[index + 1]):
            title = line.strip()
        if title is None:
            continue
        title = re.sub(r'!?\[([^\]]+)\]\([^)]*\)', r'\1', title)
        title = re.sub(r'<[^>]*>', '', html.unescape(title)).lower()
        slug = re.sub(r'[^\w\-\s]', '', title)
        slug = re.sub(r'\s', '-', slug)
        number = counts.get(slug, 0)
        counts[slug] = number + 1
        result.add(slug + (f'-{number}' if number else ''))
    return result


def links(text):
    """Extract inline, image, reference and HTML local link destinations."""
    refs = {m[1].strip().casefold(): (m[2] or m[3]) for m in re.finditer(
        r'^ {0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))', text, re.M)}
    # Inline code is not Markdown link syntax.
    plain = re.sub(r'(`+).*?\1', '', text)
    found = []
    for match in re.finditer(r'!?\[[^\]\n]*\]\(\s*(?:<([^>]+)>|([^\s()]*(?:\([^()]*\)[^\s()]*)*))', plain):
        found.append(match[1] or match[2])
    for match in re.finditer(r'!?\[([^\]\n]+)\](?:\[([^\]\n]*)\])?(?![(:])', plain):
        key = (match[2] or match[1]).strip().casefold()
        if key in refs:
            found.append(refs[key])
        elif match[2] is not None:
            found.append('UNDEFINED_REFERENCE:' + key)
    found.extend(re.findall(r'\b(?:href|src)=[\"\']([^\"\']+)[\"\']', plain))
    return found


def check(root):
    errors = []
    documents = sorted(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() == '.md'
                       and not any(part in EXCLUDED for part in p.relative_to(root).parts))
    if not documents:
        return ['No Markdown documents found']
    texts = {doc: visible_text(doc.read_text(encoding='utf-8')) for doc in documents}
    for doc, text in texts.items():
        for link in links(text):
            if link.startswith('UNDEFINED_REFERENCE:'):
                errors.append(f'{doc.relative_to(root)}: undefined reference: {link.split(":", 1)[1]}')
                continue
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            path = unquote(parsed.path)
            target = (doc if not path else root / path.lstrip('/') if path.startswith('/') else doc.parent / path).resolve()
            if not target.is_relative_to(root):
                errors.append(f'{doc.relative_to(root)}: local target escapes repository: {link}')
            elif not target.exists():
                errors.append(f'{doc.relative_to(root)}: missing local target: {link}')
            elif parsed.fragment and target.suffix.lower() == '.md':
                fragment = unquote(parsed.fragment)
                target_text = texts.get(target)
                if target_text is None:
                    target_text = visible_text(target.read_text(encoding='utf-8'))
                if fragment not in anchors(target_text):
                    errors.append(f'{doc.relative_to(root)}: missing anchor: {link}')
            # Source #L123[-L456] fragments are line references, not headings.
        for value in re.findall(r'`([^`\n]+)`', text):
            if re.fullmatch(r'(?:components|examples|tools|tests|docs)/[\w./-]+(?:#L\d+(?:-L\d+)?)?', value):
                path = value.split('#', 1)[0]
                # A documented output filename is not an existing source file.
                # Actual Markdown links still must exist, even under build/.
                if 'build' in Path(path).parts or 'managed_components' in Path(path).parts:
                    continue
                if not (root / path).exists():
                    errors.append(f'{doc.relative_to(root)}: missing source path: {value}')
    directories = []
    for cmake in (root / 'components').rglob('CMakeLists.txt'):
        if 'test_support' not in cmake.relative_to(root).parts:
            directories.append(cmake.parent)
    directories.extend(p.parent for p in (root / 'examples').glob('*/CMakeLists.txt'))
    for directory in sorted(directories):
        readme = directory / 'README.md'
        body = visible_text(readme.read_text(encoding='utf-8')) if readme.is_file() else ''
        body = re.sub(r'^\s*#+[^\n]*', '', body, flags=re.M).strip()
        if not re.search(r'\w', body):
            errors.append(f'{directory.relative_to(root)}: missing or empty description (README.md)')
    return errors


def check_source(root):
    """Verify the current destination bytes, not the historical upstream hash."""
    import hashlib
    import json
    errors = []
    try:
        entries = json.loads((root / 'SOURCE.json').read_text(encoding='utf-8'))['files']
        if not isinstance(entries, list) or not entries:
            raise ValueError('files must be a nonempty list')
        seen = set()
        for entry in entries:
            name = entry['destination']
            path = (root / name).resolve()
            if name in seen or not path.is_relative_to(root) or Path(name).is_absolute():
                errors.append(f'SOURCE invalid or duplicate destination: {name}')
                continue
            seen.add(name)
            expected = entry['sha256']
            if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
                errors.append(f'SOURCE invalid SHA256: {name}')
            elif not path.is_file():
                errors.append(f'SOURCE missing destination: {name}')
            elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                errors.append(f'SOURCE hash mismatch: {name}')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'SOURCE verification failed: {exc}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--check-source', action='store_true', help='Also verify SOURCE.json destination hashes')
    args = parser.parse_args()
    root = args.root.resolve()
    errors = check(root)
    if args.check_source:
        errors.extend(check_source(root))
    for error in errors:
        print(error)
    print(f'Documentation validation: {len(errors)} error(s)')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
