"""
레이어 구조 설계 및 사용자 시뮬레이션

실제 데이터를 보고 알게 된 것:
- 88개 perception
- 주제: 김현지 실세론, 중국 무비자, 미군, 언론, 맘카페 탄압 등
- Valence: 70.5% negative, 25% positive
- 감정: 불안(31), 분노(31), 조롱(14)
- 세계관 제목: "독재와 사찰의 부활"

이제 설계할 것:
1. Layer 0~3까지 전체 구조 설계
2. 각 레이어가 추가하는 정보와 이론적 근거
3. 실제 사용자 질문에 어떻게 답하는지 시뮬레이션
"""

import os
from supabase import create_client
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 실제 데이터 로드
all_perceptions = supabase.table("perceptions").select("*").execute().data

print("=" * 80)
print("레이어 구조 설계 및 시뮬레이션")
print("=" * 80)

print(f"\n실제 데이터: {len(all_perceptions)}개 perception")
print(f"세계관: 독재와 사찰의 부활")

# ============================================================================
# PART 1: 레이어 구조 설계
# ============================================================================

print("\n\n" + "=" * 80)
print("PART 1: 레이어 구조 설계")
print("=" * 80)

layer_design = """
┌─────────────────────────────────────────────────────────────────────────────┐
│ Layer 0: Raw Content (원본 댓글)                                              │
│ - 기술: DC 갤러리 댓글                                                         │
│ - 이론적 근거: 없음 (순수 데이터)                                              │
│ - 예시: "김현지가 진짜 실세다", "중국인 무비자 위험해"                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓ PerceptionExtractor (GPT)
┌─────────────────────────────────────────────────────────────────────────────┐
│ Layer 1: Perception (개별 인식)                                               │
│ - 기술: Subject-Attribute-Valence 구조                                        │
│ - 이론적 근거: Goffman (1974) - "프레임의 최소 단위는 주체와 속성"             │
│ - 예시: {subject: "김현지", attribute: "실세", valence: "positive"}           │
│ - 추가 정보: claims, keywords, emotions                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓ OptimalWorldviewConstructor
┌─────────────────────────────────────────────────────────────────────────────┐
│ Layer 2: Worldview Collection (인식 묶음)                                     │
│ - 기술: 비슷한 perception들을 벡터 유사도로 묶기                                │
│ - 이론적 근거: Snow & Benford (1988) - "Collective Action Frame"            │
│                비슷한 인식을 가진 사람들이 하나의 집단 프레임 형성              │
│ - 예시: 88개 perception → "독재와 사찰의 부활" 하나의 세계관                   │
│ - 현재 문제: frame 필드가 비어있음 (구조화되지 않음)                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓ ??? (이제 설계할 부분)
┌─────────────────────────────────────────────────────────────────────────────┐
│ Layer 3: Frame Structure (사고방식 구조화)                                     │
│ - 기술: ??? (여러 옵션 테스트 예정)                                            │
│ - 이론적 근거: ???                                                            │
│ - 목표: 민주세력이 "이들은 세상을 어떻게 보는가?"를 이해                         │
└─────────────────────────────────────────────────────────────────────────────┘
"""

print(layer_design)

# ============================================================================
# PART 2: Layer 3 옵션별 설계 및 시뮬레이션
# ============================================================================

print("\n\n" + "=" * 80)
print("PART 2: Layer 3 옵션별 설계")
print("=" * 80)

# 데이터 준비
stats = {
    "total": 88,
    "valence": {"negative": 62, "positive": 22, "neutral": 4},
    "top_subjects": ["김현지", "윤석열 정부", "미군", "더불어민주당", "JTBC"],
    "top_keywords": ["김현지", "중국", "좌파", "미군", "김민석", "JTBC"],
    "top_emotions": ["불안", "분노", "조롱", "실망", "우려"]
}

# 샘플 perception
sample_perceptions = all_perceptions[:30]  # GPT 비용 절감

# ============================================================================
# Option A: Minimal (Goffman만 - "무엇이 일어나고 있는가?")
# ============================================================================

print("\n\n" + "-" * 80)
print("Option A: Minimal Layer (Goffman만)")
print("-" * 80)
print("이론적 근거: Goffman (1974) - '프레임 = 무엇이 일어나고 있는가에 대한 답'")
print("구조: organizing_principle 한 문장")

async def build_layer3_minimal(perceptions):
    """Goffman의 "무엇이 일어나고 있는가?" 한 문장"""

    # 데이터 요약
    subjects = list(set([p['perceived_subject'] for p in perceptions]))[:10]
    keywords = []
    for p in perceptions:
        keywords.extend(p.get('keywords', []))
    top_keywords = sorted(set(keywords), key=keywords.count, reverse=True)[:15]

    prompt = f"""
88개의 perception 데이터를 분석한 결과:
- 주요 주체: {subjects}
- 주요 키워드: {top_keywords}
- 감정: 불안(31), 분노(31), 조롱(14)
- Valence: negative 70.5%, positive 25%

Goffman의 프레임 이론에 따라:
"이 데이터에서 무엇이 일어나고 있는가?" (What's happening here?)

한 문장으로 답하세요. 이것이 organizing principle입니다.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return {
        "layer3_type": "minimal_goffman",
        "organizing_principle": response.choices[0].message.content.strip(),
        "theory": "Goffman (1974) - Frame as organizing principle"
    }

# ============================================================================
# Option B: Entman Structure (문제-원인-도덕-해결책)
# ============================================================================

print("\n\n" + "-" * 80)
print("Option B: Entman Structure")
print("-" * 80)
print("이론적 근거: Entman (1993) - 프레임의 4가지 기능")
print("구조: Problem-Cause-Moral-Solution + Confidence")

async def build_layer3_entman(perceptions, stats):
    """Entman의 4가지 기능 + Confidence Score"""

    # 샘플 데이터
    sample_claims = []
    for p in perceptions[:20]:
        sample_claims.extend(p.get('claims', []))

    prompt = f"""
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
- evidence: 실제 주장 예시

JSON 형식으로 반환.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)

    return {
        "layer3_type": "entman_structure",
        "entman": result,
        "theory": "Entman (1993) - 4 functions of framing"
    }

# ============================================================================
# Option C: Full Integration (Foundation + Entman + Competition)
# ============================================================================

print("\n\n" + "-" * 80)
print("Option C: Full Integration (3 sub-layers)")
print("-" * 80)
print("이론적 근거:")
print("  - Goffman: What's happening?")
print("  - Entman: Problem-Cause-Moral-Solution")
print("  - Chong: Competing frames")
print("구조: 3개 서브레이어")

async def build_layer3_full(perceptions, stats):
    """3개 서브레이어 통합"""

    sample_claims = []
    for p in perceptions[:25]:
        sample_claims.extend(p.get('claims', []))

    prompt = f"""
88개 perception 분석:
- Valence: negative 70.5%, positive 25%
- 감정: 불안, 분노, 조롱
- 주요 주장:
{json.dumps(sample_claims[:25], ensure_ascii=False, indent=2)}

3개 레이어로 분석:

Layer 3a (Goffman): "무엇이 일어나고 있는가?" 한 문장

Layer 3b (Entman):
- problem: {{what, confidence, evidence}}
- cause: {{who, how, confidence, evidence}}
- moral: {{judgment, victims, responsible, confidence, evidence}}
- solution: {{what, who_acts, confidence, evidence}}

Layer 3c (Competition):
- dominant_frame: {{name, strength, core_view}}
- competing_frames: [{{name, strength, key_difference}}]

JSON으로 반환.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)

    return {
        "layer3_type": "full_integration",
        "layers": result,
        "theory": "Goffman + Entman + Chong integrated"
    }

# ============================================================================
# PART 3: 사용자 시뮬레이션
# ============================================================================

print("\n\n" + "=" * 80)
print("PART 3: 사용자 시뮬레이션 설계")
print("=" * 80)

user_questions = [
    "Q1: '독재와 사찰의 부활' 세계관을 가진 사람들은 무엇을 문제로 보나요?",
    "Q2: 이 세계관을 가진 사람들과 나(민주세력)는 어떻게 다른가요?",
    "Q3: 왜 이들은 김현지를 비판하나요?",
    "Q4: 중국 무비자 정책에 대해 이들은 어떻게 생각하나요?",
    "Q5: 이들과 대화할 때 주의할 점은 무엇인가요?"
]

print("\n사용자가 물어볼 질문들:")
for q in user_questions:
    print(f"  {q}")

print("\n각 Layer 3 옵션이 이 질문들에 답할 수 있는지 시뮬레이션 예정...")

# 저장
design_doc = {
    "layer_structure": layer_design,
    "layer3_options": {
        "A_minimal": "Goffman organizing principle only",
        "B_entman": "Problem-Cause-Moral-Solution + Confidence",
        "C_full": "Goffman + Entman + Competition (3 sub-layers)"
    },
    "user_questions": user_questions,
    "evaluation_criteria": {
        "completeness": "모든 질문에 답할 수 있는가?",
        "understanding": "민주세력이 이해하기 쉬운가?",
        "data_fidelity": "실제 데이터를 반영하는가?",
        "actionable": "소통에 활용 가능한가?"
    }
}

with open("/tmp/layer_structure_design.json", "w", encoding="utf-8") as f:
    json.dump(design_doc, f, ensure_ascii=False, indent=2)

print("\n\n✓ 레이어 구조 설계 완료")
print("다음 단계: 각 옵션별로 실제 GPT 실행 및 사용자 질문 답변 시뮬레이션")
