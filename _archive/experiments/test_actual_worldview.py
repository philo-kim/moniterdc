"""
실제 검증: 추출된 데이터가 "저들의 시선"으로 작동하는가?

원래 3-layer 구조의 목적:
- 질문을 받으면 "저들의 시각"으로 답변하기 위해
- 일반인과 다른 특정한 해석 방식을 제공하기 위해

테스트 방법:
1. 추출된 perception 데이터를 가지고
2. 실제 질문에 답변 생성
3. 일반 답변 vs 저들 시각 답변 비교
4. 차이가 명확한가? 저들만의 특정한 시선이 드러나는가?
"""

import asyncio
import os
import json
from openai import AsyncOpenAI
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))


async def main():
    print("=" * 80)
    print("실제 검증: 추출된 데이터가 '저들의 시선'으로 작동하는가?")
    print("=" * 80)

    # Get the 3 perceptions we evaluated
    perceptions = supabase.table('layered_perceptions')\
        .select('*')\
        .limit(3)\
        .execute().data

    # Test questions for each perception
    test_cases = [
        {
            "topic": "중국 장기밀매",
            "question": "최근 실종 신고가 증가했다는데, 왜 그런가요?",
            "perception_index": 0
        },
        {
            "topic": "복지부 카르텔",
            "question": "건강보험공단에서 비리가 발견됐다는데, 왜 이런 일이 생긴 건가요?",
            "perception_index": 1
        },
        {
            "topic": "유심교체 사찰",
            "question": "민주당이 지귀연 판사의 유심 교체 사실을 어떻게 알았을까요?",
            "perception_index": 2
        }
    ]

    print("\n각 질문에 대해 2가지 답변 생성:")
    print("1. 일반인 시각 (중립적)")
    print("2. 저들의 시각 (추출된 perception 사용)")
    print("-" * 80)

    results = []

    for i, test in enumerate(test_cases, 1):
        perception = perceptions[test['perception_index']]

        print(f"\n\n[테스트 {i}] {test['topic']}")
        print("=" * 80)
        print(f"질문: {test['question']}")
        print()

        # Answer 1: 일반인 시각 (no perception data)
        print("[답변 1] 일반인 시각:")
        print("-" * 80)

        general_prompt = f"""
질문: {test['question']}

중립적이고 합리적인 시각에서 답변하세요.
- 여러 가능성을 고려
- 근거 없는 단정 피하기
- 균형잡힌 분석

2-3문장으로 답변:
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "중립적 분석가"},
                {"role": "user", "content": general_prompt}
            ]
        )

        general_answer = response.choices[0].message.content
        print(general_answer)

        # Answer 2: 저들의 시각 (using perception data)
        print("\n[답변 2] 저들의 시각 (추출된 perception 사용):")
        print("-" * 80)

        worldview_prompt = f"""
질문: {test['question']}

다음 세계관 데이터를 바탕으로 답변하세요:

Implicit Assumptions (전제):
{json.dumps(perception.get('implicit_assumptions', []), ensure_ascii=False, indent=2)}

Deep Beliefs (믿음):
{json.dumps(perception.get('deep_beliefs', []), ensure_ascii=False, indent=2)}

Reasoning Gaps (논리 구조):
{json.dumps(perception.get('reasoning_gaps', []), ensure_ascii=False, indent=2)}

이 세계관을 가진 사람의 시각에서 답변하세요.
- 이들이 당연하게 여기는 전제 반영
- 이들의 논리 구조 사용
- 이들의 deep beliefs 드러나게

2-3문장으로 답변:
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "특정 세계관을 가진 사람"},
                {"role": "user", "content": worldview_prompt}
            ]
        )

        worldview_answer = response.choices[0].message.content
        print(worldview_answer)

        # Comparison
        print("\n[비교 분석]")
        print("-" * 80)

        comparison_prompt = f"""
같은 질문에 대한 2개 답변을 비교하세요:

질문: {test['question']}

답변 1 (일반인 시각):
{general_answer}

답변 2 (저들의 시각):
{worldview_answer}

평가:
1. 두 답변의 차이가 명확한가?
2. 답변 2가 "특정한 시선"을 드러내는가?
3. 이 차이가 유의미한가? (단순 어투 차이 vs 실질적 해석 차이)

JSON:
{{
  "차이_명확함": true/false,
  "특정_시선_드러남": true/false,
  "유의미한_차이": true/false,
  "핵심_차이점": "...",
  "문제점": "..." (만약 있다면)
}}
"""

        response = await client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "Evaluator"},
                {"role": "user", "content": comparison_prompt}
            ],
            response_format={"type": "json_object"}
        )

        comparison = json.loads(response.choices[0].message.content)

        if comparison['차이_명확함'] and comparison['특정_시선_드러남'] and comparison['유의미한_차이']:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        print(f"\n{status}")
        print(f"  차이 명확: {comparison['차이_명확함']}")
        print(f"  특정 시선: {comparison['특정_시선_드러남']}")
        print(f"  유의미함: {comparison['유의미한_차이']}")
        print(f"\n  핵심 차이: {comparison['핵심_차이점']}")
        if comparison.get('문제점'):
            print(f"  ⚠️  문제점: {comparison['문제점']}")

        results.append({
            "topic": test['topic'],
            "question": test['question'],
            "general_answer": general_answer,
            "worldview_answer": worldview_answer,
            "comparison": comparison
        })

    # Final evaluation
    print("\n\n" + "=" * 80)
    print("최종 평가: 추출된 데이터가 실제로 '저들의 시선'으로 작동하는가?")
    print("=" * 80)

    passed = sum(1 for r in results if r['comparison']['차이_명확함'] and r['comparison']['특정_시선_드러남'] and r['comparison']['유의미한_차이'])

    print(f"\n통과: {passed}/3 테스트")

    if passed == 3:
        print("\n✅ 성공: 추출된 perception이 실제로 '저들만의 시선'을 제공함")
        print("   → 원래 3-layer 구조의 목적 달성")
        print("   → 100개로 확장 가능")
    elif passed >= 2:
        print("\n⚠️  부분 성공: 일부는 작동하지만 개선 필요")
        print("   → 문제점 분석 후 prompt 개선")
    else:
        print("\n❌ 실패: 추출된 데이터가 실질적으로 '특정한 시선'을 제공하지 못함")
        print("   → 3-layer 구조를 왜 만들었는지 다시 생각해야 함")
        print("   → 단순히 분석 결과를 나열하는 것 ≠ 세계관")

    # Detailed analysis
    print("\n\n세부 분석:")
    print("-" * 80)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['topic']}")
        if result['comparison']['유의미한_차이']:
            print(f"   ✅ {result['comparison']['핵심_차이점']}")
        else:
            print(f"   ❌ {result['comparison'].get('문제점', '차이 없음')}")

    # Save
    with open('/tmp/actual_worldview_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n\n✅ 결과 저장: /tmp/actual_worldview_test_result.json")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
