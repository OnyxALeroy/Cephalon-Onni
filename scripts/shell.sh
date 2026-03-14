#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

source "$SCRIPT_DIR/docker-common.sh"

usage() {
    echo "Usage: $0 [backend|mongo|redis]"
    echo "  backend  - Shell into backend container"
    echo "  mongo    - MongoDB shell (mongosh)"
    echo "  redis    - Redis CLI"
    exit 1
}

CONTAINER="${1:-}"

case "$CONTAINER" in
    backend)
        print_status "Opening shell in backend container..."
        docker exec -it cephalon-onni-backend /bin/bash
        ;;
    mongo|mongodb)
        print_status "Opening MongoDB shell..."
        docker exec -it cephalon-onni-mongo mongosh -u admin -p "$MONGO_ROOT_PASSWORD"
        ;;
    redis)
        print_status "Opening Redis CLI..."
        docker exec -it cephalon-onni-redis redis-cli
        ;;
    *)
        usage
        ;;
esac
