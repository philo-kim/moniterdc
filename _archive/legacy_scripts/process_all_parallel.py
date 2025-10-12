#!/usr/bin/env python3
"""
전체 미처리 content를 병렬로 처리

GPT-5 API 호출을 10개씩 병렬로 실행
"""

import asyncio
from engines.analyzers.layered_perception_extractor import LayeredPerceptionExtractor
from engines.utils.supabase_client import get_supabase
from dotenv import load_dotenv

load_dotenv()

async def main():
    supabase = get_supabase()

    # Check unprocessed contents
    all_contents = supabase.table('contents').select('id').execute()
    existing_perceptions = supabase.table('layered_perceptions').select('content_id').execute()
    processed_ids = {p['content_id'] for p in existing_perceptions.data}

    unprocessed_count = len(all_contents.data) - len(processed_ids)

    print("=" * 60)
    print("전체 Content 병렬 처리 (GPT-5)")
    print("=" * 60)
    print(f"전체: {len(all_contents.data)}")
    print(f"처리됨: {len(processed_ids)}")
    print(f"미처리: {unprocessed_count}")

    if unprocessed_count == 0:
        print("\n✅ 모든 content가 처리되었습니다")
        return

    # Get unprocessed contents
    all_contents_data = supabase.table('contents').select('id, title, body').execute()
    unprocessed_contents = [c for c in all_contents_data.data if c['id'] not in processed_ids]

    print(f"\n병렬 처리 시작 (배치 크기: 10)")
    print("-" * 60)

    extractor = LayeredPerceptionExtractor()

    # Process in batches of 10
    batch_size = 10
    total_processed = 0

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
                    total_processed += 1
                    print(f"  ✓ [{total_processed}/{len(unprocessed_contents)}] {batch[i]['title'][:40]}")

        except Exception as e:
            print(f"  ❌ 배치 오류: {e}")
            continue

    print("\n" + "=" * 60)
    print(f"✅ 처리 완료: {total_processed}/{len(unprocessed_contents)}")
    print("=" * 60)

    # Now trigger worldview update
    print("\nWorldview 업데이트 시작...")
    from engines.analyzers.worldview_updater import WorldviewUpdater
    updater = WorldviewUpdater()
    await updater.daily_update()

    print("\n✅ 전체 처리 완료!")

if __name__ == '__main__':
    asyncio.run(main())
