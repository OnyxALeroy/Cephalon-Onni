<template>
  <div class="build-form">
    <h3>{{ isEditing ? 'Edit Build' : 'Create New Build' }}</h3>
    
    <form @submit.prevent="handleSubmit" class="form">
      <div class="form-section">
        <h4>Basic Information</h4>
        
        <div class="form-group">
          <label for="build-name">Build Name</label>
          <input
            id="build-name"
            v-model="formData.name"
            type="text"
            required
            placeholder="My Awesome Build"
            :disabled="loading"
            maxlength="50"
          />
        </div>

        <div class="form-group">
          <label for="warframe-select">Warframe</label>
          <select
            id="warframe-select"
            v-model="formData.warframe_uniqueName"
            required
            :disabled="loading || warframes.length === 0"
          >
            <option value="">Select a Warframe</option>
            <option
              v-for="warframe in warframes"
              :key="warframe.uniqueName"
              :value="warframe.uniqueName"
            >
              {{ warframe.name }}{{ warframe.masteryReq ? ` (MR ${warframe.masteryReq})` : '' }}
            </option>
          </select>
        </div>
      </div>

      <div class="form-section">
        <h4>Warframe Configuration</h4>
        
        <div class="form-group">
          <label>Warframe Mods (Max: 10)</label>
          <div class="mods-container">
            <div 
              v-for="(mod, index) in formData.warframe_mods" 
              :key="index"
              class="mod-slot"
            >
              <select 
                v-model="mod.uniqueName" 
                :disabled="loading || availableMods.length === 0"
                @change="updateModPolarity(index, mod.uniqueName)"
              >
                <option value="">No Mod</option>
                <option
                  v-for="availableMod in availableMods"
                  :key="availableMod.uniqueName"
                  :value="availableMod.uniqueName"
                >
                  {{ availableMod.name }} ({{ availableMod.type }})
                </option>
              </select>
              <input 
                v-model.number="mod.level" 
                type="number" 
                min="0" 
                max="10" 
                placeholder="Lvl"
                :disabled="loading || !mod.uniqueName"
              />
              <button 
                type="button" 
                @click="removeWarframeMod(index)"
                :disabled="loading"
                class="btn-remove"
              >
                ×
              </button>
            </div>
            <button 
              type="button" 
              @click="addWarframeMod" 
              :disabled="loading || formData.warframe_mods.length >= 10"
              class="btn-add"
            >
              + Add Mod
            </button>
          </div>
        </div>

        <div class="form-group">
          <label>Warframe Arcanes (Max: 2)</label>
          <div class="arcanes-container">
            <div 
              v-for="(arcane, index) in formData.warframe_arcanes" 
              :key="index"
              class="arcane-slot"
            >
              <select 
                v-model="formData.warframe_arcanes[index]" 
                :disabled="loading || availableArcanes.length === 0"
              >
                <option value="">No Arcane</option>
                <option
                  v-for="availableArcane in availableArcanes"
                  :key="availableArcane.uniqueName"
                  :value="availableArcane.uniqueName"
                >
                  {{ availableArcane.name }} ({{ availableArcane.rarity }})
                </option>
              </select>
              <button 
                type="button" 
                @click="removeWarframeArcane(index)"
                :disabled="loading"
                class="btn-remove"
              >
                ×
              </button>
            </div>
            <button 
              type="button" 
              @click="addWarframeArcane" 
              :disabled="loading || formData.warframe_arcanes.length >= 2"
              class="btn-add"
            >
              + Add Arcane
            </button>
          </div>
        </div>
      </div>

      <div class="form-section">
        <h4>Weapons Configuration</h4>
        
        <div v-for="(weapon, weaponType) in weaponSlots" :key="weaponType" class="weapon-section">
          <div class="form-group">
            <label>{{ (weapon as any).label }}</label>
            <select
              v-model="formData[weaponType as keyof typeof weaponSlots].weapon_uniqueName"
              :disabled="loading || availableWeapons.length === 0"
              @change="clearWeaponMods(weaponType as keyof typeof weaponSlots)"
            >
              <option value="">No {{ weapon.label }}</option>
              <option
                v-for="availableWeapon in availableWeapons"
                :key="availableWeapon.uniqueName"
                :value="availableWeapon.uniqueName"
              >
                {{ availableWeapon.name }} ({{ availableWeapon.productCategory }})
              </option>
            </select>
          </div>

          <div v-if="formData[weaponType].weapon_uniqueName" class="weapon-details">
            <div class="form-group">
              <label>{{ (weapon as any).label }} Mods (Max: 9)</label>
              <div class="mods-container">
                <div 
                  v-for="(mod, index) in formData[weaponType].mods" 
                  :key="index"
                  class="mod-slot"
                >
                  <select 
                    v-model="mod.uniqueName" 
                    :disabled="loading || availableMods.length === 0"
                  >
                    <option value="">No Mod</option>
                    <option
                      v-for="availableMod in availableMods"
                      :key="availableMod.uniqueName"
                      :value="availableMod.uniqueName"
                    >
                      {{ availableMod.name }}
                    </option>
                  </select>
                  <input 
                    v-model.number="mod.level" 
                    type="number" 
                    min="0" 
                    max="10" 
                    placeholder="Lvl"
                    :disabled="loading || !mod.uniqueName"
                  />
                  <button 
                    type="button" 
                    @click="removeWeaponMod(weaponType, index)"
                    :disabled="loading"
                    class="btn-remove"
                  >
                    ×
                  </button>
                </div>
                <button 
                  type="button" 
                  @click="addWeaponMod(weaponType as keyof typeof weaponSlots)" 
                  :disabled="loading || formData[weaponType as keyof typeof weaponSlots].mods.length >= 9"
                  class="btn-add"
                >
                  + Add Mod
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>{{ (weapon as any).label }} Arcane</label>
              <select
                v-model="formData[weaponType as keyof typeof weaponSlots].arcane_uniqueName"
                :disabled="loading || availableArcanes.length === 0"
              >
                <option value="">No Arcane</option>
                <option
                  v-for="availableArcane in availableArcanes"
                  :key="availableArcane.uniqueName"
                  :value="availableArcane.uniqueName"
                >
                  {{ availableArcane.name }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn-primary" :disabled="loading || !isFormValid">
          <span v-if="loading">Saving...</span>
          <span v-else>{{ isEditing ? 'Update' : 'Save' }} Build</span>
        </button>
        
        <button type="button" class="btn-secondary" @click="$emit('cancel')" :disabled="loading">
          Cancel
        </button>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { 
  useBuilds, 
  type BuildCreate, 
  type BuildUpdate, 
  type WarframeDetails,
  type WeaponDetails,
  type ModDetails,
  type ArcaneDetails,
  type EquippedMod,
  type WeaponBuild
} from '@/composables/useBuilds'

interface Props {
  build?: BuildCreate & { id?: string }
  isEditing?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isEditing: false
})

const emit = defineEmits<{
  submit: [build: BuildCreate | BuildUpdate]
  cancel: []
}>()

const { 
  loading, 
  error, 
  getAvailableWarframes, 
  getAvailableWeapons, 
  getAvailableMods, 
  getAvailableArcanes 
} = useBuilds()

// Form data
const formData = ref<BuildCreate>({
  name: '',
  warframe_uniqueName: '',
  warframe_mods: [],
  warframe_arcanes: [],
  primary_weapon: null,
  secondary_weapon: null,
  melee_weapon: null
})

// Available data from API
const warframes = ref<WarframeDetails[]>([])
const availableWeapons = ref<WeaponDetails[]>([])
const availableMods = ref<ModDetails[]>([])
const availableArcanes = ref<ArcaneDetails[]>([])

// Weapon slots configuration
const weaponSlots: Record<string, { label: string }> = {
  primary_weapon: { label: 'Primary Weapon' },
  secondary_weapon: { label: 'Secondary Weapon' },
  melee_weapon: { label: 'Melee Weapon' }
}

const isFormValid = computed(() => {
  return formData.value.name.trim() !== '' && formData.value.warframe_uniqueName !== ''
})

// Load all available data
const loadData = async () => {
  try {
    const [warframesData, weaponsData, modsData, arcanesData] = await Promise.all([
      getAvailableWarframes(),
      getAvailableWeapons(),
      getAvailableMods(),
      getAvailableArcanes()
    ])
    
    warframes.value = warframesData
    availableWeapons.value = weaponsData
    availableMods.value = modsData
    availableArcanes.value = arcanesData
  } catch (err) {
    console.error('Failed to load available data:', err)
  }
}

// Warframe mod management
const addWarframeMod = () => {
  if (formData.value.warframe_mods.length < 10) {
    formData.value.warframe_mods.push({ uniqueName: '', level: 0 })
  }
}

const removeWarframeMod = (index: number) => {
  formData.value.warframe_mods.splice(index, 1)
}

const updateModPolarity = (index: number, modUniqueName: string) => {
  // This could be used to update polarity display if needed
  console.log(`Updated mod ${index} to ${modUniqueName}`)
}

// Warframe arcane management
const addWarframeArcane = () => {
  if (formData.value.warframe_arcanes.length < 2) {
    formData.value.warframe_arcanes.push('')
  }
}

const removeWarframeArcane = (index: number) => {
  formData.value.warframe_arcanes.splice(index, 1)
}

// Weapon management
const initializeWeaponSlot = (weaponType: keyof typeof weaponSlots): WeaponBuild => {
  return {
    weapon_uniqueName: '',
    mods: [],
    arcane_uniqueName: undefined
  }
}

const clearWeaponMods = (weaponType: string) => {
  const typedWeaponType = weaponType as keyof typeof weaponSlots
  if (formData.value[typedWeaponType]) {
    formData.value[typedWeaponType].mods = []
    formData.value[typedWeaponType].arcane_uniqueName = undefined
  }
}

const addWeaponMod = (weaponType: string) => {
  const typedWeaponType = weaponType as keyof typeof weaponSlots
  const weapon = formData.value[typedWeaponType]
  if (weapon && weapon.mods.length < 9) {
    weapon.mods.push({ uniqueName: '', level: 0 })
  }
}

const removeWeaponMod = (weaponType: string, modIndex: number) => {
  const typedWeaponType = weaponType as keyof typeof weaponSlots
  const weapon = formData.value[typedWeaponType]
  if (weapon) {
    weapon.mods.splice(modIndex, 1)
  }
}

const handleSubmit = async () => {
  if (!isFormValid.value) return

  try {
    // Ensure weapon slots are properly initialized
    const submitData: BuildCreate | BuildUpdate = {
      ...formData.value,
      primary_weapon: formData.value.primary_weapon?.weapon_uniqueName ? formData.value.primary_weapon : null,
      secondary_weapon: formData.value.secondary_weapon?.weapon_uniqueName ? formData.value.secondary_weapon : null,
      melee_weapon: formData.value.melee_weapon?.weapon_uniqueName ? formData.value.melee_weapon : null
    }

    emit('submit', submitData)
  } catch (err) {
    console.error('Submit failed:', err)
  }
}

// Initialize form data when build prop changes
watch(() => props.build, (newBuild) => {
  if (newBuild) {
    formData.value = {
      name: newBuild.name,
      warframe_uniqueName: newBuild.warframe_uniqueName,
      warframe_mods: [...(newBuild.warframe_mods || [])],
      warframe_arcanes: [...(newBuild.warframe_arcanes || [])],
      primary_weapon: newBuild.primary_weapon ? { ...newBuild.primary_weapon } : null,
      secondary_weapon: newBuild.secondary_weapon ? { ...newBuild.secondary_weapon } : null,
      melee_weapon: newBuild.melee_weapon ? { ...newBuild.melee_weapon } : null
    }
  } else {
    formData.value = {
      name: '',
      warframe_uniqueName: '',
      warframe_mods: [],
      warframe_arcanes: [],
      primary_weapon: null,
      secondary_weapon: null,
      melee_weapon: null
    }
  }
}, { immediate: true })

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.build-form {
  background: #050b16;
  border: 1px solid #1b2a3a;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.build-form h3 {
  color: #38bdf8;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #1b2a3a;
}

.form-section h4 {
  color: #38bdf8;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.weapon-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(27, 42, 58, 0.3);
  border-radius: 4px;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  color: #c9e5ff;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.form-group input,
.form-group select {
  width: 100%;
  background: #08121f;
  border: 1px solid #1b2a3a;
  border-radius: 4px;
  padding: 0.75rem;
  color: #c9e5ff;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #38bdf8;
}

.form-group input:disabled,
.form-group select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.warframe-preview {
  background: #08121f;
  border: 1px solid #1b2a3a;
  border-radius: 4px;
  padding: 1rem;
  margin-top: 1rem;
}

.warframe-preview h4 {
  color: #38bdf8;
  margin-bottom: 0.5rem;
}

.warframe-description {
  color: #c9e5ff;
  opacity: 0.8;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.warframe-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  background: #0f172a;
  border-radius: 4px;
}

.stat-label {
  font-size: 0.7rem;
  color: #94a3b8;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-weight: bold;
  color: #38bdf8;
}

.abilities h5 {
  color: #38bdf8;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.ability-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.ability {
  background: #0f172a;
  border-left: 2px solid #38bdf8;
  padding: 0.5rem 0.75rem;
  border-radius: 0 4px 4px 0;
}

.ability h6 {
  color: #38bdf8;
  font-size: 0.8rem;
  margin-bottom: 0.25rem;
}

.ability p {
  color: #c9e5ff;
  font-size: 0.7rem;
  opacity: 0.8;
  margin: 0;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #38bdf8;
  color: #021019;
}

.btn-primary:hover:not(:disabled) {
  background: #0ea5e9;
}

.btn-secondary {
  background: #374151;
  color: #e5e7eb;
}

.btn-secondary:hover:not(:disabled) {
  background: #4b5563;
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mods-container,
.arcanes-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mod-slot,
.arcane-slot {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.mod-slot select,
.arcane-slot select {
  flex: 1;
  min-width: 200px;
}

.mod-slot input {
  width: 60px;
  text-align: center;
}

.btn-add,
.btn-remove {
  padding: 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-add {
  background: #10b981;
  color: white;
}

.btn-add:hover:not(:disabled) {
  background: #059669;
}

.btn-remove {
  background: #ef4444;
  color: white;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-remove:hover:not(:disabled) {
  background: #dc2626;
}

.btn-add:disabled,
.btn-remove:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.weapon-details {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(27, 42, 58, 0.2);
  border-radius: 4px;
  border-left: 3px solid #38bdf8;
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
</style>