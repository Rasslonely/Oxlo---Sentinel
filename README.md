# 🧠 Oxlo - Sentinel
> **An Unbreakable, Deterministic AI Logic Swarm**

![Version](https://img.shields.io/badge/Status-Hackathon_Ready-success?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Cognitive_Swarm-blue?style=for-the-badge)
![Oxlo AI](https://img.shields.io/badge/AI-Oxlo_Gateway-black?style=for-the-badge)
![E2B Sandbox](https://img.shields.io/badge/Execution-E2B_Python_Sandbox-red?style=for-the-badge)

**Oxlo - Sentinel** is a high-stakes, multi-agent cognitive architecture built for Telegram. It completely eliminates AI math hallucinations by mathematically restricting the LLM's right to guess. Instead of generating text answers, the Hivemind writes Python scripts, executes them in an isolated microVM sandbox, audits the raw stdout, and forces internal debate rounds until mathematical consensus is achieved.

It is built specifically for the **OxBuild Hackathon** to demonstrate ultra-high API call optimization combined with the bleeding-edge Model Context Protocol (MCP).

---

## ⚡ The Architecture: Why it Never Fails

Sentinel uses a deeply modified **LangGraph** state machine running on pure `asyncio` parallel event loops:

1. **Pre-Cognition (RAG Vector Memory):** 
Retrieves historical logic patterns for similar problems via Supabase `pgvector`.
2. **True Parallel Generation:** 
Fires multiple foundational models simultaneously (e.g. `deepseek-v3.2` & `llama-3.1-8b`) using `asyncio.gather` for zero chronological latency.
3. **MCP E2B Hardware Isolation:** 
The swarm is forced by system prompt to isolate numbers into `python` code blocks. Sentinel actively extracts the blocks via regex parsing, spins up a heavily isolated micro-server via E2B, executes the calculation, and retrieves the empirical truth.
4. **The Auditor (DeepSeek-R1-8B):** 
A heavy-reasoning node analyzes the Sandbox terminal output alongside the generative hypotheses. If the models contradict each other or the python script failed, the Auditor **vetoes the answer** and forces the swarm back into a new Debate Cycle.
5. **Anti-Deadlock Congestion Bypass:** 
Protected by ultra-aggressive local watchdogs (`<15s` micro-locks) and an expansive `300s` umbrella, Sentinel degrades gracefully when the upstream model APIs suffer from `429 Too Many Requests` or `502 Bad Gateway` drops, guaranteeing that a single broken server connection doesn't drag the entire graph into the abyss.

---

## 🛠️ Quickstart (5 Minutes to Hivemind)

This application runs purely as a background worker on environments like Railway, or on your local machine using Long-Polling.

### 1. Prerequisites
Ensure you have Python 3.11+ installed.
```bash
git clone https://github.com/Rasslonely/Oxlo---Sentinel.git
cd oxlo-sentinel
pip install -e .
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

### 3. Initialize the Neural Net
Start the bot. The system will automatically pre-warm the Python sandbox and establish database connection pools.
```bash
python -m bot.main
```
Open Telegram and press `/start`. You are now talking to the swarm.

---

## 📊 Live Terminal UX
Sentinel pushes live terminal telemetry down to the end-user via AIogram's debounced edit queue. You don't have to wait in the dark; you literally watch the Swarm debate itself, execute code, and audit answers in real-time right from your mobile device. 

*Designed strictly for 100% deterministic outputs. Zero guess work.*
