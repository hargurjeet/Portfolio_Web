#!/bin/bash
set -e

echo "[1/5] Starting Portfolio Chatbot..."
echo "Timestamp: $(date)"
echo "Working directory: $(pwd)"
echo "Files present: $(ls)"

# Build FAISS index if it does not exist
if [ ! -d "faiss_index" ] || [ -z "$(ls -A faiss_index 2>/dev/null)" ]; then
    echo "[2/5] Building FAISS index (this may take a few minutes on first run)..."
    python -u build_index.py
    echo "[2/5] FAISS index build complete"
else
    echo "[2/5] FAISS index already exists, skipping build"
fi

# Start FastAPI
echo "[3/5] Starting FastAPI on port 8000..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!
echo "[3/5] FastAPI process started with PID $FASTAPI_PID"

# Wait until FastAPI /health responds
echo "[4/5] Waiting for FastAPI to be ready..."
MAX_WAIT=180
WAITED=0
until curl -sf http://localhost:8000/health > /dev/null 2>&1; do
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo "ERROR: FastAPI did not become healthy within ${MAX_WAIT}s"
        echo "FastAPI logs above should show the error"
        kill $FASTAPI_PID 2>/dev/null
        exit 1
    fi
    echo "  ...waiting for FastAPI (${WAITED}s elapsed)"
    sleep 5
    WAITED=$((WAITED + 5))
done
echo "[4/5] FastAPI is ready after ${WAITED}s"

# Start Streamlit
echo "[5/5] Starting Streamlit on port 7860..."
streamlit run ui/streamlit_app.py \
    --server.port 7860 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false &
STREAMLIT_PID=$!
echo "[5/5] Streamlit process started with PID $STREAMLIT_PID"
echo "All services running. Waiting..."

# If either process dies, kill the other and exit
wait -n $FASTAPI_PID $STREAMLIT_PID
EXIT_CODE=$?
echo "A process exited with code $EXIT_CODE, shutting down..."
kill $FASTAPI_PID $STREAMLIT_PID 2>/dev/null
exit $EXIT_CODE