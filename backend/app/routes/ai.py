"""AI routes."""
from fastapi import APIRouter, HTTPException, Request
from app.models import AITestRequest, AITestResponse, AIAskRequest, AIResponse
from app.routes.auth import verify_jwt_token

router = APIRouter()


@router.post("/ai/test")
async def test_ai(request: AITestRequest):
    """Test AI connectivity."""
    import os
    from openai import OpenAI

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenRouter API key not configured",
        )

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.io/api/v1",
        )

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": request.question}],
            max_tokens=100,
        )

        return AITestResponse(response=response.choices[0].message.content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@router.post("/ai/ask")
async def ask_ai(req: Request, request: AIAskRequest):
    """Ask AI for help with board updates."""
    # Get current user
    token = req.cookies.get("auth_token")
    if not token and "authorization" in req.headers:
        auth_header = req.headers["authorization"]
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    from app.routes.auth import verify_jwt_token

    payload = verify_jwt_token(token)
    user_id = payload["user_id"]

    import os
    from openai import OpenAI
    import json

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenRouter API key not configured",
        )

    # Format conversation history for AI
    messages = []

    # Add conversation history
    for msg in request.conversationHistory:
        messages.append({"role": msg.role, "content": msg.content})

    # Prepare board context
    board_context = f"""
Current Kanban Board State:
Columns: {[c.title for c in request.boardState.columns]}
Cards: {len(request.boardState.cards)} total

User's Question: {request.userQuestion}

Please respond with a JSON object containing:
1. "message": Your response to the user
2. "boardUpdates" (optional): Object with "columns", "cards", and/or "deletedCardIds" if you want to update the board

If no board changes needed, set "boardUpdates" to null.
"""

    messages.append({"role": "user", "content": board_context})

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.io/api/v1",
        )

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            max_tokens=1000,
        )

        ai_response_text = response.choices[0].message.content

        # Try to parse JSON response
        try:
            # Find JSON in response
            import re

            json_match = re.search(r"\{.*\}", ai_response_text, re.DOTALL)
            if json_match:
                ai_response = json.loads(json_match.group())
            else:
                ai_response = {"message": ai_response_text, "boardUpdates": None}
        except json.JSONDecodeError:
            ai_response = {"message": ai_response_text, "boardUpdates": None}

        # Save conversation to history
        from app.db import save_conversation_message

        save_conversation_message(user_id, "user", request.userQuestion)
        save_conversation_message(user_id, "assistant", ai_response.get("message", ""))

        # If board updates included, validate and save
        if ai_response.get("boardUpdates"):
            from app.db import save_board_state

            try:
                # Validate board structure
                board_dict = request.boardState.model_dump()
                if ai_response["boardUpdates"].get("columns"):
                    board_dict["columns"] = ai_response["boardUpdates"]["columns"]
                if ai_response["boardUpdates"].get("cards"):
                    board_dict["cards"] = ai_response["boardUpdates"]["cards"]

                # Basic validation
                if len(board_dict["columns"]) != 5:
                    ai_response["boardUpdates"] = None
                else:
                    save_board_state(user_id, board_dict)

            except Exception as e:
                # If validation fails, don't update board
                ai_response["boardUpdates"] = None

        return AIResponse(**ai_response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
