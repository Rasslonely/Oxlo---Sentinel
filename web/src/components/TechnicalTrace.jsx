import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Terminal, Cpu, Shield, Zap, Database } from 'lucide-react'

export default function TechnicalTrace({ isOpen, onClose, traceData }) {
  if (!traceData) return null

  const { agent_hypotheses, sandbox_logs, audit_reasoning, status_messages } = traceData

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div 
          className="trace-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div 
            className="trace-modal glass-card"
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 20 }}
          >
            <div className="trace-header">
              <div className="trace-title">
                <Terminal size={18} />
                <span>TECHNICAL AUDIT TRACE</span>
              </div>
              <button onClick={onClose} className="trace-close">
                <X size={18} />
              </button>
            </div>

            <div className="trace-body scrollbar-ghost">
              
              {/* --- Layer 1: Consistency Map --- */}
              <section className="trace-section">
                <div className="section-head">
                  <Cpu size={14} /> <span>LAYER 01: SKEPTIC CONSENSUS MAP</span>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-3">
                  {agent_hypotheses?.map((h, i) => (
                    <div key={i} className="hypothesis-card">
                      <div className="hyp-header">
                        <span className="hyp-name">{h.model_id}</span>
                        <span className="hyp-conf">{(h.confidence * 100).toFixed(0)}% CONF</span>
                      </div>
                      <div className="hyp-preview">
                        {h.content.substring(0, 120)}...
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* --- Layer 2: Mechanical Proof --- */}
              <section className="trace-section">
                <div className="section-head">
                  <Zap size={14} /> <span>LAYER 02: E2B SANDBOX (MECHANICAL TRUTH)</span>
                </div>
                <div className="terminal-shell mt-3">
                  <div className="terminal-header">
                    <span className="term-dot red" />
                    <span className="term-dot yellow" />
                    <span className="term-dot green" />
                    <span className="term-title">isolated_microvm_stdout</span>
                  </div>
                  <pre className="terminal-body">
                    {sandbox_logs || '> No sandbox execution required for this query.'}
                  </pre>
                </div>
              </section>

              {/* --- Layer 3: Auditor Reasoning --- */}
              <section className="trace-section">
                <div className="section-head">
                  <Shield size={14} /> <span>LAYER 03: DEEPSEEK-R1 AUDIT TRACE</span>
                </div>
                <div className="reasoning-bubble mt-3">
                  <div className="reasoning-meta">Consensus Evaluation: JSON_STRICT</div>
                  <p className="reasoning-text">{audit_reasoning || 'Aggregating cross-model hypotheses...'}</p>
                </div>
              </section>

              {/* --- Layer 4: Infrastructure State --- */}
              <section className="trace-section">
                <div className="section-head">
                  <Database size={14} /> <span>LAYER 04: INFRASTRUCTURE SIGNALS</span>
                </div>
                <div className="signal-logs mt-3">
                  {status_messages?.map((msg, i) => (
                    <div key={i} className="signal-row">
                      <span className="signal-time">[{new Date().toLocaleTimeString()}]</span>
                      <span className="signal-msg">{msg}</span>
                    </div>
                  ))}
                </div>
              </section>

            </div>

            <div className="trace-footer">
              <span className="footer-status">● SYSTEM STABLE</span>
              <span className="footer-tag">OXLO-SENTINEL ARCHIGENCE V1.4</span>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
