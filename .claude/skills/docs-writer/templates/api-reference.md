# API Reference Template

Use this template for complete API documentation.

---

# [API Name] API Reference

## Overview

Brief description of the API, its purpose, and primary use cases.

**Base URL**: `https://api.example.com/v1`

**API Version**: v1

## Authentication

### Bearer Token

Include the token in the Authorization header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Obtaining a Token

```bash
curl -X POST https://api.example.com/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"client_id": "YOUR_CLIENT_ID", "client_secret": "YOUR_SECRET"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## Rate Limiting

| Tier | Limit | Window |
|------|-------|--------|
| Free | 100 requests | per minute |
| Pro | 1000 requests | per minute |
| Enterprise | Unlimited | - |

Rate limit headers:
- `X-RateLimit-Limit`: Maximum requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp (Unix)

## Common Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes* | Bearer token (*except public endpoints) |
| `Content-Type` | Yes | `application/json` for POST/PUT/PATCH |
| `Accept` | No | `application/json` (default) |
| `X-Request-ID` | No | Client-generated request ID for tracing |

## Pagination

List endpoints support pagination via query parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Results per page (max 100) |
| `offset` | integer | 0 | Number of results to skip |
| `cursor` | string | - | Cursor for cursor-based pagination |

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "total": 150,
    "limit": 20,
    "offset": 0,
    "has_more": true,
    "next_cursor": "abc123"
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": [
      {
        "field": "field_name",
        "message": "Specific error"
      }
    ],
    "request_id": "req_abc123"
  }
}
```

### Error Codes

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | `BAD_REQUEST` | Malformed request syntax |
| 400 | `INVALID_INPUT` | Validation error |
| 401 | `UNAUTHORIZED` | Missing/invalid auth |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 409 | `CONFLICT` | Resource conflict |
| 422 | `UNPROCESSABLE` | Semantic error |
| 429 | `RATE_LIMITED` | Rate limit exceeded |
| 500 | `INTERNAL_ERROR` | Server error |
| 503 | `SERVICE_UNAVAILABLE` | Temporary unavailability |

---

## Endpoints

### [Resource 1: Users]

#### List Users

`GET /users`

Retrieve a paginated list of users.

[See api-endpoint.md template for full structure]

#### Get User

`GET /users/{id}`

Retrieve a single user by ID.

#### Create User

`POST /users`

Create a new user.

#### Update User

`PATCH /users/{id}`

Update an existing user.

#### Delete User

`DELETE /users/{id}`

Delete a user.

---

### [Resource 2: Projects]

[Repeat endpoint documentation for each resource]

---

## Webhooks

### Overview

Webhooks notify your application when events occur.

### Events

| Event | Description |
|-------|-------------|
| `user.created` | New user created |
| `user.updated` | User updated |
| `user.deleted` | User deleted |

### Payload Format

```json
{
  "id": "evt_abc123",
  "type": "user.created",
  "created_at": "2024-01-15T10:30:00Z",
  "data": {
    "object": {
      "id": "usr_xyz789",
      "email": "user@example.com"
    }
  }
}
```

### Webhook Signatures

Verify webhook authenticity using the `X-Webhook-Signature` header:

```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

## SDKs & Libraries

| Language | Package | Documentation |
|----------|---------|---------------|
| JavaScript | `@example/sdk` | [npm](link) |
| Python | `example-sdk` | [PyPI](link) |
| Go | `github.com/example/sdk-go` | [pkg.go.dev](link) |

---

## Changelog

### v1.2.0 (2024-01-15)
- Added `projects` endpoints
- Added webhook support

### v1.1.0 (2024-01-01)
- Added pagination cursor support
- Increased rate limits

### v1.0.0 (2023-12-01)
- Initial release
