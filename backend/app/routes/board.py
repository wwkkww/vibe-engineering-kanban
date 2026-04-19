"""Board routes."""
from fastapi import APIRouter, HTTPException, Request
from app.models import BoardData
from app.db import get_board_state, save_board_state
from app.routes.auth import verify_jwt_token

router = APIRouter()


def get_current_user(request: Request) -> str:
    """Get current user from token."""
    token = request.cookies.get("auth_token")
    if not token and "authorization" in request.headers:
        auth_header = request.headers["authorization"]
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    payload = verify_jwt_token(token)
    return payload["user_id"]


@router.get("/board")
async def get_board(request: Request):
    """Get board for current user."""
    user_id = get_current_user(request)
    board = get_board_state(user_id)
    return board


@router.put("/board")
async def update_board(request: Request, board_data: BoardData):
    """Update board for current user."""
    user_id = get_current_user(request)

    # Validate board structure
    if len(board_data.columns) != 5:
        raise HTTPException(
            status_code=400, detail="Board must have exactly 5 columns"
        )

    # Check all cardIds reference existing cards
    for column in board_data.columns:
        for card_id in column.cardIds:
            if card_id not in board_data.cards:
                raise HTTPException(
                    status_code=400,
                    detail=f"Card {card_id} referenced but not found",
                )

    # Check no orphaned cards
    all_card_ids = set()
    for column in board_data.columns:
        all_card_ids.update(column.cardIds)

    for card_id in board_data.cards.keys():
        if card_id not in all_card_ids:
            raise HTTPException(
                status_code=400, detail=f"Card {card_id} exists but not in any column"
            )

    # Save board
    board_dict = board_data.model_dump()
    save_board_state(user_id, board_dict)

    return board_dict


@router.post("/board/cards")
async def create_card(request: Request, body: dict):
    """Create new card."""
    user_id = get_current_user(request)

    # Validate input
    if not body.get("columnId"):
        raise HTTPException(status_code=400, detail="Missing columnId")
    if not body.get("title"):
        raise HTTPException(status_code=400, detail="Missing title")

    # Get current board
    board = get_board_state(user_id)

    # Find column
    column = next((c for c in board["columns"] if c["id"] == body["columnId"]), None)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")

    # Create card
    import uuid

    card_id = f"card-{uuid.uuid4()}"
    board["cards"][card_id] = {
        "id": card_id,
        "title": body["title"],
        "details": body.get("details", ""),
    }
    column["cardIds"].append(card_id)

    # Save board
    save_board_state(user_id, board)

    return {"cardId": card_id, **board}


@router.put("/board/cards/{card_id}")
async def update_card(request: Request, card_id: str, body: dict):
    """Update card."""
    user_id = get_current_user(request)

    # Get current board
    board = get_board_state(user_id)

    # Find card
    if card_id not in board["cards"]:
        raise HTTPException(status_code=404, detail="Card not found")

    # Update card
    if "title" in body:
        board["cards"][card_id]["title"] = body["title"]
    if "details" in body:
        board["cards"][card_id]["details"] = body["details"]

    # Save board
    save_board_state(user_id, board)

    return {"cardId": card_id, **board}


@router.delete("/board/cards/{card_id}")
async def delete_card(request: Request, card_id: str):
    """Delete card."""
    user_id = get_current_user(request)

    # Get current board
    board = get_board_state(user_id)

    # Find card
    if card_id not in board["cards"]:
        raise HTTPException(status_code=404, detail="Card not found")

    # Remove card from columns
    for column in board["columns"]:
        if card_id in column["cardIds"]:
            column["cardIds"].remove(card_id)

    # Remove card from cards
    del board["cards"][card_id]

    # Save board
    save_board_state(user_id, board)

    return board
