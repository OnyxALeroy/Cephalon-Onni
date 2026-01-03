#!/usr/bin/env bash

# Import common functions and variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/docker-common.sh"

print_status "Running database initialization script..."

# Check if backend container is running
if ! docker ps --filter "name=cephalon-onni-backend" --filter "status=running" | grep -q "cephalon-onni-backend"; then
    print_error "Backend container is not running"
    print_status "Please start the services first: ./scripts/start-everything.sh"
    exit 1
fi

# Run the database initialization script
docker exec -it cephalon-onni-backend python app/db_init_script.py

if [ $? -eq 0 ]; then
    print_success "Database initialization completed successfully"
else
    print_error "Database initialization failed"
    exit 1
fi
