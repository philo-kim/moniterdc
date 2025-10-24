"""
실제 데이터로 다양한 프레임 구조화 방식을 시뮬레이션

목표:
- 88개 실제 perception 데이터 사용
- 10가지 이상의 다른 방식으로 GPT 프레임 구조화
- 각 결과물을 실제로 생성하고 비교
- 민주세력이 가장 이해하기 쉬운 방식 찾기

방법:
1. Foundation (데이터 기반)
2. Entman 4가지 기능 (다양한 프롬프트)
3. Competition (대조 프레임)
4. Package (Gamson)
5. 하이브리드 조합들
"""

import asyncio
import json
import os
from supabase import create_client
from openai import AsyncOpenAI
from collections import Counter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


def load_data():
    """실제 데이터 로드 및 기초 분석"""
    print("="*80)
    print("실제 데이터 로딩")
    print("="*80)

    result = supabase.table('perceptions').select('*').execute()
    perceptions = result.data

    print(f"\n✓ {len(perceptions)}개 perception 로드")

    # 기초 통계
    subjects = [p.get('perceived_subject') for p in perceptions if p.get('perceived_subject')]
    keywords = []
    emotions = []
    valences = []
    claims = []

    for p in perceptions:
        keywords.extend(p.get('keywords', []))
        emotions.extend(p.get('emotions', []))
        valences.append(p.get('perceived_valence'))
        claims.extend(p.get('claims', []))

    stats = {
        'total': len(perceptions),
        'subjects': Counter(subjects),
        'keywords': Counter(keywords),
        'emotions': Counter(emotions),
        'valences': Counter(valences),
        'total_claims': len(claims)
    }

    print(f"\n주요 주체 Top 5: {[s for s, _ in stats['subjects'].most_common(5)]}")
    print(f"주요 키워드 Top 10: {[k for k, _ in stats['keywords'].most_common(10)]}")
    print(f"주요 감정 Top 5: {[e for e, _ in stats['emotions'].most_common(5)]}")
    print(f"Valence 분포: {dict(stats['valences'])}")

    return perceptions, stats


# ============================================================================
# 방식 1: Foundation Only (순수 데이터)
# ============================================================================

def method1_foundation_only(stats):
    """방식 1: 통계만 제시 (GPT 없음)"""
    print("\n" + "="*80)
    print("방식 1: Foundation Only (순수 데이터)")
    print("="*80)

    result = {
        "method": "foundation_only",
        "organizing_principle": "무엇이 일어나고 있는가?",
        "discovered_patterns": {
            "total_perceptions": stats['total'],
            "primary_subjects": [s for s, _ in stats['subjects'].most_common(5)],
            "primary_keywords": [k for k, _ in stats['keywords'].most_common(10)],
            "emotional_tone": {
                "top_emotions": [e for e, _ in stats['emotions'].most_common(5)],
                "valence_distribution": dict(stats['valences'])
            }
        }
    }

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


# ============================================================================
# 방식 2: Entman 직접 질문
# ============================================================================

async def method2_entman_direct(perceptions):
    """방식 2: Entman 4가지 기능을 직접 물어보기"""
    print("\n" + "="*80)
    print("방식 2: Entman 직접 질문")
    print("="*80)

    # 샘플 데이터 준비
    sample = perceptions[:20]
    perception_texts = []
    for p in sample:
        text = f"{p.get('perceived_subject')} - {p.get('perceived_attribute')} ({p.get('perceived_valence')}): {p.get('claims', [])[:2]}"
        perception_texts.append(text)

    prompt = f"""
다음은 "독재와 사찰의 부활" 세계관에 속한 20개 perception입니다:

{chr(10).join(perception_texts)}

Entman의 프레임 이론에 따라 다음 4가지를 분석해주세요:

1. Problem Definition (문제 정의): 무엇이 문제인가?
2. Causal Attribution (원인 귀속): 누가/무엇이 문제를 야기했는가?
3. Moral Evaluation (도덕적 판단): 이것이 옳은가/그른가? 누가 피해자이고 책임자인가?
4. Treatment Recommendation (해결책): 무엇을 해야 하는가?

각 항목마다 실제 perception에서 근거를 들어주세요.

JSON 형식으로 답변해주세요:
{{
  "problem_definition": {{
    "what": "...",
    "why_problem": "...",
    "evidence": ["..."]
  }},
  "causal_attribution": {{
    "who": ["..."],
    "how": "...",
    "evidence": ["..."]
  }},
  "moral_evaluation": {{
    "judgment": "...",
    "victims": ["..."],
    "responsible": ["..."],
    "evidence": ["..."]
  }},
  "treatment_recommendation": {{
    "what": "...",
    "who_should_act": ["..."],
    "evidence": ["..."]
  }}
}}
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)
    result['method'] = 'entman_direct'

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


# ============================================================================
# 방식 3: Competition Frame (대조)
# ============================================================================

async def method3_competition_frame(perceptions, stats):
    """방식 3: 경쟁 프레임과의 대조"""
    print("\n" + "="*80)
    print("방식 3: Competition Frame (대조)")
    print("="*80)

    sample = perceptions[:15]
    perception_texts = []
    for p in sample:
        text = f"{p.get('perceived_subject')} - {p.get('perceived_attribute')}: {p.get('claims', [])[:1]}"
        perception_texts.append(text)

    prompt = f"""
다음은 특정 정치 프레임에 속한 15개 perception입니다:

{chr(10).join(perception_texts)}

이 프레임과 경쟁하는 다른 프레임들을 찾아주세요.

같은 사건/이슈를 다르게 해석하는 3가지 프레임:

JSON 형식으로:
{{
  "frame_A": {{
    "name": "...",
    "core_interpretation": "...",
    "strength": 0.0-1.0,
    "evidence_from_data": ["..."]
  }},
  "frame_B": {{
    "name": "...",
    "core_interpretation": "...",
    "strength": 0.0-1.0,
    "evidence_from_data": ["..."]
  }},
  "frame_C": {{
    "name": "...",
    "core_interpretation": "...",
    "strength": 0.0-1.0,
    "evidence_from_data": ["..."]
  }},
  "key_differences": "..."
}}
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.5
    )

    result = json.loads(response.choices[0].message.content)
    result['method'] = 'competition_frame'
    result['data_valence_distribution'] = dict(stats['valences'])

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


# ============================================================================
# 방식 4: Goffman "What's Happening"
# ============================================================================

async def method4_goffman_happening(perceptions):
    """방식 4: Goffman - 무엇이 일어나고 있는가?"""
    print("\n" + "="*80)
    print("방식 4: Goffman - What's Happening")
    print("="*80)

    sample = perceptions[:15]
    perception_texts = []
    for p in sample:
        text = f"{p.get('perceived_subject')} - {p.get('perceived_attribute')}: {p.get('claims', [])[:2]}"
        perception_texts.append(text)

    prompt = f"""
다음 perception들을 보고, 이 사람들이 생각하기에 "무엇이 일어나고 있는가?"를 파악해주세요.

{chr(10).join(perception_texts)}

Goffman의 프레임 이론:
- 사람들은 경험을 조직하는 원리(organizing principle)를 가짐
- "무엇이 일어나고 있는가?"가 프레임의 핵심

JSON 형식으로:
{{
  "what_is_happening": "...",
  "organizing_principle": "...",
  "frame_type": "Natural (자연적) or Social (사회적)",
  "key_actors": ["..."],
  "key_actions": ["..."],
  "evidence": ["..."]
}}
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)
    result['method'] = 'goffman_happening'

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


# ============================================================================
# 방식 5: Lakoff Metaphors
# ============================================================================

async def method5_lakoff_metaphors(perceptions, stats):
    """방식 5: Lakoff - 개념적 은유"""
    print("\n" + "="*80)
    print("방식 5: Lakoff - Conceptual Metaphors")
    print("="*80)

    top_keywords = [k for k, _ in stats['keywords'].most_common(20)]

    sample = perceptions[:15]
    claims = []
    for p in sample:
        claims.extend(p.get('claims', [])[:1])

    prompt = f"""
다음은 특정 정치 프레임의 키워드와 주장들입니다:

키워드: {top_keywords}

주장 샘플:
{chr(10).join(claims[:10])}

Lakoff의 개념적 은유 이론:
- 프레임은 은유로 활성화됨
- "정치는 전쟁이다", "국가는 가족이다" 등

이 데이터에서 발견되는 개념적 은유를 찾아주세요:

JSON 형식으로:
{{
  "primary_metaphors": [
    {{
      "metaphor": "X IS Y",
      "examples": ["..."],
      "trigger_words": ["..."]
    }}
  ],
  "frame_activation": {{
    "key_trigger_words": ["..."],
    "what_frame_activated": "..."
  }}
}}
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.5
    )

    result = json.loads(response.choices[0].message.content)
    result['method'] = 'lakoff_metaphors'

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


# ============================================================================
# 방식 6: Gamson Package
# ============================================================================

async def method6_gamson_package(perceptions, stats):
    """방식 6: Gamson - Frame Package"""
    print("\n" + "="*80)
    print("방식 6: Gamson - Frame Package")
    print("="*80)

    top_keywords = [k for k, _ in stats['keywords'].most_common(15)]

    sample = perceptions[:15]
    perception_texts = []
    for p in sample:
        text = f"{p.get('perceived_subject')}: {p.get('claims', [])[:1]}"
        perception_texts.append(text)

    prompt = f"""
다음은 특정 정치 프레임의 데이터입니다:

키워드: {top_keywords}

Perception 샘플:
{chr(10).join(perception_texts)}

Gamson의 Frame Package 이론:
- Core Position (핵심 입장)
- Metaphors (은유)
- Catchphrases (슬로건)
- Exemplars (대표 사례)
- Roots (역사적/문화적 뿌리)

이 프레임의 패키지를 구성해주세요:

JSON 형식으로:
{{
  "core_position": "...",
  "metaphors": ["..."],
  "catchphrases": ["..."],
  "exemplars": [
    {{
      "event": "...",
      "significance": "..."
    }}
  ],
  "roots": ["..."]
}}
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.4
    )

    result = json.loads(response.choices[0].message.content)
    result['method'] = 'gamson_package'

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


# ============================================================================
# 방식 7: 하이브리드 1 (Foundation + Entman)
# ============================================================================

async def method7_hybrid_foundation_entman(perceptions, stats):
    """방식 7: Foundation + Entman"""
    print("\n" + "="*80)
    print("방식 7: Hybrid (Foundation + Entman)")
    print("="*80)

    # Foundation (데이터)
    foundation = {
        "total": stats['total'],
        "주요_주체": [s for s, _ in stats['subjects'].most_common(5)],
        "주요_키워드": [k for k, _ in stats['keywords'].most_common(10)],
        "주요_감정": [e for e, _ in stats['emotions'].most_common(5)],
        "valence": dict(stats['valences'])
    }

    # Entman (GPT)
    sample = perceptions[:15]
    perception_texts = []
    for p in sample:
        text = f"{p.get('perceived_subject')} - {p.get('perceived_attribute')}: {p.get('claims', [])[:1]}"
        perception_texts.append(text)

    prompt = f"""
Foundation (실제 데이터):
{json.dumps(foundation, ensure_ascii=False, indent=2)}

Representative Perceptions:
{chr(10).join(perception_texts)}

위 데이터를 바탕으로 Entman 4가지 기능을 추출하되,
각 항목마다 데이터 근거의 confidence를 0-1로 표시해주세요.

JSON 형식:
{{
  "problem_definition": {{
    "what": "...",
    "confidence": 0.0-1.0,
    "evidence_from_foundation": "..."
  }},
  "causal_attribution": {{
    "who": ["..."],
    "confidence": 0.0-1.0,
    "evidence_from_foundation": "..."
  }},
  "moral_evaluation": {{
    "judgment": "...",
    "confidence": 0.0-1.0,
    "evidence_from_foundation": "..."
  }},
  "treatment_recommendation": {{
    "what": "...",
    "confidence": 0.0-1.0,
    "evidence_from_foundation": "..."
  }}
}}
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    entman = json.loads(response.choices[0].message.content)

    result = {
        "method": "hybrid_foundation_entman",
        "layer1_foundation": foundation,
        "layer2_entman": entman
    }

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


# ============================================================================
# 방식 8: 하이브리드 2 (Foundation + Competition)
# ============================================================================

async def method8_hybrid_foundation_competition(perceptions, stats):
    """방식 8: Foundation + Competition"""
    print("\n" + "="*80)
    print("방식 8: Hybrid (Foundation + Competition)")
    print("="*80)

    # Foundation
    foundation = {
        "주요_주체": [s for s, _ in stats['subjects'].most_common(5)],
        "주요_키워드": [k for k, _ in stats['keywords'].most_common(10)],
        "valence_분포": dict(stats['valences'])
    }

    sample = perceptions[:15]
    perception_texts = []
    for p in sample:
        text = f"{p.get('perceived_subject')}: {p.get('claims', [])[:1]}"
        perception_texts.append(text)

    prompt = f"""
Foundation:
{json.dumps(foundation, ensure_ascii=False)}

Perceptions:
{chr(10).join(perception_texts)}

이 데이터가 보여주는 프레임과, 그것과 경쟁하는 프레임들을 비교해주세요.

valence 분포를 보면:
- negative: {stats['valences']['negative']}
- positive: {stats['valences']['positive']}

이것은 하나의 통일된 프레임인가, 아니면 여러 프레임이 경쟁하는가?

JSON 형식:
{{
  "dominant_frame": {{
    "name": "...",
    "strength": 0.0-1.0,
    "core_view": "...",
    "evidence": ["..."]
  }},
  "competing_frames": [
    {{
      "name": "...",
      "strength": 0.0-1.0,
      "core_view": "...",
      "key_difference": "..."
    }}
  ],
  "interpretation": "..."
}}
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.4
    )

    competition = json.loads(response.choices[0].message.content)

    result = {
        "method": "hybrid_foundation_competition",
        "layer1_foundation": foundation,
        "layer2_competition": competition
    }

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


# ============================================================================
# 방식 9: 완전 통합 (Foundation + Entman + Competition)
# ============================================================================

async def method9_full_integration(perceptions, stats):
    """방식 9: 완전 통합 (3개 레이어)"""
    print("\n" + "="*80)
    print("방식 9: Full Integration (Foundation + Entman + Competition)")
    print("="*80)

    # Layer 1: Foundation
    foundation = {
        "total_perceptions": stats['total'],
        "주요_주체": [s for s, _ in stats['subjects'].most_common(5)],
        "주요_키워드": [k for k, _ in stats['keywords'].most_common(10)],
        "주요_감정": [e for e, _ in stats['emotions'].most_common(5)],
        "valence": dict(stats['valences']),
        "organizing_principle": "정치적 감시와 권력 남용에 대한 우려"
    }

    sample = perceptions[:20]
    perception_texts = []
    for p in sample:
        text = f"{p.get('perceived_subject')} - {p.get('perceived_attribute')} ({p.get('perceived_valence')}): {p.get('claims', [])[:1]}"
        perception_texts.append(text)

    prompt = f"""
당신은 정치 프레임 분석가입니다.

Layer 1 - Foundation (실제 데이터):
{json.dumps(foundation, ensure_ascii=False, indent=2)}

Representative Perceptions:
{chr(10).join(perception_texts)}

다음 3개 레이어를 모두 분석해주세요:

Layer 2 - Entman Structure (4가지 기능):
- Problem Definition (confidence score 포함)
- Causal Attribution (confidence score 포함)
- Moral Evaluation (confidence score 포함)
- Treatment Recommendation (confidence score 포함)

Layer 3 - Competition (경쟁 프레임):
- 이 프레임의 강도
- 경쟁하는 다른 프레임들
- 핵심 차이점

JSON 형식:
{{
  "layer1_foundation": {{...이미 제공됨...}},
  "layer2_entman": {{
    "problem": {{
      "what": "...",
      "confidence": 0.0-1.0,
      "evidence": ["..."]
    }},
    "cause": {{
      "who": ["..."],
      "how": "...",
      "confidence": 0.0-1.0,
      "evidence": ["..."]
    }},
    "moral": {{
      "judgment": "...",
      "victims": ["..."],
      "responsible": ["..."],
      "confidence": 0.0-1.0,
      "evidence": ["..."]
    }},
    "solution": {{
      "what": "...",
      "who_acts": ["..."],
      "confidence": 0.0-1.0,
      "evidence": ["..."]
    }}
  }},
  "layer3_competition": {{
    "this_frame": {{
      "name": "...",
      "strength": 0.0-1.0,
      "core_view": "..."
    }},
    "competing_frames": [
      {{
        "name": "...",
        "strength": 0.0-1.0,
        "key_difference": "..."
      }}
    ]
  }}
}}
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)
    result['method'] = 'full_integration'
    result['layer1_foundation'] = foundation  # 실제 데이터로 대체

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


# ============================================================================
# 방식 10: 민주세력 맞춤형 (대조 중심)
# ============================================================================

async def method10_democratic_audience(perceptions, stats):
    """방식 10: 민주세력을 위한 대조 중심 설명"""
    print("\n" + "="*80)
    print("방식 10: Democratic Audience (대조 중심)")
    print("="*80)

    sample = perceptions[:15]
    perception_texts = []
    for p in sample:
        text = f"{p.get('perceived_subject')} - {p.get('perceived_attribute')}: {p.get('claims', [])[:1]}"
        perception_texts.append(text)

    prompt = f"""
청중: 민주당을 지지하는 사람들
목적: 이들이 "독재와 사찰의 부활" 프레임을 이해하도록 돕기

데이터:
{chr(10).join(perception_texts)}

민주세력이 이해하기 쉽도록, 대조 중심으로 설명해주세요:

JSON 형식:
{{
  "quick_summary": "이 프레임을 한 문장으로",
  "key_contrasts": [
    {{
      "topic": "...",
      "common_view": "일반적으로 (또는 민주당 지지자들이) 이렇게 봄",
      "this_frame_view": "이 프레임에서는 이렇게 봄",
      "why_different": "왜 다르게 보는가",
      "evidence": ["실제 데이터에서"]
    }}
  ],
  "what_to_understand": "민주세력이 알아야 할 핵심",
  "communication_tip": "소통하려면 어떻게 접근해야 하나"
}}
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.4
    )

    result = json.loads(response.choices[0].message.content)
    result['method'] = 'democratic_audience'

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


# ============================================================================
# 메인 실행 및 비교
# ============================================================================

async def run_all_methods():
    """모든 방식 실행 및 비교"""

    print("\n" + "="*80)
    print("종합 프레임 구조화 시뮬레이션")
    print("="*80)

    # 데이터 로드
    perceptions, stats = load_data()

    results = []

    # 방식 1: Foundation Only
    r1 = method1_foundation_only(stats)
    results.append(r1)

    # 방식 2: Entman Direct
    r2 = await method2_entman_direct(perceptions)
    results.append(r2)

    # 방식 3: Competition
    r3 = await method3_competition_frame(perceptions, stats)
    results.append(r3)

    # 방식 4: Goffman
    r4 = await method4_goffman_happening(perceptions)
    results.append(r4)

    # 방식 5: Lakoff
    r5 = await method5_lakoff_metaphors(perceptions, stats)
    results.append(r5)

    # 방식 6: Gamson
    r6 = await method6_gamson_package(perceptions, stats)
    results.append(r6)

    # 방식 7: Hybrid Foundation+Entman
    r7 = await method7_hybrid_foundation_entman(perceptions, stats)
    results.append(r7)

    # 방식 8: Hybrid Foundation+Competition
    r8 = await method8_hybrid_foundation_competition(perceptions, stats)
    results.append(r8)

    # 방식 9: Full Integration
    r9 = await method9_full_integration(perceptions, stats)
    results.append(r9)

    # 방식 10: Democratic Audience
    r10 = await method10_democratic_audience(perceptions, stats)
    results.append(r10)

    # 전체 결과 저장
    final_report = {
        "data_stats": {
            "total_perceptions": stats['total'],
            "주요_주체": [s for s, _ in stats['subjects'].most_common(5)],
            "주요_키워드": [k for k, _ in stats['keywords'].most_common(10)]
        },
        "results": results
    }

    with open('/tmp/comprehensive_frame_results.json', 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)

    print("\n\n" + "="*80)
    print("전체 결과 저장: /tmp/comprehensive_frame_results.json")
    print("="*80)

    return final_report


if __name__ == "__main__":
    asyncio.run(run_all_methods())
