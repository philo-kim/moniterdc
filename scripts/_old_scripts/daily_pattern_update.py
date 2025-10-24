"""
Daily Pattern Update - Cron Job

Runs every day at midnight to:
1. Process yesterday's new contents
2. Integrate perceptions into worldview patterns
3. Decay old patterns
4. Clean up dead patterns

Usage:
    python3 scripts/daily_pattern_update.py

Cron:
    0 0 * * * cd /path/to/moniterdc && python3 scripts/daily_pattern_update.py
"""

import sys
import os
from datetime import datetime, timedelta
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.analyzers import (
    LayeredPerceptionExtractor,
    ReasoningStructureExtractor,
    MechanismMatcher,
    PatternManager
)
from engines.utils.supabase_client import get_supabase


async def main():
    print(f"\n{'='*80}")
    print(f"Daily Pattern Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    supabase = get_supabase()
    pattern_manager = PatternManager()

    # ===== Step 1: Get yesterday's new contents =====
    print("📥 Step 1: Fetching yesterday's contents...")

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    today = datetime.now().strftime('%Y-%m-%d')

    result = supabase.table('contents').select('*').gte('created_at', yesterday).lt('created_at', today).execute()

    new_contents = result.data if result.data else []
    print(f"   Found {len(new_contents)} new contents from yesterday")

    if len(new_contents) == 0:
        print("   No new contents to process. Skipping to decay step.\n")
    else:
        # ===== Step 2: Process each content =====
        print(f"\n🔄 Step 2: Processing {len(new_contents)} contents...")

        perception_extractor = LayeredPerceptionExtractor()
        structure_extractor = ReasoningStructureExtractor()
        matcher = MechanismMatcher()

        total_integrated = 0
        total_stats = {
            'surface': {'matched': 0, 'new': 0},
            'implicit': {'matched': 0, 'new': 0},
            'deep': {'matched': 0, 'new': 0}
        }

        for i, content in enumerate(new_contents, 1):
            print(f"\n   [{i}/{len(new_contents)}] Processing: {content['title'][:50]}...")

            try:
                # Extract 3 layers
                perception_data = await perception_extractor.extract(content)

                # Extract structure (mechanisms, actor, logic_chain)
                structure_data = await structure_extractor.extract(content)

                # Create perception
                perception = supabase.table('layered_perceptions').insert({
                    'content_id': content['id'],
                    'explicit_claims': perception_data['explicit_claims'],
                    'implicit_assumptions': perception_data['implicit_assumptions'],
                    'deep_beliefs': perception_data['deep_beliefs'],
                    'mechanisms': structure_data.get('mechanisms', []),
                    'actor': structure_data.get('actor'),
                    'logic_chain': structure_data.get('logic_chain', [])
                }).execute()

                perception_id = perception.data[0]['id']

                # Match to worldviews
                links = matcher.match_and_link({
                    'id': perception_id,
                    **perception_data,
                    **structure_data
                })

                print(f"      ✓ Created perception, matched to {len(links)} worldviews")

                # Integrate into pattern pools
                for link in links:
                    worldview_id = link['worldview_id']

                    stats = pattern_manager.integrate_perception(
                        worldview_id,
                        {
                            **perception_data,
                            **structure_data
                        }
                    )

                    # Accumulate stats
                    for layer in ['surface', 'implicit', 'deep']:
                        total_stats[layer]['matched'] += stats[layer]['matched']
                        total_stats[layer]['new'] += stats[layer]['new']

                    total_integrated += 1

            except Exception as e:
                print(f"      ✗ Error: {str(e)}")
                continue

        print(f"\n   Summary:")
        print(f"   - Perceptions created: {len(new_contents)}")
        print(f"   - Worldview integrations: {total_integrated}")
        print(f"\n   Pattern Statistics:")
        for layer in ['surface', 'implicit', 'deep']:
            matched = total_stats[layer]['matched']
            new = total_stats[layer]['new']
            total = matched + new
            match_rate = (matched / total * 100) if total > 0 else 0
            print(f"      {layer:8s}: {matched:3d} matched ({match_rate:5.1f}%), {new:3d} new")

    # ===== Step 3: Decay patterns =====
    print(f"\n⏳ Step 3: Applying natural decay to patterns...")

    decay_stats = pattern_manager.decay_patterns()

    print(f"   Decay Statistics:")
    for layer in ['surface', 'implicit', 'deep']:
        total = decay_stats[layer]['total']
        fading = decay_stats[layer]['fading']
        dead = decay_stats[layer]['dead']
        print(f"      {layer:8s}: {total:4d} total, {fading:3d} fading, {dead:3d} dead")

    # ===== Step 4: Clean up dead patterns =====
    print(f"\n🗑️  Step 4: Cleaning up dead patterns...")

    removed_count = pattern_manager.cleanup_dead_patterns()
    print(f"   Removed {removed_count} dead patterns")

    # ===== Complete =====
    print(f"\n{'='*80}")
    print(f"✅ Daily update complete!")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    asyncio.run(main())
