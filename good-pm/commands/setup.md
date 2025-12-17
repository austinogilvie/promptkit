---
description: Initialize Good PM in the current repository.
argument-hint: "[--force] [--no-settings]"
---

# /good-pm:setup

Initialize Good PM project management in the current repository.

## Arguments

- `--force` — Overwrite existing `.good-pm/` directory
- `--no-settings` — Skip hook script installation

## Instructions

1. Read `.good-pm/context/PM_CONTRACT.md` for conventions if it exists (Decision D1)
2. Check if `.good-pm/` exists (error unless `--force`)
3. Create directory structure and copy templates from plugin
4. Install hooks (unless `--no-settings`)
5. Output success message

## What It Creates

```
.good-pm/
├── context/PM_CONTRACT.md, PM_STUB.md, session-update.md
├── specs/
├── issues/
├── templates/SPEC_TEMPLATE.md, ISSUE_TEMPLATE.md
├── session/current.md
└── INDEX.md
```

## Template Sources

All from plugin `good-pm/templates/`:
- `PM_CONTRACT.md` → `.good-pm/context/`
- `PM_STUB.md` → `.good-pm/context/`
- `SESSION_UPDATE.md` → `.good-pm/context/session-update.md`
- `SESSION_TEMPLATE.md` → `.good-pm/session/current.md`
- `SPEC_TEMPLATE.md`, `ISSUE_TEMPLATE.md` → `.good-pm/templates/`
- `INDEX.md` → `.good-pm/`

## Hooks (unless --no-settings)

Copy from `good-pm/hooks/` to `.claude/hooks/` and make executable:
- `good-pm-context.sh`
- `good-pm-session-update.py`

## Output

Print success message with next steps (`/good-pm:create-spec`, `/good-pm:issues`).

For detailed documentation: `/good-pm:help setup`
