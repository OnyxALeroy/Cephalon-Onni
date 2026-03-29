#!/usr/bin/env bash
set -e

source "$(dirname "$0")/docker-common.sh"
cd "$PROJECT_ROOT"

print_status "Running PostgreSQL database initialization script..."

# Check if backend container is running
if ! docker ps --filter "name=cephalon-onni-backend" --filter "status=running" | grep -q "cephalon-onni-backend"; then
    print_error "Backend container is not running"
    print_status "Please start the services first: ./scripts/start-everything.sh"
    exit 1
fi

# Check if postgres container is running
if ! docker ps --filter "name=cephalon-onni-postgres" --filter "status=running" | grep -q "cephalon-onni-postgres"; then
    print_error "PostgreSQL container is not running"
    print_status "Please start the services first: ./scripts/start-everything.sh"
    exit 1
fi

# Run the database initialization script
docker exec -it cephalon-onni-backend python app/db_init_script.py "$@"

if [ $? -eq 0 ]; then
    print_success "PostgreSQL Database initialization completed successfully"
    
    # Check table counts
    print_status "Verifying data in PostgreSQL..."
    docker exec cephalon-onni-postgres psql -U postgres -d cephalon_onni -c "SELECT COUNT(*) FROM warframes;" 2>/dev/null || true
    docker exec cephalon-onni-postgres psql -U postgres -d cephalon_onni -c "SELECT COUNT(*) FROM weapons;" 2>/dev/null || true
    docker exec cephalon-onni-postgres psql -U postgres -d cephalon_onni -c "SELECT COUNT(*) FROM mods;" 2>/dev/null || true
else
    print_error "Database initialization failed"
    exit 1
fi
