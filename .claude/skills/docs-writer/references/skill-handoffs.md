# Documentation Skill Handoff Protocol

This document defines how documentation-related skills interact and hand off work to each other.

## Skill Responsibilities

```
┌─────────────────────────────────────────────────────────────────┐
│                  Documentation Lifecycle                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   CREATE                              MAINTAIN                   │
│   ┌─────────────────────┐             ┌─────────────────────┐   │
│   │    docs-writer      │             │   readme-updater    │   │
│   │                     │   handoff   │                     │   │
│   │  • New READMEs      │ ─────────▶  │  • Section updates  │   │
│   │  • Doc sites        │             │  • Dependency adds  │   │
│   │  • API references   │             │  • Config changes   │   │
│   │  • User guides      │             │  • Version bumps    │   │
│   │  • Architecture     │             │  • Style preserved  │   │
│   └─────────────────────┘             └─────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Decision Matrix

| User Request | Primary Skill | Reason |
|--------------|---------------|--------|
| "Create a README for this project" | docs-writer | Creation from scratch |
| "Update the README with new feature" | readme-updater | Targeted update |
| "Document the API" | docs-writer | Comprehensive docs |
| "Add redis to prerequisites" | readme-updater | Section update |
| "Write a getting started guide" | docs-writer | New document |
| "Fix outdated install instructions" | readme-updater | Maintenance |
| "Create project documentation" | docs-writer | Multi-file docs |
| "Is the README up to date?" | readme-updater | Audit/validation |

## Handoff Triggers

### docs-writer → readme-updater

After docs-writer completes initial documentation:

1. **Signal completion**: "README created. Future updates should use readme-updater methodology."
2. **Style baseline**: readme-updater uses docs-writer's output as style reference
3. **Structure preservation**: readme-updater maintains heading hierarchy and formatting

### readme-updater → docs-writer

Escalate to docs-writer when:

1. **No README exists**: Cannot update what doesn't exist
2. **Complete rewrite needed**: Changes exceed 50% of document
3. **Multi-file needed**: User requests docs beyond single README
4. **Template mismatch**: Existing README lacks standard structure

## Shared Conventions

Both skills should:

1. **Validate code blocks**: Ensure examples are syntactically correct
2. **Use language hints**: All fenced code blocks have language specified
3. **Avoid placeholders**: No `[TODO]`, `[PLACEHOLDER]` in output
4. **Match project style**: Preserve existing emoji/formatting conventions

## Integration with file-categorization

When file-categorization skill is available:

| Category | docs-writer Use | readme-updater Use |
|----------|-----------------|-------------------|
| Source Code | Generate API docs | Update Usage section |
| Config | Document in guides | Update Configuration section |
| Scripts | Include in user guide | Update Development section |
| Tests | Reference in contributing | Update Testing section |

## Example Workflow

```
1. User: "Set up documentation for my new project"
   → docs-writer creates README.md, API docs, user guide

2. User: "I added a new endpoint"
   → readme-updater adds entry to Features section
   → docs-writer updates API reference (if separate doc exists)

3. User: "Update prerequisites for new Node version"
   → readme-updater updates Prerequisites section

4. User: "Rewrite the documentation completely"
   → docs-writer handles full rewrite
   → readme-updater takes over maintenance after
```
