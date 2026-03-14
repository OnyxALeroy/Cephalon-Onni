#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

source "$SCRIPT_DIR/docker-common.sh"

usage() {
    echo "Usage: $0 [all|volumes]"
    echo "  all     - Remove containers, networks, and unused images"
    echo "  volumes - Remove containers and all volumes (DESTRUCTIVE)"
    exit 1
}

TARGET="${1:-all}"

case "$TARGET" in
    all)
        print_status "Stopping and removing containers..."
        compose down --remove-orphans
        print_status "Removing unused images..."
        docker image prune -f
        print_success "Cleanup complete (containers and unused images removed)"
        ;;
    volumes)
        print_warning "This will DELETE all database data!"
        read -p "Are you sure? Type 'yes' to confirm: " confirm
        if [[ "$confirm" != "yes" ]]; then
            print_status "Aborted"
            exit 0
        fi
        print_status "Stopping containers and removing volumes..."
        compose down -v
        print_status "Removing unused images..."
        docker image prune -f
        print_success "Cleanup complete (containers, volumes, and unused images removed)"
        ;;
    *)
        usage
        ;;
esac
