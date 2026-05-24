# MCP Forge - Implementation Roadmap

**Version:** 1.0.0  
**Status:** Ready for Implementation  
**Estimated Timeline:** 10 weeks

---

## 📋 Overview

This roadmap provides a detailed, step-by-step guide for implementing MCP Forge from initial setup to production deployment. Each phase includes specific tasks, code examples, and success criteria.

---

## 🎯 Phase 1: Project Foundation & Infrastructure (Week 1-2)

### Objectives
- Set up development environment
- Initialize project structure
- Configure Docker and databases
- Establish Git workflow

### Tasks

#### 1.1 Initialize Next.js Frontend

```bash
# Create project directory
mkdir mcp-forge && cd mcp-forge

# Initialize Next.js with TypeScript
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

cd frontend

# Install core dependencies
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-select
npm install @radix-ui/react-tabs @radix-ui/react-toast @radix-ui/react-tooltip
npm install lucide-react class-variance-authority clsx tailwind-merge
npm install react-flow-renderer recharts
npm install next-auth@beta
npm install swr axios socket.io-client
npm install zod react-hook-form @hookform/resolvers

# Install dev dependencies
npm install -D @types/node @types/react @types/react-dom
npm install -D prettier prettier-plugin-tailwindcss
```

**File: `frontend/tailwind.config.ts`**
```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // GitHub-inspired dark theme
        background: {
          primary: '#0d1117',
          secondary: '#161b22',
          tertiary: '#21262d',
        },
        border: {
          DEFAULT: '#30363d',
          muted: '#21262d',
        },
        text: {
          primary: '#c9d1d9',
          secondary: '#8b949e',
          muted: '#6e7681',
        },
        accent: {
          DEFAULT: '#58a6ff',
          hover: '#79c0ff',
        },
        success: '#3fb950',
        warning: '#d29922',
        error: '#f85149',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'Cascadia Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
export default config
```

**File: `frontend/src/app/globals.css`**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 13 17 23;
    --foreground: 201 209 217;
  }

  * {
    @apply border-border;
  }

  body {
    @apply bg-background-primary text-text-primary;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
}

@layer components {
  .github-card {
    @apply rounded-lg border border-border bg-background-secondary p-4;
  }

  .github-button {
    @apply rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover transition-colors;
  }

  .github-input {
    @apply rounded-md border border-border bg-background-tertiary px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:border-accent focus:outline-none;
  }
}
```

#### 1.2 Initialize Python FastAPI Backend

```bash
# Create backend directory
mkdir backend && cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << EOF
# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Cache & Queue
redis==5.0.1
celery==5.3.6

# MCP SDK
# Note: Replace with official SDK when available
# For now, we'll create a wrapper

# Auth & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# WebSocket
python-socketio==5.11.0

# Utilities
python-dotenv==1.0.0
httpx==0.26.0
tenacity==8.2.3

# Monitoring
prometheus-client==0.19.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0
EOF

# Install dependencies
pip install -r requirements.txt

# Create project structure
mkdir -p app/{api,models,schemas,services,middleware,utils}
touch app/__init__.py
touch app/{api,models,schemas,services,middleware,utils}/__init__.py
```

**File: `backend/app/config.py`**
```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "MCP Forge"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # MCP Discovery
    DISCOVERY_INTERVAL_SECONDS: int = 300  # 5 minutes
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

**File: `backend/app/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.database import engine, Base
from app.api import mcps, agents, auth, security, metrics

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","service":"mcp-forge-backend","message":"%(message)s"}',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting MCP Forge Backend")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start background tasks (discovery, etc.)
    # TODO: Initialize Celery tasks
    
    yield
    
    # Shutdown
    logger.info("Shutting down MCP Forge Backend")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}

@app.get("/ready")
async def readiness_check():
    # TODO: Check database, redis, etc.
    return {"status": "ready"}

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(mcps.router, prefix=f"{settings.API_V1_PREFIX}/mcps", tags=["mcps"])
app.include_router(agents.router, prefix=f"{settings.API_V1_PREFIX}/agents", tags=["agents"])
app.include_router(security.router, prefix=f"{settings.API_V1_PREFIX}/security", tags=["security"])
app.include_router(metrics.router, prefix=f"{settings.API_V1_PREFIX}/metrics", tags=["metrics"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
```

#### 1.3 Database Setup

**File: `backend/app/database.py`**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


# Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

**File: `backend/alembic.ini`**
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = postgresql+asyncpg://postgres:password@localhost:5432/mcpforge

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

```bash
# Initialize Alembic
alembic init alembic

# Edit alembic/env.py to use async engine
# Then create first migration
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

#### 1.4 Docker Configuration

**File: `docker-compose.yml`** (root directory)
```yaml
version: '3.9'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NEXTAUTH_URL=http://localhost:3000
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    command: npm run dev

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@db:5432/mcpforge
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=true
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=mcpforge
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@db:5432/mcpforge
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app

volumes:
  postgres_data:
  redis_data:
```

**File: `frontend/Dockerfile`**
```dockerfile
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

# Development image
FROM base AS dev
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

EXPOSE 3000
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["npm", "run", "dev"]

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm run build

USER nextjs

EXPOSE 3000
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["npm", "start"]
```

**File: `backend/Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 1.5 Environment Configuration

**File: `.env.example`** (root directory)
```bash
# Database
DB_PASSWORD=your_secure_password_here

# Backend
SECRET_KEY=your_secret_key_here_min_32_chars
JWT_SECRET=your_jwt_secret_here

# Frontend
NEXTAUTH_SECRET=your_nextauth_secret_here
NEXTAUTH_URL=http://localhost:3000

# OAuth (optional)
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Development
DEBUG=true
```

**File: `.gitignore`** (root directory)
```
# Environment
.env
.env.local
.env.*.local

# Dependencies
node_modules/
venv/
__pycache__/
*.pyc

# Build outputs
.next/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# Docker
docker-compose.override.yml

# Testing
.coverage
htmlcov/
.pytest_cache/
```

#### 1.6 Initialize Git Repository

```bash
# Initialize Git
git init

# Create initial commit
git add .
git commit -m "Initial commit: Project foundation"

# Create develop branch
git checkout -b develop

# Set up GitHub repository (if needed)
# git remote add origin https://github.com/yourusername/mcp-forge.git
# git push -u origin main
# git push -u origin develop
```

### Success Criteria
- ✅ Next.js project runs on `http://localhost:3000`
- ✅ FastAPI backend runs on `http://localhost:8000`
- ✅ PostgreSQL accessible on port 5432
- ✅ Redis accessible on port 6379
- ✅ Docker Compose starts all services successfully
- ✅ Health check endpoints return 200 OK
- ✅ Git repository initialized with proper structure

---

## 🔧 Phase 2: Backend Core - MCP Discovery & API (Week 3-4)

### Objectives
- Implement database models
- Create MCP discovery service
- Build REST API endpoints
- Add WebSocket support

### Tasks

#### 2.1 Database Models

**File: `backend/app/models/mcp_server.py`**
```python
from sqlalchemy import Column, String, Boolean, Integer, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class MCPServer(Base):
    __tablename__ = "mcp_servers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    endpoint = Column(String(512), nullable=False, unique=True)
    protocol = Column(String(50), nullable=False)  # stdio, sse, http, https
    status = Column(String(50), nullable=False)  # healthy, degraded, down, unknown
    version = Column(String(50))
    description = Column(Text)
    
    # Capabilities stored as JSON
    capabilities = Column(JSON)  # {tools: [], resources: [], prompts: []}
    
    # Security
    auth_type = Column(String(50))  # none, oauth, jwt, mtls
    mtls_enabled = Column(Boolean, default=False)
    
    # Metadata
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_health_check = Column(DateTime(timezone=True))
    
    # Configuration
    config = Column(JSON)
    tags = Column(JSON)  # ['production', 'development', etc.]
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<MCPServer(name='{self.name}', endpoint='{self.endpoint}', status='{self.status}')>"
```

**File: `backend/app/models/agent.py`**
```python
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)  # claude, gpt, custom, etc.
    version = Column(String(50))
    status = Column(String(50), nullable=False)
    
    # Configuration
    config = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Agent(name='{self.name}', type='{self.type}')>"
```

**File: `backend/app/models/connection.py`**
```python
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class MCPAgentConnection(Base):
    __tablename__ = "mcp_agent_connections"
    __table_args__ = (
        UniqueConstraint('mcp_server_id', 'agent_id', name='unique_connection'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mcp_server_id = Column(UUID(as_uuid=True), ForeignKey('mcp_servers.id', ondelete='CASCADE'), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id', ondelete='CASCADE'), nullable=False)
    
    status = Column(String(50), nullable=False)  # active, inactive, error
    
    # Usage metrics
    total_requests = Column(Integer, default=0)
    total_errors = Column(Integer, default=0)
    last_request_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    mcp_server = relationship("MCPServer", backref="connections")
    agent = relationship("Agent", backref="connections")

    def __repr__(self):
        return f"<MCPAgentConnection(mcp_server_id='{self.mcp_server_id}', agent_id='{self.agent_id}')>"
```

#### 2.2 Pydantic Schemas

**File: `backend/app/schemas/mcp_server.py`**
```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class MCPServerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    endpoint: str = Field(..., min_length=1, max_length=512)
    protocol: str = Field(..., pattern="^(stdio|sse|http|https)$")
    description: Optional[str] = None
    auth_type: Optional[str] = Field(None, pattern="^(none|oauth|jwt|mtls)$")
    mtls_enabled: bool = False
    config: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class MCPServerCreate(MCPServerBase):
    pass


class MCPServerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = Field(None, pattern="^(healthy|degraded|down|unknown)$")


class MCPServerResponse(MCPServerBase):
    id: UUID
    status: str
    version: Optional[str]
    capabilities: Optional[Dict[str, List[str]]]
    discovered_at: datetime
    last_seen_at: datetime
    last_health_check: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MCPServerList(BaseModel):
    items: List[MCPServerResponse]
    total: int
    page: int
    page_size: int
```

#### 2.3 MCP Discovery Service

**File: `backend/app/services/discovery.py`**
```python
import asyncio
import logging
from typing import List, Dict, Any
import subprocess
import json

from app.models.mcp_server import MCPServer
from app.database import AsyncSessionLocal
from sqlalchemy import select

logger = logging.getLogger(__name__)


class MCPDiscoveryService:
    """Service for discovering MCP servers across different environments"""
    
    def __init__(self):
        self.discovered_servers: List[Dict[str, Any]] = []
    
    async def discover_all(self) -> List[Dict[str, Any]]:
        """Run all discovery methods"""
        logger.info("Starting MCP discovery scan")
        
        tasks = [
            self.discover_local_processes(),
            self.discover_docker_containers(),
            self.discover_network_services(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_servers = []
        for result in results:
            if isinstance(result, list):
                all_servers.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Discovery error: {result}")
        
        logger.info(f"Discovery complete. Found {len(all_servers)} MCP servers")
        return all_servers
    
    async def discover_local_processes(self) -> List[Dict[str, Any]]:
        """Discover MCP servers running as local processes"""
        servers = []
        
        try:
            # Search for processes with 'mcp' in command line
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if 'mcp' in line.lower() and 'server' in line.lower():
                    # Parse process info and extract MCP server details
                    # This is a simplified example
                    servers.append({
                        'name': 'Local MCP Server',
                        'endpoint': 'stdio://local',
                        'protocol': 'stdio',
                        'status': 'unknown',
                        'discovered_method': 'process_scan'
                    })
        
        except Exception as e:
            logger.error(f"Error discovering local processes: {e}")
        
        return servers
    
    async def discover_docker_containers(self) -> List[Dict[str, Any]]:
        """Discover MCP servers running in Docker containers"""
        servers = []
        
        try:
            # List Docker containers with MCP label
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                container = json.loads(line)
                
                # Check if container is an MCP server
                if 'mcp' in container.get('Names', '').lower():
                    servers.append({
                        'name': container['Names'],
                        'endpoint': f"http://{container.get('Ports', 'unknown')}",
                        'protocol': 'http',
                        'status': 'healthy' if container['State'] == 'running' else 'down',
                        'discovered_method': 'docker_scan'
                    })
        
        except FileNotFoundError:
            logger.warning("Docker not installed or not in PATH")
        except Exception as e:
            logger.error(f"Error discovering Docker containers: {e}")
        
        return servers
    
    async def discover_network_services(self) -> List[Dict[str, Any]]:
        """Discover MCP servers on the network"""
        servers = []
        
        # TODO: Implement network scanning
        # - Check common MCP ports
        # - Use service discovery (mDNS, Consul, etc.)
        # - Probe known endpoints
        
        return servers
    
    async def probe_server(self, endpoint: str) -> Dict[str, Any]:
        """Probe an MCP server to get its capabilities"""
        # TODO: Implement MCP client probing
        # - Connect to server
        # - Fetch capabilities
        # - Get version info
        # - Check health
        
        return {
            'capabilities': {
                'tools': [],
                'resources': [],
                'prompts': []
            },
            'version': 'unknown',
            'health': 'unknown'
        }
    
    async def save_discovered_servers(self, servers: List[Dict[str, Any]]):
        """Save discovered servers to database"""
        async with AsyncSessionLocal() as session:
            for server_data in servers:
                # Check if server already exists
                stmt = select(MCPServer).where(MCPServer.endpoint == server_data['endpoint'])
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    # Update last_seen_at
                    existing.last_seen_at = func.now()
                    existing.status = server_data.get('status', 'unknown')
                else:
                    # Create new server
                    new_server = MCPServer(
                        name=server_data['name'],
                        endpoint=server_data['endpoint'],
                        protocol=server_data['protocol'],
                        status=server_data.get('status', 'unknown'),
                    )
                    session.add(new_server)
            
            await session.commit()


# Background task for periodic discovery
async def periodic_discovery_task():
    """Run discovery periodically"""
    discovery_service = MCPDiscoveryService()
    
    while True:
        try:
            servers = await discovery_service.discover_all()
            await discovery_service.save_discovered_servers(servers)
        except Exception as e:
            logger.error(f"Error in periodic discovery: {e}")
        
        # Wait 5 minutes before next scan
        await asyncio.sleep(300)
```

#### 2.4 API Endpoints

**File: `backend/app/api/mcps.py`**
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.mcp_server import MCPServer
from app.schemas.mcp_server import (
    MCPServerCreate,
    MCPServerUpdate,
    MCPServerResponse,
    MCPServerList
)
from app.services.discovery import MCPDiscoveryService

router = APIRouter()


@router.get("/", response_model=MCPServerList)
async def list_mcp_servers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    protocol: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all MCP servers with pagination and filters"""
    
    # Build query
    query = select(MCPServer)
    
    if status:
        query = query.where(MCPServer.status == status)
    if protocol:
        query = query.where(MCPServer.protocol == protocol)
    if search:
        query = query.where(
            (MCPServer.name.ilike(f"%{search}%")) |
            (MCPServer.endpoint.ilike(f"%{search}%"))
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    servers = result.scalars().all()
    
    return MCPServerList(
        items=servers,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{server_id}", response_model=MCPServerResponse)
async def get_mcp_server(
    server_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get MCP server details"""
    result = await db.execute(
        select(MCPServer).where(MCPServer.id == server_id)
    )
    server = result.scalar_one_or_none()
    
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    return server


@router.post("/", response_model=MCPServerResponse, status_code=201)
async def create_mcp_server(
    server: MCPServerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new MCP server"""
    
    # Check if endpoint already exists
    result = await db.execute(
        select(MCPServer).where(MCPServer.endpoint == server.endpoint)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="MCP server with this endpoint already exists")
    
    # Create new server
    new_server = MCPServer(
        **server.model_dump(),
        status="unknown"
    )
    db.add(new_server)
    await db.commit()
    await db.refresh(new_server)
    
    return new_server


@router.put("/{server_id}", response_model=MCPServerResponse)
async def update_mcp_server(
    server_id: UUID,
    server_update: MCPServerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update MCP server"""
    result = await db.execute(
        select(MCPServer).where(MCPServer.id == server_id)
    )
    server = result.scalar_one_or_none()
    
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    # Update fields
    update_data = server_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(server, field, value)
    
    await db.commit()
    await db.refresh(server)
    
    return server


@router.delete("/{server_id}", status_code=204)
async def delete_mcp_server(
    server_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete MCP server"""
    result = await db.execute(
        select(MCPServer).where(MCPServer.id == server_id)
    )
    server = result.scalar_one_or_none()
    
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    await db.delete(server)
    await db.commit()


@router.post("/discover", status_code=202)
async def trigger_discovery(db: AsyncSession = Depends(get_db)):
    """Trigger MCP discovery scan"""
    discovery_service = MCPDiscoveryService()
    
    # Run discovery in background
    import asyncio
    asyncio.create_task(
        discovery_service.discover_all()
    )
    
    return {"message": "Discovery scan started"}


@router.post("/{server_id}/enable", response_model=MCPServerResponse)
async def enable_mcp_server(
    server_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Enable MCP server"""
    result = await db.execute(
        select(MCPServer).where(MCPServer.id == server_id)
    )
    server = result.scalar_one_or_none()
    
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    server.status = "healthy"
    await db.commit()
    await db.refresh(server)
    
    return server


@router.post("/{server_id}/disable", response_model=MCPServerResponse)
async def disable_mcp_server(
    server_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Disable MCP server"""
    result = await db.execute(
        select(MCPServer).where(MCPServer.id == server_id)
    )
    server = result.scalar_one_or_none()
    
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    server.status = "down"
    await db.commit()
    await db.refresh(server)
    
    return server
```

### Success Criteria
- ✅ Database models created and migrations applied
- ✅ MCP discovery service finds local processes
- ✅ API endpoints return correct responses
- ✅ CRUD operations work for MCP servers
- ✅ Pagination and filtering work correctly
- ✅ Discovery scan can be triggered via API

---

## 🔐 Phase 3: Security & Authentication (Week 5)

### Objectives
- Implement OAuth/JWT authentication
- Add RBAC system
- Configure security middleware
- Set up audit logging

### Tasks

#### 3.1 Authentication Setup

**File: `frontend/src/app/api/auth/[...nextauth]/route.ts`**
```typescript
import NextAuth from "next-auth"
import GithubProvider from "next-auth/providers/github"
import GoogleProvider from "next-auth/providers/google"

const handler = NextAuth({
  providers: [
    GithubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id
        token.role = user.role || 'viewer'
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string
        session.user.role = token.role as string
      }
      return session
    },
  },
  pages: {
    signIn: '/auth/signin',
  },
})

export { handler as GET, handler as POST }
```

#### 3.2 RBAC Middleware

**File: `backend/app/middleware/auth.py`**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta

from app.config import get_settings
from app.models.user import User
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

settings = get_settings()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


def require_role(required_role: str):
    """Dependency to check user role"""
    async def role_checker(current_user: User = Depends(get_current_user)):
        role_hierarchy = {
            'viewer': 0,
            'developer': 1,
            'operator': 2,
            'admin': 3
        }
        
        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return current_user
    
    return role_checker
```

### Success Criteria
- ✅ OAuth login works with GitHub/Google
- ✅ JWT tokens generated and validated
- ✅ RBAC enforces permissions correctly
- ✅ Audit logs capture all admin actions
- ✅ Rate limiting prevents abuse

---

## 🎨 Phase 4: Frontend UI (Week 6-7)

### Objectives
- Build GitHub-inspired UI
- Create dashboard and MCP pages
- Implement real-time updates
- Add connection graphs

### Tasks

#### 4.1 Layout Components

**File: `frontend/src/components/layout/Sidebar.tsx`**
```typescript
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  LayoutDashboard, 
  Server, 
  Bot, 
  Shield, 
  Code, 
  Settings 
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'MCP Servers', href: '/mcps', icon: Server },
  { name: 'Agents', href: '/agents', icon: Bot },
  { name: 'Security', href: '/security', icon: Shield },
  { name: 'Dev Tools', href: '/dev', icon: Code },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 border-r border-border bg-background-secondary">
      <nav className="space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium
                transition-colors
                ${isActive 
                  ? 'bg-background-tertiary text-text-primary' 
                  : 'text-text-secondary hover:bg-background-tertiary hover:text-text-primary'
                }
              `}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
```

#### 4.2 Dashboard Page

**File: `frontend/src/app/(dashboard)/page.tsx`**
```typescript
import { Suspense } from 'react'
import { Server, Bot, Shield, Activity } from 'lucide-react'

async function getDashboardMetrics() {
  // Fetch from API
  return {
    totalMCPs: 42,
    activeAgents: 15,
    securityScore: 87,
    recentActivity: 234
  }
}

export default async function DashboardPage() {
  const metrics = await getDashboardMetrics()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-text-secondary">
          Overview of your MCP ecosystem
        </p>
      </div>

      {/* Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Total MCPs"
          value={metrics.totalMCPs}
          icon={Server}
          trend="+12%"
        />
        <MetricCard
          title="Active Agents"
          value={metrics.activeAgents}
          icon={Bot}
          trend="+5%"
        />
        <MetricCard
          title="Security Score"
          value={`${metrics.securityScore}%`}
          icon={Shield}
          trend="+3%"
        />
        <MetricCard
          title="Recent Activit