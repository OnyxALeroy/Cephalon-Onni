# Cephalon-Onni Scripts

This directory contains utility scripts for managing the Cephalon-Onni project.

## Available Scripts

### `start-docker-services.sh`
Starts all Docker services with health checks and testing.

**Usage:**
```bash
./scripts/start-docker-services.sh
```

**What it does:**
- Stops existing containers
- Builds and starts all services
- Waits for services to be healthy
- Tests database connections
- Tests API endpoints
- Displays service URLs and container status

### `repopulate-neo4j-db.sh`
Runs the HTML parser script to populate Neo4j database.

**Usage:**
```bash
./scripts/repopulate-neo4j-db.sh
```

**What it does:**
- Checks Docker accessibility
- Verifies Neo4j container is running
- Executes the HTML parser script in the backend container
- Clears existing database and repopulates with fresh data

### `debug-docker.sh`
Debug tool for Docker containers and services.

**Usage:**
```bash
./scripts/debug-docker.sh
```

**What it does:**
- Checks Docker status and containers
- Shows recent logs for backend/frontend
- Tests API endpoints
- Displays useful commands for manual debugging

## Quick Start Guide

### First Time Setup:
1. **Start all services:**
   ```bash
   ./scripts/start-docker-services.sh
   ```

2. **Wait for services to be healthy**, then populate database:
   ```bash
   ./scripts/repopulate-neo4j-db.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Neo4j Browser: http://localhost:7474

### Daily Usage:
- **Start services:** `./scripts/start-docker-services.sh`
- **Populate fresh data:** `./scripts/repopulate-neo4j-db.sh`
- **Debug issues:** `./scripts/debug-docker.sh`

## Requirements

- Docker and Docker Compose installed
- User permissions to access Docker (or use sudo)
- Project repository root as working directory

## Docker Access Setup

If you get permission errors, add your user to the docker group:
```bash
sudo usermod -aG docker $USER
# Then logout and login again, or run:
newgrp docker
```

## Service URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:8080 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |
| Neo4j Browser | http://localhost:7474 |
| PostgreSQL | localhost:5432 |
| MongoDB | localhost:27017 |

## Container Names

- `cephalon-onni-backend` - FastAPI backend
- `cephalon-onni-frontend` - Vue.js frontend  
- `cephalon-onni-postgres` - PostgreSQL database
- `cephalon-onni-mongo` - MongoDB database
- `cephalon-onni-neo4j` - Neo4j graph database

## Troubleshooting

### Permission Denied
```bash
# Add user to docker group (requires logout/login)
sudo usermod -aG docker $USER

# Or use sudo with commands
sudo ./scripts/run-docker.sh
```

### Containers Not Starting
```bash
# Check Docker status
docker info

# View logs
./scripts/debug_docker.sh

# Manually view logs
docker-compose logs -f [service_name]
```

### HTML Parser Issues
- Ensure Neo4j container is running
- Wait 30-60 seconds after starting services
- Check Neo4j connection with debug script
