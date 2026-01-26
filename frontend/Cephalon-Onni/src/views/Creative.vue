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
        <div v-if="error" class="error-message">
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
    padding: 0 1rem;
}

.page-header {
    text-align: center;
    margin-bottom: 2rem;
}

.page-header h1 {
    color: #a78bfa;
    letter-spacing: 2px;
    margin-bottom: 0.5rem;
    font-size: 2.5rem;
}

.subtitle {
    opacity: 0.7;
    margin-bottom: 2rem;
    font-size: 1.1rem;
}

.unsaved-build-indicator {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: #050b16;
    border: 2px solid #f59e0b;
    border-radius: 8px;
    padding: 1rem;
    max-width: 400px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    z-index: 1000;
}

.unsaved-content p {
    color: #f59e0b;
    margin: 0 0 1rem 0;
    font-size: 0.9rem;
}

.unsaved-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.btn-continue,
.btn-save,
.btn-discard {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-continue {
    background: #38bdf8;
    color: #021019;
}

.btn-continue:hover:not(:disabled) {
    background: #0ea5e9;
}

.btn-save {
    background: #22c55e;
    color: #021019;
}

.btn-save:hover:not(:disabled) {
    background: #16a34a;
}

.btn-save:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-discard {
    background: #374151;
    color: #e5e7eb;
}

.btn-discard:hover {
    background: #4b5563;
}

@media (max-width: 768px) {
    .unsaved-build-indicator {
        bottom: 1rem;
        right: 1rem;
        left: 1rem;
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
        font-size: 2rem;
    }
}

.error-message {
    background: #dc2626;
    color: white;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    text-align: center;
}

.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(5, 11, 22, 0.8);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 2000;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #374151;
    border-top: 4px solid #a78bfa;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

.loading-overlay p {
    color: white;
    font-size: 1.1rem;
}


</style>
