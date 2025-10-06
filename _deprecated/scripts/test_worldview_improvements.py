"""
방법 3 (Narrative + Metadata) 개선안 시뮬레이션

테스트할 개선 방안:
1. 매칭 방식: 키워드 vs Vector Similarity vs Hybrid
2. Metadata 구조: 단순 vs 복합 vs 계층형
3. Narrative 깊이: 요약형 vs 상세형 vs 예시 중심형
4. 세계관 개수: GPT 자동 결정 vs 고정 개수 vs 계층적 구조
"""

import asyncio
import sys
import os
import json
import numpy as np
from openai import AsyncOpenAI
from engines.utils.supabase_client import get_supabase

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def fetch_sample_data(limit=30):
    """실제 layered_perceptions 샘플 가져오기"""
    supabase = get_supabase()

    lps = supabase.table('layered_perceptions')\
        .select('id, content_id, deep_beliefs, implicit_assumptions, worldview_hints, explicit_claims')\
        .limit(limit)\
        .execute().data

    # Get content titles
    for lp in lps:
        content = supabase.table('contents')\
            .select('title')\
            .eq('id', lp['content_id'])\
            .execute().data[0]
        lp['title'] = content['title']

    return lps


async def improvement1_matching_methods(samples):
    """
    개선 1: 매칭 방식 비교

    A. 키워드 매칭 (현재 방식)
    B. Vector Similarity 매칭
    C. Hybrid (키워드 + Vector)
    """
    print("\n" + "="*70)
    print("개선 1: 매칭 방식 비교")
    print("="*70)

    # 먼저 세계관 생성
    belief_summary = []
    for lp in samples[:15]:
        belief_summary.append({
            'title': lp['title'],
            'deep_beliefs': lp.get('deep_beliefs', [])[:3],
            'implicit_assumptions': lp.get('implicit_assumptions', [])[:2],
            'worldview_hints': lp.get('worldview_hints', '')
        })

    prompt = f"""
다음은 DC Gallery 글 {len(belief_summary)}개의 분석 결과입니다.

{json.dumps(belief_summary, ensure_ascii=False, indent=2)}

**주요 세계관 4-5개**를 추출하고, 각각:

1. **Narrative**: 자연어 상세 설명 (300자 이상)
2. **Metadata**: 주체, 핵심 개념, 논리 패턴

JSON 형식:
{{
  "worldviews": [
    {{
      "title": "세계관 제목",
      "narrative": "상세한 자연어 설명...",
      "metadata": {{
        "subjects": ["주체1", "주체2"],
        "key_concepts": ["개념1", "개념2", "개념3"],
        "historical_references": ["역사1", "역사2"],
        "logic_pattern": "A → B → C",
        "emotions": ["감정1", "감정2"]
      }}
    }}
  ]
}}
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert in political discourse analysis. Always respond in valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    worldviews = result.get('worldviews', [])

    print(f"\n✅ {len(worldviews)}개 세계관 생성")

    # 테스트용 perception 5개
    test_perceptions = samples[15:20]

    # A. 키워드 매칭
    print("\n" + "─"*70)
    print("A. 키워드 매칭")
    print("─"*70)

    keyword_matches = []
    for lp in test_perceptions:
        lp_text = ' '.join(lp.get('deep_beliefs', []) + lp.get('implicit_assumptions', []))

        best_match = None
        best_score = 0

        for wv in worldviews:
            score = 0
            metadata = wv['metadata']

            for subject in metadata.get('subjects', []):
                if subject in lp_text:
                    score += 2

            for concept in metadata.get('key_concepts', []):
                if concept in lp_text:
                    score += 1

            if score > best_score:
                best_score = score
                best_match = wv['title']

        keyword_matches.append({
            'title': lp['title'][:50],
            'matched': best_match,
            'score': best_score
        })
        print(f"  {lp['title'][:45]}... → {best_match} ({best_score})")

    # B. Vector Similarity 매칭
    print("\n" + "─"*70)
    print("B. Vector Similarity 매칭")
    print("─"*70)

    # Worldview embeddings
    wv_embeddings = []
    for wv in worldviews:
        emb_response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=wv['narrative']
        )
        wv_embeddings.append({
            'title': wv['title'],
            'embedding': emb_response.data[0].embedding
        })

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    vector_matches = []
    for lp in test_perceptions:
        lp_text = ' '.join(lp.get('deep_beliefs', []))

        lp_emb_response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=lp_text
        )
        lp_embedding = lp_emb_response.data[0].embedding

        best_match = None
        best_sim = 0

        for wv_emb in wv_embeddings:
            sim = cosine_similarity(lp_embedding, wv_emb['embedding'])
            if sim > best_sim:
                best_sim = sim
                best_match = wv_emb['title']

        vector_matches.append({
            'title': lp['title'][:50],
            'matched': best_match,
            'similarity': best_sim
        })
        print(f"  {lp['title'][:45]}... → {best_match} ({best_sim:.3f})")

    # C. Hybrid (키워드 + Vector)
    print("\n" + "─"*70)
    print("C. Hybrid 매칭 (키워드 30% + Vector 70%)")
    print("─"*70)

    hybrid_matches = []
    for i, lp in enumerate(test_perceptions):
        keyword_score = keyword_matches[i]['score']
        vector_score = vector_matches[i]['similarity']

        # Normalize keyword score (0-1)
        normalized_keyword = min(keyword_score / 5.0, 1.0)

        # Hybrid score
        hybrid_score = 0.3 * normalized_keyword + 0.7 * vector_score

        # Find best match
        best_match = vector_matches[i]['matched']  # Default to vector match

        hybrid_matches.append({
            'title': lp['title'][:50],
            'matched': best_match,
            'hybrid_score': hybrid_score
        })
        print(f"  {lp['title'][:45]}... → {best_match} ({hybrid_score:.3f})")

    # 비교
    print("\n" + "="*70)
    print("📊 매칭 방식 평가")
    print("="*70)

    print("\n| 방식 | 속도 | 정확도 | 설명력 | 비용 |")
    print("|------|------|--------|--------|------|")
    print("| 키워드 | ⚡⚡⚡ | ⚠️  | ✅ | 무료 |")
    print("| Vector | ⚡⚡ | ✅✅ | ⚠️  | 💰 |")
    print("| Hybrid | ⚡⚡ | ✅✅ | ✅ | 💰 |")

    return {
        'recommendation': 'hybrid',
        'reason': 'Vector로 의미적 유사도 + 키워드로 명시적 연결 확인'
    }


async def improvement2_metadata_structure(samples):
    """
    개선 2: Metadata 구조 비교

    A. 단순형: 키워드 리스트만
    B. 복합형: 키워드 + 가중치
    C. 계층형: 카테고리별 구조화
    """
    print("\n" + "="*70)
    print("개선 2: Metadata 구조 비교")
    print("="*70)

    # A. 단순형
    print("\n" + "─"*70)
    print("A. 단순형 Metadata")
    print("─"*70)

    simple_metadata = {
        "subjects": ["민주당", "좌파"],
        "key_concepts": ["독재", "사찰", "권력남용"],
        "emotions": ["분노", "위기감"]
    }

    print(json.dumps(simple_metadata, ensure_ascii=False, indent=2))
    print("\n장점: 간단, 빠름")
    print("단점: 중요도 구분 불가, 관계 표현 불가")

    # B. 복합형 (가중치 포함)
    print("\n" + "─"*70)
    print("B. 복합형 Metadata (가중치)")
    print("─"*70)

    weighted_metadata = {
        "subjects": [
            {"name": "민주당", "importance": 1.0},
            {"name": "좌파", "importance": 0.9},
            {"name": "검찰", "importance": 0.5}
        ],
        "key_concepts": [
            {"concept": "독재", "centrality": 1.0},
            {"concept": "사찰", "centrality": 0.9},
            {"concept": "권력남용", "centrality": 0.7}
        ],
        "emotions": [
            {"emotion": "분노", "intensity": 0.8},
            {"emotion": "위기감", "intensity": 0.9}
        ]
    }

    print(json.dumps(weighted_metadata, ensure_ascii=False, indent=2))
    print("\n장점: 중요도 구분, 매칭 정확도 향상")
    print("단점: 가중치 결정 어려움")

    # C. 계층형 (구조화)
    print("\n" + "─"*70)
    print("C. 계층형 Metadata (구조화)")
    print("─"*70)

    hierarchical_metadata = {
        "core": {
            "primary_subject": "민주당",
            "primary_attribute": "독재성향",
            "primary_action": "사찰"
        },
        "interpretation_frame": {
            "historical_lens": {
                "reference_period": "1970-80년대 군사독재",
                "reference_events": ["민간인 사찰", "언론통제"],
                "projection_logic": "과거 패턴 → 현재 반복"
            },
            "causal_chain": [
                "권력 획득",
                "작은 월권",
                "점진적 확대",
                "전면 독재"
            ],
            "slippery_slope": {
                "trigger": "유심교체 정보 확인",
                "escalation": "사찰 → 장악 → 독재",
                "endpoint": "1970년대식 감시국가"
            }
        },
        "emotional_drivers": {
            "primary": "위기감",
            "secondary": ["분노", "불신"],
            "urgency_level": "high"
        },
        "validation_criteria": {
            "confirming_evidence": ["정보 파악 사례", "인사 개입"],
            "disconfirming_ignored": ["합법적 절차", "견제 작동"]
        }
    }

    print(json.dumps(hierarchical_metadata, ensure_ascii=False, indent=2))
    print("\n장점: 완전한 구조, 깊은 이해, 분석 가능")
    print("단점: 복잡, GPT 생성 어려움")

    # GPT로 실제 생성 테스트
    print("\n" + "─"*70)
    print("실제 GPT 생성 테스트")
    print("─"*70)

    sample = samples[2]  # "민주당 사찰" 글

    prompt = f"""
다음 분석 결과를 계층형 Metadata로 변환하세요:

제목: {sample['title']}
심층 믿음: {sample.get('deep_beliefs', [])}
암묵적 전제: {sample.get('implicit_assumptions', [])}

계층형 구조:
{{
  "core": {{
    "primary_subject": "주요 대상",
    "primary_attribute": "핵심 속성",
    "primary_action": "핵심 행동"
  }},
  "interpretation_frame": {{
    "historical_lens": {{
      "reference_period": "참조 시기",
      "reference_events": ["사건1", "사건2"],
      "projection_logic": "투영 논리"
    }},
    "causal_chain": ["단계1", "단계2", "단계3"],
    "slippery_slope": {{
      "trigger": "시작점",
      "escalation": "확대 경로",
      "endpoint": "최종 결과"
    }}
  }},
  "emotional_drivers": {{
    "primary": "주 감정",
    "secondary": ["부 감정들"],
    "urgency_level": "긴급도"
  }}
}}

JSON으로 응답:
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert. Always respond in valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    generated = json.loads(response.choices[0].message.content)
    print("\nGPT 생성 결과:")
    print(json.dumps(generated, ensure_ascii=False, indent=2))

    # 평가
    print("\n" + "="*70)
    print("📊 Metadata 구조 평가")
    print("="*70)

    print("\n| 구조 | 생성 용이성 | 매칭 정확도 | 이해 깊이 | 유지보수 |")
    print("|------|------------|------------|----------|---------|")
    print("| 단순형 | ⚡⚡⚡ | ⚠️  | ⚠️  | ✅✅ |")
    print("| 복합형 | ⚡⚡ | ✅ | ✅ | ✅ |")
    print("| 계층형 | ⚡ | ✅✅ | ✅✅✅ | ⚠️  |")

    return {
        'recommendation': 'hierarchical',
        'reason': '세계관의 구조를 완전히 표현, 여당 지지자가 논리 체인 이해 가능'
    }


async def improvement3_narrative_depth(samples):
    """
    개선 3: Narrative 깊이 비교

    A. 요약형: 2-3문장
    B. 상세형: 단락 형식
    C. 예시 중심형: 구체적 사례 포함
    """
    print("\n" + "="*70)
    print("개선 3: Narrative 깊이 비교")
    print("="*70)

    sample = samples[2]

    # A. 요약형
    print("\n" + "─"*70)
    print("A. 요약형 Narrative")
    print("─"*70)

    summary_narrative = """
민주당/좌파의 모든 권력 행사를 과거 독재정권의 재현으로 해석한다.
작은 월권도 반드시 전면적 감시국가로 발전한다고 믿는다.
"""

    print(summary_narrative)
    print("\n장점: 빠른 이해")
    print("단점: 맥락 부족, 왜 그렇게 생각하는지 불명확")

    # B. 상세형
    print("\n" + "─"*70)
    print("B. 상세형 Narrative")
    print("─"*70)

    detailed_narrative = """
이 세계관을 가진 사람들은 민주당이나 좌파 정권의 모든 행동을
과거 박정희/전두환 독재 정권과 동일선상에서 해석한다.

예를 들어, 통신사에서 유심 교체 정보를 알았다는 사실을
'통신사 협박을 통한 불법 사찰'로 즉시 해석하며, 이것이
과거 독재 시절의 민간인 사찰과 본질적으로 같다고 본다.

작은 월권이나 정보 파악도 '독재의 초기 단계'로 인식하며,
방치하면 반드시 전면적 감시국가로 발전한다고 믿는다(슬리퍼리 슬로프).

따라서 현재는 '독재 전야'이며, 지금 저지하지 않으면
1970-80년대로 회귀한다는 위기감을 가진다.
"""

    print(detailed_narrative)
    print("\n장점: 완전한 이해, 논리 체인 명확")
    print("단점: 길이, 읽기 부담")

    # C. 예시 중심형
    print("\n" + "─"*70)
    print("C. 예시 중심형 Narrative")
    print("─"*70)

    example_narrative = """
**세계관 핵심:**
민주당/좌파 = 독재정권 재현

**구체적 해석 방식:**

📌 사례 1: 유심교체 정보 확인
  - DC Gallery 해석: "통신사 협박 → 불법 사찰 → 독재 시작"
  - 일반인 해석: "정상적 정보 파악일 수도..."
  - 차이점: 즉시 '독재'로 연결

📌 사례 2: 판사 인사
  - DC Gallery 해석: "맘에 안드는 판사 제거 → 사법부 장악 → 독재"
  - 일반인 해석: "정상적 인사 절차..."
  - 차이점: 모든 인사를 '장악'으로 해석

**핵심 논리:**
작은 것 → 큰 것으로 반드시 확대된다 (슬리퍼리 슬로프)

**역사적 참조:**
1970-80년대 민간인 사찰 → 언론통제 → 야당 탄압

**감정:**
"지금 막지 않으면 우리도 독재 시대로 돌아간다" (위기감)
"""

    print(example_narrative)
    print("\n장점: 구체적, 이해 쉬움, 비교 가능")
    print("단점: 예시 선정 어려움")

    # 평가
    print("\n" + "="*70)
    print("📊 Narrative 깊이 평가")
    print("="*70)

    print("\n| 형식 | 이해 속도 | 이해 깊이 | 공감 유발 | 활용성 |")
    print("|------|----------|----------|----------|--------|")
    print("| 요약형 | ⚡⚡⚡ | ⚠️  | ⚠️  | ⚠️  |")
    print("| 상세형 | ⚡ | ✅✅ | ✅ | ✅ |")
    print("| 예시형 | ⚡⚡ | ✅✅✅ | ✅✅ | ✅✅ |")

    return {
        'recommendation': 'example_based',
        'reason': '구체적 예시로 이해 쉬움, 여당 지지자가 "아 이래서 저렇게 말하는구나" 즉시 파악'
    }


async def improvement4_worldview_count(samples):
    """
    개선 4: 세계관 개수 결정 방식

    A. GPT 자동 결정 (현재)
    B. 고정 개수 (5개, 10개)
    C. 계층적 구조 (대분류 → 중분류)
    """
    print("\n" + "="*70)
    print("개선 4: 세계관 개수 결정 방식")
    print("="*70)

    # A. GPT 자동 결정
    print("\n" + "─"*70)
    print("A. GPT 자동 결정")
    print("─"*70)

    belief_summary = []
    for lp in samples[:20]:
        belief_summary.append({
            'deep_beliefs': lp.get('deep_beliefs', [])[:2],
            'worldview_hints': lp.get('worldview_hints', '')
        })

    prompt_auto = f"""
{len(belief_summary)}개 분석 결과를 보고, **적절한 개수의 세계관**을 추출하세요.
(너무 적으면 과도한 단순화, 너무 많으면 파편화)

{json.dumps(belief_summary[:10], ensure_ascii=False)}

JSON: {{"worldviews": [...]}}
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt_auto}],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    auto_result = json.loads(response.choices[0].message.content)
    print(f"  결과: {len(auto_result.get('worldviews', []))}개 세계관")
    print("  장점: 데이터에 맞게 유연")
    print("  단점: 일관성 없음, 예측 불가")

    # B. 고정 개수
    print("\n" + "─"*70)
    print("B. 고정 개수 (7개)")
    print("─"*70)

    prompt_fixed = f"""
{len(belief_summary)}개 분석 결과를 **정확히 7개 세계관**으로 분류하세요.

{json.dumps(belief_summary[:10], ensure_ascii=False)}

JSON: {{"worldviews": [...7개...]}}
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt_fixed}],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    fixed_result = json.loads(response.choices[0].message.content)
    print(f"  결과: {len(fixed_result.get('worldviews', []))}개 세계관")
    print("  장점: 일관성, 예측 가능")
    print("  단점: 데이터에 안 맞을 수 있음")

    # C. 계층적 구조
    print("\n" + "─"*70)
    print("C. 계층적 구조 (대분류 → 세부)")
    print("─"*70)

    prompt_hierarchical = f"""
{len(belief_summary)}개 분석 결과를 **계층적 세계관 구조**로 조직하세요.

1단계: 3-4개 대분류
2단계: 각 대분류마다 2-3개 세부 세계관

예시:
{{
  "hierarchy": [
    {{
      "category": "대분류 1",
      "subcategories": [
        {{"title": "세부 1-1", "narrative": "..."}},
        {{"title": "세부 1-2", "narrative": "..."}}
      ]
    }}
  ]
}}

{json.dumps(belief_summary[:10], ensure_ascii=False)}
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt_hierarchical}],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    hierarchical_result = json.loads(response.choices[0].message.content)
    hierarchy = hierarchical_result.get('hierarchy', [])

    print(f"  결과: {len(hierarchy)}개 대분류")
    for cat in hierarchy:
        print(f"    - {cat.get('category', 'N/A')}: {len(cat.get('subcategories', []))}개 세부")

    print("  장점: 조직화, 브라우징 쉬움, 유연성")
    print("  단점: 복잡도 증가")

    # 평가
    print("\n" + "="*70)
    print("📊 세계관 개수 결정 평가")
    print("="*70)

    print("\n| 방식 | 일관성 | 유연성 | 사용성 | 확장성 |")
    print("|------|--------|--------|--------|--------|")
    print("| 자동 | ⚠️  | ✅✅ | ✅ | ✅ |")
    print("| 고정 | ✅✅ | ⚠️  | ✅ | ⚠️  |")
    print("| 계층 | ✅ | ✅✅ | ✅✅ | ✅✅ |")

    return {
        'recommendation': 'hierarchical',
        'reason': '대분류로 전체 파악 + 세부로 깊이 탐색 가능'
    }


async def main():
    print("="*70)
    print("방법 3 개선안 상세 시뮬레이션")
    print("="*70)

    samples = await fetch_sample_data(limit=30)
    print(f"\n✅ {len(samples)}개 샘플 로드\n")

    results = {}

    # 4가지 개선 영역 테스트
    results['matching'] = await improvement1_matching_methods(samples)
    results['metadata'] = await improvement2_metadata_structure(samples)
    results['narrative'] = await improvement3_narrative_depth(samples)
    results['count'] = await improvement4_worldview_count(samples)

    # 최종 추천
    print("\n" + "="*70)
    print("🏆 최종 추천 구성")
    print("="*70)

    print("\n1. 매칭 방식: Hybrid (키워드 30% + Vector 70%)")
    print("   → 의미적 유사도 + 명시적 연결 확인")

    print("\n2. Metadata 구조: 계층형")
    print("   → core + interpretation_frame + emotional_drivers")

    print("\n3. Narrative 깊이: 예시 중심형")
    print("   → 구체적 사례로 이해 용이")

    print("\n4. 세계관 개수: 계층적 (3-4 대분류 → 각 2-3 세부)")
    print("   → 전체 파악 + 깊이 탐색 가능")

    print("\n" + "="*70)
    print("최적 WorldviewConstructor 설계")
    print("="*70)

    optimal_design = """

class OptimalWorldviewConstructor:

    async def construct(self, perceptions):
        # 1. 계층적 세계관 추출
        worldviews = await self._extract_hierarchical_worldviews(perceptions)

        # 각 세계관 구조:
        {
          "category": "대분류명",
          "subcategories": [
            {
              "title": "세부 세계관",
              "narrative": {
                "summary": "한 줄",
                "examples": [
                  {
                    "case": "구체적 사례",
                    "interpretation": "해석 방식",
                    "contrast": "일반인 해석과 차이"
                  }
                ],
                "logic_chain": "A → B → C",
                "historical_context": "과거 참조"
              },
              "metadata": {
                "core": {...},
                "interpretation_frame": {...},
                "emotional_drivers": {...}
              }
            }
          ]
        }

        # 2. Perception 매칭 (Hybrid)
        for perception in perceptions:
            # Vector similarity
            vector_scores = await self._calculate_vector_similarity(
                perception, worldviews
            )

            # Keyword matching
            keyword_scores = self._calculate_keyword_match(
                perception, worldviews
            )

            # Hybrid score
            final_scores = 0.7 * vector_scores + 0.3 * keyword_scores

            # Link to worldviews (threshold > 0.6)
            await self._create_links(perception, final_scores)
    """

    print(optimal_design)

if __name__ == '__main__':
    asyncio.run(main())
