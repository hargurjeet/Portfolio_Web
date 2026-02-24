# Run this from your portfolio_website/ folder
cat > start.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting Portfolio Chatbot..."

if [ ! -d "faiss_index" ] || [ -z "$(ls -A faiss_index)" ]; then
    echo "📚 Building FAISS index..."
    python -c "
from core.loader import load_documents
from core.splitter import split_documents
from core.vector_store import create_vector_store
from config import DOCS_PATH, INDEX_PATH
docs = load_documents(DOCS_PATH)
chunks = split_documents(docs)
create_vector_store(chunks, INDEX_PATH)
print('Index built successfully')
"
fi

uvicorn api.main:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!
sleep 5

streamlit run ui/streamlit_app.py \
    --server.port 7860 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false &
STREAMLIT_PID=$!

wait -n $FASTAPI_PID $STREAMLIT_PID
EXIT_CODE=$?
kill $FASTAPI_PID $STREAMLIT_PID 2>/dev/null
exit $EXIT_CODE
EOF

chmod +x start.sh