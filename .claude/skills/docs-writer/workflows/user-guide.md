# User Guide Workflow

## Trigger

User asks for getting started guide, tutorial, or user documentation.

## Process

### Step 1: Identify User Journey

Answer these questions by examining the codebase:
- What's the first thing a user needs to do?
- What are the core workflows?
- What are common tasks?
- What configuration is needed?

### Step 2: Analyze Prerequisites

Check for:
- Required software/tools (check package.json, requirements.txt, etc.)
- Required accounts/credentials
- Required knowledge level
- System requirements

### Step 3: Create Structure

```markdown
# [Product] User Guide

## Quick Start (< 5 minutes)
Minimal steps to see something working.

## Installation
Complete setup instructions.

## Configuration
Required and optional configuration.

## Basic Usage
Core functionality walkthrough.

## Features
### Feature A
### Feature B
### Feature C

## Advanced Usage
Power user features and customization.

## Troubleshooting
Common issues and solutions.

## FAQ
Frequently asked questions.
```

### Step 4: Write Each Section

For each section:

1. **Start with outcomes**
   - "After this section, you'll be able to..."

2. **Be explicit about prerequisites**
   - What must be done before this section
   - Link to relevant prior sections

3. **Use numbered steps**
   - One action per step
   - Include expected results

4. **Include examples**
   - Show realistic usage
   - Include expected output

5. **Add troubleshooting tips**
   - Common mistakes
   - How to verify success

### Step 5: Quick Start Section

The Quick Start is critical. It should:
- Be completable in under 5 minutes
- Require minimal setup
- Produce a visible result
- Link to full documentation for details

Template:
```markdown
## Quick Start

Get [product] running in 5 minutes.

### 1. Install
```bash
[single install command]
```

### 2. Configure
```bash
[minimal configuration]
```

### 3. Run
```bash
[run command]
```

### 4. Verify
You should see:
```
[expected output]
```

Next: [Link to full installation] for complete setup options.
```

### Step 6: Review Checklist

- [ ] Quick Start works on a fresh system
- [ ] All commands are copy-pasteable
- [ ] Expected outputs are shown
- [ ] Prerequisites are complete
- [ ] Links are valid
- [ ] No assumed knowledge without explanation

## Output Options

**Single file**: `docs/user-guide.md`
- Good for simpler products
- Easy to search

**Multi-file**: `docs/guide/`
- `index.md` - Overview and navigation
- `quickstart.md` - Quick start
- `installation.md` - Full installation
- `configuration.md` - Configuration reference
- `features/` - Feature-specific guides
- `troubleshooting.md` - Problem solving
