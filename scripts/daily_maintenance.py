"""
Daily Maintenance Script

매일 실행:
1. Contents/Perceptions 아카이빙 (90일 이상)
2. Pattern decay (strength 감소)
3. Dead patterns cleanup
4. Lifecycle snapshots (히스토리 저장)

Usage:
    python3 scripts/daily_maintenance.py
"""

import sys
import os
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.analyzers import PatternManager
from engines.archiving import ContentArchiver
from engines.utils.supabase_client import get_supabase


def take_snapshots(supabase):
    """모든 worldviews와 patterns의 스냅샷 저장"""
    print("\n" + "="*80)
    print("Step 4: Lifecycle Snapshots")
    print("="*80 + "\n")

    today = date.today()

    # Worldview snapshots
    worldviews = supabase.table('worldviews').select('id, title').eq('archived', False).execute().data

    print(f"Worldview snapshots ({len(worldviews)}개)...")
    for wv in worldviews:
        supabase.rpc('take_worldview_snapshot', {
            'wv_id': wv['id'],
            'snap_date': today.isoformat()
        }).execute()

    print(f"✅ {len(worldviews)}개 worldview snapshot 저장\n")

    # Pattern snapshots (active/fading만)
    patterns = supabase.table('worldview_patterns').select('id').in_('status', ['active', 'fading']).execute().data

    print(f"Pattern snapshots ({len(patterns)}개)...")
    snapshot_count = 0
    for pattern in patterns:
        supabase.rpc('take_pattern_snapshot', {
            'patt_id': pattern['id'],
            'snap_date': today.isoformat()
        }).execute()
        snapshot_count += 1

        if snapshot_count % 100 == 0:
            print(f"  진행: {snapshot_count}/{len(patterns)}...")

    print(f"✅ {snapshot_count}개 pattern snapshot 저장\n")

    return len(worldviews), snapshot_count


def main():
    print("\n" + "="*80)
    print(f"Daily Maintenance - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    archiver = ContentArchiver(days_threshold=90)
    pm = PatternManager()
    supabase = get_supabase()

    # ==================== Step 1: Contents 아카이빙 ====================
    print("="*80)
    print("Step 1: Contents/Perceptions 아카이빙 (90일 이상)")
    print("="*80 + "\n")

    archive_result = archiver.archive_old_contents()

    print(f"✅ Contents archived: {archive_result['contents_archived']}개")
    print(f"✅ Perceptions archived: {archive_result['perceptions_archived']}개")
    print(f"기준 날짜: {archive_result['threshold_date'][:10]}\n")

    # ==================== Step 2: Pattern Decay ====================
    print("="*80)
    print("Step 2: Pattern Decay (strength 감소)")
    print("="*80 + "\n")

    decay_stats = pm.decay_patterns()

    for layer in ['surface', 'implicit', 'deep']:
        if decay_stats[layer]['total'] > 0:
            print(f"{layer.upper()} 레이어:")
            print(f"  처리: {decay_stats[layer]['total']}개")
            print(f"  Fading: {decay_stats[layer]['fading']}개")
            print(f"  Dead: {decay_stats[layer]['dead']}개\n")

    total_dead = sum(decay_stats[layer]['dead'] for layer in ['surface', 'implicit', 'deep'])
    print(f"총 Dead 패턴: {total_dead}개\n")

    # ==================== Step 3: Dead Patterns Cleanup ====================
    print("="*80)
    print("Step 3: Dead Patterns Cleanup")
    print("="*80 + "\n")

    removed = pm.cleanup_dead_patterns()
    print(f"✅ Dead patterns removed: {removed}개\n")

    # ==================== Step 4: Lifecycle Snapshots ====================
    wv_count, pattern_count = take_snapshots(supabase)

    # ==================== Summary ====================
    print("="*80)
    print("Daily Maintenance Complete")
    print("="*80 + "\n")

    print(f"Contents archived: {archive_result['contents_archived']}개")
    print(f"Patterns decayed: {sum(decay_stats[l]['total'] for l in ['surface', 'implicit', 'deep'])}개")
    print(f"Dead patterns removed: {removed}개")
    print(f"Snapshots saved: {wv_count} worldviews + {pattern_count} patterns\n")

    # Stats
    stats = archiver.get_archive_stats()
    if stats:
        print("="*80)
        print("현재 상태")
        print("="*80 + "\n")
        print(f"Active contents: {stats['active_contents']:,}개")
        print(f"Archived contents: {stats['archived_contents']:,}개")
        print(f"Active perceptions: {stats['active_perceptions']:,}개")
        print(f"Archived perceptions: {stats['archived_perceptions']:,}개\n")

    print("="*80)
    print("다음 단계:")
    print("="*80)
    print("- 매주: Phase 2 Claude 검증 (약한 패턴)")
    print("- 매월: Worldview Evolution\n")


if __name__ == '__main__':
    main()
