#!/usr/bin/env python3
"""
실제 Claims로 최종 검증

목적: 지귀연 게시글의 실제 claims를 사용해서 조희대 질문에 답할 수 있는지 검증
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
print("실제 Claims로 최종 검증")
print("="*80)

# 실제 claims from 지귀연 게시글
real_claims = [
    "민주당이 개인정보를 맘대로 들춰보고 있다",
    "민주당이 개인 사찰을 했다고 자백한 수준",
    "지들 맘에 안드는 판사 사찰하려고 통신사 협박해서 정보를 얻어냈다"
]

original_post = """
유심교체를 어떻게 알아ㅋㅋㅋㅋ미친
지들 맘에 안드는 판사 사찰하려고 통신사 협박해서 얻어낸 정보
"""

test_question = "조희대 대법원장을 국정감사에 부르는 것을 나경원 의원이 반대하고 있어. 그들은 어떻게 생각하기에 이렇게 행동하는거 같아?"

print(f"\n[실제 DC 게시글 원문]")
print(original_post.strip())

print(f"\n[추출된 Claims]")
for claim in real_claims:
    print(f"  - {claim}")

print(f"\n[테스트 질문]")
print(f"  {test_question}")

# Method 1: Claims 없이
print(f"\n{'='*80}")
print("Method 1: Claims 없이 (Baseline)")
print("="*80)

prompt1 = f"""
질문: {test_question}

DC 게시글 작성자처럼 2-3문장으로 답변하세요.
"""

answer1 = call_gpt(prompt1)
print(f"\n{answer1}")

# Method 2: Claims 사용
print(f"\n{'='*80}")
print("Method 2: 실제 Claims 사용")
print("="*80)

prompt2 = f"""
당신은 DC 게시글 작성자입니다.

당신이 과거에 한 주장들:
{chr(10).join(f'- "{claim}"' for claim in real_claims)}

당신이 실제로 쓴 표현:
"{original_post.strip()}"

질문: {test_question}

위 주장들과 표현을 사용해서, 당신의 시각으로 답변하세요.
반드시 위 주장에 나온 구체적인 표현을 사용하세요. 2-3문장.
"""

answer2 = call_gpt(prompt2)
print(f"\n{answer2}")

# Method 3: 인과 패턴 명시
print(f"\n{'='*80}")
print("Method 3: 인과 패턴 명시")
print("="*80)

prompt3 = f"""
당신은 DC 게시글 작성자입니다.

당신의 세계관:
- Trigger: 민주당이 X 정보를 알고 있다
- Inference: 불법 사찰로 얻었다
- Evidence: "유심교체를 어떻게 알아" = 사찰의 증거
- Generalization: 민주당은 언제나 판사 사찰을 한다

과거 증거:
"지들 맘에 안드는 판사 사찰하려고 통신사 협박해서 얻어낸 정보"

질문: {test_question}

당신의 논리 패턴대로, 과거 증거를 인용하면서 답변하세요.
실제 표현 그대로 사용. 2-3문장.
"""

answer3 = call_gpt(prompt3)
print(f"\n{answer3}")

# Comparison
print(f"\n{'='*80}")
print("GPT-4o 평가")
print("="*80)

eval_prompt = f"""
원문 DC 게시글:
"{original_post.strip()}"

질문: {test_question}

답변 1 (Claims 없음): {answer1}

답변 2 (Claims 사용): {answer2}

답변 3 (인과 패턴 명시): {answer3}

평가:
1. Authenticity (1-10): 원문 작성자 같은가?
2. Specificity (1-10): 구체적 표현 사용하는가?
3. 원문과의 유사도 (1-10): 원문 표현을 사용하는가?

JSON:
{{
  "답변1": {{"authenticity": X, "specificity": X, "similarity": X}},
  "답변2": {{"authenticity": X, "specificity": X, "similarity": X}},
  "답변3": {{"authenticity": X, "specificity": X, "similarity": X}},
  "best": 1/2/3,
  "reason": "이유"
}}
"""

eval_result = call_gpt(eval_prompt, model="gpt-4o")

# Parse JSON (코드 블록 제거)
eval_result_clean = eval_result.replace('```json', '').replace('```', '').strip()
evaluation = json.loads(eval_result_clean)

print(f"\n평가 결과:")
for i in range(1, 4):
    key = f'답변{i}'
    print(f"\n{key}:")
    print(f"  Authenticity: {evaluation[key]['authenticity']}/10")
    print(f"  Specificity: {evaluation[key]['specificity']}/10")
    print(f"  Similarity: {evaluation[key]['similarity']}/10")
    print(f"  평균: {sum(evaluation[key].values())/3:.1f}/10")

print(f"\n최고 답변: {evaluation['best']}")
print(f"이유: {evaluation['reason']}")

# Save
with open('_final_test_result.json', 'w', encoding='utf-8') as f:
    json.dump({
        "question": test_question,
        "original_post": original_post.strip(),
        "claims": real_claims,
        "answers": {
            "baseline": answer1,
            "with_claims": answer2,
            "with_pattern": answer3
        },
        "evaluation": evaluation
    }, f, ensure_ascii=False, indent=2)

print(f"\n결과 저장: _final_test_result.json")

# Final verdict
print(f"\n{'='*80}")
if evaluation['best'] in [2, 3]:
    best_key = f"답변{evaluation['best']}"
    best_avg = sum(evaluation[best_key].values())/3
    baseline_avg = sum(evaluation['답변1'].values())/3
    diff = best_avg - baseline_avg
    print("✓ 성공: Claims/패턴 사용이 더 authentic한 답변 생성!")
    print(f"  평균 점수 차이: {diff:.1f}점")
else:
    print("✗ 실패: Claims/패턴이 도움되지 않음")
print("="*80)
