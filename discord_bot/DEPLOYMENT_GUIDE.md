# CONEXUS Discord Bot Deployment Guide

Complete guide for deploying the CONEXUS Discord bot with sovereign AI integration.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Windows 10/11 (for this deployment)
- Internet connection for Discord API
- Local admin rights for service installation

### Required Services
- **CONEXUS Gateway**: Running on localhost:8000
- **Qdrant Database**: Running on localhost:6333
- **Discord Bot Token**: From Discord Developer Portal

## Step-by-Step Deployment

### 1. Install Dependencies

```bash
# Navigate to Discord bot directory
cd C:\Users\Derek Angell\Desktop\CONEXUS_REPO\discord_bot

# Install Python packages
pip install -r requirements.txt
```

### 2. Configure Discord Bot

#### Create Discord Bot
1. Go to Discord Developer Portal: https://discord.com/developers/applications
2. Click "New Application" → Name it "CONEXUS-CLAW"
3. Go to "Bot" section → Click "Add Bot"
4. Copy the bot token

#### Bot Permissions
Enable these Privileged Gateway Intents:
- ✅ Message Content Intent
- ✅ Server Members Intent

#### OAuth2 URL Generator
1. Go to "OAuth2" → "URL Generator"
2. Select scopes: `bot`
3. Select permissions:
   - Send Messages
   - Read Message History
   - Embed Links
   - Use External Emojis
4. Copy the generated URL and invite bot to server

### 3. Configure Environment

```bash
# Edit .env file
DISCORD_TOKEN=your_actual_discord_token_here
GATEWAY_URL=http://localhost:8000
QDRANT_URL=http://localhost:6333
```

### 4. Start CONEXUS Services

#### Start Qdrant Database
```bash
# Option 1: Using Docker (recommended)
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest

# Option 2: Using installed binary
qdrant --service-mode

# Option 3: Using Windows Service
# Install Qdrant as Windows service for automatic startup
```

#### Start CONEXUS Gateway
```bash
# Open new terminal
cd C:\Users\Derek Angell\Desktop\CONEXUS_REPO\golden-path\verification
python minimal-gateway.py
```

### 5. Test Integration

```bash
# Run integration test
python test_integration.py
```

Expected output:
```
🎉 All tests passed! Discord bot ready for deployment.
```

### 6. Start Discord Bot

#### Method 1: Using Startup Script
```bash
python start_bot.py
```

#### Method 2: Direct Execution
```bash
python bot.py
```

### 7. Verify Deployment

Test these commands in Discord:

```
!ping
!status
!help_conexus
!conexus hello world
```

## Service Management

### Automatic Startup (Windows)

#### Create Batch File
Create `start_conexus.bat`:
```batch
@echo off
echo Starting CONEXUS Services...

echo Starting Qdrant...
start "Qdrant" cmd /c "qdrant --service-mode"

echo Waiting for Qdrant to start...
timeout /t 10 /nobreak

echo Starting CONEXUS Gateway...
start "Gateway" cmd /c "cd C:\Users\Derek Angell\Desktop\CONEXUS_REPO\golden-path\verification && python minimal-gateway.py"

echo Waiting for Gateway to start...
timeout /t 5 /nobreak

echo Starting Discord Bot...
cd C:\Users\Derek Angell\Desktop\CONEXUS_REPO\discord_bot
python start_bot.py

pause
```

#### Windows Service (Advanced)
Use NSSM (Non-Sucking Service Manager) to create Windows services:
```bash
# Install NSSM
# Download from https://nssm.cc/download

# Create Qdrant service
nssm install Qdrant "qdrant" "--service-mode"

# Create Gateway service
nssm install CONEXUSGateway "python" "C:\Users\Derek Angell\Desktop\CONEXUS_REPO\golden-path\verification\minimal-gateway.py"

# Create Discord Bot service
nssm install CONEXUSBot "python" "C:\Users\Derek Angell\Desktop\CONEXUS_REPO\discord_bot\start_bot.py"
```

## Troubleshooting

### Common Issues

#### Bot Won't Start
**Symptoms**: Error loading Discord token or connection failed
**Solutions**:
1. Verify Discord token in .env file
2. Check bot permissions in Discord Developer Portal
3. Ensure bot is invited to server with proper permissions

#### Gateway Connection Failed
**Symptoms**: "❌ Gateway connection failed" in startup
**Solutions**:
1. Start Gateway service first
2. Check if port 8000 is available
3. Verify Gateway is running: `curl http://localhost:8000/health`

#### Qdrant Connection Failed
**Symptoms**: "❌ Qdrant connection failed"
**Solutions**:
1. Start Qdrant service
2. Check if port 6333 is available
3. Verify Qdrant is running: `curl http://localhost:6333/collections/conexus_lineage`

#### Commands Not Responding
**Symptoms**: Bot online but commands don't work
**Solutions**:
1. Check Gateway status with `!status`
2. Verify agent assignment in task submission
3. Check Discord bot permissions

### Debug Mode

Enable debug logging:
```bash
# Set debug environment variable
set DEBUG=true

# Start bot with debug
python start_bot.py
```

### Log Files

Check these log locations:
- Gateway logs: Console output from minimal-gateway.py
- Discord bot logs: Console output from start_bot.py
- Qdrant logs: Qdrant service logs

## Security Considerations

### Token Security
- Never commit Discord token to version control
- Use environment variables for sensitive data
- Rotate tokens regularly
- Limit bot permissions to minimum required

### Network Security
- Services run on localhost (not exposed to internet)
- Discord API communication uses HTTPS
- No external database connections required

### Human Authority
- All strategic decisions require human approval
- Agent execution bounded by governance constraints
- Complete audit trail with provenance tracking

## Performance Optimization

### Response Time
- Gateway responses: <100ms
- Discord bot responses: <5 seconds
- Memory operations: <10ms

### Resource Usage
- Memory usage: ~100MB for all services
- CPU usage: <5% during normal operation
- Network bandwidth: Minimal (local communication)

### Scaling Considerations
- Multiple Discord servers supported
- Concurrent command handling
- Rate limiting to prevent abuse
- Error recovery and retry logic

## Monitoring

### Health Checks
- Gateway health: `!status` command
- Database status: Memory vector count
- Bot uptime: Discord connection status

### Metrics to Monitor
- Command response times
- Error rates and types
- Memory vector growth
- User engagement levels

## Maintenance

### Regular Tasks
- Update Discord bot token quarterly
- Monitor memory vector storage growth
- Backup Qdrant data periodically
- Update dependencies monthly

### Updates
- Update Discord.py library regularly
- Update Gateway service with new features
- Add new commands based on user feedback
- Maintain documentation

---

## Deployment Summary

When deployed correctly, you'll have:
- ✅ Discord bot responding to commands
- ✅ CONEXUS Gateway processing tasks
- ✅ Qdrant storing memory vectors
- ✅ Complete sovereign AI system operational
- ✅ Public interface for CONEXUS capabilities

The system will be ready for:
- Public demonstration of sovereign AI
- Community engagement and education
- Market validation and feedback
- Real-world usage testing

---

**CONEXUS Discord Bot Deployment** - Complete sovereign AI system with public interface  
*Human-Directed • Autonomous Execution • Guaranteed Control*
