// Event types for WebSocket communication
export interface RouterEvent {
  id: string;
  session_id: string;
  request_id: string;
  event_type: string;
  timestamp: string;
  data: Record<string, any>;
}

// Node states for the live graph
export type NodeState = 'idle' | 'running' | 'complete' | 'error';

// Graph node data
export interface GraphNodeData {
  label: string;
  state: NodeState;
  latency?: number;
  model?: string;
  tier?: string;
}

// Stats from the router
export interface RouterStats {
  total_requests: number;
  requests_today: number;
  cost_today_usd: number;
  tier_distribution: Record<string, number>;
}