# API Endpoint Template

Use this template for documenting individual API endpoints.

---

## [Action] [Resource]

`[METHOD] /path/{param}`

Brief description of what this endpoint does and when to use it.

### Authentication

[Specify authentication requirement]
- `Bearer Token` - Include in Authorization header
- `API Key` - Include as X-API-Key header
- `None` - Public endpoint

### Parameters

#### Path Parameters

| Name | Type | Description |
|------|------|-------------|
| `id` | string | Unique identifier for the resource |

#### Query Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `limit` | integer | No | 20 | Maximum number of results |
| `offset` | integer | No | 0 | Number of results to skip |
| `sort` | string | No | "created_at" | Field to sort by |

#### Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | Must be `application/json` |
| `Authorization` | Yes | Bearer token |

### Request Body

```json
{
  "field1": "string (required) - Description of field1",
  "field2": 123,
  "nested": {
    "subfield": "value"
  }
}
```

### Response

#### Success Response

**Status**: `200 OK`

```json
{
  "id": "abc123",
  "field1": "value",
  "field2": 123,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Success Response (List)

**Status**: `200 OK`

```json
{
  "data": [
    {
      "id": "abc123",
      "field1": "value"
    }
  ],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

### Errors

| Status | Code | Description |
|--------|------|-------------|
| 400 | `INVALID_INPUT` | Request body validation failed |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 409 | `CONFLICT` | Resource already exists |
| 422 | `UNPROCESSABLE` | Valid syntax but semantic error |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |

#### Error Response Format

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### Examples

#### cURL

```bash
curl -X POST https://api.example.com/v1/resources \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field1": "value",
    "field2": 123
  }'
```

#### JavaScript

```javascript
const response = await fetch('https://api.example.com/v1/resources', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    field1: 'value',
    field2: 123,
  }),
});

const data = await response.json();
```

#### Python

```python
import requests

response = requests.post(
    'https://api.example.com/v1/resources',
    headers={
        'Authorization': 'Bearer YOUR_TOKEN',
        'Content-Type': 'application/json',
    },
    json={
        'field1': 'value',
        'field2': 123,
    }
)

data = response.json()
```

### Rate Limiting

This endpoint is rate limited to:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated requests

Rate limit headers included in response:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

### Notes

- [Any additional notes about this endpoint]
- [Edge cases or special behaviors]
- [Deprecation notices if applicable]
