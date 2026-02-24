---
name: removing-meta-noise
description: Strip assistant meta-noise and decision-log chatter from project management assets (SPECs, issues, notes, plans, memos). Produces clean, confident, implementation-ready markdown that reads as if written by a domain expert. Invocable only via explicit slash command. Use when scrubbing AI-drafted specs, issues, ideas, or memos after interactive chat sessions with AI coding assistants.
disable-model-invocation: true
argument-hint: "<file-path-or-id>"
allowed-tools:
  - Glob
  - Read
  - Write
---

# Remove Meta-Noise from Project Asset

Strip assistant reasoning artifacts, decision-log chatter, and hedging language from a project management document. Produce a clean, confident version that reads as written by a domain expert.

## 1. Parse Argument

Read argument from `$ARGUMENTS`.

**If empty or missing**, STOP and print:

```
Usage: /removing-meta-noise <file-path-or-id>

Examples:
  /removing-meta-noise .wingman/specifications/SPEC-000042-auth-system.md
  /removing-meta-noise SPEC-000042
  /removing-meta-noise .wingman/notes/2026-02-15-database-analysis.md
```

**Resolve to absolute file path:**

| Input Pattern | Resolution |
|---|---|
| `SPEC-NNNNNN` | Glob `.wingman/specifications/*NNNNNN*` |
| `ISS-NNNNNN` | Glob `.wingman/issues/*NNNNNN*` |
| `IDEA-NNNNNN` | Glob `.wingman/ideas/*NNNNNN*` |
| Relative or absolute path | Resolve against working directory |

If the resolved file does not exist, STOP and report the error with the resolved path.

## 2. Read the File

Use `Read` to load the full file content.

## 3. Identify Noise

Scan the document for these noise categories. Build an inventory of passages to remove or rewrite.

### Structural noise

- Sections titled "Open Questions", "Decision Log", "Options Considered", "Alternatives", "Pros/Cons" where all items are resolved
- Numbered option lists (Option 1/2/3 or Alternative A/B/C) with a selection marker
- "Resolved:" or "Decision:" annotations on question items
- "Change Log", "Decision History", or "Summary of Changes" sections that are pure process artifacts
- Appendix sections containing only conversation artifacts

### Phrasal noise

- **Openers:** "We recommend", "I suggest", "After considering", "Having evaluated", "The recommendation is", "It's worth noting that", "As discussed"
- **Hedges:** "probably", "likely", "might", "could potentially", "we think", "it seems", "arguably", "in our opinion"
- **Process markers:** "TODO: remove", "mark as resolved", "decided in meeting", "per our discussion"
- **Meta-references:** "as mentioned earlier", "going back to", "to clarify", "to summarize our discussion"
- **Self-reference:** "I suggest", "I recommend", "I think we should"
- **Conversational:** "As mentioned above", "Going back to your point", "To answer your question"

**IMPORTANT: NEVER modify content inside code blocks (fenced with ``` or indented 4+ spaces).**

## 4. Rewrite

Produce a cleaned version:

- **Remove** all identified noise sections and phrases
- **Collapse** resolved questions into confident assertions placed in the appropriate document section
- **Convert** hedged language to direct, confident statements
- **Preserve** all substantive content, structure, and formatting
- **Keep** YAML frontmatter intact (update only `updatedAt` to current ISO timestamp)
- **Maintain** the document's existing section structure and hierarchy
- **Preserve** genuinely unresolved open questions exactly as they are

### Voice rules

| Before (noisy) | After (clean) |
|---|---|
| "We decided to use PostgreSQL" | "The system uses PostgreSQL" |
| "The recommendation is to implement rate limiting at 100 req/s" | "Rate limiting is set to 100 req/s" |
| "Option B was selected because it provides better scalability" | "The system uses [Option B approach] for scalability" |
| "After careful evaluation, we'll probably go with Redis" | "The system uses Redis for caching" |
| "I suggest we add authentication middleware" | "Authentication middleware handles request validation" |

## 5. Write the File

Use `Write` to overwrite the file in-place. Do not create a new file.

## 6. Report

After writing, report:

1. Confirmation the file was updated (include file path)
2. Brief summary of what was cleaned (e.g., "Collapsed 4 resolved questions, removed 2 option enumerations, rewrote 8 hedged phrases")
3. Any genuinely open questions that were preserved

**If no noise was found**, report "No meta-noise detected -- file left unchanged" and do NOT write the file.

## Constraints

- **No noise found**: Leave file untouched, report "no changes needed"
- **Genuinely open questions**: Preserve all, report that they remain
- **Code blocks**: NEVER modify content inside fenced or indented code blocks
- **YAML frontmatter**: Only update `updatedAt`; do not modify other fields
- **Scope**: Do not restructure, add content, validate technical correctness, change semantic meaning, or act as a general-purpose editor
