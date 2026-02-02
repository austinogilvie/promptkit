#!/usr/bin/env python3
"""
map_tokens.py

Deterministically rewrites "Pencilisms" into project design system tokens.

Reads token mappings from a per-project config file (.pencil-normalize.config.json)
discovered via CWD-upward walk or explicit --config flag.

Primary purpose:
- Replace CSS variable references like var(--pencil-accent) -> var(--your-token)
- Replace common Tailwind literal classes like bg-white -> bg-[var(--your-token)]
- Replace z-index and shadow Tailwind classes optionally

Safe by default:
- Prints a unified diff for all changes
- Does NOT write files unless --apply is passed

Usage:
  map_tokens.py scan [<path>] [--config=<cfg>] [--ext=<exts>] [--include-tests] [--fix-shadows] [--fix-z] [--fix-copy] [--strict]
  map_tokens.py apply [<path>] [--config=<cfg>] [--ext=<exts>] [--include-tests] [--backup] [--fix-shadows] [--fix-z] [--fix-copy] [--strict]
  map_tokens.py check [<path>] [--config=<cfg>] [--ext=<exts>] [--include-tests] [--fix-shadows] [--fix-z] [--fix-copy] [--strict]


Options:
  --config=<cfg>       Path to .pencil-normalize.config.json (auto-discovered if omitted)
  --ext=<exts>         Comma-separated extensions to include [default: ts,tsx,js,jsx,css,md]
  --include-tests      Include *.test.*, *.spec.* files (default: excluded)
  --backup             When applying, write a .bak copy next to each modified file
  --fix-shadows        Remove Tailwind shadow-* classes from className strings
  --fix-z              Normalize z-index classes to design system tokens
  --fix-copy           Fix known copy regressions
  --strict             Enable all fix passes (equivalent to --fix-shadows --fix-z --fix-copy)

Examples:
  map_tokens.py scan src
  map_tokens.py apply src --backup
  map_tokens.py check src/components
  map_tokens.py scan src --fix-shadows --fix-z --fix-copy
  map_tokens.py apply src --backup --strict
  map_tokens.py scan --config=path/to/.pencil-normalize.config.json
"""

from __future__ import annotations

import difflib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from docopt import docopt

_CONFIG_FILENAME = ".pencil-normalize.config.json"
_REQUIRED_CONFIG_FIELDS = ("version", "scan_path", "css_var_map")


def _find_config(start: Path) -> Optional[Path]:
    """Walk from start directory upward looking for .pencil-normalize.config.json."""
    current = start.resolve()
    while True:
        candidate = current / _CONFIG_FILENAME
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            return None
        current = parent


def _load_config(config_path: Path) -> Dict:
    """Read, parse, and validate a .pencil-normalize.config.json file."""
    try:
        raw = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read config {config_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        config = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {config_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(config, dict):
        print(f"error: config must be a JSON object, got {type(config).__name__}", file=sys.stderr)
        sys.exit(1)

    missing = [f for f in _REQUIRED_CONFIG_FIELDS if f not in config]
    if missing:
        print(
            f"error: config {config_path} missing required fields: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)

    if not isinstance(config["css_var_map"], dict):
        print("error: css_var_map must be a JSON object", file=sys.stderr)
        sys.exit(1)

    return config


@dataclass(frozen=True)
class RewriteRule:
    """A single regex-based rewrite rule applied in order."""
    name: str
    pattern: re.Pattern
    replacement: str


def _parse_exts(exts_csv: str) -> List[str]:
    """Parse comma-separated extensions into normalized list (no dots)."""
    exts = [e.strip().lstrip(".") for e in exts_csv.split(",") if e.strip()]
    if not exts:
        return ["ts", "tsx", "js", "jsx", "css", "md"]
    return exts


def _iter_files(root: Path, exts: List[str], include_tests: bool) -> Iterable[Path]:
    """Yield files under root matching extensions; optionally exclude tests."""
    if root.is_file():
        if _is_allowed_file(root, exts, include_tests):
            yield root
        return

    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if _is_allowed_file(p, exts, include_tests):
            yield p


_COPY_SAFE_EXTS = frozenset({"tsx", "jsx"})


def _is_allowed_file(p: Path, exts: List[str], include_tests: bool) -> bool:
    """Return True if file should be processed."""
    if p.suffix.lstrip(".") not in exts:
        return False
    if include_tests:
        return True
    name = p.name
    if ".test." in name or ".spec." in name:
        return False
    return True


def _build_rules(
    *,
    fix_shadows: bool = False,
    fix_z: bool = False,
    fix_copy: bool = False,
) -> Tuple[List[RewriteRule], Callable[[re.Match], str]]:
    """
    Build rewrite rules.

    Keep this mapping small and authoritative.
    If you add new mappings, also add them to reference.md so humans + Claude agree.
    """
    # 1) CSS var mapping: var(--pencil-*) -> var(--system-*)
    css_var_map = {
        "--pencil-accent": "--accent-interactive",
        "--pencil-accent-hover": "--accent-attention",
        "--pencil-text-primary": "--foreground-primary",
        "--pencil-text-secondary": "--foreground-secondary",
        "--pencil-text-muted": "--foreground-muted",
        "--pencil-bg": "--surface-base",
        "--pencil-surface": "--surface-level-1",
        "--pencil-surface-muted": "--surface-level-1",
        "--pencil-border": "--border-default",
        "--pencil-border-strong": "--border-strong",
    }

    # Regex: var(--pencil-foo) including whitespace tolerance
    css_var_pattern = re.compile(r"var\(\s*(--pencil-[a-zA-Z0-9_-]+)\s*\)")

    def css_var_repl(m: re.Match) -> str:
        """Replace a var(--pencil-*) reference when mapped; otherwise keep as-is."""
        key = m.group(1)
        mapped = css_var_map.get(key)
        if not mapped:
            return m.group(0)
        return f"var({mapped})"

    # 2) Tailwind literal class replacements (in new code)
    # Apply only to className strings; we do a conservative plain-text replace for known tokens.
    # (AST codemod is better later; this is intentionally small and predictable.)
    tailwind_literal_map = {
        "bg-white": "bg-[var(--surface-level-1)]",
        "bg-gray-50": "bg-[var(--surface-level-1)]",
        "text-gray-900": "text-[var(--foreground-primary)]",
        "text-gray-700": "text-[var(--foreground-secondary)]",
        "text-gray-600": "text-[var(--foreground-secondary)]",
        "text-gray-500": "text-[var(--foreground-tertiary)]",
        "text-gray-400": "text-[var(--foreground-muted)]",
        "border-gray-200": "border-[color:var(--border-default)]",
        "border-gray-300": "border-[color:var(--border-strong)]",
    }

    # Build ordered rules list
    rules: List[RewriteRule] = []

    # Rule A: CSS var replacements via function (handled separately)
    rules.append(
        RewriteRule(
            name="css_var_rewrite",
            pattern=css_var_pattern,
            replacement="__CALLABLE__",
        )
    )

    # Rule B: Tailwind literal replacements (simple token boundaries)
    for src, dst in tailwind_literal_map.items():
        rules.append(
            RewriteRule(
                name=f"tw:{src}",
                pattern=re.compile(rf"(?<![\w-]){re.escape(src)}(?![\w-])"),
                replacement=dst,
            )
        )

    # Rule C (opt-in): Shadow removal — strip shadow-* Tailwind classes
    if fix_shadows:
        rules.append(
            RewriteRule(
                name="fix-shadow",
                pattern=re.compile(r"(?<![\w-])shadow(?:-\[[^\]]+\]|-(sm|md|lg|xl|2xl))?(?![\w-])"),
                replacement="",
            )
        )

    # Rule D (opt-in): Z-index normalization
    if fix_z:
        # (label, regex_fragment, replacement)
        z_rules = [
            ("z-[9999]", r"z-\[9999\]", "z-[var(--z-popover)]"),
            ("z-[1000]", r"z-\[1000\]", "z-[var(--z-popover)]"),
            ("z-50",     r"z-50",        "z-[var(--z-popover)]"),
            ("z-40",     r"z-40",        "z-[var(--z-sidebars)]"),
            ("z-20",     r"z-20",        "z-[var(--z-header)]"),
        ]
        for label, src_pat, dst in z_rules:
            rules.append(
                RewriteRule(
                    name=f"fix-z:{label}",
                    pattern=re.compile(rf"(?<![\w-]){src_pat}(?![\w-])"),
                    replacement=dst,
                )
            )

    # Rule E (opt-in): Copy regression fixes
    if fix_copy:
        rules.append(
            RewriteRule(
                name="fix-copy:requires-refresh",
                pattern=re.compile(r"(?i)requires refresh"),
                replacement="",
            )
        )
        rules.append(
            RewriteRule(
                name="fix-copy:refresh-detection",
                pattern=re.compile(r"(?i)Refresh detection"),
                replacement="Re-run detection",
            )
        )

    return rules, css_var_repl


_CLASSNAME_ATTR = re.compile(r'(className=")(.*?)(")')


def _collapse_classname_spaces(text: str) -> str:
    """Collapse multi-spaces and trim whitespace inside className="..." attributes only."""

    def _clean(m: re.Match) -> str:
        prefix, classes, suffix = m.group(1), m.group(2), m.group(3)
        classes = re.sub(r" {2,}", " ", classes).strip()
        return prefix + classes + suffix

    return _CLASSNAME_ATTR.sub(_clean, text)


def _apply_rules(
    text: str,
    *,
    fix_shadows: bool = False,
    fix_z: bool = False,
    fix_copy: bool = False,
) -> Tuple[str, List[str]]:
    """Apply all rewrite rules, returning new text and list of applied rule names."""
    rules, css_var_repl = _build_rules(
        fix_shadows=fix_shadows,
        fix_z=fix_z,
        fix_copy=fix_copy,
    )

    applied: List[str] = []
    need_space_cleanup = False
    out = text

    for rule in rules:
        if rule.name == "css_var_rewrite":
            new_out = rule.pattern.sub(css_var_repl, out)
            if new_out != out:
                applied.append(rule.name)
            out = new_out
            continue

        new_out = rule.pattern.sub(rule.replacement, out)
        if new_out != out:
            applied.append(rule.name)
            if rule.name == "fix-shadow":
                need_space_cleanup = True
        out = new_out

    if need_space_cleanup:
        out = _collapse_classname_spaces(out)

    return out, applied


def _diff(path: Path, before: str, after: str) -> str:
    """Return unified diff string."""
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    diff_lines = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile=str(path),
        tofile=str(path),
        lineterm="",
    )
    return "".join(diff_lines)


def _read_text(path: Path) -> str:
    """Read file as text with utf-8 fallback."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _write_text(path: Path, text: str) -> None:
    """Write file text as utf-8."""
    path.write_text(text, encoding="utf-8")


def _run_scan(
    paths: List[Path],
    exts: List[str],
    include_tests: bool,
    *,
    fix_shadows: bool = False,
    fix_z: bool = False,
    fix_copy: bool = False,
) -> int:
    """Scan and print diffs without writing."""
    changed = 0

    for root in paths:
        for fp in _iter_files(root, exts, include_tests):
            file_fix_copy = fix_copy and fp.suffix.lstrip(".") in _COPY_SAFE_EXTS
            before = _read_text(fp)
            after, applied = _apply_rules(
                before, fix_shadows=fix_shadows, fix_z=fix_z, fix_copy=file_fix_copy,
            )
            if after == before:
                continue

            changed += 1
            print(_diff(fp, before, after))
            print(f"\n# applied: {', '.join(sorted(set(applied)))}\n")

    if changed == 0:
        print("No changes would be made.")
    else:
        print(f"Would change {changed} file(s).")

    return 0


def _run_apply(
    paths: List[Path],
    exts: List[str],
    include_tests: bool,
    backup: bool,
    *,
    fix_shadows: bool = False,
    fix_z: bool = False,
    fix_copy: bool = False,
) -> int:
    """Apply changes in-place and print a summary."""
    changed_files: List[Path] = []

    for root in paths:
        for fp in _iter_files(root, exts, include_tests):
            file_fix_copy = fix_copy and fp.suffix.lstrip(".") in _COPY_SAFE_EXTS
            before = _read_text(fp)
            after, _applied = _apply_rules(
                before, fix_shadows=fix_shadows, fix_z=fix_z, fix_copy=file_fix_copy,
            )
            if after == before:
                continue

            if backup:
                bak = fp.with_suffix(fp.suffix + ".bak")
                if not bak.exists():
                    _write_text(bak, before)

            _write_text(fp, after)
            changed_files.append(fp)

    if not changed_files:
        print("No files changed.")
        return 0

    print(f"Changed {len(changed_files)} file(s):")
    for fp in changed_files:
        print(f"- {fp}")
    return 0


def _run_check(
    paths: List[Path],
    exts: List[str],
    include_tests: bool,
    *,
    fix_shadows: bool = False,
    fix_z: bool = False,
    fix_copy: bool = False,
) -> int:
    """Exit non-zero if any file would change (CI-style)."""
    offenders: List[Path] = []

    for root in paths:
        for fp in _iter_files(root, exts, include_tests):
            file_fix_copy = fix_copy and fp.suffix.lstrip(".") in _COPY_SAFE_EXTS
            before = _read_text(fp)
            after, _applied = _apply_rules(
                before, fix_shadows=fix_shadows, fix_z=fix_z, fix_copy=file_fix_copy,
            )
            if after != before:
                offenders.append(fp)

    if not offenders:
        print("OK: no pencil token rewrites needed.")
        return 0

    print("FAIL: files need normalization:")
    for fp in offenders:
        print(f"- {fp}")
    return 2


def main(argv: List[str]) -> int:
    """CLI entrypoint."""
    args = docopt(__doc__, argv=argv)

    cmd_scan = bool(args.get("scan"))
    cmd_apply = bool(args.get("apply"))
    cmd_check = bool(args.get("check"))

    exts = _parse_exts(args["--ext"])
    include_tests = bool(args["--include-tests"])
    backup = bool(args.get("--backup"))

    strict = bool(args.get("--strict"))
    fix_shadows = strict or bool(args.get("--fix-shadows"))
    fix_z = strict or bool(args.get("--fix-z"))
    fix_copy = strict or bool(args.get("--fix-copy"))

    raw_path = args["<path>"] or "frontend/src"
    root = Path(raw_path).expanduser().resolve()

    fix_kwargs = dict(fix_shadows=fix_shadows, fix_z=fix_z, fix_copy=fix_copy)

    if cmd_scan:
        return _run_scan([root], exts, include_tests, **fix_kwargs)
    if cmd_apply:
        return _run_apply([root], exts, include_tests, backup, **fix_kwargs)
    if cmd_check:
        return _run_check([root], exts, include_tests, **fix_kwargs)

    print("error: unknown command (expected scan/apply/check)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
