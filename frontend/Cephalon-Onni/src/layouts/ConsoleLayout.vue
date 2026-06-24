<template>
    <div class="console scanlines">
        <aside class="sidebar">
            <div class="sidebar-accent"></div>

            <div class="brand-section">
                <h2 class="brand">Cephalon Onni</h2>
                <span class="brand-tagline">v2.0.1 // online</span>
            </div>

            <nav class="nav-section">
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

                <RouterLink v-if="isAdmin" to="/admin" class="nav">Administrator</RouterLink>
                <span v-if="isAdmin" class="divider" />

                <template v-if="user">
                    <RouterLink to="/profile" class="nav">Profile</RouterLink>
                    <button @click="logout" class="nav logout-btn">Log Off</button>
                </template>
                <template v-else>
                    <RouterLink to="/login" class="nav">Login</RouterLink>
                    <RouterLink to="/register" class="nav">Register</RouterLink>
                </template>
            </nav>

            <div class="sidebar-footer">
                <span class="status-dot"></span>
                <span class="status-text">System Nominal</span>
            </div>
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
    background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-surface) 100%);
    border-right: 1px solid var(--border-primary);
    display: flex;
    flex-direction: column;
    padding: 0;
    position: relative;
    overflow: hidden;
}

.sidebar-accent {
    position: absolute;
    top: 0;
    right: 0;
    width: 1px;
    height: 100%;
    background: linear-gradient(
        180deg,
        transparent 0%,
        var(--accent) 15%,
        var(--accent) 50%,
        var(--accent) 85%,
        transparent 100%
    );
    opacity: 0.4;
}

.brand-section {
    padding: 1.5rem 1.2rem 0.5rem;
    border-bottom: 1px solid var(--border-primary);
    margin-bottom: 0.5rem;
}

.brand {
    font-family: var(--font-display);
    font-size: var(--text-lg);
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 4px;
    margin: 0;
    text-transform: uppercase;
    text-shadow: 0 0 8px rgba(139, 92, 246, 0.3);
}

.brand-tagline {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--text-muted);
    letter-spacing: 1px;
    display: block;
    margin-top: 0.25rem;
}

.nav-section {
    flex: 1;
    padding: 0.5rem 1.2rem;
    overflow-y: auto;
}

.nav {
    display: block;
    margin-bottom: 0.4rem;
    text-decoration: none;
    color: var(--text-primary);
    padding: 0.5rem 0.6rem;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
    font-size: var(--text-md);
    letter-spacing: 0.04em;
    position: relative;
}

.nav:hover {
    background: var(--bg-surface-hover);
    color: var(--accent-subtle);
    padding-left: 0.9rem;
}

.nav:hover::before {
    content: "";
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 2px;
    height: 16px;
    background: var(--accent);
    box-shadow: 0 0 6px rgba(139, 92, 246, 0.5);
    border-radius: 1px;
}

:deep(.router-link-exact-active) {
    color: var(--accent) !important;
    background: rgba(139, 92, 246, 0.06);
    padding-left: 0.9rem;
    text-shadow: 0 0 8px rgba(139, 92, 246, 0.2);
}

:deep(.router-link-exact-active)::before {
    content: "";
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 2px;
    height: 16px;
    background: var(--accent);
    box-shadow: 0 0 8px rgba(139, 92, 246, 0.6);
    border-radius: 1px;
}

.logout-btn {
    background: none;
    border: none;
    color: var(--text-primary);
    padding: 0.5rem 0.6rem;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
    cursor: pointer;
    text-align: left;
    width: 100%;
    font-family: inherit;
    font-size: inherit;
    margin-bottom: 0.4rem;
}

.logout-btn:hover {
    background: var(--bg-surface-hover);
    color: var(--danger);
    padding-left: 0.9rem;
}

.divider {
    height: 1px;
    background: linear-gradient(
        90deg,
        transparent 0%,
        var(--border-primary) 20%,
        var(--border-primary) 80%,
        transparent 100%
    );
    margin: 0.8rem 0;
    display: block;
}

.sidebar-footer {
    padding: 0.8rem 1.2rem;
    border-top: 1px solid var(--border-primary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: var(--radius-round);
    background: var(--success);
    box-shadow: 0 0 6px rgba(0, 230, 118, 0.5);
    animation: breathe 2.5s ease-in-out infinite;
}

.status-text {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--text-muted);
    letter-spacing: 1px;
}

.main {
    padding: var(--space-8);
    overflow-y: auto;
}

@keyframes breathe {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}
</style>
