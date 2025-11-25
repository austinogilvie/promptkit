#!/usr/bin/env python3
"""
manifest_directory.py

Usage:
  manifest_directory.py [DIRECTORY]

If DIRECTORY is omitted, the current working directory is used.

This script:

  1. Walks the target directory tree (skipping common large dirs like venv/).
  2. Indexes ALL files it finds.
  3. Analyzes Python scripts to infer file relationships:
       - Strong edges:
           * explicit reads (open/read_* with literal paths)
           * explicit writes (to_*/save/write with literal paths)
       - Weak edges:
           * scripts that merely mention a filename (like "bank-full.csv")
             are linked to actual files with that basename.
  4. Writes a JSON manifest (directory_manifest.json) with:
       - scripts: per-script reads / writes / related_files
       - files:   per-file read_by / written_by / mentioned_by
  5. Pretty-prints a human-readable summary of the manifest.

Example:
  python manifest_directory.py
  python manifest_directory.py REFERENCE
"""

import argparse
import ast
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

SKIP_DIRS = {
    "venv",
    ".venv",
    "env",
    ".env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".git",
    ".idea",
    ".vscode",
    "tmp",
}

MANIFEST_OUTPUT = "directory_manifest.json"


def parse_gitignore(root: Path) -> Set[str]:
    """
    Parse .gitignore file and return set of directory names to skip.

    Handles simple patterns:
    - Lines starting with # are comments
    - Lines ending with / are directories
    - Simple directory names without wildcards
    """
    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists():
        return set()

    skip_dirs: Set[str] = set()

    try:
        with gitignore_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Remove trailing slash if present
                if line.endswith("/"):
                    line = line[:-1]

                # Skip patterns with wildcards or path separators (too complex for simple matching)
                if "*" in line or "/" in line:
                    continue

                # Add simple directory names
                if line and not line.startswith("!"):
                    skip_dirs.add(line)

    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: Failed to parse .gitignore: {exc}", file=sys.stderr)

    return skip_dirs


def read_manifest(manifest_path: Path) -> Optional[Dict[str, Any]]:
    """Read an existing directory_manifest.json file, if it exists."""
    if not manifest_path.exists():
        return None
    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: Failed to read manifest at {manifest_path}: {exc}", file=sys.stderr)
        return None


def write_manifest(manifest_path: Path, manifest: Dict[str, Any]) -> None:
    """Write the manifest dictionary to directory_manifest.json."""
    try:
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Failed to write manifest to {manifest_path}: {exc}", file=sys.stderr)


def _relative_under_root(root: Path, path: Path) -> Optional[str]:
    """Return the path relative to root if the path is within root, else None."""
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return None


def get_file_metadata(file_path: Path) -> Dict[str, Any]:
    """Extract metadata for a file."""
    stat = file_path.stat()
    _, ext = os.path.splitext(file_path.name)

    return {
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "extension": ext if ext else None,
    }


def collect_files_and_scripts(root: Path) -> Tuple[List[str], List[Path]]:
    """
    Collect all files and Python scripts under root in a single walk.

    Returns:
        - List of all file paths (relative to root)
        - List of Python script absolute paths
    """
    root = root.resolve()
    all_files: List[str] = []
    script_paths: List[Path] = []

    # Merge hardcoded SKIP_DIRS with .gitignore patterns
    gitignore_dirs = parse_gitignore(root)
    skip_dirs = SKIP_DIRS | gitignore_dirs

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        dir_path = Path(dirpath)

        for name in filenames:
            full_path = dir_path / name
            rel = _relative_under_root(root, full_path)
            if rel is not None:
                all_files.append(rel)

                # Collect Python scripts
                if name.endswith(".py"):
                    script_paths.append(full_path)

    return sorted(all_files), script_paths


class IOVisitor(ast.NodeVisitor):
    """
    AST visitor that collects file reads, writes, and string literals from a script.

    Strong I/O heuristics:
      - open("file", "r" or default)  => reads
      - open("file", "w"/"a"/"x"/"+") => writes
      - pandas-like reads:
          .read_csv/.read_json/.read_excel/.read_parquet => reads
      - pandas-like writes:
          .to_csv/.to_json/.to_excel/.to_parquet/.to_file => writes
      - Generic helpers:
          attributes starting with read_/load_ treated as read
          attributes starting with to_ or containing write/save treated as write

    Only string literal first arguments are considered for strong edges.

    Additionally, all string literals in the file are collected so we can
    later match basenames against real files (a weak "mentioned_by" signal).
    """

    READ_FUNCS = {"read_csv", "read_json", "read_excel", "read_parquet"}
    WRITE_FUNCS = {"to_csv", "to_json", "to_excel", "to_parquet", "to_file"}

    def __init__(self) -> None:
        super().__init__()
        self.reads: Set[str] = set()
        self.writes: Set[str] = set()
        self.string_literals: Set[str] = set()

    def visit_Constant(self, node: ast.Constant) -> Any:  # type: ignore[override]
        """Collect all string literal constants."""
        if isinstance(node.value, str):
            self.string_literals.add(node.value)

    def visit_Call(self, node: ast.Call) -> Any:  # type: ignore[override]
        """Inspect function calls for strong I/O patterns."""
        func = node.func

        if isinstance(func, ast.Name) and func.id == "open":
            self._handle_open(node)
        elif isinstance(func, ast.Attribute):
            self._handle_attribute_call(func, node)

        self.generic_visit(node)

    def _get_literal_arg(self, node: ast.Call, index: int) -> Optional[str]:
        """Return the string literal argument at the given index, if present."""
        if index >= len(node.args):
            return None
        arg = node.args[index]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value
        return None

    def _get_mode(self, node: ast.Call) -> Optional[str]:
        """Return the mode argument (if any) for an open() call."""
        if len(node.args) >= 2:
            mode_arg = node.args[1]
            if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, str):
                return mode_arg.value

        for kw in node.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                return kw.value.value

        return None

    def _handle_open(self, node: ast.Call) -> None:
        """Handle open(...) calls and classify as read or write."""
        filename = self._get_literal_arg(node, 0)

        # If first arg is not a literal, try to extract from Path division (DATA_DIR / "file.csv")
        if not filename and len(node.args) > 0:
            arg = node.args[0]
            # Check for BinOp with / operator (Path division)
            if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Div):
                # Try to get the right operand (the filename part)
                if isinstance(arg.right, ast.Constant) and isinstance(arg.right.value, str):
                    filename = arg.right.value

        if not filename:
            return

        mode = self._get_mode(node)

        if mode is None or "r" in mode:
            self.reads.add(filename)

        if mode and any(ch in mode for ch in ("w", "a", "x", "+")):
            self.writes.add(filename)

    def _handle_attribute_call(self, func: ast.Attribute, node: ast.Call) -> None:
        """Handle attribute calls like df.to_csv(...) or pd.read_csv(...) or Path(...).open(...)."""
        attr = func.attr

        # Handle Path(...).open() pattern
        if attr == "open":
            self._handle_path_open(func, node)
            return

        # Existing logic for pandas methods...
        filename = self._get_literal_arg(node, 0)
        if not filename:
            return

        if attr in self.READ_FUNCS or attr.startswith(("read_", "load_")):
            self.reads.add(filename)
            return

        # Match write methods but exclude file.write() which writes content to already-open files
        if (
            attr in self.WRITE_FUNCS
            or attr.startswith("to_")
            or attr.startswith(("write_", "save_"))
        ):
            self.writes.add(filename)

    def _handle_path_open(self, func: ast.Attribute, node: ast.Call) -> None:
        """Handle Path(...).open(...) patterns."""
        # Try to extract filename from Path construction
        filename = None

        # Check if func.value is a Call to Path() with a string literal
        if isinstance(func.value, ast.Call):
            filename = self._get_literal_arg(func.value, 0)

        # Check if func.value is a BinOp with / operator (DATA_DIR / "file.csv")
        if not filename and isinstance(func.value, ast.BinOp) and isinstance(func.value.op, ast.Div):
            if isinstance(func.value.right, ast.Constant) and isinstance(func.value.right.value, str):
                filename = func.value.right.value

        # If we found a literal path, classify it
        if filename:
            mode = self._get_mode(node)

            if mode is None or "r" in mode:
                self.reads.add(filename)

            if mode and any(ch in mode for ch in ("w", "a", "x", "+")):
                self.writes.add(filename)


def analyze_script(
    script_path: Path, root: Path, basename_index: Dict[str, List[str]]
) -> Tuple[List[str], List[str], List[str], List[str], IOVisitor]:
    """
    Analyze a single Python script and return:
      - list of resolved read file paths (relative to root)
      - list of resolved write file paths (relative to root)
      - list of unresolved read paths (raw strings for non-existent files)
      - list of unresolved write paths (raw strings for non-existent files)
      - IOVisitor instance (for string literal information)
    """
    try:
        source = script_path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: Failed to read {script_path}: {exc}", file=sys.stderr)
        return [], [], [], [], IOVisitor()

    try:
        tree = ast.parse(source, filename=str(script_path))
    except SyntaxError as exc:
        print(f"WARNING: Failed to parse {script_path}: {exc}", file=sys.stderr)
        return [], [], [], [], IOVisitor()

    visitor = IOVisitor()
    visitor.visit(tree)

    reads: Set[str] = set()
    writes: Set[str] = set()
    unresolved_reads: Set[str] = set()
    unresolved_writes: Set[str] = set()

    for ref in visitor.reads:
        rel = _resolve_referenced_path(root, script_path, ref, basename_index)
        if rel:
            reads.add(rel)
        else:
            # Capture unresolved read targets (files that don't exist)
            unresolved_reads.add(ref)

    for ref in visitor.writes:
        rel = _resolve_referenced_path(root, script_path, ref, basename_index)
        if rel:
            writes.add(rel)
        else:
            # Capture unresolved write targets (files that don't exist yet)
            unresolved_writes.add(ref)

    return (
        sorted(reads),
        sorted(writes),
        sorted(unresolved_reads),
        sorted(unresolved_writes),
        visitor,
    )


def _resolve_referenced_path(
    root: Path, script_path: Path, referenced: str, basename_index: Dict[str, List[str]]
) -> Optional[str]:
    """
    Try multiple strategies to resolve a path reference.

    Strategy 1: Try relative to script directory
    Strategy 2: If no slashes in path, try basename lookup in global file index
    Strategy 3: Try relative to project root
    """
    candidate = Path(referenced)

    # Strategy 1: Try relative to script directory
    if not candidate.is_absolute():
        script_relative = script_path.parent / candidate
        if script_relative.exists():
            return _relative_under_root(root, script_relative)

    # Strategy 2: If no slashes in path, try basename lookup in global file index
    if "/" not in referenced and "\\" not in referenced:
        matches = basename_index.get(referenced, [])
        if len(matches) == 1:
            return matches[0]  # Exactly one match - use it

    # Strategy 3: Try relative to project root
    if not candidate.is_absolute():
        root_relative = root / candidate
        if root_relative.exists():
            return _relative_under_root(root, root_relative)

    return None


def _infer_ydata_reports(
    scripts: List[Dict[str, Any]],
    file_relations: Dict[str, Dict[str, Any]],
    all_files: List[str],
) -> None:
    """
    Infer YData HTML report outputs via project-specific heuristics.

    Pattern: Scripts that read CSV files in DATA/ generate HTML reports in PROFILES/
    with the naming pattern: {csv_stem}_ydata_report.html
    """
    # Find all *_ydata_report.html files
    html_reports = [f for f in all_files if f.endswith("_ydata_report.html") and "PROFILES" in f]

    for html_path in html_reports:
        # Extract CSV stem from HTML filename
        # e.g., "bank-full_ydata_report.html" -> "bank-full"
        html_filename = os.path.basename(html_path)
        if not html_filename.endswith("_ydata_report.html"):
            continue

        csv_stem = html_filename[: -len("_ydata_report.html")]

        # Find matching CSV in DATA directory
        csv_filename = f"{csv_stem}.csv"
        csv_candidates = [f for f in all_files if f.endswith(csv_filename) and "DATA" in f]

        if not csv_candidates:
            continue

        # For each matching CSV, find scripts that read it or mention it
        for csv_path in csv_candidates:
            # Find scripts that read this CSV or have it in related_files
            for script in scripts:
                mentioned = csv_path in script.get("reads", []) or csv_path in script.get("related_files", [])

                if mentioned:
                    # Add HTML to script's heuristic_writes
                    if html_path not in script["heuristic_writes"]:
                        script["heuristic_writes"].append(html_path)

                    # Add script to HTML's written_by
                    html_info = file_relations.get(html_path)
                    if html_info and script["path"] not in html_info["written_by"]:
                        html_info["written_by"].append(script["path"])


def _infer_jsonl_to_csv(
    scripts: List[Dict[str, Any]],
    file_relations: Dict[str, Dict[str, Any]],
    all_files: List[str],
) -> None:
    """
    Infer JSONL to CSV conversion outputs for jsonl_to_simple_tabular.py.

    This is a script-specific heuristic for the pattern:
      {stem}_scalar.csv and {stem}_nested_fields.csv from {stem}.jsonl
    """
    # Find scripts ending with jsonl_to_simple_tabular.py
    for script in scripts:
        if not script["path"].endswith("jsonl_to_simple_tabular.py"):
            continue

        # Look for .jsonl file in reads or related_files
        jsonl_files = [f for f in script.get("reads", []) + script.get("related_files", []) if f.endswith(".jsonl")]

        if not jsonl_files:
            continue

        # Upgrade JSONL files from related_files to reads (strong edge)
        for jsonl_path in jsonl_files:
            if jsonl_path not in script["reads"]:
                script["reads"].append(jsonl_path)
                # Update file_relations to reflect this is a read
                jsonl_info = file_relations.get(jsonl_path)
                if jsonl_info and script["path"] not in jsonl_info["read_by"]:
                    jsonl_info["read_by"].append(script["path"])

        for jsonl_path in jsonl_files:
            # Extract stem from JSONL filename
            jsonl_filename = os.path.basename(jsonl_path)
            stem = jsonl_filename[: -len(".jsonl")]

            # Construct expected CSV output filenames
            scalar_csv = f"{stem}_scalar.csv"
            nested_csv = f"{stem}_nested_fields.csv"

            # Find these CSV files in the project
            for csv_filename in [scalar_csv, nested_csv]:
                csv_candidates = [f for f in all_files if f.endswith(csv_filename)]

                for csv_path in csv_candidates:
                    # Add to heuristic_writes
                    if csv_path not in script["heuristic_writes"]:
                        script["heuristic_writes"].append(csv_path)

                    # Add script to CSV's written_by
                    csv_info = file_relations.get(csv_path)
                    if csv_info and script["path"] not in csv_info["written_by"]:
                        csv_info["written_by"].append(script["path"])


def build_manifest(root: Path) -> Dict[str, Any]:
    """
    Build a manifest by:

      1. Indexing all files under root (skipping SKIP_DIRS).
      2. Analyzing Python scripts for strong read/write edges.
      3. Linking scripts and files via weak "mentioned_by" edges based on
         filename string literals.
    """
    root = root.resolve()

    # Single filesystem walk to collect all files and scripts
    all_files, script_paths = collect_files_and_scripts(root)

    basename_index: Dict[str, List[str]] = {}
    for rel in all_files:
        base = os.path.basename(rel)
        basename_index.setdefault(base, []).append(rel)

    scripts: List[Dict[str, Any]] = []
    file_relations: Dict[str, Dict[str, Any]] = {}

    for rel in all_files:
        full_path = root / rel
        file_relations[rel] = {
            "path": rel,
            **get_file_metadata(full_path),
            "read_by": [],
            "written_by": [],
            "mentioned_by": [],
        }

    # Analyze all Python scripts
    for script_path in script_paths:
        rel_script = _relative_under_root(root, script_path)
        if rel_script is None:
            continue

        reads, writes, unresolved_reads, unresolved_writes, visitor = analyze_script(
            script_path, root, basename_index
        )

        script_entry: Dict[str, Any] = {
            "path": rel_script,
            **get_file_metadata(script_path),
            "reads": reads,
            "writes": writes,
            "unresolved_reads": unresolved_reads,
            "unresolved_writes": unresolved_writes,
            "heuristic_writes": [],
            "related_files": [],
        }

        for f in reads:
            info = file_relations.get(f)
            if info is not None and rel_script not in info["read_by"]:
                info["read_by"].append(rel_script)

        for f in writes:
            info = file_relations.get(f)
            if info is not None and rel_script not in info["written_by"]:
                info["written_by"].append(rel_script)

        related: Set[str] = set()
        for literal in visitor.string_literals:
            base = os.path.basename(literal)

            # Skip self-references to the manifest output
            if base == MANIFEST_OUTPUT:
                continue

            candidates = basename_index.get(base)
            if not candidates:
                continue
            for candidate in candidates:
                related.add(candidate)
                info = file_relations.get(candidate)
                if info is not None and rel_script not in info["mentioned_by"]:
                    info["mentioned_by"].append(rel_script)

        script_entry["related_files"] = sorted(related)
        scripts.append(script_entry)

    # Apply project-specific heuristics
    _infer_ydata_reports(scripts, file_relations, all_files)
    _infer_jsonl_to_csv(scripts, file_relations, all_files)

    scripts.sort(key=lambda s: s["path"])
    for script in scripts:
        script["reads"].sort()
        script["writes"].sort()
        script["unresolved_reads"].sort()
        script["unresolved_writes"].sort()
        script["heuristic_writes"].sort()
    for info in file_relations.values():
        info["read_by"].sort()
        info["written_by"].sort()
        info["mentioned_by"].sort()

    manifest: Dict[str, Any] = {
        "root": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scripts": scripts,
        "files": sorted(file_relations.values(), key=lambda x: x["path"]),
    }
    return manifest


def pprint_manifest(manifest: Dict[str, Any]) -> None:
    """Pretty-print a human-readable summary of the manifest."""
    root = manifest.get("root", "<unknown>")
    generated_at = manifest.get("generated_at", "<unknown>")
    scripts = manifest.get("scripts", [])
    files = manifest.get("files", [])

    print("=" * 80)
    print("Directory Manifest Summary")
    print("=" * 80)
    print(f"Root directory: {root}")
    print(f"Generated at : {generated_at}")
    print(f"Total scripts  : {len(scripts)}")
    print(f"Total files    : {len(files)}")
    print()

    print("Scripts:")
    print("--------")
    if not scripts:
        print("No Python scripts found under this root.")
    else:
        for script in scripts:
            path = script.get("path", "<unknown>")
            reads = script.get("reads", [])
            writes = script.get("writes", [])
            unresolved_reads = script.get("unresolved_reads", [])
            unresolved_writes = script.get("unresolved_writes", [])
            heuristic_writes = script.get("heuristic_writes", [])
            related = script.get("related_files", [])

            print(f"- {path}")
            if reads:
                print("    reads:")
                for r in reads:
                    print(f"      - {r}")
            if writes:
                print("    writes:")
                for w in writes:
                    print(f"      - {w}")
            if unresolved_reads:
                print("    unresolved_reads (source files don't exist):")
                for ur in unresolved_reads:
                    print(f"      - {ur}")
            if unresolved_writes:
                print("    unresolved_writes (target files don't exist yet):")
                for uw in unresolved_writes:
                    print(f"      - {uw}")
            if heuristic_writes:
                print("    heuristic_writes (medium-confidence pattern inference):")
                for hw in heuristic_writes:
                    print(f"      - {hw}")
            if related:
                print("    related_files (basename matches, weaker signal):")
                for rf in related:
                    print(f"      - {rf}")
            if (
                not reads
                and not writes
                and not unresolved_reads
                and not unresolved_writes
                and not heuristic_writes
                and not related
            ):
                print("    (no detectable relationships)")
        print()

    print("Files:")
    print("------")
    if not files:
        print("No files found under this root.")
    else:
        for info in files:
            path = info.get("path", "<unknown>")
            read_by = info.get("read_by", [])
            written_by = info.get("written_by", [])
            mentioned_by = info.get("mentioned_by", [])

            print(f"- {path}")
            if read_by:
                print("    read_by:")
                for s in read_by:
                    print(f"      - {s}")
            if written_by:
                print("    written_by:")
                for s in written_by:
                    print(f"      - {s}")
            if mentioned_by:
                print("    mentioned_by (basename string match):")
                for s in mentioned_by:
                    print(f"      - {s}")
            if not read_by and not written_by and not mentioned_by:
                print("    (no scripts detected using or mentioning this file)")
        print()

    print("=" * 80)
    print("End of manifest summary")
    print("=" * 80)


def _remove_weak_edges(manifest: Dict[str, Any]) -> None:
    """Remove weak edges (related_files and mentioned_by) from manifest."""
    for script in manifest.get("scripts", []):
        script["related_files"] = []

    for file_info in manifest.get("files", []):
        file_info["mentioned_by"] = []


def _filter_unused_files(manifest: Dict[str, Any]) -> None:
    """Remove files with no relationships from manifest."""
    files = manifest.get("files", [])
    filtered_files = []

    for file_info in files:
        # Keep file if it has any relationships
        has_relationships = (
            file_info.get("read_by")
            or file_info.get("written_by")
            or file_info.get("mentioned_by")
        )

        if has_relationships:
            filtered_files.append(file_info)

    manifest["files"] = filtered_files


def main() -> None:
    """Parse CLI arguments, build manifest, write it, and pretty-print it."""
    parser = argparse.ArgumentParser(
        description="Generate a manifest of file relationships in the project"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=None,
        help="Target directory (default: current working directory)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Skip pretty-print output to stdout, just write JSON file",
    )
    parser.add_argument(
        "--no-weak-edges",
        action="store_true",
        help="Suppress related_files and mentioned_by (weak edges)",
    )
    parser.add_argument(
        "--filter-unused",
        action="store_true",
        help="Exclude files with no relationships from output",
    )

    args = parser.parse_args()
    target_dir = Path(args.directory) if args.directory else Path.cwd()

    if not target_dir.exists() or not target_dir.is_dir():
        print(
            f"ERROR: Target directory does not exist or is not a directory: {target_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    manifest = build_manifest(target_dir)

    # Apply post-processing based on flags
    if args.no_weak_edges:
        _remove_weak_edges(manifest)
    if args.filter_unused:
        _filter_unused_files(manifest)

    manifest_path = target_dir / "directory_manifest.json"
    write_manifest(manifest_path, manifest)

    if not args.quiet:
        loaded_manifest = read_manifest(manifest_path) or manifest
        pprint_manifest(loaded_manifest)


if __name__ == "__main__":
    main()
