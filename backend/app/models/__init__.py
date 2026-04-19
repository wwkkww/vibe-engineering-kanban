"""Data models for the application."""
from typing import Optional
from pydantic import BaseModel, Field


class Card(BaseModel):
    """Card model."""
    id: str
    title: str
    details: str = ""


class Column(BaseModel):
    """Column model."""
    id: str
    title: str
    cardIds: list[str]


class BoardData(BaseModel):
    """Board data model."""
    columns: list[Column]
    cards: dict[str, Card]


class LoginRequest(BaseModel):
    """Login request."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response."""
    userId: str
    username: str
    token: str
    expiresIn: int


class VerifyResponse(BaseModel):
    """Verify response."""
    userId: str
    username: str
    isAuthenticated: bool


class CreateCardRequest(BaseModel):
    """Create card request."""
    columnId: str
    title: str
    details: str = ""


class UpdateCardRequest(BaseModel):
    """Update card request."""
    title: Optional[str] = None
    details: Optional[str] = None


class AITestRequest(BaseModel):
    """AI test request."""
    question: str


class AITestResponse(BaseModel):
    """AI test response."""
    response: str


class ConversationMessage(BaseModel):
    """Conversation message."""
    role: str  # 'user' or 'assistant'
    content: str


class AIAskRequest(BaseModel):
    """AI ask request."""
    userQuestion: str
    boardState: BoardData
    conversationHistory: list[ConversationMessage] = []


class AIResponse(BaseModel):
    """AI response."""
    message: str
    boardUpdates: Optional[dict] = None
