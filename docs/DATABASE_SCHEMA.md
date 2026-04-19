# Database Schema Documentation

## Overview

The Kanban application uses SQLite for persistent storage with a simplified JSON-based approach for MVP. This document outlines the database design, rationale, and implementation details.

**Database File**: `kanban.db` (created automatically in project root)
**Storage Approach**: JSON columns for simplicity and MVP speed
**Scalability**: Designed to support future normalization without major refactoring

---

## Design Approach: JSON Storage (MVP Recommendation)

### Rationale

**Chosen for MVP: Option 1 - JSON Storage**

Why JSON storage for MVP:
- **Matches frontend data model**: Frontend already uses `BoardData` with nested structure
- **Faster development**: No complex normalization queries needed
- **Easy to scale**: Simple migration path to relational schema later
- **Minimal ORM complexity**: Direct JSON serialization/deserialization
- **Query simplicity**: User isolation via single `user_id` lookup

### Trade-offs

| Aspect | JSON Storage | Normalized Relational |
|--------|--------------|----------------------|
| Development speed | Fast | Slower |
| Query flexibility | Limited | Full |
| Update operations | Replace entire board | Granular updates |
| Scalability | 1000s of cards per user | Millions of cards |
| Data consistency | Application-enforced | Database-enforced |
| Future migration | Straightforward | N/A |

**For MVP with expected <5000 cards per user: JSON is ideal**

---

## Schema Design

### Database Tables

#### Table 1: `users`

Stores user credentials (MVP only has one hardcoded user).

```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `id`: User ID (format: `user-{uuid}` or `user-1` for MVP)
- `username`: Username (hardcoded as "user" for MVP)
- `password_hash`: Hashed password (hardcoded "password" hashed for MVP)
- `created_at`: Account creation timestamp

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_users_username ON users(username);
```

#### Table 2: `board_state` (JSON Storage)

Stores complete board state per user as JSON.

```sql
CREATE TABLE board_state (
  user_id TEXT PRIMARY KEY,
  data TEXT NOT NULL,  -- JSON string of BoardData
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Columns:**
- `user_id`: Foreign key to users table (primary key = one board per user)
- `data`: Complete BoardData as JSON string
- `updated_at`: Last modification timestamp

**Indexes:**
```sql
CREATE INDEX idx_board_state_updated_at ON board_state(updated_at);
```

#### Table 3: `conversation_history` (For AI Chat Context)

Stores conversation history for AI context (optional, enables multi-turn conversations).

```sql
CREATE TABLE conversation_history (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL,  -- 'user' or 'assistant'
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Columns:**
- `id`: Message ID (format: `msg-{uuid}`)
- `user_id`: User who sent/received message
- `role`: 'user' or 'assistant'
- `content`: Message text
- `created_at`: Message timestamp

**Indexes:**
```sql
CREATE INDEX idx_conversation_user_created ON conversation_history(user_id, created_at DESC);
```

---

## BoardData JSON Structure

Data stored in `board_state.data` column matches frontend model exactly:

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
      "cardIds": ["card-4", "card-5"]
    },
    {
      "id": "col-review",
      "title": "Review",
      "cardIds": ["card-6"]
    },
    {
      "id": "col-done",
      "title": "Done",
      "cardIds": ["card-7", "card-8"]
    }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "Card Title",
      "details": "Card description"
    },
    "card-2": {
      "id": "card-2",
      "title": "Another Card",
      "details": "More details here"
    }
  }
}
```

**JSON Schema Validation:**
- `columns`: Array of Column objects (5 fixed columns for MVP)
- `cards`: Object with card IDs as keys, Card values
- **Invariant**: All cardIds in columns must exist in cards object
- **Invariant**: No orphaned cards (every card must be in some column)

---

## Data Model TypeScript Definitions

```typescript
// Matches frontend exactly
type Card = {
  id: string;           // Format: "card-{alphanumeric}"
  title: string;        // Required, 1-255 chars
  details: string;      // Optional, 0-2000 chars (description/notes)
};

type Column = {
  id: string;           // Format: "col-{columnType}"
  title: string;        // Editable, 1-50 chars
  cardIds: string[];    // Array of card IDs in this column
};

type BoardData = {
  columns: Column[];
  cards: Record<string, Card>;
};

// API Response for conversation
type ConversationMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;  // ISO timestamp
};
```

---

## Database Operations

### Initialization

```python
# backend/app/db/init.py
def initialize_database():
    """Create tables if they don't exist."""
    connection = sqlite3.connect('kanban.db')
    cursor = connection.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create board_state table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS board_state (
            user_id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create conversation_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    connection.commit()
    connection.close()
```

### Read Board State

```python
def get_board_state(user_id: str) -> BoardData:
    """Get board state for user, create default if not exists."""
    connection = sqlite3.connect('kanban.db')
    cursor = connection.cursor()
    
    cursor.execute('SELECT data FROM board_state WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    connection.close()
    
    if row:
        return json.loads(row[0])
    else:
        return create_default_board()
```

### Write Board State

```python
def save_board_state(user_id: str, board_data: BoardData):
    """Save/update board state for user."""
    connection = sqlite3.connect('kanban.db')
    cursor = connection.cursor()
    
    board_json = json.dumps(board_data)
    cursor.execute('''
        INSERT INTO board_state (user_id, data, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET 
            data = excluded.data,
            updated_at = CURRENT_TIMESTAMP
    ''', (user_id, board_json))
    
    connection.commit()
    connection.close()
```

### Save Conversation Message

```python
def save_conversation_message(user_id: str, role: str, content: str):
    """Save message to conversation history."""
    connection = sqlite3.connect('kanban.db')
    cursor = connection.cursor()
    msg_id = f"msg-{uuid.uuid4()}"
    
    cursor.execute('''
        INSERT INTO conversation_history (id, user_id, role, content)
        VALUES (?, ?, ?, ?)
    ''', (msg_id, user_id, role, content))
    
    connection.commit()
    connection.close()
```

### Get Conversation History

```python
def get_conversation_history(user_id: str, limit: int = 20) -> List[ConversationMessage]:
    """Get recent conversation history for AI context."""
    connection = sqlite3.connect('kanban.db')
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT id, role, content, created_at
        FROM conversation_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            'id': row[0],
            'role': row[1],
            'content': row[2],
            'createdAt': row[3]
        })
    
    connection.close()
    return list(reversed(messages))  # Return in chronological order
```

---

## Default Board Creation

```python
def create_default_board() -> BoardData:
    """Create default board with 5 empty columns."""
    return {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": []},
            {"id": "col-discovery", "title": "Discovery", "cardIds": []},
            {"id": "col-progress", "title": "In Progress", "cardIds": []},
            {"id": "col-review", "title": "Review", "cardIds": []},
            {"id": "col-done", "title": "Done", "cardIds": []},
        ],
        "cards": {}
    }
```

---

## User Isolation & Security

### Query Filtering

All database queries filter by `user_id` to ensure isolation:

```python
# Always include user_id in WHERE clause
def safe_query(user_id: str):
    cursor.execute('SELECT * FROM board_state WHERE user_id = ?', (user_id,))
    # User can only access their own data
```

### Authentication

- **MVP**: Hardcoded credentials ("user"/"password")
- **Session/JWT**: Stored in httpOnly cookie or header
- **All API requests**: Must include valid authentication

---

## Migration Path (Future)

If we need to scale beyond JSON storage:

1. **Keep conversation_history table** (already normalized)
2. **Normalize board_state into relational schema**:
   - Move `columns` data to `columns` table
   - Move `cards` data to `cards` table
   - Add `position` column for ordering
   - Migration script can auto-convert existing JSON

```sql
-- Future normalized schema (not for MVP)
CREATE TABLE columns (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL,
  position INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE cards (
  id TEXT PRIMARY KEY,
  column_id TEXT NOT NULL,
  title TEXT NOT NULL,
  details TEXT DEFAULT '',
  position INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(column_id) REFERENCES columns(id)
);
```

---

## Database File Location & Backup

- **Development**: `./kanban.db` (project root)
- **Docker container**: `/app/kanban.db` (mounted volume)
- **Backup**: Daily backups in `.backups/` directory (optional)

---

## Validation & Constraints

### Data Validation Rules

1. **Card title**: Required, 1-255 characters
2. **Card details**: Optional, 0-2000 characters
3. **Column title**: Required, 1-50 characters
4. **Column count**: Always 5 for MVP
5. **Card ID uniqueness**: All cards must have unique IDs
6. **Board completeness**: No orphaned cards, all cardIds must reference existing cards

### Validation Code

```python
def validate_board_data(board_data: BoardData) -> bool:
    """Validate board data integrity."""
    # Check columns count
    if len(board_data['columns']) != 5:
        raise ValueError("Must have exactly 5 columns")
    
    # Check all cardIds reference existing cards
    all_card_ids = set()
    for column in board_data['columns']:
        for card_id in column['cardIds']:
            if card_id not in board_data['cards']:
                raise ValueError(f"Card {card_id} referenced but not found")
            all_card_ids.add(card_id)
    
    # Check no orphaned cards
    for card_id in board_data['cards'].keys():
        if card_id not in all_card_ids:
            raise ValueError(f"Card {card_id} exists but not in any column")
    
    return True
```

---

## Summary

| Aspect | Detail |
|--------|--------|
| **Storage Model** | JSON (MVP) → Relational (future) |
| **User Isolation** | Per-user board in single JSON column |
| **Scalability** | 1000s of cards/user comfortable |
| **Backup** | Simple file backup (kanban.db) |
| **Migration** | Clear path to normalization |
| **Initialization** | Auto-creates tables if missing |

---

## Next Steps

1. Backend will auto-initialize database on first run
2. First login creates user record
3. First board access creates default board_state
4. All subsequent operations read/write to database

No manual database setup required.
