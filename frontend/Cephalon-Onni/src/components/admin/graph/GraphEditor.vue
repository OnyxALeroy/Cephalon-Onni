<template>
  <div class="graph-editor">
    <!-- Create Node Section -->
    <div class="create-section">
      <h3>Create New Node</h3>
      <form @submit.prevent="handleCreateNode" class="node-form">
        <div class="form-row">
          <label>Node Type:</label>
          <select v-model="newNode.type" required class="form-input">
            <option value="Mission">Mission</option>
            <option value="Reward">Reward</option>
            <option value="Relic">Relic</option>
            <option value="Key">Key</option>
            <option value="Sortie">Sortie</option>
            <option value="Bounty">Bounty</option>
            <option value="DynamicLocation">Dynamic Location</option>
            <option value="Source">Source</option>
            <option value="Drop">Drop</option>
          </select>
        </div>
        <div class="form-row">
          <label>Node Name:</label>
          <input 
            v-model="newNode.name" 
            type="text" 
            required 
            class="form-input" 
            placeholder="Node name" 
          />
        </div>
        <div class="form-row">
          <label>Label/Type:</label>
          <input 
            v-model="newNode.label" 
            type="text" 
            required 
            class="form-input" 
            placeholder="Node label/type" 
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
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Creating...' : 'Create Node' }}
          </button>
          <button type="button" class="btn btn-ghost" @click="resetCreateForm">
            Reset
          </button>
        </div>
      </form>
    </div>

    <!-- Create Edge Section -->
    <div class="create-section">
      <h3>Create Edge</h3>
      <form @submit.prevent="handleCreateEdge" class="edge-form">
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
          <select v-model="newEdge.relationship_type" required class="form-input">
            <option value="DROPS">DROPS</option>
            <option value="CONTAINS">CONTAINS</option>
            <option value="HAS">HAS</option>
            <option value="RELATED_TO">RELATED_TO</option>
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
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Creating...' : 'Create Edge' }}
          </button>
          <button type="button" class="btn btn-ghost" @click="resetEdgeForm">
            Reset
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useGraphApi } from '@/composables/useGraphApi';
import { usePersistentData, GraphNode, GraphEdge } from '@/composables/usePersistentData';

const { createNewNode, createNewEdge, updateGraphStats } = useGraphApi();
const { getEditorData, setEditorData } = usePersistentData();

const loading = ref(false);

// Initialize from persistent data
const persistentData = getEditorData();

// Node form data
const newNode = ref({ ...persistentData.newNode });
const newNodeProperties = ref<string>(persistentData.newNodeProperties);

// Edge form data
const newEdge = ref({ 
  ...persistentData.newEdge
});
const newEdgeProperties = ref<string>(persistentData.newEdgeProperties);

// Watch for changes and save to persistent storage
watch([newNode, newNodeProperties, newEdge, newEdgeProperties], () => {
  setEditorData({
    newNode: { ...newNode.value },
    newNodeProperties: newNodeProperties.value,
    newEdge: { ...newEdge.value },
    newEdgeProperties: newEdgeProperties.value
  });
}, { deep: true });

// Handle node creation
async function handleCreateNode() {
  loading.value = true;
  try {
    let properties = {};
    if (newNodeProperties.value.trim()) {
      properties = JSON.parse(newNodeProperties.value);
    }
    
    const nodeData = {
      type: newNode.value.type,
      label: newNode.value.label,
      properties
    };
    
    const result = await createNewNode(nodeData);
    if (result.success) {
      resetCreateForm();
      await updateGraphStats();
      alert("Node created successfully!");
    }
  } catch (error) {
    console.error("Create node error:", error);
    alert("Failed to create node. Check JSON format.");
  } finally {
    loading.value = false;
  }
}

// Handle edge creation
async function handleCreateEdge() {
  loading.value = true;
  try {
    let properties = {};
    if (newEdgeProperties.value.trim()) {
      properties = JSON.parse(newEdgeProperties.value);
    }
    
    const edgeData = {
      from_node: newEdge.value.from_node,
      to_node: newEdge.value.to_node,
      relationship_type: newEdge.value.relationship_type,
      properties
    };
    
    const result = await createNewEdge(edgeData);
    if (result.success) {
      resetEdgeForm();
      await updateGraphStats();
      alert("Edge created successfully!");
    }
  } catch (error) {
    console.error("Create edge error:", error);
    alert("Failed to create edge. Check JSON format.");
  } finally {
    loading.value = false;
  }
}

// Reset node form
function resetCreateForm() {
  newNode.value = { name: "", type: "", label: "", properties: {} };
  newNodeProperties.value = "{}";
  // Persistent data will be updated automatically by the watcher
}

// Reset edge form
function resetEdgeForm() {
  newEdge.value = { 
    from_node: "", 
    to_node: "", 
    relationship_type: "DROPS", 
    properties: {} 
  };
  newEdgeProperties.value = "{}";
  // Persistent data will be updated automatically by the watcher
}
</script>

<style scoped>
.graph-editor {
  display: grid;
  gap: var(--space-8);
}

.create-section {
  background: var(--bg-elevated);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  padding: var(--space-6);
}

.create-section h3 {
  color: var(--accent-subtle);
  margin-bottom: var(--space-4);
}

.node-form, .edge-form {
  display: grid;
  gap: var(--space-4);
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-row label {
  color: var(--text-primary);
  font-weight: bold;
  font-size: var(--text-md);
}

.form-input {
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--border-secondary);
  background: var(--bg-elevated-2);
  color: var(--text-white);
  border-radius: var(--radius-sm);
  font-family: inherit;
  resize: vertical;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(var(--accent-rgb), 0.1);
}

.form-actions {
  display: flex;
  gap: var(--space-4);
  margin-top: var(--space-4);
}
</style>