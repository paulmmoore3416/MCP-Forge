"""
SQLAlchemy models for MCP Server management
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, JSON, Enum as SQLEnum, Text, Boolean, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ProtocolType(str, enum.Enum):
    """MCP Server protocol types"""
    STDIO = "stdio"
    SSE = "sse"
    HTTP = "http"
    HTTPS = "https"


class ServerStatus(str, enum.Enum):
    """MCP Server status"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"
    DISCOVERING = "discovering"


class MCPServer(Base):
    """
    MCP Server model representing a discovered or registered MCP server
    """
    __tablename__ = "mcp_servers"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Basic information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Connection details
    protocol: Mapped[ProtocolType] = mapped_column(
        SQLEnum(ProtocolType, name="protocol_type"),
        nullable=False,
        index=True
    )
    host: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    # Status and health
    status: Mapped[ServerStatus] = mapped_column(
        SQLEnum(ServerStatus, name="server_status"),
        default=ServerStatus.UNKNOWN,
        nullable=False,
        index=True
    )
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_health_check: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    health_check_interval: Mapped[int] = mapped_column(Integer, default=300)  # seconds
    
    # Discovery information
    discovered_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'auto', 'manual', 'docker', etc.
    discovery_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Capabilities (stored as JSON)
    capabilities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Configuration
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    environment: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    server_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_managed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Managed by MCP Forge
    auto_restart: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    tools: Mapped[list["MCPTool"]] = relationship(
        "MCPTool",
        back_populates="server",
        cascade="all, delete-orphan"
    )
    resources: Mapped[list["MCPResource"]] = relationship(
        "MCPResource",
        back_populates="server",
        cascade="all, delete-orphan"
    )
    prompts: Mapped[list["MCPPrompt"]] = relationship(
        "MCPPrompt",
        back_populates="server",
        cascade="all, delete-orphan"
    )
    connections: Mapped[list["MCPConnection"]] = relationship(
        "MCPConnection",
        back_populates="server",
        cascade="all, delete-orphan"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_server_status_active', 'status', 'is_active'),
        Index('idx_server_protocol_status', 'protocol', 'status'),
        Index('idx_server_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<MCPServer(id={self.id}, name='{self.name}', protocol={self.protocol}, status={self.status})>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "protocol": self.protocol.value,
            "host": self.host,
            "port": self.port,
            "path": self.path,
            "status": self.status.value,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "discovered_by": self.discovered_by,
            "capabilities": self.capabilities,
            "version": self.version,
            "tags": self.tags,
            "is_active": self.is_active,
            "is_managed": self.is_managed,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class MCPTool(Base):
    """
    MCP Tool model representing a tool provided by an MCP server
    """
    __tablename__ = "mcp_tools"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    server_id: Mapped[int] = mapped_column(Integer, ForeignKey("mcp_servers.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    schema: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    input_schema: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    examples: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    server: Mapped["MCPServer"] = relationship("MCPServer", back_populates="tools")
    
    __table_args__ = (
        Index('idx_tool_server_name', 'server_id', 'name'),
    )
    
    def __repr__(self) -> str:
        return f"<MCPTool(id={self.id}, name='{self.name}', server_id={self.server_id})>"


class MCPResource(Base):
    """
    MCP Resource model representing a resource provided by an MCP server
    """
    __tablename__ = "mcp_resources"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    server_id: Mapped[int] = mapped_column(Integer, ForeignKey("mcp_servers.id"), nullable=False, index=True)
    
    uri: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Metadata
    resource_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    server: Mapped["MCPServer"] = relationship("MCPServer", back_populates="resources")
    
    __table_args__ = (
        Index('idx_resource_server_uri', 'server_id', 'uri'),
    )
    
    def __repr__(self) -> str:
        return f"<MCPResource(id={self.id}, uri='{self.uri}', server_id={self.server_id})>"


class MCPPrompt(Base):
    """
    MCP Prompt model representing a prompt template provided by an MCP server
    """
    __tablename__ = "mcp_prompts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    server_id: Mapped[int] = mapped_column(Integer, ForeignKey("mcp_servers.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Prompt details
    arguments: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    examples: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    server: Mapped["MCPServer"] = relationship("MCPServer", back_populates="prompts")
    
    __table_args__ = (
        Index('idx_prompt_server_name', 'server_id', 'name'),
    )
    
    def __repr__(self) -> str:
        return f"<MCPPrompt(id={self.id}, name='{self.name}', server_id={self.server_id})>"


class MCPConnection(Base):
    """
    MCP Connection model representing a connection between an agent and an MCP server
    """
    __tablename__ = "mcp_connections"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    server_id: Mapped[int] = mapped_column(Integer, ForeignKey("mcp_servers.id"), nullable=False, index=True)
    
    # Agent/Client information
    agent_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    agent_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    agent_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Connection details
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    conn_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Statistics
    request_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    last_request_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    connected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    disconnected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    server: Mapped["MCPServer"] = relationship("MCPServer", back_populates="connections")
    
    __table_args__ = (
        Index('idx_connection_server_agent', 'server_id', 'agent_id'),
        Index('idx_connection_status', 'status'),
    )
    
    def __repr__(self) -> str:
        return f"<MCPConnection(id={self.id}, server_id={self.server_id}, agent_id='{self.agent_id}', status='{self.status}')>"
