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
  background: #08121f;
  border: 1px solid #1b2a3a;
  border-radius: 4px;
  padding: 0.75rem;
  color: #c9e5ff;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #38bdf8;
}

.search-input::placeholder {
  color: #64748b;
}

.selected-item-display {
  position: absolute;
  top: 50%;
  right: 0.75rem;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #38bdf8;
  color: #021019;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.clear-btn {
  background: none;
  border: none;
  color: #021019;
  cursor: pointer;
  font-size: 1rem;
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
  color: #dc2626;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #050b16;
  border: 1px solid #1b2a3a;
  border-radius: 4px;
  margin-top: 0.25rem;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.dropdown-item {
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #1b2a3a;
  transition: background-color 0.2s;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover,
.dropdown-item.highlighted {
  background: rgba(56, 189, 248, 0.1);
}

.option-name {
  color: #c9e5ff;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.option-details {
  display: flex;
  gap: 0.5rem;
  font-size: 0.8rem;
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
  background: #f59e0b;
  color: #021019;
}

.category {
  background: #8b5cf6;
  color: white;
}

.rarity {
  background: #10b981;
  color: white;
}

.type {
  background: #6366f1;
  color: white;
}

.no-results {
  padding: 1rem;
}

.no-results-text {
  color: #64748b;
  text-align: center;
  font-style: italic;
}

/* Scrollbar styling */
.dropdown::-webkit-scrollbar {
  width: 6px;
}

.dropdown::-webkit-scrollbar-track {
  background: #1b2a3a;
}

.dropdown::-webkit-scrollbar-thumb {
  background: #38bdf8;
  border-radius: 3px;
}

.dropdown::-webkit-scrollbar-thumb:hover {
  background: #0ea5e9;
}
</style>