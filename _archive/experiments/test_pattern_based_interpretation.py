#!/usr/bin/env python3
"""
패턴 기반 이벤트 해석 테스트

목적: 추출한 인과 패턴으로 새로운 질문에 답할 수 있는지 검증
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
print("패턴 기반 이벤트 해석 테스트")
print("="*80)

# Load extracted patterns
with open('_extracted_causal_patterns.json', 'r', encoding='utf-8') as f:
    patterns = json.load(f)

print(f"\n[1] 로드된 패턴: {len(patterns)}개")

# 사찰 관련 패턴만 선택 (우리가 테스트하려는 주제)
relevant_patterns = []
for p in patterns:
    title = p.get('pattern_title', '').lower()
    generalization = p.get('generalization', '').lower()
    trigger = p.get('trigger', '').lower()

    # "사찰", "개인정보", "판사" 등이 포함된 패턴
    if any(keyword in title + generalization + trigger for keyword in ['사찰', '개인정보', '판사', '민주당']):
        relevant_patterns.append(p)

print(f"  관련 패턴 (사찰/민주당): {len(relevant_patterns)}개")

if not relevant_patterns:
    print("\n⚠️ 관련 패턴이 없습니다. 더 많은 perception을 처리해야 합니다.")
    exit()

# Test question
test_question = "조희대 대법원장을 국정감사에 부르는 것을 나경원 의원이 반대하고 있어. 그들은 어떻게 생각하기에 이렇게 행동하는거 같아?"

print(f"\n[2] 테스트 질문:")
print(f"  {test_question}")

# Method 1: 패턴 없이 (Baseline)
print(f"\n[3] Method 1: 패턴 없이 답변 생성 (Baseline)")
print("-"*80)

prompt_baseline = f"""
당신은 DC 게시글을 분석하는 AI입니다.

질문: {test_question}

DC 게시글 작성자들의 시각에서 2-3문장으로 답변하세요.
"""

answer_baseline = call_gpt(prompt_baseline)
print(f"답변: {answer_baseline}")

# Method 2: 패턴 사용
print(f"\n[4] Method 2: 패턴 사용하여 답변 생성")
print("-"*80)

# 패턴 정보를 프롬프트에 포함
patterns_text = "\n".join([
    f"패턴 {i+1}:\n"
    f"  Trigger: {p.get('trigger', 'N/A')}\n"
    f"  Inference: {p.get('inference', 'N/A')}\n"
    f"  Generalization: {p.get('generalization', 'N/A')}\n"
    f"  Evidence included: {', '.join(p.get('evidence_included', [])[:3])}\n"
    for i, p in enumerate(relevant_patterns[:3])  # 상위 3개만
])

prompt_with_patterns = f"""
당신은 DC 게시글 작성자의 세계관을 가진 사람입니다.

당신의 사고 패턴:
{patterns_text}

질문: {test_question}

위의 사고 패턴을 사용하여, 마치 DC 게시글 작성자처럼 답변하세요.
실제 표현을 사용하고, 2-3문장으로.
"""

answer_with_patterns = call_gpt(prompt_with_patterns)
print(f"답변: {answer_with_patterns}")

# Comparison
print(f"\n[5] 비교 평가 (GPT-4o)")
print("="*80)

eval_prompt = f"""
동일한 질문에 대한 두 가지 답변을 비교하세요.

질문: {test_question}

답변 1 (패턴 없음): {answer_baseline}

답변 2 (패턴 사용): {answer_with_patterns}

평가 기준:
1. Authenticity (1-10): 실제 DC 게시글 작성자 같은가?
2. Specificity (1-10): 구체적인 사건/인물/표현을 사용하는가?
3. Causal Logic (1-10): 인과 관계 논리가 명확한가?

JSON:
{{
  "답변1": {{"authenticity": 1-10, "specificity": 1-10, "causal_logic": 1-10}},
  "답변2": {{"authenticity": 1-10, "specificity": 1-10, "causal_logic": 1-10}},
  "best": 1 or 2,
  "reason": "이유"
}}
"""

eval_result = call_gpt(eval_prompt, model="gpt-4o")
try:
    evaluation = json.loads(eval_result)

    print(f"\n답변 1 (패턴 없음):")
    print(f"  Authenticity: {evaluation['답변1']['authenticity']}/10")
    print(f"  Specificity: {evaluation['답변1']['specificity']}/10")
    print(f"  Causal Logic: {evaluation['답변1']['causal_logic']}/10")

    print(f"\n답변 2 (패턴 사용):")
    print(f"  Authenticity: {evaluation['답변2']['authenticity']}/10")
    print(f"  Specificity: {evaluation['답변2']['specificity']}/10")
    print(f"  Causal Logic: {evaluation['답변2']['causal_logic']}/10")

    print(f"\n최고 답변: {evaluation['best']}")
    print(f"이유: {evaluation['reason']}")

    # Save results
    with open('_pattern_interpretation_test.json', 'w', encoding='utf-8') as f:
        json.dump({
            "question": test_question,
            "baseline_answer": answer_baseline,
            "pattern_based_answer": answer_with_patterns,
            "evaluation": evaluation,
            "patterns_used": relevant_patterns[:3]
        }, f, ensure_ascii=False, indent=2)

    print(f"\n결과 저장: _pattern_interpretation_test.json")

except Exception as e:
    print(f"평가 파싱 실패: {e}")
    print(f"Raw result: {eval_result}")

print("\n" + "="*80)
if evaluation.get('best') == 2:
    print("✓ 성공: 패턴 기반 답변이 더 authentic!")
else:
    print("✗ 실패: 패턴 없이도 충분히 답변 가능")
print("="*80)
