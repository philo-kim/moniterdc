#!/usr/bin/env python3
"""
Test Perception Extractor
"""

import asyncio
from uuid import UUID
from engines.extractors import PerceptionExtractor
from engines.utils.supabase_client import get_supabase

async def test_perception_extractor():
    print("🧪 Testing Perception Extractor...\n")

    extractor = PerceptionExtractor()
    supabase = get_supabase()

    # Get a recent content item
    response = supabase.table('contents').select('id, title, body').order('created_at', desc=True).limit(1).execute()

    if not response.data:
        print("❌ No contents found in database")
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

    if not perception_ids:
        print("❌ No perceptions extracted")
        return

    print(f"\n✅ Extracted {len(perception_ids)} perceptions\n")

    # Fetch and display perceptions
    print("📋 Perceptions:")
    for i, perception_id in enumerate(perception_ids, 1):
        response = supabase.table('perceptions').select('*').eq('id', str(perception_id)).execute()

        if response.data:
            p = response.data[0]
            print(f"\n  {i}. Perception {perception_id}")
            print(f"     Subject: {p['perceived_subject']}")
            print(f"     Attribute: {p['perceived_attribute']}")
            print(f"     Valence: {p['perceived_valence']}")
            print(f"     Claims: {p['claims']}")
            print(f"     Keywords: {p['keywords']}")
            print(f"     Emotions: {p['emotions']}")
            print(f"     Credibility: {p['credibility']}")
            print(f"     Confidence: {p['confidence']}")

if __name__ == '__main__':
    asyncio.run(test_perception_extractor())
