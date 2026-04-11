# test_mistral.py
import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Load ENV
load_dotenv()

async def test_mistral():
    api_key = os.getenv("OXLO_API_KEY")
    base_url = os.getenv("OXLO_BASE_URL", "https://api.oxlo.ai/v1")
    
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    print(f"--- TESTING MISTRAL-7B ON OXLO ---")
    print(f"Base URL: {base_url}")
    
    try:
        response = await client.chat.completions.create(
            model="mistral-7b",
            messages=[{"role": "user", "content": "Say 'MISTRAL_READY' if you receive this."}],
            max_tokens=20
        )
        print(f"SUCCESS!")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"FAILURE!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_mistral())
