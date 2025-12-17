# enhanced-progressive-disclosure

> Reduce Good PM's per-prompt context overhead by 80-90% through progressive disclosure patterns adapted from ralph-wiggum plugin.

## Structure

- `specs/` - Specification documents
- `issues/` - Issue breakdowns

## Background

This project implements token efficiency improvements for the Good PM plugin by adopting progressive disclosure patterns observed in Anthropic's ralph-wiggum plugin:

- **P0:** Tiered context injection (stub vs full contract) - ~90% token savings
- **P1 + P2:** Frontmatter-based state gating *(merged per Decision D2)*
- **P3:** Centralized help command
- **P4:** Command documentation tiering

## Decisions

### D1: Commands Auto-Load Full Contract

PM commands explicitly read PM_CONTRACT.md as part of their execution, rather than relying on the stub to prompt Claude to read it. This ensures predictable, reliable access to full conventions when PM work is happening. See spec for full rationale.

### D2: Frontmatter-Only State Gating (Merge P1 + P2)

Use SESSION.md frontmatter as the sole activity gate, eliminating the separate `.active` marker file originally proposed in P1. This follows the ralph-wiggum pattern of using a single state file with frontmatter metadata.

**Key points:**
- `pm_work_detected` frontmatter flag gates stop hook (replaces `.active` marker)
- `has_content` frontmatter flag gates context hook session injection
- Stop hook resets `pm_work_detected: false` after processing (self-healing)
- No cleanup timing questions—single source of truth

**Reference:** See `~/code/github/anthropics/claude-code/plugins/ralph-wiggum/hooks/stop-hook.sh` for the file-as-gate pattern.

### D3: Include All Commands in Stub

PM_STUB.md includes all 5 commands (issues, create-spec, create-issues, setup, help) rather than just the most common ones. Token cost is negligible (~50 tokens) and having `/good-pm:help` visible reinforces the progressive disclosure pattern.

### D4: No Backwards Compatibility

Hooks assume frontmatter exists. Users must re-run `/good-pm:setup` after upgrading. Simplifies implementation—no fallback code paths.

## Issues

Execute in order. Dependencies noted where applicable.

### Phase 1: Core Token Reduction (P0)
- [x] [001-create-pm-stub-template](issues/001-create-pm-stub-template.md) - Create PM_STUB.md minimal context template
- [x] [002-modify-context-hook-stub-injection](issues/002-modify-context-hook-stub-injection.md) - Modify context hook to inject stub *(depends on 001)*
- [x] [011-update-pm-contract-header](issues/011-update-pm-contract-header.md) - Update PM_CONTRACT.md header for on-demand loading *(depends on 001, 002)*

### Phase 2: Hook Optimization (P1 + P2 Merged per D2)
- [x] [005-frontmatter-session-state](issues/005-frontmatter-session-state.md) - Add frontmatter to SESSION_TEMPLATE.md *(foundation for D2)*
- [x] [003-state-file-gating-stop-hook](issues/003-state-file-gating-stop-hook.md) - Add frontmatter-based gating to stop hook *(depends on 005)*
- [x] [004-pm-commands-create-activity-marker](issues/004-pm-commands-create-activity-marker.md) - PM commands set `pm_work_detected` flag *(depends on 005)*

### Phase 3: Documentation Tiering (P3 + P4)
- [x] [006-create-help-command](issues/006-create-help-command.md) - Create centralized /good-pm:help command
- [x] [007-refactor-setup-command](issues/007-refactor-setup-command.md) - Refactor setup.md to core instructions only *(depends on 006)*
- [x] [008-refactor-create-spec-command](issues/008-refactor-create-spec-command.md) - Refactor create-spec.md to core instructions only *(depends on 006)*
- [x] [009-refactor-create-issues-command](issues/009-refactor-create-issues-command.md) - Refactor create-issues.md to core instructions only *(depends on 006)*
- [x] [010-refactor-issues-command](issues/010-refactor-issues-command.md) - Refactor issues.md to core instructions only *(depends on 006)*

## Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Per-prompt tokens | ~4,000 | ~900 |
| Token savings | - | ~78% |
| Stop hook exit (non-PM) | ~100ms | <50ms |
| Command file sizes | 866 lines | ~530 lines |

## Getting Started

Review the spec at `specs/SPEC_enhanced-progressive-disclosure.md` for full technical details.
