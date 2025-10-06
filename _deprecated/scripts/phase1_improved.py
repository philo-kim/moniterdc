"""
Phase 1: 데이터 수집 (개선 버전)

변경사항:
- 본문 기준: 100자 → 50자로 완화
- 수집 범위: 더 많은 페이지 (200개 → 300개 시도)
"""

import asyncio
from engines.collectors.content_collector import ContentCollector
from engines.utils.supabase_client import get_supabase

MIN_BODY_LENGTH = 50  # 최소 본문 길이

async def collect_with_relaxed_criteria():
    """완화된 기준으로 수집"""
    print("="*80)
    print(f"Phase 1: 데이터 수집 (기준: {MIN_BODY_LENGTH}자 이상)")
    print("="*80)

    supabase = get_supabase()
    collector = ContentCollector()

    # 1단계: 너무 짧은 글 제거 (50자 미만)
    print("\n[1.1] 짧은 글 정리")
    print("-"*80)

    all_posts = supabase.table('contents').select('id, body').neq('body', '').execute()
    to_delete = [p['id'] for p in all_posts.data if len(p['body']) < MIN_BODY_LENGTH]

    if to_delete:
        for post_id in to_delete:
            supabase.table('contents').delete().eq('id', post_id).execute()
        print(f"✅ {len(to_delete)}개 삭제 (50자 미만)")

    current = supabase.table('contents').select('id', count='exact').neq('body', '').execute()
    current_count = current.count or 0
    print(f"현재: {current_count}개")

    # 2단계: 더 많은 글 수집
    print("\n[1.2] 새로운 글 수집 (목표: 200개)")
    print("-"*80)

    target = 200
    needed = target - current_count

    if needed <= 0:
        print(f"✅ 이미 충분함 ({current_count}개)")
        return current_count

    print(f"추가 필요: {needed}개\n")

    # 더 많은 글 시도 (300개 크롤링 → 50자 이상 필터링)
    crawl_limit = 300

    print(f"[uspolitics] 개념글 수집 (크롤링: {crawl_limit}개)...")

    try:
        content_ids = await collector.collect(
            source_type='dc_gallery',
            gallery='uspolitics',
            limit=crawl_limit,
            concept_only=True,
            is_mgallery=True
        )

        print(f"  크롤링 완료: {len(content_ids)}개")

        # 50자 이상인 것만 카운트
        collected = supabase.table('contents')\
            .select('id, body')\
            .in_('id', [str(cid) for cid in content_ids])\
            .execute()

        good = [c for c in collected.data if len(c.get('body', '')) >= MIN_BODY_LENGTH]
        print(f"  필터링 후: {len(good)}개 (50자 이상)")

        # 최종 확인
        final = supabase.table('contents').select('id', count='exact').neq('body', '').execute()
        final_count = final.count or 0

        print(f"\n✅ 최종: {final_count}개")

        return final_count

    except Exception as e:
        print(f"  ❌ 오류: {e}")
        return current_count

async def verify_quality():
    """품질 검증"""
    print("\n[1.3] 품질 검증")
    print("-"*80)

    supabase = get_supabase()

    samples = supabase.table('contents')\
        .select('title, body')\
        .neq('body', '')\
        .limit(30)\
        .execute()

    lengths = [len(s['body']) for s in samples.data]
    avg_length = sum(lengths) / len(lengths) if lengths else 0

    over_50 = sum(1 for l in lengths if l >= 50)
    over_100 = sum(1 for l in lengths if l >= 100)

    print(f"샘플 30개:")
    print(f"  평균 본문 길이: {avg_length:.0f}자")
    print(f"  50자 이상: {over_50}/30 ({over_50/30*100:.0f}%)")
    print(f"  100자 이상: {over_100}/30 ({over_100/30*100:.0f}%)")

    if over_50 >= 20:
        print("✅ 품질 양호")
        return True
    else:
        print("⚠️ 품질 미흡")
        return False

async def main():
    """실행"""

    final_count = await collect_with_relaxed_criteria()

    quality_ok = await verify_quality()

    print("\n" + "="*80)
    print("Phase 1 완료")
    print("="*80)
    print(f"\n최종: {final_count}개 수집")

    if final_count >= 200:
        print("✅ 목표 달성 - Phase 2로 진행")
    elif final_count >= 100:
        print("⚠️ 부족하지만 진행 가능")
    else:
        print("❌ 데이터 부족")

    print("\n다음 단계: Phase 2 (DB 스키마 생성)")
    print("="*80)

if __name__ == '__main__':
    asyncio.run(main())
