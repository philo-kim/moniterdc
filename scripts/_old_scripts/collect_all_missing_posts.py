"""
Collect ALL missing CONCEPT posts from DC Gallery

DC 갤러리에서 9월 21일부터 지금까지의 모든 개념글을 수집합니다.
기존에 수집한 글은 건너뛰고, 새로운 개념글만 추가합니다.
"""

import asyncio
from engines.collectors.content_collector import ContentCollector
from engines.utils.supabase_client import get_supabase

async def collect_all_missing_concepts():
    collector = ContentCollector()
    supabase = get_supabase()

    # 현재 상태 확인
    existing = supabase.table('contents').select('id', count='exact').execute()
    current_count = existing.count if existing.count else 0

    print("="*80)
    print("대량 수집: 9월 21일 ~ 현재까지 모든 DC 개념글")
    print("="*80)
    print(f"\n현재 DB: {current_count}개 글")
    print()

    # 미국정치 갤러리에서 개념글만 대량 수집
    # 개념글은 한 페이지에 약 50개
    # 9월 21일 ~ 지금까지 약 1개월 = 최대 2000개 정도 예상

    gallery = 'uspolitics'
    is_mgallery = True

    # 여러 번에 나눠서 수집 (한번에 너무 많이 하면 부담)
    total_collected = 0
    rounds = 10  # 10번에 나눠서
    limit_per_round = 200  # 한번에 200개씩 (개념글)

    for round_num in range(1, rounds + 1):
        print(f"\n🔄 Round {round_num}/{rounds}: 개념글 {limit_per_round}개 수집 시도...")

        try:
            content_ids = await collector.collect(
                source_type='dc_gallery',
                gallery=gallery,
                limit=limit_per_round,
                concept_only=True,  # 개념글만!
                is_mgallery=is_mgallery
            )

            collected_count = len(content_ids)
            total_collected += collected_count

            print(f"  ✅ {collected_count}개 개념글 수집")
            print(f"  📊 누적: {current_count + total_collected}개")

            # 중복이 너무 많으면 (새 글이 거의 없으면) 중단
            if collected_count < 5:
                print(f"\n  ℹ️ 새 개념글이 거의 없습니다. 수집 중단.")
                break

            # 서버 부담 줄이기 위해 대기
            if round_num < rounds:
                print(f"  ⏳ 5초 대기 중...")
                await asyncio.sleep(5)

        except Exception as e:
            print(f"  ❌ 오류: {e}")
            import traceback
            traceback.print_exc()
            continue

    # 최종 확인
    final = supabase.table('contents').select('id', count='exact').execute()
    final_count = final.count if final.count else 0

    print("\n" + "="*80)
    print(f"✅ 최종 수집: {final_count}개")
    print(f"📈 신규 추가: {final_count - current_count}개")
    print("="*80)

if __name__ == '__main__':
    asyncio.run(collect_all_missing_concepts())
