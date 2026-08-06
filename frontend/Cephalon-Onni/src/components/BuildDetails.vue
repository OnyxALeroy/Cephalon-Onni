<template>
  <div class="build-details">
    <div class="details-header">
      <button @click="$emit('back')" class="btn btn-secondary btn-sm">
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
  margin-bottom: var(--space-8);
  flex-wrap: wrap;
  gap: var(--space-4);
}

.header-actions {
  display: flex;
  gap: var(--space-2);
}

.btn-edit,
.btn-delete {
  background: none;
  border: none;
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--text-body);
  transition: background-color var(--transition-normal);
}

.btn-edit {
  background: var(--success-subtle);
  color: var(--success);
}

.btn-edit:hover {
  background: var(--success-subtle);
  filter: brightness(1.4);
}

.btn-delete {
  background: var(--danger-subtle);
  color: var(--danger);
}

.btn-delete:hover {
  background: var(--danger-subtle);
  filter: brightness(1.4);
}

.build-overview {
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  margin-bottom: var(--space-8);
}

.build-title h2 {
  color: var(--text-heading);
  margin: 0 0 var(--space-4) 0;
  font-size: var(--text-3xl);
}

.build-meta {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.build-dates {
  color: var(--text-muted);
  font-size: var(--text-md);
}

.warframe-details {
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
}

.warframe-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
  gap: var(--space-4);
}

.warframe-header h3 {
  color: var(--accent);
  margin: 0;
  font-size: var(--text-2xl);
}

.mastery-req {
  background: var(--accent);
  color: var(--text-on-accent);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  font-size: var(--text-body);
  font-weight: 500;
}

.warframe-description {
  color: var(--text-body);
  line-height: 1.6;
  margin-bottom: var(--space-8);
  font-size: var(--text-normal);
}

.warframe-stats {
  margin-bottom: var(--space-8);
}

.warframe-stats h4 {
  color: var(--text-heading);
  margin-bottom: var(--space-4);
  font-size: var(--text-xl);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--space-4);
}

.stat-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.stat-icon {
  font-size: var(--text-2xl);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: var(--text-base);
  color: var(--text-muted);
}

.stat-value {
  font-size: var(--text-lg);
  font-weight: bold;
  color: var(--text-heading);
}

.passive-ability {
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: var(--space-6);
  margin-bottom: var(--space-8);
}

.passive-ability h4 {
  color: var(--accent);
  margin: 0 0 var(--space-4) 0;
  font-size: var(--text-lg);
}

.passive-content p {
  color: var(--text-body);
  margin: 0;
  line-height: 1.5;
}

.abilities-section {
  margin-bottom: var(--space-8);
}

.abilities-section h4 {
  color: var(--text-heading);
  margin-bottom: var(--space-4);
  font-size: var(--text-xl);
}

.abilities-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.ability-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: var(--space-6);
}

.ability-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.ability-header h5 {
  color: var(--accent);
  margin: 0;
  font-size: var(--text-lg);
}

.ability-number {
  background: var(--accent);
  color: var(--text-on-accent);
  width: 24px;
  height: 24px;
  border-radius: var(--radius-round);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-base);
  font-weight: bold;
}

.ability-description {
  color: var(--text-body);
  line-height: 1.5;
  margin-bottom: var(--space-3);
}

.ability-code {
  font-family: monospace;
  font-size: var(--text-sm);
  color: var(--text-muted);
  background: var(--bg-elevated);
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  word-break: break-all;
}

.exalted-section {
  margin-bottom: var(--space-8);
}

.exalted-section h4 {
  color: var(--text-heading);
  margin-bottom: var(--space-4);
  font-size: var(--text-xl);
}

.exalted-list {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.exalted-item {
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  color: var(--accent);
  font-size: var(--text-body);
}

.technical-details {
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: var(--space-6);
}

.technical-details h4 {
  color: var(--text-heading);
  margin: 0 0 var(--space-4) 0;
  font-size: var(--text-lg);
}

.tech-grid {
  display: grid;
  gap: var(--space-3);
}

.tech-item {
  display: flex;
  justify-content: space-between;
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--border-primary);
}

.tech-item:last-child {
  border-bottom: none;
}

.tech-label {
  color: var(--text-muted);
  font-size: var(--text-body);
}

.tech-value {
  color: var(--text-body);
  font-size: var(--text-body);
  font-family: monospace;
}

.no-warframe-data {
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  text-align: center;
}

.warning-content h4 {
  color: var(--warning);
  margin-bottom: var(--space-4);
}

.warning-content p {
  color: var(--text-body);
  margin-bottom: var(--space-2);
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
    padding: var(--space-6);
  }
}
</style>