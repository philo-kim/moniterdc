"""
모든 세계관에 대한 반박 논리 생성 스크립트

6개 계층형 세계관에 대해:
1. 논리적 결함 분석
2. 팩트체크 근거 제시
3. 대안적 해석 제공
4. 공감적 대화 가이드 생성
"""

import asyncio
import sys
import os
sys.path.insert(0, '/Users/taehyeonkim/dev/minjoo/moniterdc')

from engines.analyzers.deconstruction_generator import DeconstructionGenerator
from engines.utils.supabase_client import get_supabase

print("="*70)
print("세계관 반박 논리 생성")
print("="*70)

async def generate_all():
    """모든 세계관에 대한 반박 논리 생성"""

    supabase = get_supabase()
    generator = DeconstructionGenerator()

    # Load hierarchical worldviews (those with '>') that have perceptions
    worldviews = supabase.table('worldviews')\
        .select('*')\
        .like('title', '%>%')\
        .gt('total_perceptions', 0)\
        .execute().data

    print(f"\n{len(worldviews)}개 세계관에 대한 반박 논리 생성 시작...\n")

    generated = 0
    failed = 0

    for i, wv in enumerate(worldviews, 1):
        print(f"[{i}/{len(worldviews)}] {wv['title']}")
        print(f"  Perceptions: {wv['total_perceptions']}개")

        try:
            deconstruction = await generator.generate_for_worldview(wv['id'])

            # Show summary
            print(f"  ✅ 생성 완료")
            print(f"     - 논리적 결함: {len(deconstruction.get('logical_flaws', []))}개")
            print(f"     - 팩트체크: {len(deconstruction.get('fact_checks', []))}개")
            print(f"     - 대안 해석: {len(deconstruction.get('alternative_interpretations', []))}개")
            print(f"     - 대화 가이드: {'있음' if deconstruction.get('dialogue_guide') else '없음'}")
            print()

            generated += 1

        except Exception as e:
            print(f"  ❌ 실패: {e}\n")
            failed += 1
            continue

    return {
        'total': len(worldviews),
        'generated': generated,
        'failed': failed
    }

# Generate
stats = asyncio.run(generate_all())

print("="*70)
print("✅ 반박 논리 생성 완료")
print("="*70)

print(f"""
결과:
- 총 세계관: {stats['total']}개
- 생성 성공: {stats['generated']}개
- 생성 실패: {stats['failed']}개

다음 단계:
1. Dashboard에서 확인: http://localhost:3000/worldviews/[id]
2. 자동 업데이트 설정: GitHub Actions 활성화

모든 시스템이 준비되었습니다! 🎉
""")
