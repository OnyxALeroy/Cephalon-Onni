<template>
  <div>
    <!-- Not logged in -->
    <div v-if="!user" class="login-prompt">
      <h2>Authentication Required</h2>
      <p>Administrator access requires authentication.</p>
      <button class="btn primary" @click="goLogin">Login</button>
    </div>

    <!-- Logged in but not admin -->
    <div v-else-if="!isAdmin" class="access-denied">
      <h2>Access Denied</h2>
      <p>You do not have administrator privileges to access this area.</p>
      <button class="btn secondary" @click="goHome">Return to Home</button>
    </div>

    <!-- Admin user -->
    <div v-else>
      <h1>Administrator Panel</h1>
      <p class="subtitle">System management and configuration</p>

      <!-- Tabs -->
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="['tab-button', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id">
          {{ tab.name }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- User Management Tab -->
        <div v-if="activeTab === 'users'" class="tab-panel">
          <h2>User Management</h2>
          <div class="admin-placeholder">
            <p>User management interface will be implemented here.</p>
            <ul>
              <li>View all users</li>
              <li>Edit user roles</li>
              <li>Manage user permissions</li>
              <li>User activity logs</li>
            </ul>
          </div>
        </div>

        <!-- System Configuration Tab -->
        <div v-if="activeTab === 'system'" class="tab-panel">
          <h2>System Configuration</h2>
          <div class="admin-placeholder">
            <p>System configuration interface will be implemented here.</p>
            <ul>
              <li>Database settings</li>
              <li>API configuration</li>
              <li>System monitoring</li>
              <li>Performance metrics</li>
            </ul>
          </div>
        </div>

        <!-- Content Management Tab -->
        <div v-if="activeTab === 'content'" class="tab-panel">
          <h2>Content Management</h2>
          <div class="admin-placeholder">
            <p>Content management interface will be implemented here.</p>
            <ul>
              <li>Manage inventory items</li>
              <li>Update game data</li>
              <li>Content moderation</li>
              <li>Media management</li>
            </ul>
          </div>
        </div>

        <!-- Analytics Tab -->
        <div v-if="activeTab === 'analytics'" class="tab-panel">
          <h2>Analytics & Reports</h2>
          <div class="admin-placeholder">
            <p>Analytics interface will be implemented here.</p>
            <ul>
              <li>User statistics</li>
              <li>System usage reports</li>
              <li>Performance analytics</li>
              <li>Custom reports</li>
            </ul>
          </div>
        </div>

        <!-- Security Tab -->
        <div v-if="activeTab === 'security'" class="tab-panel">
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
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

interface User {
  id: string;
  username: string;
  role: string;
}

interface Tab {
  id: string;
  name: string;
}

/* --- STATES --- */

const user = ref<User | null>(null);
const activeTab = ref<string>("users");

const tabs: Tab[] = [
  { id: "users", name: "Users" },
  { id: "system", name: "System" },
  { id: "content", name: "Content" },
  { id: "analytics", name: "Analytics" },
  { id: "security", name: "Security" },
];

/* --- AUTH + DATA FETCH --- */

onMounted(async () => {
  await fetchUser();
});

async function fetchUser() {
  const res = await fetch("/api/auth/me", { credentials: "include" });

  if (res.ok) {
    user.value = await res.json();
  }
}

/* --- COMPUTED --- */

const isAdmin = computed(() => {
  return user.value && user.value.role === "Administrator";
});

/* --- ACTIONS --- */

function goLogin() {
  router.push("/login");
}

function goHome() {
  router.push("/");
}
</script>

<style scoped>
/* LOGIN UI */
.login-prompt {
  text-align: center;
  margin-top: 20vh;
}

.access-denied {
  text-align: center;
  margin-top: 20vh;
  color: #ef4444;
}

.btn {
  margin: 1rem;
  padding: 0.7rem 1.5rem;
  border-radius: 4px;
  font-weight: bold;
}

.primary {
  background: #38bdf8;
  color: #021019;
}

.secondary {
  border: 1px solid #38bdf8;
  color: #38bdf8;
  background: transparent;
}

/* ADMIN PANEL */
h1 {
  color: #7dd3fc;
  letter-spacing: 2px;
}

.subtitle {
  opacity: 0.7;
  margin-bottom: 2rem;
}

/* TABS */
.tabs {
  display: flex;
  border-bottom: 1px solid #1b2a3a;
  margin-bottom: 2rem;
}

.tab-button {
  background: transparent;
  border: none;
  color: #c9e5ff;
  padding: 1rem 1.5rem;
  cursor: pointer;
  transition: 0.2s;
  border-bottom: 2px solid transparent;
}

.tab-button:hover {
  color: #7dd3fc;
  background: #08121f;
}

.tab-button.active {
  color: #38bdf8;
  border-bottom-color: #38bdf8;
}

/* TAB CONTENT */
.tab-content {
  min-height: 400px;
}

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