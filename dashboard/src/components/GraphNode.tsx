import React from 'react';
import { Handle, Position } from '@xyflow/react';

type NodeState = 'idle' | 'running' | 'complete' | 'error';

interface GraphNodeData {
  label: string;
  state: NodeState;
  latency?: number;
  model?: string;
  tier?: string;
}

interface NodeProps {
  data: GraphNodeData;
}

export const GraphNode: React.FC<NodeProps> = ({ data }) => {
  const getNodeColor = () => {
    switch (data.state) {
      case 'idle': return '#e5e7eb';
      case 'running': return '#fbbf24';
      case 'complete': return '#10b981';
      case 'error': return '#ef4444';
      default: return '#e5e7eb';
    }
  };

  const getTextColor = () => {
    return data.state === 'idle' ? '#6b7280' : '#ffffff';
  };

  return (
    <div
      style={{
        padding: '12px 16px',
        borderRadius: '8px',
        backgroundColor: getNodeColor(),
        color: getTextColor(),
        border: '2px solid #d1d5db',
        minWidth: '120px',
        textAlign: 'center',
        fontSize: '14px',
        fontWeight: 'bold',
        transition: 'all 0.3s ease',
      }}
    >
      <Handle type="target" position={Position.Left} />
      
      <div>{data.label}</div>
      
      {data.tier && (
        <div style={{ fontSize: '10px', marginTop: '4px' }}>
          {data.tier.toUpperCase()}
        </div>
      )}
      
      {data.model && (
        <div style={{ fontSize: '10px', marginTop: '2px' }}>
          {data.model}
        </div>
      )}
      
      {data.latency && (
        <div style={{ fontSize: '10px', marginTop: '2px' }}>
          {Math.round(data.latency)}ms
        </div>
      )}
      
      <Handle type="source" position={Position.Right} />
    </div>
  );
};