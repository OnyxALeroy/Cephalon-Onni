<template>
  <div class="console">
    <aside class="sidebar">
      <h2 class="brand">Cephalon Onni</h2>

      <RouterLink to="/" class="nav">Home</RouterLink>
      <RouterLink to="/inventory" class="nav">Inventory</RouterLink>
      <RouterLink to="/arsenal" class="nav">Arsenal</RouterLink>
      <RouterLink to="/profile" class="nav">Profile</RouterLink>
      <RouterLink to="/alerts" class="nav">Alerts</RouterLink>
      <RouterLink to="/relics" class="nav">Relics</RouterLink>

      <span class="divider" />

      <!-- Admin link only shown to administrators -->
      <RouterLink v-if="isAdmin" to="/admin" class="nav">Administrator</RouterLink>
      <span v-if="isAdmin" class="divider" />

      <RouterLink to="/creative" class="nav">Creative Lab</RouterLink>
      <RouterLink to="/stars" class="nav">Star Chart</RouterLink>
      <RouterLink to="/events" class="nav">Events</RouterLink>
    </aside>

    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { RouterLink, RouterView } from "vue-router";

interface User {
  id: string;
  username: string;
  role: string;
}

/* --- STATES --- */

const user = ref<User | null>(null);

/* --- AUTH + DATA FETCH --- */

onMounted(async () => {
  await fetchUser();
});

async function fetchUser() {
  try {
    const res = await fetch("/api/auth/me", { credentials: "include" });
    
    if (res.ok) {
      user.value = await res.json();
    }
  } catch (error) {
    // User not authenticated, that's fine for layout
    console.log("User not authenticated");
  }
}

/* --- COMPUTED --- */

const isAdmin = computed(() => {
  return user.value && user.value.role === "Administrator";
});
</script>

<style scoped>
.console {
  display: grid;
  grid-template-columns: 220px 1fr;
  height: 100vh;
  background: #02050a;
  color: #c9e5ff;
}

.sidebar {
  background: #050b16;
  border-right: 1px solid #1b2a3a;
  display: flex;
  flex-direction: column;
  padding: 1.2rem;
}

.brand {
  color: #38bdf8;
  letter-spacing: 2px;
  margin-bottom: 2rem;
  text-transform: uppercase;
}

.nav {
  margin-bottom: 0.6rem;
  text-decoration: none;
  color: #c9e5ff;
  padding: 0.4rem;
  border-radius: 4px;
  transition: 0.15s;
}

.nav:hover,
.router-link-active {
  background: #08121f;
  color: #7dd3fc;
}

.divider {
  height: 1px;
  background: #1b2a3a;
  margin: 1rem 0;
}
.main {
  padding: 2rem;
  overflow-y: auto;
}
</style>
