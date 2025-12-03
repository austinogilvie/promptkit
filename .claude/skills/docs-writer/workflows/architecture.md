# Architecture Documentation Workflow

## Trigger

User asks for architecture documentation, system design docs, or ADRs (Architecture Decision Records).

## Process

### Step 1: System Discovery

Identify the system components by examining:
- Directory structure
- Package dependencies
- Configuration files
- Entry points
- Database schemas
- API definitions

### Step 2: Map Components

For each major component, document:
- Purpose and responsibility
- Dependencies (internal and external)
- Interfaces (APIs, events, files)
- Data it owns/manages

### Step 3: Identify Patterns

Look for:
- Architectural patterns (MVC, microservices, event-driven, etc.)
- Design patterns in use
- Communication patterns (sync/async, request/response, pub/sub)
- Data flow patterns

### Step 4: Create Architecture Overview

```markdown
# [System] Architecture

## Overview
High-level description of the system and its purpose.

## Architecture Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Server    │────▶│  Database   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Cache     │
                    └─────────────┘
```

## Components

### [Component 1]
**Purpose**: What this component does
**Location**: Where in the codebase
**Dependencies**: What it requires
**Interfaces**: How other components interact with it

### [Component 2]
...

## Data Flow

### [Flow 1: User Authentication]
1. Client sends credentials to `/auth/login`
2. Server validates against database
3. Server generates JWT token
4. Token stored in client
5. Subsequent requests include token

## Design Decisions

### [Decision 1: Choice of Database]
**Context**: We needed persistent storage for user data
**Decision**: PostgreSQL
**Rationale**: ACID compliance, JSON support, team familiarity
**Consequences**: Need to manage migrations, connection pooling

## Trade-offs

| Choice | Benefit | Cost |
|--------|---------|------|
| Monolith | Simpler deployment | Scaling constraints |
| REST API | Familiar pattern | Over-fetching |
```

### Step 5: Create ADRs (if requested)

For significant decisions, create ADR documents:

```markdown
# ADR-001: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or harder because of this change?

### Positive
- Benefit 1
- Benefit 2

### Negative
- Drawback 1
- Drawback 2

### Neutral
- Observation 1
```

### Step 6: Document Integration Points

```markdown
## External Integrations

### [Service 1]
**Purpose**: Why we integrate
**Protocol**: REST/GraphQL/gRPC
**Authentication**: How we auth
**Data Exchanged**: What data flows
**Failure Handling**: What happens when it's down
```

## Output Structure

**Architecture Overview**: `docs/architecture/README.md`
**Component Details**: `docs/architecture/components/`
**ADRs**: `docs/architecture/decisions/`
**Diagrams**: `docs/architecture/diagrams/`

## Diagram Guidelines

Use ASCII diagrams for maximum compatibility:

```
Sequence:
    Client          Server          Database
       │               │               │
       │──── Request ──▶               │
       │               │──── Query ────▶
       │               │◀─── Result ───│
       │◀─── Response ─│               │

Flow:
    ┌───┐    ┌───┐    ┌───┐
    │ A │───▶│ B │───▶│ C │
    └───┘    └───┘    └───┘
              │
              ▼
            ┌───┐
            │ D │
            └───┘

Hierarchy:
    ┌─────────────────────────┐
    │        System           │
    │  ┌─────┐    ┌─────┐    │
    │  │ Svc │    │ Svc │    │
    │  │  A  │    │  B  │    │
    │  └─────┘    └─────┘    │
    └─────────────────────────┘
```
