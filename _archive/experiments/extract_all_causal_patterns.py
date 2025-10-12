#!/usr/bin/env python3
"""
88개 Perception에서 인과 패턴 추출

목적: 실제 데이터에서 반복되는 인과 왜곡 패턴들을 추출
"""

import os
import json
from supabase import create_client
from openai import OpenAI
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def call_gpt(prompt, model="gpt-4o-mini"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"GPT error: {e}")
        return None

print("="*80)
print("88개 Perception에서 인과 패턴 추출")
print("="*80)

# Load all perceptions with their content
print("\n[1] 데이터 로드...")
perceptions = supabase.table('perceptions').select('*').execute().data
print(f"  Loaded {len(perceptions)} perceptions")

# Get content for each perception
perception_with_content = []
for p in perceptions:
    content_id = p.get('content_id')
    if content_id:
        content = supabase.table('contents').select('title, body').eq('id', content_id).execute().data
        if content:
            p['content'] = content[0]
            perception_with_content.append(p)

print(f"  {len(perception_with_content)} perceptions with content")

# Extract causal patterns
print(f"\n[2] 인과 패턴 추출 중... (GPT-4o-mini 사용)")
patterns = []

for i, p in enumerate(perception_with_content[:20], 1):  # 먼저 20개만
    print(f"  [{i}/20] {p['content']['title'][:50]}...")

    claims = p.get('claims', [])
    if isinstance(claims, str):
        try:
            claims = json.loads(claims)
        except:
            claims = []

    # GPT로 인과 패턴 추출
    prompt = f"""
다음 게시글과 추출된 주장들에서 인과 관계 왜곡 패턴을 찾으세요.

게시글: {p['content']['body'][:600]}

주장들: {json.dumps(claims, ensure_ascii=False)}

JSON 형식:
{{
  "found": true/false,
  "trigger": "어떤 사실/사건",
  "inference": "그로부터 추론",
  "assumption": "숨겨진 가정",
  "generalization": "일반화 (X는 언제나 Y한다)",
  "evidence_included": ["포함된 증거들"],
  "evidence_excluded": ["배제된 가능성들"],
  "pattern_title": "패턴 제목 (짧게)",
  "confidence": 1-10
}}

인과 관계가 명확하지 않으면 found: false
"""

    result = call_gpt(prompt)
    if result:
        try:
            pattern = json.loads(result)
            if pattern.get('found') and pattern.get('confidence', 0) >= 6:
                pattern['perception_id'] = p['id']
                pattern['content_title'] = p['content']['title']
                patterns.append(pattern)
                print(f"     ✓ 패턴 발견: {pattern.get('pattern_title', 'N/A')}")
        except Exception as e:
            print(f"     ✗ Parse error: {e}")

print(f"\n[3] 추출 완료")
print(f"  총 {len(patterns)}개 인과 패턴 발견")

# Save results
with open('_extracted_causal_patterns.json', 'w', encoding='utf-8') as f:
    json.dump(patterns, f, ensure_ascii=False, indent=2)

print(f"\n결과 저장: _extracted_causal_patterns.json")

# Pattern analysis
print(f"\n[4] 패턴 분석")
print("-"*80)

# Group by pattern_title (유사한 패턴 찾기)
pattern_groups = defaultdict(list)
for p in patterns:
    title = p.get('pattern_title', '').lower()
    # Simple grouping by keywords
    if '사찰' in title or 'surveillance' in title.lower():
        pattern_groups['사찰 패턴'].append(p)
    elif '보복' in title or '탄압' in title:
        pattern_groups['정치보복 패턴'].append(p)
    elif '조작' in title or '여론' in title:
        pattern_groups['여론조작 패턴'].append(p)
    else:
        pattern_groups['기타'].append(p)

print(f"\n패턴 그룹:")
for group_name, group_patterns in pattern_groups.items():
    print(f"\n  [{group_name}] {len(group_patterns)}개")
    for gp in group_patterns[:3]:  # 샘플 3개
        print(f"    - {gp.get('pattern_title')}")
        print(f"      Generalization: {gp.get('generalization', 'N/A')[:80]}...")

# Extract most common generalizations
generalizations = [p.get('generalization', '') for p in patterns if p.get('generalization')]
print(f"\n자주 나타나는 일반화:")
for i, gen in enumerate(set(generalizations)[:5], 1):
    count = generalizations.count(gen)
    print(f"  {i}. {gen[:100]}... ({count}회)")

print("\n" + "="*80)
print(f"다음 단계: 이 패턴들로 새로운 질문에 답할 수 있는지 테스트")
print("="*80)
