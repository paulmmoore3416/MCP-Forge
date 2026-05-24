"""
Pydantic schemas for MCP Server management
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ProtocolType(str, Enum):
    """MCP Server protocol types"""
    STDIO = "stdio"
    SSE = "sse"
    HTTP = "http"
    HTTPS = "https"


class ServerStatus(str, Enum):
    """MCP Server status"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"
    DISCOVERING = "discovering"


# Base schemas
class MCPServerBase(BaseModel):
    """Base schema for MCP Server"""
    name: str = Field(..., min_length=1, max_length=255, description="Server name")
    description: Optional[str] = Field(None, description="Server description")
    protocol: ProtocolType = Field(..., description="Communication protocol")
    host: Optional[str] = Field(None, max_length=255, description="Server host")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Server port")
    path: Optional[str] = Field(None, max_length=512, description="Server path")
    tags: Optional[List[str]] = Field(None, description="Server tags")
    config: Optional[Dict[str, Any]] = Field(None, description="Server configuration")
    environment: Optional[Dict[str, Any]] = Field(None, description="Environment variables")
    auto_restart: bool = Field(False, description="Auto-restart on failure")


class MCPServerCreate(MCPServerBase):
    """Schema for creating a new MCP Server"""
    discovered_by: Optional[str] = Field("manual", max_length=50, description="Discovery method")
    discovery_metadata: Optional[Dict[str, Any]] = Field(None, description="Discovery metadata")


class MCPServerUpdate(BaseModel):
    """Schema for updating an MCP Server"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    host: Optional[str] = Field(None, max_length=255)
    port: Optional[int] = Field(None, ge=1, le=65535)
    path: Optional[str] = Field(None, max_length=512)
    status: Optional[ServerStatus] = None
    tags: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    environment: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    auto_restart: Optional[bool] = None
    
    model_config = ConfigDict(extra="forbid")


class MCPServerResponse(MCPServerBase):
    """Schema for MCP Server response"""
    id: int
    status: ServerStatus
    last_seen: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    health_check_interval: int
    discovered_by: Optional[str] = None
    discovery_metadata: Optional[Dict[str, Any]] = None
    capabilities: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    server_metadata: Optional[Dict[str, Any]] = None
    is_active: bool
    is_managed: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MCPServerList(BaseModel):
    """Schema for paginated list of MCP Servers"""
    items: List[MCPServerResponse]
    total: int
    page: int
    page_size: int
    pages: int


# Tool schemas
class MCPToolBase(BaseModel):
    """Base schema for MCP Tool"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None
    input_schema: Optional[Dict[str, Any]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None


class MCPToolCreate(MCPToolBase):
    """Schema for creating a new MCP Tool"""
    server_id: int


class MCPToolResponse(MCPToolBase):
    """Schema for MCP Tool response"""
    id: int
    server_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Resource schemas
class MCPResourceBase(BaseModel):
    """Base schema for MCP Resource"""
    uri: str = Field(..., min_length=1, max_length=512)
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    mime_type: Optional[str] = Field(None, max_length=100)
    resource_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class MCPResourceCreate(MCPResourceBase):
    """Schema for creating a new MCP Resource"""
    server_id: int


class MCPResourceResponse(MCPResourceBase):
    """Schema for MCP Resource response"""
    id: int
    server_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Prompt schemas
class MCPPromptBase(BaseModel):
    """Base schema for MCP Prompt"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    arguments: Optional[List[Dict[str, Any]]] = None
    template: Optional[str] = None
    examples: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None


class MCPPromptCreate(MCPPromptBase):
    """Schema for creating a new MCP Prompt"""
    server_id: int


class MCPPromptResponse(MCPPromptBase):
    """Schema for MCP Prompt response"""
    id: int
    server_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Connection schemas
class MCPConnectionBase(BaseModel):
    """Base schema for MCP Connection"""
    agent_id: str = Field(..., min_length=1, max_length=255)
    agent_name: Optional[str] = Field(None, max_length=255)
    agent_type: Optional[str] = Field(None, max_length=100)
    conn_metadata: Optional[Dict[str, Any]] = None


class MCPConnectionCreate(MCPConnectionBase):
    """Schema for creating a new MCP Connection"""
    server_id: int


class MCPConnectionResponse(MCPConnectionBase):
    """Schema for MCP Connection response"""
    id: int
    server_id: int
    status: str
    request_count: int
    error_count: int
    last_request_at: Optional[datetime] = None
    connected_at: datetime
    disconnected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Health check schemas
class HealthCheckRequest(BaseModel):
    """Schema for health check request"""
    server_id: int
    timeout: Optional[int] = Field(30, ge=1, le=300, description="Timeout in seconds")


class HealthCheckResponse(BaseModel):
    """Schema for health check response"""
    server_id: int
    status: ServerStatus
    response_time_ms: float
    capabilities: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    error: Optional[str] = None
    checked_at: datetime


# Discovery schemas
class DiscoveryRequest(BaseModel):
    """Schema for discovery request"""
    scan_local: bool = Field(True, description="Scan local processes")
    scan_docker: bool = Field(True, description="Scan Docker containers")
    scan_network: bool = Field(False, description="Scan network")
    network_ranges: Optional[List[str]] = Field(None, description="Network ranges to scan (CIDR)")
    ports: Optional[List[int]] = Field(None, description="Ports to scan")


class DiscoveryResponse(BaseModel):
    """Schema for discovery response"""
    discovered_count: int
    servers: List[MCPServerResponse]
    scan_duration_seconds: float
    scan_timestamp: datetime


# Statistics schemas
class ServerStatistics(BaseModel):
    """Schema for server statistics"""
    server_id: int
    total_connections: int
    active_connections: int
    total_requests: int
    total_errors: int
    error_rate: float
    avg_response_time_ms: Optional[float] = None
    uptime_percentage: float
    last_24h_requests: int


class SystemStatistics(BaseModel):
    """Schema for system-wide statistics"""
    total_servers: int
    online_servers: int
    offline_servers: int
    degraded_servers: int
    total_tools: int
    total_resources: int
    total_prompts: int
    total_connections: int
    active_connections: int
