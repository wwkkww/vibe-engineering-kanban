FROM python:3.12-slim

WORKDIR /app

# Install uv package manager
RUN pip install uv

# Copy backend requirements
COPY backend/pyproject.toml backend/uv.lock* ./

# Install dependencies with uv
RUN uv sync --frozen

# Copy backend source
COPY backend/app ./app

# Copy frontend static export (built before Docker build)
COPY frontend/out ./out
COPY frontend/public ./public

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uv", "run", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
