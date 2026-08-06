<template>
    <div class="loottables-view">
        <div class="search-section">
            <h2>Loot Tables Search</h2>
            <div class="search-input-container">
                <input
                    v-model="searchName"
                    type="text"
                    placeholder="Search for items (e.g., O5, Axi O5 Relic)"
                    class="search-input"
                    @input="handleAutoSearch"
                />
                <div v-if="loading" class="loading-indicator">Searching...</div>
            </div>

            <div v-if="searchResults.length > 0" class="search-results">
                <div class="results-header">
                    <span>Found {{ searchResults.length }} results</span>
                    <button class="clear-btn" @click="clearSearch">
                        Clear
                    </button>
                </div>
                <div class="results-list">
                    <div
                        v-for="node in searchResults"
                        :key="node.id"
                        class="result-item"
                        :class="{ selected: selectedNode?.id === node.id }"
                        @click="selectNode(node)"
                    >
                        <span class="result-name">{{ node.name }}</span>
                        <span class="result-type">{{ node.type }}</span>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="selectedNode" class="sources-section">
            <h3>Sources for: {{ selectedNode.name }}</h3>

            <table v-if="sources.length > 0" class="sources-table">
                <thead>
                    <tr>
                        <th>Source</th>
                        <th>Type</th>
                        <th>Chance</th>
                        <th>Rotation</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(source, index) in sources" :key="index">
                        <td>{{ source.name }}</td>
                        <td>
                            <span class="type-badge">{{ source.type }}</span>
                        </td>
                        <td>{{ source.chance || "-" }}</td>
                        <td>{{ source.rotation || "-" }}</td>
                    </tr>
                </tbody>
            </table>
            <div v-else class="no-sources">No sources found for this item.</div>
        </div>

        <div v-else class="empty-state">
            <p>Search for an item to see its drop sources</p>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

interface GraphNode {
    id: string;
    name: string;
    type: string;
    label: string;
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

interface NodeNeighborsResponse {
    starting_node: GraphNode;
    neighbors: NodeNeighbor[];
    count: number;
}

interface NodeSearchResponse {
    nodes: GraphNode[];
}

interface Source {
    name: string;
    type: string;
    chance: string;
    rotation: string | null;
}

const searchName = ref("");
const searchResults = ref<GraphNode[]>([]);
const selectedNode = ref<GraphNode | null>(null);
const sources = ref<Source[]>([]);
const loading = ref(false);

let debounceTimer: ReturnType<typeof setTimeout> | null = null;

async function handleAutoSearch() {
    if (debounceTimer) {
        clearTimeout(debounceTimer);
    }

    if (!searchName.value.trim()) {
        searchResults.value = [];
        return;
    }

    debounceTimer = setTimeout(async () => {
        await performSearch();
    }, 300);
}

async function performSearch() {
    if (!searchName.value.trim()) return;

    loading.value = true;
    try {
        const params = new URLSearchParams();
        params.append("name", searchName.value.trim());

        const response = await fetch(`/api/loottables/search/nodes?${params}`, {
            credentials: "include",
        });

        if (!response.ok)
            throw new Error(`HTTP error! status: ${response.status}`);

        const data: NodeSearchResponse = await response.json();
        searchResults.value = data.nodes || [];
    } catch (error) {
        console.error("Error searching:", error);
        searchResults.value = [];
    } finally {
        loading.value = false;
    }
}

async function selectNode(node: GraphNode) {
    selectedNode.value = node;
    searchName.value = node.name;
    searchResults.value = [];

    await loadSources(node.name);
}

async function loadSources(name: string) {
    loading.value = true;
    sources.value = [];

    try {
        const params = new URLSearchParams();
        params.append("name", name);

        const response = await fetch(`/api/loottables/neighbors?${params}`, {
            credentials: "include",
        });

        if (!response.ok)
            throw new Error(`HTTP error! status: ${response.status}`);

        const data: NodeNeighborsResponse = await response.json();

        sources.value = data.neighbors.map((neighbor) => ({
            name: neighbor.name,
            type: neighbor.type,
            chance: neighbor.relationship_properties?.chance || "",
            rotation: neighbor.relationship_properties?.rotation || null,
        }));
    } catch (error) {
        console.error("Error loading sources:", error);
        sources.value = [];
    } finally {
        loading.value = false;
    }
}

function clearSearch() {
    searchName.value = "";
    searchResults.value = [];
    selectedNode.value = null;
    sources.value = [];
}
</script>

<style scoped>
.loottables-view {
    padding: var(--space-6);
    max-width: 1200px;
    margin: 0 auto;
    overflow-x: hidden;
}

.search-section {
    margin-bottom: var(--space-8);
}

.search-section h2 {
    color: var(--accent-subtle);
    margin-bottom: var(--space-4);
    font-size: var(--text-2xl);
}

.search-input-container {
    position: relative;
    margin-bottom: var(--space-4);
    width: 100%;
    box-sizing: border-box;
}

.search-input {
    width: 100%;
    padding: 0.8rem var(--space-4);
    font-size: var(--text-normal);
    background: var(--bg-elevated-2);
    border: 1px solid var(--border-input);
    border-radius: var(--radius-md);
    color: var(--text-light);
    box-sizing: border-box;
}

.search-input:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(var(--accent-rgb), 0.2);
}

.search-input::placeholder {
    color: var(--text-muted);
}

.loading-indicator {
    position: absolute;
    right: var(--space-4);
    top: 50%;
    transform: translateY(-50%);
    color: var(--accent);
    font-size: var(--text-md);
}

.search-results {
    background: var(--bg-elevated-2);
    border: 1px solid var(--border-secondary);
    border-radius: var(--radius-md);
    overflow: hidden;
}

.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-3) var(--space-4);
    background: var(--bg-elevated);
    border-bottom: 1px solid var(--border-secondary);
    color: var(--text-muted-2);
    font-size: var(--text-body);
}

.clear-btn {
    background: transparent;
    border: none;
    color: var(--accent);
    cursor: pointer;
    font-size: var(--text-md);
}

.clear-btn:hover {
    text-decoration: underline;
}

.results-list {
    max-height: 300px;
    overflow-y: auto;
    overflow-x: hidden;
}

.result-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border-secondary);
    cursor: pointer;
    transition: background var(--transition-normal);
}

.result-item:last-child {
    border-bottom: none;
}

.result-item:hover {
    background: var(--border-secondary);
}

.result-item.selected {
    background: var(--blue-selected);
    border-left: 3px solid var(--accent);
}

.result-name {
    color: var(--text-light);
    font-weight: 500;
}

.result-type {
    color: var(--text-muted);
    font-size: var(--text-md);
}

.sources-section {
    background: var(--bg-elevated-2);
    border: 1px solid var(--border-secondary);
    border-radius: var(--radius-md);
    padding: var(--space-6);
    overflow-x: hidden;
    max-height: 500px;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    width: 100%;
}

.sources-section h3 {
    color: var(--accent-subtle);
    margin-bottom: var(--space-4);
    font-size: var(--text-lg);
    flex-shrink: 0;
}

.sources-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--bg-elevated);
    border-radius: var(--radius-sm);
    overflow: hidden;
    overflow-y: auto;
    flex: 1;
    max-height: 400px;
}

.sources-table th {
    background: var(--bg-elevated-2);
    color: var(--accent-subtle);
    padding: var(--space-3) var(--space-4);
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid var(--border-secondary);
}

.sources-table td {
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border-secondary);
    color: var(--text-light);
}

.sources-table tr:hover {
    background: var(--bg-elevated-2);
}

.no-sources {
    text-align: center;
    color: var(--text-muted);
    padding: var(--space-8);
}
</style>
