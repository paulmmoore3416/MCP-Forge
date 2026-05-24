"""
Test suite for MCP Forge backend API
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health endpoint returns correct status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "MCP Forge"
        assert "version" in data


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_json(self):
        """Test OpenAPI JSON schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "MCP Forge"
    
    def test_docs_endpoint(self):
        """Test Swagger UI documentation is accessible"""
        response = client.get("/api/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3456",
                "Access-Control-Request-Method": "GET"
            }
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


class TestSecurityHeaders:
    """Test security headers"""
    
    def test_security_headers_present(self):
        """Test security headers are set correctly"""
        response = client.get("/health")
        headers = response.headers
        
        # Check security headers
        assert "x-content-type-options" in headers
        assert headers["x-content-type-options"] == "nosniff"
        
        assert "x-frame-options" in headers
        assert headers["x-frame-options"] == "DENY"
        
        assert "x-xss-protection" in headers
        assert headers["x-xss-protection"] == "1; mode=block"
        
        assert "strict-transport-security" in headers
        assert "max-age=31536000" in headers["strict-transport-security"]
        
        assert "content-security-policy" in headers
        assert "default-src 'self'" in headers["content-security-policy"]


class TestRequestTracking:
    """Test request tracking middleware"""
    
    def test_request_id_header(self):
        """Test X-Request-ID header is added"""
        response = client.get("/health")
        assert "x-request-id" in response.headers
        assert response.headers["x-request-id"].startswith("req-")
    
    def test_response_time_header(self):
        """Test X-Response-Time header is added"""
        response = client.get("/health")
        assert "x-response-time" in response.headers
        assert "ms" in response.headers["x-response-time"]


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_not_found(self):
        """Test 404 error for non-existent endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_method_not_allowed(self):
        """Test 405 error for wrong HTTP method"""
        response = client.post("/health")
        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])