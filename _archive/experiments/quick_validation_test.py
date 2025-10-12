"""
빠른 검증: 3개 샘플로 5개 기준 테스트

목적: pilot_10이 너무 오래 걸려서 먼저 3개로 빠르게 검증
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
    print("빠른 검증: 3개 샘플로 5개 기준 테스트")
    print("=" * 80)

    # Step 1: 3개 샘플
    print("\n[Step 1] 3개 Content 샘플링")
    print("-" * 80)

    contents = supabase.table('contents')\
        .select('id, title, body')\
        .neq('body', '')\
        .limit(3)\
        .execute().data

    for i, c in enumerate(contents, 1):
        print(f"  {i}. {c['title'][:60]}")

    # Step 2: Layered Perception 추출
    print("\n[Step 2] Layered Perception 추출")
    print("-" * 80)

    from engines.analyzers.layered_perception_extractor import LayeredPerceptionExtractor

    extractor = LayeredPerceptionExtractor()
    perceptions = []

    for i, content in enumerate(contents, 1):
        print(f"\n[{i}/3] 추출 중...", end="", flush=True)
        try:
            perception_id = await extractor.extract(content)
            perception_data = supabase.table('layered_perceptions')\
                .select('*')\
                .eq('id', str(perception_id))\
                .execute().data[0]
            perceptions.append(perception_data)
            print(" ✓")
        except Exception as e:
            print(f" ❌ {e}")

    print(f"\n✅ {len(perceptions)}개 추출 완료")

    # Step 3: 핵심 검증 - 한 번에 평가
    print("\n[Step 3] 5개 기준 통합 평가")
    print("=" * 80)

    # Prepare data
    eval_data = []
    for p in perceptions:
        eval_data.append({
            "explicit_claims": p.get('explicit_claims', []),
            "implicit_assumptions": p.get('implicit_assumptions', []),
            "reasoning_gaps": p.get('reasoning_gaps', []),
            "deep_beliefs": p.get('deep_beliefs', [])
        })

    # Single GPT-5 call for all evaluation
    eval_prompt = f"""
다음은 3개 글에서 추출한 layered perceptions입니다:

{json.dumps(eval_data, ensure_ascii=False, indent=2)}

5개 검증 기준에 따라 평가하세요:

**기준 1: 특수성 (Specificity)**
- deep_beliefs가 일반론인가, 이 진영만의 특수한 시각인가?
- ❌ "권력은 부패한다" (누구나 동의)
- ✅ "좌파는 독재 본성이 있어서 사찰로 반대파 제거" (특수)
- 점수: 0-10 (6 이상이면 통과)

**기준 2: 전제 포착 (Implicit Assumption)**
- implicit_assumptions가 질문/진술의 전제를 포착했는가?
- 예: "유심교체를 어떻게 알아?" → "합법적으로는 알 수 없다" → "불법 확신"
- 점수: 0-10 (6 이상이면 통과)

**기준 3: Reality Gap**
- reasoning_gaps가 실제 세상과의 차이(왜곡/과장/단정)를 포착했는가?
- 예: "'알고 있다'를 곧바로 '불법 사찰'로 등치" → 근거 없는 비약
- 점수: 0-10 (6 이상이면 통과)

**기준 4: Belief System 구조**
- deep_beliefs를 clustering하면 Who/How/Why/Pattern 구조가 나오는가?
- ❌ "독재와 사찰의 부활" (topic)
- ✅ "좌파는(Who) 사찰로(How) 권력 유지를 위해(Why) 항상 반대파 제거(Pattern)"
- 점수: 0-10 (7 이상이면 통과)

**기준 5: 일관성**
- 3개에서 공통 패턴이 나타나는가?
- 최소 2개 이상에서 유사한 deep belief 발견되어야 함
- 점수: 공통 패턴 비율 (66% 이상이면 통과)

JSON:
{{
  "criterion_1_specificity": {{
    "score": 0-10,
    "reason": "...",
    "pass": true/false,
    "examples": {{"generic": ["일반론들"], "specific": ["특수론들"]}}
  }},
  "criterion_2_implicit": {{
    "score": 0-10,
    "reason": "...",
    "pass": true/false,
    "good_captures": ["잘 포착한 전제들"]
  }},
  "criterion_3_reality_gap": {{
    "score": 0-10,
    "reason": "...",
    "pass": true/false,
    "distortions": ["발견된 왜곡들"]
  }},
  "criterion_4_structure": {{
    "score": 0-10,
    "reason": "...",
    "pass": true/false,
    "potential_worldviews": [
      {{
        "core_belief": "...",
        "who": "...",
        "how": "...",
        "why": "...",
        "pattern": "..."
      }}
    ]
  }},
  "criterion_5_consistency": {{
    "score": 0-100,
    "reason": "...",
    "pass": true/false,
    "common_patterns": ["공통 패턴들"]
  }},
  "total_passed": 0,
  "can_proceed_to_100": true/false,
  "key_issues": ["핵심 문제들"],
  "recommendations": ["개선 방안들"]
}}
"""

    print("\nGPT-5 통합 평가 중...")
    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "Expert evaluator. Strict criteria. JSON only."},
            {"role": "user", "content": eval_prompt}
        ],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)

    # Print results
    print("\n" + "=" * 80)
    print("평가 결과")
    print("=" * 80)

    criteria = [
        ("기준 1: 특수성", "criterion_1_specificity"),
        ("기준 2: 전제 포착", "criterion_2_implicit"),
        ("기준 3: Reality Gap", "criterion_3_reality_gap"),
        ("기준 4: Belief 구조", "criterion_4_structure"),
        ("기준 5: 일관성", "criterion_5_consistency")
    ]

    for name, key in criteria:
        criterion = result[key]
        status = "✅ PASS" if criterion['pass'] else "❌ FAIL"
        print(f"\n{name}: {criterion['score']} - {status}")
        print(f"  이유: {criterion['reason']}")

    # Summary
    passed = result['total_passed']
    print(f"\n\n{'='*80}")
    print(f"통과: {passed}/5 기준")
    print(f"100개로 확장 가능: {'✅ YES' if result['can_proceed_to_100'] else '❌ NO'}")

    if result.get('key_issues'):
        print(f"\n⚠️  핵심 문제:")
        for issue in result['key_issues']:
            print(f"  - {issue}")

    if result.get('recommendations'):
        print(f"\n💡 개선 방안:")
        for rec in result['recommendations']:
            print(f"  - {rec}")

    # Save
    output = {
        "evaluation": result,
        "perceptions": eval_data
    }

    with open('/tmp/quick_validation_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 결과 저장: /tmp/quick_validation_result.json")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
