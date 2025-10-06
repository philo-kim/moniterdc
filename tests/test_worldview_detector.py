#!/usr/bin/env python3
"""
Test Worldview Detector
"""

import asyncio
from engines.analyzers import WorldviewDetector
from engines.utils.supabase_client import get_supabase

async def test_worldview_detector():
    print("=" * 70)
    print("🧪 Testing Worldview Detector")
    print("=" * 70)
    print()

    detector = WorldviewDetector()
    supabase = get_supabase()

    # Check current state
    print("📊 Current Database State:")

    content_count = supabase.table('contents').select('id', count='exact').execute()
    perception_count = supabase.table('perceptions').select('id', count='exact').execute()
    connection_count = supabase.table('perception_connections').select('id', count='exact').execute()

    print(f"  Contents: {content_count.count}")
    print(f"  Perceptions: {perception_count.count}")
    print(f"  Connections: {connection_count.count}")
    print()

    # Run worldview detection
    print("=" * 70)
    print("🔍 Detecting Worldviews from Perception Clusters...")
    print("=" * 70)
    print()

    worldview_ids = await detector.detect_worldviews()

    print(f"\n✅ Detection Complete!")
    print(f"  Worldviews detected: {len(worldview_ids)}")
    print()

    if not worldview_ids:
        print("ℹ️  No worldviews detected. This could mean:")
        print("   - Not enough perceptions (need at least 3)")
        print("   - Perceptions are not connected")
        print("   - Connection strengths are too low")
        return

    # Display detected worldviews
    print("=" * 70)
    print("📋 Detected Worldviews:")
    print("=" * 70)
    print()

    for i, worldview_id in enumerate(worldview_ids, 1):
        response = supabase.table('worldviews').select('*').eq('id', str(worldview_id)).execute()

        if response.data:
            w = response.data[0]
            print(f"{i}. {w['title']}")
            print(f"   Frame: {w['frame']}")
            print(f"   Subject: {w['core_subject']}")
            print(f"   Attributes: {', '.join(w['core_attributes'])}")
            print(f"   Valence: {w['overall_valence']}")
            print(f"   Perceptions: {w['total_perceptions']}")
            print()
            print(f"   💪 Strengths:")
            print(f"      Cognitive: {w['strength_cognitive']:.2f}")
            print(f"      Temporal: {w['strength_temporal']:.2f}")
            print(f"      Social: {w['strength_social']:.2f}")
            print(f"      Structural: {w['strength_structural']:.2f}")
            print(f"      Overall: {w['strength_overall']:.2f}")
            print()

    # Get stats
    print("=" * 70)
    print("📊 Worldview Statistics:")
    print("=" * 70)
    print()

    stats = await detector.get_worldview_stats()
    for key, value in stats.items():
        if key != 'by_subject':
            print(f"  {key}: {value}")

    if 'by_subject' in stats:
        print(f"\n  By Subject:")
        for subject, count in stats['by_subject'].items():
            print(f"    {subject}: {count}")

if __name__ == '__main__':
    asyncio.run(test_worldview_detector())
