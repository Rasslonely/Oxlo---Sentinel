import React, { useState } from 'react'

/* ── Layout constants ─────────────────────────────────────────── */
const NODE_H    = 56
const LAYER_GAP = 92    // gap between bottom of one layer top of next
const FIRST_Y   = 24
const SVG_W     = 900

const computeLayerY = (idx) => FIRST_Y + idx * (NODE_H + LAYER_GAP)
const TOOLTIP_Y = (idx) => computeLayerY(idx) + NODE_H + 10  // 10px below layer
const TOOLTIP_H = LAYER_GAP - 18                              // ≈74px

/* ── Actual model names from the project codebase ──────────────
   Router:          llama-3.2-3b   (fast classifier, <200ms)
   Generator A:     deepseek-v3.2  (primary hypothesis)
   Generator B:     mistral-7b     (SKEPTIC — hunts fallacies)
   MCP Caller:      llama-3.2-3b   (code-fixer on sandbox error)
   Auditor:         deepseek-r1-8b (RL-trained reasoning model)
   Synthesizer:     deepseek-v3.2  (flagship composition)
   Embeddings:      bge-large      (Supabase vector store)
   ────────────────────────────────────────────────────────────── */

const LAYERS = [
  {
    id: 'client', label: 'INTERFACE LAYER', color: '#7c5ff0', idx: 0,
    nodes: [
      { id: 'tg',  x: 180, w: 120, label: '📱 Telegram', sub: 'Mobile / Desktop' },
      { id: 'web', x: 360, w: 120, label: '🌐 Web Chat',  sub: 'Vite + React' },
    ],
  },
  {
    id: 'interface', label: 'SYSTEM INFRASTRUCTURE', color: '#00b4d8', idx: 1,
    nodes: [
      { id: 'aio', x: 80,  w: 130, label: 'aiogram 3.x', sub: 'Long-Polling Bot' },
      { id: 'api', x: 280, w: 120, label: 'FastAPI',       sub: 'SSE Gateway' },
      { id: 'eq',  x: 470, w: 120, label: 'EditQueue',     sub: 'Debounced 1.2s' },
    ],
  },
  {
    id: 'engine', label: 'COGNITIVE CORE (THE BRAIN)', color: '#00f3ff', idx: 2, isBrain: true,
    nodes: [
      { id: 'n1', x: 10,  w: 112, label: 'Router',            sub: 'Complex / Flash' },
      { id: 'n2', x: 138, w: 116, label: 'Divergent Gen',     sub: 'Parallel Swarm' },
      { id: 'n3', x: 272, w: 116, label: 'Skeptic Node',      sub: 'Logic Guard' },
      { id: 'n4', x: 408, w: 120, label: 'MCP Tool Caller',   sub: 'Tool Bridge' },
      { id: 'n5', x: 546, w: 116, label: 'Auditor Node',      sub: 'Gatekeeper' },
      { id: 'n6', x: 678, w: 120, label: 'Synthesizer',       sub: 'Final Voice' },
    ],
  },
  {
    id: 'mcp', label: 'TOOLING & SANDBOX LAYER', color: '#f77f00', idx: 3,
    nodes: [
      { id: 'mcps', x: 220, w: 140, label: 'FastMCP Server', sub: 'stdio transport' },
      { id: 'e2b',  x: 430, w: 140, label: 'E2B Sandbox',    sub: 'Isolated MicroVM' },
    ],
  },
  {
    id: 'db', label: 'PERSISTENCE & INTELLIGENCE', color: '#3bf17c', idx: 4,
    nodes: [
      { id: 'pg',  x: 170, w: 160, label: 'Log Storage',    sub: 'Supabase Postgres' },
      { id: 'vec', x: 400, w: 150, label: 'Vector Memory',  sub: 'bge-large (RAG)' },
    ],
  },
]

/* ── Precise tooltips per node (drawn in gap below its layer) ─── */
const TOOLTIPS = {
  tg:   { t: '📱 Telegram',       a: 'User sends any message via Telegram (mobile or desktop).', b: 'aiogram 3.x receives it via long-polling. The bot edits one message live as the swarm runs.' },
  web:  { t: '🌐 Web Chat',        a: 'Vite + React SPA — sends POST /api/chat, gets SSE stream back.', b: 'Every LangGraph status event is forwarded in real-time, no polling.' },
  aio:  { t: 'aiogram 3.x',        a: 'Handles async Telegram updates. Manages FSM conversation state.', b: 'Invokes the LangGraph swarm and forwards status events to EditQueue.' },
  api:  { t: 'FastAPI SSE Gateway', a: 'POST /api/chat endpoint streams LangGraph astream_events.', b: 'Converts Python async generators → Server-Sent Events for the browser.' },
  eq:   { t: 'EditQueue',           a: 'Debounces Telegram message edits to max 1 edit per 1.2s.', b: 'Prevents hitting Telegram flood-control limits during rapid swarm updates.' },
  n1:   { t: 'Router — Fast Path',  a: 'Classifies intent into "Flash" (Chat) or "Complex" (Reasoning) paths.', b: 'Directly triggers Synthesis for simple queries to save tokens and time.' },
  n2:   { t: 'Divergent Generator', a: 'Fires swarm models in staggered parallel using jitter delays.', b: 'Uses DeepSeek-v3.2 and Mistral-7b as primary hypothesis engines.' },
  n3:   { t: 'Skeptic Node',        a: 'The SKEPTIC role: hunts for logical traps and inconsistencies.', b: 'Critical for avoiding AI hallucinations in mathematical proofs.' },
  n4:   { t: 'MCP Tool Caller',     a: 'The "Hands" of the AI—executes Python scripts via MCP protocol.', b: 'Extracts code blocks from the swarm and runs them in the E2B Sandbox.' },
  n5:   { t: 'Auditor Node',        a: 'The "Brain"—A heavy reasoning model (DeepSeek-R1) that audits the sandbox output.', b: 'Controls the debate loop; can force models back to generation if logic fails.' },
  n6:   { t: 'Synthesizer',         a: 'The "Voice"—composes the final human-centric verified answer.', b: 'Integrates system traces and confidence scores into the final response.' },
  mcps: { t: 'FastMCP Server',      a: 'Unified tool interface using the Model Context Protocol.', b: 'Allows any agent to access the Python Sandbox securely via stdio.' },
  e2b:  { t: 'E2B Sandbox',          a: 'Hardware-isolated MicroVM for deterministic code execution.', b: 'Ensures that calculations are proven by math, not predicted by tokens.' },
  pg:   { t: 'Supabase Postgres',   a: 'Persistent storage for user sessions and reasoning traces.', b: 'Ensures that the state machine can recover from crashes or restarts.' },
  vec:  { t: 'Vector Memory (RAG)', a: 'Semantic search layer using bge-large embeddings.', b: 'Allows the swarm to retrieve past verified logic for similar problems.' },
}

/* ── Build node center-point lookup ────────────────────────────── */
const buildNodeMap = () => {
  const map = {}
  LAYERS.forEach(layer => {
    const y = computeLayerY(layer.idx)
    layer.nodes.forEach(n => {
      map[n.id] = { x: n.x + (n.w ?? 112) / 2, y: y + NODE_H / 2, color: layer.color, layerIdx: layer.idx }
    })
  })
  return map
}
const NM = buildNodeMap()

/* ── Edges ──────────────────────────────────────────────────────── */
const EDGES = [
  { f: 'tg',  t: 'aio', d: false, lbl: 'message' },
  { f: 'web', t: 'api', d: false, lbl: 'POST /chat' },
  { f: 'aio', t: 'n1',  d: false, lbl: 'invoke' },
  { f: 'api', t: 'n1',  d: false, lbl: 'invoke' },
  { f: 'aio', t: 'eq',  d: false, lbl: 'stream' },
  { f: 'eq',  t: 'tg',  d: true,  lbl: 'edit' },
  { f: 'n1',  t: 'n2',  d: false, lbl: 'complex' },
  { f: 'n1',  t: 'n3',  d: false, lbl: 'complex' },
  { f: 'n1',  t: 'n6',  d: false, lbl: 'flash' },
  { f: 'n2',  t: 'n4',  d: false, lbl: 'logic' },
  { f: 'n3',  t: 'n4',  d: false, lbl: 'logic' },
  { f: 'n4',  t: 'n5',  d: false, lbl: 'results' },
  { f: 'n5',  t: 'n2',  d: true,  lbl: 'debate' },
  { f: 'n5',  t: 'n3',  d: true,  lbl: 'debate' },
  { f: 'n5',  t: 'n6',  d: false, lbl: 'verdict' },
  { f: 'n4',  t: 'mcps',d: false, lbl: 'MCP' },
  { f: 'mcps',t: 'e2b', d: false, lbl: 'microvm' },
  { f: 'n6',  t: 'pg',  d: false, lbl: 'store' },
  { f: 'n5',  t: 'vec', d: false, lbl: 'rag' },
]

/* ── Edge path ──────────────────────────────────────────────────── */
function edgePath(f, t) {
  const a = NM[f]; const b = NM[t]
  if (!a || !b) return ''
  const mx = (a.x + b.x) / 2
  const my = (a.y + b.y) / 2
  const dy = b.y - a.y
  if (Math.abs(dy) < 5) {
    return `M ${a.x} ${a.y} Q ${mx} ${a.y - 38} ${b.x} ${b.y}`
  }
  return `M ${a.x} ${a.y} C ${a.x} ${my} ${b.x} ${my} ${b.x} ${b.y}`
}

/* ── Layer ID → index lookup ────────────────────────────────────── */
const nodeLayerMap = {}
LAYERS.forEach(layer => { layer.nodes.forEach(n => { nodeLayerMap[n.id] = layer.idx }) })

const SVG_H = computeLayerY(LAYERS.length - 1) + NODE_H + LAYER_GAP + 10

/* ── Component ──────────────────────────────────────────────────── */
export default function ArchitectureGraph() {
  const [hovered, setHovered] = useState(null)

  const hoveredLayerIdx = hovered != null ? (nodeLayerMap[hovered] ?? -1) : -1

  return (
    <div className="arch-graph-wrapper">
      <svg
        viewBox={`0 0 ${SVG_W} ${SVG_H}`}
        xmlns="http://www.w3.org/2000/svg"
        className="arch-svg"
        style={{ width: '100%', height: 'auto', display: 'block' }}
      >
        <defs>
          <marker id="arr"  markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto">
            <path d="M0,0 L0,6 L7,3 z" fill="rgba(255,255,255,0.25)" />
          </marker>
          <marker id="arr-hi" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto">
            <path d="M0,0 L0,6 L7,3 z" fill="#00f3ff" />
          </marker>
          {LAYERS.map(l => (
            <filter key={l.id} id={`glow-${l.id}`} x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3.5" result="b" />
              <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          ))}
        </defs>

        {/* Lane backgrounds + Brain group */}
        {LAYERS.map(layer => {
          const y = computeLayerY(layer.idx)
          if (layer.isBrain) {
            return (
              <g key={layer.id}>
                <rect
                   x={4} y={y - 14} width={SVG_W - 8} height={NODE_H + 28}
                   fill="rgba(0, 243, 255, 0.05)" stroke="rgba(0, 243, 255, 0.15)"
                   strokeWidth="1" strokeDasharray="4,4" rx="12"
                />
                <text x={12} y={y - 20} fill="#00f3ff" fontSize="9" fontWeight="800" style={{ letterSpacing: 1.2 }}>HIVE CORE (AI REASONING)</text>
              </g>
            )
          }
          return (
            <rect key={layer.id}
              x={0} y={y - 6} width={SVG_W} height={NODE_H + 12}
              fill={`${layer.color}08`} rx="6"
            />
          )
        })}

        {/* Layer labels (right side) */}
        {LAYERS.map(layer => {
          const y = computeLayerY(layer.idx)
          return (
            <text key={layer.id}
              x={SVG_W - 6} y={y + NODE_H / 2 + 4}
              textAnchor="end" fill={layer.color} fontSize="8.5"
              opacity="0.45"
              style={{ fontFamily: 'JetBrains Mono, monospace', letterSpacing: 1.8, textTransform: 'uppercase' }}
            >
              {layer.label}
            </text>
          )
        })}

        {/* Edges */}
        {EDGES.map((e, i) => {
          const isHi = hovered === e.f || hovered === e.t
          const srcColor = NM[e.f]?.color ?? '#00f3ff'
          const path = edgePath(e.f, e.t)
          if (!path) return null
          return (
            <g key={i}>
              <path
                d={path} fill="none"
                stroke={isHi ? srcColor : 'rgba(255,255,255,0.09)'}
                strokeWidth={isHi ? 1.8 : 0.8}
                strokeDasharray={e.d ? '5,4' : undefined}
                markerEnd={isHi ? 'url(#arr-hi)' : 'url(#arr)'}
                style={{ transition: 'stroke 0.25s, stroke-width 0.25s' }}
              />
              {isHi && e.lbl && (
                <text
                  x={(NM[e.f]?.x + NM[e.t]?.x) / 2}
                  y={(NM[e.f]?.y + NM[e.t]?.y) / 2 - 5}
                  textAnchor="middle" fill="#ffffffaa" fontSize="7.5"
                  style={{ fontFamily: 'JetBrains Mono, monospace' }}
                >
                  {e.lbl}
                </text>
              )}
            </g>
          )
        })}

        {/* Nodes */}
        {LAYERS.flatMap(layer => {
          const y = computeLayerY(layer.idx)
          return layer.nodes.map(n => {
            const isHov = hovered === n.id
            const nw = n.w ?? 112
            return (
              <g key={n.id} style={{ cursor: 'pointer' }}
                onMouseEnter={() => setHovered(n.id)}
                onMouseLeave={() => setHovered(null)}
              >
                {isHov && (
                  <rect x={n.x - 3} y={y - 3} width={nw + 6} height={NODE_H + 6} rx="11"
                    fill="none" stroke={layer.color} strokeWidth="1.5"
                    opacity="0.55" filter={`url(#glow-${layer.id})`}
                  />
                )}
                {/* Accent bar */}
                <rect x={n.x} y={y} width={4} height={NODE_H} fill={layer.color} opacity={isHov ? 0.9 : 0.55} rx="9" />
                {/* Node body */}
                <rect
                  x={n.x} y={y} width={nw} height={NODE_H} rx="9"
                  fill={isHov ? `${layer.color}1a` : 'rgba(12,14,22,0.88)'}
                  stroke={isHov ? layer.color : 'rgba(255,255,255,0.09)'}
                  strokeWidth={isHov ? 1.5 : 0.8}
                  style={{ transition: 'all 0.22s' }}
                />
                {/* Label */}
                <text x={n.x + 13} y={y + 21}
                  fill={isHov ? '#fff' : 'rgba(255,255,255,0.83)'}
                  fontSize="10.5" fontWeight="600"
                  style={{ fontFamily: 'Inter, sans-serif', transition: 'fill 0.2s' }}
                >
                  {n.label}
                </text>
                {/* Sub-label */}
                <text x={n.x + 13} y={y + 36}
                  fill={isHov ? layer.color : 'rgba(255,255,255,0.32)'}
                  fontSize="8" style={{ fontFamily: 'JetBrains Mono, monospace', transition: 'fill 0.2s' }}
                >
                  {n.sub}
                </text>
              </g>
            )
          })
        })}

        {/* ── Inline tooltip in the gap BELOW the hovered node's layer ── */}
        {hovered && TOOLTIPS[hovered] && hoveredLayerIdx >= 0 && (() => {
          const tip = TOOLTIPS[hovered]
          const ty = TOOLTIP_Y(hoveredLayerIdx)
          const layer = LAYERS[hoveredLayerIdx]
          return (
            <g style={{ pointerEvents: 'none' }}>
              {/* Tooltip panel */}
              <rect
                x={8} y={ty} width={SVG_W - 16} height={TOOLTIP_H} rx="8"
                fill="rgba(12,14,22,0.92)"
                stroke={`${layer.color}33`}
                strokeWidth="1"
              />
              {/* Left accent */}
              <rect x={8} y={ty} width={3} height={TOOLTIP_H} rx="4" fill={layer.color} opacity="0.75" />
              {/* Node name */}
              <text x={22} y={ty + 18}
                fill={layer.color} fontSize="9.5" fontWeight="700"
                style={{ fontFamily: 'Inter, sans-serif' }}
              >
                {tip.t}
              </text>
              {/* Line A */}
              <text x={22} y={ty + 34}
                fill="rgba(255,255,255,0.72)" fontSize="9"
                style={{ fontFamily: 'Inter, sans-serif' }}
              >
                {tip.a}
              </text>
              {/* Line B */}
              <text x={22} y={ty + 50}
                fill="rgba(255,255,255,0.45)" fontSize="8.5"
                style={{ fontFamily: 'Inter, sans-serif' }}
              >
                {tip.b}
              </text>
            </g>
          )
        })()}
      </svg>

      <p className="arch-hint">Hover any node — details appear in the gap below its layer</p>
    </div>
  )
}
