"""
GPT-5 기반 세계관 통합 스크립트

문제: 484개의 고유한 consistency_pattern → 실질적 세계관이 아님
해결: GPT-5로 전체 분석 결과를 클러스터링하여 진짜 세계관 추출
"""

import os
import json
import asyncio
from openai import AsyncOpenAI
from collections import Counter

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def consolidate_worldviews():
    """
    GPT-5를 사용해 484개 패턴을 5-10개 실질적 세계관으로 통합
    """

    print("="*80)
    print("GPT-5 기반 세계관 통합")
    print("="*80)

    # 1. 분석 결과 로드
    with open('_reasoning_structures_analysis.json', 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    print(f"\n✅ {len(all_data)}개 분석 결과 로드")

    # 2. 요약 데이터 준비 (GPT-5 토큰 제한 고려)
    summary_data = []
    for item in all_data[:200]:  # 샘플 200개
        rs = item['reasoning_structure']
        summary_data.append({
            'mechanisms': rs.get('mechanisms', []),
            'actor': rs.get('actor', {}).get('subject', ''),
            'purpose': rs.get('actor', {}).get('purpose', ''),
            'pattern': rs.get('consistency_pattern', ''),
            'logic_chain': rs.get('logic_chain', [])[:3]  # 처음 3단계만
        })

    # 3. GPT-5에게 클러스터링 요청
    prompt = f"""
다음은 DC Gallery 정치 글 200개의 추론 구조 분석 결과입니다.

{json.dumps(summary_data, ensure_ascii=False, indent=1)}

이 데이터를 분석해서 **5-10개의 핵심 세계관**을 추출해주세요.

**요구사항:**

1. 각 세계관은 **추론 메커니즘 기반**이어야 합니다 (주제가 아님)
   - 좋은 예: "민주당의 어떤 행동도 독재 시도로 해석하는 구조"
   - 나쁜 예: "민주당에 대한 인식" (이건 주제임)

2. 각 세계관은 **다양한 사건에 적용 가능**해야 합니다
   - 유심교체, 집회제한, 법안발의 등 전혀 다른 사건에도 같은 논리 적용

3. 행위자 중심으로 분류:
   - 민주당/좌파에 대한 해석
   - 중국에 대한 해석
   - 언론/사법부에 대한 해석
   - 보수 진영 자신들에 대한 해석

4. 각 세계관마다:
   - 핵심 메커니즘 (즉시_단정, 필연적_인과 등)
   - 행위자
   - 추정 목적
   - 논리 구조 (A → B → C)

JSON 형식:
{{
  "worldviews": [
    {{
      "title": "민주당/좌파의 정보 파악 → 즉시 불법/사찰로 해석",
      "actor": "민주당/좌파",
      "core_mechanisms": ["즉시_단정", "역사_투사"],
      "logic_pattern": {{
        "trigger": "민주당이 어떤 정보를 알고 있음",
        "skipped_verification": ["정보 출처 확인", "합법 가능성"],
        "conclusion": "불법 사찰 및 독재 시도"
      }},
      "examples": ["유심교체 정보", "집회 정보"],
      "estimated_coverage_pct": 15
    }}
  ]
}}

**중요:** 통합 시 특정성을 잃지 마세요. 각 세계관은 구체적인 논리 패턴을 가져야 합니다.
"""

    print("\n🤖 GPT-5로 세계관 클러스터링 중...")

    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are an expert in cognitive structure analysis. Always respond in valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    worldviews = result.get('worldviews', [])

    print(f"\n✅ {len(worldviews)}개 핵심 세계관 추출")

    # 4. 결과 출력
    print("\n" + "="*80)
    print("추출된 세계관")
    print("="*80)

    for i, wv in enumerate(worldviews, 1):
        print(f"\n세계관 {i}: {wv['title']}")
        print(f"  행위자: {wv['actor']}")
        print(f"  핵심 메커니즘: {', '.join(wv['core_mechanisms'])}")
        print(f"  논리 패턴:")
        print(f"    - Trigger: {wv['logic_pattern']['trigger']}")
        print(f"    - 생략: {', '.join(wv['logic_pattern']['skipped_verification'])}")
        print(f"    - 결론: {wv['logic_pattern']['conclusion']}")
        print(f"  예시: {', '.join(wv.get('examples', []))}")
        print(f"  예상 커버리지: {wv.get('estimated_coverage_pct', 0)}%")

    # 5. 저장
    output_file = '_consolidated_worldviews_gpt5.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(worldviews, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 결과 저장: {output_file}")

    return worldviews


async def match_perceptions_to_worldviews(worldviews):
    """
    각 perception을 통합된 세계관에 매칭
    """

    print("\n" + "="*80)
    print("Perception → Worldview 매칭")
    print("="*80)

    # 분석 결과 로드
    with open('_reasoning_structures_analysis.json', 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    # 각 세계관별 매칭
    matches = {wv['title']: [] for wv in worldviews}

    for item in all_data:
        rs = item['reasoning_structure']

        # 각 세계관과 비교
        for wv in worldviews:
            # 매칭 조건:
            # 1. 행위자 일치
            # 2. 메커니즘 중 하나 이상 일치

            actor_match = wv['actor'] in rs.get('actor', {}).get('subject', '')
            mechanism_match = any(m in rs.get('mechanisms', []) for m in wv['core_mechanisms'])

            # 논리 패턴 키워드 매칭 (간단 버전)
            logic_text = ' '.join(rs.get('logic_chain', []))
            pattern_keywords = [
                wv['logic_pattern']['trigger'],
                wv['logic_pattern']['conclusion']
            ]
            keyword_match = any(kw[:10] in logic_text for kw in pattern_keywords)

            # 매칭 점수
            score = (actor_match * 0.4 + mechanism_match * 0.4 + keyword_match * 0.2)

            if score > 0.5:  # threshold
                matches[wv['title']].append({
                    'perception_id': item['perception_id'],
                    'score': score
                })

    # 결과 출력
    print("\n매칭 결과:")
    total_matched = 0
    for wv_title, perception_list in matches.items():
        count = len(perception_list)
        total_matched += count
        pct = count / len(all_data) * 100
        print(f"  {wv_title[:60]}: {count}개 ({pct:.1f}%)")

    print(f"\n총 매칭: {total_matched}개 / {len(all_data)}개 ({total_matched/len(all_data)*100:.1f}%)")

    # 저장
    output_file = '_worldview_perception_matches.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)

    print(f"✅ 매칭 결과 저장: {output_file}")

    return matches


async def main():
    """메인 실행"""

    # Step 1: GPT-5로 세계관 통합
    worldviews = await consolidate_worldviews()

    # Step 2: Perception 매칭
    matches = await match_perceptions_to_worldviews(worldviews)

    print("\n" + "="*80)
    print("✅ 전체 프로세스 완료")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
