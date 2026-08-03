<template>
    <div class="build-list">
        <div class="list-header">
            <h3>Your Builds</h3>

            <div class="header-actions">
                <button
                    v-if="hasLocalBuilds && isAuthenticated"
                    @click="handleSyncLocalBuilds"
                    class="btn-sync"
                    :disabled="loading"
                >
                    <span v-if="loading">Syncing...</span>
                    <span v-else>Sync Local Builds</span>
                </button>

                <button @click="$emit('create-new')" class="btn btn-primary">
                    New Build
                </button>
            </div>
        </div>

        <div v-if="hasLocalBuilds && !isAuthenticated" class="sync-prompt">
            <div class="sync-info">
                <p>
                    <strong>{{ composableLocalBuilds.length }}</strong> local
                    build(s) found.
                    <RouterLink to="/login" class="login-link"
                        >Login</RouterLink
                    >
                    or
                    <RouterLink to="/register" class="register-link"
                        >Register</RouterLink
                    >
                    to save them to your account.
                </p>
            </div>
        </div>

        <div v-if="loading && allBuilds.length === 0" class="loading-state">
            <p>Loading builds...</p>
        </div>

        <div v-else-if="allBuilds.length === 0" class="empty-state">
            <div class="empty-content">
                <h4>No builds yet</h4>
                <p>Start creating your first Warframe build!</p>
                <button @click="$emit('create-new')" class="btn btn-primary">
                    Create Your First Build
                </button>
            </div>
        </div>

        <div v-else class="builds-grid">
            <div
                v-for="build in allBuilds"
                :key="build.id"
                class="build-card"
                :class="{ 'local-build': build.isLocal }"
            >
                <div class="build-header">
                    <h4>{{ build.name }}</h4>
                    <div class="build-badges">
                        <span v-if="build.isLocal" class="badge-local"
                            >Local</span
                        >
                        <span v-if="build.warframe" class="badge-warframe">
                            {{ build.warframe.name
                            }}{{
                                build.warframe.masteryReq
                                    ? ` MR ${build.warframe.masteryReq}`
                                    : ""
                            }}
                        </span>
                    </div>
                </div>

                <div v-if="build.warframe" class="build-info">
                    <div class="warframe-stats-mini">
                        <span class="stat">❤️ {{ build.warframe.health }}</span>
                        <span class="stat">🛡️ {{ build.warframe.shield }}</span>
                        <span class="stat">⚔️ {{ build.warframe.armor }}</span>
                        <span class="stat">⚡ {{ build.warframe.power }}</span>
                    </div>

                    <p class="build-description">
                        {{ build.warframe.description }}
                    </p>

                    <div
                        v-if="
                            build.warframe.abilities &&
                            build.warframe.abilities.length > 0
                        "
                        class="abilities-preview"
                    >
                        <div class="ability-mini">
                            {{ build.warframe.abilities[0].abilityName }}
                        </div>
                        <span
                            v-if="build.warframe.abilities.length > 1"
                            class="more-abilities"
                        >
                            +{{ build.warframe.abilities.length - 1 }} more
                        </span>
                    </div>
                </div>

                <div class="build-footer">
                    <span class="build-date">{{
                        formatDate(build.updated_at)
                    }}</span>

                    <div class="build-actions">
                        <button
                            @click="$emit('view-build', build)"
                            class="btn-view"
                            title="View Details"
                        >
                            👁️
                        </button>
                        <button
                            @click="$emit('edit-build', build)"
                            class="btn-edit"
                            title="Edit"
                        >
                            ✏️
                        </button>
                        <button
                            v-if="build.isLocal && isAuthenticated"
                            @click="handlePushBuild(build)"
                            class="btn-push"
                            title="Push to Cloud"
                        >
                            ☁️
                        </button>
                        <button
                            @click="handleDelete(build)"
                            class="btn-delete"
                            title="Delete"
                        >
                            🗑️
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="error" class="message message-error">
            {{ error }}
        </div>

        <Teleport to="body">
            <div v-if="deletingBuild" class="modal-overlay" @click="cancelDelete">
                <div
                    class="modal-content delete-modal"
                    @click.stop
                    @keydown.esc="cancelDelete"
                    tabindex="-1"
                    ref="deleteModalRef"
                >
                    <h3>Confirm Purge</h3>
                    <p>
                        Delete build <strong>"{{ deletingBuild.name }}"</strong>?
                        This data cannot be recovered from the archive.
                    </p>
                    <div class="modal-actions">
                        <button class="btn btn-danger" @click="confirmDelete">
                            Delete
                        </button>
                        <button class="btn btn-secondary" @click="cancelDelete">
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        </Teleport>
    </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from "vue";
import { useRouter } from "vue-router";
import { useBuilds, type BuildPublic } from "@/composables/useBuilds";

const emit = defineEmits<{
    "create-new": [];
    "view-build": [build: BuildPublic];
    "edit-build": [build: BuildPublic];
    "delete-build": [id: string];
}>();

const router = useRouter();

// Get builds data from props or fallback to composable
const props = defineProps<{
    allBuilds?: any[];
    loading?: boolean;
    error?: string;
    isAuthenticated?: boolean;
}>();

const {
    builds: composableBuilds,
    localBuilds: composableLocalBuilds,
    allBuilds: composableAllBuilds,
    loading: composableLoading,
    error: composableError,
    isAuthenticated: composableIsAuthenticated,
    syncLocalBuilds,
    pushBuildToCloud,
} = useBuilds();

// Use props if provided, otherwise fallback to composable values
const allBuilds = computed(() => props.allBuilds || composableAllBuilds.value);
const loading = computed(() =>
    props.loading !== undefined ? props.loading : composableLoading.value,
);
const error = computed(() =>
    props.error !== undefined ? props.error : composableError.value,
);
const isAuthenticated = computed(() =>
    props.isAuthenticated !== undefined
        ? props.isAuthenticated
        : composableIsAuthenticated.value,
);

const hasLocalBuilds = computed(() => composableLocalBuilds.value.length > 0);

const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        if (diffHours === 0) {
            const diffMins = Math.floor(diffMs / (1000 * 60));
            return diffMins <= 1 ? "Just now" : `${diffMins}m ago`;
        }
        return diffHours === 1 ? "1h ago" : `${diffHours}h ago`;
    } else if (diffDays === 1) {
        return "Yesterday";
    } else if (diffDays < 7) {
        return `${diffDays}d ago`;
    } else {
        return date.toLocaleDateString();
    }
};

const handlePushBuild = async (build: BuildPublic) => {
    if (
        !confirm(
            `Are you sure you want to push "${build.name}" to the cloud? This will remove the local version.`,
        )
    ) {
        return;
    }
    try {
        await pushBuildToCloud(build.id);
        alert("Build pushed successfully!");
    } catch (err) {
        console.error("Failed to push build:", err);
        alert(
            "Failed to push build: " +
                (err instanceof Error ? err.message : "Unknown error"),
        );
    }
};

const deletingBuild = ref<BuildPublic | null>(null);
const deleteModalRef = ref<HTMLElement | null>(null);

const handleDelete = (build: BuildPublic) => {
    deletingBuild.value = build;
    nextTick(() => deleteModalRef.value?.focus());
};

const cancelDelete = () => {
    deletingBuild.value = null;
};

const confirmDelete = () => {
    if (!deletingBuild.value) return;
    emit("delete-build", deletingBuild.value.id);
    deletingBuild.value = null;
};

const handleSyncLocalBuilds = async () => {
    try {
        await syncLocalBuilds();
        alert("Local builds synced successfully!");
    } catch (err) {
        console.error("Failed to sync builds:", err);
        alert(
            "Failed to sync builds: " +
                (err instanceof Error ? err.message : "Unknown error"),
        );
    }
};
</script>

<style scoped>
.build-list {
    background: var(--bg-card);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
}

.list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-6);
    flex-wrap: wrap;
    gap: var(--space-4);
}

.list-header h3 {
    color: var(--accent);
    margin: 0;
    font-size: var(--text-2xl);
}

.header-actions {
    display: flex;
    gap: var(--space-3);
}

.btn-sync {
    padding: var(--space-2) var(--space-4);
    border: none;
    border-radius: var(--radius-sm);
    font-size: var(--text-body);
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-normal);
    background: var(--warning);
    color: var(--text-on-accent);
}

.btn-sync:hover:not(:disabled) {
    background: var(--warning-hover);
}

.btn-sync:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.sync-prompt {
    background: rgba(var(--accent-rgb), 0.1);
    border: 1px solid var(--accent);
    border-radius: var(--radius-sm);
    padding: var(--space-4);
    margin-bottom: var(--space-6);
}

.sync-info p {
    color: var(--accent);
    margin: 0;
    font-size: var(--text-body);
}

.login-link,
.register-link {
    color: var(--accent);
    text-decoration: none;
    font-weight: bold;
}

.login-link:hover,
.register-link:hover {
    text-decoration: underline;
}

.loading-state,
.empty-state {
    text-align: center;
    padding: var(--space-12) var(--space-4);
    color: var(--text-muted);
}

.empty-content h4 {
    color: var(--text-muted-2);
    margin-bottom: var(--space-2);
    font-size: var(--text-xl);
}

.builds-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: var(--space-4);
}

.build-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    padding: var(--space-5);
    transition: all var(--transition-normal);
}

.build-card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
}

.build-card.local-build {
    border-left: 3px solid var(--warning);
}

.build-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--space-4);
}

.build-header h4 {
    color: var(--text-heading);
    margin: 0;
    font-size: var(--text-lg);
    flex: 1;
}

.build-badges {
    display: flex;
    gap: var(--space-2);
    flex-wrap: wrap;
}

.badge-warframe {
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: 500;
    background: var(--accent);
    color: var(--text-on-accent);
}

.build-info {
    margin-bottom: var(--space-4);
}

.warframe-stats-mini {
    display: flex;
    gap: var(--space-4);
    margin-bottom: var(--space-3);
    flex-wrap: wrap;
}

.stat {
    font-size: var(--text-base);
    color: var(--text-muted-2);
}

.build-description {
    color: var(--text-body);
    font-size: var(--text-md);
    line-height: 1.4;
    margin: 0 0 var(--space-3) 0;
    opacity: 0.9;
}

.abilities-preview {
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.ability-mini {
    background: var(--bg-elevated-2);
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-sm);
    font-size: var(--text-sm);
    color: var(--accent);
}

.more-abilities {
    font-size: var(--text-xs);
    color: var(--text-muted);
}

.build-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: var(--space-3);
    border-top: 1px solid var(--border-primary);
}

.build-date {
    font-size: var(--text-sm);
    color: var(--text-muted);
}

.build-actions {
    display: flex;
    gap: var(--space-2);
}

.btn-view,
.btn-edit,
.btn-delete,
.btn-push {
    background: none;
    border: none;
    padding: var(--space-1);
    cursor: pointer;
    border-radius: var(--radius-sm);
    transition: background-color var(--transition-normal);
    font-size: var(--text-body);
}

.btn-view:hover {
    background: rgba(var(--accent-rgb), 0.1);
}

.btn-edit:hover {
    background: var(--success-subtle);
}

.btn-push:hover {
    background: var(--warning-subtle);
}

.btn-delete:hover {
    background: var(--danger-subtle);
}

.delete-modal p {
    color: var(--text-body);
    line-height: 1.5;
    margin: 0 0 var(--space-6) 0;
}

.modal-actions {
    display: flex;
    gap: var(--space-2);
    justify-content: flex-end;
}

@media (max-width: 768px) {
    .builds-grid {
        grid-template-columns: 1fr;
    }

    .list-header {
        flex-direction: column;
        align-items: stretch;
    }

    .header-actions {
        justify-content: stretch;
    }

    .btn-sync,
    .btn-create {
        flex: 1;
    }
}
</style>
