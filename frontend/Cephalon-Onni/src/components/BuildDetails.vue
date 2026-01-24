<template>
  <div class="build-details">
    <div class="details-header">
      <button @click="$emit('back')" class="btn-back">
        ← Back to Builds
      </button>
      
      <div class="header-actions">
        <button @click="$emit('edit-build', build)" class="btn-edit">
          ✏️ Edit
        </button>
        <button @click="handleDelete" class="btn-delete">
          🗑️ Delete
        </button>
      </div>
    </div>

    <div class="build-overview">
      <div class="build-title">
        <h2>{{ build.name }}</h2>
        <div class="build-meta">
          <span v-if="build.isLocal" class="badge-local">Local Build</span>
          <span class="build-dates">
            Created: {{ formatDate(build.created_at) }} • 
            Updated: {{ formatDate(build.updated_at) }}
          </span>
        </div>
      </div>
    </div>

    <div v-if="build.warframe" class="warframe-details">
      <div class="warframe-header">
        <h3>{{ build.warframe.name }}</h3>
        <span class="mastery-req">Mastery Rank {{ build.warframe.masteryReq }}</span>
      </div>

      <p class="warframe-description">{{ build.warframe.description }}</p>

      <div class="warframe-stats">
        <h4>Base Stats</h4>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">❤️</div>
            <div class="stat-info">
              <span class="stat-label">Health</span>
              <span class="stat-value">{{ build.warframe.health }}</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">🛡️</div>
            <div class="stat-info">
              <span class="stat-label">Shield</span>
              <span class="stat-value">{{ build.warframe.shield }}</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">⚔️</div>
            <div class="stat-info">
              <span class="stat-label">Armor</span>
              <span class="stat-value">{{ build.warframe.armor }}</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-info">
              <span class="stat-label">Power</span>
              <span class="stat-value">{{ build.warframe.power }}</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">🏃</div>
            <div class="stat-info">
              <span class="stat-label">Sprint Speed</span>
              <span class="stat-value">{{ build.warframe.sprintSpeed }}</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">🌟</div>
            <div class="stat-info">
              <span class="stat-label">Stamina</span>
              <span class="stat-value">{{ build.warframe.stamina }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="build.warframe.passiveDescription" class="passive-ability">
        <h4>Passive Ability</h4>
        <div class="passive-content">
          <p>{{ build.warframe.passiveDescription }}</p>
        </div>
      </div>

      <div v-if="build.warframe.abilities.length > 0" class="abilities-section">
        <h4>Abilities</h4>
        <div class="abilities-list">
          <div
            v-for="(ability, index) in build.warframe.abilities"
            :key="ability.abilityUniqueName"
            class="ability-card"
          >
            <div class="ability-header">
              <h5>{{ ability.abilityName }}</h5>
              <span class="ability-number">{{ index + 1 }}</span>
            </div>
            <p class="ability-description">{{ ability.description }}</p>
            <div class="ability-code">
              <small>{{ ability.abilityUniqueName }}</small>
            </div>
          </div>
        </div>
      </div>

      <div v-if="build.warframe.exalted && build.warframe.exalted.length > 0" class="exalted-section">
        <h4>Exalted Weapons</h4>
        <div class="exalted-list">
          <span
            v-for="weapon in build.warframe.exalted"
            :key="weapon"
            class="exalted-item"
          >
            {{ weapon }}
          </span>
        </div>
      </div>

      <div class="technical-details">
        <h4>Technical Details</h4>
        <div class="tech-grid">
          <div class="tech-item">
            <span class="tech-label">Unique Name:</span>
            <span class="tech-value">{{ build.warframe.uniqueName }}</span>
          </div>
          <div class="tech-item">
            <span class="tech-label">Product Category:</span>
            <span class="tech-value">{{ build.warframe.productCategory }}</span>
          </div>
          <div v-if="build.warframe.parentName" class="tech-item">
            <span class="tech-label">Parent:</span>
            <span class="tech-value">{{ build.warframe.parentName }}</span>
          </div>
          <div class="tech-item">
            <span class="tech-label">Codex Secret:</span>
            <span class="tech-value">{{ build.warframe.codexSecret ? 'Yes' : 'No' }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="no-warframe-data">
      <div class="warning-content">
        <h4>⚠️ Warframe Details Unavailable</h4>
        <p>The detailed information for this Warframe couldn't be loaded.</p>
        <p>This might happen if you're viewing a local build or if there's a connection issue.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useBuilds, type BuildPublic } from '@/composables/useBuilds'

interface Props {
  build: BuildPublic
}

const props = defineProps<Props>()

const emit = defineEmits<{
  back: []
  'edit-build': [build: BuildPublic]
}>()

const { deleteBuild } = useBuilds()

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleDelete = async () => {
  if (!confirm(`Are you sure you want to delete "${props.build.name}"? This action cannot be undone.`)) {
    return
  }

  try {
    await deleteBuild(props.build.id)
    emit('back')
  } catch (err) {
    console.error('Failed to delete build:', err)
  }
}
</script>

<style scoped>
.build-details {
  max-width: 1000px;
  margin: 0 auto;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.btn-back {
  background: #374151;
  color: #e5e7eb;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn-back:hover {
  background: #4b5563;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-edit,
.btn-delete {
  background: none;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn-edit {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.btn-edit:hover {
  background: rgba(34, 197, 94, 0.2);
}

.btn-delete {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.btn-delete:hover {
  background: rgba(239, 68, 68, 0.2);
}

.build-overview {
  background: #050b16;
  border: 1px solid #1b2a3a;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.build-title h2 {
  color: #e2e8f0;
  margin: 0 0 1rem 0;
  font-size: 2rem;
}

.build-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.badge-local {
  background: #f59e0b;
  color: #021019;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  width: fit-content;
}

.build-dates {
  color: #64748b;
  font-size: 0.85rem;
}

.warframe-details {
  background: #050b16;
  border: 1px solid #1b2a3a;
  border-radius: 8px;
  padding: 2rem;
}

.warframe-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.warframe-header h3 {
  color: #38bdf8;
  margin: 0;
  font-size: 1.5rem;
}

.mastery-req {
  background: #38bdf8;
  color: #021019;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
}

.warframe-description {
  color: #cbd5e1;
  line-height: 1.6;
  margin-bottom: 2rem;
  font-size: 1rem;
}

.warframe-stats {
  margin-bottom: 2rem;
}

.warframe-stats h4 {
  color: #e2e8f0;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: #08121f;
  border: 1px solid #1b2a3a;
  border-radius: 6px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stat-icon {
  font-size: 1.5rem;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.8rem;
  color: #64748b;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: bold;
  color: #e2e8f0;
}

.passive-ability {
  background: #08121f;
  border: 1px solid #1b2a3a;
  border-radius: 6px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.passive-ability h4 {
  color: #38bdf8;
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
}

.passive-content p {
  color: #cbd5e1;
  margin: 0;
  line-height: 1.5;
}

.abilities-section {
  margin-bottom: 2rem;
}

.abilities-section h4 {
  color: #e2e8f0;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.abilities-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ability-card {
  background: #08121f;
  border: 1px solid #1b2a3a;
  border-radius: 6px;
  padding: 1.5rem;
}

.ability-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.ability-header h5 {
  color: #38bdf8;
  margin: 0;
  font-size: 1.1rem;
}

.ability-number {
  background: #38bdf8;
  color: #021019;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
}

.ability-description {
  color: #cbd5e1;
  line-height: 1.5;
  margin-bottom: 0.75rem;
}

.ability-code {
  font-family: monospace;
  font-size: 0.75rem;
  color: #64748b;
  background: #0f172a;
  padding: 0.5rem;
  border-radius: 4px;
  word-break: break-all;
}

.exalted-section {
  margin-bottom: 2rem;
}

.exalted-section h4 {
  color: #e2e8f0;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.exalted-list {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.exalted-item {
  background: #08121f;
  border: 1px solid #1b2a3a;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  color: #38bdf8;
  font-size: 0.9rem;
}

.technical-details {
  background: #08121f;
  border: 1px solid #1b2a3a;
  border-radius: 6px;
  padding: 1.5rem;
}

.technical-details h4 {
  color: #e2e8f0;
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
}

.tech-grid {
  display: grid;
  gap: 0.75rem;
}

.tech-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #1b2a3a;
}

.tech-item:last-child {
  border-bottom: none;
}

.tech-label {
  color: #64748b;
  font-size: 0.9rem;
}

.tech-value {
  color: #cbd5e1;
  font-size: 0.9rem;
  font-family: monospace;
}

.no-warframe-data {
  background: #050b16;
  border: 1px solid #1b2a3a;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
}

.warning-content h4 {
  color: #f59e0b;
  margin-bottom: 1rem;
}

.warning-content p {
  color: #cbd5e1;
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .details-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .warframe-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }
  
  .build-overview,
  .warframe-details {
    padding: 1.5rem;
  }
}
</style>