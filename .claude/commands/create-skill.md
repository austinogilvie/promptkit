---
description: Create a new Claude Code skill with proper structure. Use when user wants to scaffold, initialize, or create a new skill.
argument-hint: [skill-name] [description] [--personal|--project]
allowed-tools: ["Read", "Write", "Bash", "Glob"]
---

Create a reusable Claude Code skill — a portable capability that will be used in *other* projects, not the current repo.

Do NOT analyze the current repo for how to use the skill's subject matter. Instead, create a generic, reusable skill that could apply to any project needing that capability. The skill should be self-contained and context-independent.

**Inputs:** `$ARGUMENTS` parsed as: SKILL_NAME (kebab-case, max 64 chars), DESCRIPTION (quoted string, max 1024 chars)
**Flags:** `--personal` (default: ~/.claude/skills/) or `--project` (.claude/skills/)
**Output:** `STATUS=<CREATED|EXISTS|FAIL> PATH=<path>`

## Instructions

1. **Validate:**
   - Name: lowercase letters/numbers/hyphens only, max 64 chars
   - Description: non-empty, max 1024 chars, no angle brackets

2. **Check existence:** If skill exists, output `STATUS=EXISTS PATH=<path>` and stop.

3. **Analyze and decide bundled resources.** State your reasoning, then create only what's needed:
   - `scripts/` — when skill involves file manipulation, data processing, or repeated code
   - `references/` — when skill needs docs/schemas that would make SKILL.md exceed 500 lines
   - `assets/` — when skill uses templates, boilerplate, or brand files

4. **Create structure:**
   ```
   {{SKILL_NAME}}/
   ├── SKILL.md (required)
   ├── scripts/example.py (executable, if needed)
   ├── references/.gitkeep (if needed)
   └── assets/.gitkeep (if needed)
   ```

5. **Generate SKILL.md:**
   ```markdown
   ---
   name: {{SKILL_NAME}}
   description: {{DESCRIPTION}}
   ---

   # {{Title Case Name}}

   ## Overview
   [TODO: What this skill does]

   ## When to Use
   [TODO: Triggers and scenarios]

   ## Instructions
   [TODO: Step-by-step guidance]

   ## Examples
   [TODO: Realistic user requests and responses]
   ```

6. **Output:** Print `STATUS=CREATED PATH={{path}}` and list what was created.

## Skill Frontmatter

**Required:** `name`, `description`
**Optional:** `allowed-tools`, `metadata`, `license`

## Examples

```bash
/create-skill commit-helper "Generate git commit messages. Use when writing commits."
/create-skill pdf-processor "Extract text from PDFs. Use for document extraction." --project
```
