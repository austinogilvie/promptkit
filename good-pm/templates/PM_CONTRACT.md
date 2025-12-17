<!--
PROGRESSIVE DISCLOSURE NOTE:
This file is NOT injected on every prompt. Instead, a minimal stub (PM_STUB.md)
is injected, and this full contract is read on-demand by PM commands when
detailed conventions are needed.

To update the stub: templates/PM_STUB.md
To update full conventions: this file (PM_CONTRACT.md)
-->

# Good PM Contract

> This document defines the vocabulary, conventions, and rules for filesystem-based project management. It is loaded on-demand by PM commands (see PM_STUB.md for the lightweight context injected on every prompt).

---

## Status Values

Status is **derived from checkbox state** in each file. Never set status manually.

| Status | Definition | Checkbox State |
|--------|------------|----------------|
| **Open** | No work started | 0 of N checked |
| **In Progress** | Work underway | 1+ of N checked (not all) |
| **Complete** | All tasks done | N of N checked |

### Status Transitions

```
Open ──────► In Progress ──────► Complete
(0/N)         (1+/N)              (N/N)
```

- Check a box → status may change to "In Progress"
- Check final box → status becomes "Complete"
- Uncheck a box → status may revert

---

## Checkbox Syntax

Use standard GitHub-flavored markdown checkboxes:

```markdown
- [ ] Unchecked task (counts as incomplete)
- [x] Checked task (counts as complete)
- [X] Also valid checked syntax
```

**Parsing rules:**
- Only `- [ ]` and `- [x]`/`- [X]` at line start are counted
- Nested checkboxes count equally
- Code blocks are ignored
- Checkboxes in comments are ignored

---

## Naming Conventions

### Specs

- **Pattern:** `SPEC_<name>.md`
- **Location:** `.good-pm/specs/`
- **Name format:** kebab-case, lowercase, a-z 0-9 hyphens only
- **Max length:** 64 characters

**Examples:**
- `SPEC_user-authentication.md`
- `SPEC_api-v2-migration.md`
- `SPEC_bugfix-login-timeout.md`

### Issues

- **Pattern:** `NNN-<description>.md`
- **Location:** `.good-pm/issues/`
- **NNN:** Zero-padded 3-digit number (001, 002, ... 999)
- **Description:** kebab-case, derived from title

**Examples:**
- `001-setup-database-schema.md`
- `042-implement-oauth-flow.md`
- `100-write-api-documentation.md`

---

## Directory Structure

```
.good-pm/
├── context/
│   ├── PM_CONTRACT.md          # This file (loaded on-demand by commands)
│   ├── PM_STUB.md              # Lightweight stub (injected every prompt)
│   └── session-update.md       # Stop hook instructions
├── session/
│   └── current.md              # Ephemeral work state (auto-injected if has content)
├── specs/
│   └── SPEC_<name>.md          # Specification documents
├── issues/
│   └── NNN-<description>.md    # Issue files
├── templates/
│   ├── SPEC_TEMPLATE.md        # Template for new specs
│   ├── ISSUE_TEMPLATE.md       # Template for new issues
│   └── SESSION_TEMPLATE.md     # Template for session context
└── INDEX.md                    # Navigation and quick links
```

---

## Frontmatter Fields

### Specs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Human-readable spec title |
| status | enum | Derived | Open, In Progress, Complete |
| created | date | Yes | YYYY-MM-DD format |
| updated | date | Yes | YYYY-MM-DD format |

### Issues

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Action-oriented title |
| source | path | Yes | Relative path to parent spec |
| status | enum | Derived | Open, In Progress, Complete |
| dependencies | list | No | Issue numbers or "None" |

---

## Relationships

### Spec → Issues

Specs are broken down into issues via `/good-pm:create-issues`. Each issue's `Source` section links back to its parent spec.

### Issue → Spec

Every issue should have a `## Source` section containing:

```markdown
## Source
This issue is part of the work defined in: `../specs/SPEC_<name>.md`
```

### Unlinked Issues

Issues without a valid Source section are "unlinked" and reported separately in status views.

---

## Commands Reference

| Command | Purpose |
|---------|---------|
| `/good-pm:setup` | Initialize Good PM in a project |
| `/good-pm:create-spec` | Generate a spec from summary or draft |
| `/good-pm:create-issues` | Break a spec into numbered issues |
| `/good-pm:issues` | Display status summary |

---

## Session Context

The session context file (`.good-pm/session/current.md`) tracks ephemeral work state between conversations.

### Four Sections

| Section | Purpose |
|---------|---------|
| **Active Spec** | Currently focused specification |
| **In Progress Issues** | Issues being actively worked on |
| **Blockers** | Obstacles preventing completion |
| **Notes for Next Session** | Context needed to resume work |

### Injection Behavior

- Session context is auto-injected on `UserPromptSubmit` (after PM_STUB.md)
- Only injected if file contains meaningful content (not just placeholders)
- Updated via the Stop hook before conversation ends

### Updating Session Context

The Stop hook prompts for session context review before ending conversations. Apply the Future Self test to determine what to include.

---

## Progressive Disclosure

Context injection uses **progressive disclosure** to minimize token overhead while preserving full functionality.

### Two-Tier Loading Model

| File | When Loaded | Size | Purpose |
|------|-------------|------|---------|
| PM_STUB.md | Every prompt (via hook) | ~20 lines | Quick reference, command list |
| PM_CONTRACT.md | On-demand (by commands) | ~270 lines | Full conventions and rules |

### Loading Decision Matrix

| Scenario | What Loads |
|----------|------------|
| Non-PM directory | Nothing (hook exits silently) |
| PM project, any prompt | PM_STUB.md (~400 tokens) |
| PM project, session has content | PM_STUB.md + session context |
| PM project, running PM command | Command reads PM_CONTRACT.md |

### Why Progressive Disclosure

- **Token efficiency:** ~90% reduction in per-prompt overhead for non-PM work
- **Noise reduction:** Detailed conventions only loaded when relevant
- **Project isolation:** Each project's PM state stays separate

### How It Works

The `good-pm-context.sh` hook injects the lightweight stub:

```bash
STUB="$GOODPM_DIR/context/PM_STUB.md"

if [ -f "$STUB" ]; then
  cat "$STUB"    # ~20 lines instead of ~270
fi
```

PM commands explicitly read this full contract when detailed conventions are needed:
- **PM commands still work** — they load PM_CONTRACT.md as part of execution
- **Non-PM work is unaffected** — only minimal stub context is injected
- **Subdirectories inherit** — running from `src/` in a PM project still gets stub context

---

## Progress Calculation

**Issue progress:** `checked_boxes / total_boxes`

**Spec progress:** Aggregated from linked issues:
- Sum of all checked boxes across linked issues
- Divided by sum of all total boxes across linked issues

---

## The Future Self Test

When updating session context, apply this filter:

**"If I started a new conversation tomorrow, would this information change how I respond?"**

| Answer | Action |
|--------|--------|
| **YES** | Save it to session context |
| **NO** | Don't save it |

### Examples That PASS (Save These)

| Information | Why It Passes |
|-------------|---------------|
| "Waiting on API key from client" | Blocker that affects what work can continue |
| "User prefers functional style over classes" | Changes implementation approach |
| "Issue 005 depends on external PR #123" | External dependency not visible in checkboxes |
| "Decided to use Redis over Memcached for X reason" | Decision context for future questions |

### Examples That FAIL (Don't Save)

| Information | Why It Fails |
|-------------|--------------|
| "Completed issue 003" | Checkbox state already captures this |
| "Fixed the login bug" | Git history shows this |
| "Looked up OAuth2 spec" | Session-specific research |
| "Files changed: auth.ts, config.ts" | `git diff` shows this |

### Anti-Patterns to Avoid

- **Task completion logs** — That's what checkboxes are for
- **Session-specific research** — Store in project docs if reusable
- **Git-recoverable information** — Commits capture this
- **Transient debugging notes** — Resolved issues don't need memory

---

*This contract is the source of truth for Good PM terminology and behavior.*
