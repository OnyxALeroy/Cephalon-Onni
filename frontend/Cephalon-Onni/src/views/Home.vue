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
  color: #7dd3fc;
  letter-spacing: 2px;
}
.subtitle {
  opacity: 0.7;
}
.panel-grid {
  margin-top: 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}
.panel {
  background: #08121f;
  border: 1px solid #1b2a3a;
  padding: 1rem;
  height: 120px;
  transition: 0.2s;
}
.panel:hover {
  border-color: #38bdf8;
}
</style>
