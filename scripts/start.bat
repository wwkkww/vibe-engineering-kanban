@echo off
REM Start the Kanban app (Windows)

setlocal enabledelayedexpansion

echo Starting Kanban App...

REM Build frontend
echo Building frontend...
cd frontend
call npm run build
cd ..

REM Start Docker
echo Starting Docker container...
docker-compose up --build

endlocal
