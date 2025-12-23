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
  color: #7dd3fc;
  margin-bottom: 1rem;
}

.admin-placeholder {
  background: #08121f;
  border: 1px solid #1b2a3a;
  padding: 2rem;
  border-radius: 4px;
}

.admin-placeholder p {
  margin-bottom: 1rem;
  opacity: 0.8;
}

.admin-placeholder ul {
  list-style: none;
  padding: 0;
}

.admin-placeholder li {
  padding: 0.5rem 0;
  opacity: 0.7;
}

.admin-placeholder li::before {
  content: "▸ ";
  color: #38bdf8;
  margin-right: 0.5rem;
}
</style>