# /tmp/list_models.py
import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = AsyncOpenAI(
        api_key=os.getenv("OXLO_API_KEY"),
        base_url="https://api.oxlo.ai/v1"
    )
    try:
        models = await client.models.list()
        print("Available Models on Oxlo:")
        for m in models.data:
            print(f"- {m.id}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
