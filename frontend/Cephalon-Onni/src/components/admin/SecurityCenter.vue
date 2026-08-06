<template>
  <div class="tab-panel">
    <h2>Security Center</h2>
    <div class="admin-placeholder">
      <p>Security management interface will be implemented here.</p>
      <ul>
        <li>Security audit logs</li>
        <li>Access control management</li>
        <li>Threat monitoring</li>
        <li>Security policies</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
// Security center logic will be implemented here
</script>

<style scoped>
.tab-panel h2 {
  color: var(--accent-subtle);
  margin-bottom: var(--space-4);
}

.admin-placeholder {
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  padding: var(--space-8);
  border-radius: var(--radius-sm);
}

.admin-placeholder p {
  margin-bottom: var(--space-4);
  opacity: 0.8;
}

.admin-placeholder ul {
  list-style: none;
  padding: 0;
}

.admin-placeholder li {
  padding: var(--space-2) 0;
  opacity: 0.7;
}

.admin-placeholder li::before {
  content: "▸ ";
  color: var(--accent);
  margin-right: var(--space-2);
}
</style>