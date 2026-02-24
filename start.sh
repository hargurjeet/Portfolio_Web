#!/bin/bash
set -e

echo "Starting Portfolio Chatbot..."

# Build FAISS index if it does not exist
if [ ! -d "faiss_index" ] || [ -z "$(ls -A faiss_index 2>/dev/null)" ]; then
    echo "Building FAISS index..."
    python build_index.py
else
    echo "FAISS index already exists, skipping build"
fi

# Start FastAPI internally on port 8000
echo "Starting FastAPI..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# Wait for FastAPI to be ready
sleep 5

# Start Streamlit on port 7860 (only port HF Spaces exposes)
echo "Starting Streamlit..."
streamlit run ui/streamlit_app.py \
    --server.port 7860 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false &
STREAMLIT_PID=$!

# If either process dies, kill the other and exit
wait -n $FASTAPI_PID $STREAMLIT_PID
EXIT_CODE=$?
kill $FASTAPI_PID $STREAMLIT_PID 2>/dev/null
exit $EXIT_CODE