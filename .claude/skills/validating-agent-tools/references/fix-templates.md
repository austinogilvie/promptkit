# Fix Templates

Copy-paste-ready fixes to include in the memo when applicable. Referenced by SKILL.md.

---

## Missing description (for skills/agents)
```yaml
description: [What it does]. Use when [trigger conditions/keywords].
```

## Convert allowed-tools to tools (for agents)
```diff
- allowed-tools: Read, Write
+ tools: Read, Write
```

## Convert tools to allowed-tools (for skills)
```diff
- tools: Read, Write
+ allowed-tools: Read, Write
```

## Add context: fork when agent field is present (for skills)
```diff
  agent: Explore
+ context: fork
```

## Fix invalid context value (for skills)
```diff
- context: isolated
+ context: fork
```

## Fix invalid agent value (for skills)
```diff
- agent: search
+ agent: Explore
```
Valid values: `Explore`, `Plan`, `general-purpose`

## Fix model field (invalid value, for agents)
```diff
- model: gpt-4
+ model: sonnet
```
Valid values: `sonnet`, `opus`, `haiku`, `inherit`

## Migrate legacy command to skill
```text
Move: .claude/commands/my-command.md
  To: .claude/skills/my-command/SKILL.md
Add frontmatter field: name: my-command
```

## Add argument handling (for skills)
```markdown
**Input:** `$ARGUMENTS` — [description of expected input]

If `$ARGUMENTS` is empty, [ask user for input OR use default behavior].
```

## Unrecognized frontmatter field (for skills)
```diff
- version: 1.0.0
```
This field is not in the current skill schema. Known valid fields: `name`, `description`, `allowed-tools`, `argument-hint`, `user-invocable`, `disable-model-invocation`, `context`, `agent`, `model`, `hooks`.

## Unrecognized frontmatter field (for agents)
```diff
- color: green
```
This field is not confirmed in official agent documentation. It may be valid but is unverified. Verify against the latest Anthropic agent docs.
