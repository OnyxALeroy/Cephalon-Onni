#!/usr/bin/env bash

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
        " 2>/dev/null | grep -E '^[0-9]+$' | head -1)

        if [[ "$node_count" =~ ^[0-9]+$ ]] && [ "$node_count" -gt 0 ]; then
            echo "  ✓ Graph has $node_count nodes - Ready for visualization!"
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
