#!/usr/bin/env python3
"""
실제 데이터로 인과 관계 추출 테스트

목적: 이론이 아닌 실제 DC 게시글에서 인과 패턴을 추출할 수 있는지 검증
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
print("실제 데이터로 인과 관계 추출 테스트")
print("="*80)

# 실제 게시글 1개로 테스트
content = supabase.table('contents').select('title, body').limit(1).execute().data[0]

print(f"\n[원문]")
print(f"제목: {content['title']}")
print(f"내용:\n{content['body'][:500]}...")

# GPT로 인과 관계 추출 시도
prompt = f"""
다음 DC 게시글에서 "인과 관계 왜곡 패턴"을 추출하세요.

게시글:
제목: {content['title']}
내용: {content['body']}

추출할 것:
1. trigger: 어떤 사실/사건을 언급하는가?
2. inference: 그것으로부터 무엇을 추론하는가?
3. assumption: 어떤 가정을 깔고 있는가? (명시되지 않았지만 전제되는 것)
4. generalization: "X는 언제나 Y한다" 같은 일반화가 있는가?
5. evidence_selection: 어떤 증거를 선택하고, 어떤 것을 배제하는가?

JSON 형식:
{{
  "found": true/false,  // 인과 관계가 있는지
  "trigger": "사실/사건",
  "inference": "추론",
  "assumption": "가정",
  "generalization": "일반화",
  "evidence_selection": {{
    "included": ["포함된 증거들"],
    "excluded": ["배제된 가능성들"]
  }},
  "confidence": 1-10
}}

인과 관계가 없으면 found: false로 반환.
"""

result = call_gpt(prompt)
pattern = json.loads(result)

print(f"\n[추출 결과]")
print(json.dumps(pattern, ensure_ascii=False, indent=2))

if pattern.get('found'):
    print(f"\n✓ 인과 관계 패턴 발견!")
    print(f"  Confidence: {pattern.get('confidence')}/10")
else:
    print(f"\n✗ 인과 관계 없음")

# 결과 저장
with open('_test_causal_extraction_result.json', 'w', encoding='utf-8') as f:
    json.dump({
        "content": content,
        "extracted_pattern": pattern
    }, f, ensure_ascii=False, indent=2)

print(f"\n결과 저장: _test_causal_extraction_result.json")

# 추가: 5개 샘플로 성공률 측정
print(f"\n{'='*80}")
print("5개 샘플로 성공률 측정")
print(f"{'='*80}")

contents = supabase.table('contents').select('title, body').limit(5).execute().data
success_count = 0

for i, c in enumerate(contents, 1):
    print(f"\n[{i}/5] {c['title'][:50]}...")

    prompt = f"""
    다음 게시글에서 인과 관계 왜곡 패턴을 찾으세요.

    내용: {c['body'][:800]}

    JSON:
    {{
      "found": true/false,
      "confidence": 1-10
    }}
    """

    result = call_gpt(prompt, model="gpt-4o-mini")
    pattern = json.loads(result)

    if pattern.get('found'):
        success_count += 1
        print(f"  ✓ 발견 (confidence: {pattern.get('confidence')})")
    else:
        print(f"  ✗ 없음")

print(f"\n성공률: {success_count}/5 ({success_count/5*100:.0f}%)")
print("="*80)
