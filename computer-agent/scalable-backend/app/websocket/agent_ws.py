"""
WebSocket manager for real-time communication with agent sessions
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from datetime import datetime

from app.database.connection import async_session_maker
from app.database.models import Session, ChatHistory
from app.services.container_service import ContainerService

logger = logging.getLogger(__name__)


class AgentWebSocketManager:
    """Manager for WebSocket connections to agent sessions"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        self.container_service = ContainerService()
        
    async def connect(self, websocket: WebSocket, session_id: str, user_id: Optional[str] = None):
        """Accept a WebSocket connection for a session"""
        await websocket.accept()
        
        # Initialize session connections if not exists
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        # Add connection to session
        self.active_connections[session_id].add(websocket)
        
        # Store metadata
        self.connection_metadata[websocket] = {
            'session_id': session_id,
            'user_id': user_id,
            'connected_at': datetime.utcnow(),
        }
        
        logger.info(f"WebSocket connected for session {session_id}")
        
        # Send welcome message
        await self.send_to_websocket(websocket, {
            'type': 'connection',
            'status': 'connected',
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
        })
        
    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        try:
            if websocket in self.connection_metadata:
                session_id = self.connection_metadata[websocket]['session_id']
                
                # Remove from session connections
                if session_id in self.active_connections:
                    self.active_connections[session_id].discard(websocket)
                    
                    # Clean up empty session sets
                    if not self.active_connections[session_id]:
                        del self.active_connections[session_id]
                
                # Remove metadata
                del self.connection_metadata[websocket]
                
                logger.info(f"WebSocket disconnected for session {session_id}")
        except Exception as e:
            logger.error(f"Error during WebSocket disconnect cleanup: {e}")
    
    async def send_to_websocket(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to a specific WebSocket connection"""
        try:
            # Check if websocket is still connected
            if websocket.client_state.name == "DISCONNECTED":
                logger.debug("WebSocket already disconnected, skipping message")
                self.disconnect(websocket)
                return
                
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")
            # Remove broken connection
            self.disconnect(websocket)
    
    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]):
        """Send message to all connections for a session"""
        if session_id not in self.active_connections:
            logger.warning(f"No active connections for session {session_id}")
            return
        
        # Create a copy of connections to avoid modification during iteration
        connections = list(self.active_connections[session_id])
        
        for websocket in connections:
            await self.send_to_websocket(websocket, message)
    
    async def handle_user_message(self, session_id: str, message_data: Dict[str, Any]):
        """Handle incoming user message and forward to agent container"""
        try:
            # Save message to database
            async with async_session_maker() as db:
                # Verify session exists
                session = await db.get(Session, session_id)
                if not session:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                # Save user message
                chat_message = ChatHistory(
                    session_id=session_id,
                    message=message_data.get('content', ''),
                    message_type='user',
                    timestamp=datetime.utcnow(),
                    message_metadata=json.dumps(message_data.get('metadata', {}))
                )
                db.add(chat_message)
                
                # Update session last activity
                session.last_activity = datetime.utcnow()
                
                await db.commit()
            
            # Broadcast user message to all session connections
            await self.broadcast_to_session(session_id, {
                'type': 'user_message',
                'content': message_data.get('content', ''),
                'timestamp': datetime.utcnow().isoformat(),
                'message_id': str(chat_message.id)
            })
            
            # Here you would integrate with the agent container
            # For now, we'll simulate an agent response
            await self._simulate_agent_response(session_id, message_data.get('content', ''))
            
        except Exception as e:
            logger.error(f"Error handling user message for session {session_id}: {e}")
            await self.broadcast_to_session(session_id, {
                'type': 'error',
                'message': f"Error processing message: {str(e)}",
                'timestamp': datetime.utcnow().isoformat(),
            })
    
    async def _simulate_agent_response(self, session_id: str, user_message: str):
        """Simulate agent response (replace with actual agent integration)"""
        # This is a placeholder - in production, this would integrate with the actual agent
        await asyncio.sleep(1)  # Simulate processing time
        
        # Generate a simple response
        response_content = f"I received your message: '{user_message}'. This is a simulated response from the agent container."
        
        # Save agent response to database
        async with async_session_maker() as db:
            chat_message = ChatHistory(
                session_id=session_id,
                message=response_content,
                message_type='assistant',
                timestamp=datetime.utcnow(),
                message_metadata=json.dumps({'simulated': True})
            )
            db.add(chat_message)
            await db.commit()
        
        # Broadcast agent response
        await self.broadcast_to_session(session_id, {
            'type': 'agent_message',
            'content': response_content,
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': str(chat_message.id)
        })
    
    async def handle_container_event(self, session_id: str, event_type: str, data: Dict[str, Any]):
        """Handle events from container (screenshots, tool results, etc.)"""
        try:
            # Save container event to database if needed
            if event_type in ['screenshot', 'tool_result']:
                async with async_session_maker() as db:
                    chat_message = ChatHistory(
                        session_id=session_id,
                        message=data.get('message', ''),
                        message_type='tool',
                        timestamp=datetime.utcnow(),
                        message_metadata=json.dumps(data)
                    )
                    db.add(chat_message)
                    await db.commit()
            
            # Broadcast event to session connections
            await self.broadcast_to_session(session_id, {
                'type': event_type,
                'data': data,
                'timestamp': datetime.utcnow().isoformat(),
            })
            
        except Exception as e:
            logger.error(f"Error handling container event for session {session_id}: {e}")
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session's WebSocket connections"""
        if session_id not in self.active_connections:
            return {'active_connections': 0}
        
        connections = self.active_connections[session_id]
        connection_info = []
        
        for ws in connections:
            if ws in self.connection_metadata:
                metadata = self.connection_metadata[ws]
                connection_info.append({
                    'user_id': metadata.get('user_id'),
                    'connected_at': metadata.get('connected_at').isoformat(),
                    'duration_seconds': (datetime.utcnow() - metadata.get('connected_at')).total_seconds(),
                })
        
        return {
            'active_connections': len(connections),
            'connections': connection_info,
        }
    
    def get_all_sessions(self) -> Dict[str, int]:
        """Get count of active connections per session"""
        return {
            session_id: len(connections) 
            for session_id, connections in self.active_connections.items()
        }


# Global manager instance
manager = AgentWebSocketManager()


async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for agent communication"""
    try:
        # TODO: Add authentication/authorization here
        user_id = None  # Extract from token/session
        
        await manager.connect(websocket, session_id, user_id)
        
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                message_type = message.get('type', 'message')
                
                if message_type == 'message':
                    await manager.handle_user_message(session_id, message)
                elif message_type == 'ping':
                    await manager.send_to_websocket(websocket, {
                        'type': 'pong',
                        'timestamp': datetime.utcnow().isoformat(),
                    })
                else:
                    logger.warning(f"Unknown message type: {message_type}")
                
            except json.JSONDecodeError:
                await manager.send_to_websocket(websocket, {
                    'type': 'error',
                    'message': 'Invalid JSON message format',
                    'timestamp': datetime.utcnow().isoformat(),
                })
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected during message processing")
                break
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                try:
                    await manager.send_to_websocket(websocket, {
                        'type': 'error',
                        'message': f'Error processing message: {str(e)}',
                        'timestamp': datetime.utcnow().isoformat(),
                    })
                except:
                    # If we can't send the error message, the connection is broken
                    logger.error("Failed to send error message, connection likely broken")
                    break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
    finally:
        manager.disconnect(websocket)
