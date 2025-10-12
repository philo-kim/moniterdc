"""
실제 사용자 질문 시뮬레이션

질문: "지금 조희대 대법원장을 국정감사에 부르는것을 나경원 의원이 반대하고 있어
      그들은 어떻게 생각하기에 이렇게 행동하는거 같아?"

5개 세계관의 Frame 구조를 기반으로 답변 생성
"""

import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 실제 세계관 데이터 로드
with open("/tmp/rebuilt_worldviews_complete_system.json", "r", encoding="utf-8") as f:
    worldviews_data = json.load(f)

worldviews = worldviews_data["worldviews"]

user_question = """
지금 조희대 대법원장을 국정감사에 부르는것을 나경원 의원이 반대하고 있어.
그들은 어떻게 생각하기에 이렇게 행동하는거 같아?
"""

print("=" * 100)
print("사용자 질문 시뮬레이션")
print("=" * 100)
print(f"\n질문: {user_question.strip()}")
print("\n" + "=" * 100)

# 각 세계관별로 답변 생성
for i, wv in enumerate(worldviews, 1):
    print(f"\n\n{'='*100}")
    print(f"세계관 {i}: {wv['title']}")
    print(f"{'='*100}")

    print(f"\n[이 세계관의 사고방식]")
    print(f"  Perception: {wv['perception_count']}개")
    print(f"  Valence: neg {wv['valence_distribution']['negative']}, pos {wv['valence_distribution']['positive']}")
    print(f"  문제: {wv['frame']['entman']['problem']['what']}")
    print(f"  원인: {wv['frame']['entman']['cause']['who']}")
    print(f"  지배적 프레임: {wv['frame']['competition']['dominant_frame']['name']} ({wv['frame']['competition']['dominant_frame']['strength']})")

    # GPT로 답변 생성
    prompt = f"""
당신은 "{wv['title']}" 세계관을 가진 사람들의 사고방식을 분석하는 AI입니다.

이 세계관의 Frame 구조:

Problem ({wv['frame']['entman']['problem']['confidence']} 확신):
{wv['frame']['entman']['problem']['what']}
증거: {', '.join(wv['frame']['entman']['problem']['evidence'][:3])}

Cause ({wv['frame']['entman']['cause']['confidence']} 확신):
누가: {wv['frame']['entman']['cause']['who']}
어떻게: {wv['frame']['entman']['cause']['how']}
증거: {', '.join(wv['frame']['entman']['cause']['evidence'][:3])}

Moral ({wv['frame']['entman']['moral']['confidence']} 확신):
판단: {wv['frame']['entman']['moral']['judgment']}
피해자: {wv['frame']['entman']['moral']['victims']}
책임자: {wv['frame']['entman']['moral']['responsible']}

Solution ({wv['frame']['entman']['solution']['confidence']} 확신):
{wv['frame']['entman']['solution']['what']}
누가: {wv['frame']['entman']['solution']['who_acts']}

지배적 프레임 ({wv['frame']['competition']['dominant_frame']['strength']}):
{wv['frame']['competition']['dominant_frame']['core_view']}

---

사용자 질문:
"{user_question.strip()}"

이 세계관을 가진 사람들은 위 질문에 대해 어떻게 생각할까요?

위 Frame 구조(Problem-Cause-Moral-Solution)를 바탕으로:
1. 이 사람들이 이 상황을 어떻게 해석할지
2. 왜 나경원이 반대하는지를 어떻게 이해할지
3. 이것이 그들의 "Problem"과 어떻게 연결되는지

3-4문장으로 답하세요. 반드시 위 Frame 구조를 반영해서 답하세요.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    answer = response.choices[0].message.content.strip()

    print(f"\n['{wv['title']}' 세계관에서 본 답변]")
    print(f"{answer}")

    # 관련성 점수
    prompt_relevance = f"""
세계관: {wv['title']}
Frame: {wv['frame']['entman']['problem']['what']}

질문: "{user_question.strip()}"

이 질문이 이 세계관과 얼마나 관련있나요?
0-10 점수와 1문장 이유를 JSON으로:
{{
  "relevance_score": 8,
  "reason": "..."
}}
"""

    response_rel = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_relevance}],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    relevance = json.loads(response_rel.choices[0].message.content)

    print(f"\n[관련성: {relevance['relevance_score']}/10]")
    print(f"  {relevance['reason']}")

# 최종 통합 답변
print("\n\n" + "=" * 100)
print("최종 통합 답변 (가장 관련성 높은 세계관 기준)")
print("=" * 100)

prompt_final = f"""
5개 정치 세계관이 있습니다:

{json.dumps([{
    "title": wv['title'],
    "problem": wv['frame']['entman']['problem']['what'],
    "cause": wv['frame']['entman']['cause']['who'],
    "dominant_frame": wv['frame']['competition']['dominant_frame']['name']
} for wv in worldviews], ensure_ascii=False, indent=2)}

사용자 질문:
"{user_question.strip()}"

가장 관련성 높은 1-2개 세계관을 선택하고, 그 세계관의 관점에서 답하세요.

형식:
[관련 세계관: ...]
답변: ...

3-4문장.
"""

response_final = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt_final}],
    temperature=0.3
)

print(response_final.choices[0].message.content.strip())

print("\n\n" + "=" * 100)
print("✓ 시뮬레이션 완료")
print("=" * 100)
