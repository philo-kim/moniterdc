"""
개선된 프롬프트 테스트
"""

import asyncio
from engines.analyzers.layered_perception_extractor import LayeredPerceptionExtractor
from engines.utils.supabase_client import get_supabase
import json

async def test():
    supabase = get_supabase()
    extractor = LayeredPerceptionExtractor()

    # 샘플 글 가져오기
    sample = supabase.table('contents')\
        .select('*')\
        .neq('body', '')\
        .limit(1)\
        .execute().data[0]

    print("="*80)
    print("개선된 프롬프트 테스트")
    print("="*80)

    print(f"\n원본 글:")
    print(f"제목: {sample['title']}")
    print(f"본문: {sample['body'][:300]}...")

    print("\n분석 중...")

    perception_id = await extractor.extract(sample)

    # 결과 조회
    result = supabase.table('layered_perceptions')\
        .select('*')\
        .eq('id', str(perception_id))\
        .execute().data[0]

    print("\n" + "="*80)
    print("분석 결과")
    print("="*80)

    print("\n[표면층] 명시적 주장:")
    for claim in result['explicit_claims']:
        print(f"  - {claim['subject']}: {claim['predicate']}")
        print(f"    근거: {claim['evidence_cited']}")

    print("\n[암묵층] 전제하는 사고:")
    for assumption in result['implicit_assumptions']:
        print(f"  - {assumption}")

    print("\n[심층] 무의식적 믿음:")
    for belief in result['deep_beliefs']:
        print(f"  - {belief}")

    print(f"\n힌트: {result['worldview_hints']}")

    print("\n" + "="*80)
    print("평가:")
    print("="*80)

    # 구체성 체크
    has_specific = any([
        '민주당' in str(result['deep_beliefs']),
        '좌파' in str(result['deep_beliefs']),
        '독재' in str(result['deep_beliefs']),
        '과거' in str(result['deep_beliefs']) or '역사' in str(result['deep_beliefs'])
    ])

    if has_specific:
        print("✅ 구체적인 세계관 추출됨")
    else:
        print("❌ 여전히 일반론")

    # 일반론 체크
    has_generic = any([
        '권력은 본질적으로' in str(result['deep_beliefs']),
        '권력은 부패한다' in str(result['deep_beliefs'])
    ]) and not has_specific

    if has_generic:
        print("⚠️ 일반론 포함")

    print("\n"+ "="*80)

if __name__ == '__main__':
    asyncio.run(test())
