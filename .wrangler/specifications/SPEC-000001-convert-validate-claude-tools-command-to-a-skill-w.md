---
id: SPEC-000001
title: >-
  Convert validate-claude-tools command to a skill with updated unified
  skills/commands schema
type: specification
status: closed
priority: high
labels:
  - specification
  - skills
  - validation
  - tooling
createdAt: '2026-02-02T14:11:25.741Z'
updatedAt: '2026-02-02T14:23:41.639Z'
project: promptkit
---
# Specification: validate-claude-tools Skill Conversion

## Executive Summary

**What:** Convert the existing `/validate-claude-tools` slash command (`.claude/commands/validate-claude-tools.md`) into a proper Claude Code skill (`.claude/skills/validating-claude-tools/SKILL.md`) and update all validation logic to reflect the unified skills/commands model introduced by Anthropic.

**Why:** Anthropic merged Skills and Slash Commands into a single concept. The current validator treats them as separate tool types with different frontmatter schemas, producing false positives when validating skills that use fields like `disable-model-invocation`, `argument-hint`, `context`, or `user-invocable`. The validator is also a slash command living in `.claude/commands/`, which is now a legacy location.

**Scope:**
- **Included:** Convert to skill, rewrite frontmatter schemas, merge skills/commands validation, add new field checks, update cross-reference logic, update output format, update false-positive guards
- **Excluded:** Auto-fix mode (documented as future enhancement), validation of MCP server configs, validation of hook scripts in `settings.json`, validating skills outside `.claude/` (e.g., `~/.claude/skills/`)

## Goals and Non-Goals

### Goals

1. Produce a skill that validates `.claude/` tools using the **correct, current** Anthropic schema — no false positives from the old skills-vs-commands split
2. Recognize all valid skill frontmatter fields: `name`, `description`, `allowed-tools`, `argument-hint`, `user-invocable`, `disable-model-invocation`, `context`, `agent`
3. Validate agents with their own distinct schema (agents are NOT skills — that distinction still exists)
4. Detect legacy commands in `.claude/commands/` and flag them for migration
5. Maintain the existing output contract: console summary tables + `CLAUDE_MEMO_AI_TOOLS_REVIEW.md` memo file
6. Follow project naming conventions (gerund-form skill name, directory matches `name` field)

### Non-Goals

- Implementing auto-fix mode (`--fix`)
- Validating user-level skills in `~/.claude/skills/`
- Validating hook scripts or `settings.json`
- Validating Wrangler plugin tools
- Changing the memo output file name or overall structure (preserve backward compatibility for anyone parsing it)

## Background & Context

### Problem Statement

Anthropic unified Skills and Slash Commands into a single system. The key changes:

1. **Skills and commands are the same thing.** Skills live in `.claude/skills/<name>/SKILL.md`. The old `.claude/commands/` location is legacy but still functional.
2. **The frontmatter schema expanded.** Skills now support fields that were previously command-only (`argument-hint`) plus entirely new fields (`context`, `agent`, `user-invocable`, `disable-model-invocation`).
3. **Agents remain a separate concept** with their own schema (`tools:` not `allowed-tools:`, plus `model:`, `permissionMode:`, `skills:`).

The current validator at `.claude/commands/validate-claude-tools.md` encodes the old three-type model (skills, commands, agents) and flags valid skill fields as errors.

### Current State

The validator is a slash command in `.claude/commands/validate-claude-tools.md` (372 lines). It:

- Defines three separate frontmatter schemas: Skills (3 fields), Commands (4 fields), Agents (6 fields)
- Has separate validation sections for "Skills" and "Slash Commands"
- Flags `disable-model-invocation` and `argument-hint` on skills as errors
- Does not know about `context`, `agent`, or `user-invocable` fields
- Cross-reference checks assume commands and skills are in separate directories
- False-positive table references the three-type model

**Concrete evidence of breakage:** Running `/validate-claude-tools .claude/skills/normalize-pencil/` produced 3 false-positive errors:
- E1: `disable-model-invocation: true` flagged as "not a valid skill frontmatter field"
- E2: `argument-hint:` flagged as "a command field, not valid for skills"
- E3: `/normalize-pencil` invocation syntax flagged as "slash command pattern in a skill"

All three are valid under the new unified model.

### Proposed State

A skill at `.claude/skills/validating-claude-tools/SKILL.md` that:

- Uses a **single unified schema** for skills (covering both `.claude/skills/` and legacy `.claude/commands/`)
- Keeps a **separate schema for agents** (agents remain distinct)
- Validates all 8 skill frontmatter fields correctly
- Validates field interdependencies (e.g., `agent` requires `context: fork`)
- Flags legacy `.claude/commands/` files as migration candidates
- Produces the same output format (console tables + memo file)

## Requirements

### Functional Requirements

#### FR-001: Unified Skill Frontmatter Schema

The validator MUST recognize these fields as valid for skills (both `.claude/skills/*/SKILL.md` and legacy `.claude/commands/*.md`):

```yaml
name: skill-name                        # Required (max 64 chars, lowercase + numbers + hyphens)
description: What and when              # Required (max 1024 chars, no XML tags)
allowed-tools: ["Read", "Write"]        # Optional - tools allowed without permission
argument-hint: <arg1> [arg2]            # Optional - hint shown during autocomplete
user-invocable: true | false            # Optional - show/hide from slash menu (default: true)
disable-model-invocation: true | false  # Optional - prevent Claude auto-invocation (default: false)
context: fork                           # Optional - run in isolated subagent
agent: Explore | Plan | general-purpose # Optional - agent type when context: fork
```

#### FR-002: Agent Frontmatter Schema (unchanged)

The validator MUST continue to recognize these fields as valid for agents (`.claude/agents/*.md`):

```yaml
name: agent-name                        # Required (max 64 chars)
description: What this agent does       # Required (max 1024 chars, no XML tags)
tools: Read, Write, Bash                # Optional (NOT allowed-tools)
model: sonnet | opus | haiku | inherit  # Optional (default: inherit)
permissionMode: default | acceptEdits | bypassPermissions | plan | ignore  # Optional
skills: skill1, skill2                  # Optional
color: green | blue | red | ...         # Optional
```

#### FR-003: Field Interdependency Validation

The validator MUST check these field relationships:

| Field | Constraint | Severity |
|-------|-----------|----------|
| `agent` present without `context: fork` | ERROR — `agent` only valid when `context: fork` is set |
| `context` value other than `fork` | ERROR — only valid value is `fork` |
| `user-invocable` not boolean | ERROR — must be `true` or `false` |
| `disable-model-invocation` not boolean | ERROR — must be `true` or `false` |
| `agent` value not in allowed set | ERROR — must be `Explore`, `Plan`, or `general-purpose` |
| Agent file using `allowed-tools` instead of `tools` | ERROR — agents use `tools:` field |
| Skill file using `tools` instead of `allowed-tools` | WARNING — skills use `allowed-tools:` field |

#### FR-004: Legacy Command Detection

The validator MUST:
- Scan `.claude/commands/` for markdown files
- Validate them using the **unified skill schema** (same rules as skills)
- Emit a WARNING for each file suggesting migration to `.claude/skills/<name>/SKILL.md`
- NOT treat them as a different tool type with different validation rules

#### FR-005: Classification Logic

The validator MUST classify tools by file path:
- `.claude/skills/*/SKILL.md` → Skill
- `.claude/commands/*.md` → Legacy Skill (validate as skill, flag for migration)
- `.claude/agents/*.md` → Agent

There are only **two schemas**: skills and agents. No third "command" schema.

#### FR-006: Cross-Reference Validation

The validator MUST check:

**Skill → File references:**
- All markdown links in SKILL.md resolve to existing files in the skill directory
- All referenced scripts exist and have valid syntax
- No orphaned files in `scripts/`, `references/`, `templates/` subdirectories

**Skill → Skill references:**
- If a skill body mentions `/other-skill`, check that the skill exists in **either** `.claude/skills/` or `.claude/commands/` (legacy)

**Agent → Skill references:**
- If an agent has `skills:` field, each named skill exists in `.claude/skills/`

**Agent → Tool references:**
- If an agent lists `tools:`, each tool name should be a recognized Claude tool

#### FR-007: Output Contract

The validator MUST produce:

1. **Console summary** with tables: Errors, Warnings, Cross-Reference Issues, Top Improvements
2. **Memo file** at `CLAUDE_MEMO_AI_TOOLS_REVIEW.md` in project root with: Executive Summary, Inventory table, Detailed Findings per tool, Global Recommendations, Checklist for Fixes

The inventory table MUST use these categories:

| Type | Count | With Errors | With Warnings |
|------|-------|-------------|---------------|
| Skills | X | Y | Z |
| Agents | X | Y | Z |
| Legacy Commands | X | Y | Z |

#### FR-008: Existing Validation Checks (preserve)

All existing checks that are still valid MUST be preserved:

**Structure validation:**
- SKILL.md exists in skill directory
- YAML frontmatter has opening and closing `---` delimiters
- Required fields present: `name`, `description`
- `name` format: lowercase, numbers, hyphens only, max 64 chars
- `description` non-empty, max 1024 chars, no XML tags
- No reserved words in name: "anthropic", "claude"

**Naming convention:**
- Directory name matches `name` field in frontmatter
- Name uses gerund form (verb + -ing) — WARNING level, not ERROR

**Best practices (WARNING level):**
- Description includes both what the skill does AND when to use it
- Description includes trigger phrases/keywords
- SKILL.md body under 500 lines
- Progressive disclosure: explicit "Read X when Y" for bundled files
- Forward slashes in file references
- Scripts documented for when to run vs read
- No placeholder text: `[TODO]`, `[PLACEHOLDER]`, `TBD`, `xxx`
- Code blocks have language hints

**Script validation:**
- Valid syntax (Python: `py_compile`, Bash: `bash -n`)
- Executable permissions on shell scripts
- Usage documentation (docstring or header comment)
- Referenced in SKILL.md

**Agent-specific checks (preserve as-is):**
- `tools:` field (NOT `allowed-tools:`)
- `model:` value validation
- Description explains when to invoke
- Body includes examples
- Clear scope definition

### Non-Functional Requirements

- **Correctness:** Zero false positives from the old three-type schema. Every field flagged as invalid must genuinely be invalid under the current unified model.
- **Completeness:** Every file in `.claude/` is classified and validated — nothing silently skipped.
- **Clarity:** Every error and warning includes a specific, copy-paste-ready fix instruction.

## Architecture

### File Structure

```
.claude/skills/validating-claude-tools/
├── SKILL.md                    # Main skill definition (~400 lines)
└── (no scripts needed — validation is instruction-driven)
```

The skill is pure markdown instructions. Claude performs the validation by reading files, checking frontmatter, and running syntax checks via Bash. No bundled scripts required.

### Skill Frontmatter

```yaml
---
name: validating-claude-tools
description: >-
  Validate Claude AI tools in .claude/ against Anthropic best practices.
  Use when asked to validate, audit, check, or review Claude tools,
  skills, commands, or agents. Also use after creating or modifying
  any tool in .claude/.
user-invocable: true
disable-model-invocation: true
argument-hint: "[path/to/validate]"
allowed-tools: ["Read", "Write", "Bash", "Glob", "Grep"]
---
```

Key decisions:
- `disable-model-invocation: true` — validation is destructive to context (reads many files, produces long output). Only invoke explicitly.
- `user-invocable: true` — appears in `/` menu as `/validating-claude-tools`
- `allowed-tools` includes Bash for syntax checking (`python3 -c "import py_compile; ..."`, `bash -n`)

### Validation Logic Flow

```
1. Inventory phase
   ├── Glob .claude/skills/*/SKILL.md → classify as Skills
   ├── Glob .claude/commands/*.md → classify as Legacy Skills
   └── Glob .claude/agents/*.md → classify as Agents

2. Per-tool validation phase
   ├── Read file, parse frontmatter
   ├── Apply correct schema (skill schema OR agent schema)
   ├── Check field values and interdependencies
   ├── Check naming conventions
   ├── Check best practices
   └── Run cross-reference checks

3. Cross-reference phase
   ├── Resolve all internal links
   ├── Check for orphaned files
   ├── Verify skill↔agent references
   └── Verify skill↔skill references

4. Output phase
   ├── Write CLAUDE_MEMO_AI_TOOLS_REVIEW.md
   └── Print console summary tables
```

## Implementation Details

### Key Sections to Write in SKILL.md

The SKILL.md body needs these sections:

1. **Frontmatter Schemas** — the authoritative unified skill schema and agent schema (replaces the current three-schema section)
2. **Validation Framework** — merged skills section (absorbing commands), preserved agents section, preserved CLAUDE.md/reference/script sections
3. **Field Interdependency Rules** — new section for `context`/`agent`/`user-invocable`/`disable-model-invocation` validation
4. **Legacy Command Detection** — new section for migration warnings
5. **Cross-Reference Validation** — updated to check both `.claude/skills/` and `.claude/commands/`
6. **False Positive Guards** — expanded table with all valid skill fields
7. **Analysis Process** — updated classification (two types, not three)
8. **Output Format** — updated inventory categories, same overall structure
9. **Fix Templates** — updated labels, new templates for new fields

### Migration from Command to Skill

The old command file (`.claude/commands/validate-claude-tools.md`) should be deleted after the skill is created. The skill replaces it entirely.

### Changes Summary by Section

| Current Section | Action | Notes |
|----------------|--------|-------|
| Frontmatter Schemas: Skills | **Rewrite** | Add 5 new fields to schema |
| Frontmatter Schemas: Commands | **Remove** | Merged into Skills schema |
| Frontmatter Schemas: Agents | **Keep** | Agents unchanged |
| Key distinction note | **Update** | Two types (skills, agents), not three |
| Validation: Skills | **Extend** | Add new field checks, interdependency rules |
| Validation: Slash Commands | **Remove** | Merge useful checks into Skills section |
| Validation: Agents | **Keep** | Unchanged |
| Validation: CLAUDE.md | **Keep** | Unchanged |
| Validation: References | **Keep** | Unchanged |
| Validation: Scripts | **Keep** | Unchanged |
| Cross-Reference: Agent→Skill | **Keep** | Unchanged |
| Cross-Reference: Command→Agent | **Rename** | Becomes Skill→Agent, check both dirs |
| Cross-Reference: Skill→File | **Keep** | Unchanged |
| Cross-Reference: Orphan detection | **Keep** | Unchanged |
| False Positives table | **Extend** | Add 6 new rows for valid skill fields |
| Analysis Process | **Update** | Two types, not three |
| Output: Console | **Update** | "Legacy Commands" replaces "Commands" |
| Output: Memo template | **Update** | Same |
| Fix Templates | **Update** | Labels, add new field templates |

## Open Questions & Decisions

### Resolved Decisions

| Decision | Options Considered | Chosen | Rationale |
|----------|-------------------|--------|-----------|
| Skill name | `validate-claude-tools`, `validating-claude-tools` | `validating-claude-tools` | Project convention: gerund form for skills |
| Scripts needed? | Bundled Python/Bash scripts vs pure instructions | Pure instructions | Validation is Claude reading files and checking patterns — no need for scripts. Keeps the skill simple and maintainable. |
| Legacy command handling | Ignore `.claude/commands/`, Error on them, Warn about them | Warn + validate as skills | Non-breaking, helpful. Users shouldn't be forced to migrate immediately. |
| `context: fork`? | Run in fork vs main context | Main context (`context` omitted) | Validation reads many project files and writes a memo — needs full file access. Forking would lose the working directory context. |
| Delete old command? | Keep both, delete old | Delete old command | Two validators with different schemas would cause confusion. Clean break. |

### Open Questions

- [ ] **Q1: Should the validator check `model:` on skills?** Skills don't currently document a `model:` field, but some skills in the wild have `version:` (e.g., `writing-documentation`). Should unknown fields produce warnings?
  - **Impact:** Determines strictness of frontmatter validation
  - **Options:** (a) Warn on any unrecognized field, (b) Ignore unknown fields, (c) Maintain an explicit allowlist
  - **Recommendation:** Option (a) — warn on unrecognized fields. This catches typos and drift without blocking functionality.

- [ ] **Q2: Should the `create-skill` command also be updated?** It currently scaffolds skills but may use the old schema.
  - **Impact:** New skills created by `/create-skill` might not include new frontmatter options
  - **Recommendation:** Out of scope for this spec. Create a follow-up issue.

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Anthropic adds more frontmatter fields in the future | High | Medium | Structure the schema section to be easy to extend. Add a note: "If Anthropic adds new fields, update the schema here." |
| Old command not deleted, causing two validators | Low | High | Implementation checklist explicitly includes deleting the old command file |
| False-positive regression (new validator flags valid things) | Medium | High | Test against all 6 existing skills + 3 agents in this project before considering complete |

## Success Criteria

### Launch Criteria

- [ ] Skill exists at `.claude/skills/validating-claude-tools/SKILL.md`
- [ ] Old command at `.claude/commands/validate-claude-tools.md` is deleted
- [ ] Running `/validating-claude-tools` against the full `.claude/` directory produces zero false positives
- [ ] Running against `normalize-pencil` specifically produces zero false positives (the three false positives from the old validator are gone)
- [ ] All 6 existing skills, 3 agents, and 6 legacy commands validate correctly
- [ ] `CLAUDE_MEMO_AI_TOOLS_REVIEW.md` is produced with correct inventory categories
- [ ] New frontmatter fields (`context`, `agent`, `user-invocable`, `disable-model-invocation`) are validated when present

### Verification Test Cases

| Test | Input | Expected Result |
|------|-------|----------------|
| normalize-pencil | `.claude/skills/normalize-pencil/` | 0 errors (was 3 false positives with old validator) |
| writing-documentation skill | `.claude/skills/writing-documentation/` | `version` field flagged as WARNING (unrecognized), not error |
| Legacy command | `.claude/commands/create-skill.md` | WARNING: migration suggested. Validated as skill. |
| Agent with `tools:` | `.claude/agents/issues-housekeeper.md` | PASS — `tools:` is correct for agents |
| Skill with `context: fork` + `agent: Explore` | Hypothetical skill | PASS — valid combination |
| Skill with `agent: Explore` but no `context: fork` | Hypothetical skill | ERROR — `agent` requires `context: fork` |
| Skill with `context: blah` | Hypothetical skill | ERROR — only valid value is `fork` |
| Full .claude/ scan | No arguments | All tools inventoried, categorized, validated |

## References

### Related Specifications

- None (this is standalone tooling)

### Related Issues

- Previous validation run against `normalize-pencil` (this conversation) — demonstrated the false-positive problem

### External Resources

- Anthropic Skills documentation: https://code.claude.com/docs/en/skills
- Anthropic Slash Commands documentation: https://code.claude.com/docs/en/slash-commands
- Anthropic Subagents documentation: https://code.claude.com/docs/en/sub-agents
- Anthropic CLAUDE.md best practices: https://www.anthropic.com/engineering/claude-code-best-practices

## Appendix

### Glossary

- **Skill:** A markdown file in `.claude/skills/<name>/SKILL.md` that provides instructions to Claude. Can be user-invoked via `/name` or auto-invoked by Claude based on context.
- **Legacy Command:** A markdown file in `.claude/commands/` — functionally identical to a skill but in the old location. Still works but should be migrated.
- **Agent:** A markdown file in `.claude/agents/` that defines a specialized subagent persona with its own system prompt, tools, and context window. Agents are NOT skills — they have a different schema.
- **Frontmatter:** YAML metadata between `---` delimiters at the top of a markdown file.
- **Context Fork:** Running a skill in an isolated subagent (`context: fork`). The skill's content becomes the subagent's prompt. Results return to the main conversation without intermediate work.
- **False Positive:** The validator incorrectly flags a valid configuration as an error.

### Assumptions

- Anthropic's unified model is stable and the documented fields are authoritative
- The existing `.claude/` directory in this project is representative of typical usage
- Agents remain a separate concept from skills (not merged)

### Constraints

- The skill must be pure markdown instructions (no bundled scripts) to keep it simple and maintainable
- Output format must remain backward-compatible: same memo filename, same table structure
- Must work when invoked with a specific path argument OR with no arguments (full `.claude/` scan)
