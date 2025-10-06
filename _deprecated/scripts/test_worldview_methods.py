"""
세계관 구성 방식 시뮬레이션 테스트

실제 데이터로 3가지 방식을 테스트:
1. Vector embedding only
2. Structured template
3. Narrative + Metadata hybrid
"""

import asyncio
import sys
import os
import json
from openai import AsyncOpenAI
from engines.utils.supabase_client import get_supabase

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def fetch_sample_data(limit=20):
    """실제 layered_perceptions 샘플 가져오기"""
    supabase = get_supabase()

    lps = supabase.table('layered_perceptions')\
        .select('id, content_id, deep_beliefs, implicit_assumptions, worldview_hints')\
        .limit(limit)\
        .execute().data

    # Get content titles for context
    for lp in lps:
        content = supabase.table('contents')\
            .select('title')\
            .eq('id', lp['content_id'])\
            .execute().data[0]
        lp['title'] = content['title']

    return lps


async def method1_vector_only(samples):
    """
    방법 1: Vector Embedding만 사용

    - deep_beliefs를 모두 concatenate
    - embedding 계산
    - clustering으로 그룹화
    """
    print("\n" + "="*70)
    print("방법 1: Vector Embedding Only")
    print("="*70)

    # Step 1: 모든 deep_beliefs를 텍스트로 변환
    belief_texts = []
    for lp in samples:
        beliefs = lp.get('deep_beliefs', [])
        text = ' | '.join(beliefs)
        belief_texts.append({
            'id': lp['id'],
            'text': text,
            'title': lp['title']
        })

    # Step 2: Embedding 계산
    print(f"\n{len(belief_texts)}개 perception의 embedding 계산 중...")

    embeddings = []
    for bt in belief_texts[:10]:  # First 10 for speed
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=bt['text']
        )
        embeddings.append({
            'id': bt['id'],
            'title': bt['title'],
            'embedding': response.data[0].embedding
        })

    # Step 3: 간단한 clustering (cosine similarity)
    import numpy as np

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    # 첫 번째를 seed로 사용
    clusters = []
    threshold = 0.75

    for emb in embeddings:
        matched = False
        for cluster in clusters:
            # 클러스터의 첫 번째 요소와 비교
            sim = cosine_similarity(emb['embedding'], cluster[0]['embedding'])
            if sim > threshold:
                cluster.append(emb)
                matched = True
                break

        if not matched:
            clusters.append([emb])

    print(f"\n✅ {len(clusters)}개 클러스터 발견")

    for i, cluster in enumerate(clusters[:3], 1):
        print(f"\n클러스터 {i}: {len(cluster)}개")
        for item in cluster[:2]:
            print(f"  - {item['title'][:60]}")

    # 평가
    print("\n📊 평가:")
    print("  장점: 자동화 가능, 객관적")
    print("  단점: 왜 같은 그룹인지 설명 불가, threshold 조정 어려움")

    return {
        'method': 'vector_only',
        'clusters': len(clusters),
        'avg_cluster_size': sum(len(c) for c in clusters) / len(clusters),
        'explainable': False
    }


async def method2_structured_template(samples):
    """
    방법 2: Structured Template

    - GPT로 구조화된 템플릿 추출
    - who/what/why/how/where 분석
    - 템플릿 유사도로 그룹화
    """
    print("\n" + "="*70)
    print("방법 2: Structured Template")
    print("="*70)

    # Step 1: 샘플 3개로 템플릿 생성
    sample_lps = samples[:3]

    templates = []

    for lp in sample_lps:
        prompt = f"""
다음 분석 결과를 구조화된 템플릿으로 변환해주세요.

제목: {lp['title']}
심층 믿음: {lp.get('deep_beliefs', [])}
암묵적 전제: {lp.get('implicit_assumptions', [])}

템플릿:
{{
  "who": "주체 (누구에 대한 이야기인가)",
  "what_they_do": "행동 (무엇을 한다고 보는가)",
  "why_they_do": "동기 (왜 그렇게 한다고 보는가)",
  "how_it_works": "메커니즘 (어떻게 작동한다고 보는가)",
  "where_it_leads": "결과 (어디로 향한다고 보는가)"
}}

JSON으로 응답:
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in discourse analysis. Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        template = json.loads(response.choices[0].message.content)
        templates.append({
            'id': lp['id'],
            'title': lp['title'],
            'template': template
        })

    print(f"\n✅ {len(templates)}개 템플릿 생성")

    for i, t in enumerate(templates, 1):
        print(f"\n템플릿 {i}: {t['title'][:60]}")
        print(f"  Who: {t['template'].get('who', 'N/A')}")
        print(f"  What: {t['template'].get('what_they_do', 'N/A')[:80]}")

    # Step 2: 템플릿 유사도 계산 (who 기준)
    who_groups = {}
    for t in templates:
        who = t['template'].get('who', 'unknown')
        if who not in who_groups:
            who_groups[who] = []
        who_groups[who].append(t)

    print(f"\n{len(who_groups)}개 그룹 (who 기준)")

    # 평가
    print("\n📊 평가:")
    print("  장점: 구조화되어 이해 쉬움, 섹션별 비교 가능")
    print("  단점: GPT 호출 많음, 템플릿 정의 필요")

    return {
        'method': 'structured_template',
        'groups': len(who_groups),
        'explainable': True,
        'gpt_calls': len(samples)
    }


async def method3_narrative_metadata(samples):
    """
    방법 3: Narrative + Metadata Hybrid

    - GPT로 자연어 서술 + 메타데이터 추출
    - narrative는 사람이 읽기 위함
    - metadata는 자동 분류용
    """
    print("\n" + "="*70)
    print("방법 3: Narrative + Metadata Hybrid")
    print("="*70)

    # Step 1: 전체 샘플을 보고 세계관 추출

    # 대표 샘플 수집
    belief_summary = []
    for lp in samples[:10]:
        belief_summary.append({
            'title': lp['title'],
            'deep_beliefs': lp.get('deep_beliefs', [])[:2],
            'worldview_hints': lp.get('worldview_hints', '')
        })

    prompt = f"""
다음은 DC Gallery 글 {len(belief_summary)}개의 분석 결과입니다.

{json.dumps(belief_summary, ensure_ascii=False, indent=2)}

이 중에서 **주요 세계관 3-5개**를 추출하고, 각 세계관을:

1. **Narrative** (자연어 서술 - 여당 지지자가 읽고 이해할 수 있게)
2. **Metadata** (키워드, 패턴 - 시스템이 분류에 사용)

로 표현해주세요.

JSON 형식:
{{
  "worldviews": [
    {{
      "title": "세계관 제목",
      "narrative": {{
        "summary": "한 줄 요약",
        "full_description": "자세한 설명 (200자 이상)",
        "example_interpretation": "구체적 해석 예시"
      }},
      "metadata": {{
        "subjects": ["주체1", "주체2"],
        "key_concepts": ["개념1", "개념2"],
        "logic_pattern": "논리 패턴",
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

    print(f"\n✅ {len(worldviews)}개 세계관 추출")

    for i, wv in enumerate(worldviews, 1):
        print(f"\n세계관 {i}: {wv['title']}")
        print(f"  요약: {wv['narrative']['summary']}")
        print(f"  주체: {', '.join(wv['metadata']['subjects'])}")
        print(f"  개념: {', '.join(wv['metadata']['key_concepts'][:3])}")

    # Step 2: 각 perception을 세계관에 매칭
    print(f"\n\n매칭 시뮬레이션 (샘플 5개):")

    for lp in samples[:5]:
        # 간단한 키워드 매칭
        lp_text = ' '.join(lp.get('deep_beliefs', []))

        best_match = None
        best_score = 0

        for wv in worldviews:
            score = 0
            for subject in wv['metadata']['subjects']:
                if subject in lp_text:
                    score += 1
            for concept in wv['metadata']['key_concepts']:
                if concept in lp_text:
                    score += 0.5

            if score > best_score:
                best_score = score
                best_match = wv['title']

        print(f"\n  '{lp['title'][:50]}...'")
        print(f"    → {best_match} (score: {best_score:.1f})")

    # 평가
    print("\n📊 평가:")
    print("  장점: 이해 쉬움 + 자동 분류 가능, 유연함")
    print("  단점: 복잡함, GPT 호출 필요")

    return {
        'method': 'narrative_metadata',
        'worldviews': len(worldviews),
        'explainable': True,
        'flexible': True,
        'gpt_calls': 1,  # 한 번만 호출
        'worldviews_data': worldviews
    }


async def main():
    print("="*70)
    print("세계관 구성 방식 시뮬레이션 테스트")
    print("="*70)

    # 실제 데이터 로드
    print("\n실제 layered_perceptions 데이터 로드 중...")
    samples = await fetch_sample_data(limit=20)
    print(f"✅ {len(samples)}개 샘플 로드 완료")

    # 3가지 방식 시뮬레이션
    results = []

    result1 = await method1_vector_only(samples)
    results.append(result1)

    result2 = await method2_structured_template(samples)
    results.append(result2)

    result3 = await method3_narrative_metadata(samples)
    results.append(result3)

    # 최종 비교
    print("\n" + "="*70)
    print("최종 비교")
    print("="*70)

    print("\n| 방식 | 설명가능성 | GPT 호출 | 이해 용이성 | 자동화 |")
    print("|------|-----------|----------|------------|--------|")
    print(f"| 방법 1 | {'❌' if not result1['explainable'] else '✅'} | 0 | ⚠️  | ✅ |")
    print(f"| 방법 2 | {'✅' if result2['explainable'] else '❌'} | {result2['gpt_calls']} | ✅ | ⚠️  |")
    print(f"| 방법 3 | {'✅' if result3['explainable'] else '❌'} | {result3['gpt_calls']} | ✅✅ | ✅ |")

    print("\n🏆 추천: 방법 3 (Narrative + Metadata)")
    print("\n이유:")
    print("  1. 한 번의 GPT 호출로 전체 세계관 추출")
    print("  2. Narrative로 사람이 완전히 이해 가능")
    print("  3. Metadata로 자동 분류 가능")
    print("  4. 유연하게 확장 가능")

    # 방법 3의 실제 결과 상세 출력
    if result3.get('worldviews_data'):
        print("\n" + "="*70)
        print("방법 3 실제 추출 결과 (상세)")
        print("="*70)

        for i, wv in enumerate(result3['worldviews_data'], 1):
            print(f"\n{'─'*70}")
            print(f"세계관 {i}: {wv['title']}")
            print(f"{'─'*70}")
            print(f"\n📖 Narrative:")
            print(f"  요약: {wv['narrative']['summary']}")
            print(f"\n  상세:\n  {wv['narrative']['full_description']}")
            print(f"\n  해석 예시:\n  {wv['narrative']['example_interpretation']}")

            print(f"\n🏷️  Metadata:")
            print(f"  주체: {', '.join(wv['metadata']['subjects'])}")
            print(f"  핵심 개념: {', '.join(wv['metadata']['key_concepts'])}")
            print(f"  논리 패턴: {wv['metadata']['logic_pattern']}")
            print(f"  감정: {', '.join(wv['metadata']['emotions'])}")

if __name__ == '__main__':
    asyncio.run(main())
