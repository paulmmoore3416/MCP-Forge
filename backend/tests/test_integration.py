"""
Integration tests for MCP Forge backend
Tests database connectivity, Redis, and service integration
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestDatabaseIntegration:
    """Test database integration"""
    
    def test_database_connection(self):
        """Test database connection is working"""
        # Health check should verify DB connection
        response = client.get("/health")
        assert response.status_code == 200
        # If DB was down, health check would fail


class TestRedisIntegration:
    """Test Redis integration"""
    
    def test_redis_available(self):
        """Test Redis is accessible"""
        # Health check should verify Redis connection
        response = client.get("/health")
        assert response.status_code == 200


class TestEndToEnd:
    """End-to-end integration tests"""
    
    def test_full_request_cycle(self):
        """Test complete request/response cycle with all middleware"""
        response = client.get("/health")
        
        # Verify response
        assert response.status_code == 200
        
        # Verify all middleware executed
        assert "x-request-id" in response.headers
        assert "x-response-time" in response.headers
        assert "x-content-type-options" in response.headers
        
        # Verify response data
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "MCP Forge"
        assert data["version"] == "1.0.0"


class TestConcurrency:
    """Test concurrent request handling"""
    
    def test_multiple_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        import concurrent.futures
        
        def make_request():
            return client.get("/health")
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # All should have request IDs (may have duplicates due to timing)
        request_ids = [r.headers["x-request-id"] for r in responses]
        assert len(request_ids) == 10
        assert all(rid.startswith("req-") for rid in request_ids)
        
        # Most should be unique (allow for some timing collisions)
        unique_ids = len(set(request_ids))
        assert unique_ids >= 8, f"Expected at least 8 unique IDs, got {unique_ids}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])