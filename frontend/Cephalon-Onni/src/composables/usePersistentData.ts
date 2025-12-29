import { ref, watch } from 'vue'

// API Response Interfaces (matching Pydantic models)
export interface GraphNode {
  id?: string
  name: string
  type: string
  label: string
  properties: Record<string, any>
}

export interface NodeNeighbor {
  id: string
  name: string
  type: string
  properties: Record<string, any>
  relationship_type: string
  relationship_properties: Record<string, any>
  relationship_direction: string
}

export interface NodeSearchResponse {
  nodes: GraphNode[]
}

export interface GraphResponse {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface NodeNeighborsResponse {
  neighbors: NodeNeighbor[]
  count: number
}

// Define the data structure for persistence
interface GraphVisualizationData {
  searchName: string
  searchLabel: string
  selectedNode: GraphNode | null
  searchResults: GraphNode[]
  graphData: GraphResponse | null
}

export interface GraphEdge {
  id?: string
  from_node: string
  to_node: string
  relationship_type: string
  properties: Record<string, any>
}

interface GraphEditorData {
  newNode: Omit<GraphNode, 'id'>
  newNodeProperties: string
  newEdge: Omit<GraphEdge, 'id'>
  newEdgeProperties: string
}

interface PersistentData {
  visualization: GraphVisualizationData
  editor: GraphEditorData
}

const STORAGE_KEY = 'graphDatabaseData'

// Default values
const defaultVisualizationData: GraphVisualizationData = {
  searchName: '',
  searchLabel: '',
  selectedNode: null,
  searchResults: [],
  graphData: null
}

const defaultEditorData: GraphEditorData = {
  newNode: {
    name: '',
    type: '',
    label: '',
    properties: {}
  },
  newNodeProperties: '{}',
  newEdge: {
    from_node: '',
    to_node: '',
    relationship_type: 'DROPS',
    properties: {}
  },
  newEdgeProperties: '{}'
}

export function usePersistentData() {
  // Load data from localStorage on initialization
  const getStoredData = (): PersistentData => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored)
        return {
          visualization: { ...defaultVisualizationData, ...parsed.visualization },
          editor: { ...defaultEditorData, ...parsed.editor }
        }
      }
    } catch (error) {
      console.warn('Failed to parse stored graph data:', error)
    }
    return {
      visualization: { ...defaultVisualizationData },
      editor: { ...defaultEditorData }
    }
  }

  // Reactive state
  const storedData = ref<PersistentData>(getStoredData())

  // Save data to localStorage whenever it changes
  const saveData = () => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(storedData.value))
    } catch (error) {
      console.warn('Failed to save graph data:', error)
    }
  }

  // Watch for changes and auto-save
  watch(storedData, saveData, { deep: true })

  // Getters for specific data sections
  const getVisualizationData = () => storedData.value.visualization
  const getEditorData = () => storedData.value.editor

  // Setters for specific data sections
  const setVisualizationData = (data: Partial<GraphVisualizationData>) => {
    storedData.value.visualization = { ...storedData.value.visualization, ...data }
  }

  const setEditorData = (data: Partial<GraphEditorData>) => {
    storedData.value.editor = { ...storedData.value.editor, ...data }
  }

  // Clear all stored data
  const clearData = () => {
    storedData.value = {
      visualization: { ...defaultVisualizationData },
      editor: { ...defaultEditorData }
    }
  }

  // Clear specific sections
  const clearVisualizationData = () => {
    storedData.value.visualization = { ...defaultVisualizationData }
  }

  const clearEditorData = () => {
    storedData.value.editor = { ...defaultEditorData }
  }

  return {
    getVisualizationData,
    getEditorData,
    setVisualizationData,
    setEditorData,
    clearData,
    clearVisualizationData,
    clearEditorData
  }
}