#!/usr/bin/env bash
set -euo pipefail

# Load shared Docker functions / variables
source "$(dirname "$0")/docker-common.sh"
cd "$PROJECT_ROOT"

DC="docker compose"

print_status "Stopping backend and frontend containers..."
$DC stop backend frontend

print_status "Building and recreating backend and frontend containers..."
# --build rebuilds images, --no-deps keeps other containers untouched
# --force-recreate ensures name conflicts don't happen
$DC up --build -d --no-deps --force-recreate backend frontend

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
