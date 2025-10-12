"""
세계관 통합 전략 시뮬레이션
실제 데이터로 5가지 전략을 테스트하고 결과 비교
"""

import asyncio
import os
from supabase import create_client
from openai import AsyncOpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from collections import Counter
import numpy as np
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 클라이언트 초기화
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)
openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))


async def get_worldview_data(worldview_id=None):
    """세계관과 모든 perception 데이터 가져오기"""
    if worldview_id is None:
        # 첫 번째 세계관
        wv_response = supabase.table('worldviews').select('*').limit(1).execute()
        worldview = wv_response.data[0]
    else:
        worldview = supabase.table('worldviews').select('*').eq('id', worldview_id).execute().data[0]

    # 모든 perception 가져오기
    perception_ids = worldview['perception_ids']
    perceptions = supabase.table('layered_perceptions').select('*').in_('id', perception_ids).execute().data

    return worldview, perceptions


def extract_all_texts(perceptions):
    """모든 perception에서 텍스트 추출"""
    all_deep_beliefs = []
    all_implicit_assumptions = []
    all_explicit_subjects = []

    for lp in perceptions:
        if lp.get('deep_beliefs'):
            all_deep_beliefs.extend(lp['deep_beliefs'])
        if lp.get('implicit_assumptions'):
            all_implicit_assumptions.extend(lp['implicit_assumptions'])
        if lp.get('explicit_claims'):
            for claim in lp['explicit_claims']:
                all_explicit_subjects.append(claim.get('subject', ''))

    return all_deep_beliefs, all_implicit_assumptions, all_explicit_subjects


# ============================================================================
# 전략 1: 대표 Perception 자동 선택 (TF-IDF + Centroid)
# ============================================================================

def strategy1_representative_selection(perceptions):
    """TF-IDF로 중심에 가장 가까운 perception 3개 선택"""
    print("\n" + "="*80)
    print("전략 1: 대표 Perception 자동 선택")
    print("="*80)

    # 각 perception의 deep_beliefs를 하나의 문서로
    docs = []
    for lp in perceptions:
        text = ' '.join(lp.get('deep_beliefs', []))
        docs.append(text)

    # TF-IDF 벡터화
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(docs)

    # 중심점(centroid) 계산
    centroid = np.asarray(tfidf_matrix.mean(axis=0))

    # 각 문서와 중심점의 유사도
    similarities = cosine_similarity(tfidf_matrix, centroid)

    # 상위 3개 인덱스
    top3_indices = similarities.flatten().argsort()[-3:][::-1]

    print(f"\n총 {len(perceptions)}개 중 대표 3개 선택:")
    for i, idx in enumerate(top3_indices, 1):
        lp = perceptions[idx]
        print(f"\n{i}. Perception {idx} (유사도: {similarities[idx][0]:.3f})")
        print(f"   Deep Beliefs:")
        for belief in lp.get('deep_beliefs', [])[:2]:
            print(f"   - {belief[:100]}...")

    return {
        'strategy': 'representative_selection',
        'representative_ids': [perceptions[i]['id'] for i in top3_indices],
        'representative_perceptions': [perceptions[i] for i in top3_indices]
    }


# ============================================================================
# 전략 2: GPT 기반 세계관 요약 생성
# ============================================================================

async def strategy2_gpt_summary(perceptions):
    """GPT로 모든 deep_beliefs를 통합 요약"""
    print("\n" + "="*80)
    print("전략 2: GPT 기반 세계관 요약 생성")
    print("="*80)

    # 모든 deep_beliefs 수집
    all_deep_beliefs = []
    for lp in perceptions:
        all_deep_beliefs.extend(lp.get('deep_beliefs', []))

    # 중복 제거
    unique_beliefs = list(set(all_deep_beliefs))

    print(f"\n총 {len(all_deep_beliefs)}개 deep_beliefs (유니크: {len(unique_beliefs)}개)")

    # GPT 프롬프트
    prompt = f"""다음은 같은 세계관("독재와 사찰의 부활")에 속한 {len(perceptions)}개 분석에서 나온 심층 믿음(deep_beliefs)들입니다.

이들의 공통 패턴을 찾아 하나의 통합된 세계관 구조로 요약하세요.

Deep Beliefs:
{chr(10).join([f"- {b}" for b in unique_beliefs[:50]])}

... (총 {len(unique_beliefs)}개)

다음 형식으로 JSON을 반환하세요:
{{
  "core_belief": "핵심 심층 믿음 1-2문장",
  "logic_chain": "전형적인 논리 연쇄 (A → B → C 형식)",
  "key_subjects": ["핵심 주체들"],
  "key_patterns": ["반복되는 패턴 3-5개"],
  "summary": "이 세계관에 대한 전체 요약 2-3문장"
}}"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 담론 분석 전문가입니다. 여러 분석 결과에서 공통 패턴을 찾아 통합합니다."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)

    print(f"\n생성된 통합 요약:")
    print(f"핵심 믿음: {result['core_belief']}")
    print(f"논리 연쇄: {result['logic_chain']}")
    print(f"핵심 주체: {', '.join(result['key_subjects'])}")
    print(f"주요 패턴:")
    for pattern in result['key_patterns']:
        print(f"  - {pattern}")

    return {
        'strategy': 'gpt_summary',
        'result': result
    }


# ============================================================================
# 전략 3: 클러스터링 기반 하위 패턴 발견
# ============================================================================

def strategy3_clustering(perceptions):
    """K-means로 3-5개 하위 클러스터 발견"""
    print("\n" + "="*80)
    print("전략 3: 클러스터링 기반 하위 패턴 발견")
    print("="*80)

    # 각 perception의 deep_beliefs를 하나의 문서로
    docs = []
    for lp in perceptions:
        text = ' '.join(lp.get('deep_beliefs', []))
        docs.append(text)

    # TF-IDF 벡터화
    vectorizer = TfidfVectorizer(max_features=100)
    tfidf_matrix = vectorizer.fit_transform(docs)

    # K-means 클러스터링 (k=4)
    n_clusters = 4
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(tfidf_matrix)

    print(f"\n{n_clusters}개 클러스터로 분류:")

    cluster_info = []
    for i in range(n_clusters):
        cluster_perceptions = [perceptions[j] for j in range(len(perceptions)) if clusters[j] == i]

        # 이 클러스터의 모든 deep_beliefs
        cluster_beliefs = []
        for lp in cluster_perceptions:
            cluster_beliefs.extend(lp.get('deep_beliefs', []))

        # 가장 흔한 단어들
        all_text = ' '.join(cluster_beliefs)
        words = all_text.split()
        common_words = Counter(words).most_common(5)

        print(f"\n클러스터 {i+1}: {len(cluster_perceptions)}개 perception")
        print(f"  주요 키워드: {', '.join([w for w, c in common_words])}")
        print(f"  샘플 deep_belief: {cluster_beliefs[0][:80]}...")

        cluster_info.append({
            'cluster_id': i,
            'size': len(cluster_perceptions),
            'keywords': [w for w, c in common_words[:5]],
            'sample_belief': cluster_beliefs[0] if cluster_beliefs else ""
        })

    return {
        'strategy': 'clustering',
        'n_clusters': n_clusters,
        'clusters': cluster_info
    }


# ============================================================================
# 전략 4: 빈도 기반 핵심 요소 추출
# ============================================================================

def strategy4_frequency_analysis(perceptions):
    """빈도 분석으로 핵심 주체, 키워드, 패턴 추출"""
    print("\n" + "="*80)
    print("전략 4: 빈도 기반 핵심 요소 추출")
    print("="*80)

    all_deep_beliefs, all_implicit, all_subjects = extract_all_texts(perceptions)

    # 주체 빈도
    subject_counter = Counter(all_subjects)
    top_subjects = subject_counter.most_common(10)

    print(f"\n핵심 주체 (top 10):")
    for subject, count in top_subjects:
        print(f"  {subject}: {count}회")

    # Deep_beliefs에서 키워드 추출
    all_beliefs_text = ' '.join(all_deep_beliefs)

    # 한국어 주요 명사 추출 (간단한 방법)
    keywords = ['사찰', '독재', '권력', '민주당', '좌파', '사법', '정권', '국가', '기관', '탄압',
                '감시', '통제', '장악', '제압', '반대', '비호', '친북']

    keyword_counts = {}
    for keyword in keywords:
        count = all_beliefs_text.count(keyword)
        if count > 0:
            keyword_counts[keyword] = count

    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)

    print(f"\n핵심 키워드:")
    for keyword, count in sorted_keywords[:10]:
        print(f"  {keyword}: {count}회")

    # 공통 패턴 (자주 나오는 구절)
    common_phrases = [
        "권력을 위해", "권력 유지", "국가기관", "반대파", "사법부",
        "좌파 정권", "독재 정권", "과거", "탄압"
    ]

    phrase_counts = {}
    for phrase in common_phrases:
        count = all_beliefs_text.count(phrase)
        if count > 0:
            phrase_counts[phrase] = count

    sorted_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)

    print(f"\n공통 패턴:")
    for phrase, count in sorted_phrases[:5]:
        print(f"  '{phrase}': {count}회")

    return {
        'strategy': 'frequency_analysis',
        'top_subjects': dict(top_subjects[:10]),
        'top_keywords': dict(sorted_keywords[:10]),
        'top_patterns': dict(sorted_phrases[:5])
    }


# ============================================================================
# 전략 5: 하이브리드 (대표 선택 + GPT 보강)
# ============================================================================

async def strategy5_hybrid(perceptions):
    """빈도 분석 + 대표 선택 + GPT 요약"""
    print("\n" + "="*80)
    print("전략 5: 하이브리드 (통계 + AI)")
    print("="*80)

    # 1. 빈도 분석
    freq_result = strategy4_frequency_analysis(perceptions)

    # 2. 대표 perception 선택
    rep_result = strategy1_representative_selection(perceptions)

    # 3. GPT로 통합 요약 생성 (대표 3개 + 빈도 정보 활용)
    representative_perceptions = rep_result['representative_perceptions']

    rep_text = ""
    for i, lp in enumerate(representative_perceptions, 1):
        rep_text += f"\n대표 Perception {i}:\n"
        rep_text += f"Deep Beliefs: {', '.join(lp.get('deep_beliefs', []))}\n"

    prompt = f"""다음은 "독재와 사찰의 부활" 세계관의 핵심 정보입니다.

**빈도 분석 결과:**
- 핵심 주체: {', '.join(freq_result['top_subjects'].keys())}
- 핵심 키워드: {', '.join(freq_result['top_keywords'].keys())}
- 공통 패턴: {', '.join(freq_result['top_patterns'].keys())}

**대표적인 Perception 3개:**
{rep_text}

이 정보를 바탕으로 세계관의 통합 구조를 JSON 형식으로 생성하세요:

{{
  "core_belief": "이 세계관의 핵심 심층 믿음 (1-2문장)",
  "logic_chain": "전형적인 사고 흐름 (A → B → C → D 형식)",
  "key_subjects": ["주요 주체 3-5개"],
  "narrative_summary": "이 세계관을 가진 사람들이 세상을 보는 방식 (3-4문장)",
  "examples": [
    {{
      "case": "대표 사례명",
      "dc_interpretation": "DC에서 보는 방식",
      "normal_interpretation": "일반적으로 보는 방식",
      "gap": "해석 차이의 핵심"
    }}
  ]
}}"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 담론 분석 전문가입니다."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)

    print(f"\n생성된 통합 narrative:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return {
        'strategy': 'hybrid',
        'frequency_analysis': freq_result,
        'representative_ids': rep_result['representative_ids'],
        'narrative': result
    }


# ============================================================================
# 메인 시뮬레이션
# ============================================================================

async def main():
    print("="*80)
    print("세계관 통합 전략 시뮬레이션 시작")
    print("="*80)

    # 데이터 로드
    worldview, perceptions = await get_worldview_data()

    print(f"\n세계관: {worldview['title']}")
    print(f"총 perception 수: {len(perceptions)}")

    # 5가지 전략 실행
    results = {}

    # 전략 1
    results['strategy1'] = strategy1_representative_selection(perceptions)

    # 전략 2
    results['strategy2'] = await strategy2_gpt_summary(perceptions)

    # 전략 3
    results['strategy3'] = strategy3_clustering(perceptions)

    # 전략 4
    results['strategy4'] = strategy4_frequency_analysis(perceptions)

    # 전략 5
    results['strategy5'] = await strategy5_hybrid(perceptions)

    # 결과 저장
    with open('simulation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "="*80)
    print("시뮬레이션 완료! 결과: simulation_results.json")
    print("="*80)

    return results


if __name__ == "__main__":
    asyncio.run(main())
