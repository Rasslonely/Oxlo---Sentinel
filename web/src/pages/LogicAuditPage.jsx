import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FlaskConical, Play, CheckCircle, XCircle, Loader2, ChevronRight, AlertCircle } from 'lucide-react'

const EXAMPLES = [
  { label: 'Monty Hall Sim', q: 'Simulate 100,000 Monty Hall games. Prove switching wins ~66.7% of the time.' },
  { label: 'P=NP Analysis', q: 'Analyze the logical implications if P were proven equal to NP.' },
  { label: 'Float Paradox', q: 'In IEEE 754, explain and prove why 0.1 + 0.2 ≠ 0.3 in Python.' },
  { label: 'Birthday Collision', q: 'Prove via simulation that 23 people yield >50% chance of a shared birthday.' },
  { label: 'Collatz Conjecture', q: 'Verify the Collatz conjecture for all integers 1–50,000 via Python.' },
]

const CYCLE_LABELS = ['ROUTE', 'GENERATE', 'VERIFY', 'AUDIT', 'SYNTHESIZE']

export default function LogicAuditPage() {
  const [input, setInput] = useState('')
  const [result, setResult] = useState(null)
  const [status, setStatus] = useState('idle')
  const [log, setLog] = useState([])
  const [activeStep, setActiveStep] = useState(-1)

  const runAudit = async (query) => {
    const q = query || input
    if (!q.trim()) return
    setInput(q)
    setStatus('running')
    setResult(null)
    setLog([])
    setActiveStep(0)
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: q }),
      })
      const reader = res.body.getReader()
      const dec = new TextDecoder()
      let buf = ''
      let stepIdx = 0
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buf += dec.decode(value, { stream: true })
        const lines = buf.split('\n'); buf = lines.pop()
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const d = JSON.parse(line.slice(6))
            if (d.type === 'status') {
              setLog(p => [...p, { text: d.content, ts: new Date().toLocaleTimeString() }])
              stepIdx = Math.min(stepIdx + 1, CYCLE_LABELS.length - 1)
              setActiveStep(stepIdx)
            } else if (d.type === 'final') {
              setResult({ ok: true, content: d.data?.messages?.at(-1)?.content ?? '(No answer)' })
              setStatus('done'); setActiveStep(CYCLE_LABELS.length - 1)
            } else if (d.type === 'error') {
              setResult({ ok: false, content: d.content })
              setStatus('error'); setActiveStep(-1)
            }
          } catch {}
        }
      }
    } catch (e) {
      setResult({ ok: false, content: e.message })
      setStatus('error'); setActiveStep(-1)
    }
  }

  return (
    <div className="page-shell scrollable">
      <div className="page-content-inner">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="page-hero">
          <div className="page-hero-icon"><FlaskConical size={26} /></div>
          <div>
            <h1>Logic Audit Engine</h1>
            <p>Submit a claim — the Swarm debates, the sandbox verifies, the Auditor rules.</p>
          </div>
        </motion.div>

        {/* Pipeline steps */}
        <div className="pipeline-bar">
          {CYCLE_LABELS.map((l, i) => (
            <div key={l} className={`pipeline-step ${activeStep === i ? 'active' : ''} ${activeStep > i ? 'done' : ''}`}>
              <div className="pipeline-dot">{activeStep > i ? <CheckCircle size={10} /> : <span>{i + 1}</span>}</div>
              <span>{l}</span>
              {i < CYCLE_LABELS.length - 1 && <div className="pipeline-line" />}
            </div>
          ))}
        </div>

        <div className="audit-grid">
          {/* Left panel */}
          <div className="audit-input-panel glass-card">
            <h3>Your Claim</h3>
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Enter any logical claim, math statement, or algorithm to audit…"
              rows={6}
            />
            <button className="btn-primary" onClick={() => runAudit()} disabled={status === 'running' || !input.trim()}>
              {status === 'running'
                ? <><Loader2 size={15} className="spin" /> Auditing…</>
                : <><Play size={15} /> Run Audit</>}
            </button>
            <div className="divider-label">QUICK EXAMPLES</div>
            <div className="examples-list">
              {EXAMPLES.map(ex => (
                <button key={ex.label} className="example-chip" onClick={() => runAudit(ex.q)}>
                  <ChevronRight size={12} />
                  {ex.label}
                </button>
              ))}
            </div>
          </div>

          {/* Right panel */}
          <div className="audit-output-panel">
            <div className="glass-card audit-log">
              <div className="audit-log-header">
                <span>SWARM PROCESS LOG</span>
                <span className="log-count">{log.length} events</span>
              </div>
              {log.length === 0 && status === 'idle' && (
                <div className="log-empty"><AlertCircle size={18} /><span>Run an audit to see the swarm reasoning process</span></div>
              )}
              <AnimatePresence>
                {log.map((entry, i) => (
                  <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="log-entry">
                    <span className="log-num">{String(i + 1).padStart(2, '0')}</span>
                    <span className="log-ts">{entry.ts}</span>
                    <span className="log-text">{entry.text}</span>
                  </motion.div>
                ))}
              </AnimatePresence>
              {status === 'running' && (
                <motion.div animate={{ opacity: [0.4, 1, 0.4] }} transition={{ duration: 1.5, repeat: Infinity }} className="log-entry log-live">
                  <Loader2 size={12} className="spin" />
                  <span>Swarm processing…</span>
                </motion.div>
              )}
            </div>

            <AnimatePresence>
              {result && (
                <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className={`glass-card audit-verdict ${result.ok ? 'verdict-ok' : 'verdict-fail'}`}>
                  <div className="verdict-header">
                    {result.ok ? <CheckCircle size={18} /> : <XCircle size={18} />}
                    <span>{result.ok ? 'CONSENSUS REACHED' : 'AUDIT FAILED'}</span>
                  </div>
                  <p className="verdict-body">{result.content}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  )
}
