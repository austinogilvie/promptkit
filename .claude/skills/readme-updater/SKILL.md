---
name: readme-updater
description: "Keep README.md files current with project changes. PROACTIVELY check if README needs updates after code changes, new features, dependency changes, environment variables, or configuration updates. For creating new READMEs from scratch or comprehensive documentation, use docs-writer instead."
version: 1.0.0
---

# README Updater

## README Section Taxonomy

| Section | Update Triggers |
|---------|-----------------|
| **Title/Badges** | Version bumps, CI status changes, new integrations |
| **Description** | Major feature additions, project scope changes |
| **Features** | New capabilities added, features deprecated |
| **Prerequisites** | Runtime version changes, new system requirements |
| **Installation** | New dependencies, setup steps change |
| **Configuration** | New env vars, config file changes |
| **Usage** | API changes, new examples needed |
| **Development** | Dev tooling changes, new scripts |
| **Testing** | Test framework changes, new test commands |
| **Deployment** | Infrastructure changes, new deploy steps |
| **Contributing** | Process changes, new guidelines |
| **License** | License changes (rare) |

## Change Detection Patterns

### Dependency Files → Installation Section
- package.json, package-lock.json, yarn.lock
- requirements.txt, pyproject.toml, poetry.lock
- Gemfile, Cargo.toml, go.mod
- Any lockfile changes

### Environment Files → Configuration Section
- .env.example added or modified
- New environment variables in code (process.env.*, os.environ[*])
- Config file schema changes

### Source Structure → Multiple Sections
- New directories in src/ → may need Architecture section
- New entry points → Usage section
- New CLI commands → Usage section

### CI/CD Files → Development/Deployment Sections
- .github/workflows/* changes
- Dockerfile, docker-compose.yml changes
- Deploy scripts added or modified

### Feature Additions → Features Section
- New route handlers or API endpoints
- New major components or modules
- New integrations with external services

## Update Methodology

### Step 1: Detect What Changed
- Identify modified files since last README update
- Categorize changes by type (deps, features, config, etc.)
- Determine affected README sections

### Step 2: Preserve Existing Style
- Match existing emoji usage (or lack thereof)
- Maintain heading hierarchy and formatting
- Keep consistent voice and tone
- Preserve any custom sections

### Step 3: Apply Minimal Updates
- Add new information without rewriting existing content
- Update version numbers and requirements inline
- Add new list items to existing lists
- Only restructure if necessary

### Step 4: Validate Accuracy
- Verify commands actually work
- Check that paths and filenames are correct
- Ensure environment variable names match code
- Confirm version numbers are current

## Templates

When adding missing README sections, load `references/templates.md` for:
- Full project templates (Node.js, Python, CLI, Library)
- Individual section templates (Prerequisites, Environment Variables, Testing, etc.)

Use `references/patterns.md` when detecting what changed in the project (regex for env vars, dependencies, CLI commands).

## Integration

### With file-categorization skill
If available, use file-categorization taxonomy to identify:
- Config files that affect Installation/Configuration sections
- Docs files that may duplicate README content
- Scripts that should be documented in Usage section

### With docs-writer skill

The docs-writer skill handles comprehensive documentation creation. See [references/skill-handoffs.md](references/skill-handoffs.md) for the complete handoff protocol.

Use this handoff pattern:

| Scenario | Use readme-updater | Use docs-writer |
|----------|-------------------|-----------------|
| README exists, needs section update | Yes | No |
| README exists, needs minor edits | Yes | No |
| No README exists | No | Yes |
| README needs complete rewrite | No | Yes |
| README + additional docs needed | No | Yes |

**Escalate to docs-writer when:**
- No README.md exists and user needs one created from scratch
- User requests comprehensive documentation beyond just README
- README requires complete structural overhaul
- Documentation site or multi-file docs needed

**After docs-writer creates README:**
- readme-updater takes over for ongoing maintenance
- Apply minimal update methodology to preserve docs-writer's structure
- Use docs-writer's template as baseline for style matching

### With git history
When available, check recent commits for:
- Feature additions (feat: commits)
- Breaking changes (BREAKING: or !)
- New dependencies (chore: deps commits)

### Suggesting vs. Applying
- For small, obvious updates → Apply directly
- For structural changes → Suggest and explain
- For ambiguous changes → Ask user for clarification

## Examples

### Example 1: New Dependency Added

**User:** "I just added redis to my project, update the README"

**Process:**
1. Check package.json or requirements.txt for redis dependency
2. Locate Installation and Prerequisites sections
3. Add redis to prerequisites if it requires system installation
4. Update installation instructions if setup steps needed
5. Add Configuration section entry if REDIS_URL env var used

### Example 2: New Feature Implemented

**User:** "Update README after adding the export feature"

**Process:**
1. Identify what the export feature does from code
2. Add entry to Features section
3. Add usage example if API changed
4. Update any relevant configuration docs

### Example 3: Full README Audit

**User:** "Check if my README is up to date"

**Process:**
1. Run scripts/check-readme.py if available
2. Compare README sections against project state
3. Report outdated or missing sections
4. Suggest specific updates needed
