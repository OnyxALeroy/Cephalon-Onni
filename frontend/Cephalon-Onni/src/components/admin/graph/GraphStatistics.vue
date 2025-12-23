<template>
  <div class="stats-section">
    <div class="stats-header">
      <h3>Graph Statistics</h3>
      <button 
        class="btn secondary refresh-stats-btn" 
        @click="handleRefreshStats" 
        :disabled="loading"
      >
        {{ loading ? 'Refreshing...' : '🔄 Refresh Stats' }}
      </button>
    </div>
    <div class="stats-grid">
      <div class="stat-item">
        <span class="stat-label">Total Nodes:</span>
        <span class="stat-value">{{ graphStats.totalNodes }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Total Edges:</span>
        <span class="stat-value">{{ graphStats.totalEdges }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Node Types:</span>
        <span class="stat-value">{{ Object.keys(graphStats.nodeTypes).join(', ') || 'None' }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Last Updated:</span>
        <span class="stat-value">{{ formatDate(graphStats.lastUpdated) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useGraphApi } from '@/composables/useGraphApi';

const { graphStats, updateGraphStats } = useGraphApi();
const loading = ref(false);

// Load stats on component mount
onMounted(() => {
  handleRefreshStats();
});

// Handle refresh
async function handleRefreshStats() {
  loading.value = true;
  try {
    await updateGraphStats();
  } finally {
    loading.value = false;
  }
}

// Format date
function formatDate(dateString: string) {
  try {
    return new Date(dateString).toLocaleString();
  } catch {
    return 'Invalid date';
  }
}
</script>

<style scoped>
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

.refresh-stats-btn:hover:not(:disabled) {
  background: #38bdf8;
  color: #021019;
}

.refresh-stats-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  word-break: break-word;
  max-width: 60%;
  text-align: right;
}
</style>