import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, Send, Sparkles, Cpu, Zap, Terminal } from 'lucide-react'
import SwarmStatus from '../components/SwarmStatus'
import TechnicalTrace from '../components/TechnicalTrace'

const SUGGESTIONS = [
  { icon: '🔢', label: 'Prove Primality', q: 'Is 127 prime? Write Python to verify every divisor.' },
  { icon: '🎲', label: 'Monty Hall', q: 'Simulate 100,000 Monty Hall games. What is the empirical win rate for switching?' },
  { icon: '⚡', label: 'Float Audit', q: 'In IEEE 754 floating point, is (0.1 + 0.2 == 0.3)? Why or why not?' },
  { icon: '🔮', label: 'Collatz Check', q: 'Verify the Collatz conjecture holds for all integers 1–10,000 via Python.' },
]

function ParticleField() {
  return (
    <div className="particle-field" aria-hidden>
      {Array.from({ length: 18 }).map((_, i) => (
        <motion.div
          key={i}
          className="particle"
          style={{ left: `${5 + i * 5.2}%`, top: `${10 + (i * 37) % 80}%` }}
          animate={{ y: [-8, 8, -8], opacity: [0.15, 0.45, 0.15] }}
          transition={{ duration: 4 + (i % 4), repeat: Infinity, delay: i * 0.3, ease: 'easeInOut' }}
        />
      ))}
    </div>
  )
}

export default function ChatPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [status, setStatus] = useState('Idle')
  const [isTyping, setIsTyping] = useState(false)
  
  // Trace State
  const [isTraceOpen, setIsTraceOpen] = useState(false)
  const [activeTrace, setActiveTrace] = useState(null)

  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, isTyping])

  const openTrace = (data) => {
    setActiveTrace(data)
    setIsTraceOpen(true)
  }

  const send = async (query) => {
    if (!query.trim() || status !== 'Idle') return
    setMessages(p => [...p, { role: 'user', content: query }])
    setInput('')
    setIsTyping(true)
    setStatus('Routing...')
    try {
      const apiBase = import.meta.env.VITE_API_URL || '/api'
      const res = await fetch(`${apiBase}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query }),
      })

      if (!res.ok) {
        throw new Error(`Server responded with ${res.status}: ${res.statusText}`)
      }

      const reader = res.body.getReader()
      const dec = new TextDecoder()
      let buf = ''
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buf += dec.decode(value, { stream: true })
        const lines = buf.split('\n'); buf = lines.pop()
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const d = JSON.parse(line.slice(6))
            if (d.type === 'status') setStatus(d.content)
            else if (d.type === 'final') {
              const payload = d.data || {}
              const assistantContent = payload.messages?.at(-1)?.content ?? '(empty)'
              
              setMessages(p => [...p, { 
                role: 'assistant', 
                content: assistantContent,
                metadata: {
                  agent_hypotheses: payload.agent_hypotheses,
                  sandbox_logs: payload.sandbox_logs,
                  audit_reasoning: payload.audit_reasoning,
                  status_messages: payload.status_messages
                }
              }])
              setIsTyping(false); setStatus('Idle')
            } else if (d.type === 'error') {
              setMessages(p => [...p, { role: 'assistant', content: `🚨 ${d.content}` }])
              setIsTyping(false); setStatus('Idle')
            }
          } catch {}
        }
      }
    } catch (e) {
      setMessages(p => [...p, { role: 'assistant', content: `🚨 Network error: ${e.message}` }])
      setIsTyping(false); setStatus('Idle')
    }
  }

  return (
    <div className="page-shell chat-page">
      <ParticleField />
      
      <TechnicalTrace 
        isOpen={isTraceOpen} 
        onClose={() => setIsTraceOpen(false)} 
        traceData={activeTrace} 
      />

      <div className="chat-feed">
        <AnimatePresence mode="wait">
          {messages.length === 0 ? (
            <motion.div key="welcome" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="welcome-screen">
              <motion.div className="welcome-icon" animate={{ y: [-4, 4, -4] }} transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}>
                <Shield size={44} />
              </motion.div>
              <h1>Logic Audit Workbench</h1>
              <p>Move beyond probabilistic chat. Every numerical claim in the Sentinel Swarm is verified by a secure Python sandbox.</p>
              <motion.div className="suggestion-grid" variants={{ show: { transition: { staggerChildren: 0.08 } } }} initial="hidden" animate="show">
                {SUGGESTIONS.map(s => (
                  <motion.button
                    key={s.label}
                    variants={{ hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } }}
                    className="suggestion-chip"
                    onClick={() => send(s.q)}
                  >
                    <span className="chip-icon">{s.icon}</span>
                    <span>{s.label}</span>
                  </motion.button>
                ))}
              </motion.div>
            </motion.div>
          ) : (
            <div className="messages-wrapper">
              {messages.map((m, i) => (
                <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className={`msg-row ${m.role}`}>
                  <div className="msg-avatar">{m.role === 'user' ? 'U' : <Shield size={14} />}</div>
                  <div className="msg-bubble glass-card">
                    <p>{m.content}</p>
                    
                    {m.role === 'assistant' && m.metadata && (
                      <button className="audit-btn" onClick={() => openTrace(m.metadata)}>
                        <Terminal size={12} />
                        <span>PROOF OF TRACE</span>
                      </button>
                    )}
                  </div>
                </motion.div>
              ))}
              {isTyping && (
                <div className="msg-row assistant">
                  <div className="msg-avatar pulsing"><Shield size={14} /></div>
                  <div className="thinking-bubble glass-card">
                    <div className="dots"><span/><span/><span/></div>
                    <span className="thinking-label">{status}</span>
                  </div>
                </div>
              )}
              <div ref={endRef} />
            </div>
          )}
        </AnimatePresence>
      </div>

      <div className="input-zone">
        <SwarmStatus status={status} />
        <form onSubmit={e => { e.preventDefault(); send(input) }} className="pill-input glass-card">
          <Sparkles size={16} className="pill-icon" />
          <input value={input} onChange={e => setInput(e.target.value)} placeholder="Submit logical claim for audit…" />
          <button type="submit" disabled={status !== 'Idle' || !input.trim()} className="pill-btn">
            <Send size={15} />
          </button>
        </form>
        <p className="legal-footer">Numerical claims are deterministic via Sandbox. Ethics/Opinion are probabilistic.</p>
      </div>
    </div>
  )
}
