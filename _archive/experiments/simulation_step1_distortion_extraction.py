"""
실제 시뮬레이션 Step 1: 3개 perception에서 왜곡 패턴 추출

목표:
- 추상적 전략이 아니라 실제 데이터로 검증
- 왜곡 패턴이 실제로 추출되는가?
- 이 패턴으로 세계관 만들 수 있는가?
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
    print("Step 1: 3개 perception에서 왜곡 패턴 실제 추출")
    print("=" * 80)

    # Get 3 perceptions
    perceptions = supabase.table('layered_perceptions')\
        .select('*')\
        .limit(3)\
        .execute().data

    print(f"\n✅ 3개 perception 로드 완료\n")

    # Extract reasoning gaps (왜곡들)
    all_gaps = []
    for i, p in enumerate(perceptions, 1):
        gaps = p.get('reasoning_gaps', [])
        print(f"[글 {i}] {len(gaps)}개 왜곡 발견")
        for gap in gaps:
            all_gaps.append({
                'post_num': i,
                'from': gap.get('from', ''),
                'to': gap.get('to', ''),
                'gap': gap.get('gap', ''),
                'implicit': p.get('implicit_assumptions', [])[:2],  # 관련 전제
                'deep': p.get('deep_beliefs', [])[:2]  # 관련 믿음
            })

    print(f"\n총 {len(all_gaps)}개 왜곡 추출 완료\n")

    # Analyze each distortion
    print("=" * 80)
    print("각 왜곡 분석")
    print("=" * 80)

    distortion_analysis = []

    for i, gap in enumerate(all_gaps, 1):
        print(f"\n[왜곡 {i}] 글 {gap['post_num']}")
        print(f"  현실: {gap['from'][:60]}...")
        print(f"  → 해석: {gap['to'][:60]}...")
        print(f"  왜곡: {gap['gap'][:60]}...")

        # GPT로 왜곡 유형 분석
        analysis_prompt = f"""
이 왜곡을 분석하세요:

현실: {gap['from']}
해석: {gap['to']}
Gap: {gap['gap']}

관련 전제: {json.dumps(gap['implicit'], ensure_ascii=False)}
관련 믿음: {json.dumps(gap['deep'], ensure_ascii=False)}

질문:
1. 이 왜곡의 유형은? (예: 대안 배제, 악의 단정, 극단 비약 등)
2. 왜곡의 메커니즘은? (어떤 논리로 왜곡이 일어나는가?)
3. 이게 드러내는 믿음은?

JSON:
{{
  "distortion_type": "왜곡 유형 (간단히)",
  "mechanism": "왜곡 메커니즘 (한 문장)",
  "underlying_belief": "드러내는 믿음 (한 문장)",
  "severity": "low/medium/high"
}}
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # 빠른 분석용
            messages=[
                {"role": "system", "content": "왜곡 분석 전문가"},
                {"role": "user", "content": analysis_prompt}
            ],
            response_format={"type": "json_object"}
        )

        analysis = json.loads(response.choices[0].message.content)
        analysis['gap_data'] = gap

        distortion_analysis.append(analysis)

        print(f"    유형: {analysis['distortion_type']}")
        print(f"    메커니즘: {analysis['mechanism'][:60]}...")
        print(f"    믿음: {analysis['underlying_belief'][:60]}...")

    # Find common patterns
    print("\n\n" + "=" * 80)
    print("왜곡 패턴 clustering")
    print("=" * 80)

    clustering_prompt = f"""
다음은 {len(distortion_analysis)}개 왜곡 분석 결과입니다:

{json.dumps([
    {
        'type': d['distortion_type'],
        'mechanism': d['mechanism'],
        'belief': d['underlying_belief']
    }
    for d in distortion_analysis
], ensure_ascii=False, indent=2)}

이들의 공통 패턴을 찾으세요.

목표:
- 3-5개 왜곡 유형으로 clustering
- 각 유형의 메커니즘 정의
- 각 유형이 드러내는 믿음

JSON:
{{
  "distortion_patterns": [
    {{
      "pattern_name": "패턴 이름",
      "type_description": "이 유형 설명",
      "mechanism": "작동 방식",
      "examples": [왜곡 인덱스들],
      "frequency": "X/{len(distortion_analysis)}",
      "underlying_belief": "이 패턴이 드러내는 믿음"
    }}
  ],
  "pattern_count": 0
}}
"""

    print("\nGPT-5로 clustering 중...")
    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "패턴 인식 전문가"},
            {"role": "user", "content": clustering_prompt}
        ],
        response_format={"type": "json_object"}
    )

    patterns = json.loads(response.choices[0].message.content)

    print(f"\n✅ {patterns['pattern_count']}개 공통 패턴 발견\n")

    for i, pattern in enumerate(patterns['distortion_patterns'], 1):
        print(f"[패턴 {i}] {pattern['pattern_name']} ({pattern['frequency']})")
        print(f"  설명: {pattern['type_description']}")
        print(f"  메커니즘: {pattern['mechanism']}")
        print(f"  믿음: {pattern['underlying_belief']}")
        print(f"  예시: {pattern['examples']}")
        print()

    # Validation: 이 패턴들로 세계관 만들 수 있는가?
    print("=" * 80)
    print("검증: 이 패턴들로 세계관 정의 가능한가?")
    print("=" * 80)

    validation_prompt = f"""
발견된 왜곡 패턴:

{json.dumps(patterns['distortion_patterns'], ensure_ascii=False, indent=2)}

질문:
1. 이 패턴들이 일관된가? (같은 방향을 가리키는가?)
2. 이 패턴들로 "세계관"을 정의할 수 있는가?
3. 3개 글만으로 충분한가? 아니면 더 많은 데이터 필요?

세계관 정의 시도:

JSON:
{{
  "is_consistent": true/false,
  "consistency_reason": "...",
  "can_define_worldview": true/false,
  "worldview_draft": {{
    "name": "세계관 이름",
    "core_distortion": "핵심 왜곡",
    "belief": "핵심 믿음"
  }},
  "data_sufficiency": "sufficient/insufficient",
  "next_step": "3개로 충분한가? 10개 필요한가? 100개?"
}}
"""

    print("\n검증 중...")
    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "검증 전문가"},
            {"role": "user", "content": validation_prompt}
        ],
        response_format={"type": "json_object"}
    )

    validation = json.loads(response.choices[0].message.content)

    print(f"\n일관성: {validation['is_consistent']}")
    print(f"  이유: {validation['consistency_reason']}")

    print(f"\n세계관 정의 가능: {validation['can_define_worldview']}")
    if validation['can_define_worldview']:
        draft = validation['worldview_draft']
        print(f"\n  [세계관 초안]")
        print(f"  이름: {draft['name']}")
        print(f"  핵심 왜곡: {draft['core_distortion']}")
        print(f"  핵심 믿음: {draft['belief']}")

    print(f"\n데이터 충분성: {validation['data_sufficiency']}")
    print(f"다음 단계: {validation['next_step']}")

    # Save results
    output = {
        "step": 1,
        "input": {"perception_count": 3, "gap_count": len(all_gaps)},
        "distortions": distortion_analysis,
        "patterns": patterns,
        "validation": validation,
        "conclusion": {
            "can_proceed": validation['can_define_worldview'] and validation['is_consistent'],
            "next_action": validation['next_step']
        }
    }

    with open('/tmp/simulation_step1_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Print conclusion
    print("\n\n" + "=" * 80)
    print("Step 1 결론")
    print("=" * 80)

    if output['conclusion']['can_proceed']:
        print("\n✅ 성공: 왜곡 패턴 추출 및 세계관 초안 생성 가능")
        print(f"\n다음: {validation['next_step']}")
    else:
        print("\n❌ 실패: 패턴이 불충분하거나 일관되지 않음")
        print(f"\n문제: {validation['consistency_reason']}")

    print(f"\n결과 저장: /tmp/simulation_step1_result.json")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
