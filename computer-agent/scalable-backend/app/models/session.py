"""
Pydantic models for session management
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    """Request model for creating a new session"""
    user_id: str = Field(..., description="User identifier")
    model: str = Field(default="claude-sonnet-4-20250514", description="AI model to use")
    screen_width: int = Field(default=1024, ge=800, le=1920, description="Screen width in pixels")
    screen_height: int = Field(default=768, ge=600, le=1080, description="Screen height in pixels")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt suffix")


class SessionResponse(BaseModel):
    """Response model for session information"""
    session_id: str = Field(..., description="Unique session identifier")
    status: str = Field(..., description="Session status")
    vnc_port: int = Field(..., description="VNC port for desktop access")
    websocket_url: str = Field(..., description="WebSocket URL for real-time communication")
    created_at: datetime = Field(..., description="Session creation timestamp")
    user_id: str = Field(..., description="User identifier")
    model: str = Field(..., description="AI model being used")
    screen_width: int = Field(..., description="Screen width")
    screen_height: int = Field(..., description="Screen height")


class SessionList(BaseModel):
    """Response model for listing sessions"""
    sessions: List[SessionResponse] = Field(..., description="List of sessions")
    total: int = Field(..., description="Total number of sessions")


class ChatMessage(BaseModel):
    """Model for chat messages"""
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="Message content")
    message_type: str = Field(..., description="Message type: user, assistant, system")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ChatMessageRequest(BaseModel):
    """Request model for sending chat messages"""
    content: str = Field(..., description="Message content")
    type: str = Field(default="user", description="Message type")


class ChatHistory(BaseModel):
    """Response model for chat history"""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    total: int = Field(..., description="Total number of messages")


class SessionStats(BaseModel):
    """Model for session statistics"""
    session_id: str
    total_messages: int
    duration_minutes: int
    last_activity: datetime
    container_status: str
