import { useEffect, useCallback } from 'react';
import {
  ReactFlow,
  type Node,
  type Edge,
  addEdge,
  type OnConnect,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { GraphNode } from './GraphNode';

type NodeState = 'idle' | 'running' | 'complete' | 'error';

interface GraphNodeData {
  label: string;
  state: NodeState;
  latency?: number;
  model?: string;
  tier?: string;
}

interface RouterEvent {
  id: string;
  session_id: string;
  request_id: string;
  event_type: string;
  timestamp: string;
  data: Record<string, any>;
}

const nodeTypes = {
  graphNode: GraphNode,
};

const initialNodes: Node[] = [
  {
    id: 'bypass',
    type: 'graphNode',
    position: { x: 100, y: 100 },
    data: { label: 'BYPASS', state: 'idle' },
  },
  {
    id: 'classify',
    type: 'graphNode',
    position: { x: 300, y: 100 },
    data: { label: 'CLASSIFY', state: 'idle' },
  },
  {
    id: 'route',
    type: 'graphNode',
    position: { x: 500, y: 100 },
    data: { label: 'ROUTE', state: 'idle' },
  },
  {
    id: 'generate',
    type: 'graphNode',
    position: { x: 700, y: 100 },
    data: { label: 'GENERATE', state: 'idle' },
  },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: 'bypass', target: 'classify' },
  { id: 'e2-3', source: 'classify', target: 'route' },
  { id: 'e3-4', source: 'route', target: 'generate' },
];

interface LiveGraphProps {
  events: RouterEvent[];
  lastEvent: RouterEvent | null;
}

export const LiveGraph: React.FC<LiveGraphProps> = ({ lastEvent }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect: OnConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  useEffect(() => {
    if (!lastEvent) return;

    const updateNodeState = (nodeId: string, state: NodeState, data?: Partial<GraphNodeData>) => {
      setNodes((nds) =>
        nds.map((node) =>
          node.id === nodeId
            ? { ...node, data: { ...node.data, state, ...data } }
            : node
        )
      );
    };

    if (lastEvent.event_type === 'request_start') {
      setNodes((nds) =>
        nds.map((node) => ({
          ...node,
          data: { ...node.data, state: 'idle' as NodeState },
        }))
      );
    }

    switch (lastEvent.event_type) {
      case 'bypass_detected':
        updateNodeState('bypass', 'complete', { model: lastEvent.data.target_model });
        break;
      case 'classify_start':
        updateNodeState('classify', 'running');
        break;
      case 'classify_complete':
        updateNodeState('classify', 'complete', {
          tier: lastEvent.data.tier,
          latency: lastEvent.data.latency_ms,
        });
        break;
      case 'route_decision':
        updateNodeState('route', 'complete', {
          model: lastEvent.data.target_model,
          tier: lastEvent.data.tier,
        });
        break;
      case 'forward_start':
        updateNodeState('generate', 'running', { model: lastEvent.data.model });
        break;
      case 'forward_complete':
        updateNodeState('generate', 'complete', {
          model: lastEvent.data.model,
          latency: lastEvent.data.latency_ms,
        });
        break;
      case 'request_error':
        setNodes((nds) =>
          nds.map((node) =>
            node.data.state === 'running'
              ? { ...node, data: { ...node.data, state: 'error' as NodeState } }
              : node
          )
        );
        break;
    }
  }, [lastEvent, setNodes]);

  return (
    <div style={{ width: '100%', height: '400px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
};
