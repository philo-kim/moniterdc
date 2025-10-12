#!/usr/bin/env python3
"""
신규 content 처리 스크립트

1. 미처리 content 확인
2. 3-layer 분석 (GPT-5)
3. Worldview 업데이트 (필요시)
4. Hybrid matching
"""

import asyncio
import sys
from engines.analyzers.layered_perception_extractor import LayeredPerceptionExtractor
from engines.analyzers.worldview_updater import WorldviewUpdater
from engines.utils.supabase_client import get_supabase
from dotenv import load_dotenv

load_dotenv()

async def main():
    supabase = get_supabase()

    # Check unprocessed contents
    all_contents = supabase.table('contents').select('id').execute()
    existing_perceptions = supabase.table('layered_perceptions').select('content_id').execute()
    processed_ids = {p['content_id'] for p in existing_perceptions.data}

    unprocessed = len(all_contents.data) - len(processed_ids)

    print("=" * 60)
    print(f"신규 Content 처리")
    print("=" * 60)
    print(f"전체: {len(all_contents.data)}")
    print(f"처리됨: {len(processed_ids)}")
    print(f"미처리: {unprocessed}")

    if unprocessed == 0:
        print("\n✅ 모든 content가 처리되었습니다")
        return

    # Step 1: Extract perceptions for unprocessed contents (PARALLEL)
    print(f"\n[1/2] 미처리 {unprocessed}개 분석 (GPT-5, 병렬 10개)")
    print("-" * 60)

    extractor = LayeredPerceptionExtractor()

    # Get unprocessed contents
    all_contents_data = supabase.table('contents').select('id, title, body').execute()
    unprocessed_contents = [c for c in all_contents_data.data if c['id'] not in processed_ids]

    perception_ids = []
    batch_size = 10

    for batch_start in range(0, len(unprocessed_contents), batch_size):
        batch = unprocessed_contents[batch_start:batch_start + batch_size]

        print(f"\n배치 {batch_start//batch_size + 1}/{(len(unprocessed_contents)-1)//batch_size + 1}")

        tasks = []
        for content in batch:
            tasks.append(extractor.extract(content))

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"  ❌ {batch[i]['title'][:40]}: {result}")
                else:
                    perception_ids.append(result)
                    print(f"  ✓ {batch[i]['title'][:40]}")

        except Exception as e:
            print(f"\n  ❌ 배치 오류: {e}")
            continue

    print(f"\n\n✅ {len(perception_ids)}개 perception 생성완료")

    # Step 2: Update worldviews and matching
    print(f"\n[2/2] Worldview 업데이트 & Matching")
    print("-" * 60)

    updater = WorldviewUpdater()
    await updater.daily_update()

    print("\n" + "=" * 60)
    print("처리 완료!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n중단됨")
        sys.exit(0)
