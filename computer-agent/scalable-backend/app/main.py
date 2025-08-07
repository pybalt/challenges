"""
FastAPI Backend Service for Scalable Computer Use Agent
"""

import os
import uuid
from contextlib import asynccontextmanager
from typing import Dict

import docker
import redis
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse

from app.database.connection import init_db
from app.routers import sessions, chat
from app.websocket.agent_ws import manager

# Global state management
active_sessions: Dict[str, dict] = {}

# No Docker client needed - using pre-created agent pool
docker_client = None
print("Using pre-created agent pool - no Docker client required")

try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'redis'), 
        port=int(os.getenv('REDIS_PORT', '6379')), 
        db=0,
        decode_responses=True
    )
    # Test connection
    redis_client.ping()
except Exception as e:
    print(f"Warning: Redis connection failed: {e}")
    redis_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and cleanup on startup/shutdown"""
    # Startup
    await init_db()
    print("Database initialized")
    
    yield
    
    # Shutdown
    # Using pre-created agent pool - no cleanup needed
    print("Agent pool containers remain running for reuse")


app = FastAPI(
    title="Computer Use Agent API", 
    version="1.0.0",
    description="Scalable backend for Computer Use Agent with session management",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router)
app.include_router(chat.router)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "docker": "connected",
        "redis": "connected" if redis_client else "disconnected",
        "active_sessions": len(active_sessions)
    }
    
    # Using pre-created agent pool - no Docker client needed
    status["docker"] = "pool-based"
    
    return status


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Computer Use Agent Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# VNC Reverse Proxy is now handled by Nginx
# (removed FastAPI reverse proxy endpoints)


# WebSocket endpoint for real-time communication
from app.websocket.agent_ws import websocket_endpoint
app.websocket("/ws/{session_id}")(websocket_endpoint)

# Export globals for use in other modules
__all__ = ["active_sessions", "docker_client", "redis_client"]
