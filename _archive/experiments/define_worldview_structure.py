"""
세계관 구조 정의

세계관 = 100개 글을 관통하는 일관된 사고 구조

목표:
1. 3개 perception에서 공통 구조 추출
2. 이 구조가 실제로 "세상이 작동하는 방식"에 대한 믿음인지 확인
3. 이 구조로 다른 글들도 설명 가능한지 검증
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
    print("세계관 구조 정의: 3개 perception에서 공통 사고 구조 추출")
    print("=" * 80)

    # Get 3 perceptions
    perceptions = supabase.table('layered_perceptions')\
        .select('*')\
        .limit(3)\
        .execute().data

    print("\n[Step 1] 3개 perception의 layer 구조 분석")
    print("-" * 80)

    # Analyze structure
    structure_prompt = f"""
다음은 3개 글에서 추출한 layered perceptions입니다:

글 1 (중국 장기밀매):
- Explicit: {json.dumps(perceptions[0]['explicit_claims'][:2], ensure_ascii=False)}
- Implicit: {json.dumps(perceptions[0]['implicit_assumptions'][:3], ensure_ascii=False)}
- Deep: {json.dumps(perceptions[0]['deep_beliefs'][:2], ensure_ascii=False)}

글 2 (복지부 카르텔):
- Explicit: {json.dumps(perceptions[1]['explicit_claims'][:2], ensure_ascii=False)}
- Implicit: {json.dumps(perceptions[1]['implicit_assumptions'][:3], ensure_ascii=False)}
- Deep: {json.dumps(perceptions[1]['deep_beliefs'][:2], ensure_ascii=False)}

글 3 (유심교체 사찰):
- Explicit: {json.dumps(perceptions[2]['explicit_claims'][:2], ensure_ascii=False)}
- Implicit: {json.dumps(perceptions[2]['implicit_assumptions'][:3], ensure_ascii=False)}
- Deep: {json.dumps(perceptions[2]['deep_beliefs'][:2], ensure_ascii=False)}

질문: 이 3개가 공유하는 **사고의 구조**는 무엇인가?

세계관 = 게시글별 분석이 아니라, 100개를 관통하는 하나의 구조

찾아야 할 것:
1. Explicit → Implicit → Deep로 연결되는 **논리 패턴**
2. 3개 모두에서 나타나는 **사고 방식**
3. "세상이 이렇게 작동한다"는 **믿음의 체계**

예시:
```
관찰된 현상 (Explicit)
  ↓ (어떤 추론 과정?)
합법적 가능성 무시하고 악의적 해석 (Implicit)
  ↓ (어떤 연결?)
숨겨진 세력/음모 존재 단정 (Implicit)
  ↓ (어떤 비약?)
이게 체제적 위협의 전조 (Deep)
```

JSON:
{{
  "common_structure": {{
    "step_1_observation": {{
      "pattern": "어떤 현상을 관찰하는가?",
      "examples": ["유심교체 정보 알았다", "건보공단 비리", "실종 글 증가"]
    }},
    "step_2_assumption": {{
      "pattern": "어떤 전제를 깔고 해석하는가?",
      "inference_rule": "합법적 가능성은 어떻게 배제하는가?",
      "examples": ["합법적으로는 알 수 없다", "카르텔이 존재", "무비자가 범죄 유입"]
    }},
    "step_3_hidden_actor": {{
      "pattern": "누가 배후에 있다고 보는가?",
      "connection_logic": "왜 숨겨진 세력을 상정하는가?",
      "examples": ["민주당이 통신사 협박", "복지부 카르텔", "중국 조직범죄"]
    }},
    "step_4_systemic_threat": {{
      "pattern": "이게 어떤 큰 위협의 신호인가?",
      "escalation_logic": "작은 징후 → 체제 위협으로 어떻게 비약하는가?",
      "examples": ["독재 재현", "카르텔 장악", "치안 붕괴"]
    }}
  }},
  "worldview_formula": "현상 X를 보면 → 합법적 Y는 무시하고 → 숨겨진 세력 Z가 → 체제적 위협 W로 향한다고 믿는다",
  "key_belief": "이 구조의 핵심 믿음은 무엇인가?",
  "is_this_worldview": true/false,
  "reason": "..."
}}
"""

    print("GPT-5로 공통 구조 분석 중...")
    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "구조 분석가. 표면이 아닌 사고 패턴을 본다."},
            {"role": "user", "content": structure_prompt}
        ],
        response_format={"type": "json_object"}
    )

    structure = json.loads(response.choices[0].message.content)

    print("\n" + "=" * 80)
    print("추출된 공통 구조")
    print("=" * 80)

    steps = structure['common_structure']

    print(f"\n1단계: {steps['step_1_observation']['pattern']}")
    print(f"   예시: {', '.join(steps['step_1_observation']['examples'][:2])}")

    print(f"\n2단계: {steps['step_2_assumption']['pattern']}")
    print(f"   추론 규칙: {steps['step_2_assumption']['inference_rule']}")
    print(f"   예시: {', '.join(steps['step_2_assumption']['examples'][:2])}")

    print(f"\n3단계: {steps['step_3_hidden_actor']['pattern']}")
    print(f"   연결 논리: {steps['step_3_hidden_actor']['connection_logic']}")
    print(f"   예시: {', '.join(steps['step_3_hidden_actor']['examples'][:2])}")

    print(f"\n4단계: {steps['step_4_systemic_threat']['pattern']}")
    print(f"   확대 논리: {steps['step_4_systemic_threat']['escalation_logic']}")
    print(f"   예시: {', '.join(steps['step_4_systemic_threat']['examples'][:2])}")

    print(f"\n\n세계관 공식:")
    print(f"  {structure['worldview_formula']}")

    print(f"\n핵심 믿음:")
    print(f"  {structure['key_belief']}")

    print(f"\n이게 세계관인가? {structure['is_this_worldview']}")
    print(f"  이유: {structure['reason']}")

    # Step 2: 검증 - 이 구조로 다른 글을 설명 가능한가?
    print("\n\n[Step 2] 검증: 이 구조로 새로운 글을 설명 가능한가?")
    print("=" * 80)

    # Get a different content
    test_content = supabase.table('contents')\
        .select('id, title, body')\
        .neq('body', '')\
        .limit(1)\
        .range(5, 5)\
        .execute().data[0]

    print(f"\n테스트 글: {test_content['title'][:60]}")

    verification_prompt = f"""
다음은 새로운 글입니다:

제목: {test_content['title']}
내용: {test_content['body'][:500]}

그리고 우리가 찾은 사고 구조:

{structure['worldview_formula']}

4단계 구조:
1. {steps['step_1_observation']['pattern']}
2. {steps['step_2_assumption']['pattern']} - {steps['step_2_assumption']['inference_rule']}
3. {steps['step_3_hidden_actor']['pattern']} - {steps['step_3_hidden_actor']['connection_logic']}
4. {steps['step_4_systemic_threat']['pattern']} - {steps['step_4_systemic_threat']['escalation_logic']}

질문:
1. 이 새 글도 같은 구조를 따르는가?
2. 4단계가 어떻게 나타나는가?
3. 만약 맞지 않는다면, 왜?

JSON:
{{
  "follows_structure": true/false,
  "step_1_found": {{"text": "...", "matches": true/false}},
  "step_2_found": {{"text": "...", "matches": true/false}},
  "step_3_found": {{"text": "...", "matches": true/false}},
  "step_4_found": {{"text": "...", "matches": true/false}},
  "structure_match_score": 0-4,
  "explanation": "..."
}}
"""

    print("\n검증 중...")
    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "구조 검증자"},
            {"role": "user", "content": verification_prompt}
        ],
        response_format={"type": "json_object"}
    )

    verification = json.loads(response.choices[0].message.content)

    print(f"\n구조 일치: {verification['follows_structure']}")
    print(f"매칭 점수: {verification['structure_match_score']}/4")

    for i in range(1, 5):
        step = verification[f'step_{i}_found']
        status = "✅" if step['matches'] else "❌"
        print(f"\n{status} {i}단계: {step['text'][:80]}")

    print(f"\n설명: {verification['explanation']}")

    # Final evaluation
    print("\n\n" + "=" * 80)
    print("최종 평가: 이게 진짜 '세계관'인가?")
    print("=" * 80)

    final_eval_prompt = f"""
우리가 찾은 구조:

{json.dumps(structure, ensure_ascii=False, indent=2)}

검증 결과:
- 3개 원래 글: 구조 공유함
- 1개 새 글: {verification['structure_match_score']}/4 매칭

이게 진짜 '세계관'인가?

세계관의 정의:
- 100개 글을 관통하는 일관된 사고 구조
- "세상이 이렇게 작동한다"는 믿음의 체계
- 게시글별 분석이 아니라, 전체를 연결하는 패턴

평가:
1. 이 구조가 "세상이 작동하는 방식"에 대한 믿음인가?
2. 이 구조로 다양한 주제(중국, 복지부, 민주당)를 설명 가능한가?
3. 이게 '일반적 사고'가 아닌 '특정 진영의 사고'인가?

JSON:
{{
  "is_real_worldview": true/false,
  "reason": "...",
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["약점1", "약점2"],
  "next_step": "..."
}}
"""

    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "최종 평가자"},
            {"role": "user", "content": final_eval_prompt}
        ],
        response_format={"type": "json_object"}
    )

    final_eval = json.loads(response.choices[0].message.content)

    print(f"\n진짜 세계관인가? {final_eval['is_real_worldview']}")
    print(f"\n이유: {final_eval['reason']}")

    print(f"\n강점:")
    for s in final_eval['strengths']:
        print(f"  ✅ {s}")

    print(f"\n약점:")
    for w in final_eval['weaknesses']:
        print(f"  ⚠️  {w}")

    print(f"\n다음 단계: {final_eval['next_step']}")

    # Save
    output = {
        "common_structure": structure,
        "verification_result": verification,
        "final_evaluation": final_eval
    }

    with open('/tmp/worldview_structure_definition.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n\n✅ 결과 저장: /tmp/worldview_structure_definition.json")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
