---
name: directory-manifest
description: >
  Maintain and interpret a directory manifest (JSON) that captures script-to-file relationships. Use when you need to answer questions like: which scripts read or write a file, what pipeline exists between files and scripts, or whether certain artifacts appear unused.
allowed-tools: ["Read", "Write", "Bash"]
---

# Directory Manifest Skill

## Overview
This skill includes a manifest generator script (`manifest_directory.py` in this skill directory)
and produces a manifest file (`directory_manifest.json` in the target directory). It allows Claude to:

- Regenerate the manifest when needed
- Load and parse the manifest
- Answer questions about file and script relationships
- Distinguish between strong, heuristic and weak edges

## When to Use
Trigger this skill when:
- You want to explore how files and scripts relate (e.g., "what generates this CSV?")
- You're planning refactors and need to know what pipelines exist
- You suspect there are unused files and want to detect them
- You're onboarding into a codebase and need to map data flows

## Instructions

### 1. Locate the Generator Script
The generator script is bundled with this skill at:
```
.claude/skills/directory-manifest/scripts/manifest_directory.py
```
Look for an existing `directory_manifest.json` in the target directory to determine if regeneration is needed.

### 2. Regenerate Manifest (if needed)

Use the Bash tool to run the manifest generator:
```bash
# Example: Regenerate manifest quietly for current directory
python3 .claude/skills/directory-manifest/scripts/manifest_directory.py --quiet

# Or specify a target directory
python3 .claude/skills/directory-manifest/scripts/manifest_directory.py /path/to/target --quiet
```

**Available flags:**
- `--quiet` / `-q`: Skip pretty-print, only write JSON
- `--no-weak-edges`: Suppress `related_files` and `mentioned_by` (weak edges)
- `--filter-unused`: Exclude files with no relationships
- Combine flags as needed: `--quiet --filter-unused --no-weak-edges`

### 3. Load and Parse Manifest

Use the Read tool to load `directory_manifest.json` and parse it as JSON.

For quick queries, you can use jq via the Bash tool:
```bash
# Example: Find scripts matching a pattern
cat directory_manifest.json | jq '.scripts[] | select(.path | contains("foo"))'
```

### 4. Understand the Schema

The manifest JSON has this structure:

**Top-level structure (reference):**
```json
{
  "root": "/absolute/path/to/project",
  "generated_at": "2025-11-25T04:15:48.055696+00:00",
  "scripts": [...],
  "files": [...]
}
```

**Script entry (reference):**
```json
{
  "path": "relative/path/to/script.py",
  "size_bytes": 2739,
  "modified_at": "2025-11-24T12:52:14.302435+00:00",
  "extension": ".py",
  "reads": ["data/input.csv"],                    // High confidence (AST-detected)
  "writes": ["output/result.json"],               // High confidence (AST-detected)
  "unresolved_reads": ["missing_input.txt"],      // Source files that don't exist
  "unresolved_writes": ["future_output.csv"],     // Target files not yet created
  "heuristic_writes": ["reports/output.html"],    // Medium confidence (pattern-based)
  "related_files": ["data/referenced.csv"]        // Low confidence (basename mention)
}
```

**File entry (reference):**
```json
{
  "path": "data/input.csv",
  "size_bytes": 524288,
  "modified_at": "2025-11-24T14:23:45+00:00",
  "extension": ".csv",
  "read_by": ["scripts/process.py"],              // Scripts that read this file
  "written_by": ["scripts/generate.py"],          // Scripts that write this file
  "mentioned_by": ["scripts/analyze.py"]          // Scripts that mention this filename
}
```

### 5. Edge Types and Confidence Levels

**High Confidence (AST-detected):**
- `reads` / `writes`: Literal paths in `open()`, `.read_csv()`, `.to_csv()`, etc.
- Direct evidence from parsing Python AST
- Most reliable edges

**Medium Confidence (Pattern-based):**
- `heuristic_writes`: Project-specific pattern inference
- Example: YData reports `{stem}_ydata_report.html` from `{stem}.csv`
- Example: JSONL→CSV conversion `{stem}_scalar.csv` from `{stem}.jsonl`
- Reliable for known patterns but not AST-verified

**Low Confidence (String matching):**
- `related_files` / `mentioned_by`: Basename appears in script's string literals
- Very weak signal but useful for navigation
- Many false positives (e.g., comments, error messages)

**Intent without Resolution:**
- `unresolved_reads`: Script tries to read a file that doesn't exist
- `unresolved_writes`: Script intends to write to a path not yet created
- Captures intent even when files are missing

### 6. Common Query Patterns

Use jq via the Bash tool for quick queries. Examples:

**What generates this file?**
```bash
# Example query
cat directory_manifest.json | jq '.files[] | select(.path == "data/output.csv") | .written_by'
```

**What does this script produce?**
```bash
# Example query
cat directory_manifest.json | jq '.scripts[] | select(.path | contains("process")) | {writes, heuristic_writes, unresolved_writes}'
```

**Find unused files:**
```bash
# Example query
cat directory_manifest.json | jq '.files[] | select(.read_by == [] and .written_by == [] and .mentioned_by == []) | .path'
```

**Map a pipeline:**
```bash
# Example: Find all scripts that write to files that script X reads
cat directory_manifest.json | jq '.scripts[] | select(.path == "scripts/analyze.py") | .reads[] as $file | .files[] | select(.path == $file) | .written_by[]'
```

**Check if a file is referenced anywhere:**
```bash
# Example query
cat directory_manifest.json | jq '.files[] | select(.path == "data/mystery.csv") | {read_by, written_by, mentioned_by}'
```

### 7. Answering User Questions

**Q: "What scripts use this CSV?"**
1. Look up the file in `manifest.files[]`
2. Report `.read_by` (readers) and `.mentioned_by` (mentions)
3. Explain confidence levels

**Q: "What does this script produce?"**
1. Find script in `manifest.scripts[]`
2. Report `.writes` (high confidence), `.heuristic_writes` (medium), `.unresolved_writes` (intent)
3. Distinguish between existing files and future outputs

**Q: "Are there any orphaned files?"**
1. Filter files where all relationship arrays are empty
2. Consider using `--filter-unused` flag for cleaner manifest
3. Present list with sizes/ages for prioritization

**Q: "How do I trace this data pipeline?"**
1. Start with target file, find `.written_by` scripts
2. For each script, find `.reads` to identify inputs
3. Recursively trace upstream until you hit source data
4. Present as a dependency chain

### 8. Best Practices

**Regenerate when:**
- Files are added/removed/renamed
- Scripts modify their I/O patterns
- Starting a new task that requires fresh data
- Use `--quiet` flag in scripts/CI

**Interpret conservatively:**
- Trust `reads`/`writes` (high confidence)
- Verify `heuristic_writes` if making critical decisions
- Ignore `related_files` unless no stronger edges exist
- Check `unresolved_*` for broken references or future work

**Combine with code search:**
- Manifest shows *what* relationships exist
- Grep/search shows *how* they're implemented
- Use manifest for overview, code for details

### 9. Troubleshooting

**Empty `reads`/`writes` arrays:**
- Scripts may use dynamic paths (variables, f-strings)
- Check `unresolved_*` for non-existent files
- Look at `related_files` for weak signals
- Consider adding project-specific heuristics

**False positives in `mentioned_by`:**
- Common with error messages, comments, documentation
- Focus on `read_by`/`written_by` for reliable info
- Use `--no-weak-edges` to hide noise

**Missing expected files:**
- Check if they're in `.gitignore` (auto-skipped)
- Verify they're not in `SKIP_DIRS` (.git, venv, node_modules, etc.)
- Files might be in ignored directories (tmp/, .vscode/, etc.)

### 10. Example Session

**User:** "What generates the bank-full_ydata_report.html file?"

**Approach:** Query the manifest to find which scripts write to this file:
```bash
# Example query
cat directory_manifest.json | jq '.files[] | select(.path | contains("bank-full_ydata_report.html")) | .written_by'
```

**Example output:** `["REFERENCE/examples-ydata-profiling/banking_data.py"]`

**Explanation:** The `banking_data.py` script generates this HTML report. This is a medium-confidence edge (heuristic inference based on the YData naming pattern: `{csv_stem}_ydata_report.html`). You can verify by checking the script's `heuristic_writes` field or examining the source code.

---

## Quick Reference Card

| Question | Query |
|----------|-------|
| What creates file X? | `.files[] \| select(.path == "X") \| .written_by` |
| What does script Y produce? | `.scripts[] \| select(.path == "Y") \| {writes, heuristic_writes}` |
| What does script Y read? | `.scripts[] \| select(.path == "Y") \| .reads` |
| Find unused files | `.files[] \| select(.read_by == [] and .written_by == [])` |
| Files script Y mentions | `.scripts[] \| select(.path == "Y") \| .related_files` |
| Trace upstream from file X | Start with `.written_by`, then check each script's `.reads` |
