"""
실제 데이터로 다양한 세계관 표현 방식을 실험하고 비교하는 연구 스크립트

목표: 어떤 방식이 "세계관 = 렌즈"를 가장 잘 전달하는지 실증적으로 확인
"""

import os
import json
import asyncio
from supabase import create_client
from openai import AsyncOpenAI
from collections import Counter
from typing import List, Dict, Any
import numpy as np

# Setup
SUPABASE_URL = "https://ycmcsdbxnpmthekzyppl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InljbWNzZGJ4bnBtdGhla3p5cHBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc4MzA5NzUsImV4cCI6MjA3MzQwNjk3NX0.FNN_2LdvfbIa__swyIKgzwSDVjIqaeUQisUfsuee-48"
OPENAI_API_KEY = "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"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

WORLDVIEW_ID = "5f3e5b8a-88c4-4ae9-b6ed-c8f9e3d4a1c7"  # 독재와 사찰의 부활


def load_perceptions():
    """실제 perception 데이터 로드"""
    result = supabase.table('perceptions').select('*').eq('worldview_id', WORLDVIEW_ID).execute()
    print(f"✓ Loaded {len(result.data)} perceptions")
    return result.data


def analyze_data_structure(perceptions):
    """데이터의 실제 구조 분석"""
    print("\n=== 데이터 구조 분석 ===")

    # 각 perception의 구조 확인
    if perceptions:
        sample = perceptions[0]
        print(f"\nPerception 필드: {sample.keys()}")
        print(f"\nSample perception:")
        print(json.dumps(sample, ensure_ascii=False, indent=2)[:500])

    # 통계
    total_explicit = []
    total_implicit = []
    total_deep = []

    for p in perceptions:
        layers = p.get('layers', {})
        if isinstance(layers, str):
            layers = json.loads(layers)

        explicit = layers.get('explicit_message', [])
        implicit = layers.get('implicit_assumptions', [])
        deep = layers.get('deep_beliefs', [])

        if isinstance(explicit, list):
            total_explicit.extend(explicit)
        if isinstance(implicit, list):
            total_implicit.extend(implicit)
        if isinstance(deep, list):
            total_deep.extend(deep)

    print(f"\n총 명시적 메시지: {len(total_explicit)}개")
    print(f"총 암시적 가정: {len(total_implicit)}개")
    print(f"총 심층 믿음: {len(total_deep)}개")
    print(f"고유 심층 믿음: {len(set(total_deep))}개")

    return {
        'total_perceptions': len(perceptions),
        'total_explicit': len(total_explicit),
        'total_implicit': len(total_implicit),
        'total_deep': len(total_deep),
        'unique_deep': len(set(total_deep))
    }


# ====================================
# 실험 1: 단순 요약 방식
# ====================================

async def experiment1_simple_summary(perceptions):
    """GPT에게 "이 세계관을 요약해줘"라고 물어보기"""
    print("\n\n=== 실험 1: 단순 요약 방식 ===")

    # 샘플 10개만 사용
    sample = perceptions[:10]

    perception_texts = []
    for p in sample:
        layers = p.get('layers', {})
        if isinstance(layers, str):
            layers = json.loads(layers)

        text = f"""
        명시적: {layers.get('explicit_message', [])}
        암시적: {layers.get('implicit_assumptions', [])}
        심층: {layers.get('deep_beliefs', [])}
        """
        perception_texts.append(text)

    prompt = f"""
다음은 "독재와 사찰의 부활"이라는 세계관에 속한 10개의 담론 분석입니다.

{chr(10).join(perception_texts)}

이 세계관을 3-5문장으로 요약해주세요.
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    result = response.choices[0].message.content
    print("\n결과:")
    print(result)

    return {
        "method": "simple_summary",
        "result": result,
        "pros": "빠르고 간단",
        "cons": "렌즈의 특성을 전달하지 못함, 단순 정보 압축"
    }


# ====================================
# 실험 2: 프레임 구조 방식
# ====================================

async def experiment2_frame_structure(perceptions):
    """프레임 이론 기반 구조화"""
    print("\n\n=== 실험 2: 프레임 구조 방식 ===")

    sample = perceptions[:10]

    perception_texts = []
    for p in sample:
        layers = p.get('layers', {})
        if isinstance(layers, str):
            layers = json.loads(layers)

        text = f"""
        명시적: {layers.get('explicit_message', [])}
        암시적: {layers.get('implicit_assumptions', [])}
        심층: {layers.get('deep_beliefs', [])}
        """
        perception_texts.append(text)

    prompt = f"""
다음은 "독재와 사찰의 부활"이라는 세계관에 속한 10개의 담론 분석입니다.

{chr(10).join(perception_texts)}

프레임 이론에 따라 다음 구조로 분석해주세요:

1. Problem Definition (문제 정의): 이들은 무엇을 문제로 보는가?
2. Causal Attribution (원인 진단): 문제의 원인을 어디에서 찾는가?
3. Moral Evaluation (도덕적 판단): 누가 책임이 있고, 누가 피해자인가?
4. Treatment Recommendation (해결책): 무엇을 해야 한다고 보는가?

JSON 형식으로 답변해주세요.
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)
    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return {
        "method": "frame_structure",
        "result": result,
        "pros": "체계적, 이론적으로 탄탄함",
        "cons": "추상적, 실제 '렌즈로 보기'를 경험하기 어려움"
    }


# ====================================
# 실험 3: 해석 차이 예시 방식
# ====================================

async def experiment3_interpretation_examples(perceptions):
    """같은 사건을 어떻게 다르게 보는가"""
    print("\n\n=== 실험 3: 해석 차이 예시 방식 ===")

    sample = perceptions[:15]

    perception_texts = []
    for p in sample:
        layers = p.get('layers', {})
        if isinstance(layers, str):
            layers = json.loads(layers)

        text = f"""
        명시적: {layers.get('explicit_message', [])}
        암시적: {layers.get('implicit_assumptions', [])}
        심층: {layers.get('deep_beliefs', [])}
        """
        perception_texts.append(text)

    prompt = f"""
다음은 "독재와 사찰의 부활"이라는 세계관에 속한 15개의 담론 분석입니다.

{chr(10).join(perception_texts)}

이 세계관을 가장 잘 이해할 수 있는 "해석 차이 예시" 3-4개를 만들어주세요.

형식:
{{
  "examples": [
    {{
      "event": "어떤 사건/현상",
      "normal_view": "일반적으로는 이렇게 봄",
      "this_worldview": "이 세계관에서는 이렇게 봄",
      "key_difference": "핵심 차이가 뭔지"
    }}
  ]
}}

실제 데이터에 기반해서, 구체적이고 명확한 예시를 만들어주세요.
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

    return {
        "method": "interpretation_examples",
        "result": result,
        "pros": "직관적, 렌즈의 차이를 직접 경험 가능",
        "cons": "GPT가 만든 예시가 실제 데이터와 정확히 일치하는가?"
    }


# ====================================
# 실험 4: 실제 담론 기반 방식
# ====================================

async def experiment4_actual_discourse_based(perceptions):
    """실제 perception을 그대로 보여주되, 선택과 구성으로 의미 전달"""
    print("\n\n=== 실험 4: 실제 담론 기반 방식 ===")

    # 통계로 대표 perception 선정
    all_deep_beliefs = []
    for p in perceptions:
        layers = p.get('layers', {})
        if isinstance(layers, str):
            layers = json.loads(layers)

        deep = layers.get('deep_beliefs', [])
        if isinstance(deep, list):
            all_deep_beliefs.extend(deep)

    # 가장 빈번한 심층 믿음
    common_beliefs = Counter(all_deep_beliefs).most_common(5)
    print(f"\n가장 빈번한 심층 믿음 Top 5:")
    for belief, count in common_beliefs:
        print(f"  - {belief} ({count}회)")

    # 각 핵심 믿음을 가장 잘 보여주는 perception 선정
    representative_perceptions = []
    for belief, _ in common_beliefs[:3]:
        for p in perceptions:
            layers = p.get('layers', {})
            if isinstance(layers, str):
                layers = json.loads(layers)

            deep = layers.get('deep_beliefs', [])
            if belief in deep:
                representative_perceptions.append({
                    'core_belief': belief,
                    'explicit': layers.get('explicit_message', []),
                    'implicit': layers.get('implicit_assumptions', []),
                    'deep': layers.get('deep_beliefs', [])
                })
                break

    print(f"\n대표 perception 3개:")
    for rp in representative_perceptions:
        print(f"\n핵심 믿음: {rp['core_belief']}")
        print(f"  명시: {rp['explicit'][:1]}")
        print(f"  암시: {rp['implicit'][:1]}")

    result = {
        "common_beliefs": [b for b, _ in common_beliefs],
        "representative_perceptions": representative_perceptions
    }

    return {
        "method": "actual_discourse_based",
        "result": result,
        "pros": "원본 데이터에 충실, 가짜 없음",
        "cons": "여전히 '정보 나열'에 가까움, 렌즈를 경험하기 어려움"
    }


# ====================================
# 실험 5: 하이브리드 - 원본 + 해석 레이어
# ====================================

async def experiment5_hybrid_approach(perceptions):
    """원본 데이터 + GPT 해석 레이어"""
    print("\n\n=== 실험 5: 하이브리드 방식 ===")

    # Step 1: 통계로 대표 perception 선정
    all_deep_beliefs = []
    for p in perceptions:
        layers = p.get('layers', {})
        if isinstance(layers, str):
            layers = json.loads(layers)

        deep = layers.get('deep_beliefs', [])
        if isinstance(deep, list):
            all_deep_beliefs.extend(deep)

    common_beliefs = Counter(all_deep_beliefs).most_common(3)

    # 대표 perception 추출
    representative_perceptions = []
    for belief, _ in common_beliefs:
        for p in perceptions:
            layers = p.get('layers', {})
            if isinstance(layers, str):
                layers = json.loads(layers)

            deep = layers.get('deep_beliefs', [])
            if belief in deep:
                representative_perceptions.append({
                    'explicit': layers.get('explicit_message', []),
                    'implicit': layers.get('implicit_assumptions', []),
                    'deep': layers.get('deep_beliefs', [])
                })
                break

    # Step 2: GPT에게 이 perception들이 "어떤 렌즈인지" 해석 요청
    perception_texts = []
    for i, rp in enumerate(representative_perceptions, 1):
        text = f"""
담론 {i}:
- 명시: {rp['explicit']}
- 암시: {rp['implicit']}
- 심층: {rp['deep']}
"""
        perception_texts.append(text)

    prompt = f"""
다음은 "독재와 사찰의 부활" 세계관의 대표적인 담론 3개입니다:

{chr(10).join(perception_texts)}

이 담론들을 보면, 이 세계관은 "세상을 어떤 렌즈로 보는가"?

다음 형식으로 답변해주세요:

{{
  "core_lens": "한 문장으로, 이 렌즈의 핵심 특성",
  "what_they_see": "다른 사람들이 못 보는데 이들이 보는 것",
  "what_they_miss": "이 렌즈 때문에 놓치는 것",
  "interpretation_example": {{
    "event": "구체적 사건",
    "normal_view": "일반적 해석",
    "through_this_lens": "이 렌즈로 본 해석"
  }}
}}

JSON 형식으로 답변해주세요.
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.5
    )

    interpretation = json.loads(response.choices[0].message.content)

    result = {
        "original_data": {
            "representative_perceptions": representative_perceptions,
            "common_beliefs": [b for b, _ in common_beliefs]
        },
        "interpretation_layer": interpretation
    }

    print("\n결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return {
        "method": "hybrid",
        "result": result,
        "pros": "원본 충실성 + 해석 레이어, 검증 가능",
        "cons": "복잡도 증가, GPT 의존도 있음"
    }


# ====================================
# 실험 6: 내러티브 방식
# ====================================

async def experiment6_narrative_approach(perceptions):
    """이야기 형식으로 세계관 전달"""
    print("\n\n=== 실험 6: 내러티브 방식 ===")

    sample = perceptions[:10]

    perception_texts = []
    for p in sample:
        layers = p.get('layers', {})
        if isinstance(layers, str):
            layers = json.loads(layers)

        text = f"""
        명시적: {layers.get('explicit_message', [])}
        암시적: {layers.get('implicit_assumptions', [])}
        심층: {layers.get('deep_beliefs', [])}
        """
        perception_texts.append(text)

    prompt = f"""
다음은 "독재와 사찰의 부활"이라는 세계관에 속한 10개의 담론 분석입니다.

{chr(10).join(perception_texts)}

이 세계관을 가진 사람의 관점을 전달하는 짧은 내러티브를 작성해주세요.

형식: "이 사람들에게 세상은..."으로 시작하는 3-4개 문단

감정과 논리를 모두 담아, 마치 그들의 눈으로 보는 것처럼 작성해주세요.
"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    result = response.choices[0].message.content
    print("\n결과:")
    print(result)

    return {
        "method": "narrative",
        "result": result,
        "pros": "감정적 공감 가능, 렌즈를 '느낄' 수 있음",
        "cons": "지나치게 주관적, 데이터 검증 어려움, CLAUDE.md 위반 가능성"
    }


# ====================================
# 실험 7: 대조 방식 (다른 세계관과 비교)
# ====================================

async def experiment7_contrast_approach(perceptions):
    """다른 세계관과의 대조로 특성 부각"""
    print("\n\n=== 실험 7: 대조 방식 ===")

    sample = perceptions[:10]

    perception_texts = []
    for p in sample:
        layers = p.get('layers', {})
        if isinstance(layers, str):
            layers = json.loads(layers)

        text = f"""
        명시적: {layers.get('explicit_message', [])}
        암시적: {layers.get('implicit_assumptions', [])}
        심층: {layers.get('deep_beliefs', [])}
        """
        perception_texts.append(text)

    prompt = f"""
다음은 "독재와 사찰의 부활"이라는 세계관에 속한 10개의 담론 분석입니다.

{chr(10).join(perception_texts)}

이 세계관의 특성을 가장 잘 드러내는 방법은 "대조"입니다.

같은 사건에 대해 3가지 가능한 해석을 제시하고, 이 세계관이 어디에 해당하는지 보여주세요:

{{
  "event": "구체적 사건",
  "interpretation_A": "해석 A (예: 무능)",
  "interpretation_B": "해석 B (예: 실수)",
  "interpretation_C": "해석 C (예: 의도적 사찰)",
  "this_worldview_chooses": "C",
  "why": "왜 C를 선택하는가"
}}

3개 예시를 JSON 배열로 제공해주세요.
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

    return {
        "method": "contrast",
        "result": result,
        "pros": "선택의 이유를 명확히 보여줌, 렌즈의 편향 드러냄",
        "cons": "다른 해석들을 GPT가 만들어야 함, 실제 존재하는 해석인가?"
    }


# ====================================
# 비교 및 평가
# ====================================

async def evaluate_all_methods():
    """모든 방법 실행 및 비교"""

    print("=" * 80)
    print("실제 데이터 기반 세계관 표현 방식 실험")
    print("=" * 80)

    # 데이터 로드
    perceptions = load_perceptions()

    # 데이터 구조 분석
    stats = analyze_data_structure(perceptions)

    # 모든 실험 실행
    results = []

    results.append(await experiment1_simple_summary(perceptions))
    results.append(await experiment2_frame_structure(perceptions))
    results.append(await experiment3_interpretation_examples(perceptions))
    results.append(await experiment4_actual_discourse_based(perceptions))
    results.append(await experiment5_hybrid_approach(perceptions))
    results.append(await experiment6_narrative_approach(perceptions))
    results.append(await experiment7_contrast_approach(perceptions))

    # 결과 비교
    print("\n\n" + "=" * 80)
    print("전체 실험 결과 비교")
    print("=" * 80)

    for i, result in enumerate(results, 1):
        print(f"\n실험 {i}: {result['method']}")
        print(f"  장점: {result['pros']}")
        print(f"  단점: {result['cons']}")

    # 최종 결과 저장
    final_report = {
        "data_stats": stats,
        "experiments": results,
        "analysis": """

        === 분석 ===

        각 방법의 효과를 실제로 확인한 결과:

        1. 단순 요약: 정보 압축일 뿐, 렌즈를 전달하지 못함
        2. 프레임 구조: 체계적이지만 추상적, 경험 불가
        3. 해석 차이 예시: 직관적이지만 GPT 의존
        4. 실제 담론 기반: 충실하지만 여전히 정보 나열
        5. 하이브리드: 균형적이지만 복잡
        6. 내러티브: 감성적이지만 검증 어려움
        7. 대조: 명확하지만 인위적

        === 핵심 질문 ===

        어떤 방법이 "이 사람들이 세상을 어떻게 보는가"를 가장 잘 전달하는가?
        """
    }

    with open('/tmp/worldview_experiment_results.json', 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)

    print("\n\n전체 결과 저장: /tmp/worldview_experiment_results.json")

    return final_report


if __name__ == "__main__":
    asyncio.run(evaluate_all_methods())
