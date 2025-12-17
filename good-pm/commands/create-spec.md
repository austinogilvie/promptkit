---
description: Create a structured specification document from a name and summary or draft file.
argument-hint: "<name> <summary OR path/to/draft.md>"
---

# /good-pm:create-spec

Create a spec in `.good-pm/specs/SPEC_<name>.md`.

## Arguments

- `$1` — **name**: Spec name in kebab-case (e.g., `user-auth`)
- `$2` — **input**: Text summary OR path to draft `.md` file

## Instructions

1. Read `.good-pm/context/PM_CONTRACT.md` for full conventions (Decision D1)
2. Validate prerequisites (`.good-pm/` exists, template exists)
3. Set `pm_work_detected: true` in `.good-pm/session/current.md` frontmatter (Decision D2)
4. Validate name: kebab-case, max 64 chars, no leading/trailing hyphens
5. Check spec doesn't already exist
6. Detect input type (file if ends with `.md` and exists, otherwise text)
7. Generate spec from template
8. Output success message

## Name Validation

- Format: lowercase `a-z`, `0-9`, `-` only
- Pattern: `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`
- Max length: 64 characters

## Input Modes

**Text mode:** Use `$2` as summary (max 256 chars), fill template placeholders.

**File mode:** Read draft, synthesize into spec sections, delete original draft.

## Template

Read from `.good-pm/templates/SPEC_TEMPLATE.md`. Replace:
- `{{NAME}}` → spec name
- `{{SUMMARY}}` → summary text (text mode)
- `{{DATE}}` → today's date (YYYY-MM-DD)

## Output

```
Created spec: .good-pm/specs/SPEC_<name>.md

When ready, break into issues:
  /good-pm:create-issues .good-pm/specs/SPEC_<name>.md
```

## Examples

```bash
/good-pm:create-spec user-auth "OAuth2 with Google and GitHub"
/good-pm:create-spec api-cache ./notes/caching-ideas.md
```

For detailed validation rules and error handling: `/good-pm:help create-spec`
