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

                <button @click="$emit('create-new')" class="btn-create">
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
                <button @click="$emit('create-new')" class="btn-create-empty">
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

        <div v-if="error" class="error-message">
            {{ error }}
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
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

const showDeleteConfirm = (build: BuildPublic) => {
    // Create custom confirmation dialog that won't be blocked
    const dialog = document.createElement('div');
    dialog.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #08121f;
        border: 2px solid #dc2626;
        border-radius: 8px;
        padding: 2rem;
        z-index: 10000;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
        min-width: 300px;
        color: #e2e8f0;
    `;
    
    dialog.innerHTML = `
        <h3 style="margin: 0 0 1rem 0; color: #dc2626;">Confirm Delete</h3>
        <p style="margin: 0 0 1.5rem 0;">Are you sure you want to delete "<strong>${build.name}</strong>"?</p>
        <div style="display: flex; gap: 1rem; justify-content: flex-end;">
            <button id="cancel-delete" style="
                padding: 0.5rem 1rem;
                background: #374151;
                color: #e5e7eb;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            ">Cancel</button>
            <button id="confirm-delete" style="
                padding: 0.5rem 1rem;
                background: #dc2626;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            ">Delete</button>
        </div>
    `;
    
    // Add backdrop
    const backdrop = document.createElement('div');
    backdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        z-index: 9999;
    `;
    
    document.body.appendChild(backdrop);
    document.body.appendChild(dialog);
    
    const cleanup = () => {
        document.body.removeChild(dialog);
        document.body.removeChild(backdrop);
    };
    
    return new Promise<boolean>((resolve) => {
        const cancelBtn = dialog.querySelector('#cancel-delete') as HTMLButtonElement;
        const confirmBtn = dialog.querySelector('#confirm-delete') as HTMLButtonElement;
        
        cancelBtn.onclick = () => {
            cleanup();
            resolve(false);
        };
        
        confirmBtn.onclick = () => {
            cleanup();
            resolve(true);
        };
        
        backdrop.onclick = () => {
            cleanup();
            resolve(false);
        };
        
        // Focus the cancel button by default
        cancelBtn.focus();
    });
};

const handleDelete = async (build: BuildPublic) => {
    console.log('Delete button clicked for build:', build);
    const confirmed = await showDeleteConfirm(build);
    console.log('Custom confirm result:', confirmed);
    if (confirmed) {
        console.log('Emitting delete-build event with id:', build.id);
        emit("delete-build", build.id);
    } else {
        console.log('Delete cancelled by user');
    }
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
    background: #050b16;
    border: 1px solid #1b2a3a;
    border-radius: 8px;
    padding: 1.5rem;
}

.list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.list-header h3 {
    color: #38bdf8;
    margin: 0;
    font-size: 1.5rem;
}

.header-actions {
    display: flex;
    gap: 0.75rem;
}

.btn-sync,
.btn-create {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-sync {
    background: #f59e0b;
    color: #021019;
}

.btn-sync:hover:not(:disabled) {
    background: #d97706;
}

.btn-create {
    background: #38bdf8;
    color: #021019;
}

.btn-create:hover {
    background: #0ea5e9;
}

.btn-sync:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.sync-prompt {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid #38bdf8;
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 1.5rem;
}

.sync-info p {
    color: #38bdf8;
    margin: 0;
    font-size: 0.9rem;
}

.login-link,
.register-link {
    color: #38bdf8;
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
    padding: 3rem 1rem;
    color: #64748b;
}

.empty-content h4 {
    color: #94a3b8;
    margin-bottom: 0.5rem;
    font-size: 1.2rem;
}

.btn-create-empty {
    margin-top: 1rem;
    padding: 0.75rem 1.5rem;
    background: #38bdf8;
    color: #021019;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
}

.btn-create-empty:hover {
    background: #0ea5e9;
}

.builds-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1rem;
}

.build-card {
    background: #08121f;
    border: 1px solid #1b2a3a;
    border-radius: 8px;
    padding: 1.25rem;
    transition: all 0.2s;
}

.build-card:hover {
    border-color: #38bdf8;
    transform: translateY(-2px);
}

.build-card.local-build {
    border-left: 3px solid #f59e0b;
}

.build-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.build-header h4 {
    color: #e2e8f0;
    margin: 0;
    font-size: 1.1rem;
    flex: 1;
}

.build-badges {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.badge-local,
.badge-warframe {
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 500;
}

.badge-local {
    background: #f59e0b;
    color: #021019;
}

.badge-warframe {
    background: #38bdf8;
    color: #021019;
}

.build-info {
    margin-bottom: 1rem;
}

.warframe-stats-mini {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
}

.stat {
    font-size: 0.8rem;
    color: #94a3b8;
}

.build-description {
    color: #cbd5e1;
    font-size: 0.85rem;
    line-height: 1.4;
    margin: 0 0 0.75rem 0;
    opacity: 0.9;
}

.abilities-preview {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.ability-mini {
    background: #1e293b;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    color: #38bdf8;
}

.more-abilities {
    font-size: 0.7rem;
    color: #64748b;
}

.build-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 0.75rem;
    border-top: 1px solid #1b2a3a;
}

.build-date {
    font-size: 0.75rem;
    color: #64748b;
}

.build-actions {
    display: flex;
    gap: 0.5rem;
}

.btn-view,
.btn-edit,
.btn-delete,
.btn-push {
    background: none;
    border: none;
    padding: 0.25rem;
    cursor: pointer;
    border-radius: 4px;
    transition: background-color 0.2s;
    font-size: 0.9rem;
}

.btn-view:hover {
    background: rgba(59, 130, 246, 0.1);
}

.btn-edit:hover {
    background: rgba(34, 197, 94, 0.1);
}

.btn-push:hover {
    background: rgba(245, 158, 11, 0.1);
}

.btn-delete:hover {
    background: rgba(239, 68, 68, 0.1);
}

.error-message {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid #ef4444;
    color: #ef4444;
    padding: 0.75rem;
    border-radius: 4px;
    margin-top: 1rem;
    font-size: 0.9rem;
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
