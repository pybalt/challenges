# Scalable Computer Use Agent Backend

A production-ready, scalable backend for the Computer Use Agent with session management, real-time communication, and container orchestration.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │────│  FastAPI Backend │────│   PostgreSQL    │
│  (HTML/JS/WS)   │    │   (Session Mgmt) │    │   (Chat History) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌────────┼────────┐
                       │                 │
            ┌─────────────────┐ ┌─────────────────┐
            │ Docker Container│ │     Redis       │
            │  (VNC + Agent)  │ │ (Session State) │
            └─────────────────┘ └─────────────────┘
```

## 🚀 Features

- **Multi-Session Support**: Handle multiple concurrent agent sessions
- **Real-time Communication**: WebSocket-based chat with live agent responses
- **VNC Integration**: Direct access to agent desktop environments
- **Persistent Storage**: PostgreSQL for chat history and session metadata
- **Container Orchestration**: Dynamic Docker container management
- **Session Management**: Create, monitor, and clean up agent sessions
- **Scalable Architecture**: Redis for session state, async FastAPI for performance
- **Production Ready**: Docker Compose setup with monitoring and reverse proxy

## 📋 Requirements

- Docker and Docker Compose
- Python 3.11+ (for development)
- Anthropic API key
- 4GB+ RAM (for running multiple agent containers)
- Available ports: 5900-6100 (VNC), 8000 (API), 5432 (PostgreSQL), 6379 (Redis)

## 🛠️ Quick Start

1. **Clone and Setup**
   ```bash
   cd computer-agent/scalable-backend
   cp env.example .env
   ```

2. **Configure Environment**
   Edit `.env` file with your settings:
   ```bash
   ANTHROPIC_API_KEY=your_api_key_here
   API_PROVIDER=anthropic
   ```

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

4. **Access Interface**
   Open http://localhost:8000/static/index.html

## 📖 API Documentation

Once running, visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Frontend**: http://localhost:8000/static/index.html

### Core Endpoints

#### Session Management
- `POST /api/v1/sessions/` - Create new session
- `GET /api/v1/sessions/` - List sessions
- `GET /api/v1/sessions/{id}` - Get session details
- `DELETE /api/v1/sessions/{id}` - End session

#### Chat Management
- `POST /api/v1/sessions/{id}/messages` - Send message
- `GET /api/v1/sessions/{id}/messages` - Get chat history
- `GET /api/v1/sessions/{id}/messages/export` - Export chat

#### WebSocket
- `WS /ws/{session_id}` - Real-time communication

## 🔧 Configuration

### API Providers

**Anthropic (Default)**
```bash
API_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
```

**AWS Bedrock**
```bash
API_PROVIDER=bedrock
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-west-2
```

**Google Cloud Vertex**
```bash
API_PROVIDER=vertex
CLOUD_ML_REGION=your_region
ANTHROPIC_VERTEX_PROJECT_ID=your_project
```

### Container Resources
```bash
CONTAINER_MEMORY_LIMIT=2g
CONTAINER_CPU_COUNT=2
```

### Database
```bash
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/computer_use_db
SQL_DEBUG=false
```

## 🐳 Docker Compose Services

### Core Services
- **backend**: FastAPI application server
- **postgres**: PostgreSQL database for persistence
- **redis**: Redis for session state and caching

### Optional Services (Profiles)
- **monitoring**: Prometheus + Grafana for metrics
- **production**: Nginx reverse proxy

Start with monitoring:
```bash
docker-compose --profile monitoring up -d
```

Start with production setup:
```bash
docker-compose --profile production up -d
```

## 📊 Monitoring

Access monitoring tools:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

## 🔒 Security Considerations

### Development
- Use strong passwords for database
- Restrict API access with authentication
- Use HTTPS in production

### Production
- Enable authentication/authorization
- Use secrets management
- Configure firewall rules
- Use SSL certificates
- Implement rate limiting

## 🐛 Troubleshooting

### Common Issues

**Container Creation Failed**
```bash
# Check Docker daemon
docker info

# Check available ports
netstat -tlnp | grep :590

# Check logs
docker-compose logs backend
```

**Database Connection Issues**
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U user -d computer_use_db
```

**VNC Not Accessible**
```bash
# Check container status
docker ps | grep agent-session

# Check port mapping
docker port <container_id>

# Check logs
docker logs <container_id>
```

### Log Files
- Application logs: `./logs/`
- Container logs: `docker-compose logs <service>`
- Database logs: `docker-compose logs postgres`

## 🔄 Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📈 Scaling

### Horizontal Scaling
- Use load balancer (Nginx, HAProxy)
- Scale backend instances
- Use Redis Cluster for session state
- Use PostgreSQL read replicas

### Vertical Scaling
- Increase container resources
- Optimize database configuration
- Use connection pooling
- Enable caching

### Container Management
- Set resource limits per session
- Implement cleanup policies
- Monitor container health
- Use container orchestration (Kubernetes)

## 📝 API Usage Examples

### Create Session
```bash
curl -X POST "http://localhost:8000/api/v1/sessions/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "model": "claude-sonnet-4-20250514",
    "screen_width": 1024,
    "screen_height": 768
  }'
```

### Send Message
```bash
curl -X POST "http://localhost:8000/api/v1/sessions/{session_id}/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello, please help me with a task",
    "type": "user"
  }'
```

### Get Chat History
```bash
curl "http://localhost:8000/api/v1/sessions/{session_id}/messages?limit=10"
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check troubleshooting section
2. Review logs for errors
3. Open GitHub issue with details
4. Include environment information

---

Built with ❤️ for scalable AI agent deployments
