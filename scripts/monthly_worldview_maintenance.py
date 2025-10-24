"""
Monthly Worldview Maintenance

매월 실행하여:
1. Worldview Evolution (Active perceptions 기반)
2. 모든 패턴 재생성 (3개월 윈도우 유지)
3. Mechanism Matcher 재실행

Usage:
    python3 scripts/monthly_worldview_maintenance.py
"""

import sys
import os
from datetime import datetime
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.analyzers import PatternManager
from engines.utils.supabase_client import get_supabase


async def regenerate_patterns_for_worldview(worldview_id: str, title: str):
    """
    특정 worldview의 패턴을 Active perceptions로 재생성

    Args:
        worldview_id: Worldview ID
        title: Worldview 제목 (로깅용)
    """
    pm = PatternManager()
    supabase = get_supabase()

    print(f"\n{'='*80}")
    print(f"패턴 재생성: {title}")
    print(f"{'='*80}\n")

    # Step 1: 기존 패턴 전부 삭제
    print("Step 1: 기존 패턴 삭제...")
    result = supabase.table('worldview_patterns').select('id', count='exact').eq('worldview_id', worldview_id).execute()

    existing_count = result.count if result.count else 0
    print(f"기존 패턴: {existing_count}개")

    if existing_count > 0:
        supabase.table('worldview_patterns').delete().eq('worldview_id', worldview_id).execute()
        print(f"✅ {existing_count}개 패턴 삭제 완료\n")
    else:
        print("삭제할 패턴 없음\n")

    # Step 2: Active perceptions 조회
    print("Step 2: Active perceptions 조회...")

    # perception_worldview_links에서 이 worldview와 연결된 perception들 조회
    links = supabase.table('perception_worldview_links').select('perception_id').eq('worldview_id', worldview_id).execute().data

    if not links:
        print("⚠️  연결된 perception 없음\n")
        return {
            'worldview_id': worldview_id,
            'title': title,
            'deleted': existing_count,
            'regenerated': 0,
            'active_perceptions': 0
        }

    perception_ids = [link['perception_id'] for link in links]

    # Active perceptions만 조회 (archived = false)
    active_perceptions = supabase.table('layered_perceptions').select(
        'id, explicit_claims, implicit_assumptions, deep_beliefs'
    ).in_('id', perception_ids).eq('archived', False).execute().data

    print(f"Active perceptions: {len(active_perceptions)}개\n")

    if len(active_perceptions) == 0:
        print("⚠️  Active perception 없음 (모두 archived)\n")
        return {
            'worldview_id': worldview_id,
            'title': title,
            'deleted': existing_count,
            'regenerated': 0,
            'active_perceptions': 0
        }

    # Step 3: 패턴 재생성
    print(f"Step 3: {len(active_perceptions)}개 perception으로 패턴 재생성...")

    total_stats = {
        'surface': {'new': 0, 'matched': 0},
        'implicit': {'new': 0, 'matched': 0},
        'deep': {'new': 0, 'matched': 0}
    }

    for i, perception in enumerate(active_perceptions, 1):
        if i % 50 == 0:
            print(f"  진행: {i}/{len(active_perceptions)}...")

        stats = pm.integrate_perception(worldview_id, perception)

        for layer in ['surface', 'implicit', 'deep']:
            total_stats[layer]['new'] += stats[layer]['new']
            total_stats[layer]['matched'] += stats[layer]['matched']

    # Step 4: 결과 통계
    print(f"\n{'='*80}")
    print(f"재생성 완료")
    print(f"{'='*80}\n")

    for layer in ['surface', 'implicit', 'deep']:
        total_items = total_stats[layer]['new'] + total_stats[layer]['matched']
        unique_patterns = pm.get_active_patterns(worldview_id, layer=layer)

        print(f"{layer.upper()} 레이어:")
        print(f"  전체 아이템: {total_items}개")
        print(f"  유니크 패턴: {len(unique_patterns)}개")
        print(f"  매칭률: {(total_stats[layer]['matched']/total_items*100) if total_items > 0 else 0:.1f}%\n")

    total_new_patterns = sum(total_stats[layer]['new'] for layer in ['surface', 'implicit', 'deep'])

    return {
        'worldview_id': worldview_id,
        'title': title,
        'deleted': existing_count,
        'regenerated': total_new_patterns,
        'active_perceptions': len(active_perceptions)
    }


async def main():
    print("\n" + "="*80)
    print(f"Monthly Worldview Maintenance - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    supabase = get_supabase()

    # Step 1: Worldview Evolution (이미 구현된 스크립트 사용)
    print("Step 1: Worldview Evolution")
    print("-" * 80)
    print("⚠️  WorldviewEvolutionEngine을 먼저 실행하세요:")
    print("    python3 scripts/run_worldview_evolution.py")
    print()

    input("Evolution 완료 후 Enter를 눌러 계속...")

    # Step 2: 모든 worldview의 패턴 재생성
    print(f"\n{'='*80}")
    print("Step 2: 모든 Worldview 패턴 재생성")
    print(f"{'='*80}\n")

    # Active worldviews 조회
    worldviews = supabase.table('worldviews').select('id, title').eq('archived', False).execute().data

    print(f"Active worldviews: {len(worldviews)}개\n")

    results = []
    for worldview in worldviews:
        result = await regenerate_patterns_for_worldview(
            worldview['id'],
            worldview['title']
        )
        results.append(result)

    # Step 3: Mechanism Matcher 재실행
    print(f"\n{'='*80}")
    print("Step 3: Mechanism Matcher 재실행")
    print(f"{'='*80}\n")
    print("⚠️  MechanismMatcher를 실행하세요:")
    print("    python3 scripts/run_mechanism_matcher.py")
    print()

    # 최종 요약
    print(f"\n{'='*80}")
    print("Monthly Maintenance 완료")
    print(f"{'='*80}\n")

    total_deleted = sum(r['deleted'] for r in results)
    total_regenerated = sum(r['regenerated'] for r in results)
    total_perceptions = sum(r['active_perceptions'] for r in results)

    print(f"처리된 worldviews: {len(results)}개")
    print(f"삭제된 패턴: {total_deleted}개")
    print(f"재생성된 패턴: {total_regenerated}개")
    print(f"사용된 Active perceptions: {total_perceptions}개\n")

    print("Worldview별 결과:")
    for r in results:
        print(f"  {r['title']}: {r['deleted']}개 삭제 → {r['regenerated']}개 재생성")

    print(f"\n{'='*80}")
    print("다음 단계:")
    print(f"{'='*80}")
    print("1. Mechanism Matcher 실행")
    print("2. Phase 2 Claude 검증 (약한 패턴 정리)")
    print("3. Dashboard 확인\n")


if __name__ == '__main__':
    asyncio.run(main())
