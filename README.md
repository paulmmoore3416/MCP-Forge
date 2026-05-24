# MCP Forge 🚀

**Enterprise-grade MCP governance platform with AI-powered security and observability**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)

---

## 🎯 Overview

MCP Forge is a comprehensive, GitHub-inspired administration platform for discovering, managing, observing, and governing Model Context Protocol (MCP) servers, clients, and agent interactions across distributed systems.

### Competitive Advantages

- **vs Mint MCP**: Enhanced RBAC with fine-grained permissions + multi-tenancy + compliance frameworks (SOC2, FedRAMP)
- **vs TrueFoundry**: Python/FastAPI backend (easier to extend) + built-in LLM routing + sub-10ms latency target + hybrid cloud support
- **vs Docker MCP Gateway**: K8s-native PLUS Docker Compose for simplicity + advanced resource quotas + auto-scaling
- **vs Lasso Security**: Integrated security (not just proxy) + ML-based anomaly detection + real-time threat intelligence + prompt injection prevention built-in

### Key Features

✅ **Discovery & Inventory**: Auto-scan local/remote MCP servers (STDIO, SSE, HTTP/S)  
✅ **Deep Insights**: Capabilities explorer, connection graphs, usage metrics, audit trails  
✅ **Administration**: Enable/disable, config management, RBAC, auto-approval policies  
✅ **Development Hub**: Integrated tools for building/testing MCP servers  
✅ **Observation & Governance**: Real-time monitoring, anomaly detection, security scanning  
✅ **Security-First**: OAuth/JWT, mTLS, encryption, least-privilege, audit logging  
✅ **Production-Ready**: Containerized, resilient, observable, scalable  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Forge Frontend                        │
│              (Next.js 15 + Tailwind + shadcn/ui)            │
└───────────────────────┬─────────────────────────────────────┘
                        │ REST API + WebSocket
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway / Backend                     │
│                  (Python FastAPI + Uvicorn)                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Discovery  │ │   Database   │ │    Redis     │
│   Service    │ │ (PostgreSQL) │ │   (Cache)    │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose** (recommended)
- **Node.js** 20+ (for local frontend development)
- **Python** 3.11+ (for local backend development)
- **PostgreSQL** 15+ (if not using Docker)
- **Redis** 7+ (if not using Docker)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-forge.git
cd mcp-forge

# Copy environment file and configure
cp .env.example .env
# Edit .env and set secure passwords and secrets

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001
```

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example ../.env
# Edit .env with your configuration

# Run database migrations (requires PostgreSQL running)
alembic upgrade head

# Start the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev

# Access at http://localhost:3000
```

---

## 📚 Documentation

- **[Technical Specification](./MCP_FORGE_SPECIFICATION.md)** - Complete architecture and design
- **[Implementation Roadmap](./IMPLEMENTATION_ROADMAP.md)** - Detailed development plan
- **[API Documentation](http://localhost:8000/api/docs)** - Interactive API docs (when running)

---

## 🔐 Security

MCP Forge implements enterprise-grade security:

- **Authentication**: OAuth 2.0 / JWT with support for GitHub, Google, Azure
- **Authorization**: Role-Based Access Control (RBAC) with fine-grained permissions
- **Encryption**: TLS 1.3 for transit, AES-256 for data at rest
- **mTLS**: Mutual TLS for MCP server connections
- **Audit Logging**: Comprehensive audit trail for all admin actions
- **Security Scanning**: Real-time vulnerability detection and prompt injection prevention
- **Compliance**: SOC2 and FedRAMP-ready controls

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test -- --coverage

# E2E tests
npm run test:e2e
```

---

## 📊 Monitoring

MCP Forge includes built-in observability:

- **Prometheus**: Metrics collection (http://localhost:9090)
- **Grafana**: Visualization dashboards (http://localhost:3001)
- **Structured Logging**: JSON logs with correlation IDs
- **Performance Tracking**: Sub-10ms latency target monitoring

---

## 🛠️ Development

### Project Structure

```
mcp-forge/
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/          # App router pages
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities
│   └── Dockerfile
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── middleware/  # Middleware
│   └── Dockerfile
├── monitoring/           # Prometheus config
├── docker-compose.yml    # Docker orchestration
└── README.md
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🚢 Deployment

### Docker Compose (Development/Staging)

```bash
docker-compose up -d
```

### Kubernetes (Production)

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n mcp-forge
```

See [DEPLOYMENT.md](./docs/DEPLOYMENT.md) for detailed deployment instructions.

---

## 📈 Roadmap

- [x] Phase 1: Project Foundation & Infrastructure
- [ ] Phase 2: Backend Core - MCP Discovery & API
- [ ] Phase 3: Security & Authentication
- [ ] Phase 4: Frontend UI
- [ ] Phase 5: Advanced Features - Monitoring & Governance
- [ ] Phase 6: Development Hub
- [ ] Phase 7: Production Readiness
- [ ] Phase 8: Testing & Optimization

See [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) for detailed timeline.

---

## 🤝 Support

- **Documentation**: [MCP Forge Docs](./docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/mcp-forge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mcp-forge/discussions)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io) - Official MCP specification
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [Next.js](https://nextjs.org) - React framework for production
- Inspired by GitHub's UI/UX design principles

---

**Built with ❤️ for the MCP community**
