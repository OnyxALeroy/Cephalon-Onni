<template>
  <div class="tab-panel">
    <h2>Graph Database</h2>
    
    <!-- View Mode Toggle -->
    <div class="view-toggle">
      <button 
        v-for="mode in viewModes" 
        :key="mode.id"
        :class="['view-btn', { active: currentView === mode.id }]"
        @click="currentView = mode.id">
        {{ mode.name }}
      </button>
    </div>

    <!-- Graph Visualization View -->
    <GraphVisualization v-if="currentView === 'visualize'" />

    <!-- Explorer View -->
    <div v-if="currentView === 'explore'" class="graph-explorer">
      <GraphExplorer 
        @edit-node="handleEditNode" 
        @delete-node="handleDeleteNode" 
      />
      <GraphStatistics />
    </div>

    <!-- Edit View -->
    <GraphEditor v-if="currentView === 'edit'" />

    <!-- Edit Node Modal -->
    <EditNodeModal 
      v-model:visible="showEditModal" 
      :node="editingNode" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

// Import graph components
import GraphVisualization from '@/components/admin/graph/GraphVisualization.vue';
import GraphExplorer from '@/components/admin/graph/GraphExplorer.vue';
import GraphEditor from '@/components/admin/graph/GraphEditor.vue';
import GraphStatistics from '@/components/admin/graph/GraphStatistics.vue';
import EditNodeModal from '@/components/admin/graph/EditNodeModal.vue';

// Import composable
import { useGraphApi } from '@/composables/useGraphApi';

// --- STATES ---
const currentView = ref<string>("explore");
const viewModes = [
  { id: "visualize", name: "Visualize" },
  { id: "explore", name: "Explore" },
  { id: "edit", name: "Edit" }
];

const showEditModal = ref<boolean>(false);
const editingNode = ref<any>(null);

// Get API functions from composable
const { deleteNode, updateGraphStats } = useGraphApi();

// --- HANDLERS ---

// Handle edit node
function handleEditNode(node: any) {
  editingNode.value = node;
  showEditModal.value = true;
}

// Handle delete node
async function handleDeleteNode(nodeId: string) {
  if (!confirm("Are you sure you want to delete this node and all its relationships?")) {
    return;
  }
  
  try {
    const result = await deleteNode(nodeId);
    if (result.success) {
      await updateGraphStats();
      alert("Node deleted successfully!");
    }
  } catch (error) {
    console.error("Delete node error:", error);
  }
}

// Initial load
onMounted(() => {
  // Stats are now loaded by GraphStatistics component
});
</script>

<style scoped>
.tab-panel h2 {
  color: #7dd3fc;
  margin-bottom: 1rem;
}

.graph-explorer {
  display: grid;
  gap: 2rem;
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
</style>