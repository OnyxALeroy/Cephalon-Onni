<template>
    <div class="graph-visualization">
        <div class="graph-controls">
            <div class="search-section">
                <h3>Loot Tables Node Search</h3>
                <div class="input-group">
                    <div class="input-field">
                        <label for="node-name">Node Name:</label>
                    <input
                        id="node-name"
                        v-model="searchName"
                        type="text"
                        placeholder="Enter node name"
                        class="node-input"
                        @keyup.enter="handleSearchNodes"
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
                    <div class="results-table">
                        <div class="table-header">
                            <div class="header-cell">Name</div>
                            <div class="header-cell">Type</div>
                        </div>
                        <div class="table-body">
                            <div
                                v-for="node in searchResults"
                                :key="node.id"
                                class="table-row"
                                @click="selectNode(node)"
                            >
                                <div class="table-cell name-cell">
                                    {{ node.name || "Unknown" }}
                                </div>
                                <div class="table-cell type-cell">
                                    <span class="type-badge">
                                        {{
                                            Array.isArray(node.label)
                                                ? node.label[0]
                                                : String(node.label)
                                        }}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Neighbors Table Container -->
        <div class="graph-container">
            <div v-if="!graphData && !loading" class="empty-state">
                <p>
                    Search for a node by name and/or label to explore its
                    neighbors
                </p>
            </div>
            <div v-else-if="graphData" class="graph-summary-container">
                <div class="graph-stats">
                    <div class="stat-item">
                        <div class="stat-label">Total Neighbors</div>
                        <div class="stat-value">
                            {{ graphData?.neighbors?.length || 0 }}
                        </div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Starting Node</div>
                        <div class="stat-value">
                            {{ graphData?.starting_node?.name || "None" }}
                        </div>
                    </div>
                </div>

                <h3 v-if="graphData?.starting_node">
                    Neighbors of {{ graphData.starting_node.name }} ({{
                        graphData.starting_node.label
                    }})
                </h3>

                <!-- Starting Node Section -->
                <div class="section" v-if="graphData?.starting_node">
                    <h4>Starting Node</h4>
                    <div class="nodes-grid">
                        <div class="node-card selected-node">
                            <div class="node-header">
                                <div class="node-name">
                                    {{ graphData.starting_node.name }}
                                </div>
                                <span class="type-badge">{{
                                    graphData.starting_node.type
                                }}</span>
                            </div>
                            <div class="node-properties">
                                <div
                                    v-for="(value, key) in graphData
                                        .starting_node.properties"
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

                <!-- Neighbors Tree Section -->
                <div class="section" v-if="graphData?.neighbors?.length">
                    <div class="tree-container">
                        <!-- Incoming Neighbors (Left Side) -->
                        <div class="tree-side incoming-side">
                            <h4>
                                Incoming Connections ({{
                                    incomingNeighbors.length
                                }})
                            </h4>
                            <div class="tree-nodes">
                                <div
                                    v-for="neighbor in incomingNeighbors"
                                    :key="neighbor.id"
                                    class="tree-node incoming-node"
                                    @click="selectNeighbor(neighbor)"
                                >
                                    <div class="tree-node-header">
                                        <div class="tree-node-name">
                                            {{ neighbor.name }}
                                        </div>
                                        <span class="type-badge">{{
                                            neighbor.type
                                        }}</span>
                                    </div>
                                    <div class="tree-relationship">
                                        <span class="relationship-badge">{{
                                            neighbor.relationship_type
                                        }}</span>
                                        <span class="direction-badge incoming"
                                            >→</span
                                        >
                                    </div>
                                    <div class="tree-node-properties">
                                        <div
                                            v-for="(
                                                value, key
                                            ) in neighbor.properties"
                                            :key="key"
                                            class="property-item"
                                        >
                                            <span class="prop-key"
                                                >{{ key }}:</span
                                            >
                                            <span class="prop-value">{{
                                                value
                                            }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Center Node -->
                        <div class="tree-center">
                            <div class="center-node">
                                <div class="center-node-header">
                                    <div class="center-node-name">
                                        {{ graphData.starting_node.name }}
                                    </div>
                                    <span class="type-badge center-badge">{{
                                        graphData.starting_node.type
                                    }}</span>
                                </div>
                                <div class="center-node-properties">
                                    <div
                                        v-for="(value, key) in graphData
                                            .starting_node.properties"
                                        :key="key"
                                        class="property-item"
                                    >
                                        <span class="prop-key">{{ key }}:</span>
                                        <span class="prop-value">{{
                                            value
                                        }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Outgoing Neighbors (Right Side) -->
                        <div class="tree-side outgoing-side">
                            <h4>
                                Outgoing Connections ({{
                                    outgoingNeighbors.length
                                }})
                            </h4>
                            <div class="tree-nodes">
                                <div
                                    v-for="neighbor in outgoingNeighbors"
                                    :key="neighbor.id"
                                    class="tree-node outgoing-node"
                                    @click="selectNeighbor(neighbor)"
                                >
                                    <div class="tree-node-header">
                                        <div class="tree-node-name">
                                            {{ neighbor.name }}
                                        </div>
                                        <span class="type-badge">{{
                                            neighbor.type
                                        }}</span>
                                    </div>
                                    <div class="tree-relationship">
                                        <span class="direction-badge outgoing"
                                            >→</span
                                        >
                                        <span class="relationship-badge">{{
                                            neighbor.relationship_type
                                        }}</span>
                                    </div>
                                    <div class="tree-node-properties">
                                        <div
                                            v-for="(
                                                value, key
                                            ) in neighbor.properties"
                                            :key="key"
                                            class="property-item"
                                        >
                                            <span class="prop-key"
                                                >{{ key }}:</span
                                            >
                                            <span class="prop-value">{{
                                                value
                                            }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else id="graph-canvas" style="display: none"></div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";

interface GraphNode {
    id: string;
    name: string;
    type: string;
    label: string;
    properties: Record<string, any>;
}

interface GraphEdge {
    id: string;
    from_node: string;
    to_node: string;
    relationship_type: string;
    properties: Record<string, any>;
}

interface NodeNeighbor {
    id: string;
    name: string;
    type: string;
    properties: Record<string, any>;
    relationship_type: string;
    relationship_properties: Record<string, any>;
    relationship_direction: "outgoing" | "incoming";
}

interface GraphResponse {
    nodes: GraphNode[];
    edges: GraphEdge[];
}

interface NodeNeighborsResponse {
    starting_node: GraphNode;
    neighbors: NodeNeighbor[];
    count: number;
}

interface NodeSearchResponse {
    nodes: GraphNode[];
}

interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
}

const loading = ref(false);

// Reactive state
const searchName = ref("");
const searchLabel = ref("");
const selectedNode = ref<GraphNode | null>(null);
const searchResults = ref<GraphNode[]>([]);
const graphData = ref<NodeNeighborsResponse | null>(null);

// API call to search nodes in loottables
async function searchNodes(
    name: string,
    label: string,
): Promise<ApiResponse<NodeSearchResponse>> {
    try {
        const params = new URLSearchParams();
        if (name) params.append("name", name);
        if (label) params.append("label", label);

        const response = await fetch(`/api/loottables/search/nodes?${params}`, {
            credentials: "include",
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return {
            success: true,
            data: data,
        };
    } catch (error) {
        console.error("Error searching nodes:", error);
        return {
            success: false,
            error: error instanceof Error ? error.message : "Unknown error",
        };
    }
}

// API call to get node neighbors
async function loadNodeNeighbors(
    name: string,
): Promise<ApiResponse<NodeNeighborsResponse>> {
    try {
        const params = new URLSearchParams();
        params.append("name", name);

        const response = await fetch(`/api/loottables/neighbors?${params}`, {
            credentials: "include",
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return {
            success: true,
            data: data,
        };
    } catch (error) {
        console.error("Error loading node neighbors:", error);
        return {
            success: false,
            error: error instanceof Error ? error.message : "Unknown error",
        };
    }
}

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
function selectNode(node: GraphNode) {
    selectedNode.value = node;
    searchResults.value = [];
    searchName.value = node.name;
    searchLabel.value = ""; // Clear label to avoid reuse
    handleLoadNodeNeighbors();
}

// Select a neighbor node
function selectNeighbor(neighbor: NodeNeighbor) {
    const neighborNode: GraphNode = {
        id: neighbor.id,
        name: neighbor.name,
        type: neighbor.type,
        label: neighbor.type, // Use type as label since it's not provided
        properties: neighbor.properties,
    };
    selectNode(neighborNode);
}

async function handleLoadNodeNeighbors() {
    if (!selectedNode.value) return;

    loading.value = true;

    try {
        const result = await loadNodeNeighbors(selectedNode.value.name);

        if (result.success && result.data) {
            graphData.value = result.data;
        } else {
            graphData.value = null;
        }
    } catch (e) {
        console.error(e);
        graphData.value = null;
    } finally {
        loading.value = false;
    }
}

// Computed properties to separate neighbors by direction
const incomingNeighbors = computed(() => {
    const neighbors = graphData.value?.neighbors || [];
    console.log("All neighbors:", neighbors);
    const incoming = neighbors.filter(
        (n) => n.relationship_direction === "incoming",
    );
    console.log("Incoming neighbors:", incoming);
    return incoming;
});

const outgoingNeighbors = computed(() => {
    const neighbors = graphData.value?.neighbors || [];
    const outgoing = neighbors.filter(
        (n) => n.relationship_direction === "outgoing",
    );
    console.log("Outgoing neighbors:", outgoing);
    return outgoing;
});

// Helper function to get neighbor display text
function getNeighborDisplay(neighbor: NodeNeighbor) {
    const startNode = graphData.value?.starting_node;
    if (neighbor.relationship_direction === "outgoing") {
        return `${startNode?.name || "Unknown"} → ${neighbor.name}`;
    } else {
        return `${neighbor.name} → ${startNode?.name || "Unknown"}`;
    }
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
    grid-template-columns: 1fr;
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
    grid-template-columns: 1fr;
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

.results-table {
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid #475569;
    border-radius: 4px;
    background: #0f172a;
}

.table-header {
    display: flex;
    background: #1e293b;
    border-bottom: 2px solid #334155;
    position: sticky;
    top: 0;
    z-index: 1;
}

.header-cell {
    flex: 1;
    padding: 0.8rem;
    color: #7dd3fc;
    font-weight: 600;
    text-align: left;
}

.table-body {
    display: flex;
    flex-direction: column;
}

.table-row {
    display: flex;
    border-bottom: 1px solid #334155;
    cursor: pointer;
    transition: background-color 0.2s;
}

.table-row:hover {
    background: #334155;
}

.table-row:last-child {
    border-bottom: none;
}

.table-cell {
    flex: 1;
    padding: 0.6rem 0.8rem;
    color: #f1f5f9;
    display: flex;
    align-items: center;
}

.name-cell {
    font-weight: 600;
    color: #38bdf8;
}

.type-cell {
    justify-content: flex-start;
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

.graph-summary-container {
    background: #08121f;
    border-radius: 4px;
    padding: 1.5rem;
    overflow: auto;
}

.graph-summary-container h3 {
    color: #7dd3fc;
    margin-bottom: 1.5rem;
    font-size: 1.2rem;
    text-align: center;
}

.graph-summary-container h4 {
    color: #94a3b8;
    margin: 1.5rem 0 1rem 0;
    font-size: 1.1rem;
}

.section {
    margin-bottom: 2rem;
}

.nodes-grid,
.edges-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
}

.node-card,
.edge-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 1rem;
    transition: background-color 0.2s;
}

.node-card:hover,
.edge-card:hover {
    background: #334155;
}

.node-card.selected-node {
    border-color: #38bdf8;
    background: #1e3a8a;
}

.node-header,
.edge-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
}

.node-name {
    color: #38bdf8;
    font-weight: bold;
    font-size: 1rem;
}

.edge-direction {
    color: #94a3b8;
    font-size: 0.9rem;
    text-align: center;
    margin-top: 0.5rem;
}

.node-properties,
.edge-properties {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
}

.node-properties .property-item,
.edge-properties .property-item {
    display: flex;
    gap: 0.5rem;
    font-size: 0.8rem;
    background: #0f172a;
    padding: 0.3rem 0.5rem;
    border-radius: 3px;
}

.node-properties .prop-key,
.edge-properties .prop-key {
    color: #94a3b8;
    min-width: 80px;
    font-weight: 600;
}

.node-properties .prop-value,
.edge-properties .prop-value {
    color: #38bdf8;
    word-break: break-word;
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
    min-height: 200px;
    color: #64748b;
    font-size: 1.1rem;
    padding: 2rem;
}

.neighbors-table-container {
    background: #08121f;
    border-radius: 4px;
    padding: 1.5rem;
    overflow: auto;
}

.neighbors-table-container h3 {
    color: #7dd3fc;
    margin-bottom: 1rem;
    font-size: 1.2rem;
    text-align: center;
}

.neighbors-table {
    width: 100%;
    border-collapse: collapse;
    background: #0f172a;
    border-radius: 4px;
    overflow: hidden;
}

.neighbors-table th {
    background: #1e293b;
    color: #7dd3fc;
    padding: 0.8rem 1rem;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid #334155;
}

.neighbors-table td {
    padding: 0.8rem 1rem;
    border-bottom: 1px solid #334155;
    color: #f1f5f9;
}

.neighbors-table tr:hover {
    background: #1e293b;
}

.node-id-cell {
    font-family: monospace;
    color: #94a3b8;
    font-size: 0.8rem;
    max-width: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.node-name-cell {
    font-weight: bold;
    color: #38bdf8;
}

.node-type-cell {
    text-align: center;
}

.relationship-cell {
    text-align: center;
}

.direction-cell {
    text-align: center;
}

.direction-badge {
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.direction-badge.outgoing {
    background: #10b981;
    color: #021019;
}

.direction-badge.incoming {
    background: #ef4444;
    color: #ffffff;
}

.type-badge {
    background: #38bdf8;
    color: #021019;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.relationship-badge {
    background: #f59e0b;
    color: #021019;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.relationship-properties-cell {
    max-width: 250px;
}

.properties-cell {
    max-width: 300px;
}

.properties-list {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
}

.properties-cell .property-item {
    display: flex;
    gap: 0.5rem;
    font-size: 0.8rem;
    background: #1e293b;
    padding: 0.3rem 0.5rem;
    border-radius: 3px;
}

.properties-cell .prop-key {
    color: #94a3b8;
    min-width: 80px;
    font-weight: 600;
}

.properties-cell .prop-value {
    color: #38bdf8;
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

/* Tree Layout Styles */
.tree-container {
    display: flex;
    align-items: flex-start;
    gap: 2rem;
    min-height: 400px;
    padding: 2rem 0;
}

.tree-side {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.tree-side h4 {
    color: #7dd3fc;
    margin-bottom: 1rem;
    font-size: 1rem;
    text-align: center;
}

.tree-nodes {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-height: 500px;
    overflow-y: auto;
}

.tree-node {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
}

.tree-node:hover {
    background: #334155;
    transform: translateX(5px);
}

.incoming-node:hover {
    transform: translateX(-5px);
}

.tree-node-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.tree-node-name {
    color: #38bdf8;
    font-weight: bold;
    font-size: 0.9rem;
    word-break: break-word;
}

.tree-relationship {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    font-size: 0.8rem;
}

.tree-node-properties {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}

.tree-node-properties .property-item {
    display: flex;
    gap: 0.5rem;
    font-size: 0.75rem;
    background: #0f172a;
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
}

.tree-node-properties .prop-key {
    color: #94a3b8;
    min-width: 60px;
    font-weight: 600;
}

.tree-node-properties .prop-value {
    color: #38bdf8;
    word-break: break-word;
}

.tree-center {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 300px;
}

.center-node {
    background: #1e3a8a;
    border: 2px solid #38bdf8;
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
    position: relative;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
}

.center-node-header {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.center-node-name {
    color: #7dd3fc;
    font-weight: bold;
    font-size: 1.1rem;
}

.center-badge {
    background: #38bdf8;
    color: #021019;
    padding: 0.3rem 0.8rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.center-node-properties {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    text-align: left;
}

.center-node-properties .property-item {
    display: flex;
    gap: 0.5rem;
    font-size: 0.8rem;
    background: #1e293b;
    padding: 0.3rem 0.5rem;
    border-radius: 3px;
}

.center-node-properties .prop-key {
    color: #94a3b8;
    min-width: 70px;
    font-weight: 600;
}

.center-node-properties .prop-value {
    color: #7dd3fc;
    word-break: break-word;
}

/* Connection lines visual indicator */
.incoming-node::after {
    content: "→";
    position: absolute;
    right: -15px;
    top: 50%;
    transform: translateY(-50%);
    color: #ef4444;
    font-size: 1.2rem;
}

.outgoing-node::before {
    content: "→";
    position: absolute;
    left: -15px;
    top: 50%;
    transform: translateY(-50%);
    color: #10b981;
    font-size: 1.2rem;
}

.debug-info {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.debug-info h4 {
    color: #7dd3fc;
    margin-bottom: 0.5rem;
}

.debug-info p {
    color: #94a3b8;
    margin: 0.25rem 0;
}

.debug-info pre {
    background: #0f172a;
    color: #f1f5f9;
    padding: 1rem;
    border-radius: 4px;
    overflow: auto;
    font-size: 0.8rem;
    max-height: 300px;
}

.debug-info details {
    margin-top: 1rem;
}

.debug-info summary {
    color: #38bdf8;
    cursor: pointer;
    padding: 0.5rem;
    background: #0f172a;
    border-radius: 4px;
    border: 1px solid #475569;
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
