<template>
    <div>
        <!-- Not logged in -->
        <div v-if="!user" class="login-prompt">
            <h2>Authentication Required</h2>
            <p>Administrator access requires authentication.</p>
            <button class="btn primary" @click="goLogin">Login</button>
        </div>

        <!-- Logged in but not admin -->
        <div v-else-if="!isAdmin" class="access-denied">
            <h2>Access Denied</h2>
            <p>You do not have administrator privileges to access this area.</p>
            <button class="btn secondary" @click="goHome">
                Return to Home
            </button>
        </div>

        <!-- Admin user -->
        <div v-else>
            <h1>Administrator Panel</h1>
            <p class="subtitle">System management and configuration</p>

            <!-- Tabs -->
            <div class="tabs">
                <button
                    v-for="tab in tabs"
                    :key="tab.id"
                    :class="['tab-button', { active: activeTab === tab.id }]"
                    @click="activeTab = tab.id"
                >
                    {{ tab.name }}
                </button>
            </div>

            <!-- Tab Content -->
            <div class="tab-content">
                <!-- User Management Tab -->
                <div v-if="activeTab === 'users'" class="tab-panel">
                    <h2>User Management</h2>
                    <div class="admin-placeholder">
                        <p>
                            User management interface will be implemented here.
                        </p>
                        <ul>
                            <li>View all users</li>
                            <li>Edit user roles</li>
                            <li>Manage user permissions</li>
                            <li>User activity logs</li>
                        </ul>
                    </div>
                </div>

                <!-- System Configuration Tab -->
                <div v-if="activeTab === 'system'" class="tab-panel">
                    <h2>System Configuration</h2>
                    <div class="admin-placeholder">
                        <p>
                            System configuration interface will be implemented
                            here.
                        </p>
                        <ul>
                            <li>Database settings</li>
                            <li>API configuration</li>
                            <li>System monitoring</li>
                            <li>Performance metrics</li>
                        </ul>
                    </div>
                </div>

                <!-- Content Management Tab -->
                <div v-if="activeTab === 'content'" class="tab-panel">
                    <h2>Content Management</h2>
                    <div class="admin-placeholder">
                        <p>
                            Content management interface will be implemented
                            here.
                        </p>
                        <ul>
                            <li>Manage inventory items</li>
                            <li>Update game data</li>
                            <li>Content moderation</li>
                            <li>Media management</li>
                        </ul>
                    </div>
                </div>

                <!-- Analytics Tab -->
                <div v-if="activeTab === 'analytics'" class="tab-panel">
                    <h2>Analytics & Reports</h2>
                    <div class="admin-placeholder">
                        <p>Analytics interface will be implemented here.</p>
                        <ul>
                            <li>User statistics</li>
                            <li>System usage reports</li>
                            <li>Performance analytics</li>
                            <li>Custom reports</li>
                        </ul>
                    </div>
                </div>

                <!-- Security Tab -->
                <div v-if="activeTab === 'security'" class="tab-panel">
                    <h2>Security Center</h2>
                    <div class="admin-placeholder">
                        <p>
                            Security management interface will be implemented
                            here.
                        </p>
                        <ul>
                            <li>Security audit logs</li>
                            <li>Access control management</li>
                            <li>Threat monitoring</li>
                            <li>Security policies</li>
                        </ul>
                    </div>
                </div>

                <!-- Graph Database Tab -->
                <div v-if="activeTab === 'graph'" class="tab-panel">
                    <h2>Graph Database</h2>

                    <!-- View Mode Toggle -->
                    <div class="view-toggle">
                        <button
                            v-for="mode in viewModes"
                            :key="mode.id"
                            :class="[
                                'view-btn',
                                { active: currentView === mode.id },
                            ]"
                            @click="currentView = mode.id"
                        >
                            {{ mode.name }}
                        </button>
                    </div>

                    <!-- Graph Visualization View -->
                    <div
                        v-if="currentView === 'visualize'"
                        class="graph-visualization"
                    >
                        <div class="graph-controls">
                            <div class="control-section">
                                <h3>Graph Controls</h3>
                                <div class="control-buttons">
                                    <button
                                        class="btn primary"
                                        @click="loadVisualization"
                                    >
                                        Load Graph
                                    </button>
                                    <button
                                        class="btn secondary"
                                        @click="refreshGraph"
                                    >
                                        Refresh
                                    </button>
                                    <button
                                        class="btn secondary"
                                        @click="resetZoom"
                                    >
                                        Reset Zoom
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Graph Container -->
                        <div class="graph-container" ref="graphContainer">
                            <div id="graph-canvas"></div>
                        </div>
                    </div>

                    <!-- Explorer View -->
                    <div
                        v-if="currentView === 'explore'"
                        class="graph-explorer"
                    >
                        <!-- Search Controls -->
                        <div class="search-section">
                            <h3>Search & Query</h3>
                            <div class="search-controls">
                                <input
                                    v-model="searchQuery"
                                    type="text"
                                    placeholder="Search nodes..."
                                    class="search-input"
                                    @keyup.enter="searchGraph"
                                />
                                <select
                                    v-model="searchType"
                                    class="search-type"
                                >
                                    <option value="all">All Types</option>
                                    <option value="Mission">Missions</option>
                                    <option value="Reward">Rewards</option>
                                    <option value="Relic">Relics</option>
                                    <option value="Key">Keys</option>
                                    <option value="Sortie">Sorties</option>
                                    <option value="Bounty">Bounties</option>
                                </select>
                                <button
                                    class="btn primary search-btn"
                                    @click="searchGraph"
                                >
                                    Search
                                </button>
                            </div>
                        </div>

                        <!-- Query Input -->
                        <div class="query-section">
                            <h3>Cypher Query</h3>
                            <div class="query-controls">
                                <textarea
                                    v-model="cypherQuery"
                                    placeholder="Enter Cypher query..."
                                    class="query-input"
                                    rows="3"
                                ></textarea>
                                <button
                                    class="btn primary query-btn"
                                    @click="executeCypherQuery"
                                >
                                    Execute Query
                                </button>
                                <button
                                    class="btn secondary clear-btn"
                                    @click="clearResults"
                                >
                                    Clear
                                </button>
                            </div>
                        </div>

                        <!-- Results Display -->
                        <div
                            class="results-section"
                            v-if="searchResults.length > 0"
                        >
                            <h3>Results ({{ searchResults.length }} items)</h3>
                            <div class="results-grid">
                                <div
                                    v-for="(item, index) in searchResults"
                                    :key="index"
                                    class="result-card"
                                >
                                    <div class="result-header">
                                        <span class="result-type">{{
                                            item.type
                                        }}</span>
                                        <span class="result-label">{{
                                            item.label
                                        }}</span>
                                        <div class="result-actions">
                                            <button
                                                class="btn-icon edit"
                                                @click="editNode(item)"
                                                title="Edit"
                                            >
                                                ✏️
                                            </button>
                                            <button
                                                class="btn-icon delete"
                                                @click="deleteNode(item.id)"
                                                title="Delete"
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    </div>
                                    <div class="result-content">
                                        <div
                                            v-for="(
                                                value, key
                                            ) in item.properties"
                                            :key="key"
                                            class="property"
                                        >
                                            <span class="property-key"
                                                >{{ key }}:</span
                                            >
                                            <span class="property-value">{{
                                                value
                                            }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Statistics -->
                        <div class="stats-section">
                            <div class="stats-header">
                                <h3>Graph Statistics</h3>
                                <button
                                    class="btn secondary refresh-stats-btn"
                                    @click="updateGraphStats"
                                >
                                    Refresh Stats
                                </button>
                            </div>
                            <div class="stats-grid">
                                <div class="stat-item">
                                    <span class="stat-label">Total Nodes:</span>
                                    <span class="stat-value">{{
                                        graphStats.totalNodes
                                    }}</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Total Edges:</span>
                                    <span class="stat-value">{{
                                        graphStats.totalEdges
                                    }}</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Node Types:</span>
                                    <span class="stat-value">{{
                                        Object.keys(graphStats.nodeTypes).join(
                                            ", ",
                                        )
                                    }}</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label"
                                        >Last Updated:</span
                                    >
                                    <span class="stat-value">{{
                                        new Date(
                                            graphStats.lastUpdated,
                                        ).toLocaleString()
                                    }}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Edit View -->
                    <div v-if="currentView === 'edit'" class="graph-editor">
                        <!-- Create Node Section -->
                        <div class="create-section">
                            <h3>Create New Node</h3>
                            <form
                                @submit.prevent="createNewNode"
                                class="node-form"
                            >
                                <div class="form-row">
                                    <label>Node Type:</label>
                                    <select
                                        v-model="newNode.type"
                                        required
                                        class="form-input"
                                    >
                                        <option value="Mission">Mission</option>
                                        <option value="Reward">Reward</option>
                                        <option value="Relic">Relic</option>
                                        <option value="Key">Key</option>
                                        <option value="Sortie">Sortie</option>
                                        <option value="Bounty">Bounty</option>
                                        <option value="DynamicLocation">
                                            Dynamic Location
                                        </option>
                                        <option value="Source">Source</option>
                                        <option value="Drop">Drop</option>
                                    </select>
                                </div>
                                <div class="form-row">
                                    <label>Label/Name:</label>
                                    <input
                                        v-model="newNode.label"
                                        type="text"
                                        required
                                        class="form-input"
                                        placeholder="Node name"
                                    />
                                </div>
                                <div class="form-row">
                                    <label>Properties (JSON):</label>
                                    <textarea
                                        v-model="newNodeProperties"
                                        class="form-input"
                                        rows="5"
                                        placeholder='{"key": "value"}'
                                    ></textarea>
                                </div>
                                <div class="form-actions">
                                    <button type="submit" class="btn primary">
                                        Create Node
                                    </button>
                                    <button
                                        type="button"
                                        class="btn secondary"
                                        @click="resetCreateForm"
                                    >
                                        Reset
                                    </button>
                                </div>
                            </form>
                        </div>

                        <!-- Create Edge Section -->
                        <div class="create-section">
                            <h3>Create Edge</h3>
                            <form
                                @submit.prevent="createNewEdge"
                                class="edge-form"
                            >
                                <div class="form-row">
                                    <label>From Node ID:</label>
                                    <input
                                        v-model="newEdge.from_node"
                                        type="text"
                                        required
                                        class="form-input"
                                        placeholder="Source node ID"
                                    />
                                </div>
                                <div class="form-row">
                                    <label>To Node ID:</label>
                                    <input
                                        v-model="newEdge.to_node"
                                        type="text"
                                        required
                                        class="form-input"
                                        placeholder="Target node ID"
                                    />
                                </div>
                                <div class="form-row">
                                    <label>Relationship Type:</label>
                                    <select
                                        v-model="newEdge.relationship_type"
                                        required
                                        class="form-input"
                                    >
                                        <option value="DROPS">DROPS</option>
                                        <option value="CONTAINS">
                                            CONTAINS
                                        </option>
                                        <option value="HAS">HAS</option>
                                        <option value="RELATED_TO">
                                            RELATED_TO
                                        </option>
                                    </select>
                                </div>
                                <div class="form-row">
                                    <label>Edge Properties (JSON):</label>
                                    <textarea
                                        v-model="newEdgeProperties"
                                        class="form-input"
                                        rows="3"
                                        placeholder='{"chance": "25%", "rotation": "A"}'
                                    ></textarea>
                                </div>
                                <div class="form-actions">
                                    <button type="submit" class="btn primary">
                                        Create Edge
                                    </button>
                                    <button
                                        type="button"
                                        class="btn secondary"
                                        @click="resetEdgeForm"
                                    >
                                        Reset
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>

                    <!-- Edit Modal -->
                    <div
                        v-if="showEditModal"
                        class="modal-overlay"
                        @click="closeEditModal"
                    >
                        <div class="modal-content" @click.stop>
                            <h3>Edit Node</h3>
                            <form
                                @submit.prevent="updateNode"
                                class="edit-form"
                            >
                                <div class="form-row">
                                    <label>Node Type:</label>
                                    <input
                                        v-model="editingNode.type"
                                        type="text"
                                        required
                                        class="form-input"
                                    />
                                </div>
                                <div class="form-row">
                                    <label>Label/Name:</label>
                                    <input
                                        v-model="editingNode.label"
                                        type="text"
                                        required
                                        class="form-input"
                                    />
                                </div>
                                <div class="form-row">
                                    <label>Properties (JSON):</label>
                                    <textarea
                                        v-model="editingNodeProperties"
                                        class="form-input"
                                        rows="6"
                                    ></textarea>
                                </div>
                                <div class="modal-actions">
                                    <button type="submit" class="btn primary">
                                        Update
                                    </button>
                                    <button
                                        type="button"
                                        class="btn secondary"
                                        @click="closeEditModal"
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

interface User {
    id: string;
    username: string;
    role: string;
}

interface Tab {
    id: string;
    name: string;
}

/* --- STATES --- */

const user = ref<User | null>(null);
const activeTab = ref<string>("users");

const tabs: Tab[] = [
    { id: "users", name: "Users" },
    { id: "system", name: "System" },
    { id: "content", name: "Content" },
    { id: "analytics", name: "Analytics" },
    { id: "security", name: "Security" },
    { id: "graph", name: "Graph Database" },
];

/* --- AUTH + DATA FETCH --- */

onMounted(async () => {
    await fetchUser();
});

async function fetchUser() {
    const res = await fetch("/api/auth/me", { credentials: "include" });

    if (res.ok) {
        user.value = await res.json();
    }
}

/* --- COMPUTED --- */

const isAdmin = computed(() => {
    return user.value && user.value.role === "Administrator";
});

/* --- ACTIONS --- */

function goLogin() {
    router.push("/login");
}

function goHome() {
    router.push("/");
}

/* --- GRAPH DATABASE FUNCTIONS --- */

const currentView = ref<string>("explore");
const viewModes = [
    { id: "visualize", name: "Visualize" },
    { id: "explore", name: "Explore" },
    { id: "edit", name: "Edit" },
];

const searchQuery = ref<string>("");
const searchType = ref<string>("all");
const cypherQuery = ref<string>("");
const searchResults = ref<any[]>([]);
const graphStats = ref({
    totalNodes: 0,
    totalEdges: 0,
    nodeTypes: {},
    lastUpdated: new Date().toISOString(),
});

// Create/Edit forms
const newNode = ref({ type: "", label: "", properties: {} });
const newNodeProperties = ref<string>("{}");
const newEdge = ref({
    from_node: "",
    to_node: "",
    relationship_type: "DROPS",
    properties: {},
});
const newEdgeProperties = ref<string>("{}");

const showEditModal = ref<boolean>(false);
const editingNode = ref({ id: "", type: "", label: "", properties: {} });
const editingNodeProperties = ref<string>("{}");

// --- API Functions ---

async function searchGraph() {
    if (!searchQuery.value.trim()) return;

    try {
        const response = await fetch("/api/graph/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: searchQuery.value,
                type: searchType.value,
            }),
        });

        if (response.ok) {
            searchResults.value = await response.json();
            updateGraphStats();
        } else {
            console.error("Search failed");
        }
    } catch (error) {
        console.error("Search error:", error);
    }
}

async function executeCypherQuery() {
    if (!cypherQuery.value.trim()) return;

    try {
        const response = await fetch("/api/graph/cypher", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: cypherQuery.value }),
        });

        if (response.ok) {
            const result = await response.json();
            searchResults.value = result.results || [];
            updateGraphStats();
        } else {
            console.error("Query failed");
        }
    } catch (error) {
        console.error("Query error:", error);
    }
}

function clearResults() {
    searchResults.value = [];
    searchQuery.value = "";
    cypherQuery.value = "";
}

async function updateGraphStats() {
    try {
        const response = await fetch("/api/graph/stats");
        if (response.ok) {
            graphStats.value = await response.json();
        }
    } catch (error) {
        console.error("Stats error:", error);
    }
}

// --- Graph Visualization ---
async function loadVisualization() {
    try {
        const response = await fetch("/api/graph/explore");
        if (response.ok) {
            const data = await response.json();
            renderGraph(data);
        }
    } catch (error) {
        console.error("Visualization load error:", error);
    }
}

function renderGraph(data: any) {
    // Simple SVG graph rendering
    const container = document.getElementById("graph-canvas");
    if (!container) return;

    container.innerHTML = "";

    // Create nodes
    const nodeElements = data.nodes
        .map((node: any, index: number) => {
            const x = ((index * 100) % 800) + 50;
            const y = Math.floor(index / 8) * 100 + 50;

            return `
      <g class="node" transform="translate(${x}, ${y})">
        <circle r="20" fill="#38bdf8" stroke="#021019" stroke-width="2"/>
        <text text-anchor="middle" dy="5" fill="white" font-size="10">${node.label.substring(0, 8)}</text>
        <text y="30" text-anchor="middle" fill="#c9e5ff" font-size="8">${node.type}</text>
      </g>
    `;
        })
        .join("");

    // Create edges
    const edgeElements = data.edges
        .map((edge: any) => {
            return `<line class="edge" stroke="#64748b" stroke-width="1"/>`;
        })
        .join("");

    container.innerHTML = `
    <svg width="100%" height="600">
      ${edgeElements}
      ${nodeElements}
    </svg>
  `;
}

function refreshGraph() {
    loadVisualization();
    updateGraphStats();
}

function resetZoom() {
    // Implement zoom reset if using a graph library
}

// --- CRUD Operations ---

async function createNewNode() {
    try {
        let properties = {};
        if (newNodeProperties.value.trim()) {
            properties = JSON.parse(newNodeProperties.value);
        }

        const nodeData = {
            type: newNode.value.type,
            label: newNode.value.label,
            properties,
        };

        const response = await fetch("/api/graph/nodes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(nodeData),
        });

        if (response.ok) {
            resetCreateForm();
            updateGraphStats();
            alert("Node created successfully!");
        } else {
            console.error("Create node failed");
        }
    } catch (error) {
        console.error("Create node error:", error);
        alert("Failed to create node. Check JSON format.");
    }
}

async function createNewEdge() {
    try {
        let properties = {};
        if (newEdgeProperties.value.trim()) {
            properties = JSON.parse(newEdgeProperties.value);
        }

        const edgeData = {
            from_node: newEdge.value.from_node,
            to_node: newEdge.value.to_node,
            relationship_type: newEdge.value.relationship_type,
            properties,
        };

        const response = await fetch("/api/graph/edges", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(edgeData),
        });

        if (response.ok) {
            resetEdgeForm();
            updateGraphStats();
            alert("Edge created successfully!");
        } else {
            console.error("Create edge failed");
        }
    } catch (error) {
        console.error("Create edge error:", error);
        alert("Failed to create edge. Check JSON format.");
    }
}

function editNode(node: any) {
    editingNode.value = { ...node };
    editingNodeProperties.value = JSON.stringify(node.properties, null, 2);
    showEditModal.value = true;
}

async function updateNode() {
    try {
        let properties = {};
        if (editingNodeProperties.value.trim()) {
            properties = JSON.parse(editingNodeProperties.value);
        }

        const nodeData = {
            type: editingNode.value.type,
            label: editingNode.value.label,
            properties,
        };

        const response = await fetch(
            `/api/graph/nodes/${editingNode.value.id}`,
            {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(nodeData),
            },
        );

        if (response.ok) {
            closeEditModal();
            updateGraphStats();
            alert("Node updated successfully!");
        } else {
            console.error("Update node failed");
        }
    } catch (error) {
        console.error("Update node error:", error);
        alert("Failed to update node. Check JSON format.");
    }
}

async function deleteNode(nodeId: string) {
    if (
        !confirm(
            "Are you sure you want to delete this node and all its relationships?",
        )
    ) {
        return;
    }

    try {
        const response = await fetch(`/api/graph/nodes/${nodeId}`, {
            method: "DELETE",
        });

        if (response.ok) {
            updateGraphStats();
            alert("Node deleted successfully!");
        } else {
            console.error("Delete node failed");
        }
    } catch (error) {
        console.error("Delete node error:", error);
    }
}

// --- Form Management ---

function resetCreateForm() {
    newNode.value = { type: "", label: "", properties: {} };
    newNodeProperties.value = "{}";
}

function resetEdgeForm() {
    newEdge.value = {
        from_node: "",
        to_node: "",
        relationship_type: "DROPS",
        properties: {},
    };
    newEdgeProperties.value = "{}";
}

function closeEditModal() {
    showEditModal.value = false;
    editingNode.value = { id: "", type: "", label: "", properties: {} };
    editingNodeProperties.value = "{}";
}

// Initial load
onMounted(() => {
    updateGraphStats();
    if (currentView.value === "visualize") {
        loadVisualization();
    }
});
</script>

<style scoped>
/* LOGIN UI */
.login-prompt {
    text-align: center;
    margin-top: 20vh;
}

.access-denied {
    text-align: center;
    margin-top: 20vh;
    color: #ef4444;
}

.btn {
    margin: 1rem;
    padding: 0.7rem 1.5rem;
    border-radius: 4px;
    font-weight: bold;
}

.primary {
    background: #38bdf8;
    color: #021019;
}

.secondary {
    border: 1px solid #38bdf8;
    color: #38bdf8;
    background: transparent;
}

/* ADMIN PANEL */
h1 {
    color: #7dd3fc;
    letter-spacing: 2px;
}

.subtitle {
    opacity: 0.7;
    margin-bottom: 2rem;
}

/* TABS */
.tabs {
    display: flex;
    border-bottom: 1px solid #1b2a3a;
    margin-bottom: 2rem;
}

.tab-button {
    background: transparent;
    border: none;
    color: #c9e5ff;
    padding: 1rem 1.5rem;
    cursor: pointer;
    transition: 0.2s;
    border-bottom: 2px solid transparent;
}

.tab-button:hover {
    color: #7dd3fc;
    background: #08121f;
}

.tab-button.active {
    color: #38bdf8;
    border-bottom-color: #38bdf8;
}

/* TAB CONTENT */
.tab-content {
    min-height: 400px;
}

.tab-panel h2 {
    color: #7dd3fc;
    margin-bottom: 1rem;
}

.admin-placeholder {
    background: #08121f;
    border: 1px solid #1b2a3a;
    padding: 2rem;
    border-radius: 4px;
}

.admin-placeholder p {
    margin-bottom: 1rem;
    opacity: 0.8;
}

.admin-placeholder ul {
    list-style: none;
    padding: 0;
}

.admin-placeholder li {
    padding: 0.5rem 0;
    opacity: 0.7;
}

.admin-placeholder li::before {
    content: "▸ ";
    color: #38bdf8;
    margin-right: 0.5rem;
}

/* GRAPH DATABASE STYLES */
.graph-controls {
    display: grid;
    gap: 2rem;
    margin-bottom: 2rem;
}

.search-section,
.query-section {
    background: #0f172a;
    border: 1px solid #1b2a3a;
    border-radius: 4px;
    padding: 1.5rem;
}

.search-controls {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.search-input {
    flex: 1;
    padding: 0.5rem 1rem;
    border: 1px solid #334155;
    background: #1e293b;
    color: #ffffff;
    border-radius: 4px;
}

.search-type {
    padding: 0.5rem 1rem;
    border: 1px solid #334155;
    background: #1e293b;
    color: #ffffff;
    border-radius: 4px;
}

.search-btn,
.query-btn,
.clear-btn {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-weight: bold;
    cursor: pointer;
}

.search-btn,
.query-btn {
    background: #10b981;
    color: #ffffff;
    border: none;
}

.clear-btn {
    background: #6b7280;
    color: #ffffff;
    border: 1px solid #6b7280;
}

.query-controls {
    display: flex;
    gap: 1rem;
    align-items: stretch;
}

.query-input {
    flex: 1;
    min-height: 80px;
    padding: 0.5rem 1rem;
    border: 1px solid #334155;
    background: #1e293b;
    color: #ffffff;
    border-radius: 4px;
    resize: vertical;
    font-family: "Courier New", monospace;
}

.results-section {
    background: #08121f;
    border: 1px solid #1b2a3a;
    border-radius: 4px;
    padding: 1.5rem;
}

.results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    max-height: 400px;
    overflow-y: auto;
}

.result-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 1rem;
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #334155;
}

.result-type {
    background: #7dd3fc;
    color: #021019;
    padding: 0.25rem 0.5rem;
    border-radius: 3px;
    font-size: 0.875rem;
    font-weight: bold;
}

.result-label {
    color: #c9e5ff;
    font-weight: bold;
}

.result-content {
    max-height: 200px;
    overflow-y: auto;
}

.property {
    display: flex;
    padding: 0.25rem 0;
    font-size: 0.875rem;
}

.property-key {
    color: #38bdf8;
    min-width: 120px;
    font-weight: bold;
}

.property-value {
    color: #ffffff;
    word-break: break-word;
}

.stats-section {
    background: #08121f;
    border: 1px solid #1b2a3a;
    border-radius: 4px;
    padding: 1.5rem;
}

.stats-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.stats-header h3 {
    margin: 0;
    color: #7dd3fc;
}

.refresh-stats-btn {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    background: transparent;
    border: 1px solid #38bdf8;
    color: #38bdf8;
    border-radius: 4px;
    cursor: pointer;
    transition: 0.2s;
}

.refresh-stats-btn:hover {
    background: #38bdf8;
    color: #021019;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.stat-item {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 1rem;
    background: #1e293b;
    border-radius: 4px;
    border: 1px solid #334155;
}

.stat-label {
    color: #c9e5ff;
    font-weight: bold;
}

.stat-value {
    color: #ffffff;
}

/* VIEW TOGGLE */
.view-toggle {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid #1b2a3a;
}

.view-btn {
    background: transparent;
    border: none;
    color: #c9e5ff;
    padding: 1rem 1.5rem;
    cursor: pointer;
    transition: 0.2s;
    border-bottom: 2px solid transparent;
}

.view-btn:hover {
    color: #7dd3fc;
    background: #08121f;
}

.view-btn.active {
    color: #38bdf8;
    border-bottom-color: #38bdf8;
}

/* GRAPH VISUALIZATION */
.graph-visualization {
    background: #0f172a;
    border: 1px solid #1b2a3a;
    border-radius: 4px;
    padding: 1.5rem;
}

.control-section {
    margin-bottom: 1rem;
}

.control-buttons {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}

.graph-container {
    background: #08121f;
    border: 1px solid #1b2a3a;
    border-radius: 4px;
    min-height: 600px;
    position: relative;
    overflow: hidden;
}

#graph-canvas {
    width: 100%;
    height: 100%;
    min-height: 600px;
}

/* GRAPH EDITOR */
.graph-editor {
    display: grid;
    gap: 2rem;
}

.create-section {
    background: #0f172a;
    border: 1px solid #1b2a3a;
    border-radius: 4px;
    padding: 1.5rem;
}

.create-section h3 {
    color: #7dd3fc;
    margin-bottom: 1rem;
}

.node-form,
.edge-form {
    display: grid;
    gap: 1rem;
}

.form-row {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-row label {
    color: #c9e5ff;
    font-weight: bold;
    font-size: 0.875rem;
}

.form-input {
    padding: 0.5rem 1rem;
    border: 1px solid #334155;
    background: #1e293b;
    color: #ffffff;
    border-radius: 4px;
    font-family: inherit;
}

.form-input:focus {
    outline: none;
    border-color: #38bdf8;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.1);
}

.form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

/* MODAL */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: #0f172a;
    border: 1px solid #1b2a3a;
    border-radius: 8px;
    padding: 2rem;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
}

.modal-content h3 {
    color: #7dd3fc;
    margin-bottom: 1.5rem;
}

.edit-form {
    display: grid;
    gap: 1rem;
}

.modal-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
}

/* RESULT ACTIONS */
.result-actions {
    display: flex;
    gap: 0.5rem;
}

.btn-icon {
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 2px;
    font-size: 1rem;
    transition: 0.2s;
}

.btn-icon.edit:hover {
    background: #fbbf24;
}

.btn-icon.delete:hover {
    background: #ef4444;
}
</style>
