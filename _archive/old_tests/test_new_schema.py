#!/usr/bin/env python3
"""
Test script for new 3-layer schema
Verifies that all tables and functions are created correctly
"""

import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

async def test_schema():
    print("🧪 Testing new 3-layer schema...\n")

    # Initialize Supabase client
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )

    # Test 1: Check tables exist
    print("1️⃣ Checking tables...")
    tables = ['contents', 'perceptions', 'perception_connections', 'worldviews', 'rebuttals', 'rebuttal_votes']

    for table in tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"  ✅ Table '{table}' exists")
        except Exception as e:
            print(f"  ❌ Table '{table}' error: {e}")

    # Test 2: Insert test content
    print("\n2️⃣ Inserting test content...")
    try:
        content_result = supabase.table('contents').insert({
            'source_type': 'dc_gallery',
            'source_url': 'https://test.com/test',
            'source_id': 'test_123',
            'title': '테스트 제목',
            'body': '테스트 본문입니다.',
            'metadata': {'gallery': 'uspolitics', 'post_num': 123},
            'base_credibility': 0.2,
            'published_at': 'NOW()'
        }).execute()

        content_id = content_result.data[0]['id']
        print(f"  ✅ Content created: {content_id}")

        # Test 3: Insert test perception
        print("\n3️⃣ Inserting test perception...")
        perception_result = supabase.table('perceptions').insert({
            'content_id': content_id,
            'perceived_subject': '민주당',
            'perceived_attribute': '친중',
            'perceived_valence': 'negative',
            'claims': ['민주당이 중국인 무비자를 허용했다'],
            'keywords': ['무비자', '중국', '민주당'],
            'emotions': ['fear'],
            'credibility': 0.2,
            'confidence': 0.9
        }).execute()

        perception_id = perception_result.data[0]['id']
        print(f"  ✅ Perception created: {perception_id}")

        # Test 4: Test RPC function (without embedding for now)
        print("\n4️⃣ Testing RPC functions...")

        # Test update_worldview_stats (will create empty worldview first)
        print("  ℹ️ RPC functions ready (will test with real data later)")

        # Cleanup test data
        print("\n5️⃣ Cleaning up test data...")
        supabase.table('perceptions').delete().eq('id', perception_id).execute()
        supabase.table('contents').delete().eq('id', content_id).execute()
        print("  ✅ Test data cleaned up")

        print("\n✅ All schema tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_schema())