#!/usr/bin/env python3
"""
Core Beliefs 추출 - 세계관의 본질

목적: Claims가 아닌 기본 믿음 체계 추출
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
print("Core Beliefs 추출 - 세계관의 본질")
print("="*80)

# 실제 게시글
post = """
제목: "민주, 지귀연 핸드폰 교체 어떻게 알았나…독재시대 예고편"

내용:
개인 사찰을 했다고 민주당이 자백한 수준
유심교체를 어떻게 알아ㅋㅋㅋㅋ미친
지들 맘에 안드는 판사 사찰하려고 통신사 협박해서 얻어낸 정보
통신사들도 요새 해킹 문제 많고
이게 진짜 맞는거냐
"""

print(f"\n[게시글]")
print(post.strip())

# GPT로 Core Beliefs 추출
prompt = f"""
다음 DC 게시글을 분석하여 작성자의 **기본 믿음 체계 (Core Beliefs)**를 추출하세요.

게시글:
{post}

분석 과정:

1. 명시된 주장: 작성자가 직접 말한 것
2. 암묵적 가정: 명시되지 않았지만 전제되는 것
3. 기본 믿음: "세상은 이렇게 작동한다"는 근본 믿음

예시:
- 명시된 주장: "통신사 협박해서 얻어냈다"
- 암묵적 가정: "정상적으로는 알 수 없다"
- 기본 믿음: "민주당은 법을 무시하고 권력을 악용한다"

JSON 형식:
{{
  "explicit_claims": ["명시된 주장들"],
  "implicit_assumptions": [
    {{"assumption": "가정", "why_assumed": "왜 이렇게 가정하는가"}}
  ],
  "core_beliefs": [
    {{
      "belief": "기본 믿음",
      "about": "민주당/판사/국가권력/etc",
      "implication": "이 믿음이 있으면 어떻게 해석하게 되는가"
    }}
  ],
  "worldview_structure": {{
    "how_world_works": "세상은 어떻게 작동하는가",
    "key_actors": {{"민주당": "본질", "판사": "본질", ...}},
    "causality": ["인과 관계들"],
    "interpretation_rules": ["증거 해석 규칙들"]
  }}
}}

깊이 분석하세요. 표면적 패턴이 아닌 근본 믿음을 찾으세요.
"""

result = call_gpt(prompt)
beliefs = json.loads(result)

print(f"\n[추출된 Core Beliefs]")
print("="*80)

print(f"\n1. 명시된 주장:")
for claim in beliefs.get('explicit_claims', []):
    print(f"  - {claim}")

print(f"\n2. 암묵적 가정:")
for assumption in beliefs.get('implicit_assumptions', []):
    print(f"  가정: {assumption.get('assumption')}")
    print(f"  이유: {assumption.get('why_assumed')}")
    print()

print(f"\n3. 기본 믿음 (Core Beliefs):")
for belief in beliefs.get('core_beliefs', []):
    print(f"  [{belief.get('about')}]")
    print(f"    믿음: {belief.get('belief')}")
    print(f"    결과: {belief.get('implication')}")
    print()

print(f"\n4. 세계관 구조:")
structure = beliefs.get('worldview_structure', {})
print(f"\n  세상이 작동하는 방식:")
print(f"    {structure.get('how_world_works', 'N/A')}")

print(f"\n  주요 행위자:")
for actor, nature in structure.get('key_actors', {}).items():
    print(f"    - {actor}: {nature}")

print(f"\n  인과 관계:")
for causality in structure.get('causality', []):
    print(f"    - {causality}")

print(f"\n  해석 규칙:")
for rule in structure.get('interpretation_rules', []):
    print(f"    - {rule}")

# Save
with open('_core_beliefs_extracted.json', 'w', encoding='utf-8') as f:
    json.dump(beliefs, f, ensure_ascii=False, indent=2)

print(f"\n결과 저장: _core_beliefs_extracted.json")

# Validation: 이 믿음 체계로 새로운 사건을 해석할 수 있는가?
print(f"\n{'='*80}")
print("검증: 이 믿음 체계로 다른 사건 해석 가능한가?")
print("="*80)

test_events = [
    "민주당이 조희대 대법원장 국정감사를 추진",
    "민주당이 예산안을 통과시켰다",
    "민주당이 북한과 대화를 시도"
]

for event in test_events:
    print(f"\n[사건] {event}")

    interpret_prompt = f"""
다음은 한 사람의 기본 믿음 체계입니다:

{json.dumps(structure, ensure_ascii=False, indent=2)}

새로운 사건: "{event}"

이 믿음 체계를 가진 사람은 이 사건을 어떻게 해석할까요?

JSON:
{{
  "interpretation": "해석",
  "reasoning": "왜 이렇게 해석하는가 (믿음 체계 기반)",
  "confidence": 1-10
}}
"""

    result = call_gpt(interpret_prompt, model="gpt-4o-mini")
    interpretation = json.loads(result)

    print(f"  해석: {interpretation.get('interpretation')}")
    print(f"  이유: {interpretation.get('reasoning')[:100]}...")
    print(f"  확신: {interpretation.get('confidence')}/10")

print(f"\n{'='*80}")
print("✓ 검증 완료: 믿음 체계가 일관된 해석을 생성하는가?")
print("="*80)
