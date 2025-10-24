#!/usr/bin/env python3
"""
Test Content Collector
"""

import asyncio
import logging
from engines.collectors.content_collector import ContentCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_collector():
    print("🧪 Testing Content Collector...\n")

    collector = ContentCollector()

    # Test: Collect 5 posts from DC gallery
    print("📥 Collecting 5 posts from DC gallery (uspolitics)...")

    content_ids = await collector.collect(
        source_type='dc_gallery',
        gallery='uspolitics',
        limit=5
    )

    print(f"\n✅ Collected {len(content_ids)} contents")

    if content_ids:
        print("\n📋 Content IDs:")
        for content_id in content_ids:
            print(f"  • {content_id}")

        # Display first content
        from engines.utils.supabase_client import get_supabase
        supabase = get_supabase()

        first_content = supabase.table('contents')\
            .select('*')\
            .eq('id', content_ids[0])\
            .single()\
            .execute()

        print(f"\n📄 First content:")
        print(f"  Title: {first_content.data['title']}")
        print(f"  URL: {first_content.data['source_url']}")
        print(f"  Body length: {len(first_content.data['body'])} chars")
        print(f"  Credibility: {first_content.data['base_credibility']}")

if __name__ == '__main__':
    asyncio.run(test_collector())