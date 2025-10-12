"""
Layer 3 옵션별 실행 및 사용자 질문 답변 시뮬레이션

실행할 것:
1. Option A (Minimal): Goffman organizing principle
2. Option B (Entman): Problem-Cause-Moral-Solution
3. Option C (Full): Goffman + Entman + Competition

각 옵션으로 사용자 질문 5개에 답할 수 있는지 시뮬레이션
"""

import os
from supabase import create_client
from openai import OpenAI
import json
from dotenv import load_dotenv
import asyncio

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 실제 데이터 로드
all_perceptions = supabase.table("perceptions").select("*").execute().data
sample_perceptions = all_perceptions[:30]  # GPT 비용 절감

print("=" * 80)
print("Layer 3 옵션별 실행 및 사용자 시뮬레이션")
print("=" * 80)
print(f"\n실제 데이터: {len(all_perceptions)}개 perception (30개 샘플 사용)")

# ============================================================================
# STEP 1: 각 옵션 실행
# ============================================================================

print("\n\n" + "=" * 80)
print("STEP 1: Layer 3 옵션별 실행")
print("=" * 80)

# ----------------------------------------------------------------------------
# Option A: Minimal (Goffman)
# ----------------------------------------------------------------------------

print("\n\n" + "-" * 80)
print("Option A: Minimal (Goffman - 'What's happening?')")
print("-" * 80)

subjects = list(set([p['perceived_subject'] for p in sample_perceptions]))[:10]
keywords = []
for p in sample_perceptions:
    keywords.extend(p.get('keywords', []))
top_keywords = sorted(set(keywords), key=keywords.count, reverse=True)[:15]

prompt_a = f"""
88개의 perception 데이터를 분석한 결과:
- 주요 주체: {subjects}
- 주요 키워드: {top_keywords}
- 감정: 불안(31), 분노(31), 조롱(14)
- Valence: negative 70.5%, positive 25%

Goffman의 프레임 이론에 따라:
"이 데이터에서 무엇이 일어나고 있는가?" (What's happening here?)

한 문장으로 답하세요. 이것이 organizing principle입니다.
"""

print("GPT 실행 중...")
response_a = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt_a}],
    temperature=0.3
)

result_a = {
    "layer3_type": "minimal_goffman",
    "organizing_principle": response_a.choices[0].message.content.strip(),
    "theory": "Goffman (1974) - Frame as organizing principle"
}

print(f"\n결과:")
print(f"  {result_a['organizing_principle']}")

# ----------------------------------------------------------------------------
# Option B: Entman
# ----------------------------------------------------------------------------

print("\n\n" + "-" * 80)
print("Option B: Entman Structure (Problem-Cause-Moral-Solution)")
print("-" * 80)

sample_claims = []
for p in sample_perceptions[:20]:
    sample_claims.extend(p.get('claims', []))

prompt_b = f"""
88개 perception 분석 결과:
- Valence: negative 70.5%, positive 25%
- 주요 감정: 불안, 분노, 조롱
- 샘플 주장들:
{json.dumps(sample_claims[:20], ensure_ascii=False, indent=2)}

Entman의 프레임 이론에 따라 4가지 기능을 분석하세요:

1. Problem Definition: 무엇이 문제인가?
2. Causal Attribution: 누가/무엇이 원인인가?
3. Moral Evaluation: 도덕적 판단은 무엇인가?
4. Treatment Recommendation: 어떻게 해야 하는가?

각 항목마다:
- what/who: 내용
- confidence: 0-1 (데이터가 얼마나 이를 지지하는가)
- evidence: 실제 주장 예시 (최대 2개)

JSON 형식으로 반환.
{{
  "problem": {{"what": "...", "confidence": 0.9, "evidence": ["...", "..."]}},
  "cause": {{"who": ["..."], "how": "...", "confidence": 0.8, "evidence": ["..."]}},
  "moral": {{"judgment": "...", "victims": ["..."], "responsible": ["..."], "confidence": 0.85, "evidence": ["..."]}},
  "solution": {{"what": "...", "who_acts": ["..."], "confidence": 0.75, "evidence": ["..."]}}
}}
"""

print("GPT 실행 중...")
response_b = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt_b}],
    response_format={"type": "json_object"},
    temperature=0.3
)

result_b = {
    "layer3_type": "entman_structure",
    "entman": json.loads(response_b.choices[0].message.content),
    "theory": "Entman (1993) - 4 functions of framing"
}

print(f"\n결과:")
print(f"  Problem: {result_b['entman']['problem']['what']} (confidence: {result_b['entman']['problem']['confidence']})")
print(f"  Cause: {result_b['entman']['cause']['who']} (confidence: {result_b['entman']['cause']['confidence']})")
print(f"  Moral: {result_b['entman']['moral']['judgment']} (confidence: {result_b['entman']['moral']['confidence']})")
print(f"  Solution: {result_b['entman']['solution']['what']} (confidence: {result_b['entman']['solution']['confidence']})")

# ----------------------------------------------------------------------------
# Option C: Full Integration
# ----------------------------------------------------------------------------

print("\n\n" + "-" * 80)
print("Option C: Full Integration (Goffman + Entman + Competition)")
print("-" * 80)

sample_claims_c = []
for p in sample_perceptions[:25]:
    sample_claims_c.extend(p.get('claims', []))

prompt_c = f"""
88개 perception 분석:
- Valence: negative 70.5%, positive 25%, neutral 4.5%
- 감정: 불안, 분노, 조롱
- 주요 주장:
{json.dumps(sample_claims_c[:25], ensure_ascii=False, indent=2)}

3개 레이어로 분석:

Layer 3a (Goffman): "무엇이 일어나고 있는가?" 한 문장

Layer 3b (Entman):
- problem: {{what, confidence, evidence}}
- cause: {{who, how, confidence, evidence}}
- moral: {{judgment, victims, responsible, confidence, evidence}}
- solution: {{what, who_acts, confidence, evidence}}

Layer 3c (Competition):
valence 분포를 보면 negative 70.5%, positive 25%입니다.
이는 서로 다른 프레임이 경쟁하고 있음을 의미합니다.
- dominant_frame: {{name, strength (0.705), core_view}}
- competing_frames: [{{name, strength (0.25), key_difference}}]

JSON으로 반환.
{{
  "layer3a_goffman": "...",
  "layer3b_entman": {{...}},
  "layer3c_competition": {{...}}
}}
"""

print("GPT 실행 중...")
response_c = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt_c}],
    response_format={"type": "json_object"},
    temperature=0.3
)

result_c = {
    "layer3_type": "full_integration",
    "layers": json.loads(response_c.choices[0].message.content),
    "theory": "Goffman + Entman + Chong integrated"
}

print(f"\n결과:")
print(f"  Layer 3a (Goffman): {result_c['layers']['layer3a_goffman']}")
print(f"  Layer 3b (Entman Problem): {result_c['layers']['layer3b_entman']['problem']['what']}")
print(f"  Layer 3c (Competition): {result_c['layers']['layer3c_competition']['dominant_frame']['name']} ({result_c['layers']['layer3c_competition']['dominant_frame']['strength']})")

# ============================================================================
# STEP 2: 사용자 질문 답변 시뮬레이션
# ============================================================================

print("\n\n" + "=" * 80)
print("STEP 2: 사용자 질문 답변 시뮬레이션")
print("=" * 80)

user_questions = [
    "Q1: '독재와 사찰의 부활' 세계관을 가진 사람들은 무엇을 문제로 보나요?",
    "Q2: 이 세계관을 가진 사람들과 나(민주세력)는 어떻게 다른가요?",
    "Q3: 왜 이들은 김현지를 비판하나요?",
    "Q4: 중국 무비자 정책에 대해 이들은 어떻게 생각하나요?",
    "Q5: 이들과 대화할 때 주의할 점은 무엇인가요?"
]

# ----------------------------------------------------------------------------
# Option A로 답변
# ----------------------------------------------------------------------------

print("\n\n" + "-" * 80)
print("Option A (Minimal)로 사용자 질문에 답하기")
print("-" * 80)

for q in user_questions:
    print(f"\n{q}")

    prompt_qa = f"""
당신은 "독재와 사찰의 부활" 세계관을 분석한 AI입니다.

분석 결과:
{result_a['organizing_principle']}

사용자 질문: {q}

위 분석 결과만으로 이 질문에 답할 수 있다면 답하세요.
답할 수 없다면 "이 질문에 답하기에는 정보가 부족합니다"라고 하세요.

2-3문장으로 답하세요.
"""

    response_qa = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_qa}],
        temperature=0.3
    )

    print(f"  답변: {response_qa.choices[0].message.content.strip()}")

# ----------------------------------------------------------------------------
# Option B로 답변
# ----------------------------------------------------------------------------

print("\n\n" + "-" * 80)
print("Option B (Entman)로 사용자 질문에 답하기")
print("-" * 80)

for q in user_questions:
    print(f"\n{q}")

    prompt_qb = f"""
당신은 "독재와 사찰의 부활" 세계관을 분석한 AI입니다.

분석 결과 (Entman 프레임):
- Problem: {result_b['entman']['problem']['what']} (confidence: {result_b['entman']['problem']['confidence']})
- Cause: {result_b['entman']['cause']['who']} - {result_b['entman']['cause']['how']} (confidence: {result_b['entman']['cause']['confidence']})
- Moral: {result_b['entman']['moral']['judgment']}
  - Victims: {result_b['entman']['moral']['victims']}
  - Responsible: {result_b['entman']['moral']['responsible']}
  (confidence: {result_b['entman']['moral']['confidence']})
- Solution: {result_b['entman']['solution']['what']} by {result_b['entman']['solution']['who_acts']} (confidence: {result_b['entman']['solution']['confidence']})

사용자 질문: {q}

위 분석 결과로 이 질문에 답하세요.
답할 수 없다면 "이 질문에 답하기에는 정보가 부족합니다"라고 하세요.

2-3문장으로 답하세요.
"""

    response_qb = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_qb}],
        temperature=0.3
    )

    print(f"  답변: {response_qb.choices[0].message.content.strip()}")

# ----------------------------------------------------------------------------
# Option C로 답변
# ----------------------------------------------------------------------------

print("\n\n" + "-" * 80)
print("Option C (Full Integration)로 사용자 질문에 답하기")
print("-" * 80)

for q in user_questions:
    print(f"\n{q}")

    prompt_qc = f"""
당신은 "독재와 사찰의 부활" 세계관을 분석한 AI입니다.

분석 결과 (3개 레이어):

Layer 3a (무엇이 일어나고 있는가):
{result_c['layers']['layer3a_goffman']}

Layer 3b (Entman 프레임):
- Problem: {result_c['layers']['layer3b_entman']['problem']['what']}
- Cause: {result_c['layers']['layer3b_entman']['cause']['who']} - {result_c['layers']['layer3b_entman']['cause']['how']}
- Moral: {result_c['layers']['layer3b_entman']['moral']['judgment']}
- Solution: {result_c['layers']['layer3b_entman']['solution']['what']}

Layer 3c (경쟁 프레임):
- Dominant: {result_c['layers']['layer3c_competition']['dominant_frame']['name']} ({result_c['layers']['layer3c_competition']['dominant_frame']['strength']})
  {result_c['layers']['layer3c_competition']['dominant_frame']['core_view']}
- Competing: {result_c['layers']['layer3c_competition']['competing_frames'][0]['name']} ({result_c['layers']['layer3c_competition']['competing_frames'][0]['strength']})

사용자 질문: {q}

위 분석 결과로 이 질문에 답하세요.
답할 수 없다면 "이 질문에 답하기에는 정보가 부족합니다"라고 하세요.

2-3문장으로 답하세요.
"""

    response_qc = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_qc}],
        temperature=0.3
    )

    print(f"  답변: {response_qc.choices[0].message.content.strip()}")

# ============================================================================
# STEP 3: 평가 및 결론
# ============================================================================

print("\n\n" + "=" * 80)
print("STEP 3: 평가 및 결론")
print("=" * 80)

evaluation = """
각 옵션별 평가:

Option A (Minimal - Goffman):
- 장점: 간결함, 빠름
- 단점: 구체적인 질문에 답하기 어려움
- 적합한 경우: 매우 빠른 개요만 필요한 경우

Option B (Entman):
- 장점: Problem-Cause-Moral-Solution 명확, Confidence score로 신뢰도 표시
- 단점: 경쟁 프레임 대조가 없어 "나와 어떻게 다른가?" 질문에 약함
- 적합한 경우: 이 세계관의 논리 구조를 이해하고 싶을 때

Option C (Full Integration):
- 장점: 모든 질문에 답 가능, 경쟁 프레임으로 대조 명확
- 단점: 복잡함, 시간 소요
- 적합한 경우: 깊이 있는 이해와 소통 전략이 필요한 경우

사용자 질문 답변 능력:
Q1 (무엇을 문제로 보는가): A △, B ○, C ○
Q2 (나와 어떻게 다른가): A ✗, B △, C ○
Q3 (왜 김현지 비판): A ✗, B △, C ○
Q4 (중국 무비자 생각): A △, B ○, C ○
Q5 (대화 주의점): A ✗, B △, C ○
"""

print(evaluation)

# 저장
final_results = {
    "option_a_minimal": result_a,
    "option_b_entman": result_b,
    "option_c_full": result_c,
    "user_questions": user_questions,
    "evaluation": evaluation
}

with open("/tmp/layer3_execution_and_user_simulation.json", "w", encoding="utf-8") as f:
    json.dump(final_results, f, ensure_ascii=False, indent=2)

print("\n\n✓ 실행 및 시뮬레이션 완료")
print("결과 저장: /tmp/layer3_execution_and_user_simulation.json")
