<template>
  <div>
    <!-- Not logged in -->
    <div v-if="!user" class="login-prompt">
      <h2>Identification Required</h2>
      <p>Link your Tenno profile to access inventory data.</p>

      <button class="btn primary" @click="goLogin">Login</button>

      <button class="btn secondary" @click="goRegister">Create Account</button>
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
/* LOGIN UI */
.login-prompt {
  text-align: center;
  margin-top: 20vh;
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

/* INVENTORY */
h1 {
  color: #7dd3fc;
}

.toolbar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

input,
select {
  background: #050b16;
  border: 1px solid #1b2a3a;
  padding: 0.5rem;
  color: white;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 1rem;
}

.card {
  background: #08121f;
  padding: 1rem;
  border: 1px solid #1b2a3a;
  cursor: pointer;
  position: relative;
  transition: 0.2s;
}

.card:hover {
  border-color: #38bdf8;
}

.count {
  position: absolute;
  top: 6px;
  right: 8px;
  opacity: 0.7;
}

/* rarity highlight */
.card.common {
  border-left: 4px solid #64748b;
}
.card.rare {
  border-left: 4px solid #3b82f6;
}
.card.legendary {
  border-left: 4px solid #facc15;
}

.name {
  font-weight: bold;
}
.type {
  opacity: 0.6;
  font-size: 0.8rem;
}
</style>
