# Project Vargas V4

A sovereign AI collaborator with Emotional Calibration Protocol (ECP) architecture.

## Overview

Vargas V4 represents the transition from V3 prototype to sovereign architecture, integrating:

- **ECP (Emotional Calibration Protocol)**: Advanced paradox processing and tension management
- **All V3 Capabilities**: Discord interface, multi-model LLM, tool execution, memory systems
- **Sovereign Architecture**: Self-calibrating, contradiction-embracing design

## Architecture

```
Discord Message → Intent Classification → Memory Context → 
ECP Tripwire Check → LLM Generation → ECP Interceptor → 
Memory Write → Discord Response
```

## Key Components

### ECP System
- **ECP Substrate**: Vector math for tension gradients
- **Forgetting Engine**: Consensus=DELETE logic
- **Model Bridge**: Dual-vector interceptor
- **Memory Compression**: Tension-preserving compression
- **Recursive Reinjection**: Autonomous paradox cycles

### V3 Foundation (Preserved)
- Discord bot with conversational interface
- Multi-model Gemini LLM integration with fallback
- Qdrant vector memory (identity, behavioral, attunement)
- Tool execution system (browser, shell, file I/O)
- OpenClaw skill integration (99 skills)
- Voice transcription (Whisper)
- Sovereign governance bridge

## Setup

1. Copy `.env.example` to `.env` and fill in your tokens
2. Install dependencies: `pip install -r requirements.txt`
3. Start Qdrant (Docker): `docker run -p 6333:6333 qdrant/qdrant`
4. Run the bot: `python -m project_vargas_v4.discord.bot`

## Configuration

See `config/vargas_config.json` for all settings including:
- Model configuration (primary, fallback, lightweight)
- ECP parameters (thresholds, compression settings)
- Memory system settings
- Discord integration options

## Development

V4 maintains full backward compatibility with V3 while adding ECP capabilities. All V3 features work without regression.

## Deployment

Ready for cloud deployment via Docker + Render. See `Dockerfile` and `render.yaml`.

## Version History

- **V4**: Sovereign architecture with ECP integration
- **V3**: Multi-model, context management, voice input
- **V2**: Browser automation, shell execution, file I/O
- **V1**: Core conversation, memory, web search, OpenClaw skills
