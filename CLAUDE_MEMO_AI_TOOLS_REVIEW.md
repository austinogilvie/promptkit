# Claude AI Tools Review

**Generated:** 2026-02-02
**Scope:** `.claude/skills/normalize-pencil/`

## Executive Summary

The `normalize-pencil` skill is well-structured with valid frontmatter, working scripts, correct cross-references, and no orphaned files. **No errors were found.** Four warnings were identified: the skill name does not use gerund form, the description lacks trigger phrases for auto-matching, the `docopt` external dependency is undocumented, and `reference.md` has drifted from `map_tokens.py` (missing the `text-gray-600` mapping).

## Inventory

| Type | Count | With Errors | With Warnings |
|------|-------|-------------|---------------|
| Skills | 1 | 0 | 1 |
| Agents | 0 | 0 | 0 |
| Legacy Commands | 0 | 0 | 0 |
| Other | 0 | 0 | 0 |

## Detailed Findings

### Skills

#### normalize-pencil
**Status:** WARNINGS

**Files found:**
- `SKILL.md` (74 lines)
- `reference.md` (60 lines)
- `examples.md` (25 lines)
- `scripts/map_tokens.py` (440 lines) — valid Python syntax, executable
- `scripts/scan.sh` (74 lines) — valid Bash syntax, executable

---

**Errors:**

(none)

**Warnings:**

1. **W1: Naming convention — should use gerund form**
   Best practice for skill names is the gerund form (verb + -ing). `normalize-pencil` should be `normalizing-pencil`.

   ```diff
   - name: normalize-pencil
   + name: normalizing-pencil
   ```
   Note: This also requires renaming the directory from `normalize-pencil/` to `normalizing-pencil/`.

2. **W2: Description lacks trigger phrases / "when to use" context**
   The description says *what* the skill does but not *when* to use it. Best practice is to include trigger phrases so Claude can match the skill to user intent. (Since `disable-model-invocation: true` is set, this has reduced impact, but would matter if auto-invocation is ever enabled.)

   Current:
   ```yaml
   description: Normalize Pencil/MCP-generated UI code to Cloakling's design system (tokens, primitives, shadows, z-index, spacing).
   ```

   Suggested:
   ```yaml
   description: Normalize Pencil/MCP-generated UI code to Cloakling's design system (tokens, primitives, shadows, z-index, spacing). Use when reviewing Pencil output, cleaning up generated UI code, or enforcing design system token compliance.
   ```

3. **W3: External dependency `docopt` not documented**
   `scripts/map_tokens.py` imports `docopt` (line 49), a third-party Python package not in the standard library. This dependency is not mentioned in SKILL.md. If `docopt` is not installed, the script will fail with an ImportError.

   Suggested addition to SKILL.md:
   ```markdown
   ## Prerequisites
   - Python 3.8+
   - `docopt` — install with `pip install docopt`
   - `rg` (ripgrep) — install with `brew install ripgrep`
   ```

4. **W4: Drift between `reference.md` and `map_tokens.py`**
   The Python script maps `text-gray-600` → `text-[var(--foreground-secondary)]` (line 141), but this mapping is absent from `reference.md`. The reference table should be the authoritative source of truth.

   Add to `reference.md` under "Tailwind literal replacements":
   ```markdown
   - `text-gray-600` → `text-[var(--foreground-secondary)]`
   ```

---

**Suggestions:**

1. **S1: Add `allowed-tools` to frontmatter.** Consider adding `allowed-tools: ["Bash", "Read"]` to pre-approve the tools this skill needs for its scan/apply workflow, reducing permission prompts.

2. **S2: Expand `examples.md`** to include z-index normalization and copy regression fix examples, since those are opt-in features that users may not discover.

3. **S3: Code blocks in `examples.md` use inline backticks.** Consider using fenced code blocks with `jsx` or `tsx` language hints for better readability.

---

**Cross-Reference Validation:**

| Check | Status | Notes |
|-------|--------|-------|
| `reference.md` link in SKILL.md | PASS | Lines 39 and 68 |
| `examples.md` link in SKILL.md | PASS | Line 69 |
| `scripts/scan.sh` link in SKILL.md | PASS | Lines 50 and 73 |
| `scripts/map_tokens.py` link in SKILL.md | PASS | Lines 52 and 74 |
| Orphan check: `reference.md` | PASS | Referenced by SKILL.md |
| Orphan check: `examples.md` | PASS | Referenced by SKILL.md |
| Orphan check: `scripts/scan.sh` | PASS | Referenced by SKILL.md |
| Orphan check: `scripts/map_tokens.py` | PASS | Referenced by SKILL.md |
| Python syntax valid | PASS | `py_compile` succeeds |
| Bash syntax valid | PASS | `bash -n` succeeds |
| Executable permissions (scan.sh) | PASS | `-rwxr-xr-x` |
| Executable permissions (map_tokens.py) | PASS | `-rwxr-xr-x` |
| Scripts have usage docs | PASS | Both have docstrings/header comments |
| Placeholder text check | PASS | No `[TODO]`, `TBD`, `xxx` found |
| SKILL.md under 500 lines | PASS | 74 lines |

---

**Mapping consistency check (reference.md vs map_tokens.py):**

| Mapping | In reference.md | In map_tokens.py | Status |
|---------|----------------|-------------------|--------|
| `--pencil-accent` → `--accent-interactive` | Yes | Yes | PASS |
| `--pencil-accent-hover` → `--accent-attention` | Yes | Yes | PASS |
| `--pencil-text-primary` → `--foreground-primary` | Yes | Yes | PASS |
| `--pencil-text-secondary` → `--foreground-secondary` | Yes | Yes | PASS |
| `--pencil-text-muted` → `--foreground-muted` | Yes | Yes | PASS |
| `--pencil-bg` → `--surface-base` | Yes | Yes | PASS |
| `--pencil-surface` → `--surface-level-1` | Yes | Yes | PASS |
| `--pencil-surface-muted` → `--surface-level-1` | Yes | Yes | PASS |
| `--pencil-border` → `--border-default` | Yes | Yes | PASS |
| `--pencil-border-strong` → `--border-strong` | Yes | Yes | PASS |
| `bg-white` → tokenized | Yes | Yes | PASS |
| `bg-gray-50` → tokenized | Yes | Yes | PASS |
| `text-gray-900` → tokenized | Yes | Yes | PASS |
| `text-gray-700` → tokenized | Yes | Yes | PASS |
| `text-gray-600` → tokenized | **No** | Yes | **DRIFT** |
| `text-gray-500` → tokenized | Yes | Yes | PASS |
| `text-gray-400` → tokenized | Yes | Yes | PASS |
| `border-gray-200` → tokenized | Yes | Yes | PASS |
| `border-gray-300` → tokenized | Yes | Yes | PASS |

---

**Script Validation:**

| Script | Syntax | Executable | Docs | External Deps |
|--------|--------|------------|------|---------------|
| `map_tokens.py` | PASS | PASS | PASS (docstring) | `docopt` (WARNING: undocumented) |
| `scan.sh` | PASS | PASS | PASS (header comment) | `rg` (documented in script) |

## Previous Review Corrections

The prior version of this memo (also dated 2026-02-02) contained **3 false-positive errors** that have been removed:

1. ~~E1: `disable-model-invocation` flagged as invalid~~ — This is a valid skill frontmatter field per the unified skill/command schema.
2. ~~E2: `argument-hint` flagged as invalid~~ — This is a valid skill frontmatter field that provides slash autocomplete hints.
3. ~~E3: Skill body describing `/normalize-pencil` invocation syntax flagged as invalid~~ — Skills ARE slash commands in the unified model; describing `/skill-name` invocation is standard practice.

These are explicitly documented as false positives in the validation checklist.

## Global Recommendations

1. **Sync `reference.md` with `map_tokens.py`.** The `text-gray-600` drift shows these can diverge. Consider adding a comment in the Python code noting `reference.md` as the authoritative source, or adding a CI check.

2. **Document the `docopt` dependency** so the skill doesn't fail on systems without it installed.

3. **Adopt gerund naming** (`normalizing-pencil`) to align with the Anthropic skill naming convention used across the ecosystem.

## Checklist for Fixes

- [ ] Add `text-gray-600` → `text-[var(--foreground-secondary)]` to `reference.md` (W4)
- [ ] Document `docopt` and `rg` prerequisites in SKILL.md (W3)
- [ ] Consider renaming to gerund form `normalizing-pencil` (W1)
- [ ] Optionally expand description with trigger phrases (W2)
