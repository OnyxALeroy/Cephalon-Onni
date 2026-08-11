#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

source "$SCRIPT_DIR/docker-common.sh"

usage() {
    echo "Usage: $0 [backend|postgres|redis]"
    echo "  backend  - Shell into backend container"
    echo "  postgres - PostgreSQL CLI (psql)"
    echo "  redis    - Redis CLI"
    exit 1
}

CONTAINER="${1:-}"

case "$CONTAINER" in
    backend)
        print_status "Opening shell in backend container..."
        docker exec -it cephalon-onni-backend /bin/sh
        ;;
    postgres|pg)
        print_status "Opening PostgreSQL shell..."
        docker exec -it cephalon-onni-postgres psql -U postgres -d cephalon_onni
        ;;
    redis)
        print_status "Opening Redis CLI..."
        docker exec -it cephalon-onni-redis redis-cli
        ;;
    *)
        usage
        ;;
esac
