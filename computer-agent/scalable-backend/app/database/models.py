"""
SQLAlchemy database models for PostgreSQL
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

Base = declarative_base()


class Session(Base):
    """Database model for agent sessions"""
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    status = Column(String, default="active", index=True)
    model = Column(String, default="claude-sonnet-4-20250514")
    screen_width = Column(Integer, default=1024)
    screen_height = Column(Integer, default=768)
    vnc_port = Column(Integer)  # Removed unique constraint for pool-based system
    container_id = Column(String, unique=True)
    system_prompt = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    ended_at = Column(DateTime)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to chat history
    chat_messages = relationship("ChatHistory", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, status={self.status})>"


class ChatHistory(Base):
    """Database model for chat message history"""
    __tablename__ = "chat_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    message_type = Column(String, nullable=False)  # user, assistant, system, tool
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    message_metadata = Column(Text)  # JSON string for screenshots, actions, etc.
    
    # Relationship back to session
    session = relationship("Session", back_populates="chat_messages")
    
    def __repr__(self):
        return f"<ChatHistory(id={self.id}, session_id={self.session_id}, type={self.message_type})>"


class ContainerMetrics(Base):
    """Database model for container performance metrics"""
    __tablename__ = "container_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    container_id = Column(String, nullable=False)
    cpu_percent = Column(Integer)
    memory_usage_mb = Column(Integer)
    memory_limit_mb = Column(Integer)
    network_rx_bytes = Column(Integer)
    network_tx_bytes = Column(Integer)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<ContainerMetrics(session_id={self.session_id}, cpu={self.cpu_percent}%)>"


class APIUsage(Base):
    """Database model for tracking API usage and costs"""
    __tablename__ = "api_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    model = Column(String, nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cached_tokens = Column(Integer, default=0)
    api_calls = Column(Integer, default=1)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<APIUsage(session_id={self.session_id}, model={self.model}, calls={self.api_calls})>"
