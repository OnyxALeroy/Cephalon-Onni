#!/usr/bin/env bash
set -e
source "$(dirname "$0")/docker-common.sh"

print_status "Starting standalone services only..."
cd "$PROJECT_ROOT"

compose down mongodb 2>/dev/null || true
compose down redis 2>/dev/null || true

compose up -d mongodb redis
sleep 8

services=(
  "MongoDB:cephalon-onni-mongo"
  "Redis:cephalon-onni-redis"
)

for s in "${services[@]}"; do
  IFS=':' read -r name container <<< "$s"
  check_service_health "$name" "$container"
done

test_database_connections

print_success "Standalone services are ready"
