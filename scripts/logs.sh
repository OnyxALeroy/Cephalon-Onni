#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

source "$SCRIPT_DIR/docker-common.sh"

usage() {
    echo "Usage: $0 [backend|frontend|mongo|redis|all]"
    echo "  Default: all"
    exit 1
}

SERVICE="${1:-all}"

case "$SERVICE" in
    backend)
        print_status "Tailing backend logs..."
        docker compose logs -f backend
        ;;
    frontend)
        print_status "Tailing frontend logs..."
        docker compose logs -f frontend
        ;;
    mongo|mongodb)
        print_status "Tailing MongoDB logs..."
        docker compose logs -f mongodb
        ;;
    redis)
        print_status "Tailing Redis logs..."
        docker compose logs -f redis
        ;;
    all)
        print_status "Tailing all logs..."
        docker compose logs -f
        ;;
    *)
        usage
        ;;
esac
