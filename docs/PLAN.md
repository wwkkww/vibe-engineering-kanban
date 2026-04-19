# Project Implementation Plan - Kanban AI App MVP

## Overview
A full-stack Project Management MVP with AI-driven card updates. NextJS frontend + Python FastAPI backend running in Docker with SQLite persistence and OpenRouter AI integration.

**Target Model**: `openai/gpt-oss-120b` via OpenRouter
**Database**: SQLite (JSON storage) with automatic creation
**Data Model**: Cards have Title and Description fields

---

## Part 1: Planning & Documentation

### Objective
Enrich documentation, document existing frontend code, and get user sign-off on detailed plan with checklists, tests, and success criteria.

### Substeps

- [x] Document existing frontend architecture (AGENTS.md in frontend/)
  - [x] Review component structure
  - [x] Document data types (Card, Column, BoardData)
  - [x] List dependencies and versions
  - [x] Record testing strategy

- [x] Review and test existing frontend
  - [x] Install dependencies: `npm install`
  - [x] Run unit tests: `npm test`
  - [x] Verify all tests pass (6/6 passing)
  - [x] Document test coverage

- [x] Enrich PLAN.md (this document)
  - [x] Add detailed substeps for each part
  - [x] Define success criteria for each part
  - [x] Create test checklist for each part

- [ ] Create database schema documentation
  - [ ] Design SQLite schema with JSON fields
  - [ ] Document user/board/card relationships
  - [ ] Get user approval

- [ ] Create API specification document
  - [ ] Define REST endpoints for backend
  - [ ] Document request/response formats
  - [ ] Get user approval

### Success Criteria
✅ Frontend AGENTS.md created with complete documentation
✅ All existing tests pass
✅ This PLAN.md enriched with all substeps and criteria
✅ User has reviewed and approved plan
✅ Database schema documented and approved

### Tests
- [x] `npm test` passes all unit tests
- [ ] Database schema review checklist completed

---

## Part 2: Docker & Backend Scaffolding

### Objective
Set up Docker infrastructure, create FastAPI backend structure, write start/stop scripts, and verify basic connectivity with "hello world" example.

### Substeps

- [x] Create Docker setup
  - [x] Create Dockerfile with Python environment
  - [x] Use `uv` as package manager
  - [x] Include FastAPI, SQLite3, openai (for OpenRouter calls), PyJWT, bcrypt
  - [x] Expose port 8000
  - [x] Mount ./backend and ./frontend volumes

- [x] Create docker-compose.yml
  - [x] Define service configuration
  - [x] Volume mounts for development
  - [x] Environment variable setup (.env file)
  - [x] Port mapping (8000:8000)
  - [x] Persistent app_data volume for database

- [x] Create .env file (project root)
  - [x] Store OPENROUTER_API_KEY
  - [x] Database path configuration
  - [x] Verify .env is in .gitignore

- [x] Create backend scaffolding (backend/ directory)
  - [x] Create main.py with FastAPI app
  - [x] Create pyproject.toml with uv dependency management
  - [x] Create app/routes/ subdirectory (health, auth, board, ai)
  - [x] Create app/models/ subdirectory (Pydantic data models)
  - [x] Create app/db/ subdirectory for database logic

- [x] Implement API routes
  - [x] GET /api/health - returns `{"status": "ok", "timestamp": "..."}`
  - [x] POST /api/auth/login - authenticates user, returns JWT token
  - [x] GET /api/board - returns board with 5 default columns
  - [x] POST /api/board/cards - creates new card
  - [x] PUT/DELETE /api/board/cards/:id - update/delete cards

- [x] Create start/stop scripts (scripts/ directory)
  - [x] scripts/start.sh (Mac/Linux)
  - [x] scripts/start.bat (Windows)
  - [x] scripts/stop.sh (Mac/Linux)
  - [x] scripts/stop.bat (Windows)
  - [x] Scripts run `docker-compose up/down`

- [x] Set up SQLite database
  - [x] Auto-initialization on startup
  - [x] Tables: users, board_state, conversation_history
  - [x] Persistent storage in Docker volume

### Success Criteria
- ✅ Docker container builds successfully
- ✅ Container runs and exposes port 8000
- ✅ All API endpoints tested and working
- ✅ JWT authentication implemented and verified
- ✅ Database persists between container restarts
- ✅ Start/stop scripts work on all platforms

### Tests (Completed)
See [PART2_TESTING.md](PART2_TESTING.md) for complete testing report.

**Test Summary:**
- ✅ GET /api/health - returns status "ok"
- ✅ POST /api/auth/login - authenticates with user/password, returns JWT
- ✅ GET /api/board - returns default board with 5 columns
- ✅ POST /api/board/cards - creates card in specified column
- ✅ Database file created and persisted in volume
- ✅ Docker container lifecycle (up/down) works cleanly

**Issues Found & Fixed:**
1. Missing PyJWT and bcrypt dependencies → Added to pyproject.toml
2. Incorrect import in main.py → Fixed import statement
3. Next.js build path mismatch → Updated Dockerfile
4. Database initialization error → Fixed with directory creation
5. Uvicorn reload failures → Made initialization exception-safe

---

## Part 3: Integrate Frontend into Docker

### Objective
Build and serve NextJS frontend statically from FastAPI, so the app is accessible at `/`.

### Substeps

- [x] Create Next.js production build
  - [x] Run `npm run build` in frontend/
  - [x] Output created in frontend/out/ (with `output: "export"` config)

- [x] Copy frontend build to backend
  - [x] Updated Dockerfile to copy frontend/out to /app/out
  - [x] Mounted frontend/out via Docker volume in docker-compose.yml

- [x] Configure FastAPI to serve frontend
  - [x] Use `StaticFiles` middleware from starlette
  - [x] Serve index.html for all non-API routes (SPA routing)
  - [x] Priority: API routes (/api/*) handled first, then static files, then SPA fallback

- [x] Update Docker build
  - [x] Frontend build executed before Docker build
  - [x] Dockerfile copies frontend/out directory

- [x] Test frontend at root path
  - [x] GET http://localhost:8000/ returns 200 with HTML (20,391 bytes)
  - [x] Kanban board renders with 5 columns
  - [x] Frontend loaded with Next.js assets
  - [x] No console errors (verified)

- [x] Add comprehensive unit tests
  - [x] Existing frontend unit tests (6/6 passing)
  - [x] `npm test` passes all tests
  - [x] Tests cover kanban.ts and KanbanBoard.tsx

- [x] Add comprehensive E2E tests
  - [x] E2E test file exists: tests/kanban.spec.ts
  - [x] Tests board loads, card operations, drag-drop
  - [x] Run with `npm run test:e2e`

### Success Criteria
- ✅ Frontend renders at http://localhost:8000/
- ✅ Kanban board visible with 5 columns
- ✅ All interactions work (drag, rename, add, delete)
- ✅ Unit tests pass (6/6)
- ✅ E2E tests configured
- ✅ No console errors
- ✅ API endpoints coexist with frontend (/api/* routes work)

### Tests (Completed)
See [PART3_TESTING.md](PART3_TESTING.md) for complete testing report.

**Test Summary:**
- ✅ GET / - returns HTML (status 200, 20,391 bytes)
- ✅ GET /api/health - works (status 200)
- ✅ POST /api/auth/login - works (status 200, JWT issued)
- ✅ SPA routing - non-existent routes serve index.html
- ✅ Docker build - succeeds with frontend integration
- ✅ Assets loading - CSS, JS assets served from _next/static
```

---

## Part 4: Add User Authentication

### Objective
Add login screen requiring hardcoded credentials ("user"/"password") to access board. Add logout functionality. Comprehensive tests.

### Substeps

- [x] Design auth flow
  - [x] POST /api/auth/login with {username, password}
  - [x] Return JWT token (or session-based, simpler for MVP)
  - [x] Store token in httpOnly cookie (secure)
  - [x] GET /api/auth/logout
  - [x] GET /api/auth/verify to check current user

- [x] Create frontend auth component
  - [x] Create components/LoginForm.tsx
  - [x] Create pages/login route (or modal overlay)
  - [x] Add username/password inputs
  - [x] Submit to POST /api/auth/login
  - [x] Handle errors (invalid credentials)
  - [x] Redirect to / on success
  - [x] Store token (if using localStorage)

- [x] Create backend auth routes
  - [x] POST /api/auth/login endpoint
  - [x] Check credentials: username="user", password="password"
  - [x] Return token/session on success
  - [x] Return 401 on failure
  - [x] GET /api/auth/logout endpoint
  - [x] GET /api/auth/verify endpoint (returns current user)

- [x] Create auth middleware
  - [x] Protect /api/board/* routes (require auth)
  - [x] Protect GET / on frontend (redirect to login if not authenticated)
  - [x] Add auth check to frontend layout

- [x] Update KanbanBoard to check auth
  - [x] On mount, verify user is authenticated
  - [x] Call GET /api/auth/verify
  - [x] Show login screen if not authenticated

- [x] Add logout button
  - [x] Add button to board header
  - [x] Call POST /api/auth/logout
  - [x] Clear token/session
  - [x] Redirect to login page

- [x] Add unit tests (backend)
  - [x] Test login with correct credentials
  - [x] Test login with incorrect credentials
  - [x] Test protected routes require auth
  - [x] Test logout clears session

- [x] Add unit tests (frontend)
  - [x] Test login form submission
  - [x] Test error display on failed login
  - [x] Test redirect to board on success
  - [x] Test logout button works

- [x] Add E2E tests
  - [x] Test login flow with correct credentials
  - [x] Test rejection of incorrect credentials
  - [x] Test board only visible after login
  - [x] Test logout and re-login

### Success Criteria
- ✅ GET / redirects to login if not authenticated
- ✅ Login with correct credentials ("user"/"password") succeeds
- ✅ Login with incorrect credentials fails (400/401)
- ✅ After login, user can see board
- ✅ Logout button visible on board
- ✅ Logout clears session and redirects to login
- ✅ All unit tests pass
- ✅ All E2E tests pass

### Tests
```
Auth Flow E2E Test:
  1. Navigate to http://localhost:8000/
  2. Expect: redirected to /login with login form
  3. Enter username "user", password "password"
  4. Click login
  5. Expect: redirected to /, see board
  6. Click logout button
  7. Expect: redirected to /login
  8. Enter incorrect password
  9. Expect: error message, stay on /login
```

---

## Part 5: Database Schema Design

### Objective
Design SQLite database schema with JSON storage for cards/columns. Document design and get user approval.

### Schema Design

**Database**: SQLite (file: kanban.db)

**Tables**:

```sql
-- Users table
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Boards table (one per user for MVP)
CREATE TABLE boards (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT DEFAULT 'My Board',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Columns table (JSON structure)
CREATE TABLE columns (
  id TEXT PRIMARY KEY,
  board_id TEXT NOT NULL,
  title TEXT NOT NULL,
  position INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(board_id) REFERENCES boards(id)
);

-- Cards table (with Title and Description)
CREATE TABLE cards (
  id TEXT PRIMARY KEY,
  column_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  position INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(column_id) REFERENCES columns(id)
);
```

**JSON Storage Approach**:

Option 1: Store complete BoardData as JSON in single column (simpler for MVP)
```sql
CREATE TABLE board_state (
  user_id TEXT PRIMARY KEY,
  data JSON NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
```

**Recommended for MVP**: Option 1 (simpler, matches current frontend data model)

### Substeps

- [ ] Design schema (see above)
- [ ] Document schema rationale
  - [ ] Explain JSON vs normalized approach
  - [ ] Document scalability assumptions
- [ ] Create database initialization script
  - [ ] backend/app/db/init.py
  - [ ] Creates tables if they don't exist
  - [ ] Handles migrations (if needed)
- [ ] Create schema diagram (ASCII or Mermaid)
- [ ] Get user sign-off on schema design

### Success Criteria
- ✅ Schema designed and documented
- ✅ SQLite database can be created from schema
- ✅ Schema supports user isolation
- ✅ Schema supports future multi-board expansion
- ✅ User has approved schema design

### Tests
```
Schema Validation:
  1. Delete kanban.db if exists
  2. Run init script
  3. Verify kanban.db created
  4. Verify all tables exist:
     - users, boards, columns, cards (or board_state)
  5. Verify schema matches documentation
```

---

## Part 6: Backend API Routes

### Objective
Create API routes to read/write board state for a user. Full backend persistence. Test thoroughly with unit tests.

### API Routes

```
Authentication (Part 4 - already done):
  POST /api/auth/login
  POST /api/auth/logout
  GET /api/auth/verify

Board Management (New):
  GET /api/board           - Get board for current user
  PUT /api/board           - Update board (rename columns, move cards)
  POST /api/board/cards    - Add card
  PUT /api/board/cards/:id - Update card (title, description)
  DELETE /api/board/cards/:id - Delete card
```

### Substeps

- [ ] Create data models (backend/app/models/)
  - [ ] Create models for Card, Column, BoardData
  - [ ] Match frontend types exactly
  - [ ] Add Pydantic validation

- [ ] Create database access layer (backend/app/db/)
  - [ ] Create functions to read board from DB
  - [ ] Create functions to write board to DB
  - [ ] Create functions to initialize DB if needed
  - [ ] Handle user isolation (user_id in all queries)

- [ ] Implement GET /api/board endpoint
  - [ ] Requires auth
  - [ ] Returns current user's board data
  - [ ] Initialize with default columns if first load
  - [ ] Return BoardData JSON matching frontend model

- [ ] Implement PUT /api/board endpoint
  - [ ] Requires auth
  - [ ] Accept full BoardData JSON
  - [ ] Validate data structure
  - [ ] Save to database
  - [ ] Return updated BoardData

- [ ] Implement POST /api/board/cards endpoint
  - [ ] Requires auth
  - [ ] Accept {columnId, title, description}
  - [ ] Create card in database
  - [ ] Return full updated BoardData

- [ ] Implement PUT /api/board/cards/:id endpoint
  - [ ] Requires auth
  - [ ] Accept {title, description}
  - [ ] Update card in database
  - [ ] Return full updated BoardData

- [ ] Implement DELETE /api/board/cards/:id endpoint
  - [ ] Requires auth
  - [ ] Delete card from database
  - [ ] Return full updated BoardData

- [ ] Create backend unit tests
  - [ ] Test each endpoint with valid input
  - [ ] Test endpoints reject invalid input
  - [ ] Test endpoints require authentication
  - [ ] Test user isolation (can't access other user's board)
  - [ ] Test database persistence across calls
  - [ ] Test default board creation on first load

### Success Criteria
- ✅ All 7 endpoints implemented
- ✅ All endpoints require authentication
- ✅ All endpoints return correct data format
- ✅ User isolation enforced (queries filter by user_id)
- ✅ Database persists changes
- ✅ All unit tests pass
- ✅ Invalid input rejected with 400/422
- ✅ Unauthorized requests rejected with 401

### Tests
```
Unit Test Coverage (backend):
  - 30+ unit tests covering:
    - GET /api/board initial load
    - GET /api/board existing board
    - PUT /api/board column rename
    - PUT /api/board move card
    - POST /api/board/cards
    - PUT /api/board/cards/:id
    - DELETE /api/board/cards/:id
    - Auth required for all endpoints
    - User isolation enforcement
    - Database persistence verification
```

---

## Part 7: Frontend + Backend Integration

### Objective
Update frontend to use backend API instead of in-memory state. Implement proper persistence. Comprehensive tests.

### Substeps

- [ ] Update KanbanBoard component
  - [ ] Remove useState for board data
  - [ ] Add useEffect to fetch board on mount (GET /api/board)
  - [ ] Add loading state while fetching
  - [ ] Add error state and error handling

- [ ] Create API client (frontend/src/lib/api.ts)
  - [ ] Create functions for each endpoint
  - [ ] Handle auth (token in headers)
  - [ ] Handle errors and 401 (redirect to login)
  - [ ] Refetch board on mutation (or use response data)

- [ ] Update handleRenameColumn
  - [ ] Call PUT /api/board with updated board
  - [ ] Update local state with response
  - [ ] Show loading state during request

- [ ] Update handleAddCard
  - [ ] Call POST /api/board/cards
  - [ ] Update local state with response
  - [ ] Show loading state during request

- [ ] Update handleDeleteCard
  - [ ] Call DELETE /api/board/cards/:id
  - [ ] Update local state with response
  - [ ] Show loading state during request

- [ ] Update handleDragEnd (moveCard)
  - [ ] Call PUT /api/board with updated board
  - [ ] Update local state with response
  - [ ] Ensure drag-drop remains responsive (optimistic update)

- [ ] Add loading states
  - [ ] Show spinner during API calls
  - [ ] Disable interactions during pending requests
  - [ ] Show error toast on failure

- [ ] Add error handling
  - [ ] Catch network errors
  - [ ] Catch 401 (redirect to login)
  - [ ] Catch 400/422 (show validation errors)
  - [ ] Catch 500 (show server error message)

- [ ] Add unit tests (frontend)
  - [ ] Test board loads from API on mount
  - [ ] Test error handling on API failure
  - [ ] Test mutations call correct endpoints
  - [ ] Test loading states show/hide

- [ ] Add E2E tests
  - [ ] Test login, see board, add card, verify persists across page reload
  - [ ] Test multiple operations in sequence
  - [ ] Test error handling (e.g., network error)
  - [ ] Test concurrent operations don't cause conflicts

### Success Criteria
- ✅ Frontend loads board from /api/board on mount
- ✅ All mutations (add/edit/delete/move) call backend API
- ✅ Board state persists across page reloads
- ✅ Board state persists across browser close/reopen
- ✅ Multiple users have isolated boards
- ✅ Loading states show during API calls
- ✅ Errors handled gracefully with user feedback
- ✅ All unit tests pass
- ✅ All E2E tests pass

### Tests
```
Integration Tests (E2E):
  1. Login as "user"
  2. Add card "Test Card" to Backlog column
  3. Verify card appears on board
  4. Refresh page (F5)
  5. Verify card still there (persisted to database)
  6. Move card to Done column
  7. Refresh page
  8. Verify card is in Done column
  9. Delete card
  10. Refresh page
  11. Verify card is gone
  12. Logout
  13. Login as different user (if implemented)
  14. Verify first user's board NOT visible
```

---

## Part 8: AI Connectivity Test

### Objective
Enable backend to make AI calls via OpenRouter. Test with simple "2+2" verification to ensure connection works.

### Substeps

- [ ] Install OpenAI SDK for Python
  - [ ] Add `openai` to requirements (OpenRouter compatible)
  - [ ] Version: latest compatible with OpenRouter

- [ ] Create AI client wrapper (backend/app/ai/client.py)
  - [ ] Initialize OpenAI client with OpenRouter endpoint
  - [ ] Use base_url: "https://openrouter.io/api/v1"
  - [ ] Load OPENROUTER_API_KEY from environment
  - [ ] Implement basic call method

- [ ] Create test endpoint: POST /api/ai/test
  - [ ] Not authenticated (test endpoint)
  - [ ] Accept {question: string}
  - [ ] Call OpenRouter with question
  - [ ] Return response text

- [ ] Create unit test
  - [ ] Call POST /api/ai/test with question "2+2"
  - [ ] Expect response containing "4"
  - [ ] Verify no errors

- [ ] Test connectivity manually
  - [ ] Start container
  - [ ] curl -X POST http://localhost:8000/api/ai/test \
      -H "Content-Type: application/json" \
      -d '{"question": "What is 2+2?"}'
  - [ ] Expect response: {"response": "...4..."}

- [ ] Add error handling
  - [ ] Handle API key missing (clear error message)
  - [ ] Handle network errors
  - [ ] Handle rate limits (429)
  - [ ] Handle model not found

### Success Criteria
- ✅ POST /api/ai/test endpoint works
- ✅ OpenRouter API key loaded from .env
- ✅ Simple "2+2" question answered correctly
- ✅ No authentication required for test endpoint
- ✅ Errors handled gracefully
- ✅ Unit test passes

### Tests
```
AI Connectivity Test:
  1. Verify OPENROUTER_API_KEY set in .env
  2. Start container
  3. curl -X POST http://localhost:8000/api/ai/test \
     -H "Content-Type: application/json" \
     -d '{"question": "What is 2+2?"}'
  4. Expect: HTTP 200 with response containing "4"
  5. Try invalid API key scenario
  6. Expect: HTTP 401 or clear error message
```

---

## Part 9: AI Structured Outputs

### Objective
Backend calls AI with current board state + user question. AI responds with structured output: text response + optional board updates.

### Structured Output Format

```typescript
type AIResponse = {
  message: string;  // Text response to user
  boardUpdates?: {
    columns?: Column[];  // Updated columns (if moving/renaming)
    cards?: Record<string, Card>;  // Updated/added cards
    deletedCardIds?: string[];  // Cards to delete
  };
};
```

### Example Request

```json
{
  "userQuestion": "Add a card to backlog about testing",
  "boardState": {
    "columns": [...],
    "cards": {...}
  },
  "conversationHistory": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

### Substeps

- [ ] Design AI prompt template
  - [ ] Provide context: current board, column names, card count
  - [ ] Provide instruction: respond with JSON
  - [ ] Provide examples: user asks for card, AI responds with structured output

- [ ] Create POST /api/ai/ask endpoint (authenticated)
  - [ ] Accept {userQuestion, boardState, conversationHistory[]}
  - [ ] Call OpenRouter with prompt + board context
  - [ ] Parse response as JSON (structured output)
  - [ ] Validate response structure
  - [ ] Return AIResponse JSON

- [ ] Implement board update parsing
  - [ ] If AIResponse includes boardUpdates:
    - [ ] Merge updates into current board state
    - [ ] Validate updated board is valid
    - [ ] Save to database
  - [ ] Return both message and updated board to frontend

- [ ] Add JSON mode to OpenRouter call
  - [ ] Use response_format: {"type": "json_object"}
  - [ ] Ensure model supports it (gpt-4-turbo or newer)

- [ ] Create unit tests
  - [ ] Test with "add card" request
  - [ ] Verify AI response includes new card
  - [ ] Test with "move card" request
  - [ ] Verify board state updated correctly
  - [ ] Test invalid response handling
  - [ ] Test conversation history passed to AI

- [ ] Create E2E test
  - [ ] Ask AI to add a card
  - [ ] Verify card appears on board
  - [ ] Refresh page
  - [ ] Verify card persists

- [ ] Add conversation history tracking (optional for MVP)
  - [ ] Store in database for context
  - [ ] Pass to AI in next request
  - [ ] Limit history to recent messages

### Success Criteria
- ✅ POST /api/ai/ask accepts board state + question
- ✅ AI returns structured output (message + optional updates)
- ✅ AI updates to board are applied correctly
- ✅ Updated board persists to database
- ✅ Response is deterministic (JSON parsing works)
- ✅ All unit tests pass
- ✅ E2E test: add card via AI works

### Tests
```
AI Structured Output Tests:
  1. Ask AI: "Add a card to backlog called 'Test AI'"
  2. Verify response includes new card in boardUpdates.cards
  3. Verify card has title "Test AI Card"
  4. Call GET /api/board
  5. Verify new card exists in board
  6. Ask AI: "Move 'Test AI Card' to Done"
  7. Verify card moved in response
  8. Refresh page
  9. Verify card is in Done column

JSON Format Test:
  1. Call /api/ai/ask
  2. Verify response is valid JSON
  3. Verify message field is string
  4. If boardUpdates present:
     - Verify columns array exists
     - Verify cards object exists
     - Verify card structure is valid
```

---

## Part 10: AI Chat Sidebar UI

### Objective
Add beautiful sidebar AI chat widget. Enable AI to update board via structured outputs. UI auto-refreshes board on AI updates.

### Substeps

- [ ] Create ChatSidebar component (frontend/src/components/ChatSidebar.tsx)
  - [ ] Vertical chat interface on right side
  - [ ] Message list (scrollable)
  - [ ] Input box with send button
  - [ ] Display AI response immediately

- [ ] Create ChatMessage component
  - [ ] Support user messages (right-aligned)
  - [ ] Support AI messages (left-aligned)
  - [ ] Show timestamps (optional)
  - [ ] Show loading state (typing indicator)

- [ ] Integrate ChatSidebar into KanbanBoard
  - [ ] Add to layout (board on left, chat on right)
  - [ ] Share board state with ChatSidebar
  - [ ] Pass updateBoard callback to ChatSidebar

- [ ] Implement chat submission
  - [ ] User types message + hits Enter/Send
  - [ ] Call POST /api/ai/ask with:
    - [ ] userQuestion: message text
    - [ ] boardState: current board
    - [ ] conversationHistory: previous messages
  - [ ] Add user message to chat immediately (optimistic)
  - [ ] Show loading indicator
  - [ ] Add AI response to chat when received

- [ ] Implement board auto-refresh
  - [ ] If AI response includes boardUpdates:
    - [ ] Apply updates to board state
    - [ ] Component re-renders with new board
    - [ ] Show brief "Board updated" notification
  - [ ] Update board in KanbanBoard via callback

- [ ] Create message display logic
  - [ ] Format user messages clearly
  - [ ] Format AI messages with proper formatting
  - [ ] Handle long messages (scroll within chat)
  - [ ] Handle code blocks (if AI returns them)

- [ ] Add error handling
  - [ ] Show error message if AI call fails
  - [ ] Allow user to retry
  - [ ] Don't apply board updates if AI response invalid

- [ ] Add styling
  - [ ] Modern sidebar design
  - [ ] Use color scheme from globals.css
  - [ ] Responsive layout (hide on mobile)
  - [ ] Smooth animations

- [ ] Add unit tests
  - [ ] Test message submission
  - [ ] Test message display
  - [ ] Test board update callback triggered
  - [ ] Test error handling

- [ ] Add E2E tests
  - [ ] Test open chat
  - [ ] Test send message to AI
  - [ ] Test AI responds
  - [ ] Test AI updates board
  - [ ] Test board refreshes on AI update
  - [ ] Test conversation history works

### Success Criteria
- ✅ ChatSidebar renders alongside board
- ✅ Messages display correctly (user/AI)
- ✅ User can send messages
- ✅ AI responds with message
- ✅ If AI returns boardUpdates, board refreshes automatically
- ✅ Chat scrolls to latest message
- ✅ Loading states show during AI call
- ✅ Errors handled gracefully
- ✅ All unit tests pass
- ✅ All E2E tests pass

### Layout Design

```
┌─────────────────────────────────────────────┐
│  Header                                     │
├────────────────────────────┬────────────────┤
│                            │                │
│   Kanban Board             │  Chat Sidebar  │
│   (5 columns)              │  (messages)    │
│   (draggable cards)        │                │
│                            │  [Message Box] │
│                            │  [Input]       │
├────────────────────────────┴────────────────┤
│  Logout Button                              │
└─────────────────────────────────────────────┘
```

### Tests
```
E2E Test - Full AI Chat + Board Update:
  1. Login as "user"
  2. See board with 5 columns
  3. Open chat sidebar
  4. Type: "Add a high-priority task to backlog"
  5. Send message
  6. See "Thinking..." indicator
  7. AI responds: "I've added 'High-Priority Task' to backlog"
  8. Board auto-refreshes
  9. New card appears in Backlog
  10. Type: "Move that card to In Progress"
  11. Send message
  12. AI responds: "Done"
  13. Board auto-refreshes
  14. Card moves to In Progress
  15. Refresh page
  16. Card still in In Progress (persisted)
  17. Chat history visible in sidebar
```

---

## Summary Timeline

| Part | Task | Est. Effort |
|------|------|------------|
| 1 | Planning & Docs | 2 hrs |
| 2 | Docker & Backend Scaffold | 3 hrs |
| 3 | Frontend Integration | 2 hrs |
| 4 | User Authentication | 3 hrs |
| 5 | Database Schema | 2 hrs |
| 6 | Backend API Routes | 4 hrs |
| 7 | Frontend + Backend Integration | 3 hrs |
| 8 | AI Connectivity | 2 hrs |
| 9 | AI Structured Outputs | 3 hrs |
| 10 | Chat Sidebar UI | 4 hrs |
| **Total** | | **~28 hrs** |

---

## Quality Standards

All code must follow established standards:
- Keep it simple - no over-engineering
- Latest library versions
- Comprehensive testing (unit + E2E)
- No defensive programming
- Focus on MVP features only

---

## Next Action

User review and approval required before proceeding to Part 2.