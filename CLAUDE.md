# PromptKit — Claude Code Configuration

PromptKit is a personal toolbox of **Claude Code AI coding-agent tools** (agents, subagents, skills, slash commands, hooks, plugins, MCP integrations).
Everything lives in: `~/code/github/hernamesbarbara/promptkit/`

Follow the patterns already present in `.claude/`.

Whenever creating or modifying any tool type, **consult the official Anthropic docs** for that specific tool.

---

# Choosing the Right Tool Type

## High-level purpose of each tool

* **CLAUDE.md** — persistent project memory & conventions.
* **Slash commands** — explicit, user-triggered workflows.
* **Subagents** — specialized personalities for parallel or isolated tasks.
* **Hooks** — automatic actions responding to lifecycle events.
* **Skills** — automatic behaviors triggered by task context.
* **Plugins** — bundles of commands/skills/hooks for sharing.
* **MCP** — integrates external tools through a common protocol.

Use each based on whether you want **manual control**, **automatic activation**, or **delegation to a specialized persona**.

---

# Slash Commands

**What they are**
Markdown files in `.claude/commands/` you trigger manually using `/name args`.

**Key traits**

* Use `$ARGUMENTS`, `$1`, `$2` for input.
* Use `allowed-tools:` to constrain pre-execution Bash.
* Use `@file` to inline repo content.
* Great for repeatable tasks (scaffolding, reviews, migrations).

**When to use**
Any workflow where you want **explicit, safe, predictable execution**.

**Minimal template**

```markdown
---
description: What this command does
argument-hint: [arg1] [arg2]
allowed-tools: Bash(...)
---

# /command-name

...instructions...
```

---

# Subagents

**What they are**
Standalone AI personas with their own system prompts, tools, and context windows.

**Why they matter**

* Prevent “context poisoning” by isolating deep analyses.
* Allow parallel execution on different tasks.
* Preserve main conversation clarity.

**General pattern**

```markdown
---
name: security-auditor
description: Security analysis tasks
tools: Read, Bash
model: sonnet
---

You are a security auditor. Look for...
```

**When to use**
Specialized expertise that benefits from isolation (security, QA, refactoring, test generation).

---

# Hooks

**What they are**
JSON-defined automations in `.claude/settings.json` that fire on specific lifecycle events—no user action needed.

**Typical events**
`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `SessionStart`

**Two styles**

* **Command hooks** — deterministic shell commands.
* **Prompt hooks** — LLM-driven logic.

**Common uses**

* Auto-lint on file edits
* Auto-test before writes
* Session initialization
* Guardrails for Bash or Write tools

**Minimal example**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/run-oxlint.sh"
          }
        ]
      }
    ]
  }
}
```

---

# Plugins

**What they are**
Shareable bundles containing commands, hooks, skills, and metadata.

**Why they matter**
A whole workspace setup becomes portable. Ideal for team workflows.

**Skeleton**

```
my-plugin/
  .claude-plugin/
    plugin.json
  commands/
  hooks/
  skills/
```

---

# Skills

**What they are**
Folders containing a `SKILL.md` and optional helper scripts.
Claude activates them **automatically** when the task context matches the description.

**Why they’re powerful**

* Enforce style rules
* Run analysis workflows
* Maintain docs
* Support systematic development patterns
* Add domain expertise without cluttering CLAUDE.md

**Where they can live**

* `~/.claude/skills/` (global)
* `.claude/skills/` (project)
* inside plugins (shared)

**Minimal pattern**

```markdown
---
name: directory-manifest
description: Maintain and use a directory manifest to map file/script relationships.
allowed-tools: ["Read", "Write", "Bash"]
---

# Instructions
...
```

**Skill vs command**

* Make it a **skill** if you want it to trigger automatically.
* Make it a **command** if you want manual control.

---

# MCP (Model Context Protocol)

**Purpose**
Expose external capabilities as tools.
Useful for integrating databases, cloud services, scrapers, file storage, dev tooling.

Treat MCP tools like local tools — same safety + access rules.

---

# Putting It All Together

**CLAUDE.md** establishes long-term project context.
**Skills** enforce automatic expertise.
**Slash commands** give reliable user-triggered workflows.
**Subagents** execute deep or parallel tasks cleanly.
**Hooks** automate routine actions.
**Plugins** bundle the whole setup.
**MCP** connects external tools.

This structure gives Claude predictable behavior while avoiding unnecessary context bloat.

---

# Official Documentation

* Subagents — [https://code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)
* Slash Commands — [https://code.claude.com/docs/en/slash-commands](https://code.claude.com/docs/en/slash-commands)
* Plugins — [https://code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins)
* Skills — [https://code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)
* Hooks — [https://code.claude.com/docs/en/hooks-guide](https://code.claude.com/docs/en/hooks-guide)
* Output Styles — [https://code.claude.com/docs/en/output-styles](https://code.claude.com/docs/en/output-styles)
* Headless — [https://code.claude.com/docs/en/headless](https://code.claude.com/docs/en/headless)
* MCP — [https://code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)
* CLAUDE.md best practices — [https://www.anthropic.com/engineering/claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices)
* Blog: Using CLAUDE.md files — [https://www.claude.com/blog/using-claude-md-files](https://www.claude.com/blog/using-claude-md-files)
