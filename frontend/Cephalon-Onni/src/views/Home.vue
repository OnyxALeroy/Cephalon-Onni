<template>
  <div class="dashboard">
    <div class="welcome-section">
      <h1 class="glow-accent">Welcome, Tenno.</h1>
      <p class="subtitle">System status: <span class="glow-warm">Nominal</span></p>
    </div>

    <div class="panel-grid">
      <div class="panel card-cephalon">
        <div class="panel-icon">◈</div>
        <h3>Inventory Overview</h3>
        <p>Review your Tenno arsenal and resources</p>
      </div>
      <div class="panel card-cephalon">
        <div class="panel-icon">◉</div>
        <h3>Recent Alerts</h3>
        <p>Active operations and tactical alerts</p>
      </div>
      <div class="panel card-cephalon">
        <div class="panel-icon">◇</div>
        <h3>Latest Events</h3>
        <p>Ongoing events and limited-time content</p>
      </div>
      <div class="panel card-cephalon">
        <div class="panel-icon">◎</div>
        <h3>Void Activity</h3>
        <p>Fissure locations and Void storm tracking</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1100px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  margin-bottom: var(--space-10);
}

.welcome-section h1 {
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  letter-spacing: 6px;
  text-transform: uppercase;
  margin-bottom: var(--space-3);
}

.subtitle {
  font-family: var(--font-mono);
  font-size: var(--text-md);
  opacity: 0.7;
  letter-spacing: 2px;
}

.panel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-5);
}

.panel {
  height: 140px;
  cursor: default;
  transition: all var(--transition-normal);
}

.panel:hover {
  transform: translateY(-3px);
  box-shadow: var(--accent-glow);
}

.panel-icon {
  font-size: var(--text-xl);
  color: var(--accent-warm);
  margin-bottom: var(--space-2);
  opacity: 0.8;
}

.panel h3 {
  font-family: var(--font-display);
  font-size: var(--text-base);
  color: var(--text-secondary);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin: 0 0 var(--space-1);
}

.panel p {
  font-size: var(--text-sm);
  color: var(--text-muted-2);
  margin: 0;
}
</style>
