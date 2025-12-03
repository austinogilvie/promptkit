# Architecture Decision Record Template

Use this template for documenting architectural decisions.

---

# ADR-[NUMBER]: [TITLE]

**Date**: YYYY-MM-DD

**Status**: [Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

**Deciders**: [List of people involved in the decision]

## Context

What is the issue that we're seeing that is motivating this decision or change?

Describe the forces at play:
- Technical considerations
- Business requirements
- Team constraints
- Timeline pressures
- Dependencies on other systems

## Decision

What is the change that we're proposing and/or doing?

State the decision clearly and concisely. Include:
- The specific choice made
- Any alternatives that were considered
- Why this option was chosen

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive Consequences

- Benefit 1
- Benefit 2
- Benefit 3

### Negative Consequences

- Drawback 1 and how we'll mitigate it
- Drawback 2 and how we'll mitigate it

### Neutral Observations

- Observation that's neither good nor bad

## Alternatives Considered

### Alternative 1: [Name]

**Description**: What this alternative entails

**Pros**:
- Pro 1
- Pro 2

**Cons**:
- Con 1
- Con 2

**Why not chosen**: Reason for rejection

### Alternative 2: [Name]

[Same structure]

## Implementation

### Migration Plan

If this decision requires changes to existing systems:

1. Step 1
2. Step 2
3. Step 3

### Rollback Plan

If things go wrong:

1. How to detect the problem
2. Steps to roll back
3. Expected timeline

## Related Decisions

- [ADR-XXX](./adr-xxx.md): Related decision
- [ADR-YYY](./adr-yyy.md): Another related decision

## References

- [Link to relevant documentation](url)
- [Link to RFC or proposal](url)
- [Link to discussion thread](url)

---

## Notes

Additional context, meeting notes, or discussion points that informed this decision.

---

# ADR Template Usage Guide

## When to Write an ADR

Create an ADR when:
- Making a technology choice (language, framework, database)
- Choosing between architectural patterns
- Deciding on significant process changes
- Any decision that's hard to reverse
- Decisions that affect multiple teams or systems

## ADR Lifecycle

1. **Proposed**: Decision is under discussion
2. **Accepted**: Decision has been made and approved
3. **Deprecated**: Decision is no longer recommended
4. **Superseded**: Decision has been replaced by a new ADR

## Naming Convention

```
adr-001-use-postgresql-for-data-storage.md
adr-002-adopt-microservices-architecture.md
adr-003-implement-event-sourcing.md
```

## Storage Location

Store ADRs in:
```
docs/
└── architecture/
    └── decisions/
        ├── adr-001-database-choice.md
        ├── adr-002-api-style.md
        └── README.md  # Index of all ADRs
```

## Index Template

```markdown
# Architecture Decision Records

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](adr-001.md) | Database Choice | Accepted | 2024-01-15 |
| [002](adr-002.md) | API Style | Accepted | 2024-01-20 |
| [003](adr-003.md) | Caching Strategy | Proposed | 2024-02-01 |
```
