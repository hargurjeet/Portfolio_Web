#!/bin/bash
set -e

echo "[1/6] Starting Portfolio Chatbot..."
echo "Timestamp: $(date)"

# Start a tiny placeholder on port 7860 immediately so HF Spaces health check passes
echo "[2/6] Starting placeholder on port 7860 to satisfy HF health check..."
python -c "
import http.server, threading, os, signal

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Starting...')
    def log_message(self, *a): pass

srv = http.server.HTTPServer(('0.0.0.0', 7860), H)
t = threading.Thread(target=srv.serve_forever)
t.daemon = True
t.start()
print('Placeholder running on 7860', flush=True)

# Write PID so we can kill it later
with open('/tmp/placeholder.pid', 'w') as f:
    f.write(str(os.getpid()))

import time
# Keep alive until signalled
while not os.path.exists('/tmp/placeholder_stop'):
    time.sleep(1)

srv.shutdown()
print('Placeholder stopped', flush=True)
" &
PLACEHOLDER_PID=$!
echo "[2/6] Placeholder PID: $PLACEHOLDER_PID"

# Build FAISS index if needed
if [ ! -d "faiss_index" ] || [ -z "$(ls -A faiss_index 2>/dev/null)" ]; then
    echo "[3/6] Building FAISS index..."
    python -u build_index.py
else
    echo "[3/6] FAISS index already exists, skipping"
fi

# Start FastAPI on port 8000
echo "[4/6] Starting FastAPI..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# Wait for FastAPI to be healthy
echo "[5/6] Waiting for FastAPI..."
MAX_WAIT=180
WAITED=0
until curl -sf http://localhost:8000/health > /dev/null 2>&1; do
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo "ERROR: FastAPI not ready after ${MAX_WAIT}s"
        kill $FASTAPI_PID $PLACEHOLDER_PID 2>/dev/null
        exit 1
    fi
    echo "  ...waiting (${WAITED}s)"
    sleep 5
    WAITED=$((WAITED + 5))
done
echo "[5/6] FastAPI ready after ${WAITED}s"

# Stop the placeholder and start Streamlit on port 7860
echo "[6/6] Stopping placeholder, starting Streamlit..."
touch /tmp/placeholder_stop
sleep 2
kill $PLACEHOLDER_PID 2>/dev/null || true
sleep 1

streamlit run ui/streamlit_app.py \
    --server.port 7860 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false &
STREAMLIT_PID=$!
echo "[6/6] Streamlit PID: $STREAMLIT_PID"
echo "All services running!"

wait -n $FASTAPI_PID $STREAMLIT_PID
EXIT_CODE=$?
kill $FASTAPI_PID $STREAMLIT_PID 2>/dev/null
exit $EXIT_CODE