"""
Process New Contents - GitHub Actions용 자동화 스크립트

새로 수집된 contents를 분석하여:
1. Layered perception 추출 (v2.1 with filtering)
2. Reasoning structure 추출
3. Mechanism matching으로 세계관 연결

GitHub Actions에서 10분마다 실행됨
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.analyzers.layered_perception_extractor_v2 import LayeredPerceptionExtractorV2
from engines.analyzers.reasoning_structure_extractor import ReasoningStructureExtractor
from engines.analyzers.mechanism_matcher import MechanismMatcher
from engines.utils.supabase_client import get_supabase


async def main():
    print("\n" + "="*80)
    print(f"Process New Contents - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    supabase = get_supabase()

    # Step 1: 최근 30분간 새로 수집된 contents 찾기
    since = (datetime.now() - timedelta(minutes=30)).isoformat()

    result = supabase.table('contents')\
        .select('id, title, body')\
        .gte('created_at', since)\
        .is_('body', 'not.null')\
        .neq('body', '')\
        .execute()

    new_contents = result.data

    if not new_contents:
        print("✅ No new contents to process")
        return

    print(f"Found {len(new_contents)} new contents to process\n")

    # Step 2: 이미 처리된 것 제외
    already_processed = supabase.table('layered_perceptions')\
        .select('content_id')\
        .in_('content_id', [c['id'] for c in new_contents])\
        .execute()

    processed_ids = {p['content_id'] for p in already_processed.data}
    to_process = [c for c in new_contents if c['id'] not in processed_ids]

    if not to_process:
        print("✅ All contents already processed")
        return

    print(f"Processing {len(to_process)} unprocessed contents...\n")

    # Step 3: Perception 추출 (v2.1 with filtering)
    extractor = LayeredPerceptionExtractorV2()
    structure_extractor = ReasoningStructureExtractor()

    batch_size = 5
    total = len(to_process)
    processed = 0

    for i in range(0, total, batch_size):
        batch = to_process[i:i+batch_size]

        # Perception 추출
        tasks = [extractor.extract(content) for content in batch]
        perceptions = await asyncio.gather(*tasks)

        # DB에 저장
        for perception in perceptions:
            if perception:
                supabase.table('layered_perceptions').insert(perception).execute()
                processed += 1

        print(f"Progress: {processed}/{total} ({processed/total*100:.1f}%)")

    print(f"\n✅ Perception extraction complete: {processed} perceptions created")

    # Step 4: Reasoning structure 추가
    print("\nExtracting reasoning structures...")

    perception_ids = supabase.table('layered_perceptions')\
        .select('id')\
        .in_('content_id', [c['id'] for c in to_process])\
        .execute()

    structure_count = 0
    for p in perception_ids.data:
        try:
            await structure_extractor.extract_and_save(p['id'])
            structure_count += 1
        except Exception as e:
            print(f"Warning: Structure extraction failed for {p['id']}: {e}")
            continue

    print(f"✅ Reasoning structures extracted: {structure_count}")

    # Step 5: Mechanism matching
    print("\nMatching to worldviews...")

    matcher = MechanismMatcher()
    matched = matcher.match_recent_perceptions(minutes=30)

    print(f"✅ Mechanism matching complete: {len(matched)} matches created")

    # Summary
    print("\n" + "="*80)
    print("Summary")
    print("="*80)
    print(f"New contents found: {len(new_contents)}")
    print(f"Processed: {processed}")
    print(f"Reasoning structures: {structure_count}")
    print(f"Worldview matches: {len(matched)}")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    asyncio.run(main())
