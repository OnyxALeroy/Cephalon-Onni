import { ref } from 'vue';
import { GraphNode, NodeSearchResponse, NodeNeighborsResponse, GraphEdge, GraphResponse } from './usePersistentData';

// Graph API composable for managing graph-related API calls
export function useGraphApi() {
  const searchResults = ref<GraphNode[]>([]);
  const graphStats = ref({
    totalNodes: 0,
    totalEdges: 0,
    nodeTypes: {},
    lastUpdated: new Date().toISOString()
  });

  // Search graph
  async function searchGraph(query: string, type: string = 'all') {
    if (!query.trim()) return { success: false };
    
    try {
      const response = await fetch("/api/admin/graph/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, type })
      });
      
      if (response.ok) {
        searchResults.value = await response.json();
        return { success: true };
      } else {
        console.error("Search failed");
        return { success: false };
      }
    } catch (error) {
      console.error("Search error:", error);
      return { success: false };
    }
  }

  // Execute Cypher query
  async function executeCypherQuery(query: string) {
    if (!query.trim()) return { success: false };
    
    try {
      const response = await fetch("/api/admin/graph/cypher", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      });
      
      if (response.ok) {
        const result = await response.json();
        searchResults.value = result.results || [];
        return { success: true };
      } else {
        console.error("Query failed");
        return { success: false };
      }
    } catch (error) {
      console.error("Query error:", error);
      return { success: false };
    }
  }

  // Update graph statistics
  async function updateGraphStats() {
    try {
      const response = await fetch("/api/admin/graph/stats");
      if (response.ok) {
        graphStats.value = await response.json();
        return { success: true };
      }
    } catch (error) {
      console.error("Stats error:", error);
      return { success: false };
    }
  }

  // Search nodes by name and/or label
  async function searchNodes(name: string = "", label: string = ""): Promise<{ success: boolean; data?: NodeSearchResponse; error?: string }> {
    try {
      const requestBody: any = { query: name || "", type: "all" };
      
      console.log(`Searching nodes with body:`, requestBody);
      const response = await fetch("/api/admin/graph/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody)
      });
      console.log('Search response status:', response.status);
      
      if (response.ok) {
        const data: NodeSearchResponse = await response.json();
        console.log('Search response data:', data);
        return { success: true, data };
      } else {
        const errorText = await response.text();
        console.error('Search response error:', response.status, errorText);
        return { success: false, error: errorText };
      }
    } catch (error) {
      console.error("Node search error:", error);
      return { success: false, error: error instanceof Error ? error.message : String(error) };
    }
  }

  // Load node neighbors using name and/or label (depth is hardcoded in backend)
  async function loadNodeNeighbors(name: string = "", label: string = ""): Promise<{ success: boolean; data?: GraphResponse; error?: string }> {
    try {
      const params = new URLSearchParams();
      if (name) params.append('name', name);
      if (label) params.append('label', label);
      
      console.log(`Loading neighbors with params: ${params.toString()}`);
      const response = await fetch(`/api/admin/graph/neighbors?${params}`);
      console.log('Neighbors response status:', response.status);
      
      if (response.ok) {
        const data: GraphResponse = await response.json();
        console.log('Neighbors response data:', data);
        return { success: true, data };
      } else {
        const errorText = await response.text();
        console.error('Neighbors response error:', response.status, errorText);
        return { success: false, error: errorText };
      }
    } catch (error) {
      console.error("Node neighbors load error:", error);
      return { success: false, error: error instanceof Error ? error.message : String(error) };
    }
  }

  // Create new node
  async function createNewNode(nodeData: Omit<GraphNode, 'id'>) {
    try {
      const response = await fetch("/api/admin/graph/nodes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(nodeData)
      });
      
      if (response.ok) {
        return { success: true };
      } else {
        console.error("Create node failed");
        return { success: false };
      }
    } catch (error) {
      console.error("Create node error:", error);
      return { success: false };
    }
  }

  // Create new edge
  async function createNewEdge(edgeData: Omit<GraphEdge, 'id'>) {
    try {
      const response = await fetch("/api/admin/graph/edges", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(edgeData)
      });
      
      if (response.ok) {
        return { success: true };
      } else {
        console.error("Create edge failed");
        return { success: false };
      }
    } catch (error) {
      console.error("Create edge error:", error);
      return { success: false };
    }
  }

  // Update node
  async function updateNode(nodeId: string, nodeData: Omit<GraphNode, 'id'>) {
    try {
      const response = await fetch(`/api/admin/graph/nodes/${nodeId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(nodeData)
      });
      
      if (response.ok) {
        return { success: true };
      } else {
        console.error("Update node failed");
        return { success: false };
      }
    } catch (error) {
      console.error("Update node error:", error);
      return { success: false };
    }
  }

  // Delete node
  async function deleteNode(nodeId: string) {
    try {
      const response = await fetch(`/api/admin/graph/nodes/${nodeId}`, {
        method: "DELETE"
      });
      
      if (response.ok) {
        return { success: true };
      } else {
        console.error("Delete node failed");
        return { success: false };
      }
    } catch (error) {
      console.error("Delete node error:", error);
      return { success: false };
    }
  }

  // Clear results
  function clearResults() {
    searchResults.value = [];
  }

  return {
    searchResults,
    graphStats,
    searchGraph,
    executeCypherQuery,
    updateGraphStats,
    searchNodes,
    loadNodeNeighbors,
    createNewNode,
    createNewEdge,
    updateNode,
    deleteNode,
    clearResults
  };
}