#!/usr/bin/env bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status()  { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# Root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Compose command abstraction
compose() {
    if command -v docker-compose &> /dev/null; then
        docker-compose "$@"
    else
        docker compose "$@"
    fi
}

check_service_health() {
    local service_name=$1
    local container_name=$2
    local max_attempts=30

    print_status "Checking health of $service_name..."

    for ((i=1; i<=max_attempts; i++)); do
        if docker ps --filter "name=$container_name" --filter "status=running" | grep -q "$container_name"; then
            case "$service_name" in
                Backend)
                    curl -fs http://localhost:8000/health >/dev/null && {
                        print_success "$service_name is healthy!"
                        return 0
                    }
                    ;;
                Frontend)
                    curl -fs http://localhost:8080 >/dev/null && {
                        print_success "$service_name is healthy!"
                        return 0
                    }
                    ;;
                MongoDB)
                    docker exec "$container_name" mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1 && {
                        print_success "$service_name is healthy!"
                        return 0
                    }
                    ;;
                *)
                    print_success "$service_name is running!"
                    return 0
                    ;;
            esac
        fi
        sleep 2
        echo -n "."
    done

    print_error "$service_name failed health check"
    return 1
}

test_database_connections() {
    print_status "Testing database connections..."

    docker exec cephalon-onni-postgres pg_isready -U user -d cephalon_db >/dev/null &&
        print_success "PostgreSQL OK" ||
        print_error "PostgreSQL failed"

    docker exec cephalon-onni-mongo mongosh --eval "db.adminCommand('ping')" >/dev/null &&
        print_success "MongoDB OK" ||
        print_error "MongoDB failed"
}
