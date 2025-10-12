"""
빠른 테스트: 기존 3-Layer 구조가 '특정한 세계관'을 포착하는가?
"""

import asyncio
import os
import json
from openai import AsyncOpenAI
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))


async def main():
    print("=" * 80)
    print("빠른 테스트: 기존 layered_perception_extractor.py 검증")
    print("=" * 80)

    # Test case: 유심교체 사건
    test_content = {
        "title": '"민주, 지귀연 핸드폰 교체 어떻게 알았나…독재시대 예고편"',
        "body": """나경원 "민주, 지귀연 핸드폰 교체 어떻게 알았나…독재시대 예고편"
개인 사찰을 했다고 민주당이 자백한 수준
유심교체를 어떻게 알아ㅋㅋㅋㅋ미친
지들 맘에 안드는 판사 사찰하려고 통신사 협박해서 얻어낸 정보
통신사들도 요새 해킹 문제 많고
이게 진짜 맞는거냐"""
    }

    print(f"\n테스트 글: {test_content['title'][:50]}...")

    # 기존 Prompt (layered_perception_extractor.py 그대로)
    prompt = f"""
다음은 DC Gallery 정치 갤러리의 글입니다:

제목: {test_content['title']}
내용: {test_content['body']}

이 글을 **3개 층위**로 분석해주세요.

⚠️ 중요: 일반론이 아닌, **이 글쓴이가 실제로 믿는 구체적인 내용**을 추출하세요.

## 1. 표면층 (Explicit Layer) - 명시적 주장
**글에서 직접 말하고 있는 것**

## 2. 암묵층 (Implicit Layer) - 전제하는 사고
**말하지 않았지만 당연하게 여기는 것**

❌ 나쁜 예: "비공개 정보를 안다 = 불법"
✅ 좋은 예: "민주당은 통신사를 협박해서 개인정보를 얻는다"

## 3. 심층 (Deep Layer) - 무의식적 믿음
**이 글쓴이 진영만의 세계관**

❌ 나쁜 예: "권력은 부패한다" (누구나 하는 말)
✅ 좋은 예: "민주당/좌파는 과거 독재정권처럼 사찰과 탄압으로 권력을 유지하려 한다"

JSON 형식:
{{
  "explicit_claims": [...],
  "implicit_assumptions": [...],
  "reasoning_gaps": [...],
  "deep_beliefs": [...],
  "worldview_hints": "..."
}}
"""

    print("\nGPT-5 호출 중...")
    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are an expert in discourse analysis. Always respond in valid JSON format."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)

    print("\n" + "=" * 80)
    print("추출 결과:")
    print("=" * 80)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 평가
    print("\n" + "=" * 80)
    print("평가: 이게 '특정한 세계관'을 포착했는가?")
    print("=" * 80)

    eval_prompt = f"""
다음 분석 결과를 평가하세요:

{json.dumps(result, ensure_ascii=False, indent=2)}

유저의 요구사항:
- "저들의 특정한 세계관을 이해하고 싶다"
- "'유심교체를 어떻게 알아'라는 질문 자체가 그들만의 시각이다"
- "일반론이 아닌, 이 진영 특유의 시각이어야 한다"

평가:
1. 원문의 독특한 표현이 살아있는가? (예: "유심교체를 어떻게 알아ㅋㅋㅋㅋ미친")
2. 일반론이 아닌 구체적인 믿음인가? (예: "민주당은 통신사 협박")
3. 그들만의 논리 구조가 드러나는가? (예: 유심정보 알았다 → 통신사 협박 → 사법부 장악)
4. 세계관 심도가 있는가? (예: "좌파 = 독재 본성, 역사 반복")

각 항목 10점 만점, 총 40점.

JSON:
{{
  "original_expression_preserved": 0-10,
  "specific_not_generic": 0-10,
  "unique_logic_structure": 0-10,
  "worldview_depth": 0-10,
  "total": 0-40,
  "key_issue": "가장 큰 문제점",
  "improvement": "개선 방안"
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

    print(f"\n📊 점수:")
    print(f"  원문 표현 보존: {evaluation['original_expression_preserved']}/10")
    print(f"  특정성 (일반론 아님): {evaluation['specific_not_generic']}/10")
    print(f"  독특한 논리 구조: {evaluation['unique_logic_structure']}/10")
    print(f"  세계관 심도: {evaluation['worldview_depth']}/10")
    print(f"  총점: {evaluation['total']}/40")

    print(f"\n❌ 핵심 문제: {evaluation['key_issue']}")
    print(f"💡 개선 방안: {evaluation['improvement']}")

    # Save
    output = {
        "extraction_result": result,
        "evaluation": evaluation
    }

    with open('/tmp/quick_layer_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n✅ 결과 저장: /tmp/quick_layer_test_result.json")

    # 결론
    print("\n" + "=" * 80)
    print("결론")
    print("=" * 80)

    if evaluation['total'] >= 30:
        print("✅ 현재 3-layer 구조가 잘 작동하고 있음")
        print("   → 다음 단계(clustering, worldview 생성)로 진행")
    elif evaluation['total'] >= 20:
        print("⚠️  부분적으로 작동하지만 개선 필요")
        print(f"   → {evaluation['improvement']}")
    else:
        print("❌ 근본적인 문제 있음")
        print(f"   → {evaluation['key_issue']}")
        print(f"   → {evaluation['improvement']}")


if __name__ == '__main__':
    asyncio.run(main())
