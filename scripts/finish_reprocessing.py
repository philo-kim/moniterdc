#!/usr/bin/env python3
"""
Finish Reprocessing - Steps 5-7 only

Step 4 is already complete (455/456 perceptions created).
This script only runs:
- Step 5: Worldview discovery
- Step 6: Perception-worldview matching
- Step 7: Update counts
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.analyzers.worldview_evolution_engine import WorldviewEvolutionEngine
from engines.analyzers.mechanism_matcher import MechanismMatcher
from engines.utils.supabase_client import get_supabase


async def main():
    supabase = get_supabase()

    print("=" * 80)
    print("Finishing Reprocessing - Steps 5-7")
    print("=" * 80)
    print()
    sys.stdout.flush()

    # Step 5: Rediscover worldviews with Claude Data-Driven
    print("🔍 Step 5: Rediscovering worldviews with Claude Data-Driven...")
    sys.stdout.flush()

    evolution_engine = WorldviewEvolutionEngine()

    # Fetch 200 recent perceptions
    recent_perceptions = supabase.table('layered_perceptions').select('*').order('created_at', desc=True).limit(200).execute().data
    print(f"   Analyzing {len(recent_perceptions)} recent perceptions...")
    sys.stdout.flush()

    worldviews = await evolution_engine._consolidate_worldviews(recent_perceptions)

    # Save new worldviews
    new_worldview_ids = []
    for wv in worldviews:
        # Build frame structure from individual components
        frame = {
            'actor': wv.get('actor', {}),
            'core_mechanisms': wv.get('core_mechanisms', []),
            'logic_pattern': wv.get('logic_pattern', {}),
            'statistical_basis': wv.get('statistical_basis', {})
        }

        result = supabase.table('worldviews').insert({
            'title': wv['title'],
            'description': wv.get('description', ''),
            'frame': frame,
            'core_subject': wv.get('actor', {}).get('subject', ''),
            'core_attributes': wv.get('core_mechanisms', []),
            'version': 2,
            'archived': False,
            'total_perceptions': 0,
            'overall_valence': 0.0  # Default neutral valence
        }).execute()

        new_worldview_ids.append(result.data[0]['id'])
        print(f"   ✅ Created: {wv['title']}")
        sys.stdout.flush()

    print(f"   ✅ Created {len(worldviews)} new worldviews")
    print()
    sys.stdout.flush()

    # Step 6: Re-link perceptions to worldviews with Adaptive Matching
    print("🔗 Step 6: Linking perceptions to worldviews with Adaptive Matching...")
    sys.stdout.flush()

    matcher = MechanismMatcher()

    all_perceptions = supabase.table('layered_perceptions').select('*').execute().data
    active_worldviews = supabase.table('worldviews').select('*').eq('archived', False).execute().data

    print(f"   Matching {len(all_perceptions)} perceptions to {len(active_worldviews)} worldviews...")
    sys.stdout.flush()

    # Use match_all_perceptions method
    total_links = await matcher.match_all_perceptions(threshold=0.6)

    print(f"   ✅ Created {total_links} perception-worldview links")
    print()
    sys.stdout.flush()

    # Step 7: Update worldview perception counts
    print("📊 Step 7: Updating worldview perception counts...")
    sys.stdout.flush()

    for worldview in active_worldviews:
        links = supabase.table('perception_worldview_links').select('id', count='exact').eq('worldview_id', worldview['id']).execute()
        count = links.count

        supabase.table('worldviews').update({
            'total_perceptions': count
        }).eq('id', worldview['id']).execute()

        print(f"   {worldview['title']}: {count} perceptions")
        sys.stdout.flush()

    print(f"   ✅ Updated perception counts for {len(active_worldviews)} worldviews")
    print()
    sys.stdout.flush()

    # Final report
    print("=" * 80)
    print("🎉 Reprocessing COMPLETE")
    print("=" * 80)
    print()
    print(f"📊 Final Statistics:")
    print(f"   Perceptions: {len(all_perceptions)}")
    print(f"   New worldviews: {len(worldviews)}")
    print(f"   Total links: {total_links}")
    if len(all_perceptions) > 0:
        print(f"   Avg links per perception: {total_links/len(all_perceptions):.2f}")
    print()
    print("✅ All data has been reprocessed with Claude Sonnet 4.5!")
    print()
    sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
