<template>
    <div class="console">
        <aside class="sidebar">
            <h2 class="brand">Cephalon Onni</h2>

            <RouterLink to="/" class="nav">Home</RouterLink>
            <RouterLink to="/inventory" class="nav">Inventory</RouterLink>
            <RouterLink to="/arsenal" class="nav">Arsenal</RouterLink>
            <RouterLink to="/loottables" class="nav">Loot Tables</RouterLink>
            <RouterLink to="/alerts" class="nav">Alerts</RouterLink>
            <RouterLink to="/relics" class="nav">Relics</RouterLink>

            <span class="divider" />

            <RouterLink to="/creative" class="nav">Creative Lab</RouterLink>
            <RouterLink to="/stars" class="nav">Star Chart</RouterLink>
            <RouterLink to="/events" class="nav">Events</RouterLink>
            <RouterLink to="/worldstate" class="nav">World State</RouterLink>

            <span class="divider" />

            <!-- Admin link only shown to administrators -->
            <RouterLink v-if="isAdmin" to="/admin" class="nav"
                >Administrator</RouterLink
            >
            <span v-if="isAdmin" class="divider" />

            <!-- Authenticated user navigation -->
            <template v-if="user">
                <RouterLink to="/profile" class="nav">Profile</RouterLink>
                <button @click="logout" class="nav logout-btn">Log Off</button>
            </template>
            
            <!-- Unauthenticated user navigation -->
            <template v-else>
                <RouterLink to="/login" class="nav">Login</RouterLink>
                <RouterLink to="/register" class="nav">Register</RouterLink>
            </template>
        </aside>

        <main class="main">
            <RouterView />
        </main>
    </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { RouterLink, RouterView } from "vue-router";
import { useAuth } from "@/composables/useAuth";

const { user, fetchUser, logout, isAdmin, isInitialized } = useAuth();

onMounted(async () => {
    await fetchUser();
});
</script>

<style scoped>
.console {
    display: grid;
    grid-template-columns: 220px 1fr;
    height: 100vh;
    background: var(--bg-page);
    color: var(--text-primary);
}

.sidebar {
    background: var(--bg-card);
    border-right: 1px solid var(--border-primary);
    display: flex;
    flex-direction: column;
    padding: 1.2rem;
}

.brand {
    color: var(--accent);
    letter-spacing: 2px;
    margin-bottom: 2rem;
    text-transform: uppercase;
}

.nav {
    margin-bottom: 0.6rem;
    text-decoration: none;
    color: var(--text-primary);
    padding: 0.4rem;
    border-radius: var(--radius-sm);
    transition: var(--transition-fast);
}

.nav:hover,
.router-link-active {
    background: var(--bg-surface);
    color: var(--accent-subtle);
}

.logout-btn {
    background: none;
    border: none;
    color: var(--text-primary);
    padding: 0.4rem;
    border-radius: var(--radius-sm);
    transition: var(--transition-fast);
    cursor: pointer;
    text-align: left;
    width: 100%;
    font-family: inherit;
    font-size: inherit;
    margin-bottom: 0.6rem;
}

.logout-btn:hover {
    background: var(--bg-surface);
    color: var(--accent-subtle);
}

.divider {
    height: 1px;
    background: var(--border-primary);
    margin: 1rem 0;
}

.main {
    padding: var(--space-8);
    overflow-y: auto;
}
</style>
