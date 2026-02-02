# Output Templates

Templates for console summary and technical memo. Referenced by SKILL.md during the output phase.

---

## Console Summary

Provide a brief summary to the user after validation:

````markdown
## Validation Results

Scanned: X skills, Y agents, Z legacy commands, W other files

### Errors (must fix)

| Component | Issue | Suggested Fix |
|-----------|-------|---------------|
| [name] | [description of error] | [specific fix instruction] |

### Warnings (should fix)

| Component | Issue | Suggested Fix |
|-----------|-------|---------------|
| [name] | [description of issue] | [specific fix instruction] |

### Cross-Reference Issues (if any)

| Source | References | Problem |
|--------|------------|---------|
| [name] | [referenced item] | [missing/broken/orphaned] |

### Top Improvements
1. [highest impact change]
2. [second highest]
3. [third highest]

Full analysis written to: CLAUDE_MEMO_AI_TOOLS_REVIEW.md
````

---

## Technical Memo (CLAUDE_MEMO_AI_TOOLS_REVIEW.md)

Create a detailed markdown file in the project root with this structure:

````markdown
# Claude AI Tools Review

**Generated:** [timestamp]
**Scope:** [path validated]

## Executive Summary

[2-3 sentence overview of findings]

## Inventory

| Type | Count | With Errors | With Warnings |
|------|-------|-------------|---------------|
| Skills | X | Y | Z |
| Agents | X | Y | Z |
| Legacy Commands | X | Y | Z |
| Other | X | Y | Z |

## Detailed Findings

### Skills

#### [skill-name]
**Status:** [PASS | WARNINGS | ERRORS]

**Files found:**
- [list all files in skill directory with line counts]

---

**Errors:**
[numbered list of errors with copy-paste-ready fix instructions]

**Warnings:**
[numbered list of warnings with suggested improvements]

**Suggestions:**
[numbered list of optimization opportunities]

**Cross-Reference Validation:**
[table showing all link checks and their PASS/FAIL status]

[Repeat for each skill]

### Agents

[Same format as skills]

### Legacy Commands

[Same format as skills, with migration warning for each]

## Global Recommendations

[Cross-cutting improvements that affect multiple components]

## Checklist for Fixes

- [ ] [specific action item]
- [ ] [specific action item]
- [ ] [specific action item]
````
