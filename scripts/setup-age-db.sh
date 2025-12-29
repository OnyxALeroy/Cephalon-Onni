#!/usr/bin/env bash

echo "=== Running HTML Parsers Script ==="

# Default values
OUTPUT_PATH="None"
CLEAN_AND_REFILL_AGE="false"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --output-path|-o)
            OUTPUT_PATH="$2"
            shift 2
            ;;
        --clean-and-refill-age|-c)
            CLEAN_AND_REFILL_AGE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --output-path, -o PATH     Output directory path (default: None)"
            echo "  --clean-and-refill-age, -c BOOL    Clean and refill AGE database (default: false)"
            echo "  --help, -h                 Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate boolean parameter
if [[ "$CLEAN_AND_REFILL_AGE" != "true" && "$CLEAN_AND_REFILL_AGE" != "false" ]]; then
    echo "Error: clean_and_refill_age must be 'true' or 'false'"
    exit 1
fi

echo "Output path: $OUTPUT_PATH"
echo "Clean and refill AGE: $CLEAN_AND_REFILL_AGE"

# Get project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed or not in PATH"
    exit 1
fi

# Check if we can access Docker
if docker ps &> /dev/null; then
    echo "Docker is accessible"

    # Check if backend container is running
    echo "Checking Cephalon-Onni backend container..."

    if docker ps --format "table {{.Names}}" | grep -q "cephalon-onni-backend"; then
        echo "Backend container is running"

        # Run script in backend container with parameters
        echo "Running HTML parsers script in backend container..."
        if docker exec -w /app -e PYTHONPATH=/app cephalon-onni-backend python app/html_parsers.py --output-path "$OUTPUT_PATH" --clean-and-refill-age "$CLEAN_AND_REFILL_AGE"; then
            echo "✓ HTML parsers script completed successfully!"

            # Copy outputs to host directory
            echo "Copying outputs to host directory..."
            if docker cp cephalon-onni-backend:/app/outputs ./outputs 2>/dev/null; then
                echo "✓ Output files copied to $(pwd)/outputs"
            else
                echo "No outputs directory found in container"
            fi
        else
            echo "✗ HTML parsers script failed"
            exit 1
        fi

        # Show database details after parsing
        echo
        echo "=== Database Details ==="

        # Get graph statistics using direct SQL
        echo "Graph Statistics:"
        docker exec cephalon-onni-postgres psql -U user -d cephalon_db -c "
            LOAD 'age';
            SET search_path = ag_catalog, public;

            -- Count nodes
            SELECT 'Total Nodes: ' || COUNT(*)::text
            FROM cypher('loot_tables', \$\$ MATCH (n) RETURN true \$\$) AS (x agtype);

            -- Count edges
            SELECT 'Total Edges: ' || COUNT(*)::text
            FROM cypher('loot_tables', \$\$ MATCH ()-[r]->() RETURN true \$\$) AS (x agtype);
        " 2>/dev/null || echo "  Count queries failed"

        # Sample nodes
        echo "Sample Nodes:"
        docker exec cephalon-onni-postgres psql -U user -d cephalon_db -c "
            LOAD 'age';
            SET search_path = ag_catalog, public;

            SELECT * FROM cypher('loot_tables', \$\$ MATCH (n) RETURN n LIMIT 3 \$\$) AS (n agtype);
        " 2>/dev/null | head -10 || echo "  Sample query failed"

        # Check if graph has data
        echo "Graph Status:"
        node_count=$(docker exec cephalon-onni-postgres psql -U user -d cephalon_db -t -A -c "
            LOAD 'age';
            SET search_path = ag_catalog, public;

            SELECT COUNT(*) FROM cypher('loot_tables', \$\$ MATCH (n) RETURN n \$\$) AS (n agtype);
        " 2>/dev/null | grep -oE '[0-9]+' | head -1)

        if [ -n "$node_count" ] && [ "$node_count" -gt 0 ]; then
            echo "  ✓ Graph has $node_count nodes!"
        else
            echo "  ✗ Graph is empty or inaccessible"
        fi

    else
        echo "Cephalon-Onni backend container is not running"
        echo "Please start the containers first:"
        echo "  cd $PROJECT_ROOT && docker compose up -d"
        exit 1
    fi

else
    echo "Cannot access Docker daemon"
    echo "Please either:"
    echo "  1. Add your user to docker group: sudo usermod -aG docker \$USER"
    echo "  2. Use sudo for this script"
    exit 1
fi
