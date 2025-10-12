"""
왜곡 패턴 분석

목표:
- Reasoning Gaps (왜곡)가 세계관의 핵심
- 3개 perception의 왜곡 패턴 분석
- 공통 왜곡 구조 추출
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
    print("왜곡 패턴 분석: Reasoning Gaps가 세계관의 핵심")
    print("=" * 80)

    # Get 3 perceptions
    perceptions = supabase.table('layered_perceptions')\
        .select('*')\
        .limit(3)\
        .execute().data

    # Extract all reasoning gaps (왜곡들)
    all_gaps = []
    for i, p in enumerate(perceptions, 1):
        gaps = p.get('reasoning_gaps', [])
        for gap in gaps:
            all_gaps.append({
                'post': i,
                'from': gap.get('from', ''),
                'to': gap.get('to', ''),
                'gap': gap.get('gap', '')
            })

    print(f"\n총 {len(all_gaps)}개 왜곡 발견")
    print("-" * 80)

    for i, gap in enumerate(all_gaps, 1):
        print(f"\n[왜곡 {i}] 글 {gap['post']}")
        print(f"  현실: {gap['from'][:80]}")
        print(f"  왜곡: {gap['to'][:80]}")
        print(f"  Gap: {gap['gap'][:80]}")

    # Analyze distortion patterns
    print("\n\n[분석] 왜곡의 공통 패턴 추출")
    print("=" * 80)

    distortion_prompt = f"""
다음은 DC 갤러리 글들에서 발견된 왜곡들입니다:

{json.dumps(all_gaps, ensure_ascii=False, indent=2)}

이 왜곡들의 공통 패턴을 찾으세요.

왜곡 = 현실과 해석 사이의 gap
세계관 = 왜곡의 패턴

찾아야 할 것:
1. **왜곡의 유형**: 어떤 종류의 왜곡인가?
   - 근거 없는 인과관계
   - 가능성 배제하고 단정
   - 극단으로 비약
   - 등등

2. **왜곡의 방향**: 항상 어떤 방향으로 왜곡되는가?
   - 항상 "악의적" 해석?
   - 항상 "음모" 상정?
   - 항상 "위협" 확대?

3. **왜곡의 구조**: 어떤 논리로 왜곡이 일어나는가?
   ```
   현실 X
     ↓ (어떤 왜곡?)
   해석 Y
   ```

4. **공통 왜곡 패턴**: 3개 글 모두에서 나타나는 왜곡은?

JSON:
{{
  "distortion_types": [
    {{
      "type": "왜곡 유형 이름",
      "description": "...",
      "examples": ["글1의 예", "글2의 예"],
      "frequency": "3/3"
    }}
  ],
  "distortion_direction": {{
    "always_towards": "항상 어떤 방향으로?",
    "never_towards": "절대 안 가는 방향은?",
    "pattern": "..."
  }},
  "distortion_formula": "X를 보면 항상 Y로 왜곡한다",
  "common_distortions": [
    {{
      "pattern": "공통 왜곡 패턴",
      "mechanism": "왜곡 메커니즘",
      "worldview": "이게 드러내는 세계관"
    }}
  ]
}}
"""

    print("GPT-5로 왜곡 패턴 분석 중...")
    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "왜곡 분석 전문가. 현실과 해석의 gap을 본다."},
            {"role": "user", "content": distortion_prompt}
        ],
        response_format={"type": "json_object"}
    )

    analysis = json.loads(response.choices[0].message.content)

    # Print results
    print("\n" + "=" * 80)
    print("왜곡 패턴 분석 결과")
    print("=" * 80)

    print("\n[1] 왜곡의 유형들:")
    print("-" * 80)
    for dtype in analysis['distortion_types']:
        print(f"\n• {dtype['type']} ({dtype['frequency']})")
        print(f"  설명: {dtype['description']}")
        print(f"  예시: {', '.join(dtype['examples'][:2])}")

    print("\n\n[2] 왜곡의 방향:")
    print("-" * 80)
    direction = analysis['distortion_direction']
    print(f"항상 향하는 방향: {direction['always_towards']}")
    print(f"절대 안 가는 방향: {direction['never_towards']}")
    print(f"패턴: {direction['pattern']}")

    print(f"\n\n[3] 왜곡 공식:")
    print("-" * 80)
    print(f"{analysis['distortion_formula']}")

    print("\n\n[4] 공통 왜곡 패턴 (이게 세계관):")
    print("=" * 80)
    for i, common in enumerate(analysis['common_distortions'], 1):
        print(f"\n패턴 {i}: {common['pattern']}")
        print(f"  메커니즘: {common['mechanism']}")
        print(f"  → 세계관: {common['worldview']}")

    # Worldview definition based on distortion
    print("\n\n[최종] 왜곡 기반 세계관 정의")
    print("=" * 80)

    worldview_prompt = f"""
왜곡 분석 결과:

{json.dumps(analysis, ensure_ascii=False, indent=2)}

이 왜곡 패턴들이 드러내는 **세계관**을 정의하세요.

세계관 = 왜곡의 일관된 방향과 패턴

예시:
- 왜곡 1: "온라인 글" → "사실"로 단정
- 왜곡 2: "제도 존재" → "악용"으로 비약
- 왜곡 3: "연결 존재" → "음모"로 해석
→ 세계관: "합법적 설명은 항상 거짓이고, 배후에 악의적 세력이 존재한다"

JSON:
{{
  "worldview_name": "한 문장으로",
  "core_distortion": "핵심 왜곡 패턴",
  "belief_structure": {{
    "about_reality": "현실을 어떻게 보는가?",
    "about_actors": "행위자들을 어떻게 보는가?",
    "about_causality": "인과관계를 어떻게 보는가?"
  }},
  "distortion_mechanism": "왜곡이 작동하는 방식",
  "why_this_matters": "이 세계관이 왜 위험한가?"
}}
"""

    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "세계관 정의자"},
            {"role": "user", "content": worldview_prompt}
        ],
        response_format={"type": "json_object"}
    )

    worldview = json.loads(response.choices[0].message.content)

    print(f"\n세계관: {worldview['worldview_name']}")
    print(f"\n핵심 왜곡: {worldview['core_distortion']}")

    belief = worldview['belief_structure']
    print(f"\n믿음 구조:")
    print(f"  현실 인식: {belief['about_reality']}")
    print(f"  행위자 인식: {belief['about_actors']}")
    print(f"  인과관계 인식: {belief['about_causality']}")

    print(f"\n왜곡 메커니즘: {worldview['distortion_mechanism']}")
    print(f"\n위험성: {worldview['why_this_matters']}")

    # Save
    output = {
        "all_gaps": all_gaps,
        "distortion_analysis": analysis,
        "worldview_definition": worldview
    }

    with open('/tmp/distortion_pattern_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n\n✅ 결과 저장: /tmp/distortion_pattern_analysis.json")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
