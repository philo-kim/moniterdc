"""
10개 파일럿 테스트: 5개 검증 기준 통과 여부 확인

검증 기준:
1. 특수성: 이 진영만의 특수한 시각인가?
2. 전제된 사고 포착: 질문/진술이 전제하는 믿음을 포착했는가?
3. Reality gap: 실제 세상과 그들이 본 세상의 차이를 포착했는가?
4. Belief system 구조: Topic이 아닌 Who/How/Why/Pattern 구조인가?
5. 데이터 기반 검증: 10개에서 일관된 패턴이 나타나는가?
"""

import asyncio
import os
import json
from openai import AsyncOpenAI
from supabase import create_client
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))


async def main():
    print("=" * 80)
    print("10개 파일럿 테스트: 5개 검증 기준 통과 여부")
    print("=" * 80)

    # Step 1: 10개 샘플링 (다양성 확보)
    print("\n[Step 1] 10개 Content 샘플링")
    print("-" * 80)

    # Get 10 diverse contents
    contents = supabase.table('contents')\
        .select('id, title, body, created_at')\
        .neq('body', '')\
        .order('created_at', desc=False)\
        .limit(10)\
        .execute().data

    print(f"샘플링 완료: {len(contents)}개")
    for i, c in enumerate(contents, 1):
        print(f"  {i}. {c['title'][:60]}...")

    # Step 2: Layered Perception 추출
    print("\n\n[Step 2] Layered Perception 추출 (기존 extractor 사용)")
    print("-" * 80)

    from engines.analyzers.layered_perception_extractor import LayeredPerceptionExtractor

    extractor = LayeredPerceptionExtractor()

    perceptions = []
    for i, content in enumerate(contents, 1):
        print(f"\n[{i}/10] {content['title'][:50]}...")
        try:
            perception_id = await extractor.extract(content)

            # Get the extracted perception
            perception_data = supabase.table('layered_perceptions')\
                .select('*')\
                .eq('id', str(perception_id))\
                .execute().data[0]

            perceptions.append(perception_data)
            print(f"  ✓ 추출 완료")

        except Exception as e:
            print(f"  ❌ 오류: {e}")
            continue

    print(f"\n총 {len(perceptions)}개 추출 완료")

    # Step 3: 각 기준별 평가
    print("\n\n[Step 3] 5개 검증 기준 평가")
    print("=" * 80)

    # 기준 1: 특수성
    print("\n기준 1: 특수성 (Specificity)")
    print("-" * 80)
    print("테스트: deep_beliefs가 일반론인가, 특수론인가?")

    specificity_scores = []

    for i, p in enumerate(perceptions, 1):
        deep_beliefs = p.get('deep_beliefs', [])

        # GPT-5로 특수성 평가
        eval_prompt = f"""
다음 deep beliefs를 평가하세요:

{json.dumps(deep_beliefs, ensure_ascii=False, indent=2)}

각 belief가 일반론인가, 특수론인가?

**일반론 예시:**
- "권력은 부패한다" (누구나 동의)
- "정치인은 거짓말한다" (상식)

**특수론 예시:**
- "좌파는 독재 본성이 있어서 사찰로 반대파 제거" (특정 진영만의 시각)
- "민주당은 통신사 협박해서 개인정보 수집" (근거 없는 구체적 단정)

각 belief에 점수:
- 0점: 완전 일반론 (누구나 동의)
- 5점: 약간 특수함
- 10점: 매우 특수함 (이 진영만의 극단적 시각)

JSON:
{{
  "beliefs_scores": [
    {{"belief": "...", "score": 0-10, "reason": "..."}}
  ],
  "average_score": 0-10,
  "is_specific": true/false
}}
"""

        response = await client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "Evaluator. JSON only."},
                {"role": "user", "content": eval_prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        specificity_scores.append(result['average_score'])

        print(f"\n  [{i}] 평균 특수성: {result['average_score']}/10")
        if result['average_score'] < 6:
            print(f"      ❌ 일반론 포함:")
            for b in result['beliefs_scores']:
                if b['score'] < 6:
                    print(f"         '{b['belief'][:50]}...' - {b['reason']}")

    avg_specificity = sum(specificity_scores) / len(specificity_scores)
    specificity_pass = avg_specificity >= 6.0

    print(f"\n  전체 평균 특수성: {avg_specificity:.1f}/10")
    print(f"  기준 1 통과: {'✅ PASS' if specificity_pass else '❌ FAIL'} (기준: 6.0 이상)")

    # 기준 2: 전제된 사고 포착
    print("\n\n기준 2: 전제된 사고 포착 (Implicit Assumption)")
    print("-" * 80)
    print("테스트: implicit_assumptions가 질문/진술의 전제를 잘 포착했는가?")

    implicit_scores = []

    for i, p in enumerate(perceptions, 1):
        implicit = p.get('implicit_assumptions', [])
        explicit = p.get('explicit_claims', [])

        eval_prompt = f"""
다음을 평가하세요:

Explicit (명시적 주장):
{json.dumps(explicit, ensure_ascii=False, indent=2)}

Implicit (암묵적 전제):
{json.dumps(implicit, ensure_ascii=False, indent=2)}

Implicit이 Explicit의 전제를 잘 포착했는가?

예시:
- Explicit: "유심교체를 어떻게 알아?"
- Implicit: "합법적으로는 알 수 없다" → "불법으로 얻었다는 확신"
→ ✅ GOOD: 질문이 전제하는 믿음을 포착

평가:
- 0-3점: 전제 포착 실패 (단순 반복/요약)
- 4-6점: 부분적 포착
- 7-10점: 전제를 명확히 포착

JSON:
{{
  "score": 0-10,
  "captured_assumptions": ["포착한 전제들"],
  "missing": ["놓친 전제들"]
}}
"""

        response = await client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "Evaluator. JSON only."},
                {"role": "user", "content": eval_prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        implicit_scores.append(result['score'])

        print(f"\n  [{i}] 전제 포착: {result['score']}/10")
        if result.get('missing'):
            print(f"      ⚠️  놓친 전제: {result['missing']}")

    avg_implicit = sum(implicit_scores) / len(implicit_scores)
    implicit_pass = avg_implicit >= 6.0

    print(f"\n  전체 평균: {avg_implicit:.1f}/10")
    print(f"  기준 2 통과: {'✅ PASS' if implicit_pass else '❌ FAIL'} (기준: 6.0 이상)")

    # 기준 3: Reality Gap
    print("\n\n기준 3: 실제 세상과의 Gap (Reality Distortion)")
    print("-" * 80)
    print("테스트: reasoning_gaps가 왜곡/과장/단정을 포착했는가?")

    reality_scores = []

    for i, p in enumerate(perceptions, 1):
        reasoning_gaps = p.get('reasoning_gaps', [])

        eval_prompt = f"""
다음 reasoning gaps를 평가하세요:

{json.dumps(reasoning_gaps, ensure_ascii=False, indent=2)}

실제 세상과의 gap(왜곡/과장/단정)을 포착했는가?

예시:
- Gap: "'알고 있다'를 곧바로 '불법 사찰'로 등치"
→ ✅ GOOD: 논리적 비약, 근거 없는 단정 포착

평가:
- 0-3점: Gap 포착 실패
- 4-6점: 부분적 포착
- 7-10점: 명확히 포착

JSON:
{{
  "score": 0-10,
  "distortions_found": ["발견된 왜곡들"]
}}
"""

        response = await client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "Evaluator. JSON only."},
                {"role": "user", "content": eval_prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        reality_scores.append(result['score'])

        print(f"\n  [{i}] Reality gap: {result['score']}/10")

    avg_reality = sum(reality_scores) / len(reality_scores)
    reality_pass = avg_reality >= 6.0

    print(f"\n  전체 평균: {avg_reality:.1f}/10")
    print(f"  기준 3 통과: {'✅ PASS' if reality_pass else '❌ FAIL'} (기준: 6.0 이상)")

    # 기준 4: Belief System 구조
    print("\n\n기준 4: Belief System 구조 (Worldview Structure)")
    print("-" * 80)
    print("테스트: Deep beliefs를 clustering하면 Who/How/Why/Pattern 구조가 나오는가?")

    # Collect all deep beliefs
    all_beliefs = []
    for p in perceptions:
        all_beliefs.extend(p.get('deep_beliefs', []))

    print(f"\n총 {len(all_beliefs)}개 deep beliefs 수집")

    # Clustering
    clustering_prompt = f"""
다음 10개 글에서 추출한 deep beliefs입니다:

{json.dumps(all_beliefs, ensure_ascii=False, indent=2)}

이들을 공통된 세계관으로 clustering하세요.

⚠️ 절대 규칙:
1. Topic 카테고리 금지
   ❌ "독재와 사찰의 부활" (주제)
   ✅ "좌파는 사찰과 협박으로 권력 유지를 위해 항상 반대파를 제거한다" (belief)

2. 반드시 구조화:
   - Who: 누가?
   - How: 어떻게?
   - Why: 왜?
   - Pattern: 항상 이렇게 된다 (작동 원리)

3. 근거 있는 clustering:
   - 최소 3개 이상의 belief가 지지하는 것만
   - 1-2개만 해당하는 건 버림

JSON:
{{
  "worldviews": [
    {{
      "core_belief": "한 문장으로 (Who/What)",
      "who": "주체",
      "how": "방법/메커니즘",
      "why": "목적/의도",
      "pattern": "항상 이렇게 작동한다",
      "supporting_beliefs": ["이 worldview를 지지하는 원래 beliefs"],
      "count": 3
    }}
  ],
  "total_worldviews": 0,
  "coverage": "90% (전체 beliefs 중 몇 %가 worldview에 포함되었나)"
}}
"""

    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "Expert clusterer. JSON only."},
            {"role": "user", "content": clustering_prompt}
        ],
        response_format={"type": "json_object"}
    )

    clustering_result = json.loads(response.choices[0].message.content)
    worldviews = clustering_result.get('worldviews', [])

    print(f"\n발견된 Worldviews: {len(worldviews)}개")
    print(f"Coverage: {clustering_result.get('coverage', 'N/A')}")

    for i, wv in enumerate(worldviews, 1):
        print(f"\n  [{i}] {wv['core_belief']}")
        print(f"      Who: {wv['who']}")
        print(f"      How: {wv['how']}")
        print(f"      Why: {wv['why']}")
        print(f"      Pattern: {wv['pattern']}")
        print(f"      지지 beliefs: {wv['count']}개")

    # Evaluate structure
    structure_eval_prompt = f"""
다음 worldviews의 구조를 평가하세요:

{json.dumps(worldviews, ensure_ascii=False, indent=2)}

평가:
1. Topic 카테고리인가, Belief system인가?
2. Who/How/Why/Pattern 구조가 명확한가?
3. 일반론인가, 특수론인가?

각 worldview에 점수:
- 0-3점: Topic 카테고리 (주제 분류)
- 4-6점: 부분적 구조
- 7-10점: 명확한 Belief system (Who/How/Why/Pattern)

JSON:
{{
  "worldview_scores": [
    {{"worldview": "...", "score": 0-10, "is_topic": true/false}}
  ],
  "average_score": 0-10
}}
"""

    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "Evaluator. JSON only."},
            {"role": "user", "content": structure_eval_prompt}
        ],
        response_format={"type": "json_object"}
    )

    structure_result = json.loads(response.choices[0].message.content)
    avg_structure = structure_result.get('average_score', 0)
    structure_pass = avg_structure >= 7.0 and len(worldviews) >= 2

    print(f"\n  구조 평균 점수: {avg_structure:.1f}/10")
    print(f"  기준 4 통과: {'✅ PASS' if structure_pass else '❌ FAIL'} (기준: 7.0 이상 & 2개 이상)")

    # 기준 5: 데이터 기반 검증
    print("\n\n기준 5: 데이터 기반 검증 (Consistency)")
    print("-" * 80)
    print("테스트: 10개에서 일관된 패턴이 나타나는가?")

    # Count belief patterns
    belief_patterns = []
    for p in perceptions:
        for belief in p.get('deep_beliefs', []):
            # Extract key concepts
            belief_patterns.append(belief)

    # Most common patterns
    pattern_counter = Counter(belief_patterns)
    most_common = pattern_counter.most_common(5)

    print(f"\n가장 많이 나타난 패턴:")
    for pattern, count in most_common:
        print(f"  - {pattern[:80]}... ({count}회)")

    # Coverage: 최소 30% 글에서 공통 패턴 발견되어야
    max_count = most_common[0][1] if most_common else 0
    coverage = (max_count / len(perceptions)) * 100
    consistency_pass = coverage >= 30

    print(f"\n  최대 패턴 출현율: {coverage:.1f}%")
    print(f"  기준 5 통과: {'✅ PASS' if consistency_pass else '❌ FAIL'} (기준: 30% 이상)")

    # Final Result
    print("\n\n" + "=" * 80)
    print("최종 결과")
    print("=" * 80)

    results = {
        "기준 1 - 특수성": {"score": avg_specificity, "pass": specificity_pass},
        "기준 2 - 전제 포착": {"score": avg_implicit, "pass": implicit_pass},
        "기준 3 - Reality gap": {"score": avg_reality, "pass": reality_pass},
        "기준 4 - Belief 구조": {"score": avg_structure, "pass": structure_pass},
        "기준 5 - 일관성": {"score": coverage, "pass": consistency_pass}
    }

    passed = sum(1 for r in results.values() if r['pass'])
    total = len(results)

    print(f"\n통과: {passed}/{total} 기준\n")
    for criterion, result in results.items():
        status = "✅ PASS" if result['pass'] else "❌ FAIL"
        print(f"  {criterion}: {result['score']:.1f} - {status}")

    all_pass = passed == total

    print(f"\n\n{'='*80}")
    if all_pass:
        print("✅ 모든 기준 통과! 100개로 확장 가능")
    elif passed >= 3:
        print(f"⚠️  {passed}/5 통과. 부족한 기준 개선 후 재시도 필요")
    else:
        print(f"❌ {passed}/5만 통과. 근본적 재검토 필요")

    # Save
    output = {
        "test_summary": {
            "total_criteria": total,
            "passed": passed,
            "can_proceed": all_pass
        },
        "criteria_results": results,
        "worldviews_found": worldviews,
        "perceptions": [
            {
                "content_id": p['content_id'],
                "deep_beliefs": p.get('deep_beliefs', []),
                "implicit_assumptions": p.get('implicit_assumptions', [])
            }
            for p in perceptions
        ]
    }

    with open('/tmp/pilot_10_validation_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 결과 저장: /tmp/pilot_10_validation_result.json")
    print("="*80)


if __name__ == '__main__':
    asyncio.run(main())
