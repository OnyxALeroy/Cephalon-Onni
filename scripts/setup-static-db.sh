#!/usr/bin/env bash
set -e

source "$(dirname "$0")/docker-common.sh"
cd "$PROJECT_ROOT"

# The Java backend seeds the static catalog (warframes, weapons, mods, missions, drop tables, ...)
# itself: on startup, if the warframes table is empty, it imports everything from Warframe's
# public data (see backend/src/main/java/com/cephalononni/catalog). To refresh it after a game
# update, use Admin > System Configuration > "Import now" (or POST /api/admin/catalog/import as an
# administrator). The legacy Python seeder is no longer needed.
#
# This script only reports what is currently in the catalog.

if ! docker ps --filter "name=cephalon-onni-postgres" --filter "status=running" | grep -q "cephalon-onni-postgres"; then
    print_error "PostgreSQL container is not running"
    print_status "Please start the services first: ./scripts/start-everything.sh"
    exit 1
fi

print_status "Static catalog row counts:"
docker exec cephalon-onni-postgres psql -U postgres -d cephalon_onni -c "
    SELECT 'warframes' AS table_name, count(*) FROM warframes
    UNION ALL SELECT 'weapons', count(*) FROM weapons
    UNION ALL SELECT 'mods', count(*) FROM mods
    UNION ALL SELECT 'arcanes', count(*) FROM arcanes
    UNION ALL SELECT 'relics', count(*) FROM relics
    UNION ALL SELECT 'missions', count(*) FROM missions
    UNION ALL SELECT 'drop_sources', count(*) FROM drop_sources;" 2>/dev/null || true
print_status "If these are 0, check the backend logs for 'Catalog import' (make logs-backend)."
