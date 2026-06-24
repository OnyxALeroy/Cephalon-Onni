<template>
  <div class="dashboard">
    <h1>Welcome, Tenno.</h1>
    <p class="subtitle">System status: Nominal</p>

    <div class="panel-grid">
      <div class="panel">Inventory Overview</div>
      <div class="panel">Recent Alerts</div>
      <div class="panel">Latest Events</div>
      <div class="panel">Void Activity</div>
    </div>
  </div>
</template>

<style scoped>
.dashboard h1 {
  color: var(--accent-subtle);
  letter-spacing: 2px;
}
.subtitle {
  opacity: 0.7;
}
.panel-grid {
  margin-top: var(--space-8);
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-4);
}
.panel {
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  padding: var(--space-4);
  height: 120px;
  transition: var(--transition-normal);
}
.panel:hover {
  border-color: var(--accent);
}
</style>
