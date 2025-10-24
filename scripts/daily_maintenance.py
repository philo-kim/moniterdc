"""
Daily Maintenance Script v2.0

v2.0 시스템에 맞춰 단순화:
1. Contents/Perceptions 아카이빙 (90일 이상) - published_at 기준
2. 통계 출력

Pattern decay, snapshots 등은 v2.0에서 제거됨

Usage:
    python3 scripts/daily_maintenance_v2.py
"""

import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.utils.supabase_client import get_supabase


def archive_old_contents(supabase, days_threshold=90):
    """90일 이상 된 contents와 perceptions 삭제"""

    print("="*80)
    print(f"Contents/Perceptions 아카이빙 (published_at 기준 {days_threshold}일 이상)")
    print("="*80)
    print()

    # 기준 날짜
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_threshold)
    cutoff_iso = cutoff_date.isoformat()

    print(f"기준 날짜: {cutoff_date.strftime('%Y-%m-%d')}")
    print()

    # 90일 이상 된 contents 찾기
    old_contents = supabase.table('contents')\
        .select('id')\
        .lt('published_at', cutoff_iso)\
        .execute()

    if not old_contents.data:
        print("✅ 아카이빙할 오래된 contents 없음")
        return {'contents_archived': 0, 'perceptions_archived': 0, 'threshold_date': cutoff_iso}

    old_ids = [c['id'] for c in old_contents.data]

    print(f"발견된 오래된 contents: {len(old_ids):,}개")
    print()

    # 관련 perceptions 수 확인
    old_perceptions = supabase.table('layered_perceptions')\
        .select('id')\
        .in_('content_id', old_ids)\
        .execute()

    perception_count = len(old_perceptions.data) if old_perceptions.data else 0

    print(f"관련 perceptions: {perception_count:,}개")
    print()

    # 삭제 시작
    print("삭제 중...")

    # Perceptions 먼저 삭제 (foreign key)
    if perception_count > 0:
        # perception_worldview_links 먼저 삭제
        perception_ids = [p['id'] for p in old_perceptions.data]

        supabase.table('perception_worldview_links')\
            .delete()\
            .in_('perception_id', perception_ids)\
            .execute()

        # perceptions 삭제
        supabase.table('layered_perceptions')\
            .delete()\
            .in_('content_id', old_ids)\
            .execute()

        print(f"  ✅ Perceptions 삭제: {perception_count:,}개")

    # Contents 삭제
    supabase.table('contents')\
        .delete()\
        .in_('id', old_ids)\
        .execute()

    print(f"  ✅ Contents 삭제: {len(old_ids):,}개")
    print()

    return {
        'contents_archived': len(old_ids),
        'perceptions_archived': perception_count,
        'threshold_date': cutoff_iso
    }


def print_stats(supabase):
    """현재 DB 통계 출력"""

    print("="*80)
    print("현재 상태")
    print("="*80)
    print()

    # Contents 통계
    total_contents = supabase.table('contents').select('id', count='exact').execute()

    # Perceptions 통계
    total_perceptions = supabase.table('layered_perceptions').select('id', count='exact').execute()

    # Worldviews 통계
    total_worldviews = supabase.table('worldviews').select('id', count='exact').eq('archived', False).execute()

    # Links 통계
    total_links = supabase.table('perception_worldview_links').select('id', count='exact').execute()

    print(f"Contents: {total_contents.count:,}개")
    print(f"Perceptions: {total_perceptions.count:,}개")
    print(f"Worldviews: {total_worldviews.count:,}개")
    print(f"Links: {total_links.count:,}개")
    print()

    # 커버리지 계산
    if total_perceptions.count > 0 and total_links.count > 0:
        # 링크가 있는 perception 수
        linked_perceptions = supabase.table('perception_worldview_links')\
            .select('perception_id')\
            .execute()

        unique_linked = len(set(l['perception_id'] for l in linked_perceptions.data))
        coverage = (unique_linked / total_perceptions.count) * 100

        print(f"세계관 커버리지: {coverage:.1f}% ({unique_linked:,}/{total_perceptions.count:,})")
        print()


def main():
    print("\n" + "="*80)
    print(f"Daily Maintenance v2.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()

    supabase = get_supabase()

    # Step 1: 아카이빙
    archive_result = archive_old_contents(supabase, days_threshold=90)

    # Step 2: 통계
    print_stats(supabase)

    # Summary
    print("="*80)
    print("Daily Maintenance Complete")
    print("="*80)
    print()

    if archive_result['contents_archived'] > 0:
        print(f"✅ Contents archived: {archive_result['contents_archived']:,}개")
        print(f"✅ Perceptions archived: {archive_result['perceptions_archived']:,}개")
    else:
        print("✅ 아카이빙할 오래된 데이터 없음")

    print()
    print("="*80)
    print("다음 단계:")
    print("="*80)
    print("- 매주: Worldview Evolution 검토")
    print("- 매월: run_worldview_evolution.py 실행")
    print()


if __name__ == '__main__':
    main()
