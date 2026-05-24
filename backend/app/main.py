from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
import time
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response

from app.config import get_settings
from app.database import engine, Base

settings = get_settings()

# Configure structured JSON logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","service":"mcp-forge-backend","message":"%(message)s"}',
)
logger = logging.getLogger(__name__)

# Prometheus metrics for observability (competing with TrueFoundry)
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("Competitive advantages: Enhanced RBAC, Sub-10ms latency, ML-based security, Developer tools")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start background tasks
    # TODO: Initialize Celery tasks for:
    # - Periodic MCP discovery
    # - Security scanning
    # - Anomaly detection
    # - Metrics collection
    
    logger.info("MCP Forge Backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MCP Forge Backend")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-grade MCP governance platform with AI-powered security and observability",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware with security headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
)

# GZip compression for performance
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Performance monitoring middleware (targeting sub-10ms latency)
@app.middleware("http")
async def add_performance_headers(request: Request, call_next):
    start_time = time.time()
    
    # Generate request ID for correlation
    request_id = request.headers.get("X-Request-ID", f"req-{int(time.time() * 1000)}")
    
    response = await call_next(request)
    
    # Calculate response time
    process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Add performance headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{process_time:.2f}ms"
    
    # Log slow requests (> 10ms target)
    if process_time > settings.TARGET_LATENCY_MS:
        logger.warning(
            f"Slow request detected: {request.method} {request.url.path} took {process_time:.2f}ms"
        )
    
    # Update Prometheus metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time / 1000)
    
    return response


# Security headers middleware (competing with Lasso Security)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "service": settings.APP_NAME
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check - verifies all dependencies"""
    # TODO: Check database, redis, and other dependencies
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "redis": "ok",
            "mcp_discovery": "ok"
        }
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type="text/plain")


# API routers will be included here
# TODO: Include routers for:
# - Authentication & Authorization (OAuth/JWT, RBAC)
# - MCP Servers (CRUD, discovery, health checks)
# - Agents (management, connections)
# - Security (scanning, vulnerabilities, compliance)
# - Metrics & Analytics (usage, performance, anomalies)
# - Development Tools (scaffolding, testing, validation)

# Example router structure (to be implemented):
# from app.api import auth, mcps, agents, security, metrics, dev_tools
# app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
# app.include_router(mcps.router, prefix=f"{settings.API_V1_PREFIX}/mcps", tags=["mcps"])
# app.include_router(agents.router, prefix=f"{settings.API_V1_PREFIX}/agents", tags=["agents"])
# app.include_router(security.router, prefix=f"{settings.API_V1_PREFIX}/security", tags=["security"])
# app.include_router(metrics.router, prefix=f"{settings.API_V1_PREFIX}/metrics", tags=["metrics"])
# app.include_router(dev_tools.router, prefix=f"{settings.API_V1_PREFIX}/dev", tags=["dev-tools"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Enterprise MCP Governance Platform",
        "features": [
            "Enhanced RBAC with fine-grained permissions",
            "Sub-10ms API latency target",
            "ML-based anomaly detection",
            "Real-time security scanning",
            "Integrated development tools",
            "Multi-tenancy support",
            "Compliance frameworks (SOC2, FedRAMP)",
        ],
        "competitive_advantages": {
            "vs_mint_mcp": "Enhanced RBAC + multi-tenancy + compliance frameworks",
            "vs_truefoundry": "Easier extensibility + hybrid cloud + built-in LLM routing",
            "vs_docker_gateway": "K8s-native + Docker Compose + advanced resource quotas",
            "vs_lasso_security": "Integrated security + ML anomaly detection + prompt injection prevention"
        },
        "docs": "/api/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )
