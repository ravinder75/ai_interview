#!/bin/bash

# ============================================================
#  AI Interview Platform — run.sh
#  Starts Backend (FastAPI) and Frontend (Vite) servers
# ============================================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

BACKEND_PORT=8005
FRONTEND_PORT=3000

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   🎯 AI Interview Platform — Starting...     ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# Kill any existing processes on these ports
echo -e "${YELLOW}⏳ Clearing ports $BACKEND_PORT and $FRONTEND_PORT...${NC}"
fuser -k -9 $BACKEND_PORT/tcp 2>/dev/null || true
fuser -k -9 $FRONTEND_PORT/tcp 2>/dev/null || true
sleep 1

# ---- Backend ----
echo -e "${GREEN}🚀 Starting Backend (FastAPI) on port $BACKEND_PORT...${NC}"

if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${YELLOW}   Creating Python virtual environment...${NC}"
    python3 -m venv "$BACKEND_DIR/venv"
    "$BACKEND_DIR/venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt" -q
fi

cd "$BACKEND_DIR"
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT &
BACKEND_PID=$!
echo -e "${GREEN}   ✅ Backend PID: $BACKEND_PID${NC}"

# ---- Frontend ----
echo -e "${GREEN}🚀 Starting Frontend (Vite) on port $FRONTEND_PORT...${NC}"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${YELLOW}   Installing npm dependencies...${NC}"
    cd "$FRONTEND_DIR"
    npm install -q
fi

cd "$FRONTEND_DIR"
npm run dev -- --port $FRONTEND_PORT &
FRONTEND_PID=$!
echo -e "${GREEN}   ✅ Frontend PID: $FRONTEND_PID${NC}"

echo ""
echo -e "${CYAN}══════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Backend  → http://localhost:$BACKEND_PORT${NC}"
echo -e "${GREEN}   Frontend → http://localhost:$FRONTEND_PORT${NC}"
echo -e "${CYAN}══════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"

# Trap Ctrl+C to kill both processes
cleanup() {
    echo ""
    echo -e "${RED}🛑 Stopping servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    fuser -k -9 $BACKEND_PORT/tcp 2>/dev/null || true
    fuser -k -9 $FRONTEND_PORT/tcp 2>/dev/null || true
    echo -e "${GREEN}✅ All servers stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
