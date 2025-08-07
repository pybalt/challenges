#!/bin/bash

# Setup script for Computer Use Agent Scalable Backend

echo "🚀 Setting up Computer Use Agent Scalable Backend..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created. Please edit it with your API keys."
else
    echo "✅ .env file already exists."
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p logs
mkdir -p monitoring/grafana/provisioning
mkdir -p monitoring/grafana/dashboards
mkdir -p nginx/ssl

# Set permissions
chmod +x setup.sh

echo "🔧 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your ANTHROPIC_API_KEY"
echo "2. Run: docker-compose up --build"
echo "3. Access the interface at: http://localhost:8000/static/index.html"
echo ""
echo "For monitoring (optional): docker-compose --profile monitoring up --build"
