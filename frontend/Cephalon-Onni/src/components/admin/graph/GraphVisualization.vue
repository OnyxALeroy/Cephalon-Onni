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
                            class="btn btn-ghost"
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
    background: var(--bg-elevated);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-sm);
    padding: var(--space-6);
}

.graph-controls {
    display: grid;
    gap: var(--space-8);
    margin-bottom: var(--space-8);
    grid-template-columns: 1fr;
}

.search-section,
.exploration-section {
    background: var(--bg-elevated-2);
    border: 1px solid var(--border-secondary);
    border-radius: var(--radius-sm);
    padding: var(--space-4);
}

.search-section h3,
.exploration-section h3 {
    color: var(--accent-subtle);
    margin-bottom: var(--space-4);
    font-size: var(--text-lg);
}

.search-section h4 {
    color: var(--text-muted-2);
    margin: var(--space-4) 0 var(--space-2) 0;
    font-size: var(--text-body);
}

.input-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-4);
    margin-bottom: var(--space-4);
}

.input-field {
    display: flex;
    flex-direction: column;
}

.input-field label {
    color: var(--text-muted-2);
    font-size: var(--text-body);
    margin-bottom: var(--space-2);
}

.node-input {
    background: var(--bg-elevated);
    border: 1px solid var(--border-input);
    border-radius: var(--radius-sm);
    color: var(--text-light);
    padding: 0.7rem;
    font-size: var(--text-body);
}

.node-input:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(var(--accent-rgb), 0.2);
}

.depth-select {
    background: var(--bg-elevated);
    border: 1px solid var(--border-input);
    border-radius: var(--radius-sm);
    color: var(--text-light);
    padding: 0.7rem;
    font-size: var(--text-body);
}

.depth-select:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(var(--accent-rgb), 0.2);
}

.search-buttons,
.control-buttons {
    display: flex;
    gap: var(--space-4);
    margin-bottom: var(--space-4);
    flex-wrap: wrap;
}

.search-results {
    margin-top: var(--space-4);
}

.results-list {
    max-height: 200px;
    overflow-y: auto;
    border: 1px solid var(--border-input);
    border-radius: var(--radius-sm);
    background: var(--bg-elevated);
}

.result-item {
    padding: 0.8rem;
    border-bottom: 1px solid var(--border-secondary);
    cursor: pointer;
    transition: background-color var(--transition-normal);
}

.result-item:hover {
    background: var(--border-secondary);
}

.result-item:last-child {
    border-bottom: none;
}

.node-name {
    color: var(--text-light);
    font-weight: bold;
    margin-bottom: var(--space-1);
    font-size: var(--text-normal);
}

.node-label {
    color: var(--accent);
    font-size: var(--text-body);
    margin-bottom: var(--space-2);
    font-weight: 600;
}

.node-properties {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
}

.property-item {
    display: flex;
    gap: var(--space-2);
    font-size: var(--text-base);
}

.prop-key {
    color: var(--text-muted);
    min-width: 60px;
}

.prop-value {
    color: var(--text-muted-2);
}

.selected-node {
    margin-bottom: var(--space-4);
    padding: 0.8rem;
    background: var(--bg-elevated);
    border: 1px solid var(--border-input);
    border-radius: var(--radius-sm);
}

.selected-info {
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.selected-label {
    color: var(--text-muted-2);
    font-size: var(--text-body);
}

.selected-name {
    color: var(--accent);
    font-weight: bold;
}

.graph-stats {
    display: flex;
    gap: var(--space-8);
    margin-bottom: var(--space-4);
    padding: var(--space-4);
    background: var(--bg-elevated-2);
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-secondary);
}

.graph-summary-container {
    background: var(--bg-surface);
    border-radius: var(--radius-sm);
    padding: var(--space-6);
    overflow: auto;
}

.graph-summary-container h3 {
    color: var(--accent-subtle);
    margin-bottom: var(--space-6);
    font-size: var(--text-xl);
    text-align: center;
}

.graph-summary-container h4 {
    color: var(--text-muted-2);
    margin: var(--space-6) 0 var(--space-4) 0;
    font-size: var(--text-lg);
}

.section {
    margin-bottom: var(--space-8);
}

.nodes-grid,
.edges-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: var(--space-4);
    margin-bottom: var(--space-4);
}

.node-card,
.edge-card {
    background: var(--bg-elevated-2);
    border: 1px solid var(--border-secondary);
    border-radius: var(--radius-sm);
    padding: var(--space-4);
    transition: background-color var(--transition-normal);
}

.node-card:hover,
.edge-card:hover {
    background: var(--border-secondary);
}

.node-card.selected-node {
    border-color: var(--accent);
    background: var(--blue-selected);
}

.node-header,
.edge-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
}

.node-name {
    color: var(--accent);
    font-weight: bold;
    font-size: var(--text-normal);
}

.edge-direction {
    color: var(--text-muted-2);
    font-size: var(--text-body);
    text-align: center;
    margin-top: var(--space-2);
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
    gap: var(--space-2);
    font-size: var(--text-base);
    background: var(--bg-elevated);
    padding: 0.3rem var(--space-2);
    border-radius: 3px;
}

.node-properties .prop-key,
.edge-properties .prop-key {
    color: var(--text-muted-2);
    min-width: 80px;
    font-weight: 600;
}

.node-properties .prop-value,
.edge-properties .prop-value {
    color: var(--accent);
    word-break: break-word;
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-label {
    color: var(--text-muted-2);
    font-size: var(--text-base);
    margin-bottom: var(--space-1);
}

.stat-value {
    color: var(--accent-subtle);
    font-weight: bold;
    font-size: var(--text-lg);
}

.graph-container {
    background: var(--bg-surface);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-sm);
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
    color: var(--text-muted);
    font-size: var(--text-lg);
    padding: var(--space-8);
}

.neighbors-table-container {
    background: var(--bg-surface);
    border-radius: var(--radius-sm);
    padding: var(--space-6);
    overflow: auto;
}

.neighbors-table-container h3 {
    color: var(--accent-subtle);
    margin-bottom: var(--space-4);
    font-size: var(--text-xl);
    text-align: center;
}

.neighbors-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--bg-elevated);
    border-radius: var(--radius-sm);
    overflow: hidden;
}

.neighbors-table th {
    background: var(--bg-elevated-2);
    color: var(--accent-subtle);
    padding: 0.8rem var(--space-4);
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid var(--border-secondary);
}

.neighbors-table td {
    padding: 0.8rem var(--space-4);
    border-bottom: 1px solid var(--border-secondary);
    color: var(--text-light);
}

.neighbors-table tr:hover {
    background: var(--bg-elevated-2);
}

.node-id-cell {
    font-family: monospace;
    color: var(--text-muted-2);
    font-size: var(--text-base);
    max-width: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.node-name-cell {
    font-weight: bold;
    color: var(--accent);
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
    border-radius: var(--radius-full);
    font-size: var(--text-base);
    font-weight: 600;
}

.direction-badge.outgoing {
    background: var(--success-alt);
    color: var(--text-on-accent);
}

.direction-badge.incoming {
    background: var(--danger);
    color: var(--text-white);
}

.type-badge {
    background: var(--accent);
    color: var(--text-on-accent);
    padding: 0.2rem 0.6rem;
    border-radius: var(--radius-full);
    font-size: var(--text-base);
    font-weight: 600;
}

.relationship-badge {
    background: var(--warning);
    color: var(--text-on-accent);
    padding: 0.2rem 0.6rem;
    border-radius: var(--radius-full);
    font-size: var(--text-base);
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
    gap: var(--space-2);
    font-size: var(--text-base);
    background: var(--bg-elevated-2);
    padding: 0.3rem var(--space-2);
    border-radius: 3px;
}

.properties-cell .prop-key {
    color: var(--text-muted-2);
    min-width: 80px;
    font-weight: 600;
}

.properties-cell .prop-value {
    color: var(--accent);
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
        gap: var(--space-4);
    }

    .control-buttons,
    .search-buttons {
        justify-content: center;
    }
}
</style>
