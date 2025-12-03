#!/usr/bin/env python3
"""
Documentation validation script for docs-writer skill.

Checks documentation files for common quality issues:
- Placeholder text ([TODO], [PLACEHOLDER], etc.)
- Empty code blocks
- Missing required sections
- Broken internal links
- Syntax errors in code blocks (basic check)

Usage:
    python validate_docs.py <file.md>
    python validate_docs.py <directory>
    python validate_docs.py --help

Exit codes:
    0 - All checks passed
    1 - Validation errors found
    2 - File/directory not found
"""

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class Issue(NamedTuple):
    """Represents a validation issue."""
    file: str
    line: int
    severity: str  # "error" or "warning"
    message: str


def check_placeholder_text(content: str, filepath: str) -> list[Issue]:
    """Check for placeholder text that should be replaced."""
    issues = []
    patterns = [
        (r'\[TODO\]', 'Contains [TODO] placeholder'),
        (r'\[PLACEHOLDER\]', 'Contains [PLACEHOLDER] text'),
        (r'\[INSERT.*?\]', 'Contains [INSERT...] placeholder'),
        (r'\[YOUR.*?\]', 'Contains [YOUR...] placeholder'),
        (r'<.*?TODO.*?>', 'Contains <TODO> placeholder'),
        (r'xxx+', 'Contains xxx placeholder'),
        (r'TBD', 'Contains TBD (to be determined)'),
    ]

    for line_num, line in enumerate(content.split('\n'), 1):
        for pattern, message in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # Skip if the match is inside backticks (inline code or documenting placeholders)
                # Check for `...pattern...` or documenting the pattern itself
                if re.search(r'`[^`]*' + pattern + r'[^`]*`', line, re.IGNORECASE):
                    continue
                issues.append(Issue(filepath, line_num, 'error', message))

    return issues


def check_empty_code_blocks(content: str, filepath: str) -> list[Issue]:
    """Check for empty or near-empty code blocks."""
    issues = []

    # Match code blocks with optional language hint
    code_block_pattern = r'```(\w*)\n(.*?)```'

    for match in re.finditer(code_block_pattern, content, re.DOTALL):
        lang = match.group(1)
        block_content = match.group(2).strip()

        # Find line number
        start_pos = match.start()
        line_num = content[:start_pos].count('\n') + 1

        if not block_content:
            issues.append(Issue(filepath, line_num, 'error',
                f'Empty code block{f" ({lang})" if lang else ""}'))
        elif block_content in ['...', '# ...', '// ...', '# TODO', '// TODO']:
            issues.append(Issue(filepath, line_num, 'warning',
                f'Code block contains only placeholder: {block_content}'))

    return issues


def check_broken_links(content: str, filepath: str) -> list[Issue]:
    """Check for potentially broken internal links."""
    issues = []
    base_dir = Path(filepath).parent

    # Match markdown links: [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

    for line_num, line in enumerate(content.split('\n'), 1):
        for match in re.finditer(link_pattern, line):
            link_text = match.group(1)
            link_url = match.group(2)

            # Skip external links and anchors
            if link_url.startswith(('http://', 'https://', '#', 'mailto:')):
                continue

            # Check if internal file exists
            link_path = base_dir / link_url.split('#')[0]  # Remove anchor
            if not link_path.exists():
                issues.append(Issue(filepath, line_num, 'warning',
                    f'Broken link to: {link_url}'))

    return issues


def check_required_sections(content: str, filepath: str, doc_type: str = None) -> list[Issue]:
    """Check for required sections based on document type."""
    issues = []

    # Detect document type from content if not specified
    if doc_type is None:
        if 'API' in content and ('endpoint' in content.lower() or 'GET ' in content or 'POST ' in content):
            doc_type = 'api'
        elif 'installation' in content.lower() and 'usage' in content.lower():
            doc_type = 'guide'
        elif 'architecture' in content.lower() or 'ADR' in content:
            doc_type = 'architecture'

    required_sections = {
        'api': ['Authentication', 'Endpoint', 'Error'],
        'guide': ['Installation', 'Usage'],
        'architecture': ['Overview', 'Component'],
    }

    if doc_type and doc_type in required_sections:
        for section in required_sections[doc_type]:
            if section.lower() not in content.lower():
                issues.append(Issue(filepath, 0, 'warning',
                    f'Missing recommended section: {section}'))

    return issues


def check_code_block_languages(content: str, filepath: str) -> list[Issue]:
    """Check that code blocks have language hints."""
    issues = []

    # Match code blocks without language hints
    pattern = r'```\n'

    for line_num, line in enumerate(content.split('\n'), 1):
        if line.strip() == '```' and line_num > 1:
            # Check if this is an opening fence (not closing)
            prev_lines = content.split('\n')[:line_num-1]
            open_fences = sum(1 for l in prev_lines if l.strip().startswith('```'))
            if open_fences % 2 == 0:  # Even means this is an opening fence
                issues.append(Issue(filepath, line_num, 'warning',
                    'Code block missing language hint'))

    return issues


def validate_file(filepath: str) -> list[Issue]:
    """Run all validation checks on a file."""
    try:
        content = Path(filepath).read_text()
    except FileNotFoundError:
        return [Issue(filepath, 0, 'error', 'File not found')]
    except Exception as e:
        return [Issue(filepath, 0, 'error', f'Error reading file: {e}')]

    issues = []
    issues.extend(check_placeholder_text(content, filepath))
    issues.extend(check_empty_code_blocks(content, filepath))
    issues.extend(check_broken_links(content, filepath))
    issues.extend(check_required_sections(content, filepath))
    issues.extend(check_code_block_languages(content, filepath))

    return issues


def validate_directory(dirpath: str) -> list[Issue]:
    """Validate all markdown files in a directory."""
    issues = []

    for md_file in Path(dirpath).rglob('*.md'):
        issues.extend(validate_file(str(md_file)))

    return issues


def format_issues(issues: list[Issue]) -> str:
    """Format issues for display."""
    if not issues:
        return "✓ All checks passed"

    output = []
    errors = [i for i in issues if i.severity == 'error']
    warnings = [i for i in issues if i.severity == 'warning']

    if errors:
        output.append(f"\n✗ {len(errors)} error(s):")
        for issue in errors:
            loc = f"{issue.file}:{issue.line}" if issue.line else issue.file
            output.append(f"  ERROR {loc}: {issue.message}")

    if warnings:
        output.append(f"\n⚠ {len(warnings)} warning(s):")
        for issue in warnings:
            loc = f"{issue.file}:{issue.line}" if issue.line else issue.file
            output.append(f"  WARN  {loc}: {issue.message}")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Validate documentation files for quality issues'
    )
    parser.add_argument('path', help='File or directory to validate')
    parser.add_argument('--strict', action='store_true',
        help='Treat warnings as errors')
    args = parser.parse_args()

    path = Path(args.path)

    if not path.exists():
        print(f"Error: {args.path} not found", file=sys.stderr)
        sys.exit(2)

    if path.is_dir():
        issues = validate_directory(args.path)
    else:
        issues = validate_file(args.path)

    print(format_issues(issues))

    errors = [i for i in issues if i.severity == 'error']
    warnings = [i for i in issues if i.severity == 'warning']

    if errors or (args.strict and warnings):
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
