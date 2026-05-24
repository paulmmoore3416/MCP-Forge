# 🚀 MCP Forge - Quick Start Guide

## Prerequisites

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Git**

That's it! No need to install Python, Node.js, PostgreSQL, or Redis locally.

---

## 🐳 Getting Started with Docker (Recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/paulmmoore3416/MCP-Forge.git
cd MCP-Forge
```

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Generate secure secrets (Linux/Mac)
echo "DB_PASSWORD=$(openssl rand -base64 32)" >> .env
echo "SECRET_KEY=$(openssl rand -base64 32)" >> .env
echo "JWT_SECRET=$(openssl rand -base64 32)" >> .env
echo "NEXTAUTH_SECRET=$(openssl rand -base64 32)" >> .env

# Or manually edit .env and replace placeholder values
nano .env  # or use your preferred editor
```

**Important**: Replace all `your_*` placeholder values with secure random strings.

### Step 3: Start All Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs (optional)
docker-compose logs -f
```

### Step 4: Access the Application

Once all containers are running (takes ~2-3 minutes on first start):

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (default: admin/admin)

### Step 5: Verify Installation

```bash
# Check all services are healthy
docker-compose ps

# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

---

## 🛠️ Common Commands

### Managing Services

```bash
# Stop all services
docker-compose stop

# Start services
docker-compose start

# Restart services
docker-compose restart

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (⚠️ deletes data)
docker-compose down -v

# View logs
docker-compose logs -f [service_name]

# Example: View backend logs
docker-compose logs -f backend
```

### Database Operations

```bash
# Access PostgreSQL
docker-compose exec db psql -U postgres -d mcpforge

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create a new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Development

```bash
# Rebuild containers after code changes
docker-compose up -d --build

# Access backend shell
docker-compose exec backend bash

# Access frontend shell
docker-compose exec frontend sh

# Run backend tests
docker-compose exec backend pytest

# Run frontend tests
docker-compose exec frontend npm test
```

---

## 🔧 Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Check what's using the port
sudo lsof -i :3000  # or :8000, :5432, etc.

# Stop the conflicting service or change ports in docker-compose.yml
```

### Containers Won't Start

```bash
# Check container logs
docker-compose logs [service_name]

# Remove all containers and start fresh
docker-compose down -v
docker-compose up -d
```

### Database Connection Issues

```bash
# Ensure database is healthy
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Frontend Build Errors

```bash
# Rebuild frontend
docker-compose up -d --build frontend

# Clear Next.js cache
docker-compose exec frontend rm -rf .next
docker-compose restart frontend
```

---

## 📊 Monitoring

### Prometheus Metrics

Access Prometheus at http://localhost:9090

Example queries:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `rate(http_requests_total[5m])` - Request rate

### Grafana Dashboards

1. Access Grafana at http://localhost:3001
2. Login with `admin` / `admin` (change on first login)
3. Add Prometheus data source: http://prometheus:9090
4. Import dashboards from `monitoring/grafana/`

---

## 🔐 Security Notes

### Production Deployment

Before deploying to production:

1. **Change all default passwords** in `.env`
2. **Use strong secrets** (32+ characters)
3. **Enable HTTPS** with valid SSL certificates
4. **Configure firewall** rules
5. **Set up backup** procedures
6. **Enable audit logging**
7. **Review security settings** in `docker-compose.yml`

### Environment Variables

Never commit `.env` files to version control. Use:
- **Development**: `.env` file (gitignored)
- **Production**: Environment variables or secrets management (Vault, AWS Secrets Manager)

---

## 🚀 Next Steps

1. **Configure OAuth** (optional): Add GitHub/Google OAuth credentials to `.env`
2. **Explore API**: Visit http://localhost:8000/api/docs
3. **Read Documentation**: Check `MCP_FORGE_SPECIFICATION.md`
4. **Join Community**: GitHub Discussions for questions

---

## 📞 Need Help?

- **Issues**: https://github.com/paulmmoore3416/MCP-Forge/issues
- **Discussions**: https://github.com/paulmmoore3416/MCP-Forge/discussions
- **Documentation**: See `docs/` directory

---

**Happy MCP Forging! 🔨**
