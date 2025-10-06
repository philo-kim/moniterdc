"""
PerceptionExtractor가 실제로 어떻게 작동하는지 테스트
"""
import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

async def test_extraction():
    openai = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    system_prompt = """당신은 정치 콘텐츠를 분석하여 인식(perception)을 추출하는 전문가입니다.

주어진 콘텐츠를 분석하여 다음을 추출하세요:

1. **perceived_subject**: 누구/무엇에 대한 이야기인가? (예: "민주당", "이재명", "윤석열 정부")
2. **perceived_attribute**: 어떤 속성/특성을 부여하는가? (예: "무능함", "친중", "독재적")
3. **perceived_valence**: 긍정/부정/중립 (positive/negative/neutral)
4. **claims**: 구체적인 주장들 (배열)
5. **keywords**: 핵심 키워드들 (배열)
6. **emotions**: 감정 표현들 (배열, 예: ["분노", "조롱", "불안"])

응답은 반드시 JSON 형식으로 하되, 하나의 콘텐츠에서 여러 인식이 추출될 수 있습니다.

예시:
{
  "perceptions": [
    {
      "perceived_subject": "민주당",
      "perceived_attribute": "친중 성향",
      "perceived_valence": "negative",
      "claims": ["중국 편을 든다", "국익을 해친다"],
      "keywords": ["민주당", "친중", "배신"],
      "emotions": ["분노", "배신감"]
    }
  ]
}
"""

    # 실제 DC 글로 테스트
    test_content = """제목: "민주, 지귀연 핸드폰 교체 어떻게 알았나…독재시대 예고편"

내용: 나경원 "민주, 지귀연 핸드폰 교체 어떻게 알았나…독재시대 예고편"
박태훈 선임기자 = 나경원 국민의힘 의원은 더불어민주당이 개인정보까지 맘대로 들춰보고 있다며 "폭주를 멈출 것"을 요구했다. 나 의원은 1일 SNS를 통해 "추미애 법사위가 어제 일방적으로 추진한 조희대 대법원장 청
naver.me
개인 사찰을 했다고 민주당이 자백한 수준
유심교체를 어떻게 알아ㅋㅋㅋㅋ미친
지들 맘에 안드는 판사 사찰하려고 통신사 협박해서 얻어낸 정보
통신사들도 요새 해킹 문제 많고
이게 진짜 맞는거냐"""

    print("=" * 80)
    print("테스트: PerceptionExtractor GPT 응답")
    print("=" * 80)

    response = await openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": test_content}
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
        max_tokens=2000
    )

    import json
    result = json.loads(response.choices[0].message.content)

    print("\n추출된 인식:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n" + "=" * 80)

    # 두 번째 테스트
    test_content2 = """제목: 계몽) 계엄 포고문 첫줄에 목적이 나옴

내용: 만약 계엄포고문 내용이 사실임을 인정한다면,
계엄의 목적이 자유민주주의 수호와 국민의 안전 보호임을 인정해야 함
밑에 나오는 사항들(국회 정치활동 금지 등등)은
목적을 이루기 위한 수단이므로,
계엄의 진정한 목적이라 볼 수 없음
또 6항에 나온
"반국가세력 등 체제전복세력을 제외한 선량한 일반 국민들은 일상생활에 불편을 최소화할 수 있도록 조치한다." 부분만 봐도 계엄은 평화적으로 이루어졌으며
어떤 폭력적인 일도 일어나지 않았단 걸 알수 있음
세상에 어떤 계엄이 3시간 만에, 국회의 의결에 따라
해제함? 군인들은 실탄도 한발 없었는데"""

    print("\n두 번째 테스트:")
    print("=" * 80)

    response2 = await openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": test_content2}
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
        max_tokens=2000
    )

    result2 = json.loads(response2.choices[0].message.content)
    print("\n추출된 인식:")
    print(json.dumps(result2, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    asyncio.run(test_extraction())
