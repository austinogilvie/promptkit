---
description: Detailed documentation for Good PM commands and concepts.
argument-hint: "[command-name]"
---

# Good PM Help

Comprehensive documentation for the Good PM project management plugin.

## Arguments

Parse `$ARGUMENTS` for one optional positional argument:

- `$1` (optional) — **command-name**: Show help for a specific command

| Argument | Shows |
|----------|-------|
| (none) | Full help documentation |
| `setup` | Setup command details |
| `create-spec` | Spec creation details |
| `create-issues` | Issue breakdown details |
| `issues` | Status display details |

---

## Overview

Good PM is a **filesystem-based project management plugin** for Claude Code. It provides:

- **Specification documents** for planning features and changes
- **Issue files** for tracking discrete, completable tasks
- **Automatic status derivation** from checkbox state
- **Session context** for handoff between conversations

### Core Principles

1. **Files are the source of truth** — No external databases or services
2. **Status comes from checkboxes** — Never set status manually
3. **Progressive disclosure** — Minimal context until PM work begins
4. **Future Self test** — Only save information that changes future behavior

---

## Commands

### /good-pm:setup

Initialize Good PM in the current repository.

#### Usage

```bash
/good-pm:setup              # Standard initialization
/good-pm:setup --force      # Overwrite existing installation
/good-pm:setup --no-settings  # Skip hook installation
```

#### Arguments

| Argument | Effect |
|----------|--------|
| `--force` | Overwrite existing `.good-pm/` directory |
| `--no-settings` | Skip hook script installation |

#### What It Creates

```
.good-pm/
├── context/
│   ├── PM_CONTRACT.md      # Full conventions (loaded on-demand)
│   ├── PM_STUB.md          # Lightweight stub (injected every prompt)
│   └── session-update.md   # Stop hook instructions
├── session/
│   └── current.md          # Ephemeral work state
├── specs/                  # Specification documents
├── issues/                 # Issue files
├── templates/
│   ├── SPEC_TEMPLATE.md
│   ├── ISSUE_TEMPLATE.md
│   └── SESSION_TEMPLATE.md
└── INDEX.md                # Navigation
```

#### Hooks Installed

| Hook | Event | Purpose |
|------|-------|---------|
| `good-pm-context.sh` | UserPromptSubmit | Inject PM context |
| `good-pm-session-update.py` | Stop | Update session context |

#### Errors

| Condition | Message |
|-----------|---------|
| Already initialized | "Good PM is already initialized. Use `--force` to overwrite." |
| Cannot create dirs | "Failed to create directory: [path]. Check permissions." |
| Cannot write files | "Failed to write file: [path]. Check permissions." |

---

### /good-pm:create-spec

Create a structured specification document.

#### Usage

```bash
# From text summary
/good-pm:create-spec user-auth "OAuth2 with Google and GitHub providers"

# From draft file
/good-pm:create-spec api-cache ./notes/caching-ideas.md
```

#### Arguments

| Position | Name | Description |
|----------|------|-------------|
| `$1` | name | Spec name in kebab-case (required) |
| `$2` | input | Text summary OR path to draft file (required) |

#### Name Validation

| Rule | Validation |
|------|------------|
| Format | Lowercase kebab-case: `a-z`, `0-9`, `-` |
| Length | Maximum 64 characters |
| Pattern | `^[a-z][a-z0-9]*(-[a-z0-9]+)*$` |
| No edge hyphens | Cannot start or end with `-` |
| No consecutive | Cannot contain `--` |

**Valid:** `user-auth`, `api-v2`, `bugfix-login`
**Invalid:** `UserAuth`, `api_cache`, `-leading`, `trailing-`

#### Input Detection

| Input | Detected As | Behavior |
|-------|-------------|----------|
| Ends with `.md` AND file exists | File mode | Parse and synthesize |
| Otherwise | Text mode | Use as summary |

#### Text Mode

- Summary max: 256 characters
- Creates spec with summary in Overview section
- Other sections contain `[TODO: Fill in]` placeholders

#### File Mode

- Reads draft content
- Synthesizes into structured spec sections
- Maps draft content to appropriate sections
- **Deletes original draft file** after synthesis

#### Spec Sections

Every spec includes:

| Section | Content |
|---------|---------|
| Overview | High-level description |
| Problem Statement | What problem this solves |
| Goals | What must be achieved (checkboxes) |
| Non-Goals | Explicit scope exclusions |
| Background & Context | Prior art, references |
| Proposed Solution | Technical approach |
| Implementation Plan | Phased breakdown (checkboxes) |
| Acceptance Criteria | Definition of done (checkboxes) |
| Open Questions | Unresolved decisions |
| Dependencies | Requirements and blockers |
| Risks & Mitigations | Potential issues |
| References | Links and resources |

#### Output

```
Created spec: .good-pm/specs/SPEC_user-auth.md

The spec has been initialized with your summary. Fill in the sections:
  - Overview: Expand on the summary
  - Problem Statement: What problem does this solve?
  - Goals: What must this achieve? (use checkboxes)
  - Proposed Solution: Technical approach
  - Implementation Plan: Break into phases
  - Acceptance Criteria: How do we know it's done?

When ready, break into issues:
  /good-pm:create-issues .good-pm/specs/SPEC_user-auth.md
```

#### Errors

| Condition | Message |
|-----------|---------|
| Not initialized | "Good PM is not initialized. Run `/good-pm:setup` first." |
| Empty name | "Name is required. Usage: `/good-pm:create-spec <name> <summary>`" |
| Invalid name | "Invalid name '{{name}}'. Use lowercase kebab-case." |
| Name too long | "Name '{{name}}' exceeds 64 characters." |
| Empty input | "Summary or draft file is required." |
| Summary too long | "Summary exceeds 256 characters. Use a draft file." |
| Spec exists | "Spec already exists: `.good-pm/specs/SPEC_{{name}}.md`" |
| Draft not found | "Draft file not found: `{{path}}`" |

---

### /good-pm:create-issues

Break a specification into discrete issue files.

#### Usage

```bash
/good-pm:create-issues .good-pm/specs/SPEC_user-auth.md
```

#### Arguments

| Position | Name | Description |
|----------|------|-------------|
| `$1` | spec-path | Path to spec file (required) |

#### Parsing Logic

The command extracts work items from:

1. **Implementation Plan** — Primary source of tasks
   - Phase names become issue groupings
   - Checkbox items become issue tasks

2. **Goals** — If no Implementation Plan
   - Each goal may become an issue

3. **Acceptance Criteria** — Verification points
   - Mapped to issue acceptance criteria

#### Issue Generation Rules

| Guideline | Description |
|-----------|-------------|
| Atomic | Each issue = one logical unit of work |
| Focused | Completable in one session |
| Ordered | Dependencies flow from earlier to later |
| Testable | Has verifiable acceptance criteria |
| Action-oriented | Title starts with verb |

#### Issue Numbering

- Pattern: `NNN-<description>.md`
- Scans existing issues to find highest number
- New issues start at `highest + 1`
- If no issues exist, starts at `001`

#### Issue Template

Each generated issue contains:

```markdown
## Title
[Action-oriented title]

## Source
This issue is part of the work defined in: `../specs/SPEC_{{name}}.md`

## Description
[Context and goals]

## Tasks
- [ ] Task 1
  - [ ] Subtask if applicable
- [ ] Task 2

## Acceptance Criteria
- [ ] Criteria from spec

## Dependencies
[Previous issue number or "None"]
```

#### Dependencies Logic

| Issue Position | Dependencies |
|----------------|--------------|
| First issue | `None` |
| Sequential | Previous issue number |
| Parallel-capable | `None` or shared parent |

#### Output

```
Created 5 issues from SPEC_user-auth.md:

  001-setup-database.md
  002-implement-login.md
  003-implement-register.md
  004-add-validation.md
  005-write-tests.md

Issues written to: .good-pm/issues/
Updated: .good-pm/INDEX.md

View status with:
  /good-pm:issues
```

#### Errors

| Condition | Message |
|-----------|---------|
| Not initialized | "Good PM is not initialized. Run `/good-pm:setup` first." |
| Missing template | "Missing template. Run `/good-pm:setup --force` to reinstall." |
| Empty path | "Spec path is required." |
| Spec not found | "Spec file not found: `{{path}}`" |
| Not markdown | "Expected a markdown file, got: `{{path}}`" |
| No tasks found | "No tasks found in spec. Add an Implementation Plan with checkbox items." |

---

### /good-pm:issues

Display status summary of specs and issues.

#### Usage

```bash
/good-pm:issues              # Current directory
/good-pm:issues ./my-project  # Specific path
```

#### Arguments

| Position | Name | Description |
|----------|------|-------------|
| `$1` | project-path | Path to project (optional, default: `.`) |

#### Status Derivation

Status is **calculated from checkbox state**, never set manually:

| Checkbox State | Status |
|----------------|--------|
| 0 of N checked | **Open** |
| Some checked (not all) | **In Progress** |
| N of N checked | **Complete** |
| No checkboxes | **No Tasks** (flag for review) |

#### Checkbox Patterns

```markdown
- [ ] Unchecked (incomplete)
- [x] Checked (complete)
- [X] Also valid checked
```

Only checkboxes at line start are counted. Nested checkboxes count equally.

#### Output Format

```markdown
# project-name

## Specs

| Spec | Status | Progress | Issues |
|------|--------|----------|--------|
| SPEC_user-auth | In Progress | 7/12 (58%) | 5 |

## Issues

### SPEC_user-auth

| # | Title | Status | Progress |
|---|-------|--------|----------|
| 001 | setup-database | Complete | 3/3 |
| 002 | implement-login | In Progress | 2/5 |
| 003 | add-validation | Open | 0/4 |

## Summary

- **Specs:** 0 complete, 1 in progress
- **Issues:** 1 complete, 1 in progress, 1 open
- **Next:** `003-add-validation.md`
```

#### Spec-Issue Relationships

Issues link to specs via their `## Source` section:

```markdown
## Source
This issue is part of the work defined in: `../specs/SPEC_user-auth.md`
```

Issues without valid Source sections are reported as **Unlinked**.

#### Progress Calculation

- **Issue progress:** `checked_boxes / total_boxes`
- **Spec progress:** Aggregated across all linked issues

#### What This Command Does NOT Do

- Modify any files (read-only)
- Move files to archive directories
- Fix broken references
- Create missing specs or issues

This command **observes and reports**.

#### Errors

| Condition | Message |
|-----------|---------|
| Not initialized | "Good PM is not initialized. Run `/good-pm:setup` first." |
| Path not found | "Directory not found: `{{path}}`" |
| Not a directory | "Not a directory: `{{path}}`" |

---

## Concepts

### The Future Self Test

When updating session context, ask:

> "If I started a new conversation tomorrow, would this information change how I respond?"

| Answer | Action |
|--------|--------|
| **YES** | Save to session context |
| **NO** | Don't save |

#### Examples That PASS (Save These)

| Information | Why |
|-------------|-----|
| "Waiting on API key from client" | Blocker affecting work |
| "User prefers functional style" | Changes implementation |
| "Issue 005 depends on PR #123" | External dependency |
| "Decided Redis over Memcached for X" | Decision context |

#### Examples That FAIL (Don't Save)

| Information | Why |
|-------------|-----|
| "Completed issue 003" | Checkbox captures this |
| "Fixed the login bug" | Git history shows this |
| "Looked up OAuth2 spec" | Session-specific research |
| "Files changed: auth.ts" | `git diff` shows this |

#### Anti-Patterns

- Task completion logs — Use checkboxes
- Session-specific research — Store in docs if reusable
- Git-recoverable information — Commits capture this
- Transient debugging notes — Resolved issues don't need memory

---

### Status Derivation

Status flows automatically from checkbox state:

```
Open ──────► In Progress ──────► Complete
(0/N)         (1+/N)              (N/N)
```

#### Examples

**Open (0/3):**
```markdown
- [ ] Create schema
- [ ] Add migration
- [ ] Seed data
```

**In Progress (2/3):**
```markdown
- [x] Create schema
- [x] Add migration
- [ ] Seed data
```

**Complete (3/3):**
```markdown
- [x] Create schema
- [x] Add migration
- [x] Seed data
```

**No Tasks (0/0):**
```markdown
## Tasks
(Tasks will be added during implementation)
```

---

### Naming Conventions

#### Specs

| Rule | Value |
|------|-------|
| Pattern | `SPEC_<name>.md` |
| Location | `.good-pm/specs/` |
| Format | kebab-case, lowercase |
| Characters | `a-z`, `0-9`, `-` |
| Max length | 64 characters |

**Examples:** `SPEC_user-auth.md`, `SPEC_api-v2.md`

#### Issues

| Rule | Value |
|------|-------|
| Pattern | `NNN-<description>.md` |
| Location | `.good-pm/issues/` |
| NNN | Zero-padded 3 digits (001-999) |
| Description | kebab-case from title |

**Examples:** `001-setup-database.md`, `042-oauth-flow.md`

---

### Progressive Disclosure

Good PM uses **tiered context loading** to minimize token overhead:

| Tier | File | When Loaded | Size |
|------|------|-------------|------|
| 0 | PM_STUB.md | Every prompt | ~400 tokens |
| 1 | PM_CONTRACT.md | On-demand by commands | ~3,500 tokens |
| 2 | help.md | When user runs `/good-pm:help` | Full docs |

#### Why This Matters

- **~78% token savings** on non-PM prompts
- **Full functionality preserved** for PM work
- **Fast hook execution** via early exit checks

---

## Troubleshooting

### "Good PM is not initialized"

Run `/good-pm:setup` in the project root.

### Spec already exists

Choose a different name or delete the existing spec manually.

### No tasks found in spec

Add an `## Implementation Plan` section with checkbox items:

```markdown
## Implementation Plan

### Phase 1: Setup
- [ ] Create database schema
- [ ] Add migration scripts
```

### Issues not linked to spec

Ensure each issue has a `## Source` section with valid spec path:

```markdown
## Source
This issue is part of the work defined in: `../specs/SPEC_name.md`
```

### Status not updating

Status is derived from checkboxes. Check:
- Checkboxes use correct syntax: `- [ ]` or `- [x]`
- Checkboxes are at line start (not indented with spaces before `-`)
- File is saved after changes

### Hook not running

Verify hooks are installed:
```bash
ls -la .claude/hooks/good-pm-*
```

Re-run setup if missing: `/good-pm:setup --force`

---

## Quick Reference

| Task | Command |
|------|---------|
| Initialize | `/good-pm:setup` |
| Create spec | `/good-pm:create-spec name "summary"` |
| Break into issues | `/good-pm:create-issues .good-pm/specs/SPEC_name.md` |
| View status | `/good-pm:issues` |
| Get help | `/good-pm:help [command]` |

---

*For full conventions, see `.good-pm/context/PM_CONTRACT.md`*
