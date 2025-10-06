"""
Phase 4: 패턴 탐지
- layered_perceptions에서 반복되는 deep_beliefs 찾기
- 빈도 분석 및 통계
- belief_patterns 테이블에 저장
"""

import asyncio
from collections import Counter
from engines.utils.supabase_client import get_supabase

async def detect_patterns():
    supabase = get_supabase()

    print("="*80)
    print("Phase 4: 패턴 탐지")
    print("="*80)

    # 1. 모든 deep_beliefs 추출
    print("\n[1/4] deep_beliefs 추출 중...")
    results = supabase.table('layered_perceptions').select('deep_beliefs').execute()

    all_beliefs = []
    for r in results.data:
        if r.get('deep_beliefs'):
            all_beliefs.extend(r['deep_beliefs'])

    total_beliefs = len(all_beliefs)
    print(f"총 추출된 믿음: {total_beliefs}개")

    # 2. 빈도 분석
    print("\n[2/4] 빈도 분석 중...")
    belief_counts = Counter(all_beliefs)

    # 3. belief_patterns 테이블 초기화
    print("\n[3/4] belief_patterns 테이블 초기화...")
    supabase.table('belief_patterns').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()

    # 4. 패턴 저장
    print("\n[4/4] 패턴 저장 중...")
    total_perceptions = len(results.data)

    patterns = []
    for belief, count in belief_counts.items():
        percentage = (count / total_perceptions) * 100

        patterns.append({
            'belief': belief,
            'frequency': count,
            'percentage': round(percentage, 2),
            'co_occurring_beliefs': {},  # TODO: Phase 4.2에서 구현
            'cluster_id': None  # TODO: Phase 4.3에서 구현
        })

    # 배치로 저장
    if patterns:
        supabase.table('belief_patterns').insert(patterns).execute()

    print(f"\n✅ {len(patterns)}개 패턴 저장 완료")

    # 결과 요약
    print("\n" + "="*80)
    print("패턴 탐지 결과")
    print("="*80)

    # 핵심 믿음 (30% 이상)
    core_beliefs = [p for p in patterns if p['percentage'] >= 30]
    print(f"\n핵심 믿음 (30% 이상): {len(core_beliefs)}개")
    for p in sorted(core_beliefs, key=lambda x: x['frequency'], reverse=True):
        print(f"  [{p['frequency']:3d}회 / {p['percentage']:5.1f}%] {p['belief']}")

    # 부분 믿음 (10-30%)
    partial_beliefs = [p for p in patterns if 10 <= p['percentage'] < 30]
    print(f"\n부분 믿음 (10-30%): {len(partial_beliefs)}개")
    for p in sorted(partial_beliefs, key=lambda x: x['frequency'], reverse=True)[:10]:
        print(f"  [{p['frequency']:3d}회 / {p['percentage']:5.1f}%] {p['belief']}")

    # 개별 의견 (10% 미만)
    individual_beliefs = [p for p in patterns if p['percentage'] < 10]
    print(f"\n개별 의견 (10% 미만): {len(individual_beliefs)}개")
    print(f"  (상위 10개만 표시)")
    for p in sorted(individual_beliefs, key=lambda x: x['frequency'], reverse=True)[:10]:
        print(f"  [{p['frequency']:3d}회 / {p['percentage']:5.1f}%] {p['belief']}")

    print("\n" + "="*80)
    print(f"Phase 4 완료!")
    print("="*80)

if __name__ == '__main__':
    asyncio.run(detect_patterns())
