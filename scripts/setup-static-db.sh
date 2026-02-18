#!/usr/bin/env bash
set -e

source "$(dirname "$0")/docker-common.sh"
cd "$PROJECT_ROOT"

print_status "Running database initialization script..."

print_status "Removing existing data folder..."
rm -rf ./data/

# Check if backend container is running
if ! docker ps --filter "name=cephalon-onni-backend" --filter "status=running" | grep -q "cephalon-onni-backend"; then
    print_error "Backend container is not running"
    print_status "Please start the services first: ./scripts/start-everything.sh"
    exit 1
fi

# Run the database initialization script
docker exec -it cephalon-onni-backend python app/db_init_script.py "$@"

if [ $? -eq 0 ]; then
    print_success "Database initialization completed successfully"

    # Check if there are JSON files in the container before copying
    print_status "Checking for JSON files in container..."
    json_files_count=$(docker exec cephalon-onni-backend sh -c 'ls -1 /app/data/json/*.json 2>/dev/null | wc -l')

    if [ "$json_files_count" -gt 0 ]; then
        # Create local data directory if it doesn't exist
        mkdir -p ./data/json

        # Copy JSON files from container to host
        print_status "Copying $json_files_count JSON files from container to host..."
        docker cp cephalon-onni-backend:/app/data/json/. ./data/json/

        if [ $? -eq 0 ]; then
            print_success "JSON files copied to ./data/json/"
            ls -la ./data/json/
        else
            print_error "Failed to copy JSON files from container"
        fi
    else
        print_status "No JSON files found in container, skipping copy"
    fi
else
    print_error "Database initialization failed"
    exit 1
fi
