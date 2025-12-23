<template>
  <div class="graph-explorer">
    <!-- Search Controls -->
    <div class="search-section">
      <h3>Search & Query</h3>
      <div class="search-controls">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search nodes..." 
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <select v-model="searchType" class="search-type">
          <option value="all">All Types</option>
          <option value="Mission">Missions</option>
          <option value="Reward">Rewards</option>
          <option value="Relic">Relics</option>
          <option value="Key">Keys</option>
          <option value="Sortie">Sorties</option>
          <option value="Bounty">Bounties</option>
        </select>
        <button class="btn primary search-btn" @click="handleSearch" :disabled="loading">
          {{ loading ? 'Searching...' : 'Search' }}
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
        <button class="btn primary query-btn" @click="handleExecuteQuery" :disabled="loading">
          {{ loading ? 'Executing...' : 'Execute Query' }}
        </button>
        <button class="btn secondary clear-btn" @click="handleClearResults">
          Clear
        </button>
      </div>
    </div>

    <!-- Results Display -->
    <div class="results-section" v-if="searchResults.length > 0">
      <h3>Results ({{ searchResults.length }} items)</h3>
      <div class="results-grid">
        <div v-for="(item, index) in searchResults" :key="index" class="result-card">
          <div class="result-header">
            <span class="result-type">{{ item.type }}</span>
            <span class="result-label">{{ item.label }}</span>
            <div class="result-actions">
              <button class="btn-icon edit" @click="$emit('edit-node', item)" title="Edit">
                ✏️
              </button>
              <button class="btn-icon delete" @click="$emit('delete-node', item.id)" title="Delete">
                🗑️
              </button>
            </div>
          </div>
          <div class="result-content">
            <div v-for="(value, key) in item.properties" :key="key" class="property">
              <span class="property-key">{{ key }}:</span>
              <span class="property-value">{{ value }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useGraphApi } from '@/composables/useGraphApi';

const { searchResults, searchGraph, executeCypherQuery, clearResults } = useGraphApi();

const searchQuery = ref<string>("");
const searchType = ref<string>("all");
const cypherQuery = ref<string>("");
const loading = ref(false);

// Handle search
async function handleSearch() {
  loading.value = true;
  try {
    await searchGraph(searchQuery.value, searchType.value);
  } finally {
    loading.value = false;
  }
}

// Handle Cypher query execution
async function handleExecuteQuery() {
  loading.value = true;
  try {
    await executeCypherQuery(cypherQuery.value);
  } finally {
    loading.value = false;
  }
}

// Handle clear results
function handleClearResults() {
  clearResults();
  searchQuery.value = "";
  cypherQuery.value = "";
}

// Define emits
defineEmits<{
  'edit-node': [node: any]
  'delete-node': [nodeId: string]
}>();
</script>

<style scoped>
.graph-explorer {
  display: grid;
  gap: 2rem;
}

.search-section, .query-section {
  background: #0f172a;
  border: 1px solid #1b2a3a;
  border-radius: 4px;
  padding: 1.5rem;
}

.search-section h3, .query-section h3 {
  color: #7dd3fc;
  margin-bottom: 1rem;
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
  font-family: inherit;
}

.search-input:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.1);
}

.search-type {
  padding: 0.5rem 1rem;
  border: 1px solid #334155;
  background: #1e293b;
  color: #ffffff;
  border-radius: 4px;
}

.search-btn, .query-btn, .clear-btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.2s;
}

.search-btn, .query-btn {
  background: #10b981;
  color: #ffffff;
  border: none;
}

.search-btn:hover:not(:disabled), .query-btn:hover:not(:disabled) {
  background: #059669;
}

.clear-btn {
  background: #6b7280;
  color: #ffffff;
  border: 1px solid #6b7280;
}

.clear-btn:hover {
  background: #4b5563;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  font-family: 'Courier New', monospace;
}

.query-input:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.1);
}

.results-section {
  background: #08121f;
  border: 1px solid #1b2a3a;
  border-radius: 4px;
  padding: 1.5rem;
}

.results-section h3 {
  color: #7dd3fc;
  margin-bottom: 1rem;
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
  flex: 1;
  margin-left: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

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
</style>