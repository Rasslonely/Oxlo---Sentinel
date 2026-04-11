import React from 'react'
import { motion } from 'framer-motion'
import { Send, ExternalLink, Shield, Zap, Bot, MessageSquare, Terminal, CheckCircle } from 'lucide-react'

const FEATURES = [
  { icon: Zap, color: '#00f3ff', title: 'Live Swarm Feed', desc: 'A multi-model debate in real-time. Watch the message edit itself with each node transition.' },
  { icon: Shield, color: '#00e87a', title: 'Zero Hallucination', desc: 'Every numerical claim is Python-verified in an E2B secure MicroVM before reaching you.' },
  { icon: Bot, color: '#7c5ff0', title: 'MCP Protocol', desc: 'Anthropic\'s open tool standard connects the bot to external capabilities without bespoke adapters.' },
  { icon: MessageSquare, color: '#ff006e', title: 'Deep Consensus', desc: 'DeepSeek-R1 runs up to 2 debate cycles. Forces synthesis with best answer if cycles exhaust.' },
]

const COMMANDS = [
  { cmd: '/start',          desc: 'Initialize session and see capabilities' },
  { cmd: '/help',           desc: 'Deep-dive into the Hivemind architecture' },
  { cmd: '/think',          desc: 'Force Deep Thinking mode for the next query' },
  { cmd: '/fast',           desc: 'Force Flash Mode (instant chat) for the next query' },
  { cmd: '/audit <claim>',  desc: 'Full swarm audit with E2B sandbox verification' },
  { cmd: '/calc <math>',    desc: 'Mathematical proof with verified confidence score' },
]

const container = { hidden: {}, show: { transition: { staggerChildren: 0.09 } } }
const card = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } } }

const CHAT_DEMO = [
  { role: 'user', text: 'Is 127 a prime number? Prove it.' },
  { role: 'bot',  animated: true, steps: [
    '⚡ Swarm Active…',
    '🧠 Routing → complex',
    '✦ 2 models debating in parallel…',
    '🛠️ MCP Sandbox verifying Python…',
    '⚖️ Consensus reached (cycles=1)',
    '✅ 127 is PRIME. Conf: 0.99',
  ]},
]

function AnimatedChat() {
  const [step, setStep] = React.useState(0)
  React.useEffect(() => {
    if (step >= CHAT_DEMO[1].steps.length) return
    const t = setTimeout(() => setStep(s => s + 1), 900 + step * 80)
    return () => clearTimeout(t)
  }, [step])
  return (
    <div className="tg-chat glass-card">
      <div className="tg-header">
        <div className="tg-avatar"><Shield size={16} /></div>
        <div><p className="tg-name">Oxlo Sentinel</p><p className="tg-status"><span className="dot-green" />online</p></div>
      </div>
      <div className="tg-messages">
        <div className="tg-msg user">{CHAT_DEMO[0].text}</div>
        <div className="tg-msg bot">
          {CHAT_DEMO[1].steps.slice(0, step + 1).map((s, i) => (
            <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ lineHeight: 1.7 }}>
              {s}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function TelegramPage() {
  return (
    <div className="page-shell scrollable">
      <div className="page-content-inner">

        {/* Hero */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="tg-hero glass-card">
          <div className="tg-hero-left">
            <motion.div className="tg-logo" animate={{ rotate: [0, 5, -5, 0] }} transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}>
              <Send size={36} />
            </motion.div>
            <div className="tg-hero-text">
              <div className="tg-badge">NOW AVAILABLE</div>
              <h1>Sentinel on Telegram</h1>
              <p>The fastest path to the Cognitive Swarm. Zero setup — open Telegram and start verifying logic instantly.</p>
            </div>
            <div className="tg-actions">
              <a href="https://t.me/OxloSentinelBot" target="_blank" rel="noopener noreferrer" className="btn-primary">
                <Send size={15} /> Open in Telegram
              </a>
              <a href="/tutorial" className="btn-ghost">
                View Tutorial <ExternalLink size={13} />
              </a>
            </div>
          </div>
          <div className="tg-demo-wrap">
            <AnimatedChat />
          </div>
        </motion.div>

        {/* Features */}
        <motion.div variants={container} initial="hidden" animate="show" className="features-grid">
          {FEATURES.map(f => (
            <motion.div key={f.title} variants={card} className="feature-card glass-card" style={{ '--fc': f.color }}>
              <div className="feature-icon-wrap" style={{ background: `${f.color}18`, border: `1px solid ${f.color}30` }}>
                <f.icon size={22} style={{ color: f.color }} />
              </div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Commands */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="commands-section glass-card">
          <div className="commands-header">
            <Terminal size={18} className="icon-cyan" />
            <h2>Bot Commands</h2>
          </div>
          {COMMANDS.map(c => (
            <div key={c.cmd} className="command-row">
              <code className="command-code">{c.cmd}</code>
              <span className="command-desc">{c.desc}</span>
              <CheckCircle size={14} className="icon-green" />
            </div>
          ))}
        </motion.div>

      </div>
    </div>
  )
}
