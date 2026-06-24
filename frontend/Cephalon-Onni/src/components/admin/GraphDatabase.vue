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

    <!-- Explore View (renamed from Visualize) -->
    <GraphVisualization v-if="currentView === 'visualize'" />

    <!-- Edit View -->
    <GraphEditor v-if="currentView === 'edit'" />


  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// Import graph components
import GraphVisualization from '@/components/admin/graph/GraphVisualization.vue';
import GraphEditor from '@/components/admin/graph/GraphEditor.vue';



// --- STATES ---
const currentView = ref<string>("visualize");
const viewModes = [
  { id: "visualize", name: "Explore" },
  { id: "edit", name: "Edit" }
];




</script>

<style scoped>
.tab-panel h2 {
  color: var(--accent-subtle);
  margin-bottom: var(--space-4);
}

.graph-explorer {
  display: grid;
  gap: var(--space-8);
}

.view-toggle {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-8);
  border-bottom: 1px solid var(--border-primary);
}

.view-btn {
  background: transparent;
  border: none;
  color: var(--text-primary);
  padding: var(--space-4) var(--space-6);
  cursor: pointer;
  transition: var(--transition-normal);
  border-bottom: 2px solid transparent;
}

.view-btn:hover {
  color: var(--accent-subtle);
  background: var(--bg-surface);
}

.view-btn.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
</style>