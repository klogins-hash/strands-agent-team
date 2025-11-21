# Strands Agent Team with Ultravox Voice Integration

A production-ready AI agent team that combines Strands Agents SDK with Ultravox voice capabilities. This system provides both text-based and voice-based interactions powered by OpenAI's GPT-4o-mini model.

## Features

- **Text Agent Backend**: FastAPI-based coordinator agent using Strands Agents SDK
- **Voice Integration**: Ultravox integration for voice conversational AI
- **Async Processing**: Full async/await support with httpx for inter-service communication
- **Docker Ready**: Containerized deployment with health checks
- **Security First**: API key management, environment variable handling, and .gitignore protection
- **Scalable Architecture**: Bridge networking for multi-container orchestration

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Ultravox Voice Service                    │
│                   (External API Service)                     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ Voice Calls & Stream
                             │
                ┌────────────▼────────────┐
                │  Voice Agent Gateway    │
                │  (Port 8003)            │
                │  - FastAPI              │
                │  - Ultravox Integration │
                │  - Query Forwarding     │
                └────────────┬────────────┘
                             │
                             │ HTTP POST /agent
                             │
                ┌────────────▼────────────┐
                │  Text Agent Backend     │
                │  (Port 8002)            │
                │  - FastAPI              │
                │  - Strands Agents SDK   │
                │  - GPT-4o-mini Model    │
                │  - Coordinator Agent    │
                └────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- OpenAI API Key
- Ultravox API Key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/strands-agent-team.git
cd strands-agent-team
```

2. Create a `.env` file from the example:
```bash
cp .env.example .env
```

3. Update `.env` with your API keys:
```env
OPENAI_API_KEY=sk-your-key-here
ULTRAVOX_API_KEY=your-ultravox-key-here
```

### Running with Docker

Build and run the services:

```bash
# Build the image
docker build -t strands-agent-team .

# Run text agent backend (port 8002)
docker run -d \
  --name strands-text-agent \
  -p 8002:8002 \
  --env-file .env \
  --network agent-bridge \
  strands-agent-team \
  python app.py

# Run voice agent gateway (port 8003)
docker run -d \
  --name strands-voice-agent \
  -p 8003:8003 \
  --env-file .env \
  --network agent-bridge \
  -e STRANDS_BACKEND_URL=http://strands-text-agent:8002 \
  strands-agent-team \
  python voice_agent.py
```

### Running Locally

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the text agent backend:
```bash
python app.py
```

4. In another terminal, run the voice agent:
```bash
python voice_agent.py
```

## API Endpoints

### Text Agent Backend (Port 8002)

#### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "service": "strands-agent-text-backend",
  "version": "1.0.0"
}
```

#### Process Query
```bash
POST /agent

Request Body:
{
  "query": "Help me organize my weekly tasks",
  "context": {}
}

Response:
{
  "response": "I can help organize your weekly tasks...",
  "status": "success"
}
```

#### Streaming Response
```bash
POST /agent-streaming

Request Body:
{
  "query": "What are the top 3 productivity tips?"
}

Response: Server-sent events stream of the agent's response
```

### Voice Agent Gateway (Port 8003)

#### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "service": "voice-agent-gateway",
  "version": "1.0.0"
}
```

#### Service Info
```bash
GET /info

Response:
{
  "service": "voice-agent-gateway",
  "backend_url": "http://10.0.0.3:8002",
  "voice_port": 8003,
  "ultravox_enabled": true
}
```

#### Send Voice Query
```bash
POST /query-agent

Request Body:
{
  "transcribed_text": "What should I do today?",
  "session_id": "session-123"
}

Response:
{
  "response": "Here's what you should focus on today...",
  "session_id": "session-123"
}
```

#### Create Voice Call
```bash
POST /create-call

Request Body (optional):
{
  "system_prompt": "Custom system prompt for this call"
}

Response:
{
  "call_id": "call-uuid",
  "join_url": "https://app.fixie.ai/join/...",
  "status": "created"
}
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini | - | ✓ |
| `ULTRAVOX_API_KEY` | Ultravox API key for voice service | - | ✓ |
| `PORT` | Text agent backend port | 8002 | ✗ |
| `VOICE_PORT` | Voice agent gateway port | 8003 | ✗ |
| `STRANDS_BACKEND_URL` | Backend URL for voice agent | http://10.0.0.3:8002 | ✗ |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, ERROR) | INFO | ✗ |

### System Prompt Customization

Edit the `coordinator_agent` initialization in `app.py` to customize the agent's behavior:

```python
coordinator_agent = Agent(
    name="Coordinator",
    system_prompt="Your custom system prompt here...",
    model=model,
)
```

## Docker Networking

When running multiple containers, use Bridge networking for inter-container communication:

```bash
# Create bridge network
docker network create agent-bridge

# Run services on the network
docker run --network agent-bridge ...
```

The text agent backend will be accessible at `http://strands-text-agent:8002` from other containers.

## Testing

### Test Text Agent Locally

```bash
curl -X POST http://localhost:8002/agent \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I prioritize my tasks?"}'
```

### Test Voice Agent Locally

```bash
curl -X POST http://localhost:8003/query-agent \
  -H "Content-Type: application/json" \
  -d '{"transcribed_text": "What time is the meeting?", "session_id": "test-123"}'
```

### Create Voice Call

```bash
curl -X POST http://localhost:8003/create-call \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Security

### Best Practices

1. **Never commit `.env` files** - Use `.env.example` as a template
2. **Validate all inputs** - The API uses Pydantic for request validation
3. **Use HTTPS in production** - Configure reverse proxy (nginx/traefik)
4. **Rate limiting** - Implement rate limiting for production deployments
5. **API key rotation** - Rotate API keys regularly
6. **Non-root containers** - Runs as `appuser` (UID 1000) by default

### Secrets Management

For production deployments, consider:
- AWS Secrets Manager
- HashiCorp Vault
- Kubernetes Secrets
- Azure Key Vault
- Environment-based configuration management

## Deployment

### Cloud Deployment Options

#### AWS ECS
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [account-id].dkr.ecr.us-east-1.amazonaws.com
docker tag strands-agent-team [account-id].dkr.ecr.us-east-1.amazonaws.com/strands-agent-team:latest
docker push [account-id].dkr.ecr.us-east-1.amazonaws.com/strands-agent-team:latest
```

#### Docker Hub
```bash
docker build -t yourusername/strands-agent-team:latest .
docker push yourusername/strands-agent-team:latest
```

#### Kubernetes
See `kubernetes/deployment.yaml` for example manifests (if provided).

## Troubleshooting

### Backend Connection Issues

If the voice agent can't reach the text backend:

1. Check container networking:
```bash
docker network ls
docker network inspect agent-bridge
```

2. Verify STRANDS_BACKEND_URL environment variable
3. Check logs:
```bash
docker logs strands-text-agent
docker logs strands-voice-agent
```

### API Key Errors

- **401 Unauthorized**: Verify API keys are correct in `.env`
- **Invalid API Key**: Check key format (OpenAI starts with `sk-`, Ultravox is alphanumeric)
- **Quota Exceeded**: Check API usage in respective dashboards

### Port Conflicts

If ports 8002/8003 are in use:
- Modify PORT and VOICE_PORT environment variables
- Or kill existing processes: `lsof -ti :8002 | xargs kill -9`

## Performance Considerations

- **Streaming responses**: Use `/agent-streaming` for large responses to reduce latency
- **Connection pooling**: httpx automatically manages connection pools
- **Timeout settings**: Configured to 30 seconds for backend calls
- **Health checks**: Built-in health endpoints for monitoring

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation in this README
- Review logs in `/var/log/strands-agent-team/` (if deployed to server)

## Roadmap

- [ ] Multi-agent coordination patterns
- [ ] Custom tool integration framework
- [ ] Advanced memory management
- [ ] Rate limiting middleware
- [ ] Prometheus metrics export
- [ ] OpenTelemetry tracing support
- [ ] Web dashboard for monitoring

## Acknowledgments

Built with:
- [Strands Agents SDK](https://github.com/strands-ai/agents)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Ultravox](https://www.fixie.ai/ultravox)
- [OpenAI GPT-4o-mini](https://openai.com/)
