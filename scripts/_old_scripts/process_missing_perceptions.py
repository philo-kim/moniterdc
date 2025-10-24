"""
Process Missing Perceptions

Rate limit으로 실패한 contents를 찾아서 재처리합니다.
"""

import sys
import os
import asyncio
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.analyzers.layered_perception_extractor_v2 import LayeredPerceptionExtractorV2
from engines.utils.supabase_client import get_supabase


async def main():
    print("\n" + "="*80)
    print("Process Missing Perceptions (Rate Limit Recovery)")
    print("="*80 + "\n")

    extractor = LayeredPerceptionExtractorV2()
    supabase = get_supabase()

    # Step 1: 처리되지 않은 contents 찾기
    all_contents = supabase.table('contents').select('id, title, body').execute().data
    processed = supabase.table('layered_perceptions').select('content_id').execute().data

    processed_ids = {p['content_id'] for p in processed}
    missing = [c for c in all_contents if c['id'] not in processed_ids and c['body']]

    print(f"총 contents: {len(all_contents)}개")
    print(f"처리 완료: {len(processed)}개")
    print(f"미처리: {len(missing)}개\n")

    if not missing:
        print("✅ 모든 contents가 처리되었습니다!")
        return

    # Step 2: 느린 속도로 재처리 (Rate limit 회피)
    batch_size = 3  # 더 작은 배치
    delay = 15  # 배치 사이 15초 대기

    total = len(missing)
    processed_count = 0

    for i in range(0, total, batch_size):
        batch = missing[i:i+batch_size]

        print(f"\nBatch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size} ({processed_count}/{total})")

        # 하나씩 순차 처리 (병렬 처리 안함)
        for content in batch:
            try:
                perception = await extractor.extract(content)

                if perception:
                    supabase.table('layered_perceptions').insert(perception).execute()
                    processed_count += 1
                    print(f"  ✅ {content['title'][:50]}")
                else:
                    print(f"  ❌ {content['title'][:50]} - No perception extracted")

            except Exception as e:
                error_msg = str(e)
                if '429' in error_msg or 'rate_limit' in error_msg:
                    print(f"  ⏸️  Rate limit - waiting 60s...")
                    await asyncio.sleep(60)
                    # 재시도
                    try:
                        perception = await extractor.extract(content)
                        if perception:
                            supabase.table('layered_perceptions').insert(perception).execute()
                            processed_count += 1
                            print(f"  ✅ (재시도 성공) {content['title'][:50]}")
                    except Exception as e2:
                        print(f"  ❌ {content['title'][:50]}: {str(e2)[:100]}")
                else:
                    print(f"  ❌ {content['title'][:50]}: {error_msg[:100]}")

        # 배치 간 대기
        if i + batch_size < total:
            print(f"\n  ⏳ Waiting {delay}s before next batch...")
            await asyncio.sleep(delay)

    # 최종 통계
    print("\n" + "="*80)
    print("처리 완료")
    print("="*80)
    print(f"처리된 perceptions: {processed_count}개")
    print(f"실패: {total - processed_count}개")
    print(f"성공률: {processed_count/total*100:.1f}%")


if __name__ == '__main__':
    asyncio.run(main())
