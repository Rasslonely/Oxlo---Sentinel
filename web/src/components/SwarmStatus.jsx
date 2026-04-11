import React from 'react'
import { Activity, CheckCircle, Cpu } from 'lucide-react'

export default function SwarmStatus({ status }) {
  const isActive = status !== 'Idle'
  return (
    <div className="swarm-status-bar glass-card">
      <div className="status-main">
        <Activity size={14} className={isActive ? 'pulsing' : ''} />
        <span>{status}</span>
      </div>
      <div className="model-indicators">
        {['DEEPSEEK', 'MISTRAL', 'LLAMA'].map(m => (
          <div key={m} className={`model-tag ${isActive ? 'active' : ''}`}>{m}</div>
        ))}
      </div>
      <div className="node-stats">
        <div className="stat"><Cpu size={11} /><span>8 Nodes</span></div>
        <div className="stat"><CheckCircle size={11} className="icon-green" /><span>Verifiable</span></div>
      </div>
    </div>
  )
}
