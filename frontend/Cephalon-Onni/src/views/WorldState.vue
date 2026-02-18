<template>
  <div class="worldstate-view">
    <h1>World State</h1>

    <div v-if="loading" class="status-msg">Loading worldstate data...</div>

    <div v-else-if="error" class="status-msg error">{{ error }}</div>

    <div v-else-if="worldstate" class="worldstate-data">
      <div class="meta-bar">
        <span><strong>Seed:</strong> {{ worldstate.world_seed }}</span>
        <span><strong>API:</strong> v{{ worldstate.api_version }}</span>
        <span><strong>Build:</strong> {{ worldstate.build_label }}</span>
      </div>

      <details v-for="(section, idx) in sections" :key="idx" class="section">
        <summary>{{ section.label }} ({{ section.count }})</summary>
        <pre>{{ JSON.stringify(section.data, null, 2) }}</pre>
      </details>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Message {
  LanguageCode: string
  Message: string
}

interface Link {
  LanguageCode: string
  Link: string
}

interface MissionRewardItem {
  item_type: string
  item_count: number
}

interface MissionInfo {
  location: string
  mission_type: string
  faction: string
  difficulty: number
  mission_reward: Record<string, unknown>
  level_override: string
  enemy_spec: string
  min_enemy_level: number
  max_enemy_level: number
  desc_text: string
  max_wave_num: number
}

interface Event {
  messages: Message[]
  is_mobile_only: boolean
  priority: boolean
  prop: string
  community: boolean
  icon: string
  image_url: string
  date: string | null
  start_date: string | null
  end_date: string | null
  live_url: string
  do_hide_end_date_modifier: boolean
  links: Link[]
}

interface Alert {
  activation: string
  expiry: string
  mission_info: MissionInfo
  tag: string
  force_unlock: boolean
}

interface OpenWorldMission {
  type: string
  mastery_required: number
  max_enemy_level: number
  min_enemy_level: number
  rewards_table: string
  xp_amounts: number[]
}

interface SyndicateMission {
  activation: string
  expiry: string
  syndicate_tag: string
  nodes: string[]
  open_world_missions: OpenWorldMission[] | null
}

interface VoidFissure {
  activation: string
  expiry: string
  mission_type: string
  node: string
  region: number
  seed: number
  era: string
}

interface SortieMission {
  type: string
  modifier: string
  mission: string
  tileset: string
}

interface Sortie {
  activation: string
  expiry: string
  boss: string
  reward: string
  extra_drops: unknown[]
  seed: number
  missions: SortieMission[]
}

interface VoidTrader {
  activation: string
  expiry: string
  node: string
  character: string
}

interface PrimeResurgenceItem {
  item_type: string
  price: number
}

interface PrimeResurgenceScheduleInfo {
  expiry: string
  featured_item: string
  preview_hidden_until: string
}

interface PrimeResurgence {
  activation: string
  expiry: string
  node: string
  initial_start_date: string
  manifest: PrimeResurgenceItem[]
  evergreen_manifest: PrimeResurgenceItem[]
  schedule_info: PrimeResurgenceScheduleInfo[]
}

interface DailyDeal {
  activation: string
  expiry: string
  original_price: number
  sale_price: number
  item: string
  sold_amount: number
  total_amount: number
}

interface ConclaveChallenge {
  activation: string
  expiry: string
  category: string
  pvp_mode: string
  challenge_type_id: string
  challenge_sub_challenges: string[]
}

interface FeaturedDojo {
  alliance_id: string
  has_emblem: boolean
  platforms: Record<string, boolean>
  icon_override: number
  name: string
  tier: number
}

interface MissionChallenge {
  activation: string
  challenge: string
  daily: boolean
  expiry: string
}

interface SeasonInfo {
  activation: string
  expiry: string
  affiliation_tag: string
  parameters: string
  phase: number
  season: number
  active_challenges: MissionChallenge[]
}

interface WorldState {
  world_seed: string
  api_version: number
  mobile_version: string
  build_label: string
  current_event: Event | null
  current_alerts: Alert[]
  sortie: Sortie
  syndicate_missions: SyndicateMission[]
  void_fissures: VoidFissure[]
  global_boosts: string[]
  void_traders: VoidTrader[]
  prime_resurgence: PrimeResurgence | null
  prime_token_availability: boolean
  daily_deals: DailyDeal[]
  pvp_alternative_modes: ConclaveChallenge[]
  invasion_construction_statuses: [number, number]
  feature_dojos: FeaturedDojo[]
  season_info: SeasonInfo
}

const worldstate = ref<WorldState | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const sections = computed(() => {
  if (!worldstate.value) return []
  const ws = worldstate.value
  return [
    { label: 'Event', data: ws.current_event, count: ws.current_event ? 1 : 0 },
    { label: 'Alerts', data: ws.current_alerts, count: ws.current_alerts.length },
    { label: 'Sortie', data: ws.sortie, count: ws.sortie.missions.length },
    { label: 'Syndicate Missions', data: ws.syndicate_missions, count: ws.syndicate_missions.length },
    { label: 'Void Fissures', data: ws.void_fissures, count: ws.void_fissures.length },
    { label: 'Global Boosts', data: ws.global_boosts, count: ws.global_boosts.length },
    { label: 'Void Traders', data: ws.void_traders, count: ws.void_traders.length },
    { label: 'Prime Resurgence', data: ws.prime_resurgence, count: ws.prime_resurgence?.manifest.length ?? 0 },
    { label: 'Daily Deals', data: ws.daily_deals, count: ws.daily_deals.length },
    { label: 'PvP Challenges', data: ws.pvp_alternative_modes, count: ws.pvp_alternative_modes.length },
    { label: 'Invasion Construction', data: ws.invasion_construction_statuses, count: 2 },
    { label: 'Featured Dojos', data: ws.feature_dojos, count: ws.feature_dojos.length },
    { label: 'Season Info', data: ws.season_info, count: ws.season_info.active_challenges.length },
  ]
})

onMounted(async () => {
  try {
    const response = await fetch('/api/worldstate')
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    worldstate.value = await response.json()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to fetch worldstate'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.worldstate-view h1 {
  color: #7dd3fc;
  letter-spacing: 2px;
  margin-bottom: 1.5rem;
}

.status-msg {
  padding: 1.5rem;
  text-align: center;
  font-size: 1rem;
  opacity: 0.7;
}

.status-msg.error {
  color: #f87171;
  opacity: 1;
}

.meta-bar {
  display: flex;
  gap: 2rem;
  background: #08121f;
  border: 1px solid #1b2a3a;
  padding: 0.8rem 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.85rem;
}

.section {
  margin-bottom: 0.5rem;
  border: 1px solid #1b2a3a;
  border-radius: 4px;
  background: #08121f;
}

.section summary {
  padding: 0.7rem 1rem;
  cursor: pointer;
  font-weight: 600;
  color: #7dd3fc;
  user-select: none;
  transition: 0.15s;
}

.section summary:hover {
  color: #38bdf8;
  background: #0a1929;
}

.section pre {
  margin: 0;
  padding: 1rem;
  background: #050b16;
  color: #c9e5ff;
  font-size: 0.75rem;
  overflow-x: auto;
  max-height: 500px;
  overflow-y: auto;
  border-top: 1px solid #1b2a3a;
}
</style>
