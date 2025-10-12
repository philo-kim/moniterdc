#!/usr/bin/env python3
"""
두 접근 비교: Claims vs Core Beliefs

목적: 어느 것이 진짜 세계관인가?
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def call_gpt(prompt, model="gpt-4o-mini"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

print("="*80)
print("Claims vs Core Beliefs 비교")
print("="*80)

# Load core beliefs
with open('_core_beliefs_extracted.json', 'r', encoding='utf-8') as f:
    beliefs_data = json.loads(f.read())

# 테스트 질문 3개
test_questions = [
    "조희대 대법원장 국정감사, 나경원 의원 반대 - 왜?",
    "민주당이 의료 개혁안을 발표했어. 어떻게 생각해?",
    "민주당 의원이 지역구 민원을 해결했대. 어떻게 볼까?"
]

for i, question in enumerate(test_questions, 1):
    print(f"\n{'='*80}")
    print(f"질문 {i}: {question}")
    print("="*80)

    # Approach 1: Claims 기반 (제 기존 방식)
    print(f"\n[Approach 1: Claims 기반]")
    print("-"*80)

    claims = [
        "민주당이 개인정보를 맘대로 들춰보고 있다",
        "지들 맘에 안드는 판사 사찰하려고 통신사 협박해서 정보를 얻어냈다"
    ]

    prompt1 = f"""
당신은 DC 게시글 작성자입니다.

과거 주장들:
{chr(10).join(f'- "{claim}"' for claim in claims)}

질문: {question}

위 주장들을 참고해서 답변하세요. 2문장.
"""

    answer1 = call_gpt(prompt1)
    print(answer1)

    # Approach 2: Core Beliefs 기반
    print(f"\n[Approach 2: Core Beliefs 기반]")
    print("-"*80)

    core_belief = beliefs_data['worldview_structure']['how_world_works']
    key_actors = beliefs_data['worldview_structure']['key_actors']

    prompt2 = f"""
당신은 이런 세계관을 가진 사람입니다:

세상이 작동하는 방식:
"{core_belief}"

주요 행위자:
{json.dumps(key_actors, ensure_ascii=False, indent=2)}

질문: {question}

당신의 세계관으로 해석하세요. 2문장.
"""

    answer2 = call_gpt(prompt2)
    print(answer2)

# 최종 비교
print(f"\n{'='*80}")
print("최종 분석: 어느 것이 진짜 세계관인가?")
print("="*80)

comparison_prompt = f"""
두 가지 접근을 비교 분석하세요:

Approach 1 (Claims 기반):
- "민주당이 판사 사찰한다" 같은 구체적 주장들 사용
- 유사한 주장을 찾아서 답변 생성

Approach 2 (Core Beliefs 기반):
- "권력자는 개인정보를 자신의 이익을 위해 쓴다" 같은 기본 믿음 사용
- 믿음 체계로 모든 사건 해석

질문:
1. 어느 것이 "세계관"에 더 가까운가?
2. 어느 것이 새로운 사건을 더 잘 해석하는가?
3. 어느 것이 더 일관된 해석을 제공하는가?

분석:
"""

analysis = call_gpt(comparison_prompt, model="gpt-4o")
print(analysis)

print(f"\n{'='*80}")
print("결론")
print("="*80)
print("""
Claims 접근:
- 장점: 구체적, 실제 표현 사용
- 단점: 유사한 사건에만 적용 가능, 본질이 아님

Core Beliefs 접근:
- 장점: 모든 사건 해석 가능, 일관성, 본질적
- 단점: 표현이 추상적일 수 있음

해결책: 두 가지 결합
1. Core Beliefs로 해석 (세계관의 본질)
2. Claims에서 구체적 표현 차용 (authentic voice)
""")
