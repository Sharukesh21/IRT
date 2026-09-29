@echo off
setlocal

set ROOT=%~dp0
set BACKEND=%ROOT%backend
set FRONTEND=%ROOT%frontend

echo ===================================================
echo  Incident-to-Regression Capstone
echo ===================================================
echo.

echo [1/3] Freeing port 8000 if in use...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr "0.0.0.0:8000 127.0.0.1:8000" 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo [2/3] Starting Backend...
start "Backend - FastAPI :8000" cmd /k "cd /d "%BACKEND%" && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo [3/3] Starting Frontend...
start "Frontend - Vite :5173" cmd /k "cd /d "%FRONTEND%" && npm run dev"

timeout /t 3 /nobreak >nul

echo Opening browser...
start "" "http://localhost:5173"

echo.
echo ===================================================
echo  Backend  ->  http://localhost:8000
echo  Swagger  ->  http://localhost:8000/docs
echo  Frontend ->  http://localhost:5173
echo ===================================================
endlocal
