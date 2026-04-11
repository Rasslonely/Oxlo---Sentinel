import React, { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { FileText, Database, Shield, Zap, Server, Cpu, GitBranch, Lock } from 'lucide-react'
import ArchitectureGraph from '../components/ArchitectureGraph'

const TECH_STACK = [
  { icon: Cpu,       label: 'LangGraph',      desc: 'Stateful cyclic agent graph with conditional edges and astream_events',   tag: 'ORCHESTRATION', color: '#00f3ff' },
  { icon: Shield,    label: 'Omniscient Shield', desc: 'Centralized asyncio.Semaphore(1) protecting all AI inference calls', tag: 'THROTTLING',     color: '#00e87a' },
  { icon: Zap,       label: 'Oxlo API',        desc: 'Adaptive swarm scaling: fires 2–4 parallel model calls per query', tag: 'AI INFERENCE',   color: '#ff006e' },
  { icon: Shield,    label: 'E2B Sandbox',     desc: 'Hardware-isolated Python MicroVM — verified execution, zero hallucination', tag: 'VERIFICATION', color: '#00e87a' },
  { icon: Server,    label: 'FastAPI + SSE',   desc: 'Real-time streaming from swarm nodes to the web chat interface',         tag: 'BACKEND',       color: '#7c5ff0' },
  { icon: Database,  label: 'Supabase',        desc: 'Managed PostgreSQL — sessions, chat_history, full audit_logs',           tag: 'DATABASE',      color: '#3bf17c' },
  { icon: GitBranch, label: 'MCP Protocol',    desc: 'Anthropic tool protocol — eliminates N×M integration complexity',        tag: 'TOOLING',       color: '#f77f00' },
  { icon: Lock,      label: 'DeepSeek-R1',     desc: 'RL-trained reasoning auditor — structured JSON consensus evaluation',    tag: 'AUDITOR',       color: '#ff006e' },
]

const DECISIONS = [
  { q: 'Why 2 Models for Debate?',    a: 'We use a Principal Model (DeepSeek) and a Skeptic (Mistral). Parallelism reduces latency to the slowest model (~3s) while the clash of logic eliminates bias.' },
  { q: 'Why the Omniscient Shield?',  a: 'AI APIs have strict concurrency limits. The Shield serializes requests at the kernel level, ensuring 100% reliability on any account tier.' },
  { q: 'Why MCP over direct calls?',  a: 'MCP eliminates the N×M integration problem. Add one new tool to the MCP Server and every agent gains it instantly with zero code changes.' },
  { q: 'Why E2B over subprocess?',    a: 'E2B runs in a hardware-isolated MicroVM with no network access to host secrets — critical for safe Python code execution.' },
  { q: 'Why DeepSeek-R1 for Audit?',  a: 'DeepSeek-R1 was RL-trained specifically for long-context reasoning — optimal for evaluating complex logical consensus.' },
]

const container = { hidden: {}, show: { transition: { staggerChildren: 0.07 } } }
const item = { hidden: { opacity: 0, y: 18 }, show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } } }

export default function DocsPage() {
  return (
    <div className="page-shell scrollable">
      <div className="page-content-inner">

        {/* Hero */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="page-hero">
          <div className="page-hero-icon"><FileText size={28} /></div>
          <div>
            <h1>Documentation</h1>
            <p>System architecture, technology stack, and design decisions for Oxlo-Sentinel v4.5.</p>
          </div>
        </motion.div>

        {/* Architecture Graph */}
        <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="doc-section">
          <div className="section-header">
            <h2 className="section-heading">System Architecture</h2>
            <span className="section-badge">Interactive</span>
          </div>
          <div className="glass-card arch-card">
            <ArchitectureGraph />
          </div>
        </motion.section>

        {/* Tech Stack */}
        <section className="doc-section">
          <h2 className="section-heading">Technology Stack</h2>
          <motion.div variants={container} initial="hidden" animate="show" className="tech-grid">
            {TECH_STACK.map((t) => (
              <motion.div key={t.label} variants={item} className="tech-card glass-card" style={{ '--tc': t.color }}>
                <div className="tech-card-top">
                  <div className="tech-icon-wrap" style={{ background: `${t.color}18`, border: `1px solid ${t.color}33` }}>
                    <t.icon size={22} style={{ color: t.color }} />
                  </div>
                  <span className="tech-tag" style={{ color: t.color }}>{t.tag}</span>
                </div>
                <h3>{t.label}</h3>
                <p>{t.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* Design Decisions */}
        <section className="doc-section">
          <h2 className="section-heading">Key Design Decisions</h2>
          <div className="decisions-list">
            {DECISIONS.map((d, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 + i * 0.07, duration: 0.35, ease: 'easeOut' }}
                className="decision-item glass-card"
              >
                <div className="decision-num">0{i + 1}</div>
                <div className="decision-body">
                  <h4>{d.q}</h4>
                  <p>{d.a}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </section>

      </div>
    </div>
  )
}
