---
name: removing-meta-noise
description: Strip assistant meta-noise and decision-log chatter from project management assets stored either as local documents or GitHub issues. Produces clean, confident, implementation-ready writing that reads as if written by a domain expert. Invocable via slash command or implicit discovery by an AI coding agent automatically. Use this to scrub AI-drafted specs, issues, notes, plans, or memos after interactive chat sessions with AI coding assistants.
disable-model-invocation: false
argument-hint: "<file-path-or-id>"
allowed-tools:
  - Glob
  - Read
  - Write
  - Edit
  - "mcp__plugin_wingman_wingman-mcp__issues_*"
  - Bash(gh *)
---

# Remove Meta-Noise from Project Asset

Strip assistant reasoning artifacts, decision-log chatter, and hedging language from a project management asset. The asset may be either:

- a local file such as a spec, issue draft, note, plan, or memo
- a GitHub issue, including related parent and child issues where applicable

Produce clean, confident output that reads as written by a domain expert.

## 1. Parse Argument

Read argument from `$ARGUMENTS`.

**If empty or missing**, STOP and print:

```text
Usage: /removing-meta-noise <file-path-or-id>

Examples:
  /removing-meta-noise .wingman/specifications/SPEC-000042-auth-system.md
  /removing-meta-noise SPEC-000042
  /removing-meta-noise .wingman/notes/2026-02-15-database-analysis.md
  /removing-meta-noise 123
  /removing-meta-noise https://github.com/OWNER/REPO/issues/123
````

## 2. Resolve Target Type

Determine whether the argument refers to a **local file** or a **GitHub issue**.

### Local file resolution

Use these rules:

| Input Pattern             | Resolution                              |
| ------------------------- | --------------------------------------- |
| `SPEC-NNNNNN`             | Glob `.wingman/specifications/*NNNNNN*` |
| `ISS-NNNNNN`              | Glob `.wingman/issues/*NNNNNN*`         |
| `IDEA-NNNNNN`             | Glob `.wingman/ideas/*NNNNNN*`          |
| Relative or absolute path | Resolve against working directory       |

If the resolved local file does not exist, STOP and report the error with the resolved path.

### GitHub issue resolution

Treat the argument as a GitHub issue if it is:

* a plain numeric issue number
* a full GitHub issue URL
* an issue identifier that clearly refers to a GitHub issue in the current repository context

Use `gh issue view` or equivalent via `Bash` to resolve:

* repository
* issue number
* state
* title
* body
* parent issue relationship if present
* child issue relationships if present

If the target issue cannot be resolved, STOP and report the failure.

## 3. Enforce GitHub Closed-Issue Rules

If the requested cleanup target is a **GitHub issue**:

* **Never modify a closed GitHub issue**
* If the directly requested issue is closed, **immediately reject**
* Do not inspect, traverse, or modify related issues after that rejection

Print:

```text
Refusing cleanup: the requested GitHub issue is closed. Closed issues must never be modified.
```

If the requested GitHub issue is open:

* include the requested issue
* if a parent issue exists and is open, include it
* if a parent issue exists and is closed, do not modify it
* if child issues exist, include only child issues that are open
* skip all closed child issues

## 4. Build Target Set

### If target is a local file

The target set contains exactly one item: the resolved local file.

### If target is a GitHub issue

Build a target set containing:

1. the requested open issue
2. its parent issue, only if one exists and is open
3. its child issues, only those that are open

Do not include:

* closed requested issues
* closed parent issues
* closed child issues

## 5. Read Asset Content

For each target in the target set:

### Local file

Use `Read` to load the full file content.

### GitHub issue

Use `gh issue view` or equivalent via `Bash` to load the current issue title and body.

Treat the issue body as the editable document content.

## 6. Identify Noise

For each target, scan the content for these noise categories. Build an inventory of passages to remove or rewrite.

### Structural noise

* Sections titled "Open Questions", "Decision Log", "Options Considered", "Alternatives", "Pros/Cons" where all items are resolved
* Numbered option lists (Option 1/2/3 or Alternative A/B/C) with a selection marker
* "Resolved:" or "Decision:" annotations on question items
* "Change Log", "Decision History", or "Summary of Changes" sections that are pure process artifacts
* Appendix sections containing only conversation artifacts

### Phrasal noise

* **Openers:** "We recommend", "I suggest", "After considering", "Having evaluated", "The recommendation is", "It's worth noting that", "As discussed"
* **Hedges:** "probably", "likely", "might", "could potentially", "we think", "it seems", "arguably", "in our opinion"
* **Process markers:** "TODO: remove", "mark as resolved", "decided in meeting", "per our discussion"
* **Meta-references:** "as mentioned earlier", "going back to", "to clarify", "to summarize our discussion"
* **Self-reference:** "I suggest", "I recommend", "I think we should"
* **Conversational:** "As mentioned above", "Going back to your point", "To answer your question"

**IMPORTANT: NEVER modify content inside code blocks**:

* fenced code blocks using triple backticks
* indented code blocks using 4 or more leading spaces

## 7. Rewrite

For each target, produce a cleaned version:

* **Remove** all identified noise sections and phrases
* **Collapse** resolved questions into confident assertions placed in the appropriate section
* **Convert** hedged language to direct, confident statements
* **Preserve** all substantive content, structure, and formatting
* **Preserve** genuinely unresolved open questions exactly as they are
* **Do not** change semantic meaning

### Additional rule for local files with YAML frontmatter

If the local file has YAML frontmatter:

* preserve it exactly
* update only `updatedAt` to the current ISO timestamp
* do not modify any other frontmatter fields

### Additional rule for GitHub issues

For GitHub issues:

* preserve issue title unless cleanup is clearly needed inside the title itself
* clean the issue body only
* do not add labels, comments, checklists, or metadata not already present
* do not alter issue state
* do not create or remove parent/child relationships

### Voice rules

| Before (noisy)                                                  | After (clean)                                          |
| --------------------------------------------------------------- | ------------------------------------------------------ |
| "We decided to use PostgreSQL"                                  | "The system uses PostgreSQL"                           |
| "The recommendation is to implement rate limiting at 100 req/s" | "Rate limiting is set to 100 req/s"                    |
| "Option B was selected because it provides better scalability"  | "The system uses [Option B approach] for scalability"  |
| "After careful evaluation, we'll probably go with Redis"        | "The system uses Redis for caching"                    |
| "I suggest we add authentication middleware"                    | "Authentication middleware handles request validation" |

## 8. Write Back

### Local files

When cleaning up a single local file:

* overwrite the file in place using `Write`
* do not create a new file

### GitHub issues

For each included open GitHub issue:

* update the issue body in place using `gh issue edit` or equivalent via `Bash`
* never modify any closed issue
* never create a replacement issue
* never post the cleaned text as a comment instead of editing the issue body

## 9. Report

After processing all included targets, report:

1. Which assets were updated
2. Which GitHub related issues were skipped because they were closed
3. Brief summary of what was cleaned for each updated target
   Example: "Collapsed 4 resolved questions, removed 2 option enumerations, rewrote 8 hedged phrases"
4. Any genuinely open questions that were preserved

## 10. No-Change Behavior

If no meta-noise was found in a target:

* leave it untouched
* report: `No meta-noise detected -- target left unchanged`

## Constraints

* **Closed GitHub issue requested directly**: immediately reject and make no changes anywhere
* **Closed related GitHub issues**: never modify them; skip silently but report them as skipped
* **Open child issues only**: when traversing child issues, modify only open ones
* **Single local file**: overwrite the same file
* **Code blocks**: never modify content inside fenced or indented code blocks
* **YAML frontmatter in local files**: only update `updatedAt`
* **Scope**: do not restructure beyond what is needed to remove meta-noise, do not validate technical correctness, do not change semantic meaning, and do not act as a general-purpose editor
* **Relationship traversal**: only for GitHub issues, and only parent plus direct child issues if those relationships exist
