---
description: Break down a spec, PRD, or technical memo into discrete issue files
argument-hint: <path/to/SPEC_name.md>
allowed-tools: Read, Write, Glob
---

The user wants to break down a document into issues.

**Source document:** $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user to provide a path to the spec, PRD, or technical memo.

## Setup

1. Read the document at `$ARGUMENTS`.
2. **Determine the project directory** from the spec path:
   - Expected path format: `{project}/specs/SPEC_{name}.md`
   - Extract the project directory (e.g., `new-data-pipeline/specs/SPEC_new-data-pipeline.md` → `new-data-pipeline/`)
   - Extract `{name}` from the filename (e.g., `SPEC_new-data-pipeline.md` → `new-data-pipeline`)
3. Create the `{project}/issues/` directory if it doesn't exist.

## Create Issues

Break the work into discrete, independently-completable issues. Each issue should be small enough to finish in one focused coding session.

For each issue, create a file `{project}/issues/NNN-short-description.md` with:

````markdown
## Title
Clear, action-oriented title

## Source
This issue is part of the work defined in: `../specs/SPEC_{name}.md`

## Description
What needs to be done and why

## Tasks
- [ ] Specific task 1
- [ ] Specific task 2

## Acceptance Criteria
How to verify this issue is complete

## Dependencies
List any issue numbers that must be completed first (or "None")
````

Keep issues atomic–one logical change per issue. Include specific commands, file paths, or content from the source document needed to complete each issue.

## Update README

After creating all issues, update `{project}/README.md` to add an issues summary:

- Add an "## Issues" section if not present
- List all issues in recommended execution order
- Note dependencies for each issue

## Output Structure

```
{project}/
    ├── issues/
    │   ├── 001-first-task.md
    │   ├── 002-second-task.md
    │   └── ...
    ├── README.md
    └── specs/
        └── SPEC_{name}.md
```

## Usage

````bash
/create-issues new-data-pipeline/specs/SPEC_new-data-pipeline.md
/create-issues user-auth/specs/SPEC_user-auth.md
````

---

## Related Tools

| Type | Name | Purpose |
|------|------|---------|
| command | `/create-spec` | Create spec documents (run this first) |
| command | `/issues` | View status of specs and issues |
| command | `/fix-issue-status` | Sync checkbox state with README |
| command | `/fix-issue-relationships` | Fix broken references |
| agent | `issues-housekeeper` | Validate structure, detect problems |
