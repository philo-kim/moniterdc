"""
층위별 세계관 분석

목표:
1. 표면 주장 추출
2. 암묵적 사고 파악 (전제하지만 말하지 않은 것)
3. 무의식적 믿음 발굴 (너무 당연해서 의식조차 못하는 것)
"""

from engines.utils.supabase_client import get_supabase
from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def layered_analysis():
    supabase = get_supabase()
    contents = supabase.table('contents').select('*').neq('body', '').execute().data

    print(f"총 {len(contents)}개 글 분석...\n")

    # 대표적인 글 10개 선정 (다양성 확보)
    sample_posts = []

    # 다양한 주제 선정
    keywords = ['민주당', '중국', '시위', '윤석열', '이재명', '좌파', '독재', '사찰']
    for keyword in keywords:
        for content in contents:
            if keyword in content['title'] or keyword in content['body']:
                sample_posts.append({
                    'title': content['title'],
                    'body': content['body'][:800]
                })
                break

    # 각 글마다 층위별 분석
    analyses = []

    for i, post in enumerate(sample_posts[:8], 1):  # 8개만
        print(f"[{i}/8] 분석 중: {post['title'][:50]}...")

        prompt = f"""
다음은 DC Gallery 정치 갤러리의 글입니다:

제목: {post['title']}
내용: {post['body']}

이 글을 **3개 층위**로 분석해주세요:

## 1. 표면층 (Explicit Layer)
**명시적으로 말하고 있는 주장**
- 이 글이 직접적으로 주장하는 것
- "X는 Y다", "A가 B를 했다" 같은 명확한 진술

## 2. 암묵층 (Implicit Layer)
**말하지 않았지만 전제하고 있는 사고**
- 이 주장이 성립하려면 무엇을 전제해야 하는가?
- 어떤 가정이 깔려있는가?
- 생략된 추론 단계는?

예: "민주당이 어떻게 알았나?"
→ 암묵적 전제: "공개되지 않은 정보를 안다 = 불법적으로 얻었다"

## 3. 심층 (Deep Layer)
**너무 당연해서 의식조차 못하는 무의식적 믿음**
- 세계는 어떻게 작동하는가? (세계관)
- 인간/권력/역사의 본질은?
- 절대적으로 의심하지 않는 공리(axiom)

예: "권력은 본질적으로 부패한다", "역사는 반복된다"

각 층위마다:
- 구체적인 문장/표현 인용
- 그 이면의 가정/믿음 추출
- 왜 그렇게 생각하는가 설명

JSON 형식:
{{
  "explicit": {{
    "claims": ["주장1", "주장2"],
    "quotes": ["인용1", "인용2"]
  }},
  "implicit": {{
    "assumptions": ["가정1", "가정2"],
    "reasoning": "이 가정들이 어떻게 주장을 떠받치는가"
  }},
  "deep": {{
    "beliefs": ["믿음1", "믿음2"],
    "worldview": "이 믿음들이 구성하는 세계관"
  }}
}}
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in discourse analysis and cognitive psychology. Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        analysis = json.loads(response.choices[0].message.content)
        analysis['post_title'] = post['title']
        analyses.append(analysis)

    print("\n" + "="*80)
    print("개별 글 층위 분석 완료")
    print("="*80)

    # 이제 모든 분석을 종합해서 공통 패턴 찾기
    print("\n공통 패턴 추출 중...")

    synthesis_prompt = f"""
다음은 DC Gallery 정치 갤러리 8개 글의 층위별 분석입니다:

{json.dumps(analyses, ensure_ascii=False, indent=2)}

이제 **공통 패턴**을 찾아주세요:

## 1. 반복되는 암묵적 사고
여러 글에서 공통적으로 전제하고 있는 사고는?

## 2. 공유하는 무의식적 믿음
이들이 모두 당연하게 여기는 세계관의 기반은?

## 3. 세계관의 핵심 구조
이 믿음들이 어떻게 연결되어 하나의 일관된 세계관을 구성하는가?

예:
```
무의식적 믿음: "권력은 부패한다"
     ↓
암묵적 사고: "권력자는 감시 수단을 악용한다"
     ↓
표면 주장: "민주당이 사찰했다"
```

JSON 형식:
{{
  "common_implicit_thoughts": [
    {{
      "thought": "...",
      "appears_in": 5,  // 8개 중 몇 개에서 나타나는가
      "examples": ["글 제목1", "글 제목2"]
    }}
  ],
  "shared_deep_beliefs": [
    {{
      "belief": "...",
      "foundation": "이 믿음이 세계관의 어떤 기초를 제공하는가"
    }}
  ],
  "worldview_structure": {{
    "core_axioms": ["공리1", "공리2"],
    "reasoning_patterns": ["추론 패턴1", "추론 패턴2"],
    "how_connected": "이것들이 어떻게 연결되어 세계를 해석하는 틀을 만드는가"
  }}
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert in synthesizing discourse patterns. Always respond in valid JSON."},
            {"role": "user", "content": synthesis_prompt}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    synthesis = json.loads(response.choices[0].message.content)

    # 결과 출력
    print("\n" + "="*80)
    print("층위별 세계관 분석 결과")
    print("="*80)

    print("\n## 개별 글 분석")
    print("-"*80)
    for i, analysis in enumerate(analyses, 1):
        print(f"\n[글 {i}] {analysis['post_title']}")
        print(f"\n  표면 주장:")
        for claim in analysis['explicit']['claims']:
            print(f"    - {claim}")
        print(f"\n  암묵적 사고:")
        for assumption in analysis['implicit']['assumptions']:
            print(f"    - {assumption}")
        print(f"\n  무의식적 믿음:")
        for belief in analysis['deep']['beliefs']:
            print(f"    - {belief}")

    print("\n\n" + "="*80)
    print("공통 패턴 종합")
    print("="*80)

    print("\n## 반복되는 암묵적 사고")
    print("-"*80)
    for item in synthesis['common_implicit_thoughts']:
        print(f"\n사고: {item['thought']}")
        print(f"출현: {item['appears_in']}/8개 글")
        print(f"예시: {', '.join(item['examples'][:2])}")

    print("\n## 공유하는 무의식적 믿음")
    print("-"*80)
    for item in synthesis['shared_deep_beliefs']:
        print(f"\n믿음: {item['belief']}")
        print(f"기반: {item['foundation']}")

    print("\n## 세계관의 핵심 구조")
    print("-"*80)
    structure = synthesis['worldview_structure']
    print(f"\n핵심 공리:")
    for axiom in structure['core_axioms']:
        print(f"  - {axiom}")
    print(f"\n추론 패턴:")
    for pattern in structure['reasoning_patterns']:
        print(f"  - {pattern}")
    print(f"\n연결 방식:")
    print(f"  {structure['how_connected']}")

    # JSON 저장
    result = {
        'individual_analyses': analyses,
        'synthesis': synthesis
    }

    with open('layered_worldview_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n" + "="*80)
    print("✅ 결과를 layered_worldview_analysis.json에 저장했습니다")
    print("="*80)

if __name__ == '__main__':
    layered_analysis()
