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