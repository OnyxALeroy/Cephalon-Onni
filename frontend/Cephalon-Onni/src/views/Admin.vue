<template>
  <div>
    <!-- Not logged in -->
    <div v-if="!user" class="login-prompt">
      <div class="terminal-tag mono">CEPHALON_ONNI://clearance_check</div>
      <h2>Authentication Required</h2>
      <p>Administrator access requires authentication.</p>
      <button class="btn btn-primary" @click="goLogin">Login</button>
    </div>

    <!-- Logged in but not admin -->
    <div v-else-if="!isAdmin" class="access-denied">
      <div class="terminal-tag mono">CEPHALON_ONNI://clearance_denied</div>
      <h2>Access Denied</h2>
      <p>You do not have administrator privileges to access this area.</p>
      <button class="btn btn-ghost" @click="goHome">Return to Home</button>
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
        <UserManagement v-if="activeTab === 'users'" />

        <!-- System Configuration Tab -->
        <SystemConfiguration v-if="activeTab === 'system'" />

        <!-- Content Management Tab -->
        <ContentManagement v-if="activeTab === 'content'" />

        <!-- Analytics Tab -->
        <AnalyticsReports v-if="activeTab === 'analytics'" />

        <!-- Security Tab -->
        <SecurityCenter v-if="activeTab === 'security'" />

        <!-- Graph Database Tab -->
        <GraphDatabase v-if="activeTab === 'graph'" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";

// Import admin components
import UserManagement from "@/components/admin/UserManagement.vue";
import SystemConfiguration from "@/components/admin/SystemConfiguration.vue";
import ContentManagement from "@/components/admin/ContentManagement.vue";
import AnalyticsReports from "@/components/admin/AnalyticsReports.vue";
import SecurityCenter from "@/components/admin/SecurityCenter.vue";
import GraphDatabase from "@/components/admin/GraphDatabase.vue";

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
  { id: "graph", name: "Graph Database" },
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
.login-prompt {
  text-align: center;
  margin-top: 20vh;
}

.access-denied {
  text-align: center;
  margin-top: 20vh;
  color: var(--danger);
}

.terminal-tag {
  font-size: var(--text-sm);
  letter-spacing: 1px;
  margin-bottom: var(--space-4);
  opacity: 0.7;
}

h1 {
  color: var(--accent-subtle);
  letter-spacing: 2px;
}

.subtitle {
  opacity: 0.7;
  margin-bottom: var(--space-8);
}

.tab-button {
  background: transparent;
  border: none;
  color: var(--text-primary);
  padding: var(--space-4) var(--space-6);
  cursor: pointer;
  transition: var(--transition-normal);
  border-bottom: 2px solid transparent;
}

.tab-button:hover {
  color: var(--accent-subtle);
  background: var(--bg-surface);
}

.tab-button.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

.tab-content {
  min-height: 400px;
}
</style>