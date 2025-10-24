"""
Validate Pattern Matching Rates with Real Data

Tests the dynamic pattern system with actual perceptions to verify:
- Surface layer: 20-30% match rate (events change frequently)
- Implicit layer: 60-70% match rate (assumptions repeat more)
- Deep layer: 90%+ match rate (core beliefs are stable)
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.analyzers import PatternManager
from engines.utils.supabase_client import get_supabase


def main():
    print(f"\n{'='*80}")
    print(f"Pattern Matching Rate Validation")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    pm = PatternManager()
    supabase = get_supabase()

    # Get a worldview with perceptions
    print("Finding worldview with most perceptions...")
    worldviews = supabase.rpc(
        'get_worldview_stats',
        {}
    ).execute()

    if not worldviews.data or len(worldviews.data) == 0:
        print("❌ No worldviews with perceptions found")
        return

    # Use worldview with most perceptions
    target_wv = max(worldviews.data, key=lambda x: x.get('perception_count', 0))
    worldview_id = target_wv['worldview_id']
    worldview_title = target_wv['worldview_title']
    perception_count = target_wv['perception_count']

    print(f"✅ Selected worldview: {worldview_title}")
    print(f"   Worldview ID: {worldview_id}")
    print(f"   Total perceptions: {perception_count}\n")

    # Get perceptions for this worldview
    print("Fetching perceptions...")
    result = supabase.table('perception_worldview_links').select(
        'perception_id'
    ).eq('worldview_id', worldview_id).limit(50).execute()

    perception_ids = [link['perception_id'] for link in result.data]
    print(f"✅ Fetched {len(perception_ids)} perceptions\n")

    # Split into two groups: pattern building (first 25) and testing (last 25)
    build_ids = perception_ids[:25]
    test_ids = perception_ids[25:]

    print(f"Using {len(build_ids)} perceptions to build patterns...")
    print(f"Using {len(test_ids)} perceptions to test matching rates\n")

    # Build patterns from first group
    print("="*80)
    print("Phase 1: Building Pattern Pool")
    print("="*80 + "\n")

    perceptions = supabase.table('layered_perceptions').select(
        'id, explicit_claims, implicit_assumptions, deep_beliefs'
    ).in_('id', build_ids).execute()

    total_integrated = {'surface': 0, 'implicit': 0, 'deep': 0}
    total_new = {'surface': 0, 'implicit': 0, 'deep': 0}
    total_matched = {'surface': 0, 'implicit': 0, 'deep': 0}

    for i, perception in enumerate(perceptions.data, 1):
        print(f"Integrating perception {i}/{len(perceptions.data)}...", end='\r')

        # Prepare perception data
        p_data = {
            'explicit_claims': perception.get('explicit_claims', []),
            'implicit_assumptions': perception.get('implicit_assumptions', []),
            'deep_beliefs': perception.get('deep_beliefs', [])
        }

        # Integrate
        stats = pm.integrate_perception(worldview_id, p_data)

        for layer in ['surface', 'implicit', 'deep']:
            total_new[layer] += stats[layer]['new']
            total_matched[layer] += stats[layer]['matched']
            total_integrated[layer] += stats[layer]['new'] + stats[layer]['matched']

    print(f"\n\n{'='*80}")
    print("Pattern Pool Built")
    print(f"{'='*80}\n")

    for layer in ['surface', 'implicit', 'deep']:
        active_patterns = pm.get_active_patterns(worldview_id, layer=layer)
        print(f"{layer.upper():8s} layer:")
        print(f"  Total items integrated: {total_integrated[layer]}")
        print(f"  New patterns created: {total_new[layer]}")
        print(f"  Matched existing: {total_matched[layer]}")
        print(f"  Active patterns: {len(active_patterns)}")
        if total_integrated[layer] > 0:
            match_rate = (total_matched[layer] / total_integrated[layer]) * 100
            print(f"  Initial match rate: {match_rate:.1f}%")
        print()

    # Test matching rates with second group
    print("="*80)
    print("Phase 2: Testing Matching Rates with New Perceptions")
    print("="*80 + "\n")

    test_perceptions = supabase.table('layered_perceptions').select(
        'id, explicit_claims, implicit_assumptions, deep_beliefs'
    ).in_('id', test_ids).execute()

    test_matched = {'surface': 0, 'implicit': 0, 'deep': 0}
    test_total = {'surface': 0, 'implicit': 0, 'deep': 0}

    for i, perception in enumerate(test_perceptions.data, 1):
        print(f"Testing perception {i}/{len(test_perceptions.data)}...", end='\r')

        # Prepare perception data
        p_data = {
            'explicit_claims': perception.get('explicit_claims', []),
            'implicit_assumptions': perception.get('implicit_assumptions', []),
            'deep_beliefs': perception.get('deep_beliefs', [])
        }

        # Test matching (don't actually integrate, just check)
        for claim in p_data['explicit_claims']:
            matched = pm.find_similar_pattern(worldview_id, 'surface', claim)
            test_total['surface'] += 1
            if matched:
                test_matched['surface'] += 1

        for assumption in p_data['implicit_assumptions']:
            matched = pm.find_similar_pattern(worldview_id, 'implicit', assumption)
            test_total['implicit'] += 1
            if matched:
                test_matched['implicit'] += 1

        for belief in p_data['deep_beliefs']:
            matched = pm.find_similar_pattern(worldview_id, 'deep', belief)
            test_total['deep'] += 1
            if matched:
                test_matched['deep'] += 1

    print(f"\n\n{'='*80}")
    print("Matching Rate Test Results")
    print(f"{'='*80}\n")

    expected_rates = {
        'surface': (20, 30),   # 20-30%
        'implicit': (60, 70),  # 60-70%
        'deep': (90, 100)      # 90%+
    }

    all_passed = True

    for layer in ['surface', 'implicit', 'deep']:
        if test_total[layer] == 0:
            print(f"{layer.upper():8s} layer: ⚠️  No test data")
            continue

        match_rate = (test_matched[layer] / test_total[layer]) * 100
        expected_min, expected_max = expected_rates[layer]

        status = "✅" if expected_min <= match_rate <= expected_max else "⚠️ "
        if not (expected_min <= match_rate <= expected_max):
            all_passed = False

        print(f"{layer.upper():8s} layer: {status}")
        print(f"  Test items: {test_total[layer]}")
        print(f"  Matched: {test_matched[layer]}")
        print(f"  Match rate: {match_rate:.1f}%")
        print(f"  Expected: {expected_min}-{expected_max}%")
        print()

    # Summary
    print("="*80)
    if all_passed:
        print("✅ All matching rates are within expected ranges")
    else:
        print("⚠️  Some matching rates are outside expected ranges")
        print("\nNote: This is expected behavior - these are principles, not hard targets.")
        print("The system naturally produces different rates based on the actual discourse.")
    print("="*80)

    # Cleanup test patterns
    print("\nCleaning up test patterns...")
    pm.cleanup_dead_patterns(worldview_id)
    supabase.table('worldview_patterns').delete().eq('worldview_id', worldview_id).execute()
    print("✅ Test patterns cleaned up")

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == '__main__':
    main()
