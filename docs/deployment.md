# Deployment

## HuggingFace Spaces (Active)

**Space**: `Hargurjeet/portfolio-chatbot`  
**URL**: https://huggingface.co/spaces/Hargurjeet/portfolio-chatbot  
**SDK**: Docker (`sdk: docker` in README frontmatter)  
**Exposed port**: 8501 (Streamlit) — only this port is accessible publicly

### How deployment works

HF Spaces rebuilds the Docker image automatically whenever you push to the `space` git remote:

```bash
git push space main
```

The `app_port: 8501` in the README YAML frontmatter tells HF Spaces which port to route public traffic to. FastAPI on port 8000 stays internal.

### Setting the API key

Set `FIREWORKS_API_KEY` as a Space secret — never commit it:

1. Go to the Space on huggingface.co
2. Settings → Variables and secrets → New secret
3. Name: `FIREWORKS_API_KEY`, Value: your key

### Viewing logs

Logs are available in the Space UI under the **Logs** tab (real-time build and runtime logs).

### Cold start behaviour

HF Spaces may suspend the container when idle. On resume:

1. FastAPI reloads the FAISS index and embedding model (~30–60 seconds)
2. Streamlit comes up quickly and shows "The AI backend is warming up" banner
3. Streamlit polls `localhost:8000/health` every second and reruns until the backend is ready
4. Chat becomes interactive once `/health` returns 200

The embedding model is baked into the Docker image (pre-downloaded during build), so it does not need to download on each cold start.

## Git Remotes

```
github  https://github.com/hargurjeet/Portfolio_Web.git
space   https://huggingface.co/spaces/Hargurjeet/portfolio-chatbot
```

Push to both independently as needed:

```bash
git push github main   # update GitHub
git push space main    # trigger HF Spaces rebuild
```

### Security note — HF token in remote URL

If the `space` remote URL contains an embedded HF token (visible via `git remote -v`), rotate the token and fix the remote:

```bash
# Remove the embedded token from the remote URL
git remote set-url space https://huggingface.co/spaces/Hargurjeet/portfolio-chatbot
```

When pushing, Git will prompt for credentials or use your stored HF token from `huggingface-cli login`.

## FAISS Index and Git LFS

The FAISS index files (`faiss_index/index.faiss`, `faiss_index/index.pkl`) are tracked via Git LFS.

```bash
# Pull LFS files after cloning
git lfs pull

# After rebuilding the index locally, commit and push as usual
git add faiss_index/
git commit -m "Rebuild FAISS index"
git push github main
git push space main   # triggers a redeploy with the new index
```

The Docker build includes the index via `COPY . .` — LFS files must be present locally before building.

## Dockerfile Notes

```dockerfile
FROM python:3.10-slim

# Embedding model pre-downloaded into image layer (~400 MB)
# Avoids downloading it on every cold start
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-mpnet-base-v2')"

EXPOSE 8000
EXPOSE 8501

CMD ["bash", "start.sh"]
```

`start.sh` launches FastAPI and Streamlit in parallel. The `wait -n; wait` pattern keeps the container running until either process exits.

## Local Docker Testing

```bash
# Build
docker build -t portfolio-web .

# Run (mirrors HF Spaces environment)
docker run -p 8501:8501 -e FIREWORKS_API_KEY=fw_your_key_here portfolio-web
```

Open http://localhost:8501.

Or with docker-compose (local dev only):
```bash
docker-compose up --build
```

Note: `docker-compose.yml` maps port 7860 to match HF Spaces' default port convention. The README frontmatter overrides this to 8501 — use whichever is consistent with your local testing.
