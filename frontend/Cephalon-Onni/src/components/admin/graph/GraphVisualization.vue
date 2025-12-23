<template>
    <div class="graph-visualization">
        <div class="graph-controls">
            <div class="search-section">
                <h3>Node Search</h3>
                <div class="input-group">
                    <div class="input-field">
                        <label for="node-name">Node Name:</label>
                        <input
                            id="node-name"
                            v-model="searchName"
                            type="text"
                            placeholder="Enter node name"
                            class="node-input"
                        />
                    </div>
                    <div class="input-field">
                        <label for="node-label">Node Label:</label>
                        <input
                            id="node-label"
                            v-model="searchLabel"
                            type="text"
                            placeholder="Enter node label"
                            class="node-input"
                        />
                    </div>
                </div>
                <div class="search-buttons">
                    <button
                        class="btn secondary"
                        @click="handleSearchNodes"
                        :disabled="
                            loading ||
                            (!searchName.trim() && !searchLabel.trim())
                        "
                    >
                        {{ loading ? "Searching..." : "Search Nodes" }}
                    </button>
                </div>

                <!-- Search Results -->
                <div v-if="searchResults.length > 0" class="search-results">
                    <h4>Found Nodes ({{ searchResults.length }})</h4>
                    <div class="results-list">
                        <div
                            v-for="node in searchResults"
                            :key="node.id"
                            class="result-item"
                            @click="selectNode(node)"
                        >
                            <div class="node-name">
                                {{ node.name || "Unknown" }}
                            </div>
                            <div class="node-label">
                                {{
                                    Array.isArray(node.label)
                                        ? node.label
                                        : String(node.label)
                                }}
                            </div>
                            <div class="node-properties">
                                <div
                                    v-for="(value, key) in node.properties"
                                    :key="key"
                                    class="property-item"
                                >
                                    <span class="prop-key">{{ key }}:</span>
                                    <span class="prop-value">{{ value }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="exploration-section">
                <h3>Explore Neighbors</h3>
                <div v-if="selectedNode" class="selected-node">
                    <div class="selected-info">
                        <span class="selected-label">Selected:</span>
                        <span class="selected-name"
                            >{{ selectedNode.name }} ({{
                                Array.isArray(selectedNode.label)
                                    ? selectedNode.label[0]
                                    : String(selectedNode.label)
                            }})</span
                        >
                    </div>
                </div>
                <div class="input-group">
                    <div class="input-field">
                        <label for="depth">Depth:</label>
                        <select
                            id="depth"
                            v-model="selectedDepth"
                            class="depth-select"
                        >
                            <option
                                v-for="d in depthOptions"
                                :key="d"
                                :value="d"
                            >
                                {{ d }}
                            </option>
                        </select>
                    </div>
                </div>
                <div class="control-buttons">
                    <button
                        class="btn primary"
                        @click="handleLoadNodeNeighbors"
                        :disabled="loading || !selectedNode"
                    >
                        {{ loading ? "Loading..." : "Explore Neighbors" }}
                    </button>
                    <button
                        class="btn secondary"
                        @click="handleRefreshGraph"
                        :disabled="!selectedNode"
                    >
                        Refresh
                    </button>
                    <button class="btn secondary" @click="resetZoom">
                        Reset Zoom
                    </button>
                </div>
            </div>
        </div>

        <!-- Graph Stats -->
        <div v-if="graphStats" class="graph-stats">
            <div class="stat-item">
                <span class="stat-label">Nodes:</span>
                <span class="stat-value">{{ graphStats.totalNodes }}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Edges:</span>
                <span class="stat-value">{{ graphStats.totalEdges }}</span>
            </div>
            <div v-if="selectedNode" class="stat-item">
                <span class="stat-label">Start Node:</span>
                <span class="stat-value">{{ selectedNode.name }}</span>
            </div>
            <div v-if="graphStats.depth" class="stat-item">
                <span class="stat-label">Depth:</span>
                <span class="stat-value">{{ graphStats.depth }}</span>
            </div>
        </div>

        <!-- Graph Container -->
        <div class="graph-container" ref="graphContainer">
            <div v-if="!graphData && !loading" class="empty-state">
                <p>
                    Search for a node by name and/or label to explore the graph
                </p>
            </div>
            <div id="graph-canvas"></div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useGraphApi } from "@/composables/useGraphApi";

const graphContainer = ref<HTMLElement>();
const loading = ref(false);
const searchName = ref("");
const searchLabel = ref("");
const selectedDepth = ref(2);
const selectedNode = ref<any>(null);
const searchResults = ref<any[]>([]);
const graphData = ref<any>(null);

const depthOptions = [1, 2, 3, 4, 5];

const { searchNodes, loadNodeNeighbors, updateGraphStats } = useGraphApi();

const graphStats = computed(() => {
    if (!graphData.value?.stats) return null;
    return graphData.value.stats;
});

// Search for nodes by name and/or label
async function handleSearchNodes() {
    if (!searchName.value.trim() && !searchLabel.value.trim()) return;

    loading.value = true;
    try {
        console.log("Searching for nodes:", {
            name: searchName.value.trim(),
            label: searchLabel.value.trim(),
        });
        const result = await searchNodes(
            searchName.value.trim(),
            searchLabel.value.trim(),
        );
        console.log("Search result:", result);
        if (result.success && result.data) {
            searchResults.value = result.data.nodes;
            console.log("Found nodes:", result.data.nodes);

            // Debug each node
            result.data.nodes.forEach((node, index) => {
                console.log(`Node ${index}:`, {
                    id: node.id,
                    name: node.name,
                    label: node.label,
                    labelType: typeof node.label,
                    isArray: Array.isArray(node.label),
                    properties: node.properties,
                });
            });
        } else {
            console.log("Search failed or no data");
            searchResults.value = [];
        }
    } catch (error) {
        console.error("Search error:", error);
        searchResults.value = [];
    } finally {
        loading.value = false;
    }
}

// Select a node from search results
function selectNode(node: any) {
    selectedNode.value = node;
    searchResults.value = [];
    searchName.value = node.name;
    searchLabel.value = node.label;
}

// Load and render node neighbors
async function handleLoadNodeNeighbors() {
    if (!selectedNode.value) return;

    loading.value = true;
    try {
        console.log("Loading neighbors for:", {
            name: selectedNode.value.name,
            label: selectedNode.value.label,
            depth: selectedDepth.value,
        });
        const result = await loadNodeNeighbors(
            selectedNode.value.name,
            selectedNode.value.label,
            selectedDepth.value,
        );
        console.log("Neighbors result:", result);
        if (result.success && result.data) {
            graphData.value = result.data;
            console.log("Graph data:", result.data);
            renderGraph(result.data);
        } else {
            console.log("Failed to load neighbors");
        }
    } catch (error) {
        console.error("Error loading neighbors:", error);
    } finally {
        loading.value = false;
    }
}

// Refresh graph with current settings
async function handleRefreshGraph() {
    if (selectedNode.value) {
        await handleLoadNodeNeighbors();
    }
    await updateGraphStats();
}

// Render graph data to SVG with improved layout
function renderGraph(data: any) {
    console.log("Rendering graph with data:", data);
    const container = document.getElementById("graph-canvas");
    if (!container) {
        console.error("Graph container not found");
        return;
    }
    if (!data.nodes || !data.edges) {
        console.error("Missing nodes or edges in data:", {
            nodes: data.nodes,
            edges: data.edges,
        });
        return;
    }

    console.log(
        `Rendering ${data.nodes.length} nodes and ${data.edges.length} edges`,
    );
    container.innerHTML = "";

    // Use force-directed layout for better positioning
    const nodePositions = calculateNodePositions(data.nodes, data.edges);
    console.log("Node positions calculated:", nodePositions);

    // Create edge elements
    const edgeElements = data.edges
        .map((edge: any) => {
            const from = nodePositions.get(edge.source);
            const to = nodePositions.get(edge.target);
            if (!from || !to) return "";

            return `<line
      class="edge"
      stroke="#64748b"
      stroke-width="1"
      x1="${from.x}"
      y1="${from.y}"
      x2="${to.x}"
      y2="${to.y}"
    />`;
        })
        .join("");

    // Create node elements with different colors for start node
    const nodeElements = data.nodes
        .map((node: any) => {
            const pos = nodePositions.get(node.id);
            const isStartNode =
                node.isStartNode || data.stats?.startNodeId === node.id;
            const nodeColor = isStartNode ? "#f59e0b" : "#38bdf8";

            return `
      <g class="node" transform="translate(${pos.x}, ${pos.y})" style="cursor: pointer;">
        <circle r="25" fill="${nodeColor}" stroke="#021019" stroke-width="2"/>
        <text text-anchor="middle" dy="5" fill="white" font-size="10" font-weight="bold">
          ${node.label ? node.label.substring(0, 12) : node.id.substring(0, 12)}
        </text>
        <text y="35" text-anchor="middle" fill="#c9e5ff" font-size="8">${node.type}</text>
      </g>
    `;
        })
        .join("");

    const svgWidth = container.clientWidth || 800;
    const svgHeight = 600;

    container.innerHTML = `
    <svg width="${svgWidth}" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}">
      <style>
        .node:hover circle { filter: brightness(1.2); }
        .edge { opacity: 0.6; }
      </style>
      ${edgeElements}
      ${nodeElements}
    </svg>
  `;
}

// Calculate node positions using a simple force-directed layout
function calculateNodePositions(nodes: any[], edges: any[]) {
    const positions = new Map();
    const width = 800;
    const height = 600;
    const centerX = width / 2;
    const centerY = height / 2;

    // Initialize positions
    nodes.forEach((node, index) => {
        const angle = (index / nodes.length) * 2 * Math.PI;
        const radius = 150;
        positions.set(node.id, {
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle),
        });
    });

    // Simple force simulation
    for (let iteration = 0; iteration < 50; iteration++) {
        const forces = new Map();

        // Initialize forces
        nodes.forEach((node) => {
            forces.set(node.id, { x: 0, y: 0 });
        });

        // Repulsion between all nodes
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const pos1 = positions.get(nodes[i].id);
                const pos2 = positions.get(nodes[j].id);
                const dx = pos2.x - pos1.x;
                const dy = pos2.y - pos1.y;
                const distance = Math.sqrt(dx * dx + dy * dy) || 1;
                const force = 1000 / (distance * distance);

                const force1 = forces.get(nodes[i].id);
                const force2 = forces.get(nodes[j].id);

                force1.x -= (dx / distance) * force;
                force1.y -= (dy / distance) * force;
                force2.x += (dx / distance) * force;
                force2.y += (dy / distance) * force;
            }
        }

        // Attraction along edges
        edges.forEach((edge) => {
            const pos1 = positions.get(edge.source);
            const pos2 = positions.get(edge.target);
            const dx = pos2.x - pos1.x;
            const dy = pos2.y - pos1.y;
            const distance = Math.sqrt(dx * dx + dy * dy) || 1;
            const force = distance * 0.01;

            const force1 = forces.get(edge.source);
            const force2 = forces.get(edge.target);

            force1.x += (dx / distance) * force;
            force1.y += (dy / distance) * force;
            force2.x -= (dx / distance) * force;
            force2.y -= (dy / distance) * force;
        });

        // Apply forces
        nodes.forEach((node) => {
            const pos = positions.get(node.id);
            const force = forces.get(node.id);
            pos.x += force.x * 0.1;
            pos.y += force.y * 0.1;

            // Keep within bounds
            pos.x = Math.max(50, Math.min(width - 50, pos.x));
            pos.y = Math.max(50, Math.min(height - 50, pos.y));
        });
    }

    return positions;
}

// Reset zoom (placeholder for future graph library integration)
function resetZoom() {
    console.log("Reset zoom functionality to be implemented");
}
</script>

<style scoped>
.graph-visualization {
    background: #0f172a;
    border: 1px solid #1b2a3a;
    border-radius: 4px;
    padding: 1.5rem;
}

.graph-controls {
    display: grid;
    gap: 2rem;
    margin-bottom: 2rem;
    grid-template-columns: 1fr 1fr;
}

.search-section,
.exploration-section {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 1rem;
}

.search-section h3,
.exploration-section h3 {
    color: #7dd3fc;
    margin-bottom: 1rem;
    font-size: 1.1rem;
}

.search-section h4 {
    color: #94a3b8;
    margin: 1rem 0 0.5rem 0;
    font-size: 0.9rem;
}

.input-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
}

.input-field {
    display: flex;
    flex-direction: column;
}

.input-field label {
    color: #94a3b8;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.node-input {
    background: #0f172a;
    border: 1px solid #475569;
    border-radius: 4px;
    color: #f1f5f9;
    padding: 0.7rem;
    font-size: 0.9rem;
}

.node-input:focus {
    outline: none;
    border-color: #38bdf8;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

.depth-select {
    background: #0f172a;
    border: 1px solid #475569;
    border-radius: 4px;
    color: #f1f5f9;
    padding: 0.7rem;
    font-size: 0.9rem;
}

.depth-select:focus {
    outline: none;
    border-color: #38bdf8;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

.search-buttons,
.control-buttons {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

.search-results {
    margin-top: 1rem;
}

.results-list {
    max-height: 200px;
    overflow-y: auto;
    border: 1px solid #475569;
    border-radius: 4px;
    background: #0f172a;
}

.result-item {
    padding: 0.8rem;
    border-bottom: 1px solid #334155;
    cursor: pointer;
    transition: background-color 0.2s;
}

.result-item:hover {
    background: #334155;
}

.result-item:last-child {
    border-bottom: none;
}

.node-name {
    color: #f1f5f9;
    font-weight: bold;
    margin-bottom: 0.25rem;
    font-size: 1rem;
}

.node-label {
    color: #38bdf8;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.node-properties {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.property-item {
    display: flex;
    gap: 0.5rem;
    font-size: 0.8rem;
}

.prop-key {
    color: #64748b;
    min-width: 60px;
}

.prop-value {
    color: #94a3b8;
}

.selected-node {
    margin-bottom: 1rem;
    padding: 0.8rem;
    background: #0f172a;
    border: 1px solid #475569;
    border-radius: 4px;
}

.selected-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.selected-label {
    color: #94a3b8;
    font-size: 0.9rem;
}

.selected-name {
    color: #38bdf8;
    font-weight: bold;
}

.graph-stats {
    display: flex;
    gap: 2rem;
    margin-bottom: 1rem;
    padding: 1rem;
    background: #1e293b;
    border-radius: 4px;
    border: 1px solid #334155;
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-label {
    color: #94a3b8;
    font-size: 0.8rem;
    margin-bottom: 0.25rem;
}

.stat-value {
    color: #7dd3fc;
    font-weight: bold;
    font-size: 1.1rem;
}

.graph-container {
    background: #08121f;
    border: 1px solid #1b2a3a;
    border-radius: 4px;
    min-height: 600px;
    position: relative;
    overflow: hidden;
}

.empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 600px;
    color: #64748b;
    font-size: 1.1rem;
}

#graph-canvas {
    width: 100%;
    height: 100%;
    min-height: 600px;
}

.btn {
    padding: 0.7rem 1.5rem;
    border-radius: 4px;
    font-weight: bold;
    cursor: pointer;
    transition: 0.2s;
    font-size: 0.9rem;
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.primary {
    background: #38bdf8;
    color: #021019;
    border: none;
}

.primary:hover:not(:disabled) {
    background: #2cb1d4;
}

.secondary {
    background: transparent;
    border: 1px solid #38bdf8;
    color: #38bdf8;
}

.secondary:hover:not(:disabled) {
    background: #38bdf8;
    color: #021019;
}

@media (max-width: 768px) {
    .graph-controls {
        grid-template-columns: 1fr;
    }

    .input-group {
        grid-template-columns: 1fr;
    }

    .graph-stats {
        flex-wrap: wrap;
        gap: 1rem;
    }

    .control-buttons,
    .search-buttons {
        justify-content: center;
    }
}
</style>
