#!/usr/bin/env bash

# Cephalon-Onni Docker Service Starter
# This script starts all Docker services with health checks and testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a service is healthy
check_service_health() {
    local service_name=$1
    local container_name=$2
    local max_attempts=30
    local attempt=1

    print_status "Checking health of $service_name..."

    while [ $attempt -le $max_attempts ]; do
        if docker ps --filter "name=$container_name" --filter "status=running" | grep -q "$container_name"; then
            if [ "$service_name" = "backend" ]; then
                # Check backend health endpoint
                if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
                    print_success "$service_name is healthy!"
                    return 0
                fi
            elif [ "$service_name" = "frontend" ]; then
                # Check frontend
                if curl -f -s http://localhost:8080 > /dev/null 2>&1; then
                    print_success "$service_name is healthy!"
                    return 0
                fi
            elif [ "$service_name" = "MongoDB" ]; then
                # Test MongoDB connection
                if docker exec $container_name mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
                    print_success "$service_name is healthy!"
                    return 0
                fi
            else
                # For databases, just check if container is running
                print_success "$service_name is running!"
                return 0
            fi
        fi

        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    print_error "$service_name failed to become healthy!"
    return 1
}

# Function to test database connections
test_database_connections() {
    print_status "Testing database connections..."

    # Test PostgreSQL
    print_status "Testing PostgreSQL connection..."
    if docker exec cephalon-onni-postgres pg_isready -U user -d cephalon_db > /dev/null 2>&1; then
        print_success "PostgreSQL connection successful"
    else
        print_error "PostgreSQL connection failed"
        return 1
    fi

    # Test MongoDB
    print_status "Testing MongoDB connection..."
    if docker exec cephalon-onni-mongo mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        print_success "MongoDB connection successful"
    else
        print_error "MongoDB connection failed"
        return 1
    fi

    # Test Apache AGE
    print_status "Testing Apache AGE (PostgreSQL) connection..."
    if docker exec cephalon-onni-postgres psql -U user -d cephalon_db -c "
        CREATE EXTENSION IF NOT EXISTS age;
        LOAD 'age';
        SET search_path = ag_catalog, \"\$user\", public;
        SELECT * FROM ag_graph WHERE name = 'loot_tables';
    " > /dev/null 2>&1; then
        print_success "Apache AGE and loot_tables graph are ready"
    else
        print_warning "Apache AGE or loot_tables graph not ready yet"
        print_status "You can initialize AGE by running: ./scripts/setup-age-db.sh"
    fi

    return 0
}

# Function to test API endpoints
test_api_endpoints() {
    print_status "Testing API endpoints..."

    # Wait a bit for backend to fully start
    sleep 5

    # Test health endpoint
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend health endpoint accessible"
    else
        print_warning "Backend health endpoint not accessible (might not be implemented)"
    fi

    # Test auth endpoints (should not error out)
    # Use unique email to avoid "already used" error
    local test_email="test$(date +%s)@example.com"
    local response=$(curl -s -X POST http://localhost:8000/api/auth/register \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$test_email\",\"username\":\"testuser\",\"password\":\"testpass\"}")
    
    if echo "$response" | grep -q '"email"'; then
        print_success "Registration endpoint working"
    else
        print_warning "Registration endpoint test failed - Response: $response"
    fi

    return 0
}

# Get project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Main execution
main() {
    print_status "Starting Cephalon-Onni Docker services..."

    # Navigate to project root
    cd "$PROJECT_ROOT"

    # Check if docker-compose exists
    if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
        print_error "Docker or Docker Compose not found!"
        exit 1
    fi

    # Stop existing containers
    print_status "Stopping existing containers..."
    docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

    # Clean up any orphaned containers
    docker system prune -f > /dev/null 2>&1 || true

    # Build and start services
    print_status "Building and starting services..."
    if command -v docker-compose &> /dev/null; then
        docker-compose up --build -d
    else
        docker compose up --build -d
    fi

    # Wait for services to start
    print_status "Waiting for services to start..."
    sleep 10

    # Check service health
    echo
    print_status "Checking service health..."

    services=(
        "PostgreSQL:cephalon-onni-postgres"
        "MongoDB:cephalon-onni-mongo"
        "Backend:cephalon-onni-backend"
        "Frontend:cephalon-onni-frontend"
    )

    all_healthy=true
    for service in "${services[@]}"; do
        IFS=':' read -r name container <<< "$service"
        if ! check_service_health "$name" "$container"; then
            all_healthy=false
        fi
        echo
    done

    # Test database connections
    if [ "$all_healthy" = true ]; then
        test_database_connections
        echo

        # Test API endpoints
        test_api_endpoints
        echo
    fi

    # Display service URLs
    print_status "Service URLs:"
    echo "  Frontend: http://localhost:8080"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo "  PostgreSQL (with AGE): localhost:5432"
    echo "  MongoDB: localhost:27017"
    echo

    # Show running containers
    print_status "Running containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo

    if [ "$all_healthy" = true ]; then
        print_success "All services are running successfully!"
        print_status "You can now access the application at http://localhost:8080"

    else
        print_warning "Some services may not be fully operational. Check the logs above."
        print_status "To view logs: docker-compose logs -f [service_name]"
    fi

    print_status "To stop all services: docker-compose down"
    print_status "To view logs: docker-compose logs -f"
}

# Handle script interruption
trap 'print_warning "Script interrupted. Stopping services..."; docker-compose down; exit 1' INT TERM

# Run main function
main "$@"
