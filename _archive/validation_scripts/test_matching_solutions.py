"""
3가지 매칭 솔루션 시뮬레이션

실제 데이터 샘플로 각 방법의 효과를 검증
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import json
import asyncio
from openai import AsyncOpenAI

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# ============================================================================
# 방법 1: 현재 방식 (키워드 기반 단순 매칭)
# ============================================================================
def method1_keyword_matching(perception_text, worldviews):
    """현재 사용 중인 키워드 기반 매칭"""
    best_match = None
    best_score = 0

    for wv in worldviews:
        frame = json.loads(wv['frame'])
        keywords = frame['metadata'].get('key_concepts', [])

        score = sum(1 for kw in keywords if kw in perception_text)

        if score > best_score:
            best_score = score
            best_match = wv['id']

    return best_match, best_score


# ============================================================================
# 방법 2: 임베딩 기반 시맨틱 서치 (OpenAI text-embedding-3-small)
# ============================================================================
async def method2_embedding_matching(perception_text, worldviews):
    """벡터 임베딩 기반 코사인 유사도 매칭"""

    # Perception 임베딩
    p_response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=perception_text
    )
    p_embedding = p_response.data[0].embedding

    # 각 세계관과 유사도 계산
    best_match = None
    best_similarity = -1

    for wv in worldviews:
        # 세계관 임베딩 (캐시되어 있다고 가정, 실제로는 DB에서 로드)
        if wv.get('worldview_embedding'):
            wv_embedding = wv['worldview_embedding']
        else:
            # 세계관 텍스트 생성
            frame = json.loads(wv['frame'])
            wv_text = f"{wv['title']} {frame['narrative']['summary']} {' '.join(frame['metadata']['key_concepts'])}"

            wv_response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=wv_text
            )
            wv_embedding = wv_response.data[0].embedding

        # 코사인 유사도
        similarity = sum(a*b for a, b in zip(p_embedding, wv_embedding))

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = wv['id']

    return best_match, best_similarity


# ============================================================================
# 방법 3: GPT-5 직접 판단 (Few-shot learning)
# ============================================================================
async def method3_gpt5_direct_matching(perception_text, perception_deep_beliefs, worldviews):
    """GPT-5가 직접 가장 적합한 세계관을 선택"""

    # 세계관 목록 생성
    wv_list = []
    for i, wv in enumerate(worldviews):
        frame = json.loads(wv['frame'])
        wv_list.append({
            'index': i,
            'title': wv['title'],
            'summary': frame['narrative']['summary']
        })

    prompt = f"""다음 perception을 가장 잘 설명하는 세계관을 선택하세요.

**Perception:**
심층 믿음: {perception_deep_beliefs}
전체 텍스트: {perception_text[:300]}

**세계관 목록:**
{json.dumps(wv_list, ensure_ascii=False, indent=2)}

가장 적합한 세계관의 index를 JSON 형식으로 반환하세요:
{{"best_match_index": 0, "confidence": 0.95, "reason": "이유"}}
"""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",  # 빠른 테스트용
        messages=[
            {"role": "system", "content": "You are an expert at matching perceptions to worldviews. Always respond in valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    best_match = worldviews[result['best_match_index']]['id']
    confidence = result['confidence']

    return best_match, confidence


# ============================================================================
# 시뮬레이션: 10개 샘플 perception으로 3가지 방법 비교
# ============================================================================
async def run_simulation():
    print("="*80)
    print("3가지 매칭 방법 시뮬레이션")
    print("="*80)

    # 테스트 데이터: 미매칭 + 부적절 매칭 perception
    perceptions = supabase.table('layered_perceptions').select('*').limit(10).execute().data
    worldviews = supabase.table('worldviews').select('*').execute().data

    # 계층적 세계관만 필터
    hierarchical_wvs = [wv for wv in worldviews if '>' in wv['title']]

    results = {
        'method1': [],
        'method2': [],
        'method3': []
    }

    for i, p in enumerate(perceptions, 1):
        print(f"\n{'='*80}")
        print(f"테스트 케이스 {i}/10")
        print(f"{'='*80}")

        # Perception 텍스트
        deep_beliefs = p['deep_beliefs'][0] if p['deep_beliefs'] else ""
        full_text = ' '.join(p.get('deep_beliefs', []) + p.get('implicit_assumptions', []))

        print(f"심층 믿음: {deep_beliefs[:100]}...")

        # 방법 1: 키워드 매칭
        match1, score1 = method1_keyword_matching(full_text, hierarchical_wvs)
        wv1_title = next((wv['title'] for wv in hierarchical_wvs if wv['id'] == match1), "매칭 실패")
        print(f"\n방법1 (키워드): {wv1_title} (점수: {score1})")
        results['method1'].append(match1 if score1 > 0 else None)

        # 방법 2: 임베딩 매칭
        try:
            match2, score2 = await method2_embedding_matching(full_text, hierarchical_wvs)
            wv2_title = next((wv['title'] for wv in hierarchical_wvs if wv['id'] == match2), "매칭 실패")
            print(f"방법2 (임베딩): {wv2_title} (유사도: {score2:.3f})")
            results['method2'].append(match2)
        except Exception as e:
            print(f"방법2 에러: {e}")
            results['method2'].append(None)

        # 방법 3: GPT-5 직접 판단
        try:
            match3, conf3 = await method3_gpt5_direct_matching(full_text, deep_beliefs, hierarchical_wvs)
            wv3_title = next((wv['title'] for wv in hierarchical_wvs if wv['id'] == match3), "매칭 실패")
            print(f"방법3 (GPT-5):  {wv3_title} (신뢰도: {conf3:.2f})")
            results['method3'].append(match3)
        except Exception as e:
            print(f"방법3 에러: {e}")
            results['method3'].append(None)

    # 결과 비교
    print(f"\n{'='*80}")
    print("결과 비교")
    print(f"{'='*80}")

    method1_success = sum(1 for m in results['method1'] if m is not None)
    method2_success = sum(1 for m in results['method2'] if m is not None)
    method3_success = sum(1 for m in results['method3'] if m is not None)

    print(f"\n방법1 (키워드):  {method1_success}/10 매칭 성공 ({method1_success*10}%)")
    print(f"방법2 (임베딩):  {method2_success}/10 매칭 성공 ({method2_success*10}%)")
    print(f"방법3 (GPT-5):   {method3_success}/10 매칭 성공 ({method3_success*10}%)")

    # 일치도 분석
    agreement_12 = sum(1 for m1, m2 in zip(results['method1'], results['method2']) if m1 == m2 and m1 is not None)
    agreement_13 = sum(1 for m1, m3 in zip(results['method1'], results['method3']) if m1 == m3 and m1 is not None)
    agreement_23 = sum(1 for m2, m3 in zip(results['method2'], results['method3']) if m2 == m3 and m2 is not None)

    print(f"\n방법1-2 일치: {agreement_12}/10")
    print(f"방법1-3 일치: {agreement_13}/10")
    print(f"방법2-3 일치: {agreement_23}/10")


if __name__ == "__main__":
    asyncio.run(run_simulation())
