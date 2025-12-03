---
name: docs-writer
description: "Generate comprehensive technical documentation including API references, user guides, architecture docs, ADRs, and runbooks. Use when creating new READMEs from scratch, multi-file documentation from code, OpenAPI specs, deployment guides, or architecture decision records. For updating existing READMEs, use readme-updater instead."
version: 1.0.0
---

# Documentation Writer

## Overview

Expert technical documentation specialist for comprehensive documentation tasks. Creates clear, accurate, user-friendly documentation that helps users understand and use software effectively.

## When to Use This Skill

Use docs-writer when you need:
- **API documentation** from code (OpenAPI, endpoint references, authentication docs)
- **User guides** and tutorials (getting started, feature walkthroughs)
- **Architecture documentation** (system design, ADRs, component diagrams)
- **Operational docs** (runbooks, deployment guides, troubleshooting)
- **Project documentation** (comprehensive READMEs, CONTRIBUTING guides)

**Handoff to readme-updater:** For maintaining existing READMEs (section updates, dependency changes, minor edits), use the readme-updater skill instead. docs-writer creates, readme-updater maintains.

---

## Quick Reference

| Doc Type | Workflow | Template |
|----------|----------|----------|
| API Reference | [workflows/api-docs.md](workflows/api-docs.md) | [templates/api-reference.md](templates/api-reference.md) |
| User Guide | [workflows/user-guide.md](workflows/user-guide.md) | [templates/user-guide.md](templates/user-guide.md) |
| Architecture | [workflows/architecture.md](workflows/architecture.md) | [templates/adr.md](templates/adr.md) |
| Troubleshooting | [workflows/troubleshooting.md](workflows/troubleshooting.md) | — |
| Runbook | — | [templates/runbook.md](templates/runbook.md) |
| README | — | [templates/readme-comprehensive.md](templates/readme-comprehensive.md) |

---

## Core Principles

### 1. Audience Awareness

Always identify the target audience before writing:
- **End Users**: Simple language, task-oriented, minimal jargon
- **Developers**: Technical details, code examples, API specifics
- **Administrators**: Configuration, deployment, maintenance
- **Contributors**: Architecture, conventions, processes

### 2. Documentation Standards

**Structure**
- Clear hierarchy with consistent heading levels
- Table of contents for documents > 500 words
- Cross-references between related sections
- Progressive disclosure (basic → advanced)

**Content**
- Lead with the most important information
- Use active voice and direct instructions
- Include practical examples for every concept
- Provide both quick-start and comprehensive paths

**Code Examples**
- Validate all code examples for syntax correctness
- Include expected output where applicable
- Show error handling, not just happy path
- Use realistic, not trivial, examples

### 3. Format Guidelines

**Markdown Best Practices**
- Use fenced code blocks with language hints
- Tables for structured comparisons
- Consistent formatting throughout

**API Documentation Standards**
- HTTP method and path clearly visible
- All parameters documented (path, query, body, headers)
- Request and response examples
- Error responses with codes and messages
- Authentication requirements

---

## Process

When asked to create documentation:

1. **Analyze**: Examine the code/system to understand what needs documenting
2. **Plan**: Outline the documentation structure before writing
3. **Draft**: Write the documentation following standards above
4. **Validate**: Run `scripts/validate_docs.py` to check quality
5. **Refine**: Fix issues, improve clarity, add missing sections

---

## Validation

Before delivering documentation, run the validation script:

```bash
python scripts/validate_docs.py output.md
```

This checks for:
- Placeholder text (`[TODO]`, `[PLACEHOLDER]`)
- Empty code blocks
- Missing sections
- Broken internal links

See [scripts/validate_docs.py](scripts/validate_docs.py) for implementation.

---

## Quality Checklist

Before delivering documentation, verify:
- [ ] Target audience is clear
- [ ] All code examples are syntactically correct
- [ ] No placeholder text remains
- [ ] Cross-references are valid
- [ ] Prerequisites are complete
- [ ] Examples are realistic and useful
- [ ] Error cases are documented
- [ ] Document is self-contained (or links to dependencies)

---

## Integration

### With readme-updater skill

The readme-updater skill handles ongoing README maintenance. See [references/skill-handoffs.md](references/skill-handoffs.md) for the complete handoff protocol.

Use this handoff pattern:

| Scenario | Use docs-writer | Use readme-updater |
|----------|-----------------|-------------------|
| Create README from scratch | Yes | No |
| Create comprehensive project docs | Yes | No |
| Update existing README section | No | Yes |
| Add new dependency to README | No | Yes |
| Fix outdated instructions | No | Yes |

**docs-writer responsibilities:**
- Generate initial README using [templates/readme-comprehensive.md](templates/readme-comprehensive.md)
- Create documentation sites with multiple files
- Establish documentation structure and style

**Handoff to readme-updater:**
- After creating README, readme-updater handles maintenance
- readme-updater preserves the style and structure docs-writer established
- readme-updater applies minimal, targeted updates

### With file-categorization skill

If available, use file-categorization to identify:
- Source Code files needing API documentation
- Config files requiring configuration docs
- Scripts that should be documented in user guides

---

## Examples

See [examples/](examples/) for complete output samples:
- [api-example.md](examples/api-example.md) — User Management API reference
- [guide-example.md](examples/guide-example.md) — CLI tool user guide
