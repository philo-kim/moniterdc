#!/usr/bin/env python3
"""
Test Deconstruction Engine

Tests complete deconstruction workflow:
1. FlawDetector
2. CounterNarrativeGenerator
3. DeconstructionEngine
"""

import asyncio
from uuid import UUID
from engines.deconstructors import FlawDetector, CounterNarrativeGenerator, DeconstructionEngine
from engines.utils.supabase_client import get_supabase

async def test_deconstruction_engine():
    """Test complete deconstruction workflow"""

    print("=" * 70)
    print("🧪 Testing Deconstruction Engine (Phase 3)")
    print("=" * 70)
    print()

    supabase = get_supabase()
    engine = DeconstructionEngine()

    # 1. Get a worldview to test
    print("📋 Step 1: Getting worldview for testing...")
    response = supabase.table('worldviews')\
        .select('*')\
        .gt('total_perceptions', 5)\
        .limit(1)\
        .execute()

    if not response.data:
        print("❌ No worldviews found with enough perceptions")
        return

    worldview = response.data[0]
    worldview_id = worldview['id']

    print(f"✅ Testing with worldview: {worldview['title']}")
    print(f"   ID: {worldview_id}")
    print(f"   Perceptions: {worldview['total_perceptions']}")
    print(f"   Current deconstruction: {'Yes' if worldview.get('deconstruction') else 'No'}")
    print()

    # 2. Test FlawDetector
    print("📋 Step 2: Testing FlawDetector...")
    flaw_detector = FlawDetector()

    flaws = await flaw_detector.analyze_worldview_flaws(worldview_id)

    if flaws:
        print(f"✅ Detected {len(flaws)} structural flaws:")
        for i, flaw in enumerate(flaws[:5], 1):
            print(f"   {i}. {flaw.get('name', flaw.get('type'))}: {flaw.get('description', '')[:80]}")
    else:
        print("⚠️  No flaws detected")

    print()

    # 3. Test CounterNarrativeGenerator
    print("📋 Step 3: Testing CounterNarrativeGenerator...")
    counter_gen = CounterNarrativeGenerator()

    counter_narrative = await counter_gen.generate_for_worldview(worldview_id)

    if counter_narrative:
        print("✅ Generated counter-narrative:")
        print(f"   Narrative length: {len(counter_narrative.get('counter_narrative', ''))} chars")
        print(f"   Rebuttals: {len(counter_narrative.get('key_rebuttals', []))}")
        print(f"   Suggested response: {counter_narrative.get('suggested_response', '')[:100]}...")
        print(f"   Evidence needed: {len(counter_narrative.get('evidence_needed', []))}")
        print(f"   Action guide steps: {len(counter_narrative.get('action_guide', {}))}")
    else:
        print("⚠️  Failed to generate counter-narrative")

    print()

    # 4. Test DeconstructionEngine (full workflow)
    print("📋 Step 4: Testing complete DeconstructionEngine...")
    deconstruction = await engine.deconstruct(worldview_id, save_to_db=True)

    if deconstruction:
        print("✅ Complete deconstruction generated:")
        print(f"   Flaws: {len(deconstruction.get('flaws', []))}")
        print(f"   Counter-narrative: {len(deconstruction.get('counter_narrative', ''))} chars")
        print(f"   Key rebuttals: {len(deconstruction.get('key_rebuttals', []))}")
        print(f"   Suggested response: {len(deconstruction.get('suggested_response', ''))} chars")
        print(f"   Evidence needed: {len(deconstruction.get('evidence_needed', []))}")
        print(f"   Generated at: {deconstruction.get('generated_at')}")
    else:
        print("❌ Failed to generate deconstruction")

    print()

    # 5. Verify saved to database
    print("📋 Step 5: Verifying database save...")
    response = supabase.table('worldviews')\
        .select('deconstruction')\
        .eq('id', worldview_id)\
        .execute()

    if response.data and response.data[0].get('deconstruction'):
        saved_deconstruction = response.data[0]['deconstruction']
        print("✅ Deconstruction saved to database:")
        print(f"   Flaws count: {len(saved_deconstruction.get('flaws', []))}")
        print(f"   Has counter-narrative: {bool(saved_deconstruction.get('counter_narrative'))}")
        print(f"   Has rebuttals: {bool(saved_deconstruction.get('key_rebuttals'))}")
    else:
        print("⚠️  Deconstruction not found in database")

    print()

    # 6. Display sample output
    if deconstruction:
        print("📋 Step 6: Sample Deconstruction Output")
        print("-" * 70)
        print()
        print("🔍 Detected Flaws:")
        for i, flaw in enumerate(deconstruction.get('flaws', [])[:3], 1):
            print(f"\n{i}. {flaw.get('name', flaw.get('type'))}")
            print(f"   {flaw.get('description', '')}")
            if flaw.get('counter'):
                print(f"   → {flaw.get('counter')}")

        print()
        print("💡 Counter-Narrative:")
        print(f"{deconstruction.get('counter_narrative', '')[:300]}...")

        print()
        print("🎯 Key Rebuttals:")
        for i, rebuttal in enumerate(deconstruction.get('key_rebuttals', [])[:3], 1):
            print(f"{i}. {rebuttal}")

        print()
        print("📝 Suggested Response:")
        print(f'"{deconstruction.get("suggested_response", "")}"')

    print()
    print("=" * 70)
    print("✅ Deconstruction Engine Test Complete!")
    print("=" * 70)

if __name__ == '__main__':
    asyncio.run(test_deconstruction_engine())
