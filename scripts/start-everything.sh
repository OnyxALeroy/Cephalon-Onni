#!/usr/bin/env bash
set -e
source "$(dirname "$0")/docker-common.sh"

if [[ "$1" == "prod" ]]; then
    export PROFILE=prod
    print_status "Starting in PRODUCTION mode..."
else
    print_status "Starting in DEV mode..."
fi

./scripts/start-standalones.sh
./scripts/start-apps.sh
