"""
기존에 추출된 perception 데이터 확인하고 평가
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
    print("기존 Perception 데이터로 5개 기준 평가")
    print("=" * 80)

    # Get existing layered_perceptions
    print("\n[Step 1] 기존 layered_perceptions 확인")
    print("-" * 80)

    perceptions = supabase.table('layered_perceptions')\
        .select('*')\
        .limit(3)\
        .execute().data

    if not perceptions:
        print("❌ layered_perceptions 테이블에 데이터 없음")
        print("   88개 perceptions가 있다고 했는데 layered_perceptions는 별도 테이블인가?")

        # Try perceptions table
        print("\n일반 perceptions 테이블 확인...")
        perceptions = supabase.table('perceptions')\
            .select('*')\
            .limit(3)\
            .execute().data

        if not perceptions:
            print("❌ perceptions 테이블도 비어있음")
            return

    print(f"✅ {len(perceptions)}개 perception 발견")

    # Print structure
    print("\n데이터 구조:")
    print(json.dumps(perceptions[0], ensure_ascii=False, indent=2)[:500] + "...")

    # Check if it has the fields we need
    has_layers = all(
        key in perceptions[0]
        for key in ['explicit_claims', 'implicit_assumptions', 'reasoning_gaps', 'deep_beliefs']
    )

    if not has_layers:
        print("\n❌ 3-layer 구조 없음. 필드:")
        print(list(perceptions[0].keys()))
        print("\n이건 old perception 형식. layered_perception이 필요함")
        return

    # Prepare eval data
    eval_data = []
    for p in perceptions:
        eval_data.append({
            "explicit_claims": p.get('explicit_claims', []),
            "implicit_assumptions": p.get('implicit_assumptions', []),
            "reasoning_gaps": p.get('reasoning_gaps', []),
            "deep_beliefs": p.get('deep_beliefs', [])
        })

    print("\n[Step 2] 5개 기준 통합 평가")
    print("=" * 80)

    eval_prompt = f"""
다음은 3개 글에서 추출한 layered perceptions입니다:

{json.dumps(eval_data, ensure_ascii=False, indent=2)}

5개 검증 기준에 따라 평가하세요:

**기준 1: 특수성 (Specificity)**
deep_beliefs가 일반론인가, 이 진영만의 특수한 시각인가?
- ❌ "권력은 부패한다" (누구나 동의)
- ✅ "좌파는 독재 본성이 있어서 사찰로 반대파 제거" (특수)
점수: 0-10 (6 이상 통과)

**기준 2: 전제 포착**
implicit_assumptions가 질문/진술의 전제를 포착했는가?
예: "유심교체를 어떻게 알아?" → "합법적으로는 알 수 없다"
점수: 0-10 (6 이상 통과)

**기준 3: Reality Gap**
reasoning_gaps가 왜곡/과장/단정을 포착했는가?
예: "'알고 있다'를 곧바로 '불법 사찰'로 등치"
점수: 0-10 (6 이상 통과)

**기준 4: Belief System 구조**
deep_beliefs를 clustering하면 Who/How/Why/Pattern 구조가 나오는가?
- ❌ "독재와 사찰" (topic)
- ✅ "좌파는(Who) 사찰로(How) 권력 유지 위해(Why) 항상 반대파 제거(Pattern)"
점수: 0-10 (7 이상 통과)

**기준 5: 일관성**
3개에서 공통 패턴이 나타나는가?
2개 이상에서 유사한 패턴 필요
점수: 공통 패턴 비율 % (66% 이상 통과)

JSON:
{{
  "criterion_1_specificity": {{
    "score": 0-10,
    "pass": true/false,
    "reason": "...",
    "generic_examples": [],
    "specific_examples": []
  }},
  "criterion_2_implicit": {{
    "score": 0-10,
    "pass": true/false,
    "reason": "...",
    "good_examples": []
  }},
  "criterion_3_reality_gap": {{
    "score": 0-10,
    "pass": true/false,
    "reason": "...",
    "distortions_found": []
  }},
  "criterion_4_structure": {{
    "score": 0-10,
    "pass": true/false,
    "reason": "...",
    "potential_worldviews": [
      {{"core_belief": "...", "who": "...", "how": "...", "why": "...", "pattern": "..."}}
    ]
  }},
  "criterion_5_consistency": {{
    "score": 0-100,
    "pass": true/false,
    "reason": "...",
    "common_patterns": []
  }},
  "total_passed": 0,
  "can_proceed": true/false,
  "summary": "...",
  "key_issues": [],
  "recommendations": []
}}
"""

    print("GPT-5 평가 중...")
    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "Expert evaluator. Strict but fair. JSON only."},
            {"role": "user", "content": eval_prompt}
        ],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)

    # Print
    print("\n" + "=" * 80)
    print("평가 결과")
    print("=" * 80)

    criteria_names = [
        ("기준 1: 특수성", "criterion_1_specificity"),
        ("기준 2: 전제 포착", "criterion_2_implicit"),
        ("기준 3: Reality Gap", "criterion_3_reality_gap"),
        ("기준 4: Belief 구조", "criterion_4_structure"),
        ("기준 5: 일관성", "criterion_5_consistency")
    ]

    for name, key in criteria_names:
        c = result[key]
        status = "✅ PASS" if c['pass'] else "❌ FAIL"
        print(f"\n{name}: {c['score']} - {status}")
        print(f"  {c['reason']}")

    print(f"\n\n{'='*80}")
    print(f"통과: {result['total_passed']}/5")
    print(f"100개로 확장 가능: {'✅ YES' if result['can_proceed'] else '❌ NO'}")
    print(f"\n요약: {result['summary']}")

    if result['key_issues']:
        print(f"\n⚠️  핵심 문제:")
        for issue in result['key_issues']:
            print(f"  - {issue}")

    if result['recommendations']:
        print(f"\n💡 개선 방안:")
        for rec in result['recommendations']:
            print(f"  - {rec}")

    # Details
    print(f"\n\n{'='*80}")
    print("상세 평가")
    print("=" * 80)

    for name, key in criteria_names:
        c = result[key]
        print(f"\n{name}:")

        if 'specific_examples' in c and c['specific_examples']:
            print(f"  ✅ 특수론:")
            for ex in c['specific_examples'][:3]:
                print(f"     - {ex}")

        if 'generic_examples' in c and c['generic_examples']:
            print(f"  ❌ 일반론:")
            for ex in c['generic_examples'][:3]:
                print(f"     - {ex}")

        if 'good_examples' in c and c['good_examples']:
            print(f"  ✅ 잘 포착:")
            for ex in c['good_examples'][:3]:
                print(f"     - {ex}")

        if 'distortions_found' in c and c['distortions_found']:
            print(f"  ✅ 왜곡 발견:")
            for ex in c['distortions_found'][:3]:
                print(f"     - {ex}")

        if 'potential_worldviews' in c and c['potential_worldviews']:
            print(f"  💡 Worldview 후보:")
            for wv in c['potential_worldviews'][:2]:
                print(f"     - {wv['core_belief']}")
                print(f"       Who: {wv['who']}, How: {wv['how']}")

        if 'common_patterns' in c and c['common_patterns']:
            print(f"  🔁 공통 패턴:")
            for p in c['common_patterns'][:3]:
                print(f"     - {p}")

    # Save
    with open('/tmp/existing_perception_evaluation.json', 'w', encoding='utf-8') as f:
        json.dump({
            "evaluation": result,
            "perceptions_evaluated": eval_data
        }, f, ensure_ascii=False, indent=2)

    print(f"\n\n✅ 결과 저장: /tmp/existing_perception_evaluation.json")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
