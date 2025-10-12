#!/usr/bin/env python3
"""
V3 프롬프트로 10개 게시글 테스트

목적: 최고 성능 프롬프트로 실제 데이터 추출
"""

import os
import json
from supabase import create_client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def call_gpt(prompt, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

print("="*80)
print("V3 프롬프트로 10개 게시글 테스트")
print("="*80)

# 실제 게시글 10개
contents = supabase.table('contents').select('id, title, body').limit(10).execute().data

results = []
total_specificity = 0

for i, content in enumerate(contents, 1):
    print(f"\n{'='*80}")
    print(f"[{i}/10] {content['title'][:60]}...")
    print("="*80)

    body = content['body'][:800]

    # V3 Prompt (최고 성능)
    prompt_v3 = f"""
다음 게시글을 분석하세요.

원글:
{body}

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

    result = call_gpt(prompt_v3)
    extracted = json.loads(result)

    print(f"\n핵심 질문:")
    for q in extracted.get('key_questions', [])[:3]:
        print(f"  - {q}")

    print(f"\n구체적 표현:")
    for expr in extracted.get('specific_expressions', [])[:5]:
        print(f"  - {expr}")

    print(f"\n보존된 주장:")
    for claim in extracted.get('preserved_claims', [])[:3]:
        print(f"  - {claim}")

    # 특정성 평가
    eval_prompt = f"""
원문:
{body}

추출 결과:
{json.dumps(extracted, ensure_ascii=False)}

평가:
1. 원문의 특정한 표현이 보존되었는가?
2. 질문이 있다면 보존되었는가?
3. 구체적 인물/기관/사건이 보존되었는가?

JSON:
{{
  "specificity_score": 1-10,
  "preserved_well": ["잘 보존된 부분들"],
  "lost": ["손실된 특정성"]
}}
"""

    eval_result = call_gpt(eval_prompt, model="gpt-4o-mini")
    evaluation = json.loads(eval_result)

    score = evaluation.get('specificity_score', 0)
    total_specificity += score

    print(f"\n특정성 점수: {score}/10")
    if evaluation.get('lost'):
        print(f"손실: {', '.join(evaluation.get('lost', [])[:2])}")

    results.append({
        "content_id": content['id'],
        "title": content['title'],
        "extracted": extracted,
        "evaluation": evaluation
    })

# 종합 평가
avg_specificity = total_specificity / len(results)

print(f"\n{'='*80}")
print("종합 평가")
print("="*80)
print(f"\n평균 특정성: {avg_specificity:.1f}/10")

if avg_specificity >= 7:
    print("\n✓ 성공: V3 프롬프트가 특정성을 보존합니다!")
    print("\n다음 단계: Layer 1→2 테스트 (추출된 것들을 clustering)")
else:
    print("\n✗ 실패: 프롬프트 추가 개선 필요")

# 저장
with open('_v3_extraction_10_posts.json', 'w', encoding='utf-8') as f:
    json.dump({
        "average_specificity": avg_specificity,
        "results": results
    }, f, ensure_ascii=False, indent=2)

print(f"\n결과 저장: _v3_extraction_10_posts.json")
print("="*80)
