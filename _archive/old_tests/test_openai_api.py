#!/usr/bin/env python3
"""
Test OpenAI API connection and quota
"""

import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def test_openai():
    print("🧪 Testing OpenAI API...\n")

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return

    print(f"✅ API Key found: {api_key[:20]}...\n")

    client = AsyncOpenAI(api_key=api_key)

    # Test 1: Simple completion
    print("📝 Test 1: GPT-4o-mini completion...")
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say 'Hello' in one word"}
            ],
            max_tokens=10
        )
        print(f"✅ Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return

    # Test 2: Embedding
    print("\n🔢 Test 2: Embedding generation...")
    try:
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input="테스트",
            dimensions=1536
        )
        embedding = response.data[0].embedding
        print(f"✅ Embedding generated: {len(embedding)} dimensions")
        print(f"   Sample: [{embedding[0]:.4f}, {embedding[1]:.4f}, {embedding[2]:.4f}, ...]")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return

    # Test 3: JSON mode
    print("\n📋 Test 3: JSON mode...")
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": "Return a JSON with a field 'status' set to 'ok'"}
            ],
            response_format={"type": "json_object"},
            max_tokens=20
        )
        print(f"✅ JSON Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return

    print("\n✅ All OpenAI API tests passed!")

if __name__ == '__main__':
    asyncio.run(test_openai())
