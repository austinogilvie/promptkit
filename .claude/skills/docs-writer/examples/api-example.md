# Example: User Management API Documentation

This example demonstrates the docs-writer agent's API documentation output.

---

# User Management API Reference

## Overview

The User Management API provides endpoints for creating, reading, updating, and deleting user accounts. This API follows REST principles and returns JSON responses.

**Base URL**: `https://api.example.com/v1`

**Authentication**: Bearer token required for all endpoints except user registration.

## Authentication

Include your API token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Obtaining a Token

```bash
curl -X POST https://api.example.com/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2g..."
}
```

---

## Endpoints

### List Users

`GET /users`

Retrieve a paginated list of users.

#### Authentication

Required. Must have `users:read` permission.

#### Query Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `limit` | integer | No | 20 | Number of users per page (max: 100) |
| `offset` | integer | No | 0 | Number of users to skip |
| `status` | string | No | - | Filter by status: `active`, `inactive`, `pending` |
| `sort` | string | No | `created_at` | Sort field: `created_at`, `email`, `name` |
| `order` | string | No | `desc` | Sort order: `asc`, `desc` |

#### Response

**Success (200 OK)**

```json
{
  "data": [
    {
      "id": "usr_abc123",
      "email": "john@example.com",
      "name": "John Doe",
      "status": "active",
      "role": "member",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "usr_def456",
      "email": "jane@example.com",
      "name": "Jane Smith",
      "status": "active",
      "role": "admin",
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-14T15:45:00Z"
    }
  ],
  "pagination": {
    "total": 150,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

#### Example

```bash
curl -X GET "https://api.example.com/v1/users?limit=10&status=active" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Get User

`GET /users/{id}`

Retrieve a single user by ID.

#### Path Parameters

| Name | Type | Description |
|------|------|-------------|
| `id` | string | Unique user identifier (e.g., `usr_abc123`) |

#### Response

**Success (200 OK)**

```json
{
  "id": "usr_abc123",
  "email": "john@example.com",
  "name": "John Doe",
  "status": "active",
  "role": "member",
  "profile": {
    "avatar_url": "https://cdn.example.com/avatars/abc123.jpg",
    "bio": "Software developer",
    "location": "San Francisco, CA"
  },
  "settings": {
    "notifications": true,
    "theme": "dark"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error (404 Not Found)**

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found",
    "request_id": "req_xyz789"
  }
}
```

---

### Create User

`POST /users`

Create a new user account.

#### Request Body

```json
{
  "email": "newuser@example.com",
  "password": "securePassword123!",
  "name": "New User",
  "role": "member"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Valid email address |
| `password` | string | Yes | Min 8 chars, 1 uppercase, 1 number |
| `name` | string | Yes | User's display name |
| `role` | string | No | User role: `member` (default), `admin` |

#### Response

**Success (201 Created)**

```json
{
  "id": "usr_ghi789",
  "email": "newuser@example.com",
  "name": "New User",
  "status": "pending",
  "role": "member",
  "created_at": "2024-01-20T14:00:00Z",
  "updated_at": "2024-01-20T14:00:00Z"
}
```

**Error (400 Bad Request)**

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Validation failed",
    "details": [
      {
        "field": "password",
        "message": "Password must be at least 8 characters"
      }
    ]
  }
}
```

**Error (409 Conflict)**

```json
{
  "error": {
    "code": "CONFLICT",
    "message": "User with this email already exists"
  }
}
```

#### Example

```bash
curl -X POST https://api.example.com/v1/users \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securePassword123!",
    "name": "New User"
  }'
```

---

### Update User

`PATCH /users/{id}`

Update an existing user.

#### Path Parameters

| Name | Type | Description |
|------|------|-------------|
| `id` | string | Unique user identifier |

#### Request Body

Only include fields you want to update:

```json
{
  "name": "Updated Name",
  "profile": {
    "bio": "Updated bio"
  }
}
```

#### Response

**Success (200 OK)**

Returns the updated user object.

#### Example

```bash
curl -X PATCH https://api.example.com/v1/users/usr_abc123 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Smith"}'
```

---

### Delete User

`DELETE /users/{id}`

Permanently delete a user account.

#### Path Parameters

| Name | Type | Description |
|------|------|-------------|
| `id` | string | Unique user identifier |

#### Response

**Success (204 No Content)**

No response body.

#### Example

```bash
curl -X DELETE https://api.example.com/v1/users/usr_abc123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Error Reference

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | `INVALID_INPUT` | Request validation failed |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication |
| 403 | `FORBIDDEN` | Insufficient permissions for this action |
| 404 | `NOT_FOUND` | Requested resource does not exist |
| 409 | `CONFLICT` | Resource already exists |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

---

## Rate Limiting

- **Authenticated requests**: 1000/minute
- **Unauthenticated requests**: 60/minute

Headers included in every response:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets
