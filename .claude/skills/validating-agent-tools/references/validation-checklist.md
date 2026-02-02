# Validation Checklist

Complete validation rules for all component types. Referenced by SKILL.md during validation runs.

---

## Skills (`.claude/skills/*/SKILL.md` AND legacy `.claude/commands/*.md`)

Both locations are validated using the **same skill schema**.

### Structure validation
- [ ] SKILL.md exists in skill directory (for `.claude/skills/` entries)
- [ ] YAML frontmatter has opening and closing `---` delimiters
- [ ] Required field: `name` (lowercase, numbers, hyphens only, max 64 chars)
- [ ] Required field: `description` (non-empty, max 1024 chars, no XML tags)
- [ ] No reserved words in name: "anthropic", "claude"
- [ ] No unrecognized frontmatter fields (WARNING — may indicate typo or drift). Valid skill fields: `name`, `description`, `allowed-tools`, `argument-hint`, `user-invocable`, `disable-model-invocation`, `context`, `agent`, `model`, `hooks`

### Field value validation
- [ ] If `user-invocable` is present, value must be boolean (`true` or `false`)
- [ ] If `disable-model-invocation` is present, value must be boolean (`true` or `false`)
- [ ] If `context` is present, value must be `fork` (only valid value)
- [ ] If `agent` is present, value must be one of: `Explore`, `Plan`, `general-purpose`
- [ ] If `allowed-tools` is present, value must be an array or comma-separated list
- [ ] If `tools` is present (instead of `allowed-tools`), emit WARNING — skills use `allowed-tools:` field
- [ ] If `model` is present, value should be a valid model identifier
- [ ] If `hooks` is present, value must be an object whose keys are valid lifecycle hooks (`PreToolUse`, `PostToolUse`, `Stop`) and whose values are arrays of hook definitions (ERROR if value is not an object or contains unknown keys)

### Field interdependency validation
- [ ] If `agent` is present, `context: fork` MUST also be present (ERROR if missing)
- [ ] If `context: fork` is present without `agent`, that is valid (uses default agent type)

### Naming convention
- [ ] Directory name matches `name` field in frontmatter
- [ ] Name uses gerund form (verb + -ing): e.g., `writing-documentation` not `docs-writer` (WARNING)

### Best practices
- [ ] Description includes both what the skill does AND when to use it
- [ ] Description includes trigger phrases/keywords users would say
- [ ] SKILL.md body is under 500 lines
- [ ] Progressive disclosure: explicit "Read X when Y" instructions for bundled files
- [ ] References to other files use forward slashes (not backslashes)
- [ ] If scripts exist, SKILL.md explains when to run vs read them
- [ ] No placeholder text: `[TODO]`, `[PLACEHOLDER]`, `TBD`, `xxx`
- [ ] Code blocks have language hints

### Legacy command detection (`.claude/commands/*.md` only)
- [ ] Emit WARNING: "This file is in the legacy `.claude/commands/` location. Consider migrating to `.claude/skills/<name>/SKILL.md`."
- [ ] Validate using the unified skill schema (same rules as above)
- [ ] Legacy commands without a `name:` field: use the filename (minus `.md`) as the effective name

### File validation (for skills with subdirectories)
- [ ] All internal markdown links resolve to existing files
- [ ] All referenced scripts exist and have valid syntax
- [ ] Code blocks have language hints

---

## Agents (`.claude/agents/*.md`)

> The agent schema is best-effort based on current documentation. Prefer WARNING over ERROR for unrecognized agent fields.

### Structure validation
- [ ] YAML frontmatter has opening and closing `---` delimiters
- [ ] Required field: `name` (max 64 chars)
  > Unlike skills, agent name constraints (e.g., lowercase-hyphen-only) are not fully specified in official Anthropic documentation. Do not enforce skill-level naming strictness on agents; treat deviations as WARNING at most.
- [ ] Required field: `description` (max 1024 chars, no XML tags)
- [ ] No examples or XML tags in description field (must be in body)
- [ ] Unrecognized frontmatter fields: emit WARNING (not ERROR) — agent schema may have undocumented fields

### Field validation
- [ ] If present, `tools:` field lists recognized component names (NOT `allowed-tools:`)
- [ ] If `tools:` lists specific names, each should be a recognized Claude tool (e.g., `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `WebFetch`, `WebSearch`, `Task`, `TodoWrite`, `NotebookEdit`)
- [ ] If `model:` is present, value must be one of: `sonnet`, `opus`, `haiku`, `inherit` (or a full model ID string)
- [ ] `inherit` is valid and means "use the same model as main conversation"
- [ ] If `model:` is absent, agent inherits by default (this is valid)
- [ ] If `permissionMode:` is present, value must be one of: `default`, `acceptEdits`, `bypassPermissions`, `plan`, `ignore`

### Best practices
- [ ] Description explains when the agent should be invoked
- [ ] Body includes concrete examples of appropriate use
- [ ] If agent references skills via `skills:` field, those skills exist in `.claude/skills/`
- [ ] Clear scope definition (what it handles vs what it doesn't)

---

## CLAUDE.md / Memory Files

### Structure validation
- [ ] Valid markdown syntax
- [ ] No broken internal links

### Best practices
- [ ] Clear section organization
- [ ] Actionable instructions (not vague guidance)
- [ ] No contradictory rules

---

## Reference Files (`references/*.md`, or any `.md` in skill subdirectories)

- [ ] Valid markdown syntax
- [ ] Referenced by parent SKILL.md or agent
- [ ] No orphaned files (exist but never referenced)

---

## Scripts (`scripts/*.py`, `scripts/*.sh`, etc.)

- [ ] Valid syntax for language (Python: `python3 -c "import py_compile; py_compile.compile('FILE', doraise=True)"`, Bash: `bash -n FILE`)
- [ ] Referenced in SKILL.md or agent
- [ ] Has usage documentation (docstring or header comment)
- [ ] Executable permissions if shell script (`ls -la` to check)
- [ ] External dependencies documented if imports are non-stdlib (WARNING)

---

## Cross-Reference Validation

### Agent → Skill references
- [ ] If agent has `skills:` field, each skill name exists in `.claude/skills/`
- [ ] Skill names in frontmatter match actual directory names

### Skill → Agent references
- [ ] If skill body mentions "use the X agent" or "invoke X agent", agent X exists in `.claude/agents/`
- [ ] If skill references `/other-skill`, that skill exists in either `.claude/skills/` or `.claude/commands/` (legacy)

### Skill → File references
- [ ] If SKILL.md references `scripts/foo.py`, that file exists in the skill directory
- [ ] If SKILL.md references `references/bar.md`, that file exists in the skill directory
- [ ] If SKILL.md references `templates/baz.md`, that file exists in the skill directory

### Orphan detection
- [ ] No files in skill `scripts/` subdirectory that aren't referenced by SKILL.md
- [ ] No files in skill `references/` subdirectory that aren't referenced by SKILL.md
- [ ] No files in skill `templates/` subdirectory that aren't referenced by SKILL.md

### Related items table validation
- [ ] If a component has "Related Tools" section, verify each referenced item exists
- [ ] Check that skill names match actual directory names or command filenames
- [ ] Check that agent names match actual filenames

---

## Common False Positives to Avoid

**Do NOT flag these as errors:**

| Situation | Why it's valid |
|-----------|----------------|
| Agent using `tools:` instead of `allowed-tools:` | Agents correctly use `tools:` field |
| Agent with `model: inherit` | Valid value meaning "use same model as main conversation" |
| Skill without `model:` field | `model` is optional for skills |
| Legacy command without `name:` field | Legacy commands can use filename as effective name |
| Agent without `allowed-tools:` field | Agents use `tools:`, not `allowed-tools:` |
| Skill using `allowed-tools:` instead of `tools:` | Skills correctly use `allowed-tools:` field |
| Skill with `disable-model-invocation: true` | Valid field — prevents Claude from auto-invoking |
| Skill with `argument-hint:` | Valid field — provides slash autocomplete hints |
| Skill with `user-invocable: false` | Valid field — hides skill from slash menu |
| Skill with `context: fork` | Valid field — runs skill in isolated subagent |
| Skill with `agent: Explore` (with `context: fork`) | Valid field — specifies agent type for forked context |
| Skill with `model:` field | Valid field — forces a specific model for this skill |
| Skill with `hooks:` field | Valid field — lifecycle hooks for skill execution |
| Skill body describing `/skill-name` invocation syntax | Valid — skills ARE slash commands in the unified model |
| Agent with unrecognized field (e.g., `color`) | Agent schema may have undocumented fields — use WARNING, not ERROR |

**Before flagging a field as incorrect:**
1. Verify which component type the file is (agent vs skill) based on file path
2. Consult the Frontmatter Schemas section in SKILL.md for the correct fields
3. Only flag if the field is genuinely wrong for that specific type
4. Check the false-positive table above before emitting any error
