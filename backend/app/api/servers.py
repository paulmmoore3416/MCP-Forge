"""
API endpoints for MCP Server management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from datetime import datetime

from app.database import get_db
from app.models.mcp_server import MCPServer, ServerStatus, ProtocolType
from app.schemas.mcp_server import (
    MCPServerCreate,
    MCPServerUpdate,
    MCPServerResponse,
    MCPServerList,
    HealthCheckResponse,
    DiscoveryRequest,
    DiscoveryResponse,
    SystemStatistics
)
from app.services.discovery import MCPDiscoveryService

router = APIRouter()


@router.get("", response_model=MCPServerList)
async def list_servers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[ServerStatus] = Query(None, description="Filter by status"),
    protocol: Optional[ProtocolType] = Query(None, description="Filter by protocol"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all MCP servers with pagination and filtering
    """
    try:
        # Build query
        query = select(MCPServer)
        
        # Apply filters
        if status:
            query = query.where(MCPServer.status == status)
        if protocol:
            query = query.where(MCPServer.protocol == protocol)
        if is_active is not None:
            query = query.where(MCPServer.is_active == is_active)
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    MCPServer.name.ilike(search_pattern),
                    MCPServer.description.ilike(search_pattern)
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(MCPServer.created_at.desc())
        
        # Execute query
        result = await db.execute(query)
        servers = result.scalars().all()
        
        # Calculate pages
        pages = (total + page_size - 1) // page_size
        
        return MCPServerList(
            items=[MCPServerResponse.model_validate(server) for server in servers],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing servers: {str(e)}"
        )


@router.get("/{server_id}", response_model=MCPServerResponse)
async def get_server(
    server_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific MCP server by ID
    """
    try:
        result = await db.execute(
            select(MCPServer).where(MCPServer.id == server_id)
        )
        server = result.scalar_one_or_none()
        
        if not server:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Server {server_id} not found"
            )
        
        return MCPServerResponse.model_validate(server)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving server: {str(e)}"
        )


@router.post("", response_model=MCPServerResponse, status_code=http_status.HTTP_201_CREATED)
async def create_server(
    server_data: MCPServerCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new MCP server
    """
    try:
        # Check if server with same name exists
        existing = await db.execute(
            select(MCPServer).where(MCPServer.name == server_data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=f"Server with name '{server_data.name}' already exists"
            )
        
        # Create new server
        new_server = MCPServer(
            name=server_data.name,
            description=server_data.description,
            protocol=server_data.protocol,
            host=server_data.host,
            port=server_data.port,
            path=server_data.path,
            tags=server_data.tags,
            config=server_data.config,
            environment=server_data.environment,
            auto_restart=server_data.auto_restart,
            discovered_by=server_data.discovered_by,
            discovery_metadata=server_data.discovery_metadata,
            status=ServerStatus.UNKNOWN
        )
        
        db.add(new_server)
        await db.commit()
        await db.refresh(new_server)
        
        return MCPServerResponse.model_validate(new_server)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating server: {str(e)}"
        )


@router.patch("/{server_id}", response_model=MCPServerResponse)
async def update_server(
    server_id: int,
    server_data: MCPServerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing MCP server
    """
    try:
        # Get existing server
        result = await db.execute(
            select(MCPServer).where(MCPServer.id == server_id)
        )
        server = result.scalar_one_or_none()
        
        if not server:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Server {server_id} not found"
            )
        
        # Update fields
        update_data = server_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(server, field, value)
        
        server.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(server)
        
        return MCPServerResponse.model_validate(server)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating server: {str(e)}"
        )


@router.delete("/{server_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an MCP server
    """
    try:
        # Get existing server
        result = await db.execute(
            select(MCPServer).where(MCPServer.id == server_id)
        )
        server = result.scalar_one_or_none()
        
        if not server:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Server {server_id} not found"
            )
        
        await db.delete(server)
        await db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting server: {str(e)}"
        )


@router.post("/{server_id}/health-check", response_model=HealthCheckResponse)
async def health_check_server(
    server_id: int,
    timeout: int = Query(30, ge=1, le=300, description="Timeout in seconds"),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform health check on a specific MCP server
    """
    try:
        discovery_service = MCPDiscoveryService()
        result = await discovery_service.health_check_server(db, server_id, timeout)
        
        return HealthCheckResponse(
            server_id=result["server_id"],
            status=result["status"],
            response_time_ms=result["response_time_ms"],
            error=result.get("error"),
            checked_at=result["checked_at"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing health check: {str(e)}"
        )


@router.post("/discover", response_model=DiscoveryResponse)
async def discover_servers(
    discovery_request: DiscoveryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Discover MCP servers using various methods
    """
    try:
        discovery_service = MCPDiscoveryService()
        result = await discovery_service.discover_all(
            db=db,
            scan_local=discovery_request.scan_local,
            scan_docker=discovery_request.scan_docker,
            scan_network=discovery_request.scan_network,
            network_ranges=discovery_request.network_ranges,
            ports=discovery_request.ports
        )
        
        # Get discovered servers from database
        server_ids = [s.get("id") for s in result["servers"] if s.get("id")]
        servers = []
        
        if server_ids:
            result_query = await db.execute(
                select(MCPServer).where(MCPServer.id.in_(server_ids))
            )
            servers = result_query.scalars().all()
        
        return DiscoveryResponse(
            discovered_count=result["discovered_count"],
            servers=[MCPServerResponse.model_validate(s) for s in servers],
            scan_duration_seconds=result["scan_duration_seconds"],
            scan_timestamp=result["scan_timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during discovery: {str(e)}"
        )


@router.get("/statistics/system", response_model=SystemStatistics)
async def get_system_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    Get system-wide statistics
    """
    try:
        # Count servers by status
        total_servers_result = await db.execute(select(func.count(MCPServer.id)))
        total_servers = total_servers_result.scalar()
        
        online_result = await db.execute(
            select(func.count(MCPServer.id)).where(MCPServer.status == ServerStatus.ONLINE)
        )
        online_servers = online_result.scalar()
        
        offline_result = await db.execute(
            select(func.count(MCPServer.id)).where(MCPServer.status == ServerStatus.OFFLINE)
        )
        offline_servers = offline_result.scalar()
        
        degraded_result = await db.execute(
            select(func.count(MCPServer.id)).where(MCPServer.status == ServerStatus.DEGRADED)
        )
        degraded_servers = degraded_result.scalar()
        
        # Count tools, resources, prompts (placeholder - will be implemented when those models are queried)
        total_tools = 0
        total_resources = 0
        total_prompts = 0
        total_connections = 0
        active_connections = 0
        
        return SystemStatistics(
            total_servers=total_servers,
            online_servers=online_servers,
            offline_servers=offline_servers,
            degraded_servers=degraded_servers,
            total_tools=total_tools,
            total_resources=total_resources,
            total_prompts=total_prompts,
            total_connections=total_connections,
            active_connections=active_connections
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )
