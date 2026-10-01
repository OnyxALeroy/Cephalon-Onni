<template>
  <div class="tab-panel">
    <h2>System Configuration</h2>

    <section class="config-section">
      <h3>Static catalog</h3>
      <p class="section-hint">
        Warframes, weapons, mods, missions and drop tables are imported from Warframe's public data.
        Change a source URL only if Warframe moves it. Leave a field empty to use the default.
      </p>

      <div v-if="loadingSettings" class="loading">Loading settings...</div>

      <form v-else class="sources-form" @submit.prevent="saveSources">
        <div v-for="source in sources" :key="source.key" class="field">
          <label :for="source.key">
            {{ labels[source.key] ?? source.key }}
            <span v-if="source.overridden" class="badge">custom</span>
          </label>
          <input
            :id="source.key"
            v-model="drafts[source.key]"
            type="url"
            class="text-input"
            :placeholder="source.defaultValue"
          />
          <small class="default-hint">Default: {{ source.defaultValue }}</small>
        </div>

        <div v-if="settingsError" class="error">{{ settingsError }}</div>
        <div v-if="settingsSaved" class="success">Settings saved.</div>

        <div class="actions">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? "Saving..." : "Save" }}
          </button>
          <button type="button" class="btn btn-secondary" :disabled="saving" @click="resetSources">
            Reset to defaults
          </button>
          <button type="button" class="btn btn-ghost" :disabled="checking" @click="checkSources">
            {{ checking ? "Checking sources..." : "Check sources" }}
          </button>
        </div>
      </form>

      <div v-if="checkError" class="error">{{ checkError }}</div>
      <div v-if="check" class="check-result">
        <p>
          Source check at {{ formatDate(check.checkedAt) }} ({{ Math.round(check.durationMs / 100) / 10 }} s):
          <strong :class="check.ok ? 'ok' : 'failed'">
            {{ check.ok ? "all sources OK" : "an import would fail" }}
          </strong>
        </p>
        <p v-if="check.error" class="error">{{ check.error }}</p>
        <p v-if="shrinkingTables.length" class="warning">
          {{ shrinkingTables.join(", ") }} would lose more than half of their rows: an import would be
          refused without Force.
        </p>

        <div v-if="check.ok" class="check-grid">
          <table>
            <thead>
              <tr><th>Export</th><th>Items</th></tr>
            </thead>
            <tbody>
              <tr v-for="(items, name) in check.exports" :key="name">
                <td>{{ name }}</td><td>{{ items }}</td>
              </tr>
            </tbody>
          </table>
          <table>
            <thead>
              <tr><th>Drop rows</th><th>Count</th></tr>
            </thead>
            <tbody>
              <tr v-for="(count, type) in check.dropsByType" :key="type">
                <td>{{ type }}</td><td>{{ count }}</td>
              </tr>
            </tbody>
          </table>
          <table>
            <thead>
              <tr><th>Table</th><th>Now</th><th>After import</th></tr>
            </thead>
            <tbody>
              <tr v-for="row in check.tables" :key="row.table" :class="{ shrinking: row.wouldShrinkBelowGuard }">
                <td>{{ row.table }}</td><td>{{ row.current }}</td><td>{{ row.incoming }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="config-section">
      <h3>Import</h3>
      <div class="actions">
        <button class="btn btn-primary" :disabled="status?.running || starting" @click="startImport">
          {{ status?.running ? "Import running..." : "Import now" }}
        </button>
        <label class="checkbox">
          <input v-model="force" type="checkbox" />
          Force
        </label>
      </div>
      <p v-if="force" class="warning">
        Force skips the safety check that stops an import when a table would lose more than half its rows.
        Use it only when you know the upstream data really shrank.
      </p>
      <div v-if="importError" class="error">{{ importError }}</div>

      <div v-if="status?.lastRun" class="last-run">
        <p>
          Last run ({{ status.lastRun.trigger }}{{ status.lastRun.force ? ", forced" : "" }}):
          <strong :class="status.lastRun.success ? 'ok' : 'failed'">
            {{ status.lastRun.success ? "succeeded" : "failed" }}
          </strong>
          at {{ formatDate(status.lastRun.finishedAt) }}
          ({{ duration(status.lastRun.startedAt, status.lastRun.finishedAt) }})
        </p>
        <p v-if="status.lastRun.error" class="error">{{ status.lastRun.error }}</p>

        <table v-if="status.lastRun.tables.length">
          <thead>
            <tr>
              <th>Table</th>
              <th>Inserted</th>
              <th>Updated</th>
              <th>Deleted</th>
              <th>Skipped</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in status.lastRun.tables" :key="row.table">
              <td>{{ row.table }}</td>
              <td>{{ row.inserted }}</td>
              <td>{{ row.updated }}</td>
              <td>{{ row.deleted }}</td>
              <td>{{ row.skipped }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else-if="status && !status.running" class="section-hint">No import has run since the backend started.</p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from "vue";

interface SourceSetting {
  key: string;
  value: string;
  defaultValue: string;
  overridden: boolean;
}

interface TableCounts {
  table: string;
  inserted: number;
  updated: number;
  deleted: number;
  skipped: number;
}

interface LastRun {
  trigger: string;
  force: boolean;
  startedAt: string;
  finishedAt: string;
  success: boolean;
  error?: string | null;
  tables: TableCounts[];
}

interface TablePreview {
  table: string;
  current: number;
  incoming: number;
  wouldShrinkBelowGuard: boolean;
}

interface SourceCheck {
  ok: boolean;
  error?: string | null;
  checkedAt: string;
  durationMs: number;
  urls: Record<string, string>;
  exports: Record<string, number>;
  dropsByType: Record<string, number>;
  tables: TablePreview[];
}

interface ImportStatus {
  running: boolean;
  lastRun?: LastRun | null;
}

const labels: Record<string, string> = {
  "catalog.export-index-url": "PublicExport index (LZMA)",
  "catalog.export-content-base-url": "PublicExport files base URL",
  "catalog.drop-tables-url": "Drop tables page",
};

// Keys the backend's UpdateSourcesRequest expects, per setting key.
const requestFields: Record<string, string> = {
  "catalog.export-index-url": "exportIndexUrl",
  "catalog.export-content-base-url": "exportContentBaseUrl",
  "catalog.drop-tables-url": "dropTablesUrl",
};

const sources = ref<SourceSetting[]>([]);
const drafts = reactive<Record<string, string>>({});
const loadingSettings = ref(true);
const saving = ref(false);
const settingsError = ref("");
const settingsSaved = ref(false);

const check = ref<SourceCheck | null>(null);
const checking = ref(false);
const checkError = ref("");
const shrinkingTables = computed(() =>
  (check.value?.tables ?? []).filter((t) => t.wouldShrinkBelowGuard).map((t) => t.table),
);

const status = ref<ImportStatus | null>(null);
const force = ref(false);
const starting = ref(false);
const importError = ref("");
let pollTimer: ReturnType<typeof setTimeout> | null = null;

const errorDetail = async (response: Response, fallback: string) => {
  const data = await response.json().catch(() => null);
  return (data && data.detail) || fallback;
};

const applySources = (list: SourceSetting[]) => {
  sources.value = list;
  for (const source of list) {
    drafts[source.key] = source.overridden ? source.value : "";
  }
};

const fetchSources = async () => {
  try {
    const response = await fetch("/api/admin/catalog/settings", { credentials: "include" });
    if (!response.ok) {
      throw new Error(await errorDetail(response, "Failed to load catalog settings"));
    }
    applySources(await response.json());
  } catch (err) {
    settingsError.value = err instanceof Error ? err.message : "An error occurred";
  } finally {
    loadingSettings.value = false;
  }
};

const putSources = async (body: Record<string, string | null>) => {
  saving.value = true;
  settingsError.value = "";
  settingsSaved.value = false;
  try {
    const response = await fetch("/api/admin/catalog/settings", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: "include",
    });
    if (!response.ok) {
      throw new Error(await errorDetail(response, "Failed to save catalog settings"));
    }
    applySources(await response.json());
    settingsSaved.value = true;
  } catch (err) {
    settingsError.value = err instanceof Error ? err.message : "Failed to save catalog settings";
  } finally {
    saving.value = false;
  }
};

const saveSources = () => {
  const body: Record<string, string | null> = {};
  for (const source of sources.value) {
    const field = requestFields[source.key];
    if (field) {
      body[field] = drafts[source.key]?.trim() || null;
    }
  }
  return putSources(body);
};

const resetSources = () => putSources({ exportIndexUrl: null, exportContentBaseUrl: null, dropTablesUrl: null });

// Dry run with the saved URLs: fetches and validates everything, writes nothing (~10 s).
const checkSources = async () => {
  checking.value = true;
  checkError.value = "";
  try {
    const response = await fetch("/api/admin/catalog/check", { method: "POST", credentials: "include" });
    if (!response.ok) {
      throw new Error(await errorDetail(response, "Failed to check the sources"));
    }
    check.value = await response.json();
  } catch (err) {
    checkError.value = err instanceof Error ? err.message : "Failed to check the sources";
  } finally {
    checking.value = false;
  }
};

const fetchStatus = async () => {
  try {
    const response = await fetch("/api/admin/catalog/status", { credentials: "include" });
    if (!response.ok) {
      throw new Error(await errorDetail(response, "Failed to load import status"));
    }
    status.value = await response.json();
  } catch (err) {
    importError.value = err instanceof Error ? err.message : "Failed to load import status";
  }
  schedulePoll();
};

// Poll every 3 s only while an import is running.
const schedulePoll = () => {
  if (pollTimer) {
    clearTimeout(pollTimer);
    pollTimer = null;
  }
  if (status.value?.running) {
    pollTimer = setTimeout(fetchStatus, 3000);
  }
};

const startImport = async () => {
  starting.value = true;
  importError.value = "";
  try {
    const response = await fetch(`/api/admin/catalog/import?force=${force.value}`, {
      method: "POST",
      credentials: "include",
    });
    if (!response.ok) {
      throw new Error(await errorDetail(response, "Failed to start the import"));
    }
    status.value = await response.json();
    force.value = false;
    schedulePoll();
  } catch (err) {
    importError.value = err instanceof Error ? err.message : "Failed to start the import";
  } finally {
    starting.value = false;
  }
};

const formatDate = (iso: string) => new Date(iso).toLocaleString();

const duration = (start: string, end: string) => {
  const seconds = Math.max(0, Math.round((new Date(end).getTime() - new Date(start).getTime()) / 1000));
  return seconds < 60 ? `${seconds} s` : `${Math.floor(seconds / 60)} min ${seconds % 60} s`;
};

onMounted(() => {
  fetchSources();
  fetchStatus();
});

onUnmounted(() => {
  if (pollTimer) {
    clearTimeout(pollTimer);
  }
});
</script>

<style scoped>
.tab-panel h2 {
  color: var(--accent-subtle);
  margin-bottom: var(--space-4);
}

.config-section {
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
}

.config-section h3 {
  color: var(--text-heading);
  margin-bottom: var(--space-2);
}

.section-hint {
  color: var(--text-muted);
  margin-bottom: var(--space-4);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  margin-bottom: var(--space-4);
}

.field label {
  color: var(--text-heading);
  font-size: var(--text-sm);
}

.badge {
  margin-left: var(--space-2);
  padding: 0 var(--space-2);
  border-radius: var(--radius-full);
  background: var(--warning-subtle);
  color: var(--warning-text);
  font-size: var(--text-xs);
}

.text-input {
  width: 100%;
  padding: var(--space-2) var(--space-4);
  background: var(--bg-elevated);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-heading);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

.text-input:focus {
  outline: none;
  border-color: var(--accent-hover);
}

.text-input::placeholder {
  color: var(--text-muted);
}

.default-hint {
  color: var(--text-muted);
  font-size: var(--text-xs);
  word-break: break-all;
}

.actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.checkbox {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-heading);
}

.loading,
.error,
.success,
.warning {
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  margin: var(--space-3) 0;
}

.error {
  color: var(--error-text);
  border-color: var(--error-text);
}

.success {
  color: var(--success);
  border-color: var(--success);
}

.warning {
  color: var(--warning-text);
  border-color: var(--warning);
  background: var(--warning-subtle);
}

.check-result {
  margin-top: var(--space-4);
}

.check-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-4);
  align-items: start;
}

tr.shrinking td {
  color: var(--warning-text);
  background: var(--warning-subtle);
}

.last-run {
  margin-top: var(--space-4);
}

.ok {
  color: var(--success);
}

.failed {
  color: var(--error-text);
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: var(--space-3);
}

th,
td {
  padding: var(--space-2) var(--space-3);
  text-align: left;
  border-bottom: 1px solid var(--border-primary);
}

th {
  color: var(--accent-subtle);
  font-size: var(--text-sm);
}

td {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}
</style>
