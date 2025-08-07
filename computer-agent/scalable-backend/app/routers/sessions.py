"""
REST API endpoints for session management
"""

import os
import uuid
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_

from app.database.connection import get_db
from app.database.models import Session, ChatHistory, ContainerMetrics
from app.models.session import (
    SessionCreate, 
    SessionResponse, 
    SessionList, 
    SessionStats
)
from app.services.container_service import ContainerService
from app.websocket.agent_ws import manager

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])
container_service = ContainerService()


@router.post("/", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Create a new computer use session"""
    session_id = str(uuid.uuid4())
    
    try:
        # Create container configuration
        container_config = {
            'api_key': os.getenv('ANTHROPIC_API_KEY'),
            'width': session_data.screen_width,
            'height': session_data.screen_height,
            'api_provider': os.getenv('API_PROVIDER', 'anthropic'),
            'memory_limit': os.getenv('CONTAINER_MEMORY_LIMIT', '2g'),
            'cpu_count': int(os.getenv('CONTAINER_CPU_COUNT', '2')),
        }
        
        # Validate API key
        if not container_config['api_key']:
            raise HTTPException(
                status_code=400, 
                detail="ANTHROPIC_API_KEY environment variable not set"
            )
        
        # Create container
        container_id, vnc_port = await container_service.create_session_container(
            session_id, 
            container_config
        )
        
        # Save to database
        db_session = Session(
            id=session_id,
            user_id=session_data.user_id,
            model=session_data.model,
            screen_width=session_data.screen_width,
            screen_height=session_data.screen_height,
            vnc_port=vnc_port,
            container_id=container_id,
            system_prompt=session_data.system_prompt,
            status="active",
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        
        return SessionResponse(
            session_id=session_id,
            status="active",
            vnc_port=vnc_port,
            websocket_url=f"/ws/{session_id}",
            created_at=db_session.created_at,
            user_id=session_data.user_id,
            model=session_data.model,
            screen_width=session_data.screen_width,
            screen_height=session_data.screen_height
        )
        
    except Exception as e:
        # Clean up on failure
        try:
            await container_service.stop_session_container(session_id)
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")


@router.get("/", response_model=SessionList)
async def list_sessions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of sessions to return"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip"),
    db: AsyncSession = Depends(get_db)
):
    """List sessions with optional filtering"""
    try:
        # Build query with filters
        query = select(Session).order_by(desc(Session.created_at))
        
        if user_id:
            query = query.where(Session.user_id == user_id)
        if status:
            query = query.where(Session.status == status)
        
        # Get total count
        count_query = select(func.count(Session.id))
        if user_id:
            count_query = count_query.where(Session.user_id == user_id)
        if status:
            count_query = count_query.where(Session.status == status)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        # Convert to response format
        session_responses = []
        for session in sessions:
            session_responses.append(SessionResponse(
                session_id=str(session.id),
                status=session.status,
                vnc_port=session.vnc_port or 0,
                websocket_url=f"/ws/{session.id}",
                created_at=session.created_at,
                user_id=session.user_id,
                model=session.model,
                screen_width=session.screen_width,
                screen_height=session.screen_height
            ))
        
        return SessionList(sessions=session_responses, total=total)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get session details"""
    try:
        session = await db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse(
            session_id=str(session.id),
            status=session.status,
            vnc_port=session.vnc_port or 0,
            websocket_url=f"/ws/{session.id}",
            created_at=session.created_at,
            user_id=session.user_id,
            model=session.model,
            screen_width=session.screen_width,
            screen_height=session.screen_height
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")


@router.delete("/{session_id}")
async def end_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """End and cleanup session"""
    try:
        session = await db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Stop container
        container_stopped = await container_service.stop_session_container(session_id)
        
        # Update database
        session.status = "ended"
        session.ended_at = datetime.utcnow()
        await db.commit()
        
        # Notify WebSocket connections
        await manager.broadcast_to_session(session_id, {
            'type': 'session_ended',
            'message': 'Session has been terminated',
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        return {
            "message": "Session ended successfully",
            "container_stopped": container_stopped,
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ending session: {str(e)}")


@router.get("/{session_id}/stats", response_model=SessionStats)
async def get_session_stats(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get session statistics"""
    try:
        session = await db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get message count
        message_count_query = select(func.count(ChatHistory.id)).where(
            ChatHistory.session_id == session_id
        )
        message_count_result = await db.execute(message_count_query)
        total_messages = message_count_result.scalar() or 0
        
        # Calculate duration
        end_time = session.ended_at or datetime.utcnow()
        duration = end_time - session.created_at
        duration_minutes = int(duration.total_seconds() / 60)
        
        # Get container status
        container_info = await container_service.get_container_info(session_id)
        container_status = container_info.get('status', 'unknown') if container_info else 'stopped'
        
        return SessionStats(
            session_id=session_id,
            total_messages=total_messages,
            duration_minutes=duration_minutes,
            last_activity=session.last_activity,
            container_status=container_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session stats: {str(e)}")


@router.get("/{session_id}/container/info")
async def get_container_info(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get container information for a session"""
    try:
        session = await db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        container_info = await container_service.get_container_info(session_id)
        if not container_info:
            raise HTTPException(status_code=404, detail="Container not found")
        
        return container_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting container info: {str(e)}")


@router.get("/{session_id}/container/stats")
async def get_container_stats(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get container resource usage statistics"""
    try:
        session = await db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        stats = await container_service.get_container_stats(session_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Container stats not available")
        
        # Optionally save stats to database
        metrics = ContainerMetrics(
            session_id=session_id,
            container_id=session.container_id,
            cpu_percent=int(stats['cpu_percent']),
            memory_usage_mb=int(stats['memory_usage_mb']),
            memory_limit_mb=int(stats['memory_limit_mb']),
            network_rx_bytes=stats['network_rx_bytes'],
            network_tx_bytes=stats['network_tx_bytes'],
            recorded_at=datetime.utcnow()
        )
        db.add(metrics)
        await db.commit()
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting container stats: {str(e)}")


@router.post("/{session_id}/restart")
async def restart_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Restart a session's container"""
    try:
        session = await db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Stop existing container
        await container_service.stop_session_container(session_id)
        
        # Create new container with same configuration
        container_config = {
            'api_key': os.getenv('ANTHROPIC_API_KEY'),
            'width': session.screen_width,
            'height': session.screen_height,
            'api_provider': os.getenv('API_PROVIDER', 'anthropic'),
        }
        
        container_id, vnc_port = await container_service.create_session_container(
            session_id,
            container_config
        )
        
        # Update session
        session.container_id = container_id
        session.vnc_port = vnc_port
        session.status = "active"
        session.last_activity = datetime.utcnow()
        await db.commit()
        
        # Notify WebSocket connections
        await manager.broadcast_to_session(session_id, {
            'type': 'session_restarted',
            'message': 'Session container has been restarted',
            'vnc_port': vnc_port,
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        return {
            "message": "Session restarted successfully",
            "session_id": session_id,
            "container_id": container_id,
            "vnc_port": vnc_port
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restarting session: {str(e)}")


@router.post("/cleanup")
async def cleanup_sessions(
    older_than_hours: int = Query(24, ge=1, description="Clean up sessions older than X hours"),
    db: AsyncSession = Depends(get_db)
):
    """Clean up old inactive sessions"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        
        # Find old sessions
        query = select(Session).where(
            and_(
                Session.status == "active",
                Session.last_activity < cutoff_time
            )
        )
        result = await db.execute(query)
        old_sessions = result.scalars().all()
        
        cleaned_count = 0
        for session in old_sessions:
            try:
                # Stop container
                await container_service.stop_session_container(str(session.id))
                
                # Update session status
                session.status = "ended"
                session.ended_at = datetime.utcnow()
                cleaned_count += 1
                
            except Exception as e:
                print(f"Error cleaning up session {session.id}: {e}")
        
        await db.commit()
        
        # Clean up orphaned containers
        orphaned_count = await container_service.cleanup_orphaned_containers()
        
        return {
            "message": f"Cleanup completed",
            "sessions_cleaned": cleaned_count,
            "containers_cleaned": orphaned_count,
            "cutoff_time": cutoff_time.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")


@router.get("/{session_id}/websocket/stats")
async def get_websocket_stats(session_id: str):
    """Get WebSocket connection statistics for a session"""
    try:
        stats = manager.get_session_stats(session_id)
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting WebSocket stats: {str(e)}")


@router.get("/websocket/overview")
async def get_websocket_overview():
    """Get overview of all WebSocket connections"""
    try:
        overview = manager.get_all_sessions()
        return {
            "total_sessions": len(overview),
            "total_connections": sum(overview.values()),
            "sessions": overview
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting WebSocket overview: {str(e)}")
