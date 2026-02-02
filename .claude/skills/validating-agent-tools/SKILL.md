---
name: validating-agent-tools
description: >-
  Validate Claude Code skill, agent, and command configs in .claude/ against
  Anthropic best practices and generate CLAUDE_MEMO_AI_TOOLS_REVIEW.md.
  Use when asked to validate, audit, check, or review Claude skills,
  commands, or agents, or when you want a post-change validation pass.
user-invocable: true
disable-model-invocation: true
argument-hint: "[path/to/validate]"
allowed-tools: ["Read", "Write", "Bash", "Glob", "Grep"]
---

Validate Claude Code components (skills, agents, legacy commands) against Anthropic's official documentation and best practices.

**Target:** `$ARGUMENTS` (if empty, validate all of `.claude/`)

## Setup

1. If `$ARGUMENTS` is provided, validate only that path
2. If `$ARGUMENTS` is empty, validate the entire `.claude/` directory
3. Create output file: `CLAUDE_MEMO_AI_TOOLS_REVIEW.md` in the project root

---

## Frontmatter Schemas

There are exactly **two** component types with different frontmatter schemas: **Skills** and **Agents**. Skills and slash commands are the same thing (Anthropic unified them).

### Skills (`.claude/skills/*/SKILL.md` AND legacy `.claude/commands/*.md`)

Skills and slash commands share a single schema. Files in `.claude/commands/` are legacy but functionally identical.

```yaml
---
name: skill-name                        # Required (max 64 chars, lowercase + numbers + hyphens)
description: What and when              # Required (max 1024 chars, no XML tags)
allowed-tools: ["Read", "Write"]        # Optional - pre-approved access
argument-hint: <arg1> [arg2]            # Optional - hint shown during slash autocomplete
user-invocable: true | false            # Optional - show/hide from slash menu (default: true)
disable-model-invocation: true | false  # Optional - prevent Claude auto-invocation (default: false)
context: fork                           # Optional - run in isolated subagent
agent: Explore | Plan | general-purpose # Optional - agent type when context: fork
model: model-id                         # Optional - force a specific model for this skill
hooks: { ... }                          # Optional - lifecycle hooks (PreToolUse, PostToolUse, Stop)
---
```

**Valid skill frontmatter fields (may evolve):** `name`, `description`, `allowed-tools`, `argument-hint`, `user-invocable`, `disable-model-invocation`, `context`, `agent`, `model`, `hooks`

**Key interdependency:** `agent` requires `context: fork`. The `context` field's only valid value is `fork`.

### Agents (`.claude/agents/*.md`)

Agents are a separate concept from skills with their own schema.

> **Note:** The agent schema below is best-effort based on current documentation and may not be complete. Fields like `color` appear in some agent configs but are not confirmed in official docs. Prefer WARNING over ERROR when encountering unrecognized agent fields.

```yaml
---
name: agent-name                        # Required (max 64 chars)
description: What this agent does       # Required (max 1024 chars, no XML tags)
tools: Read, Write, Bash                # Optional (NOT allowed-tools)
model: sonnet | opus | haiku | inherit  # Optional (default: inherit)
permissionMode: default | acceptEdits | bypassPermissions | plan | ignore  # Optional
skills: skill1, skill2                  # Optional - skills to auto-load
---
```

**Known agent frontmatter fields:** `name`, `description`, `tools`, `model`, `permissionMode`, `skills`

Other fields (e.g., `color`) may be valid but are unverified. Flag unrecognized agent fields as WARNING, not ERROR.

**Key distinction:** Agents use `tools:` field. Skills use `allowed-tools:` field.

---

## Analysis Process

0. **Verify schemas**: Before validating any field names, consult the Frontmatter Schemas section above. Do NOT rely on assumptions from other components in the codebase.
1. **Inventory**: List all components found in `.claude/`
2. **Classify** by file path:
   - `.claude/skills/*/SKILL.md` → **Skill**
   - `.claude/commands/*.md` → **Legacy Skill** (validate as skill, flag for migration)
   - `.claude/agents/*.md` → **Agent**
3. **Validate**: Run all applicable checks from [references/validation-checklist.md](references/validation-checklist.md)
4. **Categorize findings**:
   - **ERRORS**: Broken functionality (missing required fields, invalid field values, invalid syntax, broken links, field interdependency violations)
   - **WARNINGS**: Functional but non-conforming (unrecognized fields, missing best practices, legacy location, naming convention)
   - **SUGGESTIONS**: Optimization opportunities (improved descriptions, additional documentation)
5. **Prioritize**: For each component, identify top 3 highest-ROI improvements

## Validation Rules

Read [references/validation-checklist.md](references/validation-checklist.md) for the complete validation rules covering:

- Skill structure, field values, interdependencies, naming, and best practices
- Legacy command detection and migration warnings
- Agent structure and field validation
- CLAUDE.md, reference file, and script validation
- Cross-reference checks (agent-to-skill, skill-to-file, orphan detection)
- Common false positives to avoid

**Key false-positive reminders** (see full table in checklist):
- `disable-model-invocation`, `argument-hint`, `user-invocable`, `context`, `agent`, `model`, `hooks` are all valid skill fields
- Agents use `tools:`, skills use `allowed-tools:` — both are correct for their type
- Skill bodies describing `/skill-name` invocation syntax is valid (skills ARE slash commands)
- Unrecognized agent fields should be WARNING, not ERROR

## Output Format

Follow the templates in [references/output-templates.md](references/output-templates.md) for both:
- **Console summary** — tabular errors/warnings/cross-references shown to user
- **Technical memo** — `CLAUDE_MEMO_AI_TOOLS_REVIEW.md` written to project root

## Fix Templates

When reporting fixes, use copy-paste-ready templates from [references/fix-templates.md](references/fix-templates.md).

---

## Examples

**Invocation:** `/validating-agent-tools .claude/skills/normalize-pencil/`

**Console output:**

```markdown
## Validation Results

Scanned: 1 skill, 0 agents, 0 legacy commands

### Errors (must fix)

(none)

### Warnings (should fix)

| Component | Issue | Suggested Fix |
|-----------|-------|---------------|
| normalize-pencil | Name does not use gerund form | Rename to `normalizing-pencil` |
| normalize-pencil | Description lacks trigger phrases | Add "Use when reviewing Pencil output..." |
| normalize-pencil | `docopt` dependency undocumented | Add prerequisites section to SKILL.md |

### Top Improvements
1. Add trigger phrases to description for better auto-matching
2. Document the `docopt` Python dependency
3. Add `text-gray-600` mapping to reference.md (drift from map_tokens.py)

Full analysis written to: CLAUDE_MEMO_AI_TOOLS_REVIEW.md
```

**Full-scan invocation (no args):** `/validating-agent-tools`

Scans all of `.claude/` — skills, agents, and legacy commands. Writes the complete review to `CLAUDE_MEMO_AI_TOOLS_REVIEW.md`.

---

## Post-Validation Checks

After creating the memo, confirm:
1. `CLAUDE_MEMO_AI_TOOLS_REVIEW.md` exists in project root
2. All errors are clearly actionable with specific fix instructions
3. Summary was provided to user with tabular format
4. Cross-reference issues are identified and reported
