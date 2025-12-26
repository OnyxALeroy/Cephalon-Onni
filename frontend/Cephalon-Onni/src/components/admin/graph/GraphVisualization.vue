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

            <!-- Node Exploration Section -->
            <div v-if="selectedNode" class="exploration-section">
                <h3>Explore Node Neighbors</h3>
                <div class="selected-node">
                    <div class="selected-info">
                        <span class="selected-label">Selected Node:</span>
                        <span class="selected-name">{{
                            selectedNode.name
                        }}</span>
                        <span class="selected-label"
                            >({{ selectedNode.label }})</span
                        >
                    </div>
                </div>

                <div class="control-buttons">
                    <button
                        class="btn primary"
                        @click="handleLoadNodeNeighbors"
                        :disabled="loading"
                    >
                        {{ loading ? "Loading..." : "Load Neighbors" }}
                    </button>
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
            <div v-else-if="graphData" class="neighbors-table-container">
                <h3 v-if="selectedNode">
                    Direct Neighbors of {{ selectedNode.name }} ({{
                        selectedNode.label
                    }})
                </h3>
                <div
                    v-if="firstDepthNeighbors.length === 0"
                    class="empty-state"
                >
                    <p>No direct neighbors found for this node</p>
                </div>
                <table v-else class="neighbors-table">
                    <thead>
                        <tr>
                            <th>Node Name</th>
                            <th>Type</th>
                            <th>Properties</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr
                            v-for="neighbor in firstDepthNeighbors"
                            :key="neighbor.id"
                        >
                            <td class="node-name-cell">{{ neighbor.name }}</td>
                            <td class="node-type-cell">
                                <span class="type-badge">{{
                                    neighbor.type
                                }}</span>
                            </td>
                            <td class="properties-cell">
                                <div class="properties-list">
                                    <div
                                        v-for="(
                                            value, key
                                        ) in neighbor.properties"
                                        :key="key"
                                        class="property-item"
                                    >
                                        <span class="prop-key">{{ key }}:</span>
                                        <span class="prop-value">{{
                                            value
                                        }}</span>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div v-else id="graph-canvas" style="display: none"></div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useGraphApi } from "@/composables/useGraphApi";

const loading = ref(false);
const searchName = ref("");
const searchLabel = ref("");
const selectedNode = ref<any>(null);
const searchResults = ref<any[]>([]);
const graphData = ref<any>(null);

const { searchNodes, loadNodeNeighbors } = useGraphApi();

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

// Get neighbors for table display
const firstDepthNeighbors = computed(() => {
    if (!graphData.value || !graphData.value.neighbors) {
        return [];
    }
    
    // Return the neighbors directly from the new API response
    return graphData.value.neighbors;
});
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

.node-name-cell {
    font-weight: bold;
    color: #38bdf8;
}

.node-type-cell {
    text-align: center;
}

.type-badge {
    background: #38bdf8;
    color: #021019;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
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
