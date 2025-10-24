"""
Reprocess All Perceptions with v2.1 Filtering

Deletes all existing layered_perceptions and re-extracts with quality filtering.

This ensures:
1. Explicit claims are filtered for quality
2. Implicit/deep layers are based on high-quality claims only
3. Clean data foundation for pattern system
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.analyzers.layered_perception_extractor_v2 import LayeredPerceptionExtractorV2
from engines.utils.supabase_client import get_supabase


async def main():
    print("\n" + "="*80)
    print("Reprocess All Perceptions with v2.1 Quality Filtering")
    print("="*80 + "\n")

    extractor = LayeredPerceptionExtractorV2()
    supabase = get_supabase()

    # Step 1: Delete existing perceptions
    print("Step 1: Deleting existing layered_perceptions...")
    result = supabase.table('layered_perceptions').select('id', count='exact').execute()
    existing_count = result.count if result.count else 0

    if existing_count > 0:
        print(f"⚠️  Deleting {existing_count} existing perceptions (auto-confirmed)...")
        supabase.table('layered_perceptions').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print(f"✅ Deleted {existing_count} perceptions.\n")
    else:
        print("No existing perceptions to delete.\n")

    # Step 2: Get all contents
    print("Step 2: Loading contents...")
    contents = supabase.table('contents').select('id, title, body').neq('body', '').execute().data

    print(f"Found {len(contents)} contents.\n")

    # Step 3: Process in batches
    batch_size = 10
    total_stats = {
        'processed': 0,
        'total_claims': 0,
        'kept_claims': 0,
        'filtered_claims': 0,
        'errors': 0
    }

    print(f"{'='*80}")
    print(f"Step 3: Processing {len(contents)} contents (batch size: {batch_size})")
    print(f"{'='*80}\n")

    for batch_start in range(0, len(contents), batch_size):
        batch = contents[batch_start:batch_start + batch_size]
        batch_num = batch_start // batch_size + 1
        total_batches = (len(contents) - 1) // batch_size + 1

        print(f"Batch {batch_num}/{total_batches} ({batch_start}/{len(contents)})")

        # Process batch in parallel
        tasks = [extractor.extract_and_save(content) for content in batch]

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"  ❌ {batch[i]['title'][:40]}: {result}")
                    total_stats['errors'] += 1
                else:
                    perception_id, filter_stats = result
                    total_stats['processed'] += 1
                    total_stats['total_claims'] += filter_stats.get('total', 0)
                    total_stats['kept_claims'] += filter_stats.get('kept', 0)
                    total_stats['filtered_claims'] += filter_stats.get('filtered', 0)

                    if filter_stats.get('filtered', 0) > 0:
                        print(f"  ✅ {batch[i]['title'][:40]} | {filter_stats['kept']}/{filter_stats['total']} claims kept")

        except Exception as e:
            print(f"  ⚠️  Batch error: {e}")
            total_stats['errors'] += len(batch)

    # Step 4: Summary
    print(f"\n{'='*80}")
    print(f"Processing Complete")
    print(f"{'='*80}\n")

    print(f"Contents processed: {total_stats['processed']}/{len(contents)}")
    print(f"Errors: {total_stats['errors']}")
    print(f"\nClaims statistics:")
    print(f"  Total extracted: {total_stats['total_claims']}")
    print(f"  Kept (high quality): {total_stats['kept_claims']}")
    print(f"  Filtered (low quality): {total_stats['filtered_claims']}")

    if total_stats['total_claims'] > 0:
        filter_rate = total_stats['filtered_claims'] / total_stats['total_claims'] * 100
        print(f"  Filter rate: {filter_rate:.1f}%")

    # Verify
    final_count = supabase.table('layered_perceptions').select('id', count='exact').execute().count
    print(f"\nFinal layered_perceptions count: {final_count}")

    print(f"\n{'='*80}")
    print("Reprocessing complete!")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    asyncio.run(main())
