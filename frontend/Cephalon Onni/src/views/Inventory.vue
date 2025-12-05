<template>
  <div>
    <h1>Inventory</h1>

    <input class="search" placeholder="Search item..." v-model="search" />

    <div class="grid">
      <div
        v-for="item in filtered"
        :key="item.name"
        class="card"
        :class="item.rarity">
        <span class="name">{{ item.name }}</span>
        <span class="type">{{ item.type }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

interface Item {
  name: string;
  type: string;
  rarity: "common" | "rare" | "legendary";
}

const search = ref("");

const inventory = ref<Item[]>([
  { name: "Braton", type: "Rifle", rarity: "common" },
  { name: "Excalibur", type: "Warframe", rarity: "rare" },
  { name: "Paris Prime", type: "Bow", rarity: "legendary" },
]);

const filtered = computed(() =>
  inventory.value.filter((i) =>
    i.name.toLowerCase().includes(search.value.toLowerCase())
  )
);
</script>

<style scoped>
h1 {
  color: #7dd3fc;
}
.search {
  margin: 1rem 0;
  width: 100%;
  padding: 0.5rem;
  background: #050b16;
  border: 1px solid #1b2a3a;
  color: white;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}

.card {
  background: #08121f;
  padding: 1rem;
  border: 1px solid #1b2a3a;
  cursor: pointer;
}

.card:hover {
  border-color: #38bdf8;
}

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
  display: block;
  font-weight: bold;
}
.type {
  opacity: 0.6;
  font-size: 0.85rem;
}
</style>
