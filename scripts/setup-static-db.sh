#!/usr/bin/env bash
set -e

source "$(dirname "$0")/docker-common.sh"
cd "$PROJECT_ROOT"

print_status "Running PostgreSQL database initialization script..."

# The Java backend (cephalon-onni-backend) does NOT seed the static catalog (warframes, weapons,
# mods, ...) - it only creates schema via Flyway and expects that data to already be in Postgres
# (see backend-rework-plan.md Phase 2: "Static data is already in Postgres - no copy needed").
# The seeder itself (app/db_init_script.py + app/database/static/db_init/*) still only exists in
# the legacy Python backend, which is no longer part of the default docker-compose stack.
#
# To (re)seed a genuinely empty Postgres, build and run the legacy backend's image once, pointed
# at the same Postgres, e.g.:
#   docker build -t cephalon-onni-backend-legacy ./backend-python-legacy
#   docker run --rm --network cephalon-onni_default --env-file .env \
#       cephalon-onni-backend-legacy python app/db_init_script.py -y
#
# Porting this seeder to Java is a known follow-up, not yet done.

# Check if postgres container is running
if ! docker ps --filter "name=cephalon-onni-postgres" --filter "status=running" | grep -q "cephalon-onni-postgres"; then
    print_error "PostgreSQL container is not running"
    print_status "Please start the services first: ./scripts/start-everything.sh"
    exit 1
fi

print_status "Verifying static catalog data in PostgreSQL..."
docker exec cephalon-onni-postgres psql -U postgres -d cephalon_onni -c "SELECT COUNT(*) FROM warframes;" 2>/dev/null || true
docker exec cephalon-onni-postgres psql -U postgres -d cephalon_onni -c "SELECT COUNT(*) FROM weapons;" 2>/dev/null || true
docker exec cephalon-onni-postgres psql -U postgres -d cephalon_onni -c "SELECT COUNT(*) FROM mods;" 2>/dev/null || true
print_status "If any of the above are 0, see the comment at the top of this script."
