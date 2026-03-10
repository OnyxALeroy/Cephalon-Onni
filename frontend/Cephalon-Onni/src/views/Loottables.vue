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
    padding: 1.5rem;
    max-width: 1200px;
    margin: 0 auto;
    overflow-x: hidden;
}

.search-section {
    margin-bottom: 2rem;
}

.search-section h2 {
    color: #7dd3fc;
    margin-bottom: 1rem;
    font-size: 1.5rem;
}

.search-input-container {
    position: relative;
    margin-bottom: 1rem;
    width: 100%;
    box-sizing: border-box;
}

.search-input {
    width: 100%;
    padding: 0.8rem 1rem;
    font-size: 1rem;
    background: #1e293b;
    border: 1px solid #475569;
    border-radius: 6px;
    color: #f1f5f9;
    box-sizing: border-box;
}

.search-input:focus {
    outline: none;
    border-color: #38bdf8;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

.search-input::placeholder {
    color: #64748b;
}

.loading-indicator {
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: #38bdf8;
    font-size: 0.85rem;
}

.search-results {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    overflow: hidden;
}

.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    background: #0f172a;
    border-bottom: 1px solid #334155;
    color: #94a3b8;
    font-size: 0.9rem;
}

.clear-btn {
    background: transparent;
    border: none;
    color: #38bdf8;
    cursor: pointer;
    font-size: 0.85rem;
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
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #334155;
    cursor: pointer;
    transition: background 0.2s;
}

.result-item:last-child {
    border-bottom: none;
}

.result-item:hover {
    background: #334155;
}

.result-item.selected {
    background: #1e3a8a;
    border-left: 3px solid #38bdf8;
}

.result-name {
    color: #f1f5f9;
    font-weight: 500;
}

.result-type {
    color: #64748b;
    font-size: 0.85rem;
}

.sources-section {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 1.5rem;
    overflow-x: hidden;
    max-height: 500px;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    width: 100%;
}

.sources-section h3 {
    color: #7dd3fc;
    margin-bottom: 1rem;
    font-size: 1.1rem;
    flex-shrink: 0;
}

.sources-table {
    width: 100%;
    border-collapse: collapse;
    background: #0f172a;
    border-radius: 4px;
    overflow: hidden;
    overflow-y: auto;
    flex: 1;
    max-height: 400px;
}

.sources-table th {
    background: #1e293b;
    color: #7dd3fc;
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid #334155;
}

.sources-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #334155;
    color: #f1f5f9;
}

.sources-table tr:hover {
    background: #1e293b;
}

.type-badge {
    background: #38bdf8;
    color: #021019;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}

.no-sources {
    text-align: center;
    color: #64748b;
    padding: 2rem;
}

.empty-state {
    text-align: center;
    padding: 3rem;
    color: #64748b;
    font-size: 1.1rem;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
}
</style>
