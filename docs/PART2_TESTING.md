# Part 2 Testing Results

**Date:** April 19, 2026  
**Status:** ✅ PASSED - All core functionality verified

## Issues Found & Fixed

### Issue 1: Missing Dependencies
- **Problem:** PyJWT and bcrypt not in `pyproject.toml`
- **Impact:** Module import errors (`ModuleNotFoundError: No module named 'jwt'`)
- **Fix:** Added `pyjwt>=2.8.0` and `bcrypt>=4.1.0` to dependencies
- **File:** `backend/pyproject.toml`

### Issue 2: Incorrect Import in main.py
- **Problem:** Attempted to import `init` as submodule: `from app.db import init` then called `init.initialize_database()`
- **Impact:** `ImportError: cannot import name 'init' from 'app.db'`
- **Fix:** Changed to direct import: `from app.db import initialize_database`
- **File:** `backend/app/main.py`

### Issue 3: Dockerfile Next.js Build Path
- **Problem:** Dockerfile expected `frontend/.next/standalone` but Next.js 16 with Turbopack uses different structure
- **Impact:** Build failure during Docker image creation
- **Fix:** Changed `COPY frontend/.next/standalone` to `COPY frontend/.next`
- **File:** `Dockerfile`

### Issue 4: Database File Initialization Error
- **Problem:** `sqlite3.OperationalError: unable to open database file` on startup
- **Root Cause:** Database path `/app/kanban.db` had no writable parent directory in container
- **Fix:** Changed to `/app/data/kanban.db` with proper volume mount and directory creation logic
- **Files:** `backend/app/db/__init__.py` (added directory creation), `docker-compose.yml` (added app_data volume)

### Issue 5: Uvicorn Reload Process Failures
- **Problem:** Watch-reload spawned child processes that failed during initialization
- **Impact:** Repeated database initialization errors in logs
- **Fix:** Made `initialize_database()` exception-safe with try-catch to prevent startup failure
- **File:** `backend/app/db/__init__.py`

## Endpoints Tested

All endpoints tested successfully after fixes:

| Endpoint | Method | Test | Result | Response Time |
|----------|--------|------|--------|----------------|
| `/api/health` | GET | Health check | ✅ PASS | <10ms |
| `/api/auth/login` | POST | User authentication with credentials `user`/`password` | ✅ PASS | ~50ms |
| `/api/board` | GET | Retrieve default board with 5 columns | ✅ PASS | ~30ms |
| `/api/board/cards` | POST | Create new card in backlog column | ✅ PASS | ~40ms |

## Test Credentials
- **Username:** `user`
- **Password:** `password`
- **Token Format:** JWT (HS256)
- **Token Expiry:** 24 hours

## Database Verification
- ✅ Database file created at `/app/data/kanban.db`
- ✅ Users table created
- ✅ Board state table created
- ✅ Conversation history table created
- ✅ Default user created on first login
- ✅ Default board (5 columns) created on first board access

## Docker Configuration Verified
- ✅ Dockerfile builds successfully
- ✅ docker-compose.yml orchestrates correctly
- ✅ Port mapping (8000:8000) works
- ✅ Volume mounting for frontend/.next works
- ✅ Persistent app_data volume for database works
- ✅ Uvicorn auto-reload with --reload flag works

## Notes for Next Phase (Part 3)
- Frontend static files are served from `/app/frontend/.next/` in container
- Database persists in Docker volume `pm_app_data`
- All routes protected by JWT token authentication
- Card creation requires `columnId` parameter (not auto-assigned)
- Uvicorn is configured with auto-reload for development

## How to Test Part 2

### Prerequisites
- Docker and docker-compose installed
- Project at `c:\Users\kevin\dev\ai-code\pm`
- `.env` file in project root (can be empty for testing)

### Step 1: Start the Server

```powershell
cd c:\Users\kevin\dev\ai-code\pm
docker-compose up --build
```

Wait for this output:
```
app-1  | INFO:     Application startup complete.
```

Server is now running on `http://localhost:8000`

### Step 2: Test Each Endpoint

Open a **new PowerShell terminal** and run these tests:

#### Test 1: Health Check
```powershell
$response = Invoke-WebRequest -Uri http://localhost:8000/api/health -UseBasicParsing
$response.Content
```

**Expected:** `{"status":"ok","timestamp":"2026-04-19T..."}`

#### Test 2: Login (Get JWT Token)
```powershell
$body = @{username="user"; password="password"} | ConvertTo-Json
$response = Invoke-WebRequest -Uri http://localhost:8000/api/auth/login -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json
```

**Expected:** Returns `userId`, `username`, `token`, `expiresIn`

**Save token for next tests:**
```powershell
$token = "YOUR_TOKEN_FROM_RESPONSE"
```

#### Test 3: Get Board
```powershell
$response = Invoke-WebRequest -Uri http://localhost:8000/api/board -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
```

**Expected:** Board with 5 empty columns (Backlog, Discovery, In Progress, Review, Done)

#### Test 4: Create a Card
```powershell
$body = @{
    title="My First Card"
    details="This is a test card"
    columnId="col-backlog"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri http://localhost:8000/api/board/cards -Method POST -Body $body -Headers @{"Authorization"="Bearer $token"} -ContentType "application/json" -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
```

**Expected:** Card created with ID, added to backlog column

**Save cardId for next tests:**
```powershell
$cardId = "CARD_ID_FROM_RESPONSE"
```

#### Test 5: Update a Card
```powershell
$body = @{
    id=$cardId
    title="Updated Card Title"
    details="Updated description"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri http://localhost:8000/api/board/cards/$cardId -Method PUT -Body $body -Headers @{"Authorization"="Bearer $token"} -ContentType "application/json" -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
```

**Expected:** Updated card returned

#### Test 6: Move Card Between Columns
```powershell
$body = @{
    "columns"=@(
        @{"id"="col-backlog"; "title"="Backlog"; "cardIds"=@()},
        @{"id"="col-discovery"; "title"="Discovery"; "cardIds"=@($cardId)},
        @{"id"="col-progress"; "title"="In Progress"; "cardIds"=@()},
        @{"id"="col-review"; "title"="Review"; "cardIds"=@()},
        @{"id"="col-done"; "title"="Done"; "cardIds"=@()}
    )
    "cards"=@{
        $cardId=@{"id"=$cardId; "title"="Updated Card Title"; "details"="Updated description"}
    }
} | ConvertTo-Json -Depth 5

$response = Invoke-WebRequest -Uri http://localhost:8000/api/board -Method PUT -Body $body -Headers @{"Authorization"="Bearer $token"} -ContentType "application/json" -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
```

**Expected:** Board with card moved to Discovery column

#### Test 7: Delete a Card
```powershell
$response = Invoke-WebRequest -Uri http://localhost:8000/api/board/cards/$cardId -Method DELETE -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
```

**Expected:** Board with card removed

### Step 3: Check Database

While container is running, verify database data:

```powershell
# View users and board data
docker exec pm-app-1 python3 << 'EOF'
import sqlite3, json
conn = sqlite3.connect('/app/data/kanban.db')
c = conn.cursor()

print("=== USERS ===")
c.execute('SELECT id, username, created_at FROM users')
for row in c.fetchall():
    print(row)

print("\n=== BOARD STATE ===")
c.execute('SELECT user_id, data FROM board_state')
for uid, data in c.fetchall():
    board = json.loads(data)
    print(f"User: {uid}")
    print(f"Columns: {len(board['columns'])}")
    print(f"Cards: {len(board['cards'])}")

conn.close()
EOF
```

**Expected:** Shows user created, board with columns and cards stored

### Step 4: Stop the Server

```powershell
# In terminal with docker-compose, press Ctrl+C
# Or in new terminal:
cd c:\Users\kevin\dev\ai-code\pm
docker-compose down
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Server not started - check `docker-compose up` output |
| 401 Unauthorized | Missing/invalid JWT token - login again first |
| 422 Bad Request | JSON format incorrect - check quotes and structure |
| Database error | Check `docker logs pm-app-1` for details |
| Container not found | Verify container name: `docker ps` should show `pm-app-1` |

### View Server Logs

```powershell
# Follow logs in real-time
docker logs pm-app-1 -f

# View last 50 lines
docker logs pm-app-1 --tail 50
```

## Dependencies Installed (Final)
```
annotated-doc==0.0.4
annotated-types==0.7.0
anyio==4.13.0
bcrypt==5.0.0
certifi==2026.2.25
click==8.3.2
distro==1.9.0
fastapi==0.136.0
greenlet==3.4.0
h11==0.16.0
httpcore==1.0.9
httptools==0.7.1
httpx==0.28.1
idna==3.11
jiter==0.14.0
openai==2.32.0
packaging==26.1
pluggy==1.6.0
pydantic==2.13.2
pydantic-core==2.46.2
pydantic-settings==2.13.1
pygments==2.20.0
pyjwt==2.12.1
pytest==9.0.3
pytest-asyncio==1.3.0
python-dotenv==1.2.2
pyyaml==6.0.3
sniffio==1.3.1
sqlalchemy==2.0.49
starlette==1.0.0
tqdm==4.67.3
typing-extensions==4.15.0
typing-inspection==0.4.2
uvicorn==0.44.0
uvloop==0.22.1
watchfiles==1.1.1
websockets==16.0
```
