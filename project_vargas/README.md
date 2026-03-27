# Project Vargas

A personal collaborator AI designed for long-arc thinking, continuity, and reflective presence.

Vargas is not a church system, not public-facing, and not pastoral. He is a sovereign, private, experimental companion that challenges when integrity requires it.

## Stack

- **Model**: Gemini 3.1 Pro (via `google-genai`)
- **Interface**: Discord (pure natural language — no commands)
- **Memory**: Qdrant vector database (identity + behavioral + attunement)
- **Calibration**: Emoji vectors as latent substrate
- **Skills**: OpenClaw semantic skill matching
- **Web**: Google Custom Search API

## Setup

1. Copy `.env.example` to `.env` and fill in your tokens
2. Install dependencies: `pip install -r requirements.txt`
3. Start Qdrant (Docker): `docker run -p 6333:6333 qdrant/qdrant`
4. Run the bot: `python -m project_vargas.discord.bot`

## Architecture

All interaction is conversational. Vargas infers intent from natural language and autonomously decides when to:
- Respond conversationally
- Challenge or reframe
- Inspect or modify memory
- Search the web
- Invoke OpenClaw skills

Tool use is invisible to the user.
