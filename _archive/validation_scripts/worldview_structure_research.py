"""
세계관 구조 연구: 실제 데이터 기반 최적 구조 찾기

실험 목표:
- 137개 perception을 "세계관"으로 이해할 수 있게 만드는 최적의 구조 발견
- 이론보다는 실제 데이터가 보여주는 패턴 중심
- 사용자가 "이 관점"을 이해하는데 도움되는 구조
"""

import asyncio
import os
from supabase import create_client
from openai import AsyncOpenAI
import json
from collections import Counter, defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
import numpy as np
import re
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)
openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# ==============================================================================
# 데이터 로드
# ==============================================================================

def load_worldview_data():
    """독재와 사찰의 부활 데이터 로드"""
    wv = supabase.table('worldviews').select('*').limit(1).execute().data[0]
    perception_ids = wv['perception_ids']

    # 모든 perception 로드
    perceptions = supabase.table('layered_perceptions').select('*').in_('id', perception_ids).execute().data

    print(f"Loaded: {wv['title']}")
    print(f"Perceptions: {len(perceptions)}")

    return wv, perceptions


# ==============================================================================
# 실험 1: 통계적 패턴 분석 (What do they actually talk about?)
# ==============================================================================

def experiment1_statistical_patterns(perceptions):
    """실제로 무엇에 대해 이야기하는가?"""
    print("\n" + "="*80)
    print("실험 1: 통계적 패턴 분석")
    print("="*80)

    # 모든 텍스트 수집
    all_explicit = []
    all_implicit = []
    all_deep = []

    subjects = []
    predicates = []

    for lp in perceptions:
        if lp.get('explicit_claims'):
            for claim in lp['explicit_claims']:
                subjects.append(claim.get('subject', ''))
                predicates.append(claim.get('predicate', ''))
                all_explicit.append(f"{claim.get('subject', '')} {claim.get('predicate', '')}")

        if lp.get('implicit_assumptions'):
            all_implicit.extend(lp['implicit_assumptions'])

        if lp.get('deep_beliefs'):
            all_deep.extend(lp['deep_beliefs'])

    # 주체 분석
    subject_counter = Counter(subjects)
    print(f"\n📊 가장 많이 언급된 주체 (Top 15):")
    for subj, count in subject_counter.most_common(15):
        print(f"  {subj}: {count}회")

    # Deep beliefs 키워드 분석
    all_deep_text = ' '.join(all_deep)

    # 명사구 추출 (간단한 패턴)
    noun_phrases = re.findall(r'[가-힣]{2,}(?:은|는|이|가|을|를|의)', all_deep_text)
    noun_phrase_counter = Counter([p[:-1] for p in noun_phrases])

    print(f"\n🔑 Deep beliefs에서 자주 등장하는 개념:")
    for phrase, count in noun_phrase_counter.most_common(20):
        if len(phrase) > 1:
            print(f"  {phrase}: {count}회")

    # 서술어 패턴 (동사/형용사)
    verb_patterns = re.findall(r'[가-힣]{2,}(?:한다|하는|했다|될|되는|이다|있다)', all_deep_text)
    verb_counter = Counter(verb_patterns)

    print(f"\n⚡ 자주 나오는 서술 패턴:")
    for verb, count in verb_counter.most_common(15):
        print(f"  {verb}: {count}회")

    # 관계 패턴 (X는 Y하다)
    print(f"\n🔗 주요 관계 패턴 (샘플):")
    for belief in all_deep[:10]:
        # 간단한 구문 파싱
        match = re.match(r'([^은는이가]+)[은는이가]\s*(.+)', belief)
        if match:
            subject, predicate = match.groups()
            print(f"  [{subject}] → {predicate[:60]}...")

    return {
        'subjects': dict(subject_counter.most_common(20)),
        'key_concepts': dict(noun_phrase_counter.most_common(20)),
        'verb_patterns': dict(verb_counter.most_common(15)),
        'all_deep': all_deep,
        'all_implicit': all_implicit
    }


# ==============================================================================
# 실험 2: 토픽 모델링 (What are the underlying themes?)
# ==============================================================================

def experiment2_topic_modeling(perceptions):
    """잠재된 주제들은 무엇인가?"""
    print("\n" + "="*80)
    print("실험 2: 토픽 모델링 (LDA)")
    print("="*80)

    # Deep beliefs만 모으기
    docs = []
    for lp in perceptions:
        if lp.get('deep_beliefs'):
            docs.append(' '.join(lp['deep_beliefs']))

    # LDA
    vectorizer = CountVectorizer(max_features=100, min_df=2)
    doc_term_matrix = vectorizer.fit_transform(docs)

    lda = LatentDirichletAllocation(n_components=5, random_state=42)
    lda.fit(doc_term_matrix)

    feature_names = vectorizer.get_feature_names_out()

    print(f"\n발견된 5개 주제:")
    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        top_words_idx = topic.argsort()[-10:][::-1]
        top_words = [feature_names[i] for i in top_words_idx]
        print(f"\n주제 {topic_idx + 1}: {', '.join(top_words)}")
        topics.append(top_words)

    return {
        'topics': topics,
        'model': lda,
        'vectorizer': vectorizer
    }


# ==============================================================================
# 실험 3: 인과 관계 추출 (What causal chains do they believe?)
# ==============================================================================

def experiment3_causal_chains(perceptions):
    """어떤 인과 연쇄를 믿는가?"""
    print("\n" + "="*80)
    print("실험 3: 인과 관계 패턴 추출")
    print("="*80)

    # 인과 표현 패턴
    causal_patterns = [
        r'(.+?)(?:때문에|으로 인해|하여|해서)\s*(.+)',
        r'(.+?)\s*→\s*(.+)',
        r'(.+?)(?:하면|한다면)\s*(.+)',
    ]

    all_deep = []
    for lp in perceptions:
        if lp.get('deep_beliefs'):
            all_deep.extend(lp['deep_beliefs'])

    causal_chains = []
    for belief in all_deep:
        for pattern in causal_patterns:
            matches = re.findall(pattern, belief)
            if matches:
                causal_chains.extend(matches)

    print(f"\n발견된 인과 관계 패턴 (샘플 10개):")
    for cause, effect in causal_chains[:10]:
        print(f"  {cause.strip()[:40]} → {effect.strip()[:40]}")

    return causal_chains


# ==============================================================================
# 실험 4: GPT로 구조 추출 (다양한 프롬프트)
# ==============================================================================

async def experiment4_gpt_structuring(perceptions, stats_result):
    """GPT로 여러 방식의 구조 추출"""
    print("\n" + "="*80)
    print("실험 4: GPT 구조화 (5가지 프롬프트)")
    print("="*80)

    # 샘플 데이터 준비
    deep_beliefs_sample = []
    for lp in perceptions[:30]:  # 처음 30개만
        if lp.get('deep_beliefs'):
            deep_beliefs_sample.extend(lp['deep_beliefs'])

    # 통계 데이터
    top_subjects = list(stats_result['subjects'].keys())[:10]
    top_concepts = list(stats_result['key_concepts'].keys())[:10]

    results = {}

    # -------------------------------------------------------------------------
    # 프롬프트 1: "이 사람들은 세상을 어떻게 보는가?"
    # -------------------------------------------------------------------------
    print("\n🔬 프롬프트 1: 세계관의 본질")

    prompt1 = f"""다음은 같은 정치적 관점을 가진 사람들의 심층 믿음(deep beliefs) 샘플입니다:

{chr(10).join([f"- {b}" for b in deep_beliefs_sample[:20]])}

이 사람들은 **세상을 어떻게 보는가**를 JSON으로 설명하세요:

{{
  "core_lens": "이 관점의 핵심 렌즈 (1문장)",
  "what_they_see": "무엇에 주목하는가",
  "how_they_interpret": "어떻게 해석하는가",
  "what_they_fear": "무엇을 두려워하는가",
  "what_they_want": "무엇을 원하는가"
}}"""

    response1 = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt1}],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    results['prompt1'] = json.loads(response1.choices[0].message.content)
    print(json.dumps(results['prompt1'], indent=2, ensure_ascii=False))

    # -------------------------------------------------------------------------
    # 프롬프트 2: "핵심 주장과 그 근거"
    # -------------------------------------------------------------------------
    print("\n🔬 프롬프트 2: 주장의 구조")

    prompt2 = f"""같은 관점의 심층 믿음들:
{chr(10).join([f"- {b}" for b in deep_beliefs_sample[:20]])}

주요 언급 대상: {', '.join(top_subjects)}

이 관점의 **핵심 주장과 근거 구조**를 JSON으로:

{{
  "main_claim": "핵심 주장",
  "why_they_believe": ["믿는 이유 3-5개"],
  "evidence_they_use": ["어떤 사실을 증거로 보는가"],
  "logic_chain": "사고 흐름 (A → B → C)"
}}"""

    response2 = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt2}],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    results['prompt2'] = json.loads(response2.choices[0].message.content)
    print(json.dumps(results['prompt2'], indent=2, ensure_ascii=False))

    # -------------------------------------------------------------------------
    # 프롬프트 3: "이야기 구조"
    # -------------------------------------------------------------------------
    print("\n🔬 프롬프트 3: 서사 구조")

    prompt3 = f"""심층 믿음 샘플:
{chr(10).join([f"- {b}" for b in deep_beliefs_sample[:20]])}

이 관점이 **이야기하는 스토리**를 JSON으로:

{{
  "protagonist": "주인공 (누가 피해자인가)",
  "antagonist": "악당 (누가 가해자인가)",
  "conflict": "갈등 (무엇이 문제인가)",
  "plot": "줄거리 (무슨 일이 일어나고 있는가)",
  "ending": "결말 (어디로 향하는가)"
}}"""

    response3 = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt3}],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    results['prompt3'] = json.loads(response3.choices[0].message.content)
    print(json.dumps(results['prompt3'], indent=2, ensure_ascii=False))

    # -------------------------------------------------------------------------
    # 프롬프트 4: "패턴 인식"
    # -------------------------------------------------------------------------
    print("\n🔬 프롬프트 4: 반복 패턴")

    prompt4 = f"""심층 믿음들:
{chr(10).join([f"- {b}" for b in deep_beliefs_sample[:25]])}

**반복되는 패턴**을 JSON으로:

{{
  "recurring_themes": ["반복되는 주제 3-5개"],
  "typical_interpretation": "전형적인 해석 방식",
  "common_metaphors": ["자주 쓰는 비유"],
  "signature_moves": ["특징적인 사고 패턴"]
}}"""

    response4 = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt4}],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    results['prompt4'] = json.loads(response4.choices[0].message.content)
    print(json.dumps(results['prompt4'], indent=2, ensure_ascii=False))

    # -------------------------------------------------------------------------
    # 프롬프트 5: "차이점 - 같은 사건을 어떻게 다르게 보는가"
    # -------------------------------------------------------------------------
    print("\n🔬 프롬프트 5: 해석 차이")

    prompt5 = f"""이 관점의 심층 믿음:
{chr(10).join([f"- {b}" for b in deep_beliefs_sample[:20]])}

**같은 사건을 어떻게 다르게 해석하는가** JSON으로:

{{
  "interpretation_examples": [
    {{
      "event": "사건/상황",
      "normal_view": "일반적으로 보는 방식",
      "this_view": "이 관점에서 보는 방식",
      "key_difference": "핵심 차이"
    }}
  ]
}}

최소 3개 예시를 만드세요."""

    response5 = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt5}],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    results['prompt5'] = json.loads(response5.choices[0].message.content)
    print(json.dumps(results['prompt5'], indent=2, ensure_ascii=False))

    return results


# ==============================================================================
# 실험 5: 구조 조합 실험
# ==============================================================================

async def experiment5_combined_structure(perceptions, all_results):
    """여러 실험 결과를 종합한 최적 구조"""
    print("\n" + "="*80)
    print("실험 5: 종합 구조 생성")
    print("="*80)

    # 모든 실험 결과를 GPT에게 주고 최적 구조 생성
    summary = f"""다음은 "독재와 사찰의 부활" 세계관에 대한 여러 분석 결과입니다:

**통계 분석:**
- 주요 주체: {list(all_results['stats']['subjects'].keys())[:10]}
- 핵심 개념: {list(all_results['stats']['key_concepts'].keys())[:10]}

**GPT 분석 결과:**

세계관의 본질: {json.dumps(all_results['gpt']['prompt1'], ensure_ascii=False)}

주장의 구조: {json.dumps(all_results['gpt']['prompt2'], ensure_ascii=False)}

서사 구조: {json.dumps(all_results['gpt']['prompt3'], ensure_ascii=False)}

반복 패턴: {json.dumps(all_results['gpt']['prompt4'], ensure_ascii=False)}

해석 차이: {json.dumps(all_results['gpt']['prompt5'], ensure_ascii=False)}

이 모든 정보를 종합해서, 사용자가 "이 세계관(관점)"을 이해하는데 가장 도움이 되는 구조를 만드세요.

JSON 형식으로, 다음 기준을 고려하세요:
1. **직관적**: 5분 안에 이해 가능
2. **구체적**: 추상적 개념보다 실제 예시
3. **차별적**: 다른 관점과 어떻게 다른지 명확
4. **행동 지향적**: 왜 이렇게 생각하고, 뭘 하려는지

자유롭게 구조를 설계하세요. 이론에 얽매이지 말고 "이해"에 최적화하세요."""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",  # 더 강력한 모델 사용
        messages=[
            {
                "role": "system",
                "content": "당신은 복잡한 세계관을 사용자가 이해하기 쉬운 구조로 만드는 전문가입니다."
            },
            {"role": "user", "content": summary}
        ],
        response_format={"type": "json_object"},
        temperature=0.4
    )

    final_structure = json.loads(response.choices[0].message.content)

    print("\n" + "="*80)
    print("🎯 최종 제안 구조:")
    print("="*80)
    print(json.dumps(final_structure, indent=2, ensure_ascii=False))

    return final_structure


# ==============================================================================
# 메인 실행
# ==============================================================================

async def main():
    print("="*80)
    print("세계관 구조 연구: 실제 데이터 기반")
    print("="*80)

    # 데이터 로드
    worldview, perceptions = load_worldview_data()

    results = {}

    # 실험 1: 통계
    results['stats'] = experiment1_statistical_patterns(perceptions)

    # 실험 2: 토픽 모델링
    results['topics'] = experiment2_topic_modeling(perceptions)

    # 실험 3: 인과 관계
    results['causal'] = experiment3_causal_chains(perceptions)

    # 실험 4: GPT 구조화
    results['gpt'] = await experiment4_gpt_structuring(perceptions, results['stats'])

    # 실험 5: 종합
    results['final'] = await experiment5_combined_structure(perceptions, results)

    # 결과 저장
    with open('worldview_structure_research_results.json', 'w', encoding='utf-8') as f:
        # causal_chains는 tuple이라 JSON 직렬화 불가, 제외
        save_results = {
            'stats': results['stats'],
            'gpt': results['gpt'],
            'final': results['final']
        }
        json.dump(save_results, f, ensure_ascii=False, indent=2)

    print("\n" + "="*80)
    print("✅ 연구 완료! 결과: worldview_structure_research_results.json")
    print("="*80)

    return results


if __name__ == "__main__":
    asyncio.run(main())
