#!/usr/bin/env bash

echo "Cephalon-Onni Docker Debugging Tool"
echo "==================================="

# Get project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Navigate to project root
cd "$PROJECT_ROOT"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running or you don't have permissions"
    echo "Try: sudo systemctl start docker"
    echo "Or add your user to docker group: sudo usermod -aG docker \$USER"
    exit 1
fi

echo "Docker is running"
echo ""

# Check containers
echo "Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(cephalon|backend|frontend|mongo)" || echo "No containers found with expected names"
echo ""

# Check frontend logs
echo "Frontend Logs (last 20 lines):"
if docker ps | grep -q frontend; then
    docker logs --tail 20 $(docker ps -q --filter "name=frontend") 2>&1
else
    echo "Frontend container not found"
fi
echo ""

# Test API endpoints
echo "Testing API Endpoints:"
echo "Testing backend health..."
if curl -s -f http://localhost:8000/docs > /dev/null 2>&1; then
    echo "Backend API docs accessible"
else
    echo "Backend API docs not accessible"
fi

echo "Testing auth endpoint..."
# 401 is expected for unauthenticated request to /me
if curl -s http://localhost:8000/api/auth/me | grep -q "Not authenticated"; then
    echo "Auth endpoint responding correctly (401 for unauthenticated)"
else
    echo "Auth endpoint not responding properly"
fi

echo "Testing registration endpoint..."
if curl -s -X POST http://localhost:8000/api/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","username":"testuser","password":"testpass123"}' \
    | grep -q "email\|detail"; then
    echo "Registration endpoint responding"
else
    echo "Registration endpoint not responding"
fi

echo ""
echo "Useful Commands:"
echo "View all logs: docker-compose logs -f"
echo "View backend logs: docker-compose logs -f backend"
echo "View frontend logs: docker-compose logs -f frontend"
echo "Restart services: docker-compose restart"
echo "Stop services: docker-compose down"
echo ""
echo "Access URLs:"
echo "Frontend: http://localhost:8080"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""

# Backend logs section - runs indefinitely until Ctrl+C
echo "Backend Live Logs (Press Ctrl+C to exit):"
echo "=========================================="
echo ""

if docker ps | grep -q backend; then
    # Show last 10 lines then follow live logs indefinitely
    docker logs --tail 10 -f $(docker ps -q --filter "name=backend") 2>&1
else
    echo "Backend container not found"
    exit 1
fi
