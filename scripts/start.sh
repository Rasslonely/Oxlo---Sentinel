#!/bin/bash
# Oxlo-Sentinel: Hybrid Startup Script
# This script launches both the Telegram Bot and the FastAPI Web Server.

echo "🚀 Starting Oxlo-Sentinel Swarm Infrastructure..."

# 1. Start the Telegram Bot in the background
echo "🤖 Launching Telegram Bot (Background Service)..."
python -m bot.main &

# 2. Start the FastAPI Web Server in the foreground
# This process will bind to the $PORT provided by the platform (Railway/Vercel)
echo "🌐 Launching Web API (Foreground Web Service)..."
python -m api.main
