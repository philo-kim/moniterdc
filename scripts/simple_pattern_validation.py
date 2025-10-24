"""
Simple Pattern System Validation

Tests pattern matching with a sample of real perceptions to demonstrate
the dynamic pattern lifecycle.
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
    print(f"Simple Pattern System Validation")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    pm = PatternManager()
    supabase = get_supabase()

    # Create a test worldview
    print("Creating test worldview...")
    test_wv = supabase.table('worldviews').insert({
        'title': '패턴 테스트용 세계관',
        'description': '동적 패턴 시스템 테스트',
        'core_subject': '테스트',
        'core_attributes': [],
        'version': 1
    }).execute()

    worldview_id = test_wv.data[0]['id']
    print(f"✅ Created test worldview: {worldview_id}\n")

    # Get sample perceptions
    print("Fetching sample perceptions...")
    perceptions = supabase.table('layered_perceptions').select(
        'id, explicit_claims, implicit_assumptions, deep_beliefs'
    ).limit(30).execute()

    print(f"✅ Fetched {len(perceptions.data)} perceptions\n")

    # Split into build (20) and test (10)
    build_perceptions = perceptions.data[:20]
    test_perceptions = perceptions.data[20:]

    # Phase 1: Build patterns
    print("="*80)
    print(f"Phase 1: Building Pattern Pool ({len(build_perceptions)} perceptions)")
    print("="*80 + "\n")

    total_stats = {
        'surface': {'new': 0, 'matched': 0},
        'implicit': {'new': 0, 'matched': 0},
        'deep': {'new': 0, 'matched': 0}
    }

    for i, p in enumerate(build_perceptions, 1):
        print(f"Processing {i}/{len(build_perceptions)}...", end='\r')

        p_data = {
            'explicit_claims': p.get('explicit_claims', []),
            'implicit_assumptions': p.get('implicit_assumptions', []),
            'deep_beliefs': p.get('deep_beliefs', [])
        }

        stats = pm.integrate_perception(worldview_id, p_data)

        for layer in ['surface', 'implicit', 'deep']:
            total_stats[layer]['new'] += stats[layer]['new']
            total_stats[layer]['matched'] += stats[layer]['matched']

    print("\n\n" + "="*80)
    print("Pattern Pool Summary")
    print("="*80 + "\n")

    for layer in ['surface', 'implicit', 'deep']:
        patterns = pm.get_active_patterns(worldview_id, layer=layer)
        total = total_stats[layer]['new'] + total_stats[layer]['matched']

        print(f"{layer.upper():8s} layer:")
        print(f"  Items processed: {total}")
        print(f"  New patterns: {total_stats[layer]['new']}")
        print(f"  Matched existing: {total_stats[layer]['matched']}")
        print(f"  Total unique patterns: {len(patterns)}")

        if total > 0:
            match_rate = (total_stats[layer]['matched'] / total) * 100
            print(f"  Build phase match rate: {match_rate:.1f}%")

        # Show top 3 patterns by strength
        if len(patterns) > 0:
            print(f"  Top patterns:")
            for p in patterns[:3]:
                print(f"    - {p['text'][:60]}... (strength: {p['strength']:.1f})")

        print()

    # Phase 2: Test with new perceptions
    print("="*80)
    print(f"Phase 2: Testing Matching Rates ({len(test_perceptions)} perceptions)")
    print("="*80 + "\n")

    test_stats = {
        'surface': {'total': 0, 'matched': 0},
        'implicit': {'total': 0, 'matched': 0},
        'deep': {'total': 0, 'matched': 0}
    }

    for i, p in enumerate(test_perceptions, 1):
        print(f"Testing {i}/{len(test_perceptions)}...", end='\r')

        # Test surface
        for claim in p.get('explicit_claims', []):
            test_stats['surface']['total'] += 1
            if pm.find_similar_pattern(worldview_id, 'surface', claim):
                test_stats['surface']['matched'] += 1

        # Test implicit
        for assumption in p.get('implicit_assumptions', []):
            test_stats['implicit']['total'] += 1
            if pm.find_similar_pattern(worldview_id, 'implicit', assumption):
                test_stats['implicit']['matched'] += 1

        # Test deep
        for belief in p.get('deep_beliefs', []):
            test_stats['deep']['total'] += 1
            if pm.find_similar_pattern(worldview_id, 'deep', belief):
                test_stats['deep']['matched'] += 1

    print("\n\n" + "="*80)
    print("Test Results")
    print("="*80 + "\n")

    for layer in ['surface', 'implicit', 'deep']:
        total = test_stats[layer]['total']
        matched = test_stats[layer]['matched']

        if total == 0:
            print(f"{layer.upper():8s} layer: No test data")
            continue

        match_rate = (matched / total) * 100

        print(f"{layer.upper():8s} layer:")
        print(f"  Test items: {total}")
        print(f"  Matched: {matched}")
        print(f"  Match rate: {match_rate:.1f}%")
        print()

    # Cleanup
    print("="*80)
    print("Cleaning up test data...")
    supabase.table('worldview_patterns').delete().eq('worldview_id', worldview_id).execute()
    supabase.table('worldviews').delete().eq('id', worldview_id).execute()
    print("✅ Cleanup complete")
    print("="*80)

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == '__main__':
    main()
