# Vargas — Local Development Setup

## Prerequisites

- **Python 3.11+**
- **Docker Desktop** (for Qdrant vector database)
- **Discord Bot Token** (from [Discord Developer Portal](https://discord.com/developers/applications))
- **Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/apikey))

## 1. Start Qdrant

Vargas uses Qdrant as its vector memory backend. Run it locally via Docker:

```bash
docker pull qdrant/qdrant
docker run -d --name vargas-qdrant -p 6333:6333 qdrant/qdrant
```

Verify it's running:

```bash
curl http://localhost:6333/collections
```

You should see `{"result":{"collections":[]},...}` on a fresh install.

## 2. Configure Environment

```bash
cd project_vargas
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | Required | Source |
|----------|----------|--------|
| `DISCORD_TOKEN` | Yes | Discord Developer Portal |
| `GEMINI_API_KEY` | Yes | Google AI Studio |
| `GOOGLE_CSE_API_KEY` | Optional | Google Custom Search (for web search) |
| `GOOGLE_CSE_ID` | Optional | Google Custom Search Engine ID |
| `QDRANT_HOST` | No | Defaults to `localhost` |
| `QDRANT_PORT` | No | Defaults to `6333` |
| `OPENAI_API_KEY` | Optional | For voice transcription (Whisper) |

## 3. Install Dependencies

```bash
pip install -r project_vargas/requirements.txt
```

## 4. Run Vargas

```bash
python -m project_vargas.discord.bot
```

Vargas will connect to Discord and log in. You should see:

```
Vargas online: {'agent': 'vargas', 'version': '2.0', 'status': 'online', ...}
```

## 5. Quick Health Check

If Qdrant is not running when Vargas starts, you'll see:

```
[MEMORY] Qdrant not reachable at localhost:6333 — start with: docker run -d -p 6333:6333 qdrant/qdrant
[MEMORY] Using in-memory fallback (memories will not persist across restarts)
```

Vargas will still work with in-memory fallback, but memories won't survive restarts.

## Cloud Qdrant (Optional)

For cloud deployment, set `qdrant_url` and `qdrant_api_key` in `config/vargas_config.json`:

```json
{
  "qdrant_url": "https://your-cluster.qdrant.io:6333",
  "qdrant_api_key": "your-api-key"
}
```
