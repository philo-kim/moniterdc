"""
Cleanup Low Quality Patterns (Phase 2 Filtering)

Periodic script to validate and remove low-quality patterns using Claude.

Usage:
    python3 scripts/cleanup_low_quality_patterns.py [worldview_id]

If worldview_id is not provided, cleans up all worldviews.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.analyzers import PatternManager
from engines.utils.supabase_client import get_supabase


def main():
    pm = PatternManager()
    supabase = get_supabase()

    # Get worldview ID from args or process all
    if len(sys.argv) > 1:
        worldview_ids = [sys.argv[1]]
    else:
        # Get all worldviews
        result = supabase.table('worldviews').select('id, title').eq('archived', False).execute()
        worldview_ids = [wv['id'] for wv in result.data]
        print(f"Processing {len(worldview_ids)} worldviews\n")

    total_stats = {'checked': 0, 'removed': 0}

    for wv_id in worldview_ids:
        # Get worldview title
        wv = supabase.table('worldviews').select('title').eq('id', wv_id).single().execute()
        title = wv.data['title'] if wv.data else wv_id

        print(f"\n{'='*80}")
        print(f"Cleaning up: {title}")
        print(f"{'='*80}\n")

        # Get weak pattern count before cleanup
        before = supabase.table('worldview_patterns').select('id', count='exact').eq('worldview_id', wv_id).eq('layer', 'surface').lt('strength', 3.0).in_('status', ['active', 'fading']).execute()

        before_count = before.count if before.count else 0

        print(f"Weak patterns (strength < 3.0): {before_count}")

        if before_count == 0:
            print("No weak patterns to check.\n")
            continue

        # Run cleanup
        stats = pm.cleanup_low_quality_patterns(wv_id, strength_threshold=3.0)

        print(f"\nResults:")
        print(f"  Checked: {stats['checked']}")
        print(f"  Removed: {stats['removed']}")

        if stats['checked'] > 0:
            removal_rate = stats['removed'] / stats['checked'] * 100
            print(f"  Removal rate: {removal_rate:.1f}%")

        total_stats['checked'] += stats['checked']
        total_stats['removed'] += stats['removed']

        # Cleanup dead patterns
        removed = pm.cleanup_dead_patterns(wv_id)
        print(f"  Dead patterns cleaned up: {removed}")

    # Summary
    print(f"\n{'='*80}")
    print(f"Total Summary")
    print(f"{'='*80}\n")

    print(f"Total patterns checked: {total_stats['checked']}")
    print(f"Total patterns removed: {total_stats['removed']}")

    if total_stats['checked'] > 0:
        total_removal_rate = total_stats['removed'] / total_stats['checked'] * 100
        print(f"Overall removal rate: {total_removal_rate:.1f}%")

    print("\nCleanup complete.\n")


if __name__ == '__main__':
    main()
