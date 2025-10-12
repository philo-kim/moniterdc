"""
핵심 검증: "저들만의 특정한 목소리"가 나오는가?

문제:
- 현재 답변은 일반적인 정치 분석 ("부패 은폐", "권력 투쟁")
- "저들의 세계관"이 안 보임

목표:
- 실제 claims/evidence를 직접 사용해서 "저들의 목소리" 재현
- 일반적 분석 vs 특정한 세계관 비교
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

user_question = "지금 조희대 대법원장을 국정감사에 부르는것을 나경원 의원이 반대하고 있어. 그들은 어떻게 생각하기에 이렇게 행동하는거 같아?"

print("=" * 100)
print("핵심 검증: '저들만의 특정한 목소리'가 나오는가?")
print("=" * 100)
print(f"\n질문: {user_question}")

# 세계관 1: 정치적 갈등과 부패 - 가장 관련성 높음
wv = worldviews[0]

print(f"\n\n{'='*100}")
print(f"세계관: {wv['title']}")
print(f"{'='*100}")

print(f"\n[실제 데이터 분석]")
print(f"Perception: {wv['perception_count']}개")
print(f"Valence: negative {wv['valence_distribution']['negative']}, positive {wv['valence_distribution']['positive']}")

print(f"\n[실제 주장들 (Evidence)]")
all_evidence = []
all_evidence.extend(wv['frame']['entman']['problem']['evidence'])
all_evidence.extend(wv['frame']['entman']['cause']['evidence'])
all_evidence.extend(wv['frame']['entman']['moral']['evidence'])
all_evidence.extend(wv['frame']['entman']['solution']['evidence'])

for i, ev in enumerate(all_evidence[:15], 1):
    print(f"  {i}. \"{ev}\"")

# ============================================================================
# 테스트 1: 현재 방식 (일반적 분석)
# ============================================================================

print(f"\n\n{'='*100}")
print("테스트 1: 현재 방식 (Frame 구조 기반 - 일반적 분석)")
print("=" * 100)

prompt_generic = f"""
당신은 "{wv['title']}" 세계관을 분석하는 AI입니다.

Frame 구조:
- Problem: {wv['frame']['entman']['problem']['what']}
- Cause: {wv['frame']['entman']['cause']['who']} - {wv['frame']['entman']['cause']['how']}
- Moral: {wv['frame']['entman']['moral']['judgment']}

질문: "{user_question}"

이 세계관을 가진 사람들은 어떻게 생각할까요? 3-4문장으로 답하세요.
"""

response_generic = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt_generic}],
    temperature=0.3
)

answer_generic = response_generic.choices[0].message.content.strip()

print(f"\n답변:")
print(f"{answer_generic}")

# ============================================================================
# 테스트 2: 새 방식 (실제 목소리 재현)
# ============================================================================

print(f"\n\n{'='*100}")
print("테스트 2: 새 방식 (실제 주장 기반 - 저들의 목소리)")
print("=" * 100)

prompt_authentic = f"""
당신은 "{wv['title']}" 세계관을 가진 사람입니다.

당신이 실제로 한 주장들:
{chr(10).join([f'- "{ev}"' for ev in all_evidence[:15]])}

질문: "{user_question}"

위 주장들에서 실제로 사용한 표현, 논리, 패턴을 그대로 사용해서 답하세요.

중요:
1. 실제 주장에 나온 구체적인 이름, 사건을 언급하세요
2. 실제 주장의 어투와 논리를 유지하세요
3. 일반적인 분석이 아니라, "이들만의 특정한 시각"을 보여주세요

3-4문장으로 답하세요.
"""

response_authentic = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt_authentic}],
    temperature=0.3
)

answer_authentic = response_authentic.choices[0].message.content.strip()

print(f"\n답변:")
print(f"{answer_authentic}")

# ============================================================================
# 테스트 3: 강화 버전 (실제 perception의 claims 직접 사용)
# ============================================================================

print(f"\n\n{'='*100}")
print("테스트 3: 강화 버전 (실제 perception claims 직접 사용)")
print("=" * 100)

# 실제 perception 로드
from supabase import create_client

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

all_perceptions = supabase.table("perceptions").select("*").execute().data
perception_by_id = {p['id']: p for p in all_perceptions}

# 이 세계관에 속한 perception들
wv_perceptions = []
for pid in wv['perception_ids']:
    if pid in perception_by_id:
        wv_perceptions.append(perception_by_id[pid])

print(f"\n실제 Perception 샘플 (14개 중 10개):")
for i, p in enumerate(wv_perceptions[:10], 1):
    print(f"\n{i}. [{p['perceived_valence']}] {p['perceived_subject']} - {p['perceived_attribute']}")
    print(f"   주장: {p.get('claims', [])[:2]}")
    print(f"   키워드: {p.get('keywords', [])[:5]}")

# 실제 claims 수집
all_claims = []
for p in wv_perceptions:
    all_claims.extend(p.get('claims', []))

print(f"\n\n실제 주장 전체 ({len(all_claims)}개):")
for i, claim in enumerate(all_claims[:20], 1):
    print(f"  {i}. \"{claim}\"")

prompt_enhanced = f"""
당신은 "{wv['title']}" 세계관을 가진 사람입니다.

당신이 실제로 한 주장들 (원문 그대로):
{chr(10).join([f'- "{claim}"' for claim in all_claims[:20]])}

질문: "{user_question}"

위 실제 주장들의 표현과 논리를 그대로 사용해서 답하세요.

반드시:
1. 위 주장에 나온 구체적인 인물 이름 사용 (예: "김현지", "민주당", "판사 사찰")
2. 위 주장의 실제 어투 유지 (예: "맘대로 들춰보고", "협박해서")
3. 위 주장들이 보여주는 패턴 반영 (예: "실세론", "정치보복", "사찰")

"저들만의 특정한 시각"이 드러나게 3-4문장으로 답하세요.
"""

response_enhanced = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt_enhanced}],
    temperature=0.3
)

answer_enhanced = response_enhanced.choices[0].message.content.strip()

print(f"\n\n답변:")
print(f"{answer_enhanced}")

# ============================================================================
# 비교 및 평가
# ============================================================================

print(f"\n\n{'='*100}")
print("비교 및 평가")
print("=" * 100)

print(f"\n[테스트 1: 현재 방식 - 일반적 분석]")
print(f"{answer_generic}")

print(f"\n[테스트 2: 새 방식 - 저들의 목소리]")
print(f"{answer_authentic}")

print(f"\n[테스트 3: 강화 버전 - 실제 claims 사용]")
print(f"{answer_enhanced}")

# GPT로 평가
prompt_eval = f"""
3개의 답변을 비교 평가하세요.

질문: "{user_question}"

답변 1 (일반적 분석):
{answer_generic}

답변 2 (저들의 목소리):
{answer_authentic}

답변 3 (실제 claims):
{answer_enhanced}

평가 기준:
1. "저들만의 특정한 세계관"이 드러나는가? (일반적 분석 vs 특정한 시각)
2. 실제 주장의 표현과 논리를 사용하는가?
3. 구체적인 인물/사건 언급이 있는가?
4. "이 세계관 특유의 뭔가"가 느껴지는가?

JSON 형식:
{{
  "답변1_평가": {{
    "특정성": 1-10,
    "authenticity": 1-10,
    "총평": "..."
  }},
  "답변2_평가": {{...}},
  "답변3_평가": {{...}},
  "최고_답변": 1 or 2 or 3,
  "이유": "..."
}}
"""

response_eval = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt_eval}],
    response_format={"type": "json_object"},
    temperature=0.3
)

evaluation = json.loads(response_eval.choices[0].message.content)

print(f"\n\n{'='*100}")
print("GPT 평가 결과")
print("=" * 100)
print(json.dumps(evaluation, ensure_ascii=False, indent=2))

# 저장
results = {
    "question": user_question,
    "worldview": wv['title'],
    "actual_claims": all_claims[:20],
    "answers": {
        "generic": answer_generic,
        "authentic": answer_authentic,
        "enhanced": answer_enhanced
    },
    "evaluation": evaluation
}

with open("/tmp/authentic_voice_validation.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n\n{'='*100}")
print("결론")
print("=" * 100)

if evaluation.get("최고_답변") == 3:
    print("\n✓ 테스트 3 (실제 claims 사용)이 가장 우수")
    print("\n→ 시스템 구현 방향: 실제 perception의 claims를 직접 사용해야 함")
    print("→ Frame 구조만으로는 '저들의 목소리' 재현 불가")
elif evaluation.get("최고_답변") == 2:
    print("\n✓ 테스트 2 (저들의 목소리)가 가장 우수")
    print("\n→ Evidence만으로도 충분")
else:
    print("\n✗ 현재 방식(일반적 분석)이 가장 우수")
    print("\n→ 재검토 필요")

print(f"\n이유: {evaluation.get('이유')}")

print(f"\n\n결과 저장: /tmp/authentic_voice_validation.json")
