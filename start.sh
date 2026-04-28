#!/bin/bash
echo "Starting FastAPI..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 &

echo "Waiting for FastAPI to be ready..."
elapsed=0
until curl -s http://localhost:8000/health > /dev/null 2>&1; do
    sleep 2
    elapsed=$((elapsed + 2))
    echo "  ...waiting (${elapsed}s)"
    if [ $elapsed -ge 120 ]; then
        echo "FastAPI did not start within 120s, continuing anyway..."
        break
    fi
done
echo "FastAPI is ready!"

echo "Starting Streamlit..."
streamlit run ui/streamlit_app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true