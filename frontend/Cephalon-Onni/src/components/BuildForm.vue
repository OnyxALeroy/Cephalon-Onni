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
            class="form-input"
          />
        </div>

         <div class="form-group">
           <label for="warframe-select">Warframe</label>
           <SearchableSelect
             :options="warframes"
             placeholder="Search for a warframe..."
             v-model="formData.warframe_uniqueName"
           />
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
               <SearchableSelect
                 :options="availableMods"
                 placeholder="Search for mod..."
                 v-model="mod.uniqueName"
                 @update:modelValue="updateModPolarity(index, mod.uniqueName)"
               />
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
<SearchableSelect
                 :options="availableArcanes"
                 placeholder="Search for arcane..."
                 v-model="formData.warframe_arcanes[index]"
               />
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
              <SearchableSelect
                :options="availableWeapons"
                :placeholder="`Search for ${weapon.label.toLowerCase()}...`"
                :model-value="formData[weaponType as keyof typeof weaponSlots]?.weapon_uniqueName"
                @update:modelValue="(value) => setWeaponUniqueName(weaponType as keyof typeof weaponSlots, value)"
              />
            </div>

           <div v-if="formData[weaponType as keyof typeof weaponSlots]?.weapon_uniqueName" class="weapon-details">
            <div class="form-group">
              <label>{{ (weapon as any).label }} Mods (Max: 9)</label>
              <div class="mods-container">
                 <div 
                   v-for="(mod, index) in formData[weaponType as keyof typeof weaponSlots]?.mods || []" 
                   :key="index"
                   class="mod-slot"
                 >
                   <SearchableSelect
                     :options="availableMods"
                     placeholder="Search for mod..."
                     v-model="mod.uniqueName"
                   />
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
                  :disabled="loading || (formData[weaponType as keyof typeof weaponSlots]?.mods?.length || 0) >= 9"
                  class="btn-add"
                >
                  + Add Mod
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>{{ (weapon as any).label }} Arcane</label>
              <SearchableSelect
                :options="availableArcanes"
                placeholder="Search for arcane..."
                :model-value="formData[weaponType as keyof typeof weaponSlots]?.arcane_uniqueName"
                @update:modelValue="(value) => setWeaponArcane(weaponType as keyof typeof weaponSlots, value)"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="loading || !isFormValid">
          <span v-if="loading">Saving...</span>
          <span v-else>{{ isEditing ? 'Update' : 'Save' }} Build</span>
        </button>
        
        <button type="button" class="btn btn-secondary" @click="$emit('cancel')" :disabled="loading">
          Cancel
        </button>
      </div>

      <div v-if="error" class="message message-error">
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
 import SearchableSelect from './SearchableSelect.vue'

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
  // Only require name and warframe - weapons are optional and can be incomplete
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

const setWeaponUniqueName = (weaponType: keyof typeof weaponSlots, value: string) => {
  if (!formData.value[weaponType]) {
    formData.value[weaponType] = initializeWeaponSlot(weaponType)
  }
  formData.value[weaponType]!.weapon_uniqueName = value
  clearWeaponMods(weaponType)
}

const setWeaponArcane = (weaponType: keyof typeof weaponSlots, value: string | undefined) => {
  if (!formData.value[weaponType]) {
    formData.value[weaponType] = initializeWeaponSlot(weaponType)
  }
  formData.value[weaponType]!.arcane_uniqueName = value
}

const clearWeaponMods = (weaponType: string) => {
  const typedWeaponType = weaponType as keyof typeof weaponSlots
  if (formData.value[typedWeaponType]) {
    formData.value[typedWeaponType] = {
      weapon_uniqueName: formData.value[typedWeaponType]?.weapon_uniqueName || '',
      mods: [],
      arcane_uniqueName: undefined
    }
  }
}

const addWeaponMod = (weaponType: string) => {
  const typedWeaponType = weaponType as keyof typeof weaponSlots
  const weapon = formData.value[typedWeaponType]
  if (weapon && weapon.mods && weapon.mods.length < 9) {
    weapon.mods.push({ uniqueName: '', level: 0 })
  }
}

const removeWeaponMod = (weaponType: string, modIndex: number) => {
  const typedWeaponType = weaponType as keyof typeof weaponSlots
  const weapon = formData.value[typedWeaponType]
  if (weapon && weapon.mods) {
    weapon.mods.splice(modIndex, 1)
  }
}

const validateWeaponData = (weapon: WeaponBuild | null): boolean => {
  if (!weapon) return true; // null is valid for optional fields
  return weapon.weapon_uniqueName && weapon.weapon_uniqueName.trim() !== '';
}

const cleanWeaponData = (weapon: WeaponBuild | null): WeaponBuild | null => {
  if (!weapon || !weapon.weapon_uniqueName || weapon.weapon_uniqueName.trim() === '') {
    return null;
  }
  
  // Filter out empty mods
  const cleanedMods = weapon.mods.filter(mod => 
    mod.uniqueName && mod.uniqueName.trim() !== ''
  );
  
  return {
    weapon_uniqueName: weapon.weapon_uniqueName.trim(),
    mods: cleanedMods,
    arcane_uniqueName: weapon.arcane_uniqueName || undefined
  };
}

const handleSubmit = async () => {
  if (!isFormValid.value) return

  try {
    // Log data for debugging
    console.log('Submitting build data:', JSON.stringify(formData.value, null, 2))
    
    // Clean weapon data to remove empty mods and validate weapon names
    const submitData: BuildCreate | BuildUpdate = {
      ...formData.value,
      primary_weapon: cleanWeaponData(formData.value.primary_weapon),
      secondary_weapon: cleanWeaponData(formData.value.secondary_weapon),
      melee_weapon: cleanWeaponData(formData.value.melee_weapon)
    }

    // Log final submit data
    console.log('Final submit data:', JSON.stringify(submitData, null, 2))

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
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  margin-bottom: var(--space-8);
}

.build-form h3 {
  color: var(--accent);
  margin-bottom: var(--space-6);
  font-size: var(--text-2xl);
}

.form-section {
  margin-bottom: var(--space-8);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--border-primary);
}

.form-section h4 {
  color: var(--accent);
  margin-bottom: var(--space-4);
  font-size: var(--text-xl);
}

.weapon-section {
  margin-bottom: var(--space-6);
  padding: var(--space-4);
  background: rgba(27, 42, 58, 0.3);
  border-radius: var(--radius-sm);
}

.form-group {
  margin-bottom: var(--space-6);
}

.form-group label {
  display: block;
  color: var(--text-primary);
  margin-bottom: var(--space-2);
  font-size: var(--text-body);
  font-weight: 500;
}

.form-group select {
  width: 100%;
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  padding: var(--space-3);
  color: var(--text-primary);
  font-size: var(--text-normal);
  transition: border-color var(--transition-normal);
}

.form-group select:focus {
  outline: none;
  border-color: var(--accent);
}

.form-group select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.warframe-preview {
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
  margin-top: var(--space-4);
}

.warframe-preview h4 {
  color: var(--accent);
  margin-bottom: var(--space-2);
}

.warframe-description {
  color: var(--text-primary);
  opacity: 0.8;
  margin-bottom: var(--space-4);
  font-size: var(--text-body);
}

.warframe-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-2);
  background: var(--bg-elevated);
  border-radius: var(--radius-sm);
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--text-muted-2);
  margin-bottom: var(--space-1);
}

.stat-value {
  font-weight: bold;
  color: var(--accent);
}

.abilities h5 {
  color: var(--accent);
  margin-bottom: var(--space-2);
  font-size: var(--text-body);
}

.ability-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.ability {
  background: var(--bg-elevated);
  border-left: 2px solid var(--accent);
  padding: var(--space-2) var(--space-3);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.ability h6 {
  color: var(--accent);
  font-size: var(--text-base);
  margin-bottom: var(--space-1);
}

.ability p {
  color: var(--text-primary);
  font-size: var(--text-xs);
  opacity: 0.8;
  margin: 0;
}

.form-actions {
  display: flex;
  gap: var(--space-4);
  margin-top: var(--space-8);
}

.mods-container,
.arcanes-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.mod-slot,
.arcane-slot {
  display: flex;
  gap: var(--space-2);
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
  padding: var(--space-2);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-normal);
  font-size: var(--text-body);
}

.btn-add {
  background: var(--success-alt);
  color: var(--text-white);
}

.btn-add:hover:not(:disabled) {
  background: var(--success-alt-hover);
}

.btn-remove {
  background: var(--danger);
  color: var(--text-white);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-remove:hover:not(:disabled) {
  background: var(--danger-hover);
}

.btn-add:disabled,
.btn-remove:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.weapon-details {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background: rgba(27, 42, 58, 0.2);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--accent);
}
</style>