#!/usr/bin/env python3
"""
Code block syntax validator for docs-writer skill.

Extracts code blocks from markdown and validates syntax:
- Python: Uses ast.parse()
- JavaScript/TypeScript: Basic syntax check
- JSON: Uses json.loads()
- YAML: Uses yaml.safe_load() if available
- Bash: Basic syntax patterns

Usage:
    python check_code_blocks.py <file.md>
    python check_code_blocks.py --lang python <file.md>

Exit codes:
    0 - All code blocks valid (or no code blocks found)
    1 - Syntax errors found
    2 - File not found
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class CodeBlock(NamedTuple):
    """Represents an extracted code block."""
    language: str
    content: str
    line_number: int


class SyntaxIssue(NamedTuple):
    """Represents a syntax error in a code block."""
    language: str
    line_number: int
    error: str


def extract_code_blocks(content: str) -> list[CodeBlock]:
    """Extract all code blocks from markdown content."""
    blocks = []

    # Match fenced code blocks with language hint
    pattern = r'```(\w+)\n(.*?)```'

    for match in re.finditer(pattern, content, re.DOTALL):
        lang = match.group(1).lower()
        code = match.group(2)

        # Calculate line number
        start_pos = match.start()
        line_num = content[:start_pos].count('\n') + 1

        blocks.append(CodeBlock(lang, code, line_num))

    return blocks


def validate_python(code: str) -> str | None:
    """Validate Python syntax using ast.parse()."""
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return str(e)


def validate_json(code: str) -> str | None:
    """Validate JSON syntax."""
    try:
        json.loads(code)
        return None
    except json.JSONDecodeError as e:
        return f"Line {e.lineno}: {e.msg}"


def validate_yaml(code: str) -> str | None:
    """Validate YAML syntax (if PyYAML available)."""
    if not HAS_YAML:
        return None  # Skip if yaml not available

    try:
        yaml.safe_load(code)
        return None
    except yaml.YAMLError as e:
        return str(e)


def validate_javascript(code: str) -> str | None:
    """Basic JavaScript syntax validation (pattern-based)."""
    issues = []

    # Check for common syntax errors
    # Unmatched braces
    if code.count('{') != code.count('}'):
        issues.append("Unmatched curly braces")
    if code.count('[') != code.count(']'):
        issues.append("Unmatched square brackets")
    if code.count('(') != code.count(')'):
        issues.append("Unmatched parentheses")

    # Unclosed strings (basic check)
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('//'):
            continue

        # Count unescaped quotes
        single_quotes = len(re.findall(r"(?<!\\)'", line))
        double_quotes = len(re.findall(r'(?<!\\)"', line))
        backticks = line.count('`')

        # Template literals can span lines, so only check regular quotes
        if single_quotes % 2 != 0:
            issues.append(f"Line {i}: Unclosed single quote")
        if double_quotes % 2 != 0:
            issues.append(f"Line {i}: Unclosed double quote")

    return '; '.join(issues) if issues else None


def validate_bash(code: str) -> str | None:
    """Basic bash syntax validation (pattern-based)."""
    issues = []

    lines = code.split('\n')
    in_heredoc = False
    heredoc_marker = None

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Track heredocs
        if '<<' in stripped and not in_heredoc:
            match = re.search(r"<<['\"]?(\w+)['\"]?", stripped)
            if match:
                in_heredoc = True
                heredoc_marker = match.group(1)
                continue

        if in_heredoc:
            if stripped == heredoc_marker:
                in_heredoc = False
                heredoc_marker = None
            continue

        # Skip comments
        if stripped.startswith('#'):
            continue

        # Check for common issues
        if stripped.endswith('\\') and i == len(lines):
            issues.append(f"Line {i}: Trailing backslash at end of file")

        # Unmatched quotes (basic)
        if stripped.count("'") % 2 != 0 and not stripped.endswith('\\'):
            # Could be a line continuation, check for common patterns
            if not any(p in stripped for p in ['$(', '`']):
                issues.append(f"Line {i}: Possibly unclosed single quote")

    if in_heredoc:
        issues.append(f"Unclosed heredoc (expecting {heredoc_marker})")

    return '; '.join(issues) if issues else None


def validate_code_block(block: CodeBlock) -> SyntaxIssue | None:
    """Validate a single code block based on its language."""
    validators = {
        'python': validate_python,
        'py': validate_python,
        'json': validate_json,
        'yaml': validate_yaml,
        'yml': validate_yaml,
        'javascript': validate_javascript,
        'js': validate_javascript,
        'typescript': validate_javascript,  # Basic check only
        'ts': validate_javascript,
        'bash': validate_bash,
        'sh': validate_bash,
        'shell': validate_bash,
    }

    validator = validators.get(block.language)
    if not validator:
        return None  # No validator for this language

    error = validator(block.content)
    if error:
        return SyntaxIssue(block.language, block.line_number, error)

    return None


def validate_file(filepath: str, lang_filter: str = None) -> list[SyntaxIssue]:
    """Validate all code blocks in a file."""
    try:
        content = Path(filepath).read_text()
    except FileNotFoundError:
        print(f"Error: {filepath} not found", file=sys.stderr)
        sys.exit(2)

    blocks = extract_code_blocks(content)

    if lang_filter:
        blocks = [b for b in blocks if b.language == lang_filter.lower()]

    issues = []
    for block in blocks:
        issue = validate_code_block(block)
        if issue:
            issues.append(issue)

    return issues


def main():
    parser = argparse.ArgumentParser(
        description='Validate code block syntax in markdown files'
    )
    parser.add_argument('file', help='Markdown file to validate')
    parser.add_argument('--lang', help='Only check blocks of this language')
    parser.add_argument('--list', action='store_true',
        help='List code blocks without validating')
    args = parser.parse_args()

    content = Path(args.file).read_text()
    blocks = extract_code_blocks(content)

    if args.list:
        print(f"Found {len(blocks)} code block(s):\n")
        for block in blocks:
            preview = block.content[:50].replace('\n', '\\n')
            if len(block.content) > 50:
                preview += '...'
            print(f"  Line {block.line_number}: {block.language} - {preview}")
        return

    issues = validate_file(args.file, args.lang)

    if not issues:
        print(f"✓ All code blocks valid ({len(blocks)} checked)")
        sys.exit(0)

    print(f"✗ Found {len(issues)} syntax error(s):\n")
    for issue in issues:
        print(f"  Line {issue.line_number} ({issue.language}): {issue.error}")

    sys.exit(1)


if __name__ == '__main__':
    main()
