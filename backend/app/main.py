"""Main FastAPI application."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.routes import health, auth, board, ai
from app.db import initialize_database

# Initialize database
initialize_database()

app = FastAPI(title="Kanban API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(board.router, prefix="/api", tags=["board"])
app.include_router(ai.router, prefix="/api", tags=["ai"])

# Mount Next.js static assets (_next directory)
next_static_path = os.path.join(os.path.dirname(__file__), "..", "out", "_next")
if os.path.exists(next_static_path):
    app.mount("/_next", StaticFiles(directory=next_static_path), name="static")

# Mount public directory
public_path = os.path.join(os.path.dirname(__file__), "..", "public")
if os.path.exists(public_path):
    app.mount("/public", StaticFiles(directory=public_path), name="public")

# Get index.html path
index_html_path = os.path.join(os.path.dirname(__file__), "..", "out", "index.html")

# Serve frontend HTML for SPA routing
@app.get("/")
async def serve_index():
    """Serve index.html for root path."""
    if os.path.exists(index_html_path):
        return FileResponse(index_html_path, media_type="text/html")
    return {
        "message": "Kanban App - API available at /api/health",
        "frontend": "Frontend build not found - ensure 'npm run build' was executed in frontend/"
    }

@app.get("/{path:path}")
async def serve_spa(path: str):
    """Serve SPA routes - try to find the file, otherwise serve index.html."""
    if path.startswith("api/"):
        # Let API routes through (handled by routers)
        raise HTTPException(status_code=404)
    
    # Try to serve static file from out directory
    file_path = os.path.join(os.path.dirname(__file__), "..", "out", path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Try public directory
    file_path = os.path.join(os.path.dirname(__file__), "..", "public", path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Fallback to index.html for SPA routing
    if os.path.exists(index_html_path):
        return FileResponse(index_html_path, media_type="text/html")
    
    raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
