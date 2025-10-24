"""
DC 개념글 수집 스크립트

특징:
- 목표 개수 기반 수집
- 글 번호 범위 필터링 (선택)
- 진행 상황 실시간 모니터링
- 점진적 limit 증가로 깊은 페이지 탐색

사용 예시:
    # 1개월치 수집 (9/24~10/24, no=2,535,000~2,611,060)
    python3 scripts/collect_dc_posts.py --target 2580 --min-no 2535000 --max-no 2611060

    # 단순히 500개 수집
    python3 scripts/collect_dc_posts.py --target 500

    # 범위 없이 최대한 수집
    python3 scripts/collect_dc_posts.py --limit 10000
"""

import asyncio
import argparse
import re
from typing import Optional, Tuple
from engines.collectors.content_collector import ContentCollector
from engines.utils.supabase_client import get_supabase


def count_in_range(supabase, min_no: Optional[int] = None, max_no: Optional[int] = None) -> Tuple[int, int]:
    """
    DB에서 범위 내 글 개수 확인

    Returns:
        (범위 내 개수, 전체 개수)
    """
    all_contents = []
    page_size = 1000
    offset = 0

    while True:
        result = supabase.table('contents').select('source_url').range(offset, offset + page_size - 1).execute()
        if not result.data:
            break
        all_contents.extend(result.data)
        if len(result.data) < page_size:
            break
        offset += page_size

    total = len(all_contents)

    if min_no is None and max_no is None:
        return total, total

    # 범위 필터링
    in_range = 0
    for c in all_contents:
        match = re.search(r'no=(\d+)', c['source_url'])
        if not match:
            continue

        no = int(match.group(1))

        if min_no is not None and no < min_no:
            continue
        if max_no is not None and no > max_no:
            continue

        in_range += 1

    return in_range, total


async def collect_dc_posts(
    target_count: Optional[int] = None,
    min_no: Optional[int] = None,
    max_no: Optional[int] = None,
    max_limit: int = 10000,
    gallery: str = 'uspolitics'
):
    """
    DC 개념글 수집

    Args:
        target_count: 목표 개수 (범위 내)
        min_no: 최소 글 번호 (None이면 제한 없음)
        max_no: 최대 글 번호 (None이면 제한 없음)
        max_limit: 최대 크롤링 limit
        gallery: 갤러리 ID
    """
    collector = ContentCollector()
    supabase = get_supabase()

    print("=" * 80)
    print("DC 개념글 수집")
    print("=" * 80)

    if min_no or max_no:
        print(f"범위: no={min_no or '제한없음'} ~ {max_no or '제한없음'}")

    if target_count:
        print(f"목표: {target_count:,}개")
    else:
        print(f"목표: limit={max_limit}까지 최대한 수집")

    print(f"갤러리: {gallery}")
    print("=" * 80)
    print()

    # 현재 상태
    current, total_db = count_in_range(supabase, min_no, max_no)

    print(f"📊 현재 상태:")
    print(f"   전체 DB: {total_db:,}개")

    if min_no or max_no:
        print(f"   범위 내: {current:,}개")
        if target_count:
            print(f"   달성률: {current/target_count*100:.1f}%")
    else:
        if target_count:
            print(f"   달성률: {current/target_count*100:.1f}%")

    print()

    # 목표 달성 확인
    if target_count and current >= target_count:
        print("✅ 이미 목표 달성!")
        return

    # 크롤링 전략: 점진적 limit 증가
    limits = [1000, 2000, 3000, 5000, 8000, max_limit]
    limits = [l for l in limits if l <= max_limit]

    for round_num, limit in enumerate(limits, 1):
        print("=" * 80)
        print(f"🔄 Round {round_num}/{len(limits)}: limit={limit:,}")
        print("=" * 80)

        try:
            new_ids = await collector.collect(
                source_type='dc_gallery',
                gallery=gallery,
                limit=limit,
                concept_only=True,
                is_mgallery=True
            )

            print(f"✅ 새로 저장: {len(new_ids):,}개")

            # 현재 상태 재확인
            current, total_db = count_in_range(supabase, min_no, max_no)

            print(f"\n📊 현재 상태:")
            print(f"   전체 DB: {total_db:,}개")

            if min_no or max_no:
                print(f"   범위 내: {current:,}개")
                if target_count:
                    achievement = current / target_count * 100
                    print(f"   달성률: {achievement:.1f}%")
            else:
                if target_count:
                    achievement = current / target_count * 100
                    print(f"   달성률: {achievement:.1f}%")

            print()

            # 목표 달성 확인
            if target_count and current >= target_count:
                print("=" * 80)
                print(f"🎉 목표 달성! ({current:,}개)")
                print("=" * 80)
                break

            # 새 글이 거의 없으면 계속
            if len(new_ids) < 5:
                print(f"ℹ️  새 글이 거의 없음 ({len(new_ids)}개). 더 깊은 페이지 탐색 계속...")
                if round_num < len(limits):
                    await asyncio.sleep(2)
                continue

            # 대기
            if round_num < len(limits):
                print(f"⏳ 3초 대기 후 다음 라운드...")
                await asyncio.sleep(3)

        except Exception as e:
            print(f"❌ 오류: {e}")
            import traceback
            traceback.print_exc()

            if round_num < len(limits):
                print(f"⏳ 5초 대기 후 재시도...")
                await asyncio.sleep(5)
                continue
            else:
                break

    # 최종 결과
    print("\n" + "=" * 80)
    print("최종 결과")
    print("=" * 80)

    current, total_db = count_in_range(supabase, min_no, max_no)

    print(f"전체 DB: {total_db:,}개")

    if min_no or max_no:
        print(f"범위 내: {current:,}개")

    if target_count:
        achievement = current / target_count * 100
        print(f"달성률: {achievement:.1f}%")

        if current >= target_count:
            print("\n✅ 목표 달성 완료!")
        else:
            remaining = target_count - current
            print(f"\n⚠️  {remaining:,}개 부족")

    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='DC 개념글 수집',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 1개월치 수집 (9/24~10/24)
  python3 scripts/collect_dc_posts.py --target 2580 --min-no 2535000 --max-no 2611060

  # 500개 수집
  python3 scripts/collect_dc_posts.py --target 500

  # 최대한 수집 (limit 10000까지)
  python3 scripts/collect_dc_posts.py --limit 10000
        """
    )

    parser.add_argument('--target', type=int, help='목표 개수')
    parser.add_argument('--min-no', type=int, help='최소 글 번호')
    parser.add_argument('--max-no', type=int, help='최대 글 번호')
    parser.add_argument('--limit', type=int, default=10000, help='최대 크롤링 limit (기본: 10000)')
    parser.add_argument('--gallery', type=str, default='uspolitics', help='갤러리 ID (기본: uspolitics)')

    args = parser.parse_args()

    asyncio.run(collect_dc_posts(
        target_count=args.target,
        min_no=args.min_no,
        max_no=args.max_no,
        max_limit=args.limit,
        gallery=args.gallery
    ))


if __name__ == '__main__':
    main()
