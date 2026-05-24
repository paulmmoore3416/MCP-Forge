"""
MCP Server Discovery Service

Discovers MCP servers through multiple methods:
- Local process scanning
- Docker container scanning
- Network service scanning
"""
import asyncio
import logging
import psutil
import docker
import socket
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.mcp_server import MCPServer, ProtocolType, ServerStatus
from app.schemas.mcp_server import MCPServerCreate

logger = logging.getLogger(__name__)


class MCPDiscoveryService:
    """Service for discovering MCP servers"""
    
    def __init__(self):
        self.docker_client = None
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker client not available: {e}")
    
    async def discover_all(
        self,
        db: AsyncSession,
        scan_local: bool = True,
        scan_docker: bool = True,
        scan_network: bool = False,
        network_ranges: Optional[List[str]] = None,
        ports: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Discover MCP servers using all available methods
        
        Args:
            db: Database session
            scan_local: Scan local processes
            scan_docker: Scan Docker containers
            scan_network: Scan network
            network_ranges: Network ranges to scan (CIDR notation)
            ports: Ports to scan
            
        Returns:
            Discovery results with count and discovered servers
        """
        start_time = datetime.utcnow()
        discovered_servers = []
        
        try:
            # Scan local processes
            if scan_local:
                logger.info("Starting local process scan...")
                local_servers = await self._discover_local_processes()
                discovered_servers.extend(local_servers)
                logger.info(f"Found {len(local_servers)} local MCP servers")
            
            # Scan Docker containers
            if scan_docker and self.docker_client:
                logger.info("Starting Docker container scan...")
                docker_servers = await self._discover_docker_containers()
                discovered_servers.extend(docker_servers)
                logger.info(f"Found {len(docker_servers)} Docker MCP servers")
            
            # Scan network
            if scan_network:
                logger.info("Starting network scan...")
                network_servers = await self._discover_network_services(
                    network_ranges or [],
                    ports or [8080, 8000, 3000, 5000]
                )
                discovered_servers.extend(network_servers)
                logger.info(f"Found {len(network_servers)} network MCP servers")
            
            # Save discovered servers to database
            saved_count = 0
            for server_data in discovered_servers:
                try:
                    # Check if server already exists
                    existing = await self._find_existing_server(db, server_data)
                    
                    if existing:
                        # Update existing server
                        existing.status = ServerStatus.ONLINE
                        existing.last_seen = datetime.utcnow()
                        existing.discovery_metadata = server_data.get("discovery_metadata")
                        logger.info(f"Updated existing server: {existing.name}")
                    else:
                        # Create new server
                        new_server = MCPServer(
                            name=server_data["name"],
                            description=server_data.get("description"),
                            protocol=server_data["protocol"],
                            host=server_data.get("host"),
                            port=server_data.get("port"),
                            path=server_data.get("path"),
                            status=ServerStatus.ONLINE,
                            discovered_by=server_data.get("discovered_by", "auto"),
                            discovery_metadata=server_data.get("discovery_metadata"),
                            last_seen=datetime.utcnow()
                        )
                        db.add(new_server)
                        saved_count += 1
                        logger.info(f"Created new server: {new_server.name}")
                    
                except Exception as e:
                    logger.error(f"Error saving server {server_data.get('name')}: {e}")
                    continue
            
            await db.commit()
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return {
                "discovered_count": len(discovered_servers),
                "saved_count": saved_count,
                "scan_duration_seconds": duration,
                "scan_timestamp": start_time,
                "servers": discovered_servers
            }
            
        except Exception as e:
            logger.error(f"Discovery error: {e}")
            await db.rollback()
            raise
    
    async def _discover_local_processes(self) -> List[Dict[str, Any]]:
        """Discover MCP servers running as local processes"""
        discovered = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'connections']):
                try:
                    proc_info = proc.info
                    cmdline = proc_info.get('cmdline', [])
                    
                    # Look for MCP-related processes
                    if self._is_mcp_process(cmdline):
                        server_info = self._extract_server_info_from_process(proc_info)
                        if server_info:
                            discovered.append(server_info)
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            logger.error(f"Error scanning local processes: {e}")
        
        return discovered
    
    async def _discover_docker_containers(self) -> List[Dict[str, Any]]:
        """Discover MCP servers running in Docker containers"""
        discovered = []
        
        if not self.docker_client:
            return discovered
        
        try:
            containers = self.docker_client.containers.list()
            
            for container in containers:
                try:
                    # Check container labels and environment
                    labels = container.labels
                    env_vars = container.attrs.get('Config', {}).get('Env', [])
                    
                    if self._is_mcp_container(labels, env_vars):
                        server_info = self._extract_server_info_from_container(container)
                        if server_info:
                            discovered.append(server_info)
                            
                except Exception as e:
                    logger.error(f"Error processing container {container.id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scanning Docker containers: {e}")
        
        return discovered
    
    async def _discover_network_services(
        self,
        network_ranges: List[str],
        ports: List[int]
    ) -> List[Dict[str, Any]]:
        """Discover MCP servers on the network"""
        discovered = []
        
        # Network scanning implementation
        # This is a placeholder for network discovery
        # In production, use proper network scanning libraries
        
        logger.info(f"Network scanning not fully implemented yet")
        return discovered
    
    def _is_mcp_process(self, cmdline: List[str]) -> bool:
        """Check if process is an MCP server"""
        if not cmdline:
            return False
        
        cmdline_str = ' '.join(cmdline).lower()
        
        # Look for MCP-related keywords
        mcp_keywords = [
            'mcp-server',
            'mcp_server',
            'mcpserver',
            'model-context-protocol',
            '--mcp',
            'mcp.json'
        ]
        
        return any(keyword in cmdline_str for keyword in mcp_keywords)
    
    def _is_mcp_container(self, labels: Dict[str, str], env_vars: List[str]) -> bool:
        """Check if Docker container is an MCP server"""
        # Check labels
        if any('mcp' in key.lower() or 'mcp' in value.lower() 
               for key, value in labels.items()):
            return True
        
        # Check environment variables
        env_str = ' '.join(env_vars).lower()
        return 'mcp' in env_str
    
    def _extract_server_info_from_process(
        self,
        proc_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extract MCP server information from process info"""
        try:
            cmdline = proc_info.get('cmdline', [])
            connections = proc_info.get('connections', [])
            
            # Determine protocol and port
            protocol = ProtocolType.STDIO
            port = None
            host = "localhost"
            
            # Check for network connections
            if connections:
                for conn in connections:
                    if conn.status == 'LISTEN':
                        port = conn.laddr.port
                        protocol = ProtocolType.HTTP
                        break
            
            return {
                "name": f"Local MCP Server (PID: {proc_info['pid']})",
                "description": f"MCP server running as local process",
                "protocol": protocol,
                "host": host,
                "port": port,
                "path": ' '.join(cmdline) if cmdline else None,
                "discovered_by": "local_scan",
                "discovery_metadata": {
                    "pid": proc_info['pid'],
                    "process_name": proc_info.get('name'),
                    "cmdline": cmdline
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting process info: {e}")
            return None
    
    def _extract_server_info_from_container(
        self,
        container: Any
    ) -> Optional[Dict[str, Any]]:
        """Extract MCP server information from Docker container"""
        try:
            name = container.name
            labels = container.labels
            ports = container.attrs.get('NetworkSettings', {}).get('Ports', {})
            
            # Determine protocol and port
            protocol = ProtocolType.HTTP
            port = None
            host = "localhost"
            
            # Extract port from container ports
            for container_port, host_bindings in ports.items():
                if host_bindings:
                    port = int(host_bindings[0]['HostPort'])
                    break
            
            return {
                "name": f"Docker MCP Server ({name})",
                "description": f"MCP server running in Docker container",
                "protocol": protocol,
                "host": host,
                "port": port,
                "discovered_by": "docker_scan",
                "discovery_metadata": {
                    "container_id": container.id,
                    "container_name": name,
                    "image": container.image.tags[0] if container.image.tags else None,
                    "labels": labels
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting container info: {e}")
            return None
    
    async def _find_existing_server(
        self,
        db: AsyncSession,
        server_data: Dict[str, Any]
    ) -> Optional[MCPServer]:
        """Find existing server in database"""
        try:
            # Try to find by host and port
            if server_data.get("host") and server_data.get("port"):
                result = await db.execute(
                    select(MCPServer).where(
                        MCPServer.host == server_data["host"],
                        MCPServer.port == server_data["port"]
                    )
                )
                return result.scalar_one_or_none()
            
            # Try to find by name
            result = await db.execute(
                select(MCPServer).where(
                    MCPServer.name == server_data["name"]
                )
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error finding existing server: {e}")
            return None
    
    async def health_check_server(
        self,
        db: AsyncSession,
        server_id: int,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Perform health check on a specific MCP server
        
        Args:
            db: Database session
            server_id: Server ID
            timeout: Timeout in seconds
            
        Returns:
            Health check results
        """
        start_time = datetime.utcnow()
        
        try:
            # Get server from database
            result = await db.execute(
                select(MCPServer).where(MCPServer.id == server_id)
            )
            server = result.scalar_one_or_none()
            
            if not server:
                raise ValueError(f"Server {server_id} not found")
            
            # Perform health check based on protocol
            if server.protocol == ProtocolType.HTTP or server.protocol == ProtocolType.HTTPS:
                status, response_time, error = await self._http_health_check(
                    server.host,
                    server.port,
                    server.protocol == ProtocolType.HTTPS,
                    timeout
                )
            elif server.protocol == ProtocolType.STDIO:
                status, response_time, error = await self._stdio_health_check(
                    server.path,
                    timeout
                )
            else:
                status = ServerStatus.UNKNOWN
                response_time = 0
                error = "Unsupported protocol"
            
            # Update server status
            server.status = status
            server.last_health_check = datetime.utcnow()
            if status == ServerStatus.ONLINE:
                server.last_seen = datetime.utcnow()
            
            await db.commit()
            
            end_time = datetime.utcnow()
            
            return {
                "server_id": server_id,
                "status": status,
                "response_time_ms": response_time,
                "error": error,
                "checked_at": end_time
            }
            
        except Exception as e:
            logger.error(f"Health check error for server {server_id}: {e}")
            await db.rollback()
            raise
    
    async def _http_health_check(
        self,
        host: str,
        port: int,
        use_https: bool,
        timeout: int
    ) -> tuple[ServerStatus, float, Optional[str]]:
        """Perform HTTP/HTTPS health check"""
        import aiohttp
        
        protocol = "https" if use_https else "http"
        url = f"{protocol}://{host}:{port}/health"
        
        try:
            start = datetime.utcnow()
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    end = datetime.utcnow()
                    response_time = (end - start).total_seconds() * 1000
                    
                    if response.status == 200:
                        return ServerStatus.ONLINE, response_time, None
                    else:
                        return ServerStatus.DEGRADED, response_time, f"HTTP {response.status}"
                        
        except asyncio.TimeoutError:
            return ServerStatus.OFFLINE, 0, "Timeout"
        except Exception as e:
            return ServerStatus.OFFLINE, 0, str(e)
    
    async def _stdio_health_check(
        self,
        path: str,
        timeout: int
    ) -> tuple[ServerStatus, float, Optional[str]]:
        """Perform STDIO health check"""
        try:
            # Check if process is running
            # This is a simplified check
            return ServerStatus.UNKNOWN, 0, "STDIO health check not fully implemented"
            
        except Exception as e:
            return ServerStatus.OFFLINE, 0, str(e)
