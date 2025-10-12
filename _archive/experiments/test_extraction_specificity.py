#!/usr/bin/env python3
"""
추출 특정성 테스트

목적: 원글 → 추출 과정에서 특정성이 보존되는가?
방법: 프롬프트 버전별 비교 → 개선 → 재테스트
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def call_gpt(prompt, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

print("="*80)
print("추출 특정성 테스트")
print("="*80)

# 실제 원글
original = """
유심교체를 어떻게 알아ㅋㅋㅋㅋ미친
지들 맘에 안드는 판사 사찰하려고 통신사 협박해서 얻어낸 정보
"""

print(f"\n[원글]")
print(original.strip())

# Prompt Version 1: 기존 방식 (추상화)
print(f"\n{'='*80}")
print("Prompt V1: 기존 방식 (추상화)")
print("="*80)

prompt_v1 = f"""
다음 게시글에서 주장을 추출하세요.

원글:
{original}

JSON:
{{
  "claims": ["주장들"]
}}
"""

result_v1 = call_gpt(prompt_v1)
extracted_v1 = json.loads(result_v1)

print("\n추출된 claims:")
for claim in extracted_v1.get('claims', []):
    print(f"  - {claim}")

# Prompt Version 2: 구체적 표현 보존 강조
print(f"\n{'='*80}")
print("Prompt V2: 구체적 표현 보존")
print("="*80)

prompt_v2 = f"""
다음 게시글에서 주장을 추출하세요.

원글:
{original}

규칙:
1. 원문의 표현을 최대한 그대로 사용
2. 인물명, 고유명사 보존
3. 특정한 어휘 보존 ("어떻게 알아", "맘에 안드는", "협박" 등)

JSON:
{{
  "claims": ["주장들"]
}}
"""

result_v2 = call_gpt(prompt_v2)
extracted_v2 = json.loads(result_v2)

print("\n추출된 claims:")
for claim in extracted_v2.get('claims', []):
    print(f"  - {claim}")

# Prompt Version 3: 특정성 보존 + 구조 추출
print(f"\n{'='*80}")
print("Prompt V3: 특정성 보존 + 구조")
print("="*80)

prompt_v3 = f"""
다음 게시글을 분석하세요.

원글:
{original}

추출할 것:
1. 핵심 질문/의문: 원문 그대로
2. 구체적 표현: 특정한 단어들 그대로
3. 논리 구조: A → B 연결을 원문 표현으로

절대 추상화하지 마세요. 원문 그대로.

JSON:
{{
  "key_questions": ["원문의 질문들"],
  "specific_expressions": ["특정한 표현들"],
  "logic_structure": {{
    "from": "원문 표현",
    "to": "원문 표현",
    "connection": "어떻게 연결되는가"
  }},
  "preserved_claims": ["원문을 최대한 보존한 주장들"]
}}
"""

result_v3 = call_gpt(prompt_v3)
extracted_v3 = json.loads(result_v3)

print("\n핵심 질문:")
for q in extracted_v3.get('key_questions', []):
    print(f"  - {q}")

print("\n구체적 표현:")
for expr in extracted_v3.get('specific_expressions', []):
    print(f"  - {expr}")

print("\n논리 구조:")
logic = extracted_v3.get('logic_structure', {})
print(f"  {logic.get('from')} → {logic.get('to')}")
print(f"  연결: {logic.get('connection')}")

print("\n보존된 주장:")
for claim in extracted_v3.get('preserved_claims', []):
    print(f"  - {claim}")

# 평가: 어느 버전이 특정성을 보존했는가?
print(f"\n{'='*80}")
print("평가: 특정성 보존도")
print("="*80)

eval_prompt = f"""
원문:
{original}

3가지 추출 결과를 비교하세요.

V1: {json.dumps(extracted_v1, ensure_ascii=False)}
V2: {json.dumps(extracted_v2, ensure_ascii=False)}
V3: {json.dumps(extracted_v3, ensure_ascii=False)}

평가:
1. 특정성 보존 (1-10): 원문의 특정한 표현이 유지되었는가?
2. "어떻게 알아" 같은 핵심 질문이 보존되었는가?
3. "지들 맘에 안드는" 같은 특정 표현이 유지되었는가?

JSON:
{{
  "v1_score": {{"specificity": X, "key_question": true/false, "specific_expr": true/false}},
  "v2_score": {{"specificity": X, "key_question": true/false, "specific_expr": true/false}},
  "v3_score": {{"specificity": X, "key_question": true/false, "specific_expr": true/false}},
  "best": "v1/v2/v3",
  "why": "이유",
  "improvement_needed": "개선 방향"
}}
"""

eval_result = call_gpt(eval_prompt)
evaluation = json.loads(eval_result)

print("\n평가 결과:")
for v in ['v1', 'v2', 'v3']:
    score = evaluation.get(f'{v}_score', {})
    print(f"\n{v.upper()}:")
    print(f"  특정성: {score.get('specificity')}/10")
    print(f"  핵심 질문 보존: {'✓' if score.get('key_question') else '✗'}")
    print(f"  특정 표현 보존: {'✓' if score.get('specific_expr') else '✗'}")

print(f"\n최고: {evaluation.get('best').upper()}")
print(f"이유: {evaluation.get('why')}")
print(f"\n개선 필요: {evaluation.get('improvement_needed')}")

# 개선된 Prompt Version 4
print(f"\n{'='*80}")
print("Prompt V4: 평가 기반 개선")
print("="*80)

improvement = evaluation.get('improvement_needed', '')

prompt_v4 = f"""
다음 게시글을 분석하세요.

원글:
{original}

추출 규칙:
1. 질문 형태는 절대 바꾸지 말고 그대로 ("어떻게 알아")
2. 감정 표현 보존 ("ㅋㅋㅋㅋ미친")
3. 구체적 표현 그대로 ("지들 맘에 안드는", "통신사 협박")
4. 추상화 금지 (❌ "불법 획득" → ✓ "통신사 협박해서 얻어냄")

개선 사항:
{improvement}

JSON:
{{
  "preserved_text": ["원문 그대로 보존한 부분들"],
  "key_question": "핵심 질문 (원문 그대로)",
  "specific_actors": ["구체적 인물/기관"],
  "specific_actions": ["구체적 행동 표현"],
  "logic_chain": [
    {{"step": "A (원문 표현)", "next": "B (원문 표현)"}}
  ]
}}
"""

result_v4 = call_gpt(prompt_v4)
extracted_v4 = json.loads(result_v4)

print("\n보존된 원문:")
for text in extracted_v4.get('preserved_text', []):
    print(f"  - {text}")

print(f"\n핵심 질문: {extracted_v4.get('key_question')}")

print(f"\n구체적 인물/기관:")
for actor in extracted_v4.get('specific_actors', []):
    print(f"  - {actor}")

print(f"\n구체적 행동:")
for action in extracted_v4.get('specific_actions', []):
    print(f"  - {action}")

print(f"\n논리 체인:")
for step in extracted_v4.get('logic_chain', []):
    print(f"  {step.get('step')} → {step.get('next')}")

# 최종 검증
print(f"\n{'='*80}")
print("최종 검증: V4가 특정성을 보존했는가?")
print("="*80)

verify_prompt = f"""
원문:
{original}

V4 추출 결과:
{json.dumps(extracted_v4, ensure_ascii=False, indent=2)}

검증:
1. "어떻게 알아"가 보존되었는가?
2. "지들 맘에 안드는 판사"가 보존되었는가?
3. "통신사 협박해서"가 보존되었는가?
4. 원문의 특정성이 유지되었는가?

JSON:
{{
  "question_preserved": true/false,
  "expression_preserved": true/false,
  "action_preserved": true/false,
  "overall_specificity": 1-10,
  "success": true/false,
  "next_improvement": "다음 개선 방향"
}}
"""

verify_result = call_gpt(verify_prompt)
verification = json.loads(verify_result)

print(f"\n검증 결과:")
print(f"  핵심 질문 보존: {'✓' if verification.get('question_preserved') else '✗'}")
print(f"  특정 표현 보존: {'✓' if verification.get('expression_preserved') else '✗'}")
print(f"  구체적 행동 보존: {'✓' if verification.get('action_preserved') else '✗'}")
print(f"  전체 특정성: {verification.get('overall_specificity')}/10")
print(f"\n성공: {'✓' if verification.get('success') else '✗'}")
print(f"\n다음 개선: {verification.get('next_improvement')}")

# 결과 저장
with open('_extraction_specificity_test.json', 'w', encoding='utf-8') as f:
    json.dump({
        "original": original,
        "versions": {
            "v1": extracted_v1,
            "v2": extracted_v2,
            "v3": extracted_v3,
            "v4": extracted_v4
        },
        "evaluation": evaluation,
        "verification": verification
    }, f, ensure_ascii=False, indent=2)

print(f"\n결과 저장: _extraction_specificity_test.json")

if verification.get('success'):
    print(f"\n{'='*80}")
    print("✓ 성공: V4 프롬프트가 특정성을 보존합니다!")
    print("다음 단계: 이 프롬프트로 10개 게시글 테스트")
    print("="*80)
else:
    print(f"\n{'='*80}")
    print("✗ 실패: 추가 개선 필요")
    print(f"개선 방향: {verification.get('next_improvement')}")
    print("="*80)
