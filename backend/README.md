# Kanban Backend

FastAPI backend for the Kanban application with AI integration.

## Quick Start

### Development with Docker

```bash
# Start the app (builds frontend and starts Docker)
./scripts/start.sh          # Mac/Linux
scripts/start.bat           # Windows

# Stop the app
./scripts/stop.sh           # Mac/Linux
scripts/stop.bat            # Windows
```

### Manual Development (Without Docker)

```bash
# Install dependencies
uv sync

# Run backend
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or with Python directly (if uv not in PATH)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Configuration

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your-key-here
DATABASE_PATH=./kanban.db
ENVIRONMENT=development
```

## API Endpoints

See `docs/API_SPEC.md` for complete API documentation.

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'
```

**Get Board:**
```bash
curl http://localhost:8000/api/board \
  -H "Cookie: auth_token=<token>"
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── models/              # Pydantic models
│   ├── routes/              # API route handlers
│   │   ├── health.py        # Health check
│   │   ├── auth.py          # Authentication
│   │   ├── board.py         # Board management
│   │   └── ai.py            # AI integration
│   └── db/                  # Database utilities
├── pyproject.toml           # Project config (uv)
└── uv.lock                  # Dependency lock file
```

## Database

SQLite database automatically created at `kanban.db` on first run.

Schema includes:
- `users` - User credentials
- `board_state` - Board state (JSON)
- `conversation_history` - AI chat history

See `docs/DATABASE_SCHEMA.md` for details.

## Testing

```bash
# Run unit tests
uv run pytest

# Run with coverage
uv run pytest --cov
```

## AI Integration

Uses OpenRouter API with `openai/gpt-oss-120b` model.

**Test AI connectivity:**
```bash
curl -X POST http://localhost:8000/api/ai/test \
  -H "Content-Type: application/json" \
  -d '{"question": "What is 2+2?"}'
```

## Development Notes

- Latest Python 3.12 with async/await
- FastAPI for high performance
- uv package manager (faster than pip)
- CORS enabled for localhost
- httpOnly cookies for session management
- Database auto-initialization

## Troubleshooting

**Port 8000 already in use:**
```bash
# Find and kill process using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows
```

**Database locked:**
```bash
# Remove old database and let it reinitialize
rm kanban.db
```

**Missing OpenRouter key:**
```bash
# Set in .env file
OPENROUTER_API_KEY=sk-or-...
```
