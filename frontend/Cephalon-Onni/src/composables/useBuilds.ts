import { ref, computed, watch } from "vue";

// API Response Interfaces (matching backend Pydantic models)
export interface WarframeAbility {
  abilityUniqueName: string;
  abilityName: string;
  description: string;
}

export interface WarframeDetails {
  uniqueName: string;
  name: string;
  parentName?: string;
  description: string;
  health: number;
  shield: number;
  armor: number;
  stamina: number;
  power: number;
  codexSecret: boolean;
  masteryReq: number;
  sprintSpeed: number;
  passiveDescription?: string;
  exalted?: string[];
  abilities: WarframeAbility[];
  productCategory: string;
}

export interface ModDetails {
  uniqueName: string;
  name: string;
  polarity: string;
  rarity: string;
  type?: string;
  subtype?: string;
  codexSecret: boolean;
  baseDrain: number;
  fusionLimit: number;
  compatName?: string;
  modSet?: string;
  isUtility?: boolean;
  description?: string[];
}

export interface WeaponDetails {
  uniqueName: string;
  name: string;
  codexSecret: boolean;
  criticalChance: number;
  criticalMultiplier: number;
  damagePerShot: number[];
  description: string;
  fireRate: number;
  masteryReq: number;
  omegaAttenuation: number;
  procChance: number;
  productCategory: string;
  totalDamage: number;
  accuracy?: number;
  magazineSize?: number;
  reloadTime?: number;
  multishot?: number;
  noise?: string;
  trigger?: string;
}

export interface ArcaneDetails {
  uniqueName: string;
  name: string;
  codexSecret: boolean;
  rarity?: string;
  levelStats: object[];
}

export interface EquippedMod {
  uniqueName: string;
  level: number;
}

export interface WeaponBuild {
  weapon_uniqueName: string;
  mods: EquippedMod[];
  arcane_uniqueName?: string;
}

export interface BuildCreate {
  name: string;
  warframe_uniqueName: string;
  warframe_mods: EquippedMod[];
  warframe_arcanes: string[];
  primary_weapon?: WeaponBuild | null;
  secondary_weapon?: WeaponBuild | null;
  melee_weapon?: WeaponBuild | null;
}

export interface BuildUpdate {
  name?: string;
  warframe_uniqueName?: string;
  warframe_mods?: EquippedMod[];
  warframe_arcanes?: string[];
  primary_weapon?: WeaponBuild | null;
  secondary_weapon?: WeaponBuild | null;
  melee_weapon?: WeaponBuild | null;
}

export interface BuildPublic {
  id: string;
  name: string;
  warframe_uniqueName: string;
  created_at: string;
  updated_at: string;
  warframe?: WarframeDetails;
  warframe_mods: EquippedMod[];
  warframe_arcanes: string[];
  primary_weapon?: WeaponBuild | null;
  secondary_weapon?: WeaponBuild | null;
  melee_weapon?: WeaponBuild | null;
  isLocal?: boolean;
}

export interface BuildWithDetails {
  id: string;
  name: string;
  warframe_uniqueName: string;
  created_at: string;
  updated_at: string;
  warframe: WarframeDetails;
  warframe_mods: EquippedMod[];
  warframe_arcanes: ArcaneDetails[];
  primary_weapon?: WeaponBuild | null;
  secondary_weapon?: WeaponBuild | null;
  melee_weapon?: WeaponBuild | null;
  primary_weapon_details?: WeaponDetails | null;
  secondary_weapon_details?: WeaponDetails | null;
  melee_weapon_details?: WeaponDetails | null;
  primary_arcane_details?: ArcaneDetails | null;
  secondary_arcane_details?: ArcaneDetails | null;
  melee_arcane_details?: ArcaneDetails | null;
}

// Local Storage Interface for unauthenticated users
export interface LocalBuild extends BuildCreate {
  id: string;
  created_at: string;
  updated_at: string;
  isLocal: boolean;
}

const STORAGE_KEY = "creativeBuilds";
const CURRENT_BUILD_KEY = "currentCreativeBuild";

// Default current build
const defaultCurrentBuild: BuildCreate = {
  name: "",
  warframe_uniqueName: "",
  warframe_mods: [],
  warframe_arcanes: [],
  primary_weapon: null,
  secondary_weapon: null,
  melee_weapon: null,
};

// --- Singleton State ---
const builds = ref<BuildPublic[]>([]);
const currentBuild = ref<BuildCreate>({ ...defaultCurrentBuild });
const localBuilds = ref<LocalBuild[]>([]);
const loading = ref(false);
const error = ref("");
const isAuthenticated = ref(false);
// ---

export function useBuilds() {
  // Computed properties
  const hasUnsavedBuild = computed(() => {
    return (
      currentBuild.value.name !== "" ||
      currentBuild.value.warframe_uniqueName !== "" ||
      currentBuild.value.warframe_mods.length > 0 ||
      currentBuild.value.warframe_arcanes.length > 0 ||
      currentBuild.value.primary_weapon !== null ||
      currentBuild.value.secondary_weapon !== null ||
      currentBuild.value.melee_weapon !== null
    );
  });

  const allBuilds = computed(() => {
    const userBuilds = builds.value.map((build) => ({
      ...build,
      isLocal: false,
    }));
    const local = localBuilds.value.map((build) => ({
      ...build,
      isLocal: true,
    }));
    return [...userBuilds, ...local].sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    );
  });

  // Load local data on initialization
  const loadLocalData = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        localBuilds.value = JSON.parse(stored);
      }

      const current = localStorage.getItem(CURRENT_BUILD_KEY);
      if (current) {
        currentBuild.value = JSON.parse(current);
      }
    } catch (err) {
      console.warn("Failed to load local build data:", err);
    }
  };

  // Save local builds to localStorage
  const saveLocalBuilds = () => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(localBuilds.value));
    } catch (err) {
      console.warn("Failed to save local builds:", err);
    }
  };

  // Save current build to localStorage
  const saveCurrentBuild = () => {
    try {
      if (hasUnsavedBuild.value) {
        localStorage.setItem(
          CURRENT_BUILD_KEY,
          JSON.stringify(currentBuild.value),
        );
      } else {
        localStorage.removeItem(CURRENT_BUILD_KEY);
      }
    } catch (err) {
      console.warn("Failed to save current build:", err);
    }
  };

  // Watch for changes and auto-save
  watch(localBuilds, saveLocalBuilds, { deep: true });
  watch(currentBuild, saveCurrentBuild, { deep: true });

  // Watch for auth changes to clear remote builds on logout
  watch(isAuthenticated, (isAuth, wasAuth) => {
    if (wasAuth && !isAuth) {
      builds.value = [];
    }
  });

  // Check authentication status
  const checkAuthStatus = async () => {
    try {
      const response = await fetch("/api/users/profile", {
        credentials: "include",
      });
      isAuthenticated.value = response.ok;
      return isAuthenticated.value;
    } catch {
      isAuthenticated.value = false;
      return false;
    }
  };

  // API calls
  const fetchBuilds = async () => {
    loading.value = true;
    error.value = "";

    try {
      const isAuth = await checkAuthStatus();
      if (isAuth) {
        const response = await fetch("/api/builds?include_details=true", {
          credentials: "include",
        });
        console.log("Fetch builds URL:", "/api/builds?include_details=true");
        console.log("Fetch builds response status:", response.status);

        if (!response.ok) {
          throw new Error("Failed to fetch builds");
        }

        builds.value = await response.json();
      } else {
        // Clear remote builds if not authenticated
        builds.value = [];
      }
    } catch (err: any) {
      error.value = err.message || "Failed to load builds";
    } finally {
      loading.value = false;
    }
  };

  const createBuild = async (build: BuildCreate) => {
    loading.value = true;
    error.value = "";

    try {
      const isAuth = await checkAuthStatus();

      if (isAuth) {
        // Validate build data before sending
        if (!build.name || build.name.trim() === "") {
          throw new Error("Build name is required");
        }
        if (
          !build.warframe_uniqueName ||
          build.warframe_uniqueName.trim() === ""
        ) {
          throw new Error("Warframe selection is required");
        }

        // Create on backend
        console.log("Creating build with data:", build);
        const response = await fetch("/api/builds/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify(build),
        });
        console.log("Create build response status:", response.status);

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Failed to create build");
        }

        const newBuild = await response.json();
        builds.value.unshift(newBuild);
        return newBuild;
      } else {
        // Create locally
        const localBuild: LocalBuild = {
          ...build,
          id: `local_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          isLocal: true,
        };

        localBuilds.value.push(localBuild);
        return localBuild;
      }
    } catch (err: any) {
      error.value = err.message || "Failed to create build";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const updateBuild = async (id: string, update: BuildUpdate) => {
    loading.value = true;
    error.value = "";

    try {
      const isAuth = await checkAuthStatus();

      if (isAuth && !id.startsWith("local_")) {
        // Update on backend
        const response = await fetch(`/api/builds/${id}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify(update),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Failed to update build");
        }

        const updatedBuild = await response.json();
        const index = builds.value.findIndex((b) => b.id === id);
        if (index !== -1) {
          builds.value[index] = updatedBuild;
        }
        return updatedBuild;
      } else {
        // Update local build
        const index = localBuilds.value.findIndex((b) => b.id === id);
        if (index === -1) {
          throw new Error("Build not found");
        }

        localBuilds.value[index] = {
          ...localBuilds.value[index],
          ...update,
          updated_at: new Date().toISOString(),
        };

        return localBuilds.value[index];
      }
    } catch (err: any) {
      error.value = err.message || "Failed to update build";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const deleteBuild = async (id: string) => {
    loading.value = true;
    error.value = "";

    try {
      const isLocalBuild = id.startsWith("local_");

      if (isLocalBuild) {
        // Handle local build deletion
        localBuilds.value = localBuilds.value.filter((b) => b.id !== id);
        return; // Done
      }

      // Handle remote build deletion
      const isAuth = await checkAuthStatus();
      if (!isAuth) {
        throw new Error("Authentication required to delete cloud builds.");
      }

      const response = await fetch(`/api/builds/${id}`, {
        method: "DELETE",
        credentials: "include",
      });

      if (!response.ok) {
        // Try to get a meaningful error from the backend
        const errorData = await response
          .json()
          .catch(() => ({ detail: "Failed to delete build from server" }));
        throw new Error(errorData.detail);
      }

      // If deletion was successful, refetch the builds list from the server
      await fetchBuilds();
    } catch (err: any) {
      error.value = err.message || "Failed to delete build";
      throw err; // Re-throw so the component can catch it and show an alert
    } finally {
      loading.value = false;
    }
  };

  const pushBuildToCloud = async (id: string) => {
    const buildToPush = localBuilds.value.find((b) => b.id === id);
    if (!buildToPush) {
      throw new Error("Local build not found");
    }

    loading.value = true;
    error.value = "";

    try {
      const isAuth = await checkAuthStatus();
      if (!isAuth) {
        throw new Error("User must be authenticated to push builds");
      }

      // 1. Create the build on the backend
      const newBuild = await createBuild({
        name: buildToPush.name,
        warframe_uniqueName: buildToPush.warframe_uniqueName,
        warframe_mods: buildToPush.warframe_mods || [],
        warframe_arcanes: buildToPush.warframe_arcanes || [],
        primary_weapon: buildToPush.primary_weapon || null,
        secondary_weapon: buildToPush.secondary_weapon || null,
        melee_weapon: buildToPush.melee_weapon || null,
      });

      if (newBuild) {
        // 2. Delete the local build
        localBuilds.value = localBuilds.value.filter((b) => b.id !== id);
      }

      // 3. Refresh server data
      await fetchBuilds();
    } catch (err: any) {
      error.value = err.message || "Failed to push build to cloud";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const syncLocalBuilds = async () => {
    if (localBuilds.value.length === 0) return;

    loading.value = true;
    error.value = "";

    try {
      const isAuth = await checkAuthStatus();
      if (!isAuth) {
        throw new Error("Must be authenticated to sync builds");
      }

      // Sync each local build to the backend
      for (const localBuild of localBuilds.value) {
        try {
          await createBuild({
            name: localBuild.name,
            warframe_uniqueName: localBuild.warframe_uniqueName,
            warframe_mods: localBuild.warframe_mods || [],
            warframe_arcanes: localBuild.warframe_arcanes || [],
            primary_weapon: localBuild.primary_weapon || null,
            secondary_weapon: localBuild.secondary_weapon || null,
            melee_weapon: localBuild.melee_weapon || null,
          });
        } catch (err) {
          console.warn(`Failed to sync local build "${localBuild.name}":`, err);
        }
      }

      // Clear local builds after sync
      localBuilds.value = [];
      await fetchBuilds();
    } catch (err: any) {
      error.value = err.message || "Failed to sync local builds";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Current build management
  const setCurrentBuild = (build: BuildCreate) => {
    currentBuild.value = { ...build };
  };

  const clearCurrentBuild = () => {
    currentBuild.value = { ...defaultCurrentBuild };
  };

  const saveCurrentBuildAsNew = async () => {
    if (!hasUnsavedBuild.value) {
      throw new Error("No build to save");
    }

    const newBuild = await createBuild(currentBuild.value);
    clearCurrentBuild();
    return newBuild;
  };

  // Get warframe details from API
  const getWarframeDetails = async (
    uniqueName: string,
  ): Promise<WarframeDetails | null> => {
    try {
      if (!uniqueName || uniqueName === "undefined") {
        console.warn(
          "Invalid uniqueName passed to getWarframeDetails:",
          uniqueName,
        );
        return null;
      }

      const response = await fetch(`/api/warframes/${uniqueName}`, {
        credentials: "include",
      });

      if (!response.ok) {
        return null;
      }

      return await response.json();
    } catch (err) {
      console.error("Failed to fetch warframe details:", err);
      return null;
    }
  };

  // Get all warframes from API
  const getAllWarframes = async (): Promise<WarframeDetails[]> => {
    try {
      const response = await fetch("/api/warframes/", {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch warframes");
      }

      const warframes = await response.json();

      // Filter out any warframes without uniqueName
      const validWarframes = warframes.filter((warframe: any) => {
        // Handle both camelCase and lowercase property names
        const uniqueName = warframe.uniqueName || warframe.uniquename;
        const isValid = uniqueName && uniqueName !== "undefined";
        if (!isValid) {
          console.warn("Warframe missing uniqueName:", warframe);
        }
        // Normalize the property name to uniqueName for consistency
        if (warframe.uniquename && !warframe.uniqueName) {
          warframe.uniqueName = warframe.uniquename;
        }
        return isValid;
      });

      console.log(
        `Filtered ${warframes.length} warframes to ${validWarframes.length} valid ones`,
      );

      return validWarframes;
    } catch (err: any) {
      console.error("Failed to fetch warframes:", err);
      throw err;
    }
  };

  // Get available warframes for build creation
  const getAvailableWarframes = async () => {
    try {
      const response = await fetch("/api/builds/available/warframes", {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch available warframes");
      }

      return await response.json();
    } catch (err: any) {
      console.error("Failed to fetch available warframes:", err);
      throw err;
    }
  };

  // Get available weapons for build creation
  const getAvailableWeapons = async () => {
    try {
      const response = await fetch("/api/builds/available/weapons", {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch available weapons");
      }

      return await response.json();
    } catch (err: any) {
      console.error("Failed to fetch available weapons:", err);
      throw err;
    }
  };

  // Get available mods for build creation
  const getAvailableMods = async () => {
    try {
      const response = await fetch("/api/builds/available/mods", {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch available mods");
      }

      return await response.json();
    } catch (err: any) {
      console.error("Failed to fetch available mods:", err);
      throw err;
    }
  };

  // Get available arcanes for build creation
  const getAvailableArcanes = async () => {
    try {
      const response = await fetch("/api/builds/available/arcanes", {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch available arcanes");
      }

      return await response.json();
    } catch (err: any) {
      console.error("Failed to fetch available arcanes:", err);
      throw err;
    }
  };

  // Initialize
  loadLocalData();

  return {
    // State
    builds,
    currentBuild,
    localBuilds,
    allBuilds,
    loading,
    error,
    isAuthenticated,
    hasUnsavedBuild,

    // Methods
    fetchBuilds,
    createBuild,
    updateBuild,
    deleteBuild,
    pushBuildToCloud,
    syncLocalBuilds,
    setCurrentBuild,
    clearCurrentBuild,
    saveCurrentBuildAsNew,
    checkAuthStatus,
    getWarframeDetails,
    getAllWarframes,
    getAvailableWarframes,
    getAvailableWeapons,
    getAvailableMods,
    getAvailableArcanes,
  };
}
