# CONEXUS Discord Bot

The public Discord interface for the CONEXUS sovereign AI system - the world's first sovereign artificial intelligence with guaranteed human supremacy.

## Features

- **Real-time Interaction**: Live sovereign AI responses through Discord
- **Strategic Analysis**: Market insights and business intelligence
- **Content Creation**: Narrative generation and strategic storytelling
- **System Monitoring**: Health checks and status updates
- **Memory Integration**: All interactions stored in persistent memory

## Commands

### Basic Commands
- `!ping` - Test bot connectivity
- `!help_conexus` - Show CONEXUS command help

### System Commands
- `!status` - Check CONEXUS system health and memory vector count
- `!conexus <query>` - Main interaction with sovereign AI

### Specialized Commands
- `!analyze <topic>` - Strategic analysis and market insights
- `!narrative <topic>` - Strategic storytelling and content creation

## Setup

### Prerequisites
- Python 3.8+
- CONEXUS Gateway service running on localhost:8000
- Qdrant database running on localhost:6333
- Discord bot token

### Installation

1. **Install Dependencies**
   ```bash
   cd C:\Users\Derek Angell\Desktop\CONEXUS_REPO\discord_bot
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Edit .env file
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

3. **Start CONEXUS Services**
   ```bash
   # Start Gateway (in separate terminal)
   cd C:\Users\Derek Angell\Desktop\CONEXUS_REPO\golden-path\verification
   python minimal-gateway.py
   
   # Start Qdrant (if not running)
   qdrant
   ```

4. **Start Discord Bot**
   ```bash
   cd C:\Users\Derek Angell\Desktop\CONEXUS_REPO\discord_bot
   python start_bot.py
   ```

## Usage Examples

### System Status
```
!status
```
Shows CONEXUS system health, Gateway status, and memory vector count.

### Strategic Analysis
```
!analyze sovereign AI market opportunity
```
Provides strategic analysis of sovereign AI market potential.

### Content Creation
```
!narrative the future of human-AI partnership
```
Creates strategic narrative about human-AI collaboration.

### General Interaction
```
!conexus what makes sovereign AI different from regular AI?
```
General interaction with CONEXUS sovereign AI system.

## Architecture

```
Discord User → Discord Command → Discord Bot → Gateway API → Agent Execution → Qdrant Storage → Discord Response
```

### Components
- **Discord Bot**: Public interface for CONEXUS interaction
- **Gateway API**: HTTP service for task submission and results
- **Agent System**: Sway (Collapse Agent) for task execution
- **Qdrant Database**: Persistent memory storage with provenance
- **Human Authority**: Derek Angell as Principal Orchestrator

## Security

- **Human Supremacy**: All strategic decisions require human approval
- **Bounded Autonomy**: Agents execute within defined parameters
- **Memory Tracking**: All interactions stored with complete provenance
- **Rate Limiting**: Prevents abuse and ensures system stability

## Troubleshooting

### Common Issues

**Bot won't start**
- Check Discord token in .env file
- Ensure dependencies are installed
- Verify CONEXUS Gateway is running

**Commands not working**
- Check Gateway connection with `!status`
- Verify Qdrant database is running
- Check bot permissions in Discord

**No response from CONEXUS**
- Gateway service may be down
- Agent execution may be delayed
- Check system logs for errors

### Health Checks

The bot automatically checks:
- Gateway connectivity on startup
- Qdrant database status
- System health and memory vector count

## Development

### Adding New Commands

1. Create command function in `bot.py`
2. Add error handling and validation
3. Update help documentation
4. Test with CONEXUS system

### Integration Testing

Test integration with:
- CONEXUS Gateway API
- Qdrant database operations
- Agent task execution
- Memory storage and retrieval

## Support

For technical support:
1. Check system status with `!status`
2. Verify all services are running
3. Review error messages and logs
4. Consult CONEXUS documentation

---

**CONEXUS Discord Bot** - Public interface for the world's first sovereign AI system  
*Human-Directed • Autonomous Execution • Guaranteed Control*
