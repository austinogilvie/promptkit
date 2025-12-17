---
description: Display status summary of specs and issues based on checkbox state.
argument-hint: "[project-path]"
---

# /good-pm:issues

Display status of specs and issues by counting checkboxes.

## Arguments

- `$1` (optional) — **project-path**: Path to project (default: current directory)

## Instructions

1. Read `.good-pm/context/PM_CONTRACT.md` for full conventions (Decision D1)
2. Resolve project path (use `$1` or current directory)
3. Validate `.good-pm/` exists
4. Discover specs (`specs/SPEC_*.md`) and issues (`issues/NNN-*.md`)
5. Count checkboxes in each file
6. Derive status from checkbox state
7. Map issues to specs via `## Source` section
8. Output formatted summary

## Status Derivation

| Checkbox State | Status |
|----------------|--------|
| 0 of N checked | **Open** |
| Some checked | **In Progress** |
| N of N checked | **Complete** |
| No checkboxes | **No Tasks** |

Patterns: `- [ ]` (unchecked), `- [x]` or `- [X]` (checked)

## Output Format

```markdown
# project-name

## Specs
| Spec | Status | Progress | Issues |
|------|--------|----------|--------|
| SPEC_name | In Progress | 7/12 (58%) | 5 |

## Issues
### SPEC_name
| # | Title | Status | Progress |
|---|-------|--------|----------|
| 001 | description | Complete | 3/3 |

## Summary
- **Specs:** 0 complete, 1 in progress
- **Next:** `002-next-issue.md`
```

## Example

```bash
/good-pm:issues
/good-pm:issues ./my-project
```

For detailed formatting and examples: `/good-pm:help issues`
