"""
Phase 1: 데이터 수집

목표:
- 본문 길이 100자 이상인 양질의 글 200개 수집
- 짧은 글, 의미없는 글 제거
- 다양한 주제 확보
"""

import asyncio
from engines.collectors.content_collector import ContentCollector
from engines.utils.supabase_client import get_supabase

async def clean_low_quality_posts():
    """품질 낮은 글 제거"""
    print("="*80)
    print("Phase 1: 데이터 수집")
    print("="*80)

    print("\n[1.1] 품질 낮은 글 정리")
    print("-"*80)

    supabase = get_supabase()

    # 본문이 100자 미만인 글 찾기
    short_posts = supabase.table('contents')\
        .select('id, title, body')\
        .neq('body', '')\
        .execute()

    to_delete = []
    for post in short_posts.data:
        if len(post['body']) < 100:
            to_delete.append(post['id'])

    print(f"짧은 글(100자 미만): {len(to_delete)}개 발견")

    if to_delete:
        # 삭제
        for post_id in to_delete:
            supabase.table('contents').delete().eq('id', post_id).execute()
        print(f"✅ {len(to_delete)}개 글 삭제 완료")

    # 현재 상태
    remaining = supabase.table('contents').select('id', count='exact').neq('body', '').execute()
    count = remaining.count or 0
    print(f"남은 글: {count}개")

    return count

async def collect_new_posts(current_count: int, target: int = 200):
    """새로운 글 수집"""
    print("\n[1.2] 새로운 글 수집")
    print("-"*80)

    needed = target - current_count

    if needed <= 0:
        print(f"✅ 이미 {current_count}개 확보 완료")
        return current_count

    print(f"추가 필요: {needed}개")

    collector = ContentCollector()
    supabase = get_supabase()

    # 갤러리 목록
    galleries = [
        ('uspolitics', True, needed + 50),  # 여유있게
    ]

    total_collected = 0

    for gallery, is_mgallery, limit in galleries:
        print(f"\n[{gallery}] 수집 시작 (목표: {limit}개)...")

        try:
            # 배치로 나눠서 수집 (안전)
            batch_size = 50
            for batch_num in range(0, limit, batch_size):
                batch_limit = min(batch_size, limit - batch_num)

                print(f"  배치 {batch_num//batch_size + 1}: {batch_limit}개 수집 중...")

                content_ids = await collector.collect(
                    source_type='dc_gallery',
                    gallery=gallery,
                    limit=batch_limit,
                    concept_only=True,
                    is_mgallery=is_mgallery
                )

                # 본문 100자 이상만 카운트
                collected = supabase.table('contents')\
                    .select('id, body', count='exact')\
                    .in_('id', [str(cid) for cid in content_ids])\
                    .execute()

                good_count = sum(1 for c in collected.data if len(c.get('body', '')) >= 100)
                total_collected += good_count

                print(f"    ✅ {good_count}개 수집 (본문 100자 이상)")
                print(f"    누적: {current_count + total_collected}/{target}개")

                # 목표 달성하면 중단
                if current_count + total_collected >= target:
                    print(f"\n✅ 목표 달성! ({current_count + total_collected}개)")
                    return current_count + total_collected

                # Rate limit 고려 (1초 대기)
                await asyncio.sleep(1)

        except Exception as e:
            print(f"  ❌ 오류: {e}")
            continue

    final_count = current_count + total_collected
    print(f"\n최종: {final_count}개 수집")

    return final_count

async def verify_quality():
    """수집된 데이터 품질 재확인"""
    print("\n[1.3] 품질 검증")
    print("-"*80)

    supabase = get_supabase()

    # 샘플 20개 확인
    samples = supabase.table('contents')\
        .select('id, title, body')\
        .neq('body', '')\
        .limit(20)\
        .execute()

    good = 0
    for content in samples.data:
        if len(content['body']) >= 100:
            good += 1

    print(f"샘플 품질: {good}/20 (100자 이상)")

    if good >= 15:
        print("✅ 품질 양호")
        return True
    else:
        print("⚠️ 품질 미흡 - 추가 수집 필요")
        return False

async def main():
    """Phase 1 실행"""

    # 1.1 기존 데이터 정리
    current = await clean_low_quality_posts()

    # 1.2 새로운 글 수집
    final = await collect_new_posts(current, target=200)

    # 1.3 품질 검증
    quality_ok = await verify_quality()

    # 최종 결과
    print("\n" + "="*80)
    print("Phase 1 완료")
    print("="*80)

    supabase = get_supabase()
    total = supabase.table('contents').select('id', count='exact').neq('body', '').execute()
    final_count = total.count or 0

    print(f"\n최종 수집: {final_count}개 (본문 있음)")

    if final_count >= 200 and quality_ok:
        print("✅ Phase 1 성공 - Phase 2로 진행 가능")
    elif final_count >= 100:
        print("⚠️ 부족하지만 진행 가능 - Phase 2로 계속")
    else:
        print("❌ 데이터 부족 - 추가 수집 필요")

    print("\n다음 단계:")
    print("  → Phase 2: DB 스키마 생성")
    print("="*80)

if __name__ == '__main__':
    asyncio.run(main())
