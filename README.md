# promptkit

A collection of Claude Code skills, agents, and commands for enhanced AI-assisted development workflows.

## Overview

promptkit provides reusable AI tooling components that extend Claude Code's capabilities. These components encode domain expertise, enforce best practices, and automate repetitive tasks across projects.

### Key Features

- **Skills**: Reusable capabilities for documentation, code quality, database setup, and file analysis
- **Agents**: Specialized AI personas for complex multi-step tasks like data profiling
- **Commands**: Slash commands for scaffolding and project automation

## Quick Start

```bash
# Clone the repository
git clone https://github.com/austinogilvie/promptkit.git

# Copy skills to your user-level Claude Code config
cp -r promptkit/.claude/skills/* ~/.claude/skills/

# Or symlink for easy updates
ln -s $(pwd)/promptkit/.claude/skills/* ~/.claude/skills/
```

## Contents

### Skills

| Skill | Description |
|-------|-------------|
| **docs-writer** | Generate comprehensive technical documentation—API references, user guides, architecture docs, ADRs, and runbooks. Includes templates and validation scripts. |
| **readme-updater** | Keep README files synchronized with code changes. Detects dependency updates, new features, and configuration changes that require documentation updates. |
| **file-categorization** | Classify project files using an 8-category taxonomy (Config, Tests, Docs, Scripts, Source Code, Data, AI Tooling, Other). Includes automated categorization script. |
| **python-dunder-enforcer** | Ensure Python classes include appropriate dunder methods (`__repr__`, `__str__`, comparisons). Enforces best practices and provides field ranking heuristics. |
| **duckdb-setup** | Initialize and configure DuckDB databases. Handles extensions, connection settings, and project structure with security best practices for `.gitignore`. |

### Agents

| Agent | Description |
|-------|-------------|
| **data-profiler** | Perform comprehensive dataset profiling before modeling or schema design. Analyzes field structures, type distributions, null percentages, nested objects, and generates schema recommendations. |

### Commands

| Command | Description |
|---------|-------------|
| `/create-skill` | Scaffold a new Claude Code skill with proper structure (SKILL.md, scripts/, references/, assets/). |
| `/build-research-doc` | Convert a directory of interlinked Markdown research files into a single DOCX with preserved structure, links, and auto-generated TOC via Pandoc. |

## Structure

```
.claude/
├── agents/
│   └── data-profiler.md          # Dataset profiling agent
├── commands/
│   ├── create-skill.md           # Skill scaffolding command
│   ├── build-research-doc.md     # Markdown-to-DOCX converter
│   └── scripts/
│       └── build_research_doc.py # Python script for build-research-doc
└── skills/
    ├── docs-writer/
    │   ├── SKILL.md              # Main skill definition
    │   ├── workflows/            # Task-specific workflows
    │   ├── templates/            # Documentation templates
    │   ├── examples/             # Output samples
    │   └── scripts/              # Validation tools
    ├── readme-updater/
    │   ├── SKILL.md
    │   ├── references/           # Patterns and templates
    │   └── scripts/              # README checking tools
    ├── file-categorization/
    │   ├── SKILL.md
    │   ├── references/           # Pattern definitions
    │   └── scripts/              # categorize.py
    ├── python-dunder-enforcer/
    │   ├── SKILL.md
    │   └── references/           # Examples and cheatsheets
    └── duckdb-setup/
        ├── SKILL.md
        ├── references/           # Extension docs
        ├── scripts/              # init_duckdb.py
        └── assets/               # SQL templates
```

## Usage

### Using Skills

Skills activate automatically based on context when Claude Code recognizes a matching task:

```
User: "Create a README for this project"
→ Claude activates docs-writer skill

User: "Categorize the files in this repo"
→ Claude activates file-categorization skill

User: "Add __repr__ to my Python class"
→ Claude activates python-dunder-enforcer skill
```

### Using Agents

Agents are invoked via the Task tool for complex, multi-step operations:

```
User: "Profile this JSONL dataset before I build models"
→ Claude spawns data-profiler agent for comprehensive analysis
```

### Using Commands

Commands are invoked with the slash prefix:

```
/create-skill api-client "Generate typed API clients from OpenAPI specs"

/build-research-doc ~/research/my-project
/build-research-doc ./docs/analysis --output final_report.docx
```

## Installation

### User-Level (Recommended)

Install skills globally for use across all projects:

```bash
# Create Claude config directory if needed
mkdir -p ~/.claude/skills ~/.claude/agents ~/.claude/commands

# Copy or symlink components
cp -r .claude/skills/* ~/.claude/skills/
cp -r .claude/agents/* ~/.claude/agents/
cp -r .claude/commands/* ~/.claude/commands/
```

### Project-Level

Install skills for a specific project only:

```bash
# From your project root
mkdir -p .claude/skills
cp -r /path/to/promptkit/.claude/skills/docs-writer .claude/skills/
```

## Skill Design Principles

Each skill in promptkit follows these conventions:

1. **SKILL.md** contains the complete skill definition with YAML frontmatter
2. **references/** holds documentation too large for the main file
3. **scripts/** contains executable tools that support the skill
4. **assets/** stores templates, boilerplate, and static resources
5. **examples/** provides sample inputs and outputs

Skills are designed to:
- Activate automatically based on context
- Provide clear guidance without excessive explanation
- Include validation and quality checks
- Hand off to related skills when appropriate (e.g., docs-writer → readme-updater)

## License

MIT
