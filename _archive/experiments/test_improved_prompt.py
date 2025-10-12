"""
개선된 Prompt 테스트: 원문 표현 보존 + 특정성 유지
"""

import asyncio
import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))


async def main():
    test_content = {
        "title": '"민주, 지귀연 핸드폰 교체 어떻게 알았나…독재시대 예고편"',
        "body": """나경원 "민주, 지귀연 핸드폰 교체 어떻게 알았나…독재시대 예고편"
개인 사찰을 했다고 민주당이 자백한 수준
유심교체를 어떻게 알아ㅋㅋㅋㅋ미친
지들 맘에 안드는 판사 사찰하려고 통신사 협박해서 얻어낸 정보
통신사들도 요새 해킹 문제 많고
이게 진짜 맞는거냐"""
    }

    print("=" * 80)
    print("개선된 Prompt 테스트")
    print("=" * 80)

    # 개선된 Prompt - 원문 표현 보존 강조
    improved_prompt = f"""
다음은 DC Gallery 정치 갤러리의 글입니다:

제목: {test_content['title']}
내용: {test_content['body']}

이 글을 **3개 층위**로 분석해주세요.

⚠️ **절대 규칙: 원문의 표현, 어투, 말투를 그대로 보존하세요!**
- ❌ "개인정보 불법 취득 의혹" (추상화/정리)
- ✅ "유심교체를 어떻게 알아ㅋㅋㅋㅋ미친" (원문 그대로)

## 1. 표면층 (Explicit Layer) - 명시적 주장
**글에서 직접 말하고 있는 것을 원문 표현으로**

각 주장마다 반드시:
- `raw_quote`: 원문에서 그대로 가져온 문장/표현 (ㅋㅋ, 이모티콘 포함)
- `who_what`: 누가/무엇을 비난하는가
- `tone`: 어떤 감정 톤인가 (조롱, 분노, 냉소 등)

예시:
{{
  "raw_quote": "유심교체를 어떻게 알아ㅋㅋㅋㅋ미친",
  "who_what": "민주당이 유심교체 정보를 알고 있었다",
  "tone": "조롱+불신"
}}

## 2. 암묵층 (Implicit Layer) - 전제하는 사고
**말하지 않았지만 당연하게 여기는 것**

⚠️ 중요: 그들의 문법/표현으로 서술하세요!
- ❌ "비공개 정보 접근은 불법일 가능성이 있다"
- ✅ "통신사 협박해서 얻어낸 정보"

각 가정마다:
- 그들이 실제 쓸 법한 표현으로
- 구체적 메커니즘 명시 (어떤 방법으로?)
- 의도/목적 명시 (왜?)

예시:
- "지들 맘에 안드는 판사 사찰하려고 통신사 협박"
- "민주당은 사법부까지 장악하려고 판사 뒷조사"

## 3. 심층 (Deep Layer) - 무의식적 믿음
**이 진영만의 세계관**

⚠️ 절대 일반론 금지! 그들만의 특수한 시각!
- ❌ "권력은 부패하는 경향이 있다" (누구나 하는 말)
- ✅ "좌파는 독재 본성이 있어서 반대파를 사찰로 제거한다" (특정 진영만의 시각)

각 믿음마다:
- 역사 연결: 과거 사례를 현재와 어떻게 연결하는가?
- 본질 규정: 상대를 어떤 존재로 규정하는가?
- 작동 원리: 세상이 어떻게 돌아간다고 보는가?

예시:
- "독재시대 예고편 - 과거 독재정권처럼 사찰로 시작해서 전면 통제로 간다"
- "민주당/좌파는 본질적으로 독재 성향 - 권력 유지 위해 사법부 장악"

## 4. 논리 사슬 (Reasoning Chain)
**그들만의 추론 방식을 단계별로**

원문 표현을 사용해서 A → B → C → D 형태로:

예시:
1. "유심교체를 어떻게 알아" (의문)
2. → "통신사 협박해서 얻어낸 정보" (방법 단정)
3. → "지들 맘에 안드는 판사 사찰" (목적)
4. → "사법부 장악 시도" (의도)
5. → "독재시대 예고편" (역사 반복)

JSON 형식:
{{
  "explicit_claims": [
    {{
      "raw_quote": "원문 그대로",
      "who_what": "누가 무엇을",
      "tone": "감정 톤"
    }}
  ],
  "implicit_assumptions": [
    "그들의 표현으로 서술한 암묵적 가정 1",
    "그들의 표현으로 서술한 암묵적 가정 2"
  ],
  "reasoning_chain": [
    {{
      "step": 1,
      "raw_expression": "원문 표현",
      "inference": "이 표현이 전제하는 추론"
    }}
  ],
  "deep_beliefs": [
    {{
      "belief": "이 진영 특유의 믿음 (원문 표현 활용)",
      "history_connection": "과거와 어떻게 연결하는가",
      "essence": "상대를 어떤 존재로 보는가"
    }}
  ],
  "worldview_signature": "이 진영의 세계관을 한 문장으로 (그들의 표현으로)"
}}
"""

    print("\nGPT-5 호출 중...")
    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are an expert in discourse analysis. PRESERVE original expressions and tone. Always respond in valid JSON format."},
            {"role": "user", "content": improved_prompt}
        ],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)

    print("\n" + "=" * 80)
    print("개선된 Prompt 결과:")
    print("=" * 80)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 비교 평가
    print("\n" + "=" * 80)
    print("개선 여부 평가")
    print("=" * 80)

    eval_prompt = f"""
개선된 분석 결과:

{json.dumps(result, ensure_ascii=False, indent=2)}

평가:
1. 원문 표현 보존: "유심교체를 어떻게 알아ㅋㅋㅋㅋ", "지들 맘에 안드는", "통신사 협박" 같은 독특한 표현이 살아있는가?
2. 특정성: 일반론이 아닌 이 진영 특유의 시각인가?
3. 논리 구조: 그들만의 추론 방식이 명확한가?
4. 세계관 심도: 세상 작동 원리에 대한 깊은 믿음인가?

각 10점 만점, 총 40점.

기존 버전 점수: 2 + 7 + 8 + 9 = 26점
이번 버전이 개선되었는가?

JSON:
{{
  "original_expression_preserved": 0-10,
  "specific_not_generic": 0-10,
  "unique_logic_structure": 0-10,
  "worldview_depth": 0-10,
  "total": 0-40,
  "vs_previous": "+X점 개선" or "-X점 하락",
  "key_improvements": ["개선점 1", "개선점 2"],
  "remaining_issues": ["남은 문제 1"],
  "final_recommendation": "최종 판단"
}}
"""

    eval_response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "Evaluator. JSON only."},
            {"role": "user", "content": eval_prompt}
        ],
        response_format={"type": "json_object"}
    )

    evaluation = json.loads(eval_response.choices[0].message.content)

    print(f"\n📊 새 점수:")
    print(f"  원문 표현 보존: {evaluation['original_expression_preserved']}/10 (기존 2점)")
    print(f"  특정성: {evaluation['specific_not_generic']}/10 (기존 7점)")
    print(f"  논리 구조: {evaluation['unique_logic_structure']}/10 (기존 8점)")
    print(f"  세계관 심도: {evaluation['worldview_depth']}/10 (기존 9점)")
    print(f"  총점: {evaluation['total']}/40 (기존 26점)")
    print(f"\n{evaluation['vs_previous']}")

    print(f"\n✅ 개선점:")
    for imp in evaluation['key_improvements']:
        print(f"  - {imp}")

    if evaluation['remaining_issues']:
        print(f"\n⚠️  남은 문제:")
        for issue in evaluation['remaining_issues']:
            print(f"  - {issue}")

    print(f"\n💡 최종 판단:")
    print(f"  {evaluation['final_recommendation']}")

    # Save
    output = {
        "improved_result": result,
        "evaluation": evaluation,
        "comparison": {
            "previous_total": 26,
            "new_total": evaluation['total'],
            "improvement": evaluation['total'] - 26
        }
    }

    with open('/tmp/improved_prompt_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n✅ 결과 저장: /tmp/improved_prompt_test_result.json")


if __name__ == '__main__':
    asyncio.run(main())
