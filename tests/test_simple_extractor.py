#!/usr/bin/env python3
"""
Test Simple Perception Extractor (rule-based, no API needed)
"""

import asyncio
from uuid import UUID
from engines.extractors.perception_extractor_simple import SimplePerceptionExtractor
from engines.utils.supabase_client import get_supabase

async def test_simple_extractor():
    print("🧪 Testing Simple Perception Extractor (rule-based)...\n")

    extractor = SimplePerceptionExtractor()
    supabase = get_supabase()

    # Get a recent content
    response = supabase.table('contents').select('id, title, body').order('created_at', desc=True).limit(1).execute()

    if not response.data:
        print("❌ No contents found")
        return

    content = response.data[0]
    content_id = UUID(content['id'])

    print(f"📄 Testing with content:")
    print(f"  ID: {content_id}")
    print(f"  Title: {content['title']}")
    print(f"  Body: {content['body'][:100]}...\n")

    # Extract perceptions
    print("🔍 Extracting perceptions...")
    perception_ids = await extractor.extract(content_id)

    print(f"\n✅ Extracted {len(perception_ids)} perceptions\n")

    # Display perceptions
    print("📋 Perceptions:")
    for i, pid in enumerate(perception_ids, 1):
        response = supabase.table('perceptions').select('*').eq('id', str(pid)).execute()

        if response.data:
            p = response.data[0]
            print(f"\n  {i}. Perception {pid}")
            print(f"     Subject: {p['perceived_subject']}")
            print(f"     Attribute: {p['perceived_attribute']}")
            print(f"     Valence: {p['perceived_valence']}")
            print(f"     Claims: {p['claims']}")
            print(f"     Keywords: {p['keywords']}")
            print(f"     Emotions: {p['emotions']}")

if __name__ == '__main__':
    asyncio.run(test_simple_extractor())
