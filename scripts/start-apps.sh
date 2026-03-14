#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/docker-common.sh"
cd "$PROJECT_ROOT"

RESTART_MODE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --restart|-r)
      RESTART_MODE=true
      shift
      ;;
    *)
      echo "Usage: $0 [--restart|-r]"
      echo "  --restart, -r  Start in restart-mode with auto-update on code changes"
      exit 1
      ;;
  esac
done

print_status "Stopping backend and frontend containers..."
compose stop backend frontend

if [[ "$RESTART_MODE" == true ]]; then
  print_status "Building and starting in restart-mode (auto-update on code changes)..."
  print_warning "Running in foreground. Press Ctrl+C to stop."
  compose up --build --no-deps --watch backend frontend
else
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

  print_success "Backend and Frontend are running${RESTART_MODE:+ (restart-mode: auto-update on code changes)}"
fi
