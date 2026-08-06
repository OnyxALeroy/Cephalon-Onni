<template>
  <div class="searchable-select">
    <div class="search-input-container">
      <input
        ref="searchInput"
        v-model="searchQuery"
        type="text"
        :placeholder="placeholder"
        class="search-input"
        @focus="showDropdown = true"
        @input="filterOptions"
        @keydown.down="highlightNext"
        @keydown.up="highlightPrevious"
        @keydown.enter="selectHighlighted"
        @keydown.esc="showDropdown = false"
      />
      <div v-if="selectedItem" class="selected-item-display">
        {{ selectedItem.name }}
        <button type="button" @click="clearSelection" class="clear-btn">×</button>
      </div>
    </div>
    
    <div v-if="showDropdown && filteredOptions.length > 0" class="dropdown">
      <div
        v-for="(option, index) in filteredOptions"
        :key="option.uniqueName"
        :class="['dropdown-item', { highlighted: index === highlightedIndex }]"
        @click="selectOption(option)"
      >
        <div class="option-name">{{ option.name }}</div>
        <div class="option-details">
          <span v-if="option.masteryReq" class="mastery-req">MR {{ option.masteryReq }}</span>
          <span v-if="option.productCategory" class="category">{{ option.productCategory }}</span>
          <span v-if="option.rarity" class="rarity">{{ option.rarity }}</span>
          <span v-if="option.type" class="type">{{ option.type }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="showDropdown && searchQuery && filteredOptions.length === 0" class="dropdown no-results">
      <div class="no-results-text">No results found</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'

// Generic type for items with uniqueName and name
interface SearchableItem {
  uniqueName: string
  name: string
  masteryReq?: number
  productCategory?: string
  rarity?: string
  type?: string
}

interface Props {
  options: SearchableItem[]
  placeholder?: string
  modelValue?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Search...',
  modelValue: null
})

const emit = defineEmits<{
  'update:modelValue': [value: string | null]
  'select': [item: SearchableItem]
}>()

const searchQuery = ref('')
const showDropdown = ref(false)
const highlightedIndex = ref(-1)
const searchInput = ref<HTMLInputElement>()

const selectedItem = computed(() => {
  if (!props.modelValue) return null
  return props.options.find(option => option.uniqueName === props.modelValue) || null
})

const filteredOptions = ref<SearchableItem[]>([])

const filterOptions = () => {
  if (!searchQuery.value.trim()) {
    filteredOptions.value = [...props.options]
  } else {
    const query = searchQuery.value.toLowerCase()
    filteredOptions.value = props.options.filter(option =>
      option.name.toLowerCase().includes(query) ||
      option.uniqueName.toLowerCase().includes(query)
    )
  }
  highlightedIndex.value = -1
}

const selectOption = (option: SearchableItem) => {
  emit('update:modelValue', option.uniqueName)
  emit('select', option)
  searchQuery.value = ''
  showDropdown.value = false
  searchInput.value?.blur()
}

const clearSelection = () => {
  emit('update:modelValue', null)
  searchQuery.value = ''
  showDropdown.value = false
}

const highlightNext = () => {
  if (highlightedIndex.value < filteredOptions.value.length - 1) {
    highlightedIndex.value++
  }
}

const highlightPrevious = () => {
  if (highlightedIndex.value > 0) {
    highlightedIndex.value--
  }
}

const selectHighlighted = () => {
  if (highlightedIndex.value >= 0 && filteredOptions.value[highlightedIndex.value]) {
    selectOption(filteredOptions.value[highlightedIndex.value])
  }
}

// Close dropdown when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.searchable-select')) {
    showDropdown.value = false
  }
}

// Watch for model changes to update display
watch(() => props.modelValue, (newValue) => {
  if (!newValue) {
    searchQuery.value = ''
  }
})

// Watch for options changes to update filtered list
watch(() => props.options, () => {
  filterOptions()
}, { immediate: true })

// Initialize filtered options
filterOptions()

// Add click outside listener
if (typeof document !== 'undefined') {
  document.addEventListener('click', handleClickOutside)
}
</script>

<style scoped>
.searchable-select {
  position: relative;
  width: 100%;
}

.search-input-container {
  position: relative;
}

.search-input {
  width: 100%;
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  padding: var(--space-3);
  color: var(--text-primary);
  font-size: var(--text-normal);
  transition: border-color var(--transition-normal);
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.selected-item-display {
  position: absolute;
  top: 50%;
  right: var(--space-3);
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background: var(--accent);
  color: var(--text-on-accent);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-base);
  font-weight: 500;
}

.clear-btn {
  background: none;
  border: none;
  color: var(--text-on-accent);
  cursor: pointer;
  font-size: var(--text-normal);
  font-weight: bold;
  padding: 0;
  margin: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-btn:hover {
  color: var(--danger-hover);
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  margin-top: var(--space-1);
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: var(--shadow-sm);
}

.dropdown-item {
  padding: var(--space-3);
  cursor: pointer;
  border-bottom: 1px solid var(--border-primary);
  transition: background-color var(--transition-normal);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover,
.dropdown-item.highlighted {
  background: rgba(var(--accent-rgb), 0.1);
}

.option-name {
  color: var(--text-primary);
  font-weight: 500;
  margin-bottom: var(--space-1);
}

.option-details {
  display: flex;
  gap: var(--space-2);
  font-size: var(--text-base);
}

.mastery-req,
.category,
.rarity,
.type {
  padding: 0.125rem 0.375rem;
  border-radius: 2px;
  font-weight: 500;
}

.mastery-req {
  background: var(--warning);
  color: var(--text-on-accent);
}

.category {
  background: var(--purple-alt);
  color: var(--text-white);
}

.rarity {
  background: var(--success-alt);
  color: var(--text-white);
}

.type {
  background: var(--indigo);
  color: var(--text-white);
}

.no-results {
  padding: var(--space-4);
}

.no-results-text {
  color: var(--text-muted);
  text-align: center;
  font-style: italic;
}

.dropdown::-webkit-scrollbar {
  width: 6px;
}

.dropdown::-webkit-scrollbar-track {
  background: var(--border-primary);
}

.dropdown::-webkit-scrollbar-thumb {
  background: var(--accent);
  border-radius: 3px;
}

.dropdown::-webkit-scrollbar-thumb:hover {
  background: var(--accent-hover);
}
</style>