# Technical Memo: Stop Hook Flag Reset Bug

**Date:** 2025-12-17
**Status:** Resolved
**Related:** SPEC_enhanced-progressive-disclosure.md (Decision D2)

---

## Summary

During manual testing of the enhanced-progressive-disclosure implementation, we discovered that the `pm_work_detected` frontmatter flag is not being reset to `false` after the stop hook processes. This defeats the P1+P2 optimization that gates expensive transcript analysis.

## Observed Behavior

### Test Sequence

1. **Before:** `pm_work_detected: false` (confirmed)
2. **Action:** `/good-pm:create-spec test-cycle "Testing stop hook cycle"`
3. **During:** Command correctly set `pm_work_detected: true`
4. **Stop Hook:** Fired, blocked Claude, prompted for session update
5. **Claude:** Applied Future Self test, updated session content
6. **After:** `pm_work_detected: true` ← **BUG: Should be `false`**

### Actual Session State After

```yaml
---
pm_work_detected: true    # ❌ Should be false
has_content: true         # ✅ Correct
last_updated: 2025-12-17
active_spec: SPEC_hello-cli
---
```

## Expected Behavior (per Spec)

From SPEC Decision D2:

> Stop hook resets `pm_work_detected: false` after processing transcript

The spec pseudocode shows:
```bash
# After processing, reset the flag
sed -i '' 's/^pm_work_detected: true/pm_work_detected: false/' "$SESSION"
```

## Impact

If the flag stays `true`:
- Stop hook runs expensive transcript analysis on EVERY subsequent response
- Defeats the <50ms early exit optimization for non-PM sessions
- Token overhead savings from P1+P2 are nullified

## Hypotheses

### H1: Reset Logic Not Implemented

The stop hook (`good-pm-session-update.py`) may not include the flag reset logic.

**Investigation:**
```bash
grep -n "pm_work_detected" ~/.claude/plugins/cache/promptkit/good-pm/*/hooks/good-pm-session-update.py
```

### H2: Race Condition

Timeline possibility:
1. Stop hook fires, reads `pm_work_detected: true`
2. Stop hook resets flag to `false`
3. Claude updates session (overwrites with `true` again?)
4. Response completes

This seems unlikely since Claude's update set `has_content: true` but didn't touch `pm_work_detected`.

### H3: Hook Timing Issue

The reset may need to happen AFTER Claude completes its session update, not before. Stop hooks that return "block" may not have a post-completion phase.

**Investigation:** Review Claude Code hook lifecycle documentation for Stop event behavior.

### H4: Python vs Bash Implementation Mismatch

The spec shows a bash `sed` command, but the hook is `good-pm-session-update.py`. The Python implementation may have different logic.

## Investigation Steps

### Step 1: Audit the Stop Hook

```bash
# View the full stop hook implementation
cat ~/.claude/plugins/cache/promptkit/good-pm/*/hooks/good-pm-session-update.py

# Search for flag handling
grep -A10 -B5 "pm_work_detected" ~/.claude/plugins/cache/promptkit/good-pm/*/hooks/good-pm-session-update.py
```

### Step 2: Trace Hook Execution

Add debug logging to the stop hook:
```python
import sys
print(f"DEBUG: pm_work_detected = {frontmatter.get('pm_work_detected')}", file=sys.stderr)
```

### Step 3: Test Flag Reset Manually

```bash
# Reset flag manually
sed -i '' 's/pm_work_detected: true/pm_work_detected: false/' .good-pm/session/current.md

# Verify non-PM work doesn't trigger session update prompt
# (In Claude session): "What is 2+2?"

# Check flag stayed false
head -6 .good-pm/session/current.md
```

### Step 4: Review Hook Return Value

The stop hook returns `{"decision": "block", "reason": "..."}` to trigger the session update prompt. After Claude responds, does the hook get another chance to run? Or is return-once-and-done?

## Potential Fixes

### Fix A: Add Reset After Block Response

If the hook can detect that Claude has completed its session update, reset the flag:

```python
# After Claude's response to the block
session_content = read_session()
if session_content.get('has_content'):
    update_frontmatter('pm_work_detected', 'false')
```

### Fix B: Reset at Next PM Command

Each PM command could reset the flag at the START of execution:
```markdown
## Instructions
1. Reset `pm_work_detected: false` in session frontmatter
2. Read PM_CONTRACT.md...
3. Set `pm_work_detected: true` when starting actual work
```

This ensures stale flags don't persist but adds complexity.

### Fix C: Use Different Gating Strategy

Instead of a persistent flag, use a per-conversation marker that auto-clears. This would require architectural changes to how hooks track state.

## Test Project Location

Manual testing was performed in:
```
~/code/testing-good-pm-install/
```

Session state and hook behavior can be verified there.

## References

- [SPEC_enhanced-progressive-disclosure.md](../specs/SPEC_enhanced-progressive-disclosure.md) - Decision D2
- [Manual Testing Log](../MANUAL_TESTING_GOOD_PM.md) - Full test transcript
- [ralph-wiggum stop hook](~/code/github/anthropics/claude-code/plugins/ralph-wiggum/hooks/stop-hook.sh) - Reference implementation

---

## Diagnostic Analysis

### Code Audit Findings

Auditing `good-pm-session-update.py` revealed that reset logic **does exist** but is **unreachable** in the bug scenario.

#### Existing Reset Functions

```python
def reset_pm_work_detected(session_path: Path) -> None:
    """Reset pm_work_detected flag to false after processing."""
    if not session_path.exists():
        return
    content = session_path.read_text()
    updated = content.replace('pm_work_detected: true', 'pm_work_detected: false')
    session_path.write_text(updated)
```

#### Existing Reset Call Sites

1. **Line 154** (self-healing path):
   ```python
   if not has_tool_usage and not has_pm_activity:
       reset_pm_work_detected(session_file)
       print(json.dumps({"decision": "approve"}))
       return 0
   ```
   - Only triggers when NO tools used AND NO PM keywords found
   - Intended for stale flags from previous sessions
   - **Not triggered** when `/create-spec` runs (has both tool usage and PM activity)

2. **Line 186** (update indicator detection):
   ```python
   if any(indicator in lower_msg for indicator in update_indicators):
       reset_pm_work_detected(session_file)
       print(json.dumps({"decision": "approve"}))
       return 0
   ```
   - Only triggers when last assistant message contains "session context updated" etc.
   - **Never reached** because of the `stop_hook_active` early exit

#### The `stop_hook_active` Guard (Root Cause)

The bug was in the original lines 89-92:

```python
# Prevent infinite loops - if we already blocked once, allow completion
if stop_hook_active:
    print(json.dumps({"decision": "approve"}))
    return 0
```

This check happened **before** `session_file` was defined (line 102), making it impossible to call `reset_pm_work_detected()` in this code path.

### Execution Trace

| Phase | `stop_hook_active` | Code Path | Reset Called? |
|-------|-------------------|-----------|---------------|
| 1. First stop hook call | `false` | Lines 111-197: Full transcript analysis, returns `{"decision": "block"}` | No (blocked, waiting for Claude) |
| 2. Claude responds | — | Updates session, says "Session context updated" | — |
| 3. Second stop hook call | `true` | **Line 90: Immediately returns `{"decision": "approve"}`** | **No (early exit!)** |
| 4. Result | — | `pm_work_detected: true` persists | — |

### Spec vs Implementation Mismatch

The spec pseudocode assumed a linear flow:

```bash
# After processing, reset the flag
sed -i '' 's/^pm_work_detected: true/pm_work_detected: false/' "$SESSION"
```

But Claude Code's stop hook lifecycle is **two-phase**:

1. **Phase 1:** Hook blocks → returns control to Claude
2. **Phase 2:** Claude responds → hook fires **again** with `stop_hook_active=true`

The spec didn't account for the second invocation being a distinct code path that bypasses all transcript analysis (including reset logic).

### Hypothesis Evaluation

| Hypothesis | Status | Notes |
|------------|--------|-------|
| H1: Reset logic not implemented | **Partial** | Logic existed but was unreachable from `stop_hook_active` path |
| H2: Race condition | **Ruled out** | Claude doesn't overwrite `pm_work_detected` |
| H3: Hook timing issue | **Confirmed** | Reset must happen in the `stop_hook_active=true` phase |
| H4: Python vs Bash mismatch | **Ruled out** | Python implementation was correct, just unreachable |

---

## Resolution

### Root Cause

The `stop_hook_active` check at original line 90 exited immediately before reaching any reset logic. Critically, this check happened **before** `session_file` was even defined (line 102), making it structurally impossible to reset the flag.

### Fix Applied

Moved the `stop_hook_active` check to **after** `session_file` is defined, and added the reset call:

**Before (buggy):**
```python
# Line 87
stop_hook_active = hook_input.get("stop_hook_active", False)

# Lines 89-92 - EARLY EXIT, session_file NOT YET DEFINED
if stop_hook_active:
    print(json.dumps({"decision": "approve"}))
    return 0

# ... later at line 102 ...
session_file = good_pm_dir / "session" / "current.md"
```

**After (fixed):**
```python
# Line 87
stop_hook_active = hook_input.get("stop_hook_active", False)

# Lines 89-102: Project and session checks first
good_pm_dir = Path(".good-pm")
if not good_pm_dir.exists():
    print(json.dumps({"decision": "approve"}))
    return 0

session_file = good_pm_dir / "session" / "current.md"
if not session_file.parent.exists():
    print(json.dumps({"decision": "approve"}))
    return 0

# Lines 104-109: NOW we can reset because session_file is defined
if stop_hook_active:
    reset_pm_work_detected(session_file)  # FIX: Reset before approving
    print(json.dumps({"decision": "approve"}))
    return 0
```

### Why This Fix is Correct

1. **Lifecycle alignment:** `stop_hook_active=true` signals that Claude responded to our block—the PM work cycle is complete
2. **Single responsibility:** The reset happens exactly once, at the natural "end of PM session" moment
3. **No side effects:** Non-Good PM projects still exit early (line 91-94), before the reset check
4. **Self-healing preserved:** The existing reset at line 154 still handles stale flags from edge cases

### Corrected Execution Trace

| Phase | `stop_hook_active` | Code Path | Reset Called? |
|-------|-------------------|-----------|---------------|
| 1. First stop hook call | `false` | Full transcript analysis, returns `{"decision": "block"}` | No |
| 2. Claude responds | — | Updates session | — |
| 3. Second stop hook call | `true` | **Line 107: `reset_pm_work_detected()` called** | **Yes** |
| 4. Result | — | `pm_work_detected: false` | — |

### Files Modified

- `good-pm/hooks/good-pm-session-update.py` — Moved `stop_hook_active` check, added reset call

### Verification

To verify the fix:
1. In `~/code/testing-good-pm-install/`, run `/good-pm:create-spec test-fix "Verifying flag reset"`
2. Complete the session update when prompted
3. Check `head -6 .good-pm/session/current.md`
4. Confirm `pm_work_detected: false`
