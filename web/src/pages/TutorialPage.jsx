import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { BookOpen, MessageSquare, Bot, Shield, Zap, CheckCircle, ChevronRight, Terminal } from 'lucide-react'

const STEPS = [
  {
    num: '01', icon: MessageSquare, color: '#00f3ff',
    title: 'Find the Bot',
    desc: 'Search @OxloSentinelBot in Telegram. Hit Start to initialize your secure session. The bot responds instantly.',
    terminal: [
      { type: 'user', text: '/start' },
      { type: 'bot',  text: '⚡ Sentinel Swarm initialized.\nSend me any logical claim or complex question.\n\nSessions are end-to-end encrypted.' },
    ],
  },
  {
    num: '02', icon: Zap, color: '#7c5ff0',
    title: 'Submit a Query',
    desc: 'Send any complex question or logical claim. The bot immediately posts a live-edited "thinking" message.',
    terminal: [
      { type: 'user', text: 'Is 127 prime? Prove it.' },
      { type: 'bot',  text: '⚡ Swarm Active…\n🧠 Routing → complex\n✦ 2 models debating in parallel…' },
    ],
  },
  {
    num: '03', icon: Bot, color: '#ff006e',
    title: 'Watch the Swarm',
    desc: 'The single bot message edits itself live — every 1.2s you see a new status update as each LangGraph node completes.',
    terminal: [
      { type: 'bot',  text: '🛠️ MCP Sandbox executing Python…\nstdout: "True — no divisors found in [2,11]"\n⚖️ Auditor: consensus reached (cycles=1)' },
    ],
  },
  {
    num: '04', icon: Shield, color: '#00e87a',
    title: 'Get Verified Answer',
    desc: 'The final message contains the verified answer with Python proof, confidence score, and sandbox execution time.',
    terminal: [
      { type: 'bot',  text: '✅ CONSENSUS REACHED\n\n127 is PRIME.\nVerified: no divisors in range [2, √127]\nSandbox: 12ms | Confidence: 0.99\n\nProof: checked all integers 2–11 ✓' },
    ],
  },
]

function TerminalLine({ line, i }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: i * 0.1 }}
      className={`term-line ${line.type}`}
    >
      <span className="term-prefix">{line.type === 'user' ? '>' : '$'}</span>
      <pre>{line.text}</pre>
    </motion.div>
  )
}

export default function TutorialPage() {
  const [active, setActive] = useState(0)
  const step = STEPS[active]

  return (
    <div className="page-shell scrollable">
      <div className="page-content-inner">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="page-hero">
          <div className="page-hero-icon"><BookOpen size={26} /></div>
          <div>
            <h1>Tutorial Flow</h1>
            <p>Zero to a verified Swarm query in 4 steps. No setup. Just Telegram.</p>
          </div>
        </motion.div>

        <div className="tutorial-layout">
          {/* Step rail */}
          <div className="steps-rail glass-card">
            {STEPS.map((s, i) => (
              <button key={i} className={`step-btn ${active === i ? 'active' : ''} ${i < active ? 'done' : ''}`} onClick={() => setActive(i)}>
                <div className="step-indicator" style={{ '--sc': s.color }}>
                  {i < active ? <CheckCircle size={14} /> : <span>{s.num}</span>}
                </div>
                <div className="step-btn-body">
                  <span className="step-btn-title">{s.title}</span>
                </div>
                {active === i && <div className="step-active-bar" style={{ background: s.color }} />}
              </button>
            ))}
            <div className="steps-progress">
              <div className="steps-progress-fill" style={{ width: `${((active + 1) / STEPS.length) * 100}%` }} />
            </div>
          </div>

          {/* Step detail */}
          <AnimatePresence mode="wait">
            <motion.div key={active} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.28, ease: 'easeOut' }} className="step-detail glass-card">
              <div className="step-detail-header" style={{ '--sc': step.color }}>
                <div className="step-detail-icon"><step.icon size={28} style={{ color: step.color }} /></div>
                <div>
                  <div className="step-label" style={{ color: step.color }}>STEP {step.num}</div>
                  <h2>{step.title}</h2>
                </div>
              </div>
              <p className="step-desc">{step.desc}</p>
              <div className="terminal-window">
                <div className="terminal-bar">
                  <span className="dot red"/><span className="dot yellow"/><span className="dot green"/>
                  <label><Terminal size={10} /> TELEGRAM TERMINAL</label>
                </div>
                <div className="terminal-body">
                  {step.terminal.map((line, j) => <TerminalLine key={j} line={line} i={j} />)}
                </div>
              </div>
              <div className="step-nav">
                {active > 0 && <button className="btn-ghost" onClick={() => setActive(a => a - 1)}>← Back</button>}
                {active < STEPS.length - 1
                  ? <button className="btn-primary" onClick={() => setActive(a => a + 1)}>Next Step <ChevronRight size={14} /></button>
                  : <a href="https://t.me/OxloSentinelBot" target="_blank" rel="noopener noreferrer" className="btn-primary">🚀 Open Bot</a>}
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
