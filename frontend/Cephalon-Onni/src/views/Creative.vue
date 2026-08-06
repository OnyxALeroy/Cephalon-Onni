<template>
    <div class="creative-mode">
        <div class="page-header">
            <h1>Creative Mode</h1>
            <p class="subtitle">Design and manage your Warframe builds</p>
        </div>

        <!-- List View -->
        <div v-if="currentView === 'list'">
            <BuildList
                :all-builds="allBuilds"
                :loading="loading"
                :error="error"
                :is-authenticated="isAuthenticated"
                @create-new="startNewBuild"
                @view-build="viewBuild"
                @edit-build="editBuild"
                @delete-build="handleDeleteBuild"
            />
        </div>

        <!-- Build Form View -->
        <div v-else-if="currentView === 'form'">
            <BuildForm
                :build="editingBuild"
                :is-editing="!!editingBuild?.id"
                @submit="handleBuildSubmit"
                @cancel="backToList"
            />
        </div>

        <!-- Build Details View -->
        <div v-else-if="currentView === 'details'">
            <BuildDetails
                v-if="selectedBuild"
                :build="selectedBuild"
                @back="backToList"
                @edit-build="editBuild"
            />
        </div>

        <!-- Error Display -->
        <div v-if="error" class="message message-error">
            {{ error }}
        </div>

        <!-- Loading Overlay -->
        <div v-if="loading" class="loading-overlay">
            <div class="loading-spinner"></div>
            <p>Loading...</p>
        </div>

        <!-- Current Build Indicator -->
        <div
            v-if="hasUnsavedBuild && currentView === 'list'"
            class="unsaved-build-indicator"
        >
            <div class="unsaved-content">
                <p>
                    <strong>Unsaved Build:</strong>
                    {{ currentBuild.name || "Unnamed" }}
                    <span v-if="currentBuild.warframe_uniqueName">
                        with
                        {{ getWarframeName(currentBuild.warframe_uniqueName) }}
                    </span>
                </p>
                <div class="unsaved-actions">
                    <button
                        @click="continueEditing"
                        class="btn-continue"
                        :disabled="loading"
                    >
                        Continue Editing
                    </button>
                    <button
                        @click="saveAsNew"
                        class="btn-save"
                        :disabled="loading"
                    >
                        Save as New
                    </button>
                    <button
                        @click="discardBuild"
                        class="btn-discard"
                        :disabled="loading"
                    >
                        Discard
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
 import { ref, computed, onMounted } from "vue";
 import BuildList from "@/components/BuildList.vue";
 import BuildDetails from "@/components/BuildDetails.vue";
 import BuildForm from "@/components/BuildForm.vue";
 import {
     useBuilds,
     type BuildPublic,
     type BuildCreate,
     type BuildUpdate,
     type WarframeDetails,
 } from "@/composables/useBuilds";

type ViewType = "list" | "form" | "details";

const {
    currentBuild,
    loading,
    hasUnsavedBuild,
    allBuilds,
    error,
    isAuthenticated,
    setCurrentBuild,
    clearCurrentBuild,
    saveCurrentBuildAsNew,
    createBuild,
    updateBuild,
    deleteBuild,
    fetchBuilds,
    checkAuthStatus,
    getAllWarframes,
} = useBuilds();

 const currentView = ref<ViewType>("list");
 const editingBuild = ref<BuildCreate & { id?: string }>();
 const selectedBuild = ref<BuildPublic>();
 const warframes = ref<WarframeDetails[]>([]);

// Mock warframe name mapping (in real app, this would come from API)
const warframeNames: Record<string, string> = {
    "/Lotus/Powersuits/Excalibur/ExcaliburBaseSuit": "Excalibur",
    "/Lotus/Powersuits/Mag/MagBaseSuit": "Mag",
};

 const getWarframeName = (uniqueName: string) => {
    const warframe = warframes.value.find(
        (w) => (w.uniqueName || w.uniquename) === uniqueName,
    );
    return (
        warframe?.name ||
        uniqueName.split("/").pop()?.replace("BaseSuit", "") ||
        "Unknown"
    );
};

const loadWarframes = async () => {
    try {
        console.log("Loading warframes...");
        warframes.value = await getAllWarframes();
        console.log(`Loaded ${warframes.value.length} warframes`);
    } catch (err) {
        console.error("Failed to load warframes:", err);
    }
};

 const startNewBuild = () => {
    editingBuild.value = undefined;
    currentView.value = "form";
};

const continueEditing = () => {
    editingBuild.value = { ...currentBuild.value };
    currentView.value = "form";
};

const saveAsNew = async () => {
    try {
        await saveCurrentBuildAsNew();
        await fetchBuilds();
        alert("Build saved successfully!");
    } catch (err) {
        console.error("Failed to save build:", err);
        alert(
            "Failed to save build: " +
                (err instanceof Error ? err.message : "Unknown error"),
        );
    }
};

const discardBuild = () => {
    if (confirm("Are you sure you want to discard your unsaved build?")) {
        clearCurrentBuild();
    }
};

const viewBuild = (build: BuildPublic) => {
    selectedBuild.value = build;
    currentView.value = "details";
};

  const editBuild = (build: BuildPublic) => {
    editingBuild.value = {
        id: build.id,
        name: build.name,
        warframe_uniqueName: build.warframe_uniqueName,
        warframe_mods: build.warframe_mods || [],
        warframe_arcanes: build.warframe_arcanes || [],
        primary_weapon: build.primary_weapon || null,
        secondary_weapon: build.secondary_weapon || null,
        melee_weapon: build.melee_weapon || null,
    };
    currentView.value = "form";
};

const handleDeleteBuild = async (id: string) => {
    console.log('handleDeleteBuild called with id:', id);
    try {
        await deleteBuild(id);
        console.log('Build deleted successfully');
        // Optionally show a success message, though the reactive list updating is usually enough.
    } catch (err) {
        console.error("Failed to delete build:", err);
        alert(
            "Failed to delete build: " +
                (err instanceof Error ? err.message : "Unknown error"),
        );
    }
};

 const handleBuildSubmit = async (buildData: BuildCreate | BuildUpdate) => {
    try {
        console.log("Submitting build data:", buildData);
        
        if (editingBuild.value?.id) {
            // Update existing build
            await updateBuild(editingBuild.value.id, buildData);
            alert("Build updated successfully!");
        } else {
            // Create new build
            await createBuild(buildData as BuildCreate);
            alert("Build created successfully!");
        }

        await fetchBuilds();
        backToList();
    } catch (err) {
        console.error("Failed to save build:", err);
        let errorMessage = "Failed to save build: ";

        if (err instanceof Error) {
            errorMessage += err.message;
        } else if (err && typeof err === 'object' && 'detail' in err) {
            // Handle FastAPI validation errors
            errorMessage += JSON.stringify(err.detail, null, 2);
        } else {
            errorMessage += "Unknown error";
        }

        // Provide more user-friendly error messages
        if (errorMessage.includes("422") || errorMessage.includes("Validation failed")) {
            errorMessage =
                "Invalid data provided. Please check all fields and try again.";
        } else if (
            errorMessage.includes("Warframe") &&
            errorMessage.includes("not found")
        ) {
            errorMessage =
                "Selected warframe is not available. Please select a different warframe.";
        } else if (errorMessage.includes("Maximum number of builds")) {
            errorMessage =
                "You've reached the maximum number of builds (30). Please delete some builds first.";
        }

        alert(errorMessage);
    }
};

const backToList = () => {
    currentView.value = "list";
    editingBuild.value = undefined;
    selectedBuild.value = undefined;
};

onMounted(async () => {
    await Promise.all([fetchBuilds(), checkAuthStatus(), loadWarframes()]);
});
</script>

<style scoped>
.creative-mode {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--space-4);
}

.page-header {
    text-align: center;
    margin-bottom: var(--space-8);
}

.page-header h1 {
    color: var(--purple);
    letter-spacing: 2px;
    margin-bottom: var(--space-2);
    font-size: var(--text-4xl);
}

.subtitle {
    opacity: 0.7;
    margin-bottom: var(--space-8);
    font-size: var(--text-lg);
}

.unsaved-build-indicator {
    position: fixed;
    bottom: var(--space-8);
    right: var(--space-8);
    background: var(--bg-card);
    border: 2px solid var(--warning);
    border-radius: var(--radius-lg);
    padding: var(--space-4);
    max-width: 400px;
    box-shadow: var(--shadow-sm);
    z-index: 1000;
}

.unsaved-content p {
    color: var(--warning);
    margin: 0 0 var(--space-4) 0;
    font-size: var(--text-body);
}

.unsaved-actions {
    display: flex;
    gap: var(--space-2);
    flex-wrap: wrap;
}

.btn-continue,
.btn-save,
.btn-discard {
    padding: var(--space-2) var(--space-4);
    border: none;
    border-radius: var(--radius-sm);
    font-size: var(--text-base);
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-normal);
}

.btn-continue {
    background: var(--accent);
    color: var(--text-on-accent);
}

.btn-continue:hover:not(:disabled) {
    background: var(--accent-hover);
}

.btn-save {
    background: var(--success);
    color: var(--text-on-accent);
}

.btn-save:hover:not(:disabled) {
    background: var(--success-hover);
}

.btn-save:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-discard {
    background: var(--gray-btn);
    color: var(--text-gray-light);
}

.btn-discard:hover {
    background: var(--gray-btn-hover);
}

@media (max-width: 768px) {
    .unsaved-build-indicator {
        bottom: var(--space-4);
        right: var(--space-4);
        left: var(--space-4);
        max-width: none;
    }

    .unsaved-actions {
        justify-content: stretch;
    }

    .btn-continue,
    .btn-save,
    .btn-discard {
        flex: 1;
        text-align: center;
    }

    .page-header h1 {
        font-size: var(--text-3xl);
    }
}
</style>
