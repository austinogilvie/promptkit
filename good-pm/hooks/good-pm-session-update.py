#!/usr/bin/env python3
"""
Good PM Session Update Hook (Stop Event)

Blocks Claude from ending a response until session context is reviewed.
This converts Good PM from a vocabulary injector to a learning system by
ensuring every session can contribute to long-term memory.

Hook Event: Stop
Trigger: When Claude is about to end its response

Exit codes:
- 0 with {"decision": "approve"} - Allow response to complete
- 0 with {"decision": "block", "reason": "..."} - Block and continue conversation
"""

import json
import re
import sys
from pathlib import Path


def check_pm_work_detected(session_path: Path) -> bool:
    """Check SESSION.md frontmatter for pm_work_detected flag (D4: assumes frontmatter exists)."""
    if not session_path.exists():
        return False

    content = session_path.read_text()
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False  # No frontmatter = no PM work

    frontmatter = frontmatter_match.group(1)
    return 'pm_work_detected: true' in frontmatter


def reset_pm_work_detected(session_path: Path) -> None:
    """Reset pm_work_detected flag to false after processing."""
    if not session_path.exists():
        return

    content = session_path.read_text()
    updated = content.replace('pm_work_detected: true', 'pm_work_detected: false')
    session_path.write_text(updated)


def load_transcript(transcript_path):
    """Load transcript from JSONL file."""
    transcript = []
    try:
        with open(transcript_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        # Extract message if it's a conversation entry
                        if "type" in entry and entry["type"] in ("user", "assistant"):
                            transcript.append({
                                "role": entry["type"],
                                "content": entry.get("message", {}).get("content", "")
                            })
                    except json.JSONDecodeError:
                        continue
    except (IOError, OSError):
        pass
    return transcript


def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        # If no valid input, allow completion
        print(json.dumps({"decision": "approve"}))
        return 0

    # Extract conversation context
    # Claude Code passes transcript_path, not transcript directly
    transcript_path = hook_input.get("transcript_path")
    if transcript_path:
        transcript = load_transcript(transcript_path)
    else:
        transcript = hook_input.get("transcript", [])

    stop_hook_active = hook_input.get("stop_hook_active", False)

    # Check if we're in a Good PM project
    good_pm_dir = Path(".good-pm")
    if not good_pm_dir.exists():
        # Not a Good PM project, allow completion
        print(json.dumps({"decision": "approve"}))
        return 0

    # Check if session context file exists
    session_file = good_pm_dir / "session" / "current.md"

    # If session directory doesn't exist, allow (older Good PM installation)
    if not session_file.parent.exists():
        print(json.dumps({"decision": "approve"}))
        return 0

    # Prevent infinite loops - if we already blocked once, allow completion
    # Reset pm_work_detected flag since the PM work cycle is complete (Bug fix: D2)
    if stop_hook_active:
        reset_pm_work_detected(session_file)
        print(json.dumps({"decision": "approve"}))
        return 0

    # Early exit if no PM activity detected (Decision D2)
    # This is the ralph-wiggum pattern: check state flag before expensive parsing
    if not check_pm_work_detected(session_file):
        print(json.dumps({"decision": "approve"}))
        return 0

    # Check if any meaningful PM work was done in this conversation
    # Only block if there were tool calls or PM-related activity
    has_tool_usage = False
    has_pm_activity = False
    last_assistant_msg = None

    pm_keywords = [
        "good-pm", ".good-pm", "spec", "issue", "create-spec",
        "create-issues", "implementation", "acceptance criteria"
    ]

    for msg in transcript:
        content = msg.get("content", "")

        # Check for tool_use blocks (indicates actual work was done)
        if isinstance(content, list):
            for block in content:
                if block.get("type") == "tool_use":
                    has_tool_usage = True
                    break

        # Check for PM-related keywords in messages
        if isinstance(content, str):
            lower_content = content.lower()
            if any(kw in lower_content for kw in pm_keywords):
                has_pm_activity = True
        elif isinstance(content, list):
            text_content = " ".join(
                block.get("text", "")
                for block in content
                if block.get("type") == "text"
            )
            lower_content = text_content.lower()
            if any(kw in lower_content for kw in pm_keywords):
                has_pm_activity = True

    # If no tools used and no PM activity, this is a casual conversation - don't block
    # Reset flag (self-healing for stale pm_work_detected: true)
    if not has_tool_usage and not has_pm_activity:
        reset_pm_work_detected(session_file)
        print(json.dumps({"decision": "approve"}))
        return 0

    # Get last assistant message for session update check
    for msg in reversed(transcript):
        if msg.get("role") == "assistant":
            content = msg.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    block.get("text", "")
                    for block in content
                    if block.get("type") == "text"
                )
            last_assistant_msg = content
            break

    # Keywords that indicate session context was just updated
    update_indicators = [
        "session context updated",
        "updated session",
        "notes for next session",
        "session handoff",
        "updated .good-pm/session",
        "no updates needed",
        "no changes needed",
    ]

    if last_assistant_msg:
        lower_msg = last_assistant_msg.lower()
        if any(indicator in lower_msg for indicator in update_indicators):
            # Session was updated, reset flag and approve
            reset_pm_work_detected(session_file)
            print(json.dumps({"decision": "approve"}))
            return 0

    # Block and request session context review
    # Keep reason concise - detailed instructions are in PM_CONTRACT.md (injected via UserPromptSubmit)
    reason = "Review session context before ending. Check `.good-pm/session/current.md` and apply the Future Self test. Say 'no updates needed' or update the file, then complete your response."

    print(json.dumps({
        "decision": "block",
        "reason": reason
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
