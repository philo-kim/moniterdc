"""
Daily Archiving Script

매일 실행하여 90일 이상 된 contents를 자동으로 아카이브

Usage:
    python3 scripts/daily_archiving.py             # 실제 아카이브
    python3 scripts/daily_archiving.py --dry-run   # 미리보기
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.archiving import ContentArchiver


def main():
    dry_run = '--dry-run' in sys.argv

    print("\n" + "="*80)
    print(f"Daily Archiving - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if dry_run:
        print("MODE: DRY RUN (미리보기)")
    print("="*80 + "\n")

    archiver = ContentArchiver(days_threshold=90)

    # Step 1: 현재 통계
    print("Step 1: 현재 상태")
    print("-" * 80)

    stats = archiver.get_archive_stats()

    if stats:
        print(f"Active contents: {stats['active_contents']:,}개")
        print(f"  - 0-30일: {stats['active_0_30_days']:,}개")
        print(f"  - 30-60일: {stats['active_30_60_days']:,}개")
        print(f"  - 60-90일: {stats['active_60_90_days']:,}개")
        print(f"\nArchived contents: {stats['archived_contents']:,}개")
        print(f"\nActive perceptions: {stats['active_perceptions']:,}개")
        print(f"Archived perceptions: {stats['archived_perceptions']:,}개\n")
    else:
        print("통계 조회 실패\n")

    # Step 2: 아카이브 실행
    print("Step 2: 아카이브 실행")
    print("-" * 80)

    result = archiver.archive_old_contents(dry_run=dry_run)

    if dry_run:
        print(f"아카이브 대상: {result['contents_archived']}개 contents")
        print(f"기준 날짜: {result['threshold_date'][:10]} (90일 전)")

        if result.get('preview'):
            print(f"\n대상 목록 (처음 10개):")
            for i, content in enumerate(result['preview'], 1):
                print(f"  {i}. {content['published_at'][:10]} - {content['title'][:60]}")

        print(f"\n⚠️  실제로 아카이브하려면 --dry-run 없이 실행하세요.")
    else:
        print(f"✅ Contents archived: {result['contents_archived']}개")
        print(f"✅ Perceptions archived: {result['perceptions_archived']}개")
        print(f"기준 날짜: {result['threshold_date'][:10]} (90일 전)")

    # Step 3: 아카이브 후 통계
    if not dry_run and result['contents_archived'] > 0:
        print(f"\nStep 3: 아카이브 후 상태")
        print("-" * 80)

        stats = archiver.get_archive_stats()

        if stats:
            print(f"Active contents: {stats['active_contents']:,}개")
            print(f"Archived contents: {stats['archived_contents']:,}개")
            print(f"\nActive perceptions: {stats['active_perceptions']:,}개")
            print(f"Archived perceptions: {stats['archived_perceptions']:,}개\n")

    print("="*80)
    print("Daily Archiving Complete")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
