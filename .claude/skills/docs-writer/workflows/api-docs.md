# API Documentation Workflow

## Trigger

User asks for API documentation for endpoints, routes, or services.

## Process

### Step 1: Discover Endpoints

Search for route definitions based on the project's framework:

```bash
# Express/Node.js
grep -r "router\." --include="*.ts" --include="*.js" src/

# Flask/FastAPI Python
grep -r "@app\." --include="*.py" src/
grep -r "@router\." --include="*.py" src/

# Go
grep -r "func.*Handler" --include="*.go" .

# Rails
grep -r "resources\|get\|post\|put\|delete" config/routes.rb
```

### Step 2: For Each Endpoint, Extract

- HTTP method and path
- Path parameters (`:id`, `{id}`)
- Query parameters
- Request body schema
- Response schema
- Authentication requirements
- Error responses

### Step 3: Analyze Request/Response Types

Look for:
- TypeScript interfaces/types
- Pydantic models
- JSON Schema definitions
- OpenAPI annotations in code comments

### Step 4: Generate Documentation

For each endpoint, create documentation following this structure:

```markdown
## [Resource Name]

### [Action] [Resource]
`[METHOD] /path/{param}`

[Brief description of what this endpoint does]

#### Authentication
[Required auth method or "None"]

#### Parameters

**Path Parameters**
| Name | Type | Description |
|------|------|-------------|

**Query Parameters**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|

**Request Body**
```json
{
  "field": "type and description"
}
```

#### Response

**Success (200)**
```json
{
  "example": "response"
}
```

#### Errors
| Status | Code | Description |
|--------|------|-------------|
| 400 | INVALID_INPUT | Description |
| 404 | NOT_FOUND | Description |
```

### Step 5: Organize

- Group endpoints by resource/domain
- Add overview section explaining the API
- Add authentication section
- Add error codes reference
- Generate table of contents

### Step 6: Output Options

**Single file**: `docs/api-reference.md`
- Best for smaller APIs (< 20 endpoints)
- Easy to search and navigate

**Multi-file**: `docs/api/[resource].md`
- Best for larger APIs
- Separate file per resource
- Include index.md linking all resources

## Output Structure

```markdown
# API Reference

## Overview
Brief description of the API, base URL, versioning.

## Authentication
How to authenticate requests.

## Rate Limiting
Rate limit details if applicable.

## Common Headers
Headers required for all requests.

## Endpoints

### [Resource 1]
[Endpoints for resource 1]

### [Resource 2]
[Endpoints for resource 2]

## Error Reference
Complete list of error codes.

## Changelog
API version history.
```
