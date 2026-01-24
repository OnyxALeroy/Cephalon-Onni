<template>
  <div class="build-form">
    <h3>{{ isEditing ? 'Edit Build' : 'Create New Build' }}</h3>
    
    <form @submit.prevent="handleSubmit" class="form">
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

      <div v-if="selectedWarframe" class="warframe-preview">
        <h4>{{ selectedWarframe.name }}</h4>
        <p class="warframe-description">{{ selectedWarframe.description }}</p>
        
        <div class="warframe-stats">
          <div class="stat">
            <span class="stat-label">Health:</span>
            <span class="stat-value">{{ selectedWarframe.health }}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Shield:</span>
            <span class="stat-value">{{ selectedWarframe.shield }}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Armor:</span>
            <span class="stat-value">{{ selectedWarframe.armor }}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Power:</span>
            <span class="stat-value">{{ selectedWarframe.power }}</span>
          </div>
        </div>

        <div v-if="selectedWarframe.abilities && selectedWarframe.abilities.length > 0" class="abilities">
          <h5>Abilities:</h5>
          <div class="ability-list">
            <div
              v-for="ability in selectedWarframe.abilities"
              :key="ability.abilityUniqueName"
              class="ability"
            >
              <h6>{{ ability.abilityName }}</h6>
              <p>{{ ability.description }}</p>
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
import { useBuilds, type BuildCreate, type BuildUpdate, type WarframeDetails } from '@/composables/useBuilds'

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

const { loading, error, getAllWarframes } = useBuilds()

// Form data
const formData = ref<BuildCreate>({
  name: '',
  warframe_uniqueName: ''
})

// Warframes data (in real app, this would come from API)
const warframes = ref<WarframeDetails[]>([])

const selectedWarframe = computed(() => {
  if (!formData.value.warframe_uniqueName) return null
  
  // Find warframe with case-insensitive comparison
  const found = warframes.value.find(w => {
    if (!w || !w.uniqueName) return false
    return w.uniqueName.toString() === formData.value.warframe_uniqueName.toString()
  })
  
  return found || null
})

const isFormValid = computed(() => {
  return formData.value.name.trim() !== '' && formData.value.warframe_uniqueName !== ''
})

// Load warframes data
const loadWarframes = async () => {
  try {
    warframes.value = await getAllWarframes()
  } catch (err) {
    console.error('Failed to load warframes:', err)
  }
}

const handleSubmit = async () => {
  if (!isFormValid.value) return

  try {
    const submitData = props.isEditing 
      ? { name: formData.value.name, warframe_uniqueName: formData.value.warframe_uniqueName } as BuildUpdate
      : { ...formData.value } as BuildCreate

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
      warframe_uniqueName: newBuild.warframe_uniqueName
    }
  } else {
    formData.value = { name: '', warframe_uniqueName: '' }
  }
}, { immediate: true })

onMounted(() => {
  loadWarframes()
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