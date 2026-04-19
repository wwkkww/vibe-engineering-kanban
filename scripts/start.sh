#!/bin/bash
# Start the Kanban app (Mac/Linux)

set -e

echo "Starting Kanban App..."

# Build frontend
echo "Building frontend..."
cd frontend
npm run build
cd ..

# Start Docker
echo "Starting Docker container..."
docker-compose up --build
