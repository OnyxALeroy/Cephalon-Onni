<template>
  <div>
    <!-- Not logged in -->
    <div v-if="!user" class="login-prompt">
      <h2>Identification Required</h2>
      <p>Link your Tenno profile to access inventory data.</p>

      <button class="btn btn-primary" @click="goLogin">Login</button>

      <button class="btn btn-ghost" @click="goRegister">Create Account</button>
    </div>

    <!-- Logged in -->
    <div v-else>
      <h1>Inventory</h1>

      <!-- Toolbar -->
      <div class="toolbar">
        <input v-model="search" placeholder="Search..." />

        <select v-model="type">
          <option value="">All</option>
          <option value="warframe">Warframes</option>
          <option value="weapon">Weapons</option>
          <option value="mod">Mods</option>
          <option value="resource">Resources</option>
          <option value="relic">Relics</option>
        </select>
      </div>

      <!-- Inventory grid -->
      <div class="grid">
        <div
          v-for="item in filtered"
          :key="item.id"
          class="card"
          :class="item.rarity"
          @click="openItem(item)">
          <span class="name">{{ item.name }}</span>
          <span class="type">{{ item.type }}</span>
          <span class="count" v-if="item.count">x{{ item.count }}</span>
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
}

interface Item {
  id: string;
  name: string;
  type: string;
  rarity: string;
  count?: number;
}

/* --- STATES --- */

const user = ref<User | null>(null);
const inventory = ref<Item[]>([]);
const search = ref("");
const type = ref("");

/* --- AUTH + DATA FETCH --- */

onMounted(async () => {
  await fetchUser();
  if (user.value) fetchInventory();
});

async function fetchUser() {
  const res = await fetch("/api/auth/me", { credentials: "include" });

  if (res.ok) {
    user.value = await res.json();
  }
}

async function fetchInventory() {
  const res = await fetch("/api/inventory", { credentials: "include" });
  inventory.value = await res.json();
}

/* --- FILTERING --- */

const filtered = computed(() =>
  inventory.value.filter((i) => {
    if (type.value && i.type !== type.value) return false;
    return i.name.toLowerCase().includes(search.value.toLowerCase());
  })
);

/* --- ACTIONS --- */

function goLogin() {
  router.push("/login");
}

function goRegister() {
  router.push("/register");
}

function openItem(item: Item) {
  console.log("Clicked", item);
}
</script>

<style scoped>
.login-prompt {
  text-align: center;
  margin-top: 20vh;
}

h1 {
  color: var(--accent-subtle);
}

.toolbar {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

input,
select {
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  padding: var(--space-2);
  color: var(--text-white);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: var(--space-4);
}

.card {
  background: var(--bg-surface);
  padding: var(--space-4);
  border: 1px solid var(--border-primary);
  cursor: pointer;
  position: relative;
  transition: var(--transition-normal);
}

.card:hover {
  border-color: var(--accent);
}

.count {
  position: absolute;
  top: 6px;
  right: 8px;
  opacity: 0.7;
}

.card.common {
  border-left: 4px solid var(--text-muted);
}
.card.rare {
  border-left: 4px solid var(--blue-rare);
}
.card.legendary {
  border-left: 4px solid var(--yellow-legendary);
}

.name {
  font-weight: bold;
}
.type {
  opacity: 0.6;
  font-size: var(--text-base);
}
</style>
