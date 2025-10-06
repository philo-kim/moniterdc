"""
깊은 세계관 분석: 숨어있는 작동 원리 파악

목적:
- 표면 주장이 아닌 세계관의 구조 자체를 이해
- 왜 이들에게는 이 논리가 당연한가?
- 어떤 암묵적 규칙으로 작동하는가?
"""

from engines.utils.supabase_client import get_supabase
from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def analyze_deep_worldview():
    """
    실제 글들을 읽고 숨어있는 세계관 구조 파악
    """

    supabase = get_supabase()

    # Get all contents with body
    contents = supabase.table('contents').select('*').neq('body', '').execute().data

    print(f"총 {len(contents)}개 글 분석 시작...\n")

    # Prepare full text for deep analysis
    full_text = ""
    for i, content in enumerate(contents, 1):
        full_text += f"\n{'='*80}\n"
        full_text += f"글 {i}. {content['title']}\n"
        full_text += f"{'='*80}\n"
        full_text += f"{content['body'][:1000]}\n"  # First 1000 chars

    prompt = f"""
당신은 정치 심리학과 담론 분석 전문가입니다.

다음은 DC Gallery 정치 갤러리에서 수집한 81개의 글입니다.

{full_text[:30000]}  # GPT context limit

이 글들을 쓴 사람들의 **숨어있는 세계관 구조**를 분석해주세요.

⚠️ 중요:
- "민주당 = 독재" 같은 표면 주장은 이미 알고 있습니다
- 우리가 알고 싶은 건: **왜 이들에게는 이 논리가 당연한가?**

다음 질문에 답해주세요:

## 1. 시간관/역사관
- 과거 사례(북한, 중국, 소련)를 현재와 어떻게 연결하는가?
- "역사는 반복된다"는 믿음이 어떻게 작동하는가?
- 과거 → 현재 → 미래의 연결 고리

## 2. 증거와 추론의 기준
- "어떻게 알았나?" → "사찰했다" (왜 이 점프가 당연한가?)
- 어떤 것은 증거로 인정하고, 어떤 것은 무시하는가?
- 의심이 확신이 되는 메커니즘

## 3. 도덕적 우주의 구조
- 왜 타협/중도가 불가능한가?
- 선과 악의 경계는 어떻게 그어지는가?
- 무엇이 배신이고, 무엇이 충성인가?

## 4. 행동의 논리
- 왜 작은 징조에 큰 반응을 하는가?
- "지금 안 막으면 늦는다"는 절박함의 근원
- 예방적 행동을 정당화하는 논리

## 5. 정체성과 역할
- "우리"는 누구이고, 무엇을 하는 사람들인가?
- 왜 "우리만 진실을 본다"고 믿는가?
- 다른 사람들은 왜 "속았다" 또는 "공모자"인가?

## 6. 세계의 작동 원리 (물리 법칙처럼)
- 이들의 세계에서 "당연한 인과관계"는?
- "A가 일어나면 반드시 B가 일어난다"는 법칙들
- 예외가 없는 절대 규칙

각 항목마다:
1. 구체적인 글 예시 인용
2. 숨어있는 가정/전제 추출
3. 이 가정이 어떻게 작동하는지 설명

JSON 형식으로 답변:
{{
  "time_history_view": {{
    "pattern": "...",
    "examples": ["..."],
    "hidden_assumption": "...",
    "how_it_works": "..."
  }},
  "evidence_reasoning": {{...}},
  "moral_universe": {{...}},
  "action_logic": {{...}},
  "identity_role": {{...}},
  "world_physics": {{...}}
}}
"""

    print("GPT 분석 중...")

    response = client.chat.completions.create(
        model="gpt-4o",  # Use GPT-4 for deeper analysis
        messages=[
            {"role": "system", "content": "You are an expert in political psychology and discourse analysis. Always respond in valid JSON format."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)

    print("\n" + "="*80)
    print("깊은 세계관 분석 결과")
    print("="*80)

    for key, value in result.items():
        print(f"\n## {key}")
        print("-"*80)
        if isinstance(value, dict):
            for k, v in value.items():
                print(f"\n{k}:")
                if isinstance(v, list):
                    for item in v:
                        print(f"  - {item}")
                else:
                    print(f"  {v}")
        print()

    # Save to file
    with open('deep_worldview_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n✅ 결과를 deep_worldview_analysis.json에 저장했습니다")

if __name__ == '__main__':
    analyze_deep_worldview()
