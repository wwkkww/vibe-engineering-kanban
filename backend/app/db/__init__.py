"""Database initialization and utilities."""
import json
import os
import sqlite3
from datetime import datetime


def get_db_path():
    """Get database path from environment or default."""
    default_path = os.getenv("DATABASE_PATH", "/tmp/kanban.db")
    return default_path


def initialize_database():
    """Initialize database with schema."""
    try:
        db_path = get_db_path()
        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Board state table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS board_state (
                user_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """
        )

        # Conversation history table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_history (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """
        )

        conn.commit()
        conn.close()
    except Exception as e:
        # Log but don't fail on initialization errors
        print(f"Warning: Database initialization error: {e}", flush=True)


def create_default_board():
    """Create default board with 5 empty columns."""
    return {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": []},
            {"id": "col-discovery", "title": "Discovery", "cardIds": []},
            {"id": "col-progress", "title": "In Progress", "cardIds": []},
            {"id": "col-review", "title": "Review", "cardIds": []},
            {"id": "col-done", "title": "Done", "cardIds": []},
        ],
        "cards": {},
    }


def get_board_state(user_id: str):
    """Get board state for user."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT data FROM board_state WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    else:
        return create_default_board()


def save_board_state(user_id: str, board_data: dict):
    """Save/update board state for user."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    board_json = json.dumps(board_data)
    cursor.execute(
        """
        INSERT INTO board_state (user_id, data, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET 
            data = excluded.data,
            updated_at = CURRENT_TIMESTAMP
    """,
        (user_id, board_json),
    )

    conn.commit()
    conn.close()


def save_conversation_message(user_id: str, role: str, content: str):
    """Save message to conversation history."""
    import uuid

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    msg_id = f"msg-{uuid.uuid4()}"

    cursor.execute(
        """
        INSERT INTO conversation_history (id, user_id, role, content, created_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    """,
        (msg_id, user_id, role, content),
    )

    conn.commit()
    conn.close()


def get_conversation_history(user_id: str, limit: int = 20):
    """Get recent conversation history."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, role, content, created_at
        FROM conversation_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """,
        (user_id, limit),
    )

    messages = []
    for row in cursor.fetchall():
        messages.append(
            {"id": row[0], "role": row[1], "content": row[2], "createdAt": row[3]}
        )

    conn.close()
    return list(reversed(messages))  # Return in chronological order


def user_exists(username: str) -> bool:
    """Check if user exists."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()

    return exists


def get_user_by_username(username: str):
    """Get user by username."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {"id": row[0], "username": row[1], "password_hash": row[2]}
    return None


def create_user(user_id: str, username: str, password_hash: str):
    """Create new user."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (id, username, password_hash)
        VALUES (?, ?, ?)
    """,
        (user_id, username, password_hash),
    )

    conn.commit()
    conn.close()

    # Create default board for new user
    save_board_state(user_id, create_default_board())
