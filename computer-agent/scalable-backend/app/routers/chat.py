"""
REST API endpoints for chat management
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, func

from app.database.connection import get_db
from app.database.models import Session, ChatHistory
from app.models.session import (
    ChatMessage,
    ChatMessageRequest,
    ChatHistory as ChatHistoryResponse
)
from app.websocket.agent_ws import manager

router = APIRouter(prefix="/api/v1/sessions", tags=["chat"])


@router.post("/{session_id}/messages")
async def send_message(
    session_id: str,
    message: ChatMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send message to agent session"""
    try:
        # Verify session exists and is active
        session = await db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")
        
        # Save message to history
        chat_entry = ChatHistory(
            session_id=session_id,
            message=message.content,
            message_type=message.type,
            timestamp=datetime.utcnow()
        )
        db.add(chat_entry)
        
        # Update session last activity
        session.last_activity = datetime.utcnow()
        
        await db.commit()
        await db.refresh(chat_entry)
        
        # Forward to WebSocket for real-time processing
        await manager.handle_user_message(session_id, {
            'content': message.content,
            'type': message.type,
            'message_id': str(chat_entry.id)
        })
        
        return {
            "status": "sent",
            "message_id": str(chat_entry.id),
            "timestamp": chat_entry.timestamp.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")


@router.get("/{session_id}/messages", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: int = Query(50, ge=1, le=500, description="Maximum number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    message_type: Optional[str] = Query(None, description="Filter by message type"),
    since: Optional[datetime] = Query(None, description="Get messages since this timestamp"),
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for session"""
    try:
        # Verify session exists
        session = await db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Build query with filters
        query = select(ChatHistory).where(ChatHistory.session_id == session_id)
        
        if message_type:
            query = query.where(ChatHistory.message_type == message_type)
        
        if since:
            query = query.where(ChatHistory.timestamp >= since)
        
        # Get total count
        count_query = select(func.count(ChatHistory.id)).where(ChatHistory.session_id == session_id)
        if message_type:
            count_query = count_query.where(ChatHistory.message_type == message_type)
        if since:
            count_query = count_query.where(ChatHistory.timestamp >= since)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results, ordered by timestamp
        query = query.order_by(desc(ChatHistory.timestamp)).limit(limit).offset(offset)
        result = await db.execute(query)
        messages = result.scalars().all()
        
        # Convert to response format
        chat_messages = []
        for msg in reversed(messages):  # Reverse to get chronological order
            chat_messages.append(ChatMessage(
                session_id=session_id,
                message=msg.message,
                message_type=msg.message_type,
                timestamp=msg.timestamp,
                metadata=msg.message_metadata
            ))
        
        return ChatHistoryResponse(messages=chat_messages, total=total)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")


@router.get("/{session_id}/messages/{message_id}")
async def get_message(
    session_id: str,
    message_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific message by ID"""
    try:
        # Verify session exists
        session = await db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get message
        query = select(ChatHistory).where(
            and_(
                ChatHistory.id == message_id,
                ChatHistory.session_id == session_id
            )
        )
        result = await db.execute(query)
        message = result.scalar_one_or_none()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return ChatMessage(
            session_id=session_id,
            message=message.message,
            message_type=message.message_type,
            timestamp=message.timestamp,
            metadata=message.message_metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving message: {str(e)}")


@router.delete("/{session_id}/messages")
async def clear_chat_history(
    session_id: str,
    message_type: Optional[str] = Query(None, description="Clear only messages of this type"),
    before: Optional[datetime] = Query(None, description="Clear messages before this timestamp"),
    db: AsyncSession = Depends(get_db)
):
    """Clear chat history for a session"""
    try:
        # Verify session exists
        session = await db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Build delete query
        query = select(ChatHistory).where(ChatHistory.session_id == session_id)
        
        if message_type:
            query = query.where(ChatHistory.message_type == message_type)
        
        if before:
            query = query.where(ChatHistory.timestamp < before)
        
        # Get messages to delete (for counting)
        result = await db.execute(query)
        messages_to_delete = result.scalars().all()
        
        # Delete messages
        for message in messages_to_delete:
            await db.delete(message)
        
        await db.commit()
        
        # Notify WebSocket connections
        await manager.broadcast_to_session(session_id, {
            'type': 'chat_cleared',
            'message': f'Cleared {len(messages_to_delete)} messages',
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        return {
            "message": "Chat history cleared",
            "deleted_count": len(messages_to_delete),
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing chat history: {str(e)}")


@router.get("/{session_id}/messages/export")
async def export_chat_history(
    session_id: str,
    format: str = Query("json", description="Export format: json, txt, csv"),
    db: AsyncSession = Depends(get_db)
):
    """Export chat history in various formats"""
    try:
        # Verify session exists
        session = await db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all messages
        query = select(ChatHistory).where(ChatHistory.session_id == session_id).order_by(ChatHistory.timestamp)
        result = await db.execute(query)
        messages = result.scalars().all()
        
        if format.lower() == "json":
            return {
                "session_id": session_id,
                "session_info": {
                    "user_id": session.user_id,
                    "model": session.model,
                    "created_at": session.created_at.isoformat(),
                    "status": session.status
                },
                "messages": [
                    {
                        "id": str(msg.id),
                        "message": msg.message,
                        "type": msg.message_type,
                        "timestamp": msg.timestamp.isoformat(),
                        "metadata": msg.message_metadata
                    }
                    for msg in messages
                ]
            }
        
        elif format.lower() == "txt":
            lines = [f"Chat History for Session: {session_id}"]
            lines.append(f"User: {session.user_id}")
            lines.append(f"Model: {session.model}")
            lines.append(f"Created: {session.created_at}")
            lines.append("-" * 50)
            
            for msg in messages:
                timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                lines.append(f"[{timestamp}] {msg.message_type.upper()}: {msg.message}")
            
            return {"content": "\n".join(lines), "format": "text"}
        
        elif format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow(["timestamp", "type", "message", "metadata"])
            
            # Data
            for msg in messages:
                writer.writerow([
                    msg.timestamp.isoformat(),
                    msg.message_type,
                    msg.message,
                    msg.message_metadata or ""
                ])
            
            return {"content": output.getvalue(), "format": "csv"}
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use: json, txt, csv")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting chat history: {str(e)}")


@router.get("/{session_id}/messages/stats")
async def get_message_stats(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get message statistics for a session"""
    try:
        # Verify session exists
        session = await db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get message counts by type
        query = select(
            ChatHistory.message_type,
            func.count(ChatHistory.id).label('count')
        ).where(
            ChatHistory.session_id == session_id
        ).group_by(ChatHistory.message_type)
        
        result = await db.execute(query)
        type_counts = {row.message_type: row.count for row in result}
        
        # Get first and last message timestamps
        first_msg_query = select(ChatHistory.timestamp).where(
            ChatHistory.session_id == session_id
        ).order_by(ChatHistory.timestamp).limit(1)
        
        last_msg_query = select(ChatHistory.timestamp).where(
            ChatHistory.session_id == session_id
        ).order_by(desc(ChatHistory.timestamp)).limit(1)
        
        first_result = await db.execute(first_msg_query)
        last_result = await db.execute(last_msg_query)
        
        first_message = first_result.scalar()
        last_message = last_result.scalar()
        
        # Calculate conversation duration
        duration_minutes = 0
        if first_message and last_message:
            duration = last_message - first_message
            duration_minutes = int(duration.total_seconds() / 60)
        
        return {
            "session_id": session_id,
            "total_messages": sum(type_counts.values()),
            "message_types": type_counts,
            "first_message": first_message.isoformat() if first_message else None,
            "last_message": last_message.isoformat() if last_message else None,
            "conversation_duration_minutes": duration_minutes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting message stats: {str(e)}")
