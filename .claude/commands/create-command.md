---
description: Create a new Claude Code Slash Command with standardized structure
argument-hint: [name] [purpose]
allowed-tools: Bash(mkdir:*), Bash(test:*)
---

# /create-command

## Purpose

Scaffold a new slash command file with proper structure and frontmatter.

## Inputs

- `$1` — COMMAND_NAME: Required. Lowercase kebab-case (e.g., `fix-issue`, `run-tests`). Max 64 chars.
- `$2` — PURPOSE: Required. Brief description of what the command does. Max 1024 chars. No `<` or `>` characters.

## Output Contract

Single status line:
- Success: `STATUS=CREATED PATH=.claude/commands/{name}.md`
- Already exists: `STATUS=EXISTS PATH=.claude/commands/{name}.md`
- Validation error: `STATUS=FAIL ERROR="{message}"`

## Instructions

1. **Validate inputs:**
   - If `$1` is empty: output `STATUS=FAIL ERROR="Command name is required"` and stop
   - If `$1` contains uppercase letters, spaces, or special chars (only `a-z`, `0-9`, `-` allowed): output `STATUS=FAIL ERROR="Command name must be lowercase kebab-case"` and stop
   - If `$1` exceeds 64 characters: output `STATUS=FAIL ERROR="Command name exceeds 64 characters"` and stop
   - If `$2` is empty: output `STATUS=FAIL ERROR="Purpose is required"` and stop
   - If `$2` exceeds 1024 characters: output `STATUS=FAIL ERROR="Purpose exceeds 1024 characters"` and stop
   - If `$2` contains `<` or `>`: output `STATUS=FAIL ERROR="Purpose cannot contain angle brackets"` and stop

2. **Check existence:**
   - If `.claude/commands/$1.md` exists: output `STATUS=EXISTS PATH=.claude/commands/$1.md` and stop

3. **Create directory:**
   - Run `mkdir -p .claude/commands` to ensure directory exists

4. **Generate command file** using the template below, substituting:
   - `{{NAME}}` with `$1`
   - `{{PURPOSE}}` with `$2`

5. **Write file and output:**
   - Write generated content to `.claude/commands/$1.md`
   - Output `STATUS=CREATED PATH=.claude/commands/$1.md`

## Embedded Template

```markdown
---
description: {{PURPOSE}}
argument-hint: [args]
---

# /{{NAME}}

## Purpose

{{PURPOSE}}

## Inputs

- `$ARGUMENTS` — Command arguments (describe expected format)

## Instructions

1. **Validate inputs:**
   - Check required arguments are provided
   - Validate format and values

2. **Execute:**
   - [TODO: Add implementation steps]

3. **Output:**
   - `STATUS=OK` on success
   - `STATUS=FAIL ERROR="message"` on failure

## Examples

\`\`\`bash
/{{NAME}} example-arg
\`\`\`
```

## Examples

```bash
# Basic usage
/create-command analyze-deps "Analyze project dependencies for updates"
# Output: STATUS=CREATED PATH=.claude/commands/analyze-deps.md

# Command already exists
/create-command analyze-deps "Different description"
# Output: STATUS=EXISTS PATH=.claude/commands/analyze-deps.md

# Invalid name
/create-command AnalyzeDeps "Bad name format"
# Output: STATUS=FAIL ERROR="Command name must be lowercase kebab-case"

# Missing arguments
/create-command
# Output: STATUS=FAIL ERROR="Command name is required"
```
