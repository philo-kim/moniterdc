#!/usr/bin/env python3
"""
Test Worldview Updater functionality
Tests: update_worldview, trend calculation, strength history
"""

import asyncio
from uuid import UUID
from engines.analyzers.worldview_detector import WorldviewDetector
from engines.utils.supabase_client import get_supabase

async def test_worldview_updater():
    """Test worldview update and trend calculation"""

    print("=" * 70)
    print("🧪 Testing Worldview Updater")
    print("=" * 70)
    print()

    detector = WorldviewDetector()
    supabase = get_supabase()

    # 1. Find existing worldview
    print("📋 Step 1: Finding existing worldview...")
    response = supabase.table('worldviews').select('*').limit(1).execute()

    if not response.data:
        print("❌ No worldviews found in database")
        return

    worldview = response.data[0]
    worldview_id = UUID(worldview['id'])
    print(f"✅ Found worldview: {worldview['title']}")
    print(f"   ID: {worldview_id}")
    print(f"   Perceptions: {worldview['total_perceptions']}")
    print(f"   Strength: {worldview['strength_overall']:.2f}")
    print()

    # 2. Find some new perceptions to add
    print("📋 Step 2: Finding new perceptions to add...")
    existing_perception_ids = worldview.get('perception_ids', [])

    response = supabase.table('perceptions')\
        .select('id')\
        .limit(10)\
        .execute()

    all_perceptions = [p['id'] for p in response.data]
    new_perceptions = [p for p in all_perceptions if p not in existing_perception_ids][:3]

    if not new_perceptions:
        print("⚠️  No new perceptions to add, using existing ones for testing")
        new_perceptions = all_perceptions[:3]

    print(f"✅ Found {len(new_perceptions)} perceptions to add")
    print()

    # 3. Test update_worldview
    print("📋 Step 3: Testing update_worldview()...")
    success = await detector.update_worldview(worldview_id, new_perceptions)

    if success:
        print("✅ Successfully updated worldview")

        # Check updated state
        response = supabase.table('worldviews').select('*').eq('id', str(worldview_id)).execute()
        updated = response.data[0]

        print(f"   Perceptions: {worldview['total_perceptions']} → {updated['total_perceptions']}")
        print(f"   Strength: {worldview['strength_overall']:.2f} → {updated['strength_overall']:.2f}")
        print(f"   Trend: {updated.get('trend', 'N/A')}")
    else:
        print("❌ Failed to update worldview")

    print()

    # 4. Test find_existing_worldview
    print("📋 Step 4: Testing find_existing_worldview()...")
    existing = await detector.find_existing_worldview(
        worldview['core_subject'],
        worldview['frame']
    )

    if existing:
        print(f"✅ Found existing worldview: {existing['title']}")
    else:
        print("❌ Failed to find existing worldview")

    print()

    # 5. Test strength snapshot
    print("📋 Step 5: Checking strength history...")
    response = supabase.table('worldview_strength_history')\
        .select('*')\
        .eq('worldview_id', str(worldview_id))\
        .order('recorded_at', desc=True)\
        .limit(5)\
        .execute()

    if response.data:
        print(f"✅ Found {len(response.data)} strength snapshots")
        for i, snapshot in enumerate(response.data, 1):
            print(f"   #{i}: {snapshot['recorded_at'][:19]} - Strength: {snapshot['strength_overall']:.2f}")
    else:
        print("⚠️  No strength history found")

    print()

    # 6. Test trend calculation
    print("📋 Step 6: Testing trend calculation...")
    trend = await detector.calculate_trend(worldview_id)
    print(f"✅ Calculated trend: {trend}")
    print()

    # 7. Test should_update_vs_create
    print("📋 Step 7: Testing should_update_vs_create()...")
    should_update, existing_id = await detector.should_update_vs_create(
        worldview['core_subject'],
        worldview['frame'],
        []
    )

    print(f"   Should update: {should_update}")
    print(f"   Existing ID: {existing_id}")

    if should_update and existing_id == worldview_id:
        print("✅ Correctly identified existing worldview")
    else:
        print("⚠️  Unexpected result")

    print()

    print("=" * 70)
    print("✅ Worldview Updater Test Complete!")
    print("=" * 70)

if __name__ == '__main__':
    asyncio.run(test_worldview_updater())
