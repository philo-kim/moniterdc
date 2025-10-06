"""
반박 논리 생성 시뮬레이션

세계관의 논리적 허점을 분석하고 반박 논리 생성
"""

import asyncio
import sys
import os
import json
from openai import AsyncOpenAI
sys.path.insert(0, '/Users/taehyeonkim/dev/minjoo/moniterdc')
from engines.utils.supabase_client import get_supabase

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def generate_deconstruction_demo():
    """반박 논리 생성 데모"""

    print("="*70)
    print("반박 논리 생성 시뮬레이션")
    print("="*70)

    supabase = get_supabase()

    # 세계관 하나 선택 (독재 재현)
    wv = supabase.table('worldviews')\
        .select('*')\
        .ilike('title', '%독재 재현%')\
        .execute().data[0]

    frame = json.loads(wv['frame'])

    print(f"\n세계관: {wv['title']}")
    print(f"요약: {frame['narrative']['summary']}")

    # 반박 논리 생성
    print("\n" + "="*70)
    print("반박 논리 생성 중...")
    print("="*70)

    prompt = f"""
다음은 DC Gallery에서 발견된 세계관입니다.

【세계관】
제목: {wv['title']}
요약: {frame['narrative']['summary']}

【구체적 해석】
{json.dumps(frame['narrative'].get('examples', []), ensure_ascii=False, indent=2)}

【논리 구조】
- Causal Chain: {frame['metadata']['interpretation_frame'].get('causal_chain', [])}
- Slippery Slope: {json.dumps(frame['metadata']['interpretation_frame'].get('slippery_slope', {}), ensure_ascii=False)}
- 감정: {frame['metadata']['emotional_drivers'].get('primary', '')} (긴급도: {frame['metadata']['emotional_drivers'].get('urgency_level', '')})

---

이 세계관에 대한 **반박 논리**를 생성해주세요.

목적: 여당 지지자가 이 세계관을 가진 사람과 대화할 때 사용할 수 있는 논리적 반박

필요한 항목:

1. **논리적 허점 분석** (Logical Flaws)
   - 이 세계관이 사용하는 논리적 오류 식별
   - 예: 슬리퍼리 슬로프, 허수아비 공격, 성급한 일반화, 인과관계 오류 등

2. **사실 확인** (Fact Check)
   - 이 세계관의 전제가 되는 "사실"들이 실제로 맞는지 검증
   - 반증 사례 제시

3. **대안적 해석** (Alternative Interpretation)
   - 같은 사건을 다르게 해석하는 방법
   - "이렇게도 볼 수 있다"

4. **역사적 맥락 교정** (Historical Context Correction)
   - 이들이 참조하는 역사가 실제와 어떻게 다른지
   - 과거와 현재의 실제 차이

5. **감정적 요소 이해** (Emotional Understanding)
   - 왜 이런 감정(불신, 위기감)을 느끼는지 공감
   - 하지만 그 감정이 사실과는 다를 수 있음을 설명

6. **건설적 대화 가이드** (Constructive Dialogue)
   - 이 세계관을 가진 사람과 대화할 때 피해야 할 것
   - 효과적인 대화 전략

JSON 형식:
{{
  "logical_flaws": [
    {{
      "type": "슬리퍼리 슬로프",
      "description": "A가 일어나면 반드시 Z가 일어난다고 가정",
      "example": "사찰 → 독재 (중간 단계 생략)",
      "rebuttal": "사찰과 독재 사이에는 많은 견제 장치가 존재"
    }}
  ],
  "fact_checks": [
    {{
      "claim": "민주당이 통신사 협박으로 정보 얻음",
      "reality": "정상적인 법적 절차로 정보 확인 가능",
      "evidence": "통신비밀보호법 제13조..."
    }}
  ],
  "alternative_interpretations": [
    {{
      "dc_interpretation": "사찰 시도",
      "alternative": "정상적인 정보 파악",
      "reasoning": "정부는 법적 권한 내에서 필요한 정보 수집 가능"
    }}
  ],
  "historical_corrections": [
    {{
      "their_reference": "1970년대 독재 시절 사찰",
      "actual_difference": "당시: 법적 근거 없이 광범위한 감청 / 현재: 법원 영장 필요, 국회 감독 존재",
      "context": "민주화 이후 사법부 독립, 언론 자유, 시민사회 감시 등 견제 장치 다수"
    }}
  ],
  "emotional_understanding": {{
    "their_emotion": "위기감, 불신 (긴급도: 높음)",
    "why_they_feel": "과거 독재 경험의 트라우마, 권력 남용에 대한 경계",
    "empathy": "그런 우려를 하는 마음은 이해할 수 있다",
    "but": "현재 한국은 민주주의 국가이며 과거와는 다른 견제 시스템이 작동 중"
  }},
  "dialogue_guide": {{
    "avoid": [
      "너희가 틀렸다고 정면 공격",
      "과거 독재 피해자를 무시하는 발언",
      "감정을 무시하고 논리만 강조"
    ],
    "effective": [
      "우려는 이해하지만, 현재는 과거와 다른 점들이 있다",
      "구체적 사례로 견제 장치 설명 (예: 법원 영장, 국회 청문회)",
      "과거와 현재의 차이를 인정하며 대화"
    ],
    "example_response": "유심 교체 정보를 확인한 것에 대한 우려는 이해합니다. 하지만 1970년대와 달리 현재는 법원 영장 없이는 통신 정보 접근이 불가능하며, 국회와 시민사회의 감시가 있습니다. 만약 불법이라면 언론과 야당이 즉시 문제 제기할 것입니다."
  }}
}}
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert in political discourse analysis and constructive dialogue. Always respond in valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    deconstruction = json.loads(response.choices[0].message.content)

    # 결과 출력
    print("\n" + "="*70)
    print("생성된 반박 논리")
    print("="*70)

    print("\n【1. 논리적 허점】")
    for flaw in deconstruction.get('logical_flaws', []):
        print(f"\n  오류 유형: {flaw['type']}")
        print(f"  설명: {flaw['description']}")
        print(f"  예시: {flaw['example']}")
        print(f"  반박: {flaw['rebuttal']}")

    print("\n【2. 사실 확인】")
    for fc in deconstruction.get('fact_checks', []):
        print(f"\n  주장: {fc['claim']}")
        print(f"  실제: {fc['reality']}")
        print(f"  근거: {fc['evidence'][:100]}...")

    print("\n【3. 대안적 해석】")
    for alt in deconstruction.get('alternative_interpretations', []):
        print(f"\n  DC 해석: {alt['dc_interpretation']}")
        print(f"  대안 해석: {alt['alternative']}")
        print(f"  논리: {alt['reasoning']}")

    print("\n【4. 역사적 맥락 교정】")
    for hist in deconstruction.get('historical_corrections', []):
        print(f"\n  그들의 참조: {hist['their_reference']}")
        print(f"  실제 차이: {hist['actual_difference']}")
        print(f"  맥락: {hist['context'][:150]}...")

    print("\n【5. 감정적 이해】")
    emo = deconstruction.get('emotional_understanding', {})
    print(f"\n  그들의 감정: {emo.get('their_emotion', '')}")
    print(f"  왜 그렇게 느끼나: {emo.get('why_they_feel', '')}")
    print(f"  공감: {emo.get('empathy', '')}")
    print(f"  하지만: {emo.get('but', '')}")

    print("\n【6. 대화 가이드】")
    guide = deconstruction.get('dialogue_guide', {})
    print(f"\n  피해야 할 것:")
    for avoid in guide.get('avoid', []):
        print(f"    ❌ {avoid}")

    print(f"\n  효과적인 것:")
    for eff in guide.get('effective', []):
        print(f"    ✅ {eff}")

    print(f"\n  예시 응답:")
    print(f"    \"{guide.get('example_response', '')}\"")

    # DB 저장 시뮬레이션
    print("\n\n" + "="*70)
    print("DB 저장 방식")
    print("="*70)

    print(f"""
이 반박 논리를 worldviews 테이블에 추가:

UPDATE worldviews
SET deconstruction = '{json.dumps(deconstruction, ensure_ascii=False)}'::jsonb
WHERE id = '{wv['id']}';

또는 frame JSON에 추가:
frame.deconstruction = {{...}}
""")

    return deconstruction


async def main():
    deconstruction = await generate_deconstruction_demo()

    print("\n\n" + "="*70)
    print("반박 논리 생성 방식 요약")
    print("="*70)

    print("""
【생성 방식】

1. 입력: 세계관 (narrative + metadata)
   ↓
2. GPT-4o 분석:
   - 논리적 오류 식별
   - 사실 확인
   - 대안적 해석
   - 역사적 맥락 교정
   - 감정 이해
   - 대화 전략
   ↓
3. 출력: 구조화된 반박 논리 (JSON)
   ↓
4. 저장: worldviews.deconstruction 필드

【활용 방식】

1. 대시보드에서 세계관 클릭
   ↓
2. "반박 논리 보기" 탭
   ↓
3. 논리적 허점, 사실 확인, 대화 가이드 표시
   ↓
4. 여당 지지자가 실제 대화에 활용

【장점】

✅ 논리적: 감정이 아닌 논리로 접근
✅ 공감적: 상대방 감정 이해하며 대화
✅ 건설적: 싸우기보다 이해시키기
✅ 실용적: 실제 대화에 사용 가능한 예시

【비용】

- 세계관 1개당 GPT-4o 호출 1회: ~$0.02
- 총 6개 세계관: ~$0.12
- 필요 시만 생성 (일회성)
""")

if __name__ == '__main__':
    asyncio.run(main())
