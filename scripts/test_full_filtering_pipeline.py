"""
Test Full 2-Stage Filtering Pipeline

Tests the complete pattern quality filtering system:
1. Phase 1: Enhanced fast filter (rule-based)
2. Pattern creation and usage
3. Phase 2: Claude validation of weak patterns
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.analyzers import PatternManager
from engines.utils.supabase_client import get_supabase


def main():
    print("\n" + "="*80)
    print("Full 2-Stage Filtering Pipeline Test")
    print("="*80 + "\n")

    pm = PatternManager()
    supabase = get_supabase()

    wv_id = '72494546-0243-43f8-91d5-3a6c24791951'

    # Clean up existing patterns
    print("Cleaning up existing patterns...")
    supabase.table('worldview_patterns').delete().eq('worldview_id', wv_id).execute()
    print("Done.\n")

    # Get perceptions (first 100 for faster testing)
    print("Loading perceptions...")
    result = supabase.table('layered_perceptions').select(
        'explicit_claims, implicit_assumptions, deep_beliefs'
    ).limit(100).execute()

    perceptions = result.data
    print(f"Loaded {len(perceptions)} perceptions.\n")

    # ====================
    # Phase 1: Create patterns with fast filter
    # ====================
    print("="*80)
    print("Phase 1: Creating patterns with enhanced fast filter")
    print("="*80 + "\n")

    start_time = time.time()

    total_stats = {
        'surface': {'new': 0, 'matched': 0, 'filtered': 0},
        'implicit': {'new': 0, 'matched': 0},
        'deep': {'new': 0, 'matched': 0}
    }

    for i, p in enumerate(perceptions, 1):
        if i % 25 == 0:
            print(f"Processing {i}/{len(perceptions)}...")

        stats = pm.integrate_perception(wv_id, p)

        for layer in ['surface', 'implicit', 'deep']:
            total_stats[layer]['new'] += stats[layer]['new']
            total_stats[layer]['matched'] += stats[layer]['matched']

    phase1_time = time.time() - start_time

    print(f"\nPhase 1 completed in {phase1_time:.1f}s\n")

    # Calculate filtering stats
    surface_total_items = sum(len(p.get('explicit_claims', [])) for p in perceptions)
    surface_created = total_stats['surface']['new'] + total_stats['surface']['matched']
    surface_filtered = surface_total_items - surface_created

    print(f"Surface Layer Stats:")
    print(f"  Total items: {surface_total_items}")
    print(f"  Created/matched: {surface_created}")
    print(f"  Filtered by Phase 1: {surface_filtered} ({surface_filtered/surface_total_items*100:.1f}%)\n")

    # Get pattern counts
    surface_patterns = pm.get_active_patterns(wv_id, layer='surface')
    print(f"  Unique patterns created: {len(surface_patterns)}")

    # Count weak patterns
    weak_patterns = [p for p in surface_patterns if p['strength'] < 3.0]
    print(f"  Weak patterns (strength < 3.0): {len(weak_patterns)} ({len(weak_patterns)/len(surface_patterns)*100:.1f}%)\n")

    # Show top patterns
    top_patterns = sorted(surface_patterns, key=lambda x: x['strength'], reverse=True)[:5]
    print("  Top 5 patterns by strength:")
    for p in top_patterns:
        print(f"    {p['strength']:.1f} ({p['appearance_count']}회): {p['text'][:60]}...")

    print("\n")

    # ====================
    # Phase 2: Claude validation
    # ====================
    print("="*80)
    print("Phase 2: Claude validation of weak patterns")
    print("="*80 + "\n")

    if len(weak_patterns) == 0:
        print("No weak patterns to validate.\n")
    else:
        print(f"Validating {len(weak_patterns)} weak patterns with Claude...")

        start_time = time.time()
        cleanup_stats = pm.cleanup_low_quality_patterns(wv_id, strength_threshold=3.0)
        phase2_time = time.time() - start_time

        print(f"\nPhase 2 completed in {phase2_time:.1f}s\n")

        print(f"Results:")
        print(f"  Patterns checked: {cleanup_stats['checked']}")
        print(f"  Patterns removed: {cleanup_stats['removed']}")

        if cleanup_stats['checked'] > 0:
            removal_rate = cleanup_stats['removed'] / cleanup_stats['checked'] * 100
            print(f"  Removal rate: {removal_rate:.1f}%\n")

        # Cleanup dead patterns
        removed = pm.cleanup_dead_patterns(wv_id)
        print(f"  Dead patterns cleaned up: {removed}\n")

    # ====================
    # Final stats
    # ====================
    print("="*80)
    print("Final Statistics")
    print("="*80 + "\n")

    final_surface = pm.get_active_patterns(wv_id, layer='surface')

    print(f"Surface Layer:")
    print(f"  Total items processed: {surface_total_items}")
    print(f"  Phase 1 filtered: {surface_filtered} ({surface_filtered/surface_total_items*100:.1f}%)")

    if len(weak_patterns) > 0 and cleanup_stats.get('removed', 0) > 0:
        print(f"  Phase 2 removed: {cleanup_stats['removed']} ({cleanup_stats['removed']/surface_total_items*100:.1f}%)")

        total_filtered = surface_filtered + cleanup_stats['removed']
        print(f"  Total filtered: {total_filtered} ({total_filtered/surface_total_items*100:.1f}%)")

    print(f"  Final unique patterns: {len(final_surface)}")

    # Show final top patterns
    final_top = sorted(final_surface, key=lambda x: x['strength'], reverse=True)[:10]
    print(f"\n  Top 10 patterns after filtering:")
    for i, p in enumerate(final_top, 1):
        print(f"    {i}. {p['strength']:.1f} ({p['appearance_count']}회): {p['text']}")

    print("\n" + "="*80)
    print("Test Complete")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
