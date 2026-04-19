# API Specification

## Overview

Complete REST API specification for the Kanban application backend. All endpoints run on `http://localhost:8000` in development.

**Base Path**: `/api`
**Response Format**: JSON
**Error Format**: `{"error": "error message", "code": "ERROR_CODE"}`

---

## Authentication

### Overview

MVP uses simple hardcoded credentials. Tokens stored in httpOnly cookies.

**Credentials (MVP)**:
- Username: `user`
- Password: `password`

### Session Management

- **Token Format**: JWT (or simple session ID)
- **Storage**: httpOnly cookie `auth_token`
- **Expiration**: 24 hours
- **Refresh**: Optional (auto-login on session extension)

---

## Error Codes & HTTP Status

| Status | Code | Meaning |
|--------|------|---------|
| 200 | OK | Request succeeded |
| 201 | CREATED | Resource created |
| 400 | BAD_REQUEST | Invalid input |
| 401 | UNAUTHORIZED | Missing/invalid auth |
| 403 | FORBIDDEN | Access denied |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Data conflict (e.g., duplicate) |
| 422 | UNPROCESSABLE_ENTITY | Validation error |
| 500 | INTERNAL_ERROR | Server error |

---

## Authentication Endpoints

### 1. POST /api/auth/login

Login with username and password.

**Request:**
```json
{
  "username": "user",
  "password": "password"
}
```

**Success Response (200):**
```json
{
  "userId": "user-1",
  "username": "user",
  "token": "eyJ...",
  "expiresIn": 86400
}
```

**Error Response (401):**
```json
{
  "error": "Invalid credentials",
  "code": "INVALID_CREDENTIALS"
}
```

**Side Effects:**
- Sets `auth_token` httpOnly cookie
- Creates user record if new user (MVP: only "user" allowed)
- Initializes board_state with default board if first login

---

### 2. POST /api/auth/logout

Logout current user.

**Request:**
- Requires `Authorization` header with valid token

**Success Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

**Side Effects:**
- Clears `auth_token` cookie
- Invalidates session

---

### 3. GET /api/auth/verify

Check if current session is valid.

**Request:**
- Requires `Authorization` header or valid `auth_token` cookie

**Success Response (200):**
```json
{
  "userId": "user-1",
  "username": "user",
  "isAuthenticated": true
}
```

**Error Response (401):**
```json
{
  "error": "Invalid or expired token",
  "code": "UNAUTHORIZED",
  "isAuthenticated": false
}
```

**Note**: Frontend calls this on app mount to verify session

---

## Board Endpoints

### 1. GET /api/board

Get current user's board state.

**Request:**
- Requires authentication
- No body

**Success Response (200):**
```json
{
  "columns": [
    {
      "id": "col-backlog",
      "title": "Backlog",
      "cardIds": ["card-1", "card-2"]
    },
    {
      "id": "col-discovery",
      "title": "Discovery",
      "cardIds": ["card-3"]
    },
    {
      "id": "col-progress",
      "title": "In Progress",
      "cardIds": ["card-4"]
    },
    {
      "id": "col-review",
      "title": "Review",
      "cardIds": ["card-5"]
    },
    {
      "id": "col-done",
      "title": "Done",
      "cardIds": []
    }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "First Card",
      "details": "Card details go here"
    },
    "card-2": {
      "id": "card-2",
      "title": "Second Card",
      "details": "More details"
    }
  }
}
```

**Error Response (401):**
```json
{
  "error": "Invalid or expired token",
  "code": "UNAUTHORIZED"
}
```

**Notes:**
- Returns default board with 5 empty columns if first access
- No board data transformation needed (matches frontend model exactly)

---

### 2. PUT /api/board

Update entire board (rename columns, move cards).

**Request:**
```json
{
  "columns": [
    {
      "id": "col-backlog",
      "title": "Backlog Updated",
      "cardIds": ["card-1", "card-2"]
    },
    {
      "id": "col-discovery",
      "title": "Discovery",
      "cardIds": ["card-3"]
    },
    {
      "id": "col-progress",
      "title": "In Progress",
      "cardIds": ["card-4", "card-5"]
    },
    {
      "id": "col-review",
      "title": "Review",
      "cardIds": []
    },
    {
      "id": "col-done",
      "title": "Done",
      "cardIds": ["card-6"]
    }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "First Card",
      "details": "Updated details"
    },
    "card-2": {
      "id": "card-2",
      "title": "Second Card",
      "details": "More details"
    },
    "card-3": {
      "id": "card-3",
      "title": "Third Card",
      "details": ""
    },
    "card-4": {
      "id": "card-4",
      "title": "Fourth Card",
      "details": "In progress card"
    },
    "card-5": {
      "id": "card-5",
      "title": "Fifth Card",
      "details": "Also in progress"
    },
    "card-6": {
      "id": "card-6",
      "title": "Done Card",
      "details": "This is done"
    }
  }
}
```

**Success Response (200):**
- Returns updated board (same as request body, echoed back)

**Error Response (400):**
```json
{
  "error": "Invalid board data: must have exactly 5 columns",
  "code": "INVALID_BOARD_DATA"
}
```

**Validation:**
- Must have exactly 5 columns
- All cardIds must reference existing cards
- No orphaned cards
- Card titles required, 1-255 chars
- Column titles required, 1-50 chars

**Side Effects:**
- Validates complete board structure
- Saves to database with timestamp
- Overwrites entire board state (client is source of truth)

---

### 3. POST /api/board/cards

Create new card in specified column.

**Request:**
```json
{
  "columnId": "col-backlog",
  "title": "New Card Title",
  "details": "Optional card details"
}
```

**Success Response (201):**
```json
{
  "cardId": "card-9",
  "columns": [...],
  "cards": {...}
}
```

**Error Response (400):**
```json
{
  "error": "Card title is required",
  "code": "MISSING_FIELD"
}
```

**Validation:**
- `columnId` must exist
- `title` required, 1-255 chars
- `details` optional, 0-2000 chars

**Side Effects:**
- Generates new card ID
- Appends to column.cardIds array
- Saves to database
- Returns complete updated board

---

### 4. PUT /api/board/cards/:cardId

Update existing card (title and/or details).

**Request:**
```json
{
  "title": "Updated Title",
  "details": "Updated details"
}
```

**Path Parameters:**
- `:cardId`: Card ID to update (e.g., "card-5")

**Success Response (200):**
```json
{
  "cardId": "card-5",
  "columns": [...],
  "cards": {...}
}
```

**Error Response (404):**
```json
{
  "error": "Card not found",
  "code": "CARD_NOT_FOUND"
}
```

**Validation:**
- Card must exist
- If `title` provided: 1-255 chars
- If `details` provided: 0-2000 chars

**Side Effects:**
- Updates card in place
- Saves to database
- Returns complete updated board

---

### 5. DELETE /api/board/cards/:cardId

Delete card from board.

**Request:**
- Path parameter: `:cardId`
- No body

**Success Response (200):**
```json
{
  "columns": [...],
  "cards": {...}
}
```

**Error Response (404):**
```json
{
  "error": "Card not found",
  "code": "CARD_NOT_FOUND"
}
```

**Side Effects:**
- Removes card from cards object
- Removes card ID from all column.cardIds arrays
- Saves to database
- Returns complete updated board

---

## AI Endpoints

### 1. POST /api/ai/test

Test AI connectivity (no auth required).

**Request:**
```json
{
  "question": "What is 2+2?"
}
```

**Success Response (200):**
```json
{
  "response": "2+2 equals 4."
}
```

**Error Response (500):**
```json
{
  "error": "Failed to connect to AI service",
  "code": "AI_CONNECTION_ERROR"
}
```

**Error Response (401):**
```json
{
  "error": "OpenRouter API key not configured",
  "code": "MISSING_API_KEY"
}
```

**Notes:**
- No authentication required (test endpoint)
- For troubleshooting AI connectivity
- Response is plain text from AI model

---

### 2. POST /api/ai/ask

Ask AI to help with board updates (requires auth).

**Request:**
```json
{
  "userQuestion": "Add a card to backlog about testing",
  "boardState": {
    "columns": [...],
    "cards": {...}
  },
  "conversationHistory": [
    {
      "role": "user",
      "content": "What should I do next?"
    },
    {
      "role": "assistant",
      "content": "You should focus on testing."
    }
  ]
}
```

**Success Response (200):**
```json
{
  "message": "I've added a card titled 'Testing' to the backlog.",
  "boardUpdates": {
    "columns": [...],
    "cards": {...},
    "deletedCardIds": []
  }
}
```

**Success Response (200) - No Board Changes:**
```json
{
  "message": "The backlog currently has 5 items. You might want to prioritize the highest-impact tasks.",
  "boardUpdates": null
}
```

**Error Response (400):**
```json
{
  "error": "Invalid request format",
  "code": "INVALID_REQUEST"
}
```

**Error Response (401):**
```json
{
  "error": "Invalid or expired token",
  "code": "UNAUTHORIZED"
}
```

**Request Validation:**
- `userQuestion`: Required, 1-1000 chars
- `boardState`: Required, valid BoardData structure
- `conversationHistory`: Optional, array of {role, content}

**Response Structure:**

```typescript
type AIResponse = {
  message: string;  // Text response to user
  boardUpdates?: {
    columns?: Column[];
    cards?: Record<string, Card>;
    deletedCardIds?: string[];
  } | null;
};
```

**Side Effects:**
- Saves user message to conversation_history
- Saves AI response to conversation_history
- If boardUpdates provided: validates and saves board to database
- Returns updated board state to frontend

**Notes:**
- AI prompt includes current board state for context
- Structured output: AI responds with JSON
- Board validation: backend validates any updates before saving
- Graceful degradation: if board update invalid, still returns message without updates

---

## Health Check

### GET /api/health

Check if API is running.

**Request:**
- No auth required
- No body

**Success Response (200):**
```json
{
  "status": "ok",
  "timestamp": "2026-04-19T12:34:56Z"
}
```

---

## Request/Response Format

### Standard Request

```json
{
  "field1": "value",
  "field2": 123
}
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <token>  // OR: auth_token cookie
```

### Standard Success Response

```json
{
  "data": { ... },
  "timestamp": "2026-04-19T12:34:56Z"
}
```

**HTTP Status**: 200, 201

### Standard Error Response

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "timestamp": "2026-04-19T12:34:56Z"
}
```

**HTTP Status**: 400, 401, 404, 500, etc.

---

## CORS & Security

### CORS Headers

For localhost development (will be same-origin in Docker):
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

### Security Headers

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000 (HTTPS only)
```

### HttpOnly Cookies

```
Set-Cookie: auth_token=<token>; HttpOnly; SameSite=Lax; Path=/api
```

---

## Rate Limiting (Optional for MVP)

Not implemented in MVP, but reserved for future:
- 100 requests per minute per user
- 10 AI requests per minute per user

---

## API Client Examples

### JavaScript/TypeScript (Frontend)

```typescript
// POST /api/auth/login
const login = async (username: string, password: string) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
    credentials: 'include'  // Include cookies
  });
  return response.json();
};

// GET /api/board
const getBoard = async () => {
  const response = await fetch('/api/board', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include'
  });
  if (response.status === 401) {
    window.location.href = '/login';
  }
  return response.json();
};

// PUT /api/board
const updateBoard = async (boardData: BoardData) => {
  const response = await fetch('/api/board', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(boardData),
    credentials: 'include'
  });
  return response.json();
};

// POST /api/ai/ask
const askAI = async (question: string, boardState: BoardData, history: any[]) => {
  const response = await fetch('/api/ai/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      userQuestion: question,
      boardState,
      conversationHistory: history
    }),
    credentials: 'include'
  });
  return response.json();
};
```

### Python (Backend Testing)

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "user",
    "password": "password"
})
session = requests.Session()
session.cookies.update(response.cookies)

# Get board
board = session.get(f"{BASE_URL}/board").json()

# Test AI
test_response = requests.post(f"{BASE_URL}/ai/test", json={
    "question": "What is 2+2?"
})
print(test_response.json())
```

---

## Summary Table

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/auth/login` | POST | No | Login user |
| `/auth/logout` | POST | Yes | Logout user |
| `/auth/verify` | GET | Yes | Check session |
| `/board` | GET | Yes | Get board state |
| `/board` | PUT | Yes | Update board |
| `/board/cards` | POST | Yes | Create card |
| `/board/cards/:id` | PUT | Yes | Update card |
| `/board/cards/:id` | DELETE | Yes | Delete card |
| `/ai/test` | POST | No | Test AI connection |
| `/ai/ask` | POST | Yes | Ask AI for help |
| `/health` | GET | No | Check API health |

---

## Versioning

**Current Version**: v1 (implicit in API)

Future versions (if needed):
- `/api/v1/board` - Current
- `/api/v2/board` - Future breaking changes

---

## Testing

See PLAN.md Part 6 for comprehensive backend unit tests.

All endpoints should be tested with:
- Valid input
- Invalid input (validation)
- Missing authentication
- User isolation (can't access other users' data)
