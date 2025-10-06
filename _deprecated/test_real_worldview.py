"""
진짜 세계관 분석 테스트
"""
import asyncio
from engines.analyzers.worldview_analyzer import WorldviewAnalyzer
from engines.utils.supabase_client import get_supabase
import json

async def main():
    print("=" * 80)
    print("진짜 세계관 분석 테스트")
    print("=" * 80)

    analyzer = WorldviewAnalyzer()
    supabase = get_supabase()

    # Get sample contents
    contents = supabase.table('contents').select('*').neq('body', '').limit(30).execute().data

    print(f"\n분석 대상: {len(contents)}개 글")
    print("\n분석 중...")

    result = await analyzer.analyze_worldview_from_posts(contents)

    print("\n" + "=" * 80)
    print("분석 결과")
    print("=" * 80)

    print("\n## 1. 인과 구조 (Causal Chains)")
    print("-" * 80)
    for i, chain in enumerate(result.get('causal_chains', []), 1):
        print(f"\n[Chain {i}]")
        print(" → ".join(chain['chain']))
        print(f"관련 글: {', '.join(chain.get('example_posts', [])[:2])}")

    print("\n## 2. 대립 구도 (Opposition Framework)")
    print("-" * 80)
    opp = result.get('opposition_framework', {})
    if opp:
        print("\n우리 편:")
        print(f"  정체성: {', '.join(opp.get('us', {}).get('identity', []))}")
        print(f"  속성: {', '.join(opp.get('us', {}).get('attributes', []))}")
        print(f"  역할: {opp.get('us', {}).get('role', '')}")

        print("\n적:")
        print(f"  정체성: {', '.join(opp.get('them', {}).get('identity', []))}")
        print(f"  속성: {', '.join(opp.get('them', {}).get('attributes', []))}")
        print(f"  역할: {opp.get('them', {}).get('role', '')}")

        print(f"\n대립의 성격: {opp.get('conflict_nature', '')}")

    print("\n## 3. 감정 논리 (Emotional Logic)")
    print("-" * 80)
    for i, emo in enumerate(result.get('emotional_logic', []), 1):
        print(f"\n[감정 {i}] {emo.get('emotion', '')}")
        print(f"  촉발: {emo.get('trigger', '')}")
        print(f"  해석: {emo.get('interpretation', '')}")
        print(f"  결론: {emo.get('conclusion', '')}")

    print("\n## 4. 암묵적 전제 (Implicit Assumptions)")
    print("-" * 80)
    for i, assumption in enumerate(result.get('implicit_assumptions', []), 1):
        print(f"\n[전제 {i}] {assumption.get('assumption', '')}")
        print(f"  근거: {assumption.get('evidence', '')}")
        print(f"  영향: {assumption.get('impact', '')}")

    print("\n## 5. 전체 서사 (Narrative)")
    print("-" * 80)
    print(result.get('narrative', ''))

    print("\n" + "=" * 80)
    print("✅ 분석 완료")
    print("=" * 80)

if __name__ == '__main__':
    asyncio.run(main())
