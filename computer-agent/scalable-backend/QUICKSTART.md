# 🚀 Quick Start Guide

## Step-by-Step Setup

### 1. **Environment Setup**
```bash
# Navigate to the scalable-backend directory
cd computer-agent/scalable-backend

# Run setup script (creates .env file and directories)
./setup.sh

# OR manually create .env file
cp env.example .env
```

### 2. **Configure API Key**
Edit the `.env` file and add your Anthropic API key:
```bash
# Edit .env file
ANTHROPIC_API_KEY=your_actual_api_key_here
API_PROVIDER=anthropic
```

### 3. **Start Services**
```bash
# Build and start all services
docker-compose up --build

# OR run in background
docker-compose up --build -d
```

### 4. **Access the Interface**
- **Main Interface**: http://localhost:8000/static/index.html
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Fix Common Issues

### Docker Compose Command Error
❌ **Wrong:** `docker-compose up --build .`  
✅ **Correct:** `docker-compose up --build`

### Environment Variable Warnings
These warnings are normal if you're only using Anthropic API:
- AWS_* variables (only needed for Bedrock)
- CLOUD_ML_* variables (only needed for Vertex)

### Port Conflicts
If you get port conflicts, check what's running:
```bash
# Check what's using port 8000
netstat -tulpn | grep :8000

# Check Docker containers
docker ps
```

### Container Creation Issues
```bash
# Check Docker daemon
docker info

# Check logs
docker-compose logs backend

# Restart with fresh build
docker-compose down
docker-compose up --build
```

## 🎯 Usage

1. **Create Session**: Click "Create Session" in the web interface
2. **Chat**: Type messages in the chat panel
3. **Desktop View**: See the agent's desktop in the VNC panel
4. **End Session**: Click "End Session" when done

## 📊 Optional: Enable Monitoring
```bash
# Start with Prometheus and Grafana
docker-compose --profile monitoring up --build

# Access monitoring
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)
```

## 🛑 Troubleshooting

### If containers fail to start:
1. Check Docker is running: `docker info`
2. Check available disk space: `df -h`
3. Check logs: `docker-compose logs`

### If API calls fail:
1. Verify ANTHROPIC_API_KEY in .env
2. Check internet connectivity
3. Verify API key permissions

### If VNC doesn't work:
1. Wait 30-60 seconds for container startup
2. Check container logs: `docker logs <container_name>`
3. Try refreshing the browser

## 🔄 Development Mode

For development with hot reload:
```bash
# Install Python dependencies locally
pip install -r requirements.txt

# Run backend locally (with Docker for databases)
docker-compose up postgres redis -d
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
