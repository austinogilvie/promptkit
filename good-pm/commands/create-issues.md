---
description: Break down a spec into discrete, numbered issue files.
argument-hint: "<path/to/SPEC_name.md>"
---

# /good-pm:create-issues

Break a spec into discrete issue files in `.good-pm/issues/`.

## Arguments

- `$1` — **spec-path**: Path to spec file (e.g., `.good-pm/specs/SPEC_user-auth.md`)

## Instructions

1. Read `.good-pm/context/PM_CONTRACT.md` for full conventions (Decision D1)
2. Validate prerequisites (`.good-pm/` exists, template exists)
3. Set `pm_work_detected: true` in `.good-pm/session/current.md` frontmatter (Decision D2)
4. Validate spec path exists and is markdown
5. Parse spec: extract Implementation Plan, Goals, Acceptance Criteria
6. Generate issues from extracted tasks
7. Write issue files with sequential numbering
8. Update `.good-pm/INDEX.md`
9. Output success message

## Issue Numbering

1. Scan `.good-pm/issues/` for existing `NNN-*.md` files
2. Find highest number, start new issues at `highest + 1`
3. If no issues exist, start at `001`
4. Format: zero-padded 3 digits (001, 002, ..., 999)

## Issue Structure

Each issue contains:
- **Title**: Action-oriented (verb phrase)
- **Source**: `../specs/SPEC_<name>.md`
- **Tasks**: Checkbox list from spec
- **Dependencies**: Previous issue number or "None"

Use template: `.good-pm/templates/ISSUE_TEMPLATE.md`

## Parsing Priority

1. **Implementation Plan** — Primary source (phases → issues)
2. **Goals** — Secondary if no Implementation Plan
3. **Acceptance Criteria** — Mapped to issue acceptance criteria

## Issue Guidelines

- Each issue = one logical unit of work
- Completable in one session
- Action-oriented titles (Implement, Add, Create, Fix)
- Dependencies flow from earlier to later issues

## Output

```
Created N issues from SPEC_<name>.md:
  001-description.md
  002-description.md
  ...

Issues written to: .good-pm/issues/
Updated: .good-pm/INDEX.md

View status: /good-pm:issues
```

## Example

```bash
/good-pm:create-issues .good-pm/specs/SPEC_user-auth.md
```

For detailed parsing rules and examples: `/good-pm:help create-issues`
