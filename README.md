# Bilingual Healthcare RAG Backend

A Retrieval-Augmented Generation (RAG) backend for answering clinical questions from medical guidelines, supporting both English and Japanese. Handles multilingual ingestion (.txt), chunking, vector search with sentence-transformers + FAISS, mock answer generation, translation, and API-key security. Built for modularity, CI/CD, and Dockerized deployment.

---

## Setup Instructions

**1. Clone the repo:**
```sh
git clone https://github.com/Tashin2098/bilingual-rag-fastapi.git
cd bilingual-rag-fastapi
```

**2. (Option 1) Run Locally:**
```sh
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```
Visit: http://localhost:8000/docs

**3. (Option 2) Run with Docker:**
```sh
docker build -t healthcare-rag-backend .
docker run -d -p 8000:8000 --name rag-app healthcare-rag-backend
```
Visit: http://localhost:8000/docs

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ingest` | POST | Upload .txt files (English or Japanese). Auto language detection, embedding generation, FAISS storage. |
| `/retrieve` | GET | Query in English or Japanese. Returns top-3 relevant text chunks with similarity scores. |
| `/generate` | GET | Combines best documents + query; returns synthesized answer. Supports `output_language` toggle (en/ja). |

**All endpoints require:** `X-API-Key: my_very_secret_key_123`

**Example API test:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "X-API-Key: my_very_secret_key_123" \
  -F "file=@yourfile.txt"
```

---

## Security

All endpoints require an API key in the header:
```
X-API-Key: my_very_secret_key_123
```

---

## Design Notes

### Scalability
The API is stateless (via FastAPI) and uses FAISS for efficient similarity search. This allows scaling by running multiple containers behind a load balancer or switching to distributed vector stores if data/traffic become very large. All endpoints are separated for flexible, independent scaling.

### Modularity
Each function—ingestion, retrieval, generation, translation, and security—is implemented as a separate component. This enables you to upgrade to a production LLM, use an alternate vector DB, add new languages, or change translation services without major code rewrites. Security can be upgraded from API Key to OAuth as needed.

### Future Improvements
- Integrate production LLM for richer answer generation (OpenAI, Claude, etc.)
- Support additional file types (PDF, DOCX) and more languages
- Add robust authentication (OAuth2, JWT), monitoring, and rate limiting
- Use cloud-native vector DB for cross-node queries at scale
- Implement caching and request batching for high-throughput scenarios

---

## CI/CD & Deployment

- **GitHub Actions:** `.github/workflows/ci.yml` runs tests and import checks on every commit.
- **Docker:** `Dockerfile` provides reproducible builds on any machine or cloud environment.

---

