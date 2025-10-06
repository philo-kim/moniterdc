#!/usr/bin/env python3
"""
Complete System Demo

Demonstrates the full Worldview Deconstruction Engine workflow
"""

import asyncio
from engines.utils.supabase_client import get_supabase
from engines.deconstructors import DeconstructionEngine

async def main():
    print()
    print("=" * 80)
    print("🎯 WORLDVIEW DECONSTRUCTION ENGINE - LIVE DEMO")
    print("=" * 80)
    print()
    print("시스템 아키텍처:")
    print()
    print("  Layer 1: REALITY      → Contents (source-independent storage)")
    print("  Layer 2: PERCEPTION   → Perceptions + Embeddings + Connections")
    print("  Layer 3: WORLDVIEW    → Detected Patterns + Mechanisms")
    print("  Layer 4: DECONSTRUCT  → Flaws + Counter-Narratives + Action Guide")
    print()
    print("=" * 80)
    print()

    supabase = get_supabase()

    # Database stats
    print("📊 Current System State:")
    print()

    contents_count = supabase.table('contents').select('id', count='exact').execute().count
    perceptions_count = supabase.table('perceptions').select('id', count='exact').execute().count
    connections_count = supabase.table('perception_connections').select('id', count='exact').execute().count
    worldviews_count = supabase.table('worldviews').select('id', count='exact').execute().count

    print(f"  📄 Contents:     {contents_count:4d} (DC Gallery posts)")
    print(f"  🧠 Perceptions:  {perceptions_count:4d} (extracted impressions)")
    print(f"  🔗 Connections:  {connections_count:5d} (temporal, thematic, semantic)")
    print(f"  🌍 Worldviews:   {worldviews_count:4d} (detected patterns)")
    print()
    print("=" * 80)
    print()

    # Get worldviews
    response = supabase.table('worldviews').select('*').execute()
    worldviews = response.data

    print(f"🌍 Detected Worldviews ({len(worldviews)}):")
    print()

    for i, wv in enumerate(worldviews, 1):
        print(f"  {i}. {wv['title']}")
        print(f"     📐 Frame: {wv['frame']}")
        print(f"     🎯 Subject: {wv['core_subject']}")
        print(f"     🏷️  Attributes: {', '.join(wv['core_attributes'][:3])}")
        print(f"     💪 Strength: {wv['strength_overall']:.2f} ({wv.get('trend', 'N/A')})")
        print(f"     📊 Data: {wv['total_perceptions']} perceptions, {wv['total_contents']} contents")
        print()

    print("=" * 80)
    print()

    # Select target worldview
    target_wv = None
    for wv in worldviews:
        if wv.get('deconstruction'):
            target_wv = wv
            break

    if not target_wv:
        print("⚠️  No worldview with deconstruction found. Generating one...")
        target_wv = worldviews[0]
        engine = DeconstructionEngine()
        await engine.deconstruct(target_wv['id'], save_to_db=True)

        # Refresh
        response = supabase.table('worldviews').select('*').eq('id', target_wv['id']).execute()
        target_wv = response.data[0]

    print(f"🔬 DECONSTRUCTION ANALYSIS: {target_wv['title']}")
    print("=" * 80)
    print()

    deconstruction = target_wv['deconstruction']

    # Flaws
    print("🔍 STRUCTURAL FLAWS DETECTED:")
    print()
    flaws = deconstruction.get('flaws', [])
    for i, flaw in enumerate(flaws, 1):
        print(f"  {i}. {flaw.get('name', flaw.get('type'))}")
        print(f"     ├─ 설명: {flaw.get('description', '')[:70]}...")
        if flaw.get('severity'):
            print(f"     ├─ 심각도: {flaw.get('severity')}")
        if flaw.get('counter'):
            print(f"     └─ 대응: {flaw.get('counter')[:70]}...")
        print()

    print("=" * 80)
    print()

    # Counter-narrative
    print("💭 ALTERNATIVE NARRATIVE:")
    print()
    narrative = deconstruction.get('counter_narrative', '')
    for line in narrative.split('\n'):
        if line.strip():
            print(f"  {line}")
    print()

    print("=" * 80)
    print()

    # Rebuttals
    print("🎯 KEY REBUTTAL POINTS:")
    print()
    rebuttals = deconstruction.get('key_rebuttals', [])
    for i, rebuttal in enumerate(rebuttals, 1):
        print(f"  {i}. {rebuttal}")
    print()

    print("=" * 80)
    print()

    # Suggested response
    print("📝 READY-TO-USE RESPONSE:")
    print()
    response_text = deconstruction.get('suggested_response', '')
    print(f'  "{response_text}"')
    print()

    print("=" * 80)
    print()

    # Action guide
    print("📚 4-STEP ACTION GUIDE:")
    print()
    action_guide = deconstruction.get('action_guide', {})
    for step_key in ['step_1', 'step_2', 'step_3', 'step_4']:
        step = action_guide.get(step_key, {})
        if step:
            print(f"  {step_key.upper()}: {step.get('title', '')}")
            print(f"  ├─ {step.get('description', '')}")
            print(f"  └─ 예시: {step.get('example', '')}")
            print()

    print("=" * 80)
    print()
    print("✅ SYSTEM FULLY OPERATIONAL")
    print()
    print("🌐 Dashboard:  http://localhost:3001")
    print("📡 API:        http://localhost:3001/api/worldviews")
    print()
    print("Next Steps:")
    print("  1. Open dashboard in browser to see WorldviewMap")
    print("  2. Use API to integrate with other systems")
    print("  3. Run batch deconstruction: python3 scripts/generate_all_deconstructions.py")
    print()
    print("=" * 80)
    print()

if __name__ == '__main__':
    asyncio.run(main())
