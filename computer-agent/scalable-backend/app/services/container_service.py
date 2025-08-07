"""
Docker container orchestration service for agent sessions
"""

import asyncio
import os
import socket
from typing import Dict, Tuple, Optional, Set
import docker
from docker.errors import DockerException, NotFound, APIError
import logging

logger = logging.getLogger(__name__)


class ContainerService:
    """Service for managing pre-created agent containers"""
    
    def __init__(self):
        # Pre-defined agent containers with their ports
        self.agent_pool = {
            "agent-1": {"vnc_port": 5900, "novnc_port": 6900, "container_name": "scalable-backend-agent-1-1"},
            "agent-2": {"vnc_port": 5901, "novnc_port": 6901, "container_name": "scalable-backend-agent-2-1"},
            "agent-3": {"vnc_port": 5902, "novnc_port": 6902, "container_name": "scalable-backend-agent-3-1"}
        }
        self.available_agents = set(self.agent_pool.keys())  # Available agents
        self.session_assignments: Dict[str, str] = {}  # session_id -> agent_id
        self.client = None  # No Docker client needed for pre-created containers

    
    async def create_session_container(
        self, 
        session_id: str, 
        config: Dict[str, any]
    ) -> Tuple[str, int]:
        """Assign an available agent container to the session"""
        if not self.available_agents:
            raise Exception("No available agent containers. All agents are busy.")
        
        # Get the next available agent
        agent_id = self.available_agents.pop()
        agent_info = self.agent_pool[agent_id]
        
        # Assign the agent to this session
        self.session_assignments[session_id] = agent_id
        
        logger.info(f"Assigned agent {agent_id} to session {session_id} on VNC port {agent_info['vnc_port']}")
        
        # Return container name and VNC port
        return agent_info["container_name"], agent_info["vnc_port"]
    
    async def _wait_for_container_ready(self, container, timeout: int = 120):
        """Wait for container to be ready to accept connections"""
        logger.info(f"Waiting for container {container.id[:12]} to be ready...")
        
        for i in range(timeout):
            try:
                container.reload()
                if container.status == 'running':
                    # Additional health checks
                    # Check if VNC server is responding
                    await asyncio.sleep(2)  # Give services time to start
                    
                    # Try to get container logs to verify startup
                    logs = container.logs(tail=50).decode('utf-8')
                    if 'VNC server started' in logs or 'x11vnc' in logs:
                        logger.info(f"Container {container.id[:12]} is ready")
                        return
                    
                    # If specific ready indicators aren't found, wait a bit more
                    if i > 30:  # After 30 seconds, just check if it's running
                        logger.info(f"Container {container.id[:12]} appears ready (running)")
                        return
                        
            except Exception as e:
                logger.warning(f"Error checking container readiness: {e}")
                
            await asyncio.sleep(1)
            
        raise Exception(f"Container failed to start within {timeout} seconds")
    
    async def stop_session_container(self, session_id: str) -> bool:
        """Release agent back to the pool"""
        if session_id not in self.session_assignments:
            logger.warning(f"No agent assigned to session {session_id}")
            return False
            
        agent_id = self.session_assignments[session_id]
        
        try:
            # Release the agent back to the pool
            self.available_agents.add(agent_id)
            
            # Clean up assignment
            del self.session_assignments[session_id]
            
            logger.info(f"Released agent {agent_id} back to pool for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error releasing agent for session {session_id}: {e}")
            return False
    
    async def get_container_info(self, session_id: str) -> Optional[Dict]:
        """Get information about a session's container"""
        if session_id not in self.session_containers:
            return None
            
        container_id = self.session_containers[session_id]
        
        try:
            container = self.client.containers.get(container_id)
            container.reload()
            
            # Get port mappings
            port_bindings = container.attrs.get('NetworkSettings', {}).get('Ports', {})
            vnc_port = None
            novnc_port = None
            combined_port = None
            
            if '5900/tcp' in port_bindings and port_bindings['5900/tcp']:
                vnc_port = int(port_bindings['5900/tcp'][0]['HostPort'])
            if '6080/tcp' in port_bindings and port_bindings['6080/tcp']:
                novnc_port = int(port_bindings['6080/tcp'][0]['HostPort'])
            if '8080/tcp' in port_bindings and port_bindings['8080/tcp']:
                combined_port = int(port_bindings['8080/tcp'][0]['HostPort'])
            
            return {
                'container_id': container_id,
                'status': container.status,
                'created': container.attrs.get('Created'),
                'vnc_port': vnc_port,
                'novnc_port': novnc_port,
                'combined_port': combined_port,
                'image': container.image.tags[0] if container.image.tags else 'unknown',
            }
            
        except NotFound:
            logger.warning(f"Container {container_id} not found")
            # Clean up tracking
            del self.session_containers[session_id]
            return None
        except Exception as e:
            logger.error(f"Error getting container info for session {session_id}: {e}")
            return None
    
    async def get_container_stats(self, session_id: str) -> Optional[Dict]:
        """Get resource usage stats for a container"""
        if session_id not in self.session_containers:
            return None
            
        container_id = self.session_containers[session_id]
        
        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=False)
            
            # Parse CPU usage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
            
            # Parse memory usage
            memory_usage = stats['memory_stats'].get('usage', 0)
            memory_limit = stats['memory_stats'].get('limit', 0)
            memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0
            
            # Parse network usage
            network_stats = stats.get('networks', {})
            rx_bytes = sum(net.get('rx_bytes', 0) for net in network_stats.values())
            tx_bytes = sum(net.get('tx_bytes', 0) for net in network_stats.values())
            
            return {
                'cpu_percent': round(cpu_percent, 2),
                'memory_usage_mb': round(memory_usage / 1024 / 1024, 2),
                'memory_limit_mb': round(memory_limit / 1024 / 1024, 2),
                'memory_percent': round(memory_percent, 2),
                'network_rx_bytes': rx_bytes,
                'network_tx_bytes': tx_bytes,
            }
            
        except Exception as e:
            logger.error(f"Error getting container stats for session {session_id}: {e}")
            return None
    
    async def cleanup_orphaned_containers(self):
        """Clean up any orphaned agent containers"""
        try:
            containers = self.client.containers.list(
                all=True, 
                filters={"name": "agent-session-*"}
            )
            
            cleaned = 0
            for container in containers:
                try:
                    if container.status in ['exited', 'dead']:
                        container.remove()
                        cleaned += 1
                        logger.info(f"Removed orphaned container: {container.name}")
                except Exception as e:
                    logger.warning(f"Failed to remove container {container.name}: {e}")
            
            logger.info(f"Cleaned up {cleaned} orphaned containers")
            return cleaned
            
        except Exception as e:
            logger.error(f"Error during container cleanup: {e}")
            return 0
