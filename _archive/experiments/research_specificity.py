#!/usr/bin/env python3
"""
특정성(Specificity) 연구

목적: 실제 DC 게시글에서 "저들만의 특정한 것"을 발견
방법: 데이터 분석 → 가설 → 검증 → 개선
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
print("특정성 연구: 저들만의 것을 발견하기")
print("="*80)

# 실제 DC 게시글 10개 로드
contents = supabase.table('contents').select('id, title, body').limit(10).execute().data

research_results = []

for i, content in enumerate(contents, 1):
    print(f"\n{'='*80}")
    print(f"게시글 {i}/10: {content['title'][:50]}...")
    print("="*80)

    body = content['body'][:1000]
    print(f"\n원문:\n{body}\n")

    # Research Question: 이 글에서 "특정한 것"은 무엇인가?
    prompt = f"""
다음 DC 게시글을 분석하세요.

원문:
{body}

질문들:
1. 이 글이 "특정한" 이유는 무엇인가?
   - 일반인이라면 어떻게 볼까?
   - 이 사람은 왜 다르게 보는가?

2. 생략된 전제는 무엇인가?
   - 명시되지 않았지만 전제되는 것
   - 당연시하는 것

3. 독특한 연결고리는?
   - A에서 B로 넘어갈 때 중간 단계
   - 왜 이 연결이 당연한가?

4. 사용하는 언어/프레임은?
   - 특정 단어 선택
   - 반복되는 표현

JSON:
{{
  "what_makes_it_specific": "이 글이 특정한 이유",
  "general_person_view": "일반인이라면 어떻게 볼까",
  "this_person_view": "이 사람은 어떻게 보는가",
  "why_different": "왜 다른가",
  "hidden_premises": ["생략된 전제들"],
  "unique_connections": [
    {{"from": "A", "to": "B", "missing_step": "중간 단계", "why_automatic": "왜 자동인가"}}
  ],
  "language_patterns": ["특정 단어/프레임"],
  "specificity_score": 1-10
}}
"""

    result = call_gpt(prompt)
    analysis = json.loads(result)

    print(f"[분석 결과]")
    print(f"특정성 점수: {analysis.get('specificity_score')}/10")
    print(f"\n특정한 이유: {analysis.get('what_makes_it_specific')}")
    print(f"\n일반인 시각: {analysis.get('general_person_view')}")
    print(f"이 사람 시각: {analysis.get('this_person_view')}")
    print(f"차이 이유: {analysis.get('why_different')}")

    print(f"\n생략된 전제:")
    for premise in analysis.get('hidden_premises', [])[:3]:
        print(f"  - {premise}")

    print(f"\n독특한 연결:")
    for conn in analysis.get('unique_connections', [])[:2]:
        print(f"  {conn.get('from')} → {conn.get('to')}")
        print(f"    중간: {conn.get('missing_step')}")
        print(f"    이유: {conn.get('why_automatic')}")

    print(f"\n언어 패턴:")
    for pattern in analysis.get('language_patterns', [])[:3]:
        print(f"  - {pattern}")

    research_results.append({
        "content_id": content['id'],
        "title": content['title'],
        "analysis": analysis
    })

# 패턴 발견
print(f"\n{'='*80}")
print("패턴 발견: 10개 게시글 종합 분석")
print("="*80)

# 가장 많이 나타나는 특정성 요소
all_premises = []
all_patterns = []
all_connections = []

for r in research_results:
    analysis = r['analysis']
    all_premises.extend(analysis.get('hidden_premises', []))
    all_patterns.extend(analysis.get('language_patterns', []))
    all_connections.extend(analysis.get('unique_connections', []))

print(f"\n반복되는 생략된 전제 (상위 5개):")
from collections import Counter
premise_freq = Counter(all_premises)
for premise, count in premise_freq.most_common(5):
    print(f"  ({count}회) {premise}")

print(f"\n반복되는 언어 패턴 (상위 5개):")
pattern_freq = Counter(all_patterns)
for pattern, count in pattern_freq.most_common(5):
    print(f"  ({count}회) {pattern}")

# 가설 수립
print(f"\n{'='*80}")
print("가설: 특정성의 구조")
print("="*80)

hypothesis_prompt = f"""
10개 DC 게시글 분석 결과:

반복되는 생략된 전제:
{json.dumps(premise_freq.most_common(5), ensure_ascii=False)}

반복되는 언어 패턴:
{json.dumps(pattern_freq.most_common(5), ensure_ascii=False)}

질문:
1. "특정한 세계관"의 구조는 무엇인가?
2. 어떤 요소들이 반복되는가?
3. 이것들을 어떻게 시스템화할 수 있는가?

JSON:
{{
  "specificity_structure": {{
    "core_elements": ["핵심 요소들"],
    "how_they_connect": "어떻게 연결되는가",
    "what_makes_unique": "무엇이 특정하게 만드는가"
  }},
  "pattern_categories": [
    {{"category": "카테고리", "examples": ["예시들"]}}
  ],
  "system_design": {{
    "what_to_extract": "무엇을 추출해야 하는가",
    "how_to_extract": "어떻게 추출하는가",
    "how_to_verify": "어떻게 검증하는가"
  }}
}}
"""

hypothesis = call_gpt(hypothesis_prompt)
hypothesis_data = json.loads(hypothesis)

print(f"\n특정성의 구조:")
structure = hypothesis_data.get('specificity_structure', {})
for key, val in structure.items():
    print(f"  {key}: {val}")

print(f"\n패턴 카테고리:")
for cat in hypothesis_data.get('pattern_categories', []):
    print(f"  [{cat.get('category')}]")
    for ex in cat.get('examples', [])[:2]:
        print(f"    - {ex}")

print(f"\n시스템 설계:")
system = hypothesis_data.get('system_design', {})
for key, val in system.items():
    print(f"  {key}: {val}")

# 결과 저장
with open('_specificity_research.json', 'w', encoding='utf-8') as f:
    json.dump({
        "individual_analyses": research_results,
        "patterns": {
            "premises": premise_freq.most_common(10),
            "language": pattern_freq.most_common(10)
        },
        "hypothesis": hypothesis_data
    }, f, ensure_ascii=False, indent=2)

print(f"\n결과 저장: _specificity_research.json")

print(f"\n{'='*80}")
print("다음 단계: 가설 검증")
print("="*80)
print("""
1. 추출 방법 설계
2. 새로운 게시글로 테스트
3. 검증 지표 설정
4. 개선 방향 도출
""")
