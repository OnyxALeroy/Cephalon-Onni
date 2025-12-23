<template>
  <div v-if="visible" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <h3>Edit Node</h3>
      <form @submit.prevent="handleUpdateNode" class="edit-form">
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
          <button type="submit" class="btn primary" :disabled="loading">
            {{ loading ? 'Updating...' : 'Update' }}
          </button>
          <button type="button" class="btn secondary" @click="handleClose">
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

const { updateNode, updateGraphStats } = useGraphApi();

// Props
const props = defineProps<{
  visible: boolean;
  node: any;
}>();

// Emits
const emit = defineEmits<{
  'update:visible': [visible: boolean]
}>();

// Local state
const loading = ref(false);
const editingNode = ref({ id: "", type: "", label: "", properties: {} });
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
  resize: vertical;
}

.form-input:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.1);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.7rem 1.5rem;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.2s;
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

.secondary:hover {
  background: #38bdf8;
  color: #021019;
}
</style>