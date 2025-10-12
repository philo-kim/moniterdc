"""
추론 구조 분석 스크립트

목적: 실제 GPT-5 API로 모든 perception의 추론 구조를 상세 분석
"""

import os
import json
import asyncio
from openai import AsyncOpenAI
from engines.utils.supabase_client import get_supabase

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
supabase = get_supabase()


async def analyze_reasoning_structure(perception):
    """
    단일 perception의 추론 구조 상세 분석

    반환:
    - 추론 메커니즘 (즉시_단정, 필연적_인과, 표면_부정 등)
    - 생략된 추론 단계
    - 행위자 및 목적
    - 일관성 패턴
    """

    # 분석용 데이터 준비
    explicit = perception.get('explicit_claims', [])
    implicit = perception.get('implicit_assumptions', [])
    gaps = perception.get('reasoning_gaps', [])
    deep = perception.get('deep_beliefs', [])

    prompt = f"""
다음은 DC Gallery 정치 글의 3층 분석 결과입니다.

**표면 주장 (Explicit)**:
{json.dumps(explicit, ensure_ascii=False, indent=2)}

**암묵적 전제 (Implicit)**:
{json.dumps(implicit, ensure_ascii=False, indent=2)}

**추론 과정 (Reasoning Gaps)**:
{json.dumps(gaps, ensure_ascii=False, indent=2)}

**심층 믿음 (Deep Beliefs)**:
{json.dumps(deep, ensure_ascii=False, indent=2)}

---

이 글의 **추론 구조**를 분석해주세요:

1. **추론 메커니즘** (해당되는 것 모두):
   - 즉시_단정: 관찰 → (중간 과정 생략) → 결론
   - 필연적_인과: X → 반드시/곧/필연적으로 → Y
   - 표면_부정: 표면은 X / 실제는 Y
   - 역사_투사: 과거 패턴 → 현재 반복
   - 네트워크_추론: 연결 → 조직적 공모

2. **생략된 추론 단계** (무엇을 검증하지 않았나?):
   - 예: 정보 출처 탐색, 합법 가능성, 직접 증거 등

3. **행위자 규정**:
   - 주체: 누가 행동하는가?
   - 목적: 왜 그렇게 한다고 보는가?
   - 방법: 어떤 수단을 쓴다고 보는가?

4. **논리 체인** (관찰 → ... → 결론):
   - Step 1: 구체적 관찰
   - Step 2, 3, ...: 중간 추론 (있다면)
   - Final: 최종 결론

JSON 형식으로 출력:
{{
  "mechanisms": ["즉시_단정", ...],
  "skipped_steps": ["출처 탐색 안 함", ...],
  "actor": {{
    "subject": "민주당/좌파",
    "purpose": "권력 유지",
    "methods": ["사찰", "협박"]
  }},
  "logic_chain": [
    "정보 파악",
    "불법으로 단정",
    "독재 시도"
  ],
  "consistency_pattern": "정보_파악_불법_해석"
}}
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",  # gpt-5 사용 시 변경
            messages=[
                {"role": "system", "content": "You are an expert in analyzing reasoning structures in political discourse. Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        print(f"  ❌ 분석 실패: {e}")
        return None


async def analyze_all_perceptions(limit=None):
    """
    모든 perception 분석
    """

    print("="*80)
    print("추론 구조 분석 시작")
    print("="*80)

    # 1. 모든 perception 로드
    query = supabase.table('layered_perceptions').select('*')
    if limit:
        query = query.limit(limit)

    perceptions = query.execute().data
    print(f"\n총 {len(perceptions)}개 perception 분석 시작\n")

    # 2. 배치 처리
    batch_size = 5  # API 제한 고려
    results = []

    for i in range(0, len(perceptions), batch_size):
        batch = perceptions[i:i+batch_size]

        print(f"배치 {i//batch_size + 1}/{(len(perceptions)-1)//batch_size + 1}")

        # 병렬 처리
        tasks = []
        for lp in batch:
            tasks.append(analyze_reasoning_structure(lp))

        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 결과 저장
        for j, result in enumerate(batch_results):
            if isinstance(result, Exception):
                print(f"  ❌ {batch[j]['id']}: {result}")
            elif result:
                results.append({
                    'perception_id': batch[j]['id'],
                    'content_id': batch[j]['content_id'],
                    'reasoning_structure': result
                })
                print(f"  ✓ {batch[j]['id'][:8]}... - {result.get('consistency_pattern', 'unknown')}")

        # Rate limit 고려
        await asyncio.sleep(1)

    print(f"\n✅ {len(results)}개 분석 완료")

    # 3. 결과 저장
    output_file = '_reasoning_structures_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ 결과 저장: {output_file}")

    return results


async def main():
    """메인 실행"""

    # 전체 데이터 분석
    print("🚀 전체 데이터 분석 실행")
    results = await analyze_all_perceptions()

    # 패턴 분석
    print("\n" + "="*80)
    print("패턴 분석")
    print("="*80)

    from collections import Counter

    all_mechanisms = []
    all_patterns = []

    for r in results:
        structure = r['reasoning_structure']
        all_mechanisms.extend(structure.get('mechanisms', []))
        pattern = structure.get('consistency_pattern', 'unknown')
        all_patterns.append(pattern)

    print("\n메커니즘 분포:")
    for mech, count in Counter(all_mechanisms).most_common():
        print(f"  {mech}: {count}개")

    print("\n일관성 패턴:")
    for pattern, count in Counter(all_patterns).most_common(10):
        print(f"  {pattern}: {count}개")

    print("\n" + "="*80)
    print("✅ 전체 분석 완료")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
