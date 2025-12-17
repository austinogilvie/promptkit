---
description: Create a structured SPEC/PRD document for planning new features
argument-hint: <name> <summary OR path/to/draft.md>
allowed-tools: Read, Write
---

## Purpose

Scaffold a structured SPEC or PRD (Product Requirements Document) for planning a new feature. The generated spec follows a consistent format that works well with `/create-issues` for breaking down work into discrete tasks.

## Inputs

| Argument | Format | Validation |
|----------|--------|------------|
| `$1` | SPEC_NAME | Required. Lowercase kebab-case (e.g., `user-auth`, `api-caching`). Max 64 chars. |
| `$2` | SUMMARY or FILE | Required. Either: (A) a one-line text summary, or (B) a path to an existing markdown draft file. |

### Input Detection

- **Case A (text summary):** If `$2` does NOT end with `.md` OR the file does not exist → treat as plain text summary (max 256 chars)
- **Case B (file input):** If `$2` ends with `.md` AND the file exists → read file content as context for spec generation

## Output Structure

When you run `/create-spec {name} ...`, the command creates:

```
{name}/
    ├── README.md
    └── specs/
        └── SPEC_{name}.md
```

## Output Contract

**Case A (text summary):**
- Success: `Created new spec: {name}/specs/SPEC_{name}.md`
- Already exists: `Spec already exists: {name}/specs/SPEC_{name}.md`
- Validation error: `Error: {message}`

**Case B (file input):**
- Reading: `Reading draft: {filepath}`
- Success: `Created new spec: {name}/specs/SPEC_{name}.md (from {filepath})`
- Validation error: `Error: {message}`

## Instructions

1. **Validate `$1` (name):**
   - If `$1` is empty: output `Error: Spec name is required` and stop
   - If `$1` contains uppercase letters, spaces, or special chars (only `a-z`, `0-9`, `-` allowed): output `Error: Spec name must be lowercase kebab-case` and stop
   - If `$1` exceeds 64 characters: output `Error: Spec name exceeds 64 characters` and stop

2. **Validate `$2` (summary or file):**
   - If `$2` is empty: output `Error: Summary or draft file path is required` and stop

3. **Detect input type:**
   - If `$2` ends with `.md` AND the file exists at that path → **Case B**
   - Otherwise → **Case A**

4. **Check existence:**
   - If `$1/specs/SPEC_$1.md` exists: output `Spec already exists: $1/specs/SPEC_$1.md` and stop

5. **Create directory structure:**
   - Create directory `$1/` if it doesn't exist
   - Create directory `$1/specs/` if it doesn't exist

6. **Case A (text summary):**
   - If `$2` exceeds 256 characters: output `Error: Summary exceeds 256 characters` and stop
   - Generate spec file using the template below, substituting:
     - `{{NAME}}` with `$1`
     - `{{SUMMARY}}` with `$2`
     - `{{DATE}}` with today's date (YYYY-MM-DD)
   - Write generated content to `$1/specs/SPEC_$1.md`
   - Output: `Created new spec: $1/specs/SPEC_$1.md`

7. **Case B (file input):**
   - Output: `Reading draft: $2`
   - Read the contents of the draft file at `$2`
   - Analyze the draft content to understand the feature being described
   - Generate spec file using the template below, **intelligently populating sections** based on the draft content:
     - `{{NAME}}` with `$1`
     - `{{SUMMARY}}` with a one-line summary derived from the draft
     - `{{DATE}}` with today's date (YYYY-MM-DD)
     - Fill in Overview, Problem Statement, Goals, Proposed Solution, etc. based on what you learn from the draft
     - Do NOT copy-paste the draft verbatim; synthesize and structure the information
   - Write generated content to `$1/specs/SPEC_$1.md`
   - Delete the original draft file at `$2`
   - Output: `Created new spec: $1/specs/SPEC_$1.md (from $2)`

8. **Create README.md:**
   - Create `$1/README.md` with a brief project overview:
     ```markdown
     # {{NAME}}

     > {{SUMMARY}}

     ## Structure

     - `specs/` - Specification documents
     - `issues/` - Issue breakdowns (created via `/create-issues`)

     ## Getting Started

     Review the spec at `specs/SPEC_{{NAME}}.md`, then run:
     ```
     /create-issues $1/specs/SPEC_$1.md
     ```
     ```

9. **Next steps:**
   - Tell the user to review and fill in any remaining sections
   - Remind them they can use `/create-issues $1/specs/SPEC_$1.md` when ready to break down work

## Embedded Template

```markdown
# SPEC: {{NAME}}

> {{SUMMARY}}

**Created:** {{DATE}}
**Status:** Draft

---

## Overview

[What is this feature? Why are we building it? 2-3 sentences explaining the high-level goal.]

## Problem Statement

[What problem does this solve? Who has this problem? What's the impact of not solving it?]

## Goals

- [ ] Primary goal 1
- [ ] Primary goal 2

### Non-Goals

- What this spec explicitly does NOT cover

## Background & Context

[Any relevant context, prior art, existing systems, or constraints that inform this work.]

## Proposed Solution

### High-Level Approach

[Describe the solution at a high level. What's the strategy?]

### Technical Design

[Key technical decisions, architecture choices, data models, APIs, etc.]

### User Experience

[If applicable: user flows, UI changes, behavior changes]

## Implementation Plan

### Phase 1: [Name]
- Task 1
- Task 2

### Phase 2: [Name]
- Task 3
- Task 4

## Acceptance Criteria

- [ ] Criterion 1: [How do we know this is done?]
- [ ] Criterion 2: [What must be true for this to be complete?]
- [ ] Criterion 3: [What tests or validations must pass?]

## Open Questions

- [ ] Question 1
- [ ] Question 2

## Dependencies

- External dependency 1
- Internal dependency 2

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Risk 1 | Low/Med/High | Low/Med/High | How to address |

## References

- [Link to relevant docs]
- [Link to related specs]

---

*When ready to break this into discrete issues, run: `/create-issues {{NAME}}/specs/SPEC_{{NAME}}.md`*
```

## Examples

```bash
# Case A: Basic usage with text summary
/create-spec user-auth "Add OAuth2 authentication with Google and GitHub providers"
# Creates:
#   user-auth/
#       ├── README.md
#       └── specs/
#           └── SPEC_user-auth.md
# Output: Created new spec: user-auth/specs/SPEC_user-auth.md

# Case B: Using an existing draft file
/create-spec user-auth ./drafts/auth-notes.md
# Output:
#   Reading draft: ./drafts/auth-notes.md
#   Created new spec: user-auth/specs/SPEC_user-auth.md (from ./drafts/auth-notes.md)

# Spec already exists
/create-spec user-auth "Different description"
# Output: Spec already exists: user-auth/specs/SPEC_user-auth.md

# Invalid name
/create-spec UserAuth "Bad name format"
# Output: Error: Spec name must be lowercase kebab-case

# Missing arguments
/create-spec
# Output: Error: Spec name is required

# File path provided but doesn't exist (treated as Case A text)
/create-spec my-feature ./nonexistent.md
# Output: Created new spec: my-feature/specs/SPEC_my-feature.md (uses "./nonexistent.md" as summary text)
```

## Design Decisions

### Dual input modes
The command accepts either plain text or a file path as the second argument:
- **Text mode** is fast for quick specs when you know what you want
- **File mode** lets you start with rough notes and convert them into a structured spec

### File detection logic
A path is treated as a file only if it ends with `.md` AND exists. This prevents accidental file mode when someone types a summary that happens to end with `.md`.

### Draft file is deleted (renamed)
In file mode, the original draft is removed after the spec is created. This keeps the workspace clean and enforces the naming convention. The original content is synthesized into the spec, not lost.

### Filename convention
Specs are named `SPEC_{name}.md` (uppercase SPEC prefix) to make them visually distinct and easy to glob for. This matches the user's existing convention. Both input modes produce the same naming pattern.

### Directory structure
Each spec gets its own project directory (`{name}/`) with subdirectories for `specs/` and `issues/`. This keeps related artifacts together and makes it easy to work on multiple features simultaneously. The structure is:
```
{name}/
    ├── README.md       # Project overview
    ├── specs/          # Specification documents
    └── issues/         # Issue breakdowns (created via /create-issues)
```

### Structured for create-issues compatibility
The template includes:
- Clear **Acceptance Criteria** with checkboxes
- **Implementation Plan** with phases and tasks
- **Dependencies** section

These sections map directly to fields in issues generated by `/create-issues`.

### Balanced structure
The template balances thoroughness with pragmatism:
- Enough structure to force clear thinking
- Not so rigid that it feels bureaucratic
- Sections can be deleted if not relevant

---

## Related Tools

| Type | Name | Purpose |
|------|------|---------|
| command | `/create-issues` | Break this spec into issue files |
| command | `/issues` | View status of specs and issues |
| command | `/fix-issue-status` | Sync checkbox state with README |
| command | `/fix-issue-relationships` | Fix broken references |
| agent | `issues-housekeeper` | Validate structure, detect problems |
