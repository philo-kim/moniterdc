"""
실제 데이터 구조에 맞춘 세계관 표현 방식 실험

데이터 구조:
- perception: {subject, attribute, valence, claims[], keywords[], emotions[]}
- worldview: {title, frame, perception_ids[]}

목표: 어떤 방식이 "세계관 = 렌즈"를 가장 효과적으로 전달하는가?
"""

import os
import json
import asyncio
from supabase import create_client
from openai import AsyncOpenAI
from collections import Counter
from typing import List, Dict, Any
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


def load_worldview_with_perceptions():
    """worldview와 해당하는 모든 perception 로드"""
    print("데이터 로딩 중...")

    # worldview 중 "독재와 사찰의 부활" 가져오기
    wv_result = supabase.table('worldviews').select('*').eq('title', '독재와 사찰의 부활').execute()

    if not wv_result.data:
        print("worldview를 찾을 수 없습니다")
        # 첫 번째 worldview 사용
        wv_result = supabase.table('worldviews').select('*').limit(1).execute()

    worldview = wv_result.data[0] if wv_result.data else {}
    print(f"\nWorldview: {worldview.get('title', 'No title')}")
    print(f"ID: {worldview.get('id', 'No ID')}")

    # 실제 DB에 있는 모든 perception 가져오기 (perception_ids가 outdated됨)
    print("\n전체 perception 로드 중...")
    p_result = supabase.table('perceptions').select('*').execute()
    perceptions = p_result.data

    print(f"✓ Loaded {len(perceptions)} perceptions (전체)")

    return worldview, perceptions


def analyze_perception_structure(perceptions):
    """실제 perception 데이터 구조 분석"""
    print("\n" + "="*80)
    print("=== 데이터 구조 분석 ===")
    print("="*80)

    all_subjects = []
    all_attributes = []
    all_valences = []
    all_keywords = []
    all_emotions = []
    all_claims = []

    for p in perceptions:
        all_subjects.append(p.get('perceived_subject', ''))
        all_attributes.append(p.get('perceived_attribute', ''))
        all_valences.append(p.get('perceived_valence', ''))
        all_keywords.extend(p.get('keywords', []))
        all_emotions.extend(p.get('emotions', []))
        all_claims.extend(p.get('claims', []))

    print(f"\n총 perception: {len(perceptions)}개")
    print(f"총 claims: {len(all_claims)}개")
    print(f"총 keywords: {len(all_keywords)}개 (고유: {len(set(all_keywords))})")
    print(f"총 emotions: {len(all_emotions)}개 (고유: {len(set(all_emotions))})")

    print(f"\n주요 주체 Top 10:")
    for subject, count in Counter(all_subjects).most_common(10):
        if subject:
            print(f"  - {subject}: {count}회")

    print(f"\n주요 속성 Top 10:")
    for attr, count in Counter(all_attributes).most_common(10):
        if attr:
            print(f"  - {attr}: {count}회")

    print(f"\nValence 분포:")
    for val, count in Counter(all_valences).most_common():
        print(f"  - {val}: {count}개")

    print(f"\n주요 키워드 Top 15:")
    for kw, count in Counter(all_keywords).most_common(15):
        print(f"  - {kw}: {count}회")

    print(f"\n주요 감정 Top 10:")
    for em, count in Counter(all_emotions).most_common(10):
        print(f"  - {em}: {count}회")

    print(f"\n샘플 perception 3개:")
    for i, p in enumerate(perceptions[:3], 1):
        print(f"\n  [{i}] {p.get('perceived_subject')} - {p.get('perceived_attribute')}")
        print(f"      Valence: {p.get('perceived_valence')}")
        print(f"      Claims: {p.get('claims', [])[:2]}")
        print(f"      Keywords: {p.get('keywords', [])[:5]}")
        print(f"      Emotions: {p.get('emotions', [])}")

    return {
        'total': len(perceptions),
        'subjects': Counter(all_subjects),
        'attributes': Counter(all_attributes),
        'valences': Counter(all_valences),
        'keywords': Counter(all_keywords),
        'emotions': Counter(all_emotions),
        'all_claims': all_claims
    }


# ====================================
# 실험 1: 통계적 요약
# ====================================

async def experiment1_statistical_summary(perceptions, stats):
    """통계 기반 세계관 요약"""
    print("\n" + "="*80)
    print("=== 실험 1: 통계적 요약 방식 ===")
    print("="*80)

    summary = {
        "총_perception수": len(perceptions),
        "주요_주체_top5": [s for s, c in stats['subjects'].most_common(5)],
        "주요_속성_top5": [a for a, c in stats['attributes'].most_common(5)],
        "주요_키워드_top10": [k for k, c in stats['keywords'].most_common(10)],
        "주요_감정_top5": [e for e, c in stats['emotions'].most_common(5)],
        "감정_분포": dict(stats['valences'])
    }

    print("\n결과:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    print("\n=== 평가 ===")
    print("👍 장점: 객관적, 데이터에 충실, 검증 가능")
    print("👎 단점: '세계관 = 렌즈'를 전혀 전달하지 못함, 단순 통계일 뿐")
    print("📊 사용자 이해도: ★☆☆☆☆ (1/5)")

    return {
        "method": "statistical_summary",
        "result": summary,
        "understanding_score": 1,
        "fidelity_score": 5
    }


# ====================================
# 실험 2: GPT 단순 요약
# ====================================

async def experiment2_gpt_simple_summary(perceptions):
    """GPT에게 perception 주고 요약 요청"""
    print("\n" + "="*80)
    print("=== 실험 2: GPT 단순 요약 방식 ===")
    print("="*80)

    # 샘플 15개만 사용
    sample = perceptions[:15]

    perception_texts = []
    for i, p in enumerate(sample, 1):
        text = f"""
[{i}] {p.get('perceived_subject')} - {p.get('perceived_attribute')} ({p.get('perceived_valence')})
   Claims: {p.get('claims', [])}
   Keywords: {p.get('keywords', [])}
   Emotions: {p.get('emotions', [])}
"""
        perception_texts.append(text)

    prompt = f"""
다음은 특정 세계관에 속한 15개의 perception입니다:

{chr(10).join(perception_texts)}

이 perception들을 관통하는 세계관을 3-5문장으로 요약해주세요.
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    result = response.choices[0].message.content

    print("\n결과:")
    print(result)

    print("\n=== 평가 ===")
    print("👍 장점: 읽기 쉬움, 간결함")
    print("👎 단점: 추상적, '렌즈'를 경험할 수 없음, 정보 압축일 뿐")
    print("📊 사용자 이해도: ★★☆☆☆ (2/5)")

    return {
        "method": "gpt_simple_summary",
        "result": result,
        "understanding_score": 2,
        "fidelity_score": 3
    }


# ====================================
# 실험 3: 패턴 기반 해석 차이
# ====================================

async def experiment3_pattern_based_interpretation(perceptions, stats):
    """실제 데이터 패턴에서 해석 차이 추출"""
    print("\n" + "="*80)
    print("=== 실험 3: 패턴 기반 해석 차이 방식 ===")
    print("="*80)

    # 대표 perception 선정 (빈번한 주체 + 명확한 valence)
    representative = []

    # Top 주체들의 대표 perception
    for subject, _ in stats['subjects'].most_common(5):
        if not subject:
            continue
        for p in perceptions:
            if p.get('perceived_subject') == subject and p.get('claims'):
                representative.append(p)
                break

    # GPT에게 "이 perception들이 보여주는 렌즈"를 물어보기
    perception_texts = []
    for p in representative[:6]:
        text = f"""
주체: {p.get('perceived_subject')}
속성: {p.get('perceived_attribute')}
평가: {p.get('perceived_valence')}
주장: {p.get('claims', [])[:3]}
"""
        perception_texts.append(text)

    prompt = f"""
다음은 특정 세계관에 속한 대표적인 perception 6개입니다:

{chr(10).join(perception_texts)}

이 perception들이 공통적으로 보여주는 "렌즈의 특성"을 파악하고,
"해석 차이 예시" 3개를 만들어주세요.

형식:
{{
  "core_lens": "이 렌즈의 핵심 특성 (1문장)",
  "interpretation_examples": [
    {{
      "subject": "대상/주체",
      "normal_view": "일반적으로는 이렇게 봄",
      "through_this_lens": "이 렌즈로는 이렇게 봄",
      "key_difference": "핵심 차이점",
      "evidence_from_data": "실제 perception에서의 근거"
    }}
  ]
}}

실제 데이터에 기반해서 만들어주세요. 지어내지 마세요.
JSON 형식으로 답변해주세요.
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.5
    )

    result = json.loads(response.choices[0].message.content)

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n=== 평가 ===")
    print("👍 장점: 직관적, 렌즈의 차이를 보여줌, 이해하기 쉬움")
    print("👎 단점: GPT가 해석을 추가함, 실제 데이터와 정확히 일치하는가?")
    print("📊 사용자 이해도: ★★★★☆ (4/5)")

    return {
        "method": "pattern_based_interpretation",
        "result": result,
        "understanding_score": 4,
        "fidelity_score": 3
    }


# ====================================
# 실험 4: 실제 perception 직접 제시
# ====================================

async def experiment4_direct_perception_presentation(perceptions, stats):
    """가공 없이 대표 perception을 직접 보여주기"""
    print("\n" + "="*80)
    print("=== 실험 4: 실제 Perception 직접 제시 방식 ===")
    print("="*80)

    # 주요 주체별로 가장 대표적인 perception 선정
    representatives = []

    for subject, count in stats['subjects'].most_common(5):
        if not subject:
            continue

        # 해당 주체의 perception 중 claims가 많은 것
        subject_perceptions = [p for p in perceptions if p.get('perceived_subject') == subject]
        if subject_perceptions:
            best = max(subject_perceptions, key=lambda x: len(x.get('claims', [])))
            representatives.append({
                "subject": best.get('perceived_subject'),
                "attribute": best.get('perceived_attribute'),
                "valence": best.get('perceived_valence'),
                "claims": best.get('claims', [])[:3],
                "keywords": best.get('keywords', [])[:5],
                "emotions": best.get('emotions', [])[:3]
            })

    result = {
        "approach": "대표 perception을 직접 제시",
        "representative_perceptions": representatives[:5]
    }

    print("\n결과:")
    for i, rp in enumerate(result['representative_perceptions'], 1):
        print(f"\n[{i}] {rp['subject']} - {rp['attribute']}")
        print(f"    평가: {rp['valence']}")
        print(f"    주장: {rp['claims']}")
        print(f"    키워드: {rp['keywords']}")
        print(f"    감정: {rp['emotions']}")

    print("\n=== 평가 ===")
    print("👍 장점: 원본 데이터에 100% 충실, 가짜 없음")
    print("👎 단점: '렌즈'를 경험하기 어려움, 여전히 정보 나열")
    print("📊 사용자 이해도: ★★☆☆☆ (2/5)")

    return {
        "method": "direct_perception",
        "result": result,
        "understanding_score": 2,
        "fidelity_score": 5
    }


# ====================================
# 실험 5: 대조적 프레임 (A vs B vs C)
# ====================================

async def experiment5_contrastive_frames(perceptions, stats):
    """같은 대상을 다르게 보는 방식을 대조로 보여주기"""
    print("\n" + "="*80)
    print("=== 실험 5: 대조적 프레임 방식 ===")
    print("="*80)

    # 가장 빈번한 주체 선택
    top_subject = stats['subjects'].most_common(1)[0][0] if stats['subjects'] else None

    if not top_subject:
        print("주체를 찾을 수 없습니다")
        return None

    # 해당 주체에 대한 perception들
    subject_perceptions = [p for p in perceptions if p.get('perceived_subject') == top_subject][:5]

    perception_texts = []
    for p in subject_perceptions:
        text = f"""
속성: {p.get('perceived_attribute')}
평가: {p.get('perceived_valence')}
주장: {p.get('claims', [])}
"""
        perception_texts.append(text)

    prompt = f"""
다음은 "{top_subject}"에 대한 여러 perception입니다:

{chr(10).join(perception_texts)}

"{top_subject}"를 3가지 다른 렌즈로 볼 수 있습니다.
이 데이터는 그 중 어느 렌즈를 선택하고 있는지 보여주세요:

{{
  "subject": "{top_subject}",
  "possible_frames": [
    {{
      "frame_name": "프레임 A 이름",
      "view": "이렇게 본다",
      "this_is_chosen": false
    }},
    {{
      "frame_name": "프레임 B 이름",
      "view": "이렇게 본다",
      "this_is_chosen": false
    }},
    {{
      "frame_name": "프레임 C 이름",
      "view": "이렇게 본다",
      "this_is_chosen": true,
      "evidence": "실제 perception에서의 근거"
    }}
  ]
}}

JSON 형식으로 답변해주세요.
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.6
    )

    result = json.loads(response.choices[0].message.content)

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n=== 평가 ===")
    print("👍 장점: 선택의 이유가 명확함, 렌즈의 편향을 잘 드러냄")
    print("👎 단점: 다른 프레임들은 GPT가 만든 것, 실제 존재하는가?")
    print("📊 사용자 이해도: ★★★★☆ (4/5)")

    return {
        "method": "contrastive_frames",
        "result": result,
        "understanding_score": 4,
        "fidelity_score": 2
    }


# ====================================
# 실험 6: 하이브리드 (원본 + 해석 레이어)
# ====================================

async def experiment6_hybrid_original_plus_interpretation(perceptions, stats):
    """원본 perception + GPT 해석 레이어"""
    print("\n" + "="*80)
    print("=== 실험 6: 하이브리드 (원본 + 해석 레이어) ===")
    print("="*80)

    # Layer 1: 원본 통계
    layer1_stats = {
        "주요_주체": [s for s, c in stats['subjects'].most_common(5)],
        "주요_키워드": [k for k, c in stats['keywords'].most_common(10)],
        "주요_감정": [e for e, c in stats['emotions'].most_common(5)]
    }

    # Layer 2: 대표 perception
    representatives = []
    for subject, _ in stats['subjects'].most_common(3):
        if not subject:
            continue
        for p in perceptions:
            if p.get('perceived_subject') == subject and p.get('claims'):
                representatives.append({
                    "subject": p.get('perceived_subject'),
                    "attribute": p.get('perceived_attribute'),
                    "claims": p.get('claims', [])[:2]
                })
                break

    layer2_perceptions = representatives

    # Layer 3: GPT 해석
    perception_texts = []
    for rp in layer2_perceptions:
        text = f"{rp['subject']} - {rp['attribute']}: {rp['claims']}"
        perception_texts.append(text)

    prompt = f"""
다음은 세계관의 통계와 대표 perception입니다:

통계:
{json.dumps(layer1_stats, ensure_ascii=False)}

대표 Perception:
{chr(10).join(perception_texts)}

이 데이터가 보여주는 "렌즈의 특성"을 해석해주세요:

{{
  "core_lens": "이 렌즈의 핵심 특성 (1문장)",
  "what_they_focus_on": "이 렌즈가 주목하는 것",
  "what_they_ignore": "이 렌즈가 놓치는 것",
  "emotional_tone": "전반적인 감정 톤"
}}

JSON 형식으로 답변해주세요.
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.5
    )

    layer3_interpretation = json.loads(response.choices[0].message.content)

    result = {
        "layer1_statistics": layer1_stats,
        "layer2_representative_perceptions": layer2_perceptions,
        "layer3_gpt_interpretation": layer3_interpretation
    }

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n=== 평가 ===")
    print("👍 장점: 원본 충실성 + 해석 레이어, 검증 가능, 균형적")
    print("👎 단점: 복잡도 증가, 여전히 '렌즈 경험'은 약함")
    print("📊 사용자 이해도: ★★★☆☆ (3/5)")

    return {
        "method": "hybrid_original_plus_interpretation",
        "result": result,
        "understanding_score": 3,
        "fidelity_score": 4
    }


# ====================================
# 실험 7: 스토리텔링 (내러티브)
# ====================================

async def experiment7_narrative_storytelling(perceptions, stats):
    """이야기 형식으로 렌즈 전달"""
    print("\n" + "="*80)
    print("=== 실험 7: 스토리텔링 (내러티브) 방식 ===")
    print("="*80)

    # 샘플 perception
    sample = perceptions[:10]

    perception_texts = []
    for p in sample:
        text = f"{p.get('perceived_subject')} - {p.get('perceived_attribute')} ({p.get('perceived_valence')}): {p.get('claims', [])[:2]}"
        perception_texts.append(text)

    prompt = f"""
다음 perception들을 바탕으로:

{chr(10).join(perception_texts)}

이 세계관을 가진 사람의 시각으로 세상을 보는 짧은 내러티브를 작성해주세요.

"이 사람들에게 세상은..."으로 시작하는 3-4개 문단.
감정과 논리를 모두 담아주세요.

단, 실제 perception에 없는 내용을 지어내지 마세요.
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    result = response.choices[0].message.content

    print("\n결과:")
    print(result)

    print("\n=== 평가 ===")
    print("👍 장점: 감정적으로 공감 가능, 렌즈를 '느낄' 수 있음")
    print("👎 단점: 지나치게 주관적, 검증 어려움, CLAUDE.md 위반 가능성")
    print("⚠️  경고: 사용자가 만든 스크립트/서사를 강요하는 것일 수 있음")
    print("📊 사용자 이해도: ★★★☆☆ (3/5)")

    return {
        "method": "narrative_storytelling",
        "result": result,
        "understanding_score": 3,
        "fidelity_score": 1,
        "warning": "CLAUDE.md 온보딩 원칙 위반 가능성"
    }


# ====================================
# 종합 평가
# ====================================

async def run_all_experiments():
    """모든 실험 실행 및 비교"""

    print("="*80)
    print("실제 데이터 기반 세계관 표현 방식 종합 실험")
    print("="*80)

    # 데이터 로드
    worldview, perceptions = load_worldview_with_perceptions()

    if not perceptions:
        print("데이터 로드 실패")
        return

    # 데이터 구조 분석
    stats = analyze_perception_structure(perceptions)

    # 모든 실험 실행
    results = []

    results.append(await experiment1_statistical_summary(perceptions, stats))
    results.append(await experiment2_gpt_simple_summary(perceptions))
    results.append(await experiment3_pattern_based_interpretation(perceptions, stats))
    results.append(await experiment4_direct_perception_presentation(perceptions, stats))
    results.append(await experiment5_contrastive_frames(perceptions, stats))
    results.append(await experiment6_hybrid_original_plus_interpretation(perceptions, stats))
    results.append(await experiment7_narrative_storytelling(perceptions, stats))

    # 최종 비교
    print("\n\n" + "="*80)
    print("=== 전체 실험 결과 비교 ===")
    print("="*80)

    print("\n{:40s} {:20s} {:20s}".format("방법", "사용자 이해도", "데이터 충실성"))
    print("-"*80)

    for r in results:
        method = r['method']
        understanding = "★" * r['understanding_score'] + "☆" * (5 - r['understanding_score'])
        fidelity = "★" * r['fidelity_score'] + "☆" * (5 - r['fidelity_score'])
        print(f"{method:40s} {understanding:20s} {fidelity:20s}")

    # 분석
    print("\n\n" + "="*80)
    print("=== 핵심 발견 ===")
    print("="*80)

    analysis = """
트레이드오프가 명확합니다:

1. 데이터 충실성 ↑ → 사용자 이해도 ↓
   - 실험 1, 4: 원본에 충실하지만 '렌즈'를 전달 못함

2. 사용자 이해도 ↑ → 데이터 충실성 ↓
   - 실험 3, 5: 렌즈를 잘 보여주지만 GPT가 해석 추가

3. 내러티브 (실험 7): 공감은 가능하지만 위험성 높음
   - CLAUDE.md 위반 가능성
   - 사용자 주도권 침해 가능성

=== 질문 ===

어떤 것을 선택할 것인가?

A. 충실성 우선 (실험 1, 4)
   → 사용자가 스스로 해석하게 함
   → 하지만 대부분의 사용자는 해석 못함

B. 이해도 우선 (실험 3, 5)
   → GPT 해석 레이어 제공
   → 하지만 "가짜" 세계관 만들 위험

C. 균형 (실험 6)
   → 원본 + 해석 레이어 병행
   → 하지만 복잡도 증가

=== 더 깊은 질문 ===

애초에 "세계관을 표현한다"는 것이 가능한가?

- 세계관 = 137개 perception의 집합
- 통일된 "렌즈"가 존재하지 않을 수도 있음
- 우리가 "렌즈"를 만들어내는 것일 수도 있음

대안:
- 세계관을 "표현"하려 하지 말고
- perception들을 "탐색"할 수 있게 하는 것은 어떤가?
"""

    print(analysis)

    # 결과 저장
    final_report = {
        "worldview": {
            "id": worldview['id'],
            "title": worldview.get('title'),
            "total_perceptions": len(perceptions)
        },
        "data_analysis": {
            "total": stats['total'],
            "주요_주체": [s for s, c in stats['subjects'].most_common(5)],
            "주요_키워드": [k for k, c in stats['keywords'].most_common(10)]
        },
        "experiments": results,
        "conclusion": analysis
    }

    with open('/tmp/real_worldview_experiments_result.json', 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)

    print("\n\n전체 결과 저장: /tmp/real_worldview_experiments_result.json")

    return final_report


if __name__ == "__main__":
    asyncio.run(run_all_experiments())
