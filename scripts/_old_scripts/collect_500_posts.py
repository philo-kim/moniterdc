"""
Phase 1: 500개 글 수집

목표:
- DC Gallery 정치 갤러리에서 500개 이상의 글 수집
- 다양한 시기, 다양한 주제
- 본문이 있는 글만
"""

import asyncio
from engines.collectors.content_collector import ContentCollector
from engines.utils.supabase_client import get_supabase

async def collect_500_posts():
    collector = ContentCollector()
    supabase = get_supabase()

    # 현재 상태 확인
    existing = supabase.table('contents').select('id', count='exact').neq('body', '').execute()
    current_count = existing.count if existing.count else 0

    print("="*80)
    print("Phase 1: 500개 글 수집")
    print("="*80)
    print(f"\n현재 DB: {current_count}개 글 (본문 있음)")

    needed = 500 - current_count

    if needed <= 0:
        print(f"\n✅ 이미 {current_count}개 수집 완료")
        return

    print(f"\n추가 필요: {needed}개")

    # 갤러리 목록 (다양성 확보)
    galleries = [
        ('uspolitics', True),   # 미국정치 마이너 갤러리
        # ('politics', False),    # 정치 갤러리 (일반)
    ]

    total_collected = 0

    for gallery, is_mgallery in galleries:
        if total_collected >= needed:
            break

        limit = min(needed - total_collected + 50, 200)  # 여유있게

        print(f"\n[{gallery}] 수집 중... (목표: {limit}개)")

        try:
            content_ids = await collector.collect(
                source_type='dc_gallery',
                gallery=gallery,
                limit=limit,
                concept_only=True,
                is_mgallery=is_mgallery
            )

            # 본문 있는 것만 카운트
            collected_with_body = supabase.table('contents')\
                .select('id', count='exact')\
                .in_('id', [str(cid) for cid in content_ids])\
                .neq('body', '')\
                .execute()

            count = collected_with_body.count if collected_with_body.count else 0
            total_collected += count

            print(f"  ✅ {count}개 수집 (본문 있음)")
            print(f"  누적: {current_count + total_collected}개")

        except Exception as e:
            print(f"  ❌ 오류: {e}")
            continue

    # 최종 확인
    final = supabase.table('contents').select('id', count='exact').neq('body', '').execute()
    final_count = final.count if final.count else 0

    print("\n" + "="*80)
    print(f"최종 수집: {final_count}개")

    if final_count >= 500:
        print("✅ 목표 달성!")
    else:
        print(f"⚠️ 부족: {500 - final_count}개 더 필요")

    print("="*80)

if __name__ == '__main__':
    asyncio.run(collect_500_posts())
