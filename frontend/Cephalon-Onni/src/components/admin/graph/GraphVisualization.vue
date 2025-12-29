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
                    <div class="stat-label">Total Nodes</div>
                    <div class="stat-value">{{ graphData?.nodes?.length || 0 }}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Total Edges</div>
                    <div class="stat-value">{{ graphData?.edges?.length || 0 }}</div>
                </div>
            </div>

            <h3 v-if="selectedNode">
                Graph for {{ selectedNode.name }} ({{
                    selectedNode.label
                }})
            </h3>

<!-- Nodes Section -->
            <div class="section" v-if="graphData?.nodes?.length">
                <h4>Nodes ({{ graphData.nodes.length }})</h4>
                <div class="nodes-grid">
                    <div
                        v-for="node in graphData.nodes"
                        :key="node.id"
                        class="node-card"
                        :class="{ 'selected-node': selectedNode?.id === node.id }"
                    >
                        <div class="node-header">
                            <div class="node-name">{{ node.name }}</div>
                            <span class="type-badge">{{ node.type }}</span>
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

<!-- Edges Section -->
            <div class="section" v-if="graphData?.edges?.length">
                <h4>Edges ({{ graphData.edges.length }})</h4>
                <div class="edges-grid">
                    <div
                        v-for="edge in graphData.edges"
                        :key="edge.id"
                        class="edge-card"
                    >
                        <div class="edge-header">
                            <span class="relationship-badge">{{ edge.relationship_type }}</span>
                            <div class="edge-direction">
                                {{ getEdgeDisplay(edge) }}
                            </div>
                        </div>
                        <div class="edge-properties">
                            <div
                                v-for="(value, key) in edge.properties"
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
            <div v-else id="graph-canvas" style="display: none"></div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useGraphApi } from "@/composables/useGraphApi";
import {
    usePersistentData,
    GraphNode,
    NodeNeighborsResponse,
    GraphResponse,
} from "@/composables/usePersistentData";

const loading = ref(false);
const { searchNodes, loadNodeNeighbors } = useGraphApi();
const { getVisualizationData, setVisualizationData } = usePersistentData();

// Initialize from persistent data
const persistentData = getVisualizationData();

const searchName = ref(persistentData.searchName);
const searchLabel = ref(persistentData.searchLabel);
const selectedNode = ref<GraphNode | null>(persistentData.selectedNode);
const searchResults = ref<GraphNode[]>(persistentData.searchResults);
const graphData = ref<GraphResponse | null>(persistentData.graphData);

// Watch for changes and save to persistent storage
watch(
    [searchName, searchLabel, selectedNode, searchResults, graphData],
    () => {
        setVisualizationData({
            searchName: searchName.value,
            searchLabel: searchLabel.value,
            selectedNode: selectedNode.value,
            searchResults: searchResults.value,
            graphData: graphData.value,
        });
    },
    { deep: true },
);

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
    searchLabel.value = node.label;
    handleLoadNodeNeighbors();
}

async function handleLoadNodeNeighbors() {
    if (!selectedNode.value) return;

    loading.value = true;

    try {
        const result = await loadNodeNeighbors(
            selectedNode.value.name,
            selectedNode.value.label,
        );

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

// Helper function to get edge display text
function getEdgeDisplay(edge: any) {
    const fromNode = graphData.value?.nodes?.find(n => n.id === edge.from_node);
    const toNode = graphData.value?.nodes?.find(n => n.id === edge.to_node);
    return `${fromNode?.name || edge.from_node} → ${toNode?.name || edge.to_node}`;
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
