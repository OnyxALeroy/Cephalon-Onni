<template>
  <div v-if="visible" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <h3>Edit Node</h3>
      <form @submit.prevent="handleUpdateNode" class="edit-form">
        <div class="form-row">
          <label>Node Name:</label>
          <input 
            v-model="editingNode.name" 
            type="text" 
            required 
            class="form-input" 
          />
        </div>
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
          <label>Label:</label>
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
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Updating...' : 'Update' }}
          </button>
          <button type="button" class="btn btn-ghost" @click="handleClose">
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useGraphApi } from '@/composables/useGraphApi';
import { GraphNode } from '@/composables/usePersistentData';

const { updateNode, updateGraphStats } = useGraphApi();

// Props
const props = defineProps<{
  visible: boolean;
  node: GraphNode;
}>();

// Emits
const emit = defineEmits<{
  'update:visible': [visible: boolean]
}>();

// Local state
const loading = ref(false);
const editingNode = ref<GraphNode>({ id: "", name: "", type: "", label: "", properties: {} });
const editingNodeProperties = ref<string>("{}");

// Watch for node prop changes
watch(() => props.node, (newNode) => {
  if (newNode) {
    editingNode.value = { ...newNode };
    editingNodeProperties.value = JSON.stringify(newNode.properties || {}, null, 2);
  }
}, { immediate: true });

// Handle update
async function handleUpdateNode() {
  loading.value = true;
  try {
    let properties = {};
    if (editingNodeProperties.value.trim()) {
      properties = JSON.parse(editingNodeProperties.value);
    }
    
    const nodeData = {
      name: editingNode.value.name,
      type: editingNode.value.type,
      label: editingNode.value.label,
      properties
    };
    
    const result = await updateNode(editingNode.value.id, nodeData);
    if (result.success) {
      await updateGraphStats();
      handleClose();
      alert("Node updated successfully!");
    }
  } catch (error) {
    console.error("Update node error:", error);
    alert("Failed to update node. Check JSON format.");
  } finally {
    loading.value = false;
  }
}

// Handle close
function handleClose() {
  emit('update:visible', false);
}
</script>

<style scoped>
.modal-content {
  background: var(--bg-elevated);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h3 {
  color: var(--accent-subtle);
  margin-bottom: var(--space-6);
}

.edit-form {
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

.modal-actions {
  display: flex;
  gap: var(--space-4);
  margin-top: var(--space-6);
}
</style>