from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


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
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # MCP Discovery
    DISCOVERY_INTERVAL_SECONDS: int = 300  # 5 minutes
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Performance (competing with TrueFoundry's sub-5ms latency)
    TARGET_LATENCY_MS: int = 10  # Sub-10ms target
    
    # Security (competing with Lasso Security)
    ENABLE_PROMPT_INJECTION_DETECTION: bool = True
    ENABLE_DATA_EXFILTRATION_DETECTION: bool = True
    ENABLE_ANOMALY_DETECTION: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
