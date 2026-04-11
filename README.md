# 🧠 Oxlo - Sentinel
> **An Unbreakable, Deterministic AI Logic Swarm**

![Version](https://img.shields.io/badge/Status-Hackathon_Ready-success?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Cognitive_Swarm-blue?style=for-the-badge)
![Oxlo AI](https://img.shields.io/badge/AI-Oxlo_Gateway-black?style=for-the-badge)
![E2B Sandbox](https://img.shields.io/badge/Execution-E2B_Python_Sandbox-red?style=for-the-badge)

**Oxlo - Sentinel** is a high-fidelity, cognitive swarm platform that eliminates AI hallucinations through deterministic mathematical verification. Unlike traditional bots, Sentinel operates as a dual-interface command center (Telegram + Web) where a hivemind of models debates logically, executes Python code in isolated microVMs, and reaches consensus before delivering verified answers.

It is built for the **OxBuild Hackathon** to showcase extreme API optimization, real-time SSE streaming, and the Model Context Protocol (MCP).

---

## ⚡ The Architecture: Why it Never Fails

Sentinel uses a deeply modified **LangGraph** state machine running on pure `asyncio` parallel event loops:

1. **Pre-Cognition (RAG Vector Memory):** 
Retrieves historical logic patterns for similar problems via Supabase `pgvector` & `bge-large`.
2. **True Parallel Generation:** 
Fires multiple foundational models simultaneously (`deepseek-v3.2`, `mistral-7b`) using `asyncio.gather` for zero chronological latency.
3. **MCP E2B Hardware Isolation:** 
The swarm is forced by system prompt to isolate numbers into `python` code blocks. Sentinel actively extracts the blocks via regex parsing, spins up a heavily isolated micro-server via E2B, executes the calculation, and retrieves the empirical truth.
4. **The Auditor (DeepSeek-R1-8B):** 
A heavy-reasoning node analyzes the Sandbox terminal output alongside the generative hypotheses. If models contradict each other or the script fails, the Auditor **vetoes the answer** and triggers a debate cycle.
5. **Anti-Deadlock Congestion Bypass:** 
Protecting the Hivemind via ultra-aggressive local watchdogs (`<15s` micro-locks) and an expansive `300s` umbrella, Sentinel degrades gracefully when the upstream model APIs suffer from `429 Too Many Requests` or `502 Bad Gateway` drops, guaranteeing that a single broken server connection doesn't drag the entire graph into the abyss.

---

## 🖥️ The Command Center (Web UI)

Sentinel v5.0 introduces a premium Web Interface built with Vite + React:
- **Alpha Swarm Feed**: Real-time SSE streaming of swarm reasoning and status events.
- **Logic Audit**: Visual 5-step pipeline tracking consensus, sandbox logs, and models.
- **Interactive Architecture**: A custom SVG graph showing the entire client-to-tooling topology.
- **Tutorial & Docs**: Integrated interactive walkthroughs and technical specs.

---

## 🛠️ Quickstart (5 Minutes to Hivemind)

This application runs purely as a background worker on environments like Railway, or on your local machine using Long-Polling.

### 1. Prerequisites
Ensure you have Python 3.11+ installed.
```bash
git clone https://github.com/Rasslonely/Oxlo---Sentinel.git
cd oxlo-sentinel

# 1. Backend Setup
pip install -e .

# 2. Frontend Setup
cd web && npm install
cd ..
```

### 2. Environment Variables
Copy `.env.example` to `.env` and inject the required keys:
```env
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
OXLO_API_KEY="your_oxlo_api_key"
E2B_API_KEY="your_e2b_api_key"
SUPABASE_URL="https://xxx.supabase.co"
SUPABASE_ANON_KEY="your_db_key"
```

# Start the Telegram Bot
python -m bot.main

# Start the Web API (in another terminal)
python -m api.main

# Start the Command Center (in another terminal)
cd web && npm run dev
```

Open Telegram and press `/start`, or visit `http://localhost:5173` to enter the Command Center.

---

## 📊 Real-Time Telemetry
Sentinel pushes live telemetry to both Telegram (via debounced edit queues) and the Web (via Server-Sent Events). You don't have to wait in the dark; you literally watch the Swarm debate itself, execute code, and audit answers in real-time across all your devices. 

*Designed strictly for 100% deterministic outputs. Zero guess work.*
