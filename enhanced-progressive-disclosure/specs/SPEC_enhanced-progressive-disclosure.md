# SPEC: enhanced-progressive-disclosure

> Reduce Good PM's per-prompt context overhead by 80-90% through progressive disclosure patterns adapted from ralph-wiggum plugin.

**Created:** 2025-12-17
**Status:** Complete
**Source:** Analysis of ralph-wiggum plugin patterns vs good-pm current implementation

---

## Overview

Good PM currently injects ~270 lines of PM_CONTRACT.md on every user prompt in PM-enabled projects, regardless of whether PM-related work is happening. This "eager loading" approach wastes tokens on non-PM tasks and can dilute Claude's focus.

This spec proposes adopting progressive disclosure patterns from the ralph-wiggum plugin: expose brief summaries initially, load detailed instructions only when needed.

## Problem Statement

**Who has this problem:** Users of good-pm plugin in Claude Code sessions.

**The problem:** Every `UserPromptSubmit` event in a PM project injects the full PM_CONTRACT.md (~3,500 tokens) even when:
- The user's prompt mentions nothing about PM work
- No PM commands will be used
- The conversation is about something entirely unrelated (debugging, feature implementation, etc.)

**Impact of not solving:**
- Wasted tokens reduce effective context window for actual work
- Diluted focus as Claude processes irrelevant PM instructions
- Expensive stop hook parses full transcript even for non-PM sessions
- Slower hook execution

## Goals

- [x] Reduce per-prompt context injection by 80-90% for non-PM work
- [x] Maintain full PM functionality when PM work is actually happening
- [x] Reduce stop hook execution time for non-PM conversations
- [x] Improve command discoverability without bloating context

### Non-Goals

- Changing core PM workflows (spec creation, issue breakdown)
- Modifying PM_CONTRACT.md philosophy or conventions
- Adding new PM features beyond disclosure optimization
- Breaking backwards compatibility with existing .good-pm projects

## Background & Context

### Current Architecture

**Context Hook (`good-pm-context.sh`):**
```bash
if [ -f "$CONTRACT" ]; then
  cat "$CONTRACT"    # Injects ALL 269 lines every time
fi
```

**Stop Hook (`good-pm-session-update.py`):**
- Parses full transcript on EVERY stop event
- Scans all messages for PM keywords
- No early exit for non-PM sessions

### ralph-wiggum Patterns (Reference)

**Pattern 1: State File Gating**
```bash
if [[ ! -f "$RALPH_STATE_FILE" ]]; then
  exit 0  # Near-zero cost when inactive
fi
```

**Pattern 2: Frontmatter-Based State**
```bash
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE")
ITERATION=$(echo "$FRONTMATTER" | grep '^iteration:' | sed 's/iteration: *//')
```

**Pattern 3: Minimal Command Descriptions**
- Frontmatter contains only essential metadata
- Detailed docs in centralized `/help` command

## Proposed Solution

### High-Level Approach

Implement a tiered loading strategy:
1. **Tier 0 (Always):** Minimal stub (~30 lines) with quick reference and command list
2. **Tier 1 (On-demand):** Full PM_CONTRACT.md when PM work is detected
3. **Tier 2 (On-demand):** Detailed command help via centralized `/help` command

### Technical Design

#### P0: Tiered Context Injection

Create `templates/PM_STUB.md` (~30 lines):
```markdown
# Good PM Active

This project uses Good PM for spec/issue tracking.

## Quick Reference
- Status: Open (0/N) → In Progress (M/N) → Complete (N/N)
- Specs: `.good-pm/specs/SPEC_<name>.md`
- Issues: `.good-pm/issues/NNN-<desc>.md`

## Commands
- `/good-pm:issues` - View status
- `/good-pm:create-spec` - Create specification
- `/good-pm:create-issues` - Break spec into issues
- `/good-pm:setup` - Initialize Good PM
- `/good-pm:help` - Detailed documentation

For full PM conventions, read: `.good-pm/context/PM_CONTRACT.md`
```

Modify `hooks/good-pm-context.sh`:
```bash
# Inject stub instead of full contract
if [ -f "$STUB" ]; then
  cat "$STUB"
fi
```

#### P1 + P2: Frontmatter-Based State Gating (Merged per Decision D2)

**Note:** P1 (separate `.active` marker) and P2 (frontmatter state) have been merged into a single approach per Decision D2, following the ralph-wiggum pattern of using a single state file.

Update SESSION_TEMPLATE.md with activity flag:
```yaml
---
pm_work_detected: false
has_content: false
last_updated: null
active_spec: null
---
```

Stop hook checks frontmatter for early exit:
```bash
# Near-zero cost check (following ralph-wiggum pattern)
PM_ACTIVE=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$SESSION" | grep '^pm_work_detected:' | grep -c 'true')
if [[ "$PM_ACTIVE" -eq 0 ]]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# ... expensive transcript analysis only if PM work detected ...

# After processing, reset the flag
sed -i '' 's/^pm_work_detected: true/pm_work_detected: false/' "$SESSION"
```

PM commands set the flag when starting work:
```bash
# In create-spec, create-issues commands
sed -i '' 's/^pm_work_detected: false/pm_work_detected: true/' "$SESSION"
```

Context hook checks `has_content` frontmatter for session injection:
```bash
HAS_CONTENT=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$SESSION" | grep '^has_content:' | grep -c 'true')
if [[ "$HAS_CONTENT" -gt 0 ]]; then
  cat "$SESSION"
fi
```

#### P3: Centralized Help Command

Create `commands/help.md`:
- Move detailed documentation from individual commands
- Argument: optional command name for specific help
- Contains: full create-spec docs, create-issues docs, concepts like Future Self Test

Trim other commands to essential instructions (~50-70 lines each).

#### P4: Command Documentation Tiering

Three-tier structure per command:
- **Tier 1 - Frontmatter:** Description, argument-hint (always visible)
- **Tier 2 - Core Instructions:** Quick usage, basic requirements (~20-30 lines)
- **Tier 3 - Detailed Reference:** Validation rules, error cases, examples (in help.md)

### User Experience

**Before (current):**
- Every prompt gets ~3,500 tokens of PM context
- Commands are self-contained but verbose

**After (proposed):**
- Non-PM prompts get ~400 tokens (stub only)
- PM work loads full context on-demand
- `/good-pm:help` provides detailed docs when needed
- Commands stay focused and quick to parse

## Implementation Plan

### Phase 1: Core Token Reduction (P0)
- [x] Create `templates/PM_STUB.md` with minimal context
- [x] Modify `hooks/good-pm-context.sh` to inject stub instead of full contract
- [x] Test PM commands still work (they read full contract as needed)
- [x] Update PM_CONTRACT.md header noting on-demand loading

### Phase 2: Hook Optimization (P1 + P2 Merged per Decision D2)
- [x] Add `pm_work_detected: false` to SESSION_TEMPLATE.md frontmatter
- [x] Modify stop hook to check `pm_work_detected` frontmatter flag first
- [x] Stop hook resets `pm_work_detected: false` after processing
- [x] Modify PM commands to set `pm_work_detected: true` when starting work
- [x] Implement `has_content` frontmatter check in context hook
- [x] ~~Handle backwards compatibility for sessions without frontmatter~~ *(Decision D4: not implemented—users re-run setup)*

### Phase 3: Documentation Tiering (P3 + P4)
- [x] Create `/good-pm:help` command with centralized detailed docs
- [x] Refactor `setup.md` from 165 to ~50 lines
- [x] Refactor `create-spec.md` from 194 to ~60 lines
- [x] Refactor `create-issues.md` from 248 to ~70 lines
- [x] Refactor `issues.md` from 259 to ~50 lines
- [x] Test all commands work correctly with slimmed docs

## Acceptance Criteria

- [x] Non-PM prompts inject <500 tokens (down from ~3,500)
- [x] PM commands function correctly with stub-based context
- [x] Stop hook exits in <50ms for non-PM sessions
- [x] `/good-pm:help` provides equivalent detailed documentation
- [x] All existing tests pass
- [x] No regression in PM workflow (create-spec, create-issues, issues status)

## Decisions

### D1: Commands Auto-Load Full Contract (Option A)

**Decision:** PM commands explicitly read PM_CONTRACT.md as part of their execution, rather than relying on the stub to prompt Claude to read it.

**Rationale:**
- Predictable—contract loads exactly when a PM command runs
- No ambiguity about when conventions apply
- Commands stay self-contained and reliable
- Stub still includes pointer for edge cases (ad-hoc PM questions)

**Implementation:** Each refactored command (Issues 007-010) must include an explicit instruction to read `.good-pm/context/PM_CONTRACT.md` for full conventions.

### D2: Frontmatter-Only State Gating (Merge P1 + P2)

**Decision:** Use SESSION.md frontmatter as the sole activity gate, eliminating the separate `.active` marker file proposed in P1.

**Rationale (from ralph-wiggum analysis):**
- ralph-wiggum uses a single state file (`.claude/ralph-loop.local.md`) where file existence IS the activity state
- For Good PM, SESSION.md persists across sessions, so we use a frontmatter flag instead of file existence
- Single source of truth eliminates orphaned markers and sync issues
- No cleanup timing questions—flag is reset by stop hook after processing
- Self-healing: stale `pm_work_detected: true` causes one extra stop hook run, then resets

**Implementation:**
- SESSION.md frontmatter includes `pm_work_detected: false` (replaces separate `.active` marker)
- Stop hook checks frontmatter flag first; if false, exits immediately (~5ms)
- PM commands set `pm_work_detected: true` when starting work
- Stop hook resets `pm_work_detected: false` after processing transcript

**Reference:** See `~/code/github/anthropics/claude-code/plugins/ralph-wiggum/hooks/stop-hook.sh` lines 13-18 for the file-as-gate pattern.

### D3: Include All Commands in Stub

**Decision:** The PM_STUB.md template includes all 5 commands rather than just the most common ones.

**Rationale:**
- Token cost is negligible (~50 extra tokens for 2 additional command lines)
- Having `/good-pm:help` visible in the stub reinforces the progressive disclosure pattern
- Users immediately know where to go for detailed documentation
- Complete discoverability without requiring users to run a command to find commands

**Implementation:** PM_STUB.md lists: issues, create-spec, create-issues, setup, help

### D4: No Backwards Compatibility for Legacy Sessions

**Decision:** Do not support SESSION.md files without frontmatter. Users must re-run `/good-pm:setup` to get the new frontmatter structure.

**Rationale:**
- Single user plugin—no migration burden
- Simplifies implementation (no fallback logic)
- Re-running setup is trivial

**Implementation:** Hooks can assume frontmatter exists. No fallback code paths needed.

---

## Open Questions

None—all questions resolved.

## Dependencies

- No external dependencies
- Internal: Good PM templates, hooks, commands

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Claude forgets PM conventions | Medium | Medium | Stub includes command list + pointer to full docs; commands explicitly read PM_CONTRACT.md |
| Session state frontmatter gets out of sync | Low | Low | Include last_updated timestamp; stop hook can validate flag matches content |
| Complexity increases with more moving parts | Medium | Low | P0 is simple (swap file); implement incrementally |
| Breaking existing .good-pm projects | Low | High | Frontmatter check gracefully falls back to content check if no frontmatter |

## Token Savings Estimates

### Per-Prompt Overhead Comparison

| Component | Current (tokens) | Proposed (tokens) |
|-----------|------------------|-------------------|
| PM_CONTRACT.md | ~3,500 | 0 (on-demand) |
| PM_STUB.md | 0 | ~400 |
| Session context | ~500 | ~500 |
| **Total** | ~4,000 | ~900 |

**Savings:** ~3,100 tokens per prompt (~78%)

### Command Size Comparison

| Command | Current Lines | Proposed Lines |
|---------|---------------|----------------|
| setup.md | 165 | ~50 |
| create-spec.md | 194 | ~60 |
| create-issues.md | 248 | ~70 |
| issues.md | 259 | ~50 |
| help.md (new) | 0 | ~300 |
| **Total** | 866 | ~530 |

## References

- [Technical Memo: Progressive Disclosure Improvements](../docs/MEMO_progressive-disclosure-improvements.md)
- [ralph-wiggum plugin](~/code/github/anthropics/claude-code/plugins/ralph-wiggum/)
- [Good PM README](../good-pm/README.md)

---

*When ready to break this into discrete issues, run: `/create-issues enhanced-progressive-disclosure/specs/SPEC_enhanced-progressive-disclosure.md`*
