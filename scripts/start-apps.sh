#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/docker-common.sh"
cd "$PROJECT_ROOT"

print_status "Stopping backend and frontend containers..."
compose stop backend frontend

print_status "Building and recreating backend and frontend containers..."
compose up --build -d --no-deps --force-recreate backend frontend

# Optional: short wait before checking health
sleep 5

# List of services and their container names
services=(
  "Backend:cephalon-onni-backend"
  "Frontend:cephalon-onni-frontend"
)

# Check health of each service
for s in "${services[@]}"; do
  IFS=':' read -r name container <<< "$s"
  check_service_health "$name" "$container"
done

print_status "Service URLs:"
echo "  Frontend: http://localhost:8080"
echo "  Backend:  http://localhost:8000"

print_success "Backend and Frontend are running"
