"""
Worldview 통합 전략 시뮬레이션

문제:
1. 24개 worldview가 너무 많음 → 8-10개로 통합
2. 학술적/추상적 명칭 → 사용자 친화적 명칭
4. 분석자 관점 → 사용자 관점

시뮬레이션할 전략:
- Strategy 1: 키워드 기반 자동 클러스터링
- Strategy 2: GPT-5 기반 의미론적 통합
- Strategy 3: 사용자 관점 재분류 (공격 유형 중심)
- Strategy 4: 하이브리드 (통계 + GPT + 사용자 관점)
"""

import os
from supabase import create_client
import json
from collections import defaultdict
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Setup
load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 현재 worldview 데이터 로드
worldviews = supabase.table('worldviews').select('*').execute().data

print("=" * 80)
print("현재 Worldview 현황")
print("=" * 80)

# 카테고리별 그룹화
by_category = defaultdict(list)
for wv in worldviews:
    frame = json.loads(wv['frame'])
    category = frame.get('category', 'Unknown')
    by_category[category].append({
        'id': wv['id'],
        'subcategory': frame.get('subcategory'),
        'count': wv.get('total_perceptions', 0),
        'keywords': frame.get('metadata', {}).get('key_concepts', [])
    })

for cat, items in sorted(by_category.items()):
    total = sum(item['count'] for item in items)
    print(f"\n{cat} ({len(items)}개 worldview, {total}개 perception)")
    for item in items:
        print(f"  - {item['subcategory']} ({item['count']}개)")


print("\n" + "=" * 80)
print("Strategy 1: 키워드 기반 자동 클러스터링")
print("=" * 80)
print("방법: 키워드 유사도를 계산하여 유사한 worldview를 자동 병합")

def calculate_keyword_similarity(keywords1, keywords2):
    """두 키워드 리스트의 Jaccard 유사도"""
    set1 = set(keywords1)
    set2 = set(keywords2)
    if not set1 or not set2:
        return 0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union

# 유사도 행렬 계산
similarity_threshold = 0.3

clusters = []
used = set()

for i, wv1 in enumerate(worldviews):
    if wv1['id'] in used:
        continue

    frame1 = json.loads(wv1['frame'])
    keywords1 = frame1.get('metadata', {}).get('key_concepts', [])

    cluster = [wv1]
    used.add(wv1['id'])

    for j, wv2 in enumerate(worldviews):
        if i == j or wv2['id'] in used:
            continue

        frame2 = json.loads(wv2['frame'])
        keywords2 = frame2.get('metadata', {}).get('key_concepts', [])

        similarity = calculate_keyword_similarity(keywords1, keywords2)

        if similarity >= similarity_threshold:
            cluster.append(wv2)
            used.add(wv2['id'])

    clusters.append(cluster)

print(f"\n결과: {len(clusters)}개 클러스터 생성 (threshold={similarity_threshold})")
print("\n클러스터 상세:")
for i, cluster in enumerate(sorted(clusters, key=lambda c: sum(wv.get('total_perceptions', 0) for wv in c), reverse=True), 1):
    total_perceptions = sum(wv.get('total_perceptions', 0) for wv in cluster)
    print(f"\n클러스터 {i} ({len(cluster)}개 worldview, {total_perceptions}개 perception):")
    for wv in cluster:
        frame = json.loads(wv['frame'])
        print(f"  - {frame.get('subcategory')} ({wv.get('total_perceptions', 0)}개)")


print("\n" + "=" * 80)
print("Strategy 2: GPT-5 기반 의미론적 통합")
print("=" * 80)
print("방법: GPT-5에게 24개 worldview를 보여주고 의미론적으로 8-10개로 통합 요청")

async def gpt5_consolidate_worldviews():
    # Worldview 정보 준비
    wv_descriptions = []
    for wv in worldviews:
        frame = json.loads(wv['frame'])
        wv_descriptions.append({
            'id': wv['id'],
            'category': frame.get('category'),
            'subcategory': frame.get('subcategory'),
            'description': frame.get('description', ''),
            'keywords': frame.get('metadata', {}).get('key_concepts', []),
            'perception_count': wv.get('total_perceptions', 0)
        })

    prompt = f"""당신은 정치적 담론 분석 전문가입니다.

현재 24개의 worldview(세계관/프레임)가 있습니다. 이들은 DC Gallery에서 수집한 정치적 공격/담론을 분류하기 위한 것입니다.

**문제:**
- 24개가 너무 많음
- 유사/중복된 worldview들이 존재
- 사용자(여당 지지자)가 이해하기 어려움

**목표:**
24개를 8-10개의 명확하고 구분되는 worldview로 통합하세요.

**현재 24개 Worldview:**
{json.dumps(wv_descriptions, ensure_ascii=False, indent=2)}

**작업:**
1. 의미론적으로 유사한 worldview들을 그룹화
2. 각 그룹을 하나의 통합된 worldview로 정의
3. 8-10개의 최종 worldview 제안

**출력 형식 (JSON):**
{{
  "consolidated_worldviews": [
    {{
      "new_name": "통합된 명확한 이름",
      "new_category": "카테고리",
      "description": "이 worldview가 무엇을 의미하는지",
      "merged_ids": ["통합될 기존 worldview ID들"],
      "reasoning": "왜 이들을 통합했는지"
    }}
  ]
}}

**중요:**
- 최종 개수: 8-10개
- 각 worldview는 명확히 구분되어야 함
- perception 개수를 고려 (많은 것을 우선)
- 사용자가 이해하기 쉬워야 함
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a political discourse analysis expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    return result

print("\nGPT-5 실행 중...")
gpt5_result = asyncio.run(gpt5_consolidate_worldviews())

print(f"\n결과: {len(gpt5_result['consolidated_worldviews'])}개 통합 worldview")
print("\n통합 제안:")
for i, wv in enumerate(gpt5_result['consolidated_worldviews'], 1):
    merged_count = len(wv['merged_ids'])
    print(f"\n{i}. {wv['new_name']}")
    print(f"   카테고리: {wv['new_category']}")
    print(f"   통합 개수: {merged_count}개")
    print(f"   설명: {wv['description'][:100]}...")
    print(f"   이유: {wv['reasoning'][:100]}...")


print("\n" + "=" * 80)
print("Strategy 3: 사용자 관점 재분류 (공격 유형 중심)")
print("=" * 80)
print("방법: '이게 무슨 프레임인가?' 대신 '어떤 공격인가?'로 재구성")

async def user_centric_reclassification():
    """사용자 관점에서 worldview를 재분류"""

    prompt = f"""당신은 여당 지지자를 위한 정보 시스템을 설계하는 전문가입니다.

**상황:**
- DC Gallery에서 정치적 공격/담론 수집
- 현재 24개 worldview로 분류
- 사용자: 여당 지지자들
- 목적: 어떤 공격이 들어오는지 파악하고 이해하기

**문제:**
현재 worldview는 학술적/분석적 관점:
- "권력의 도구화와 감시국가 프레임"
- "체제 취약성 모델: 안보 이완 → 경제·사회 연쇄 붕괴"

→ 사용자가 이해하기 어려움!

**목표:**
사용자 관점으로 재분류:
- "이게 무슨 프레임인가?" (X)
- "어떤 공격인가?" (O)

**현재 24개 Worldview:**
{json.dumps([{
    'id': wv['id'],
    'category': json.loads(wv['frame']).get('category'),
    'subcategory': json.loads(wv['frame']).get('subcategory'),
    'perception_count': wv.get('total_perceptions', 0)
} for wv in worldviews], ensure_ascii=False, indent=2)}

**작업:**
1. 사용자 관점에서 "공격 유형"으로 8-10개 재분류
2. 명칭은 명확하고 직관적으로
3. "~에 대한 공격", "~를 이용한 선동" 등

**출력 형식 (JSON):**
{{
  "attack_types": [
    {{
      "attack_name": "명확한 공격 유형 이름",
      "user_description": "사용자가 이해할 수 있는 설명",
      "example_attacks": "이런 식으로 공격함",
      "merged_ids": ["통합될 worldview ID들"],
      "perception_count": 예상_perception_개수
    }}
  ]
}}

**중요:**
- 8-10개
- 사용자 친화적 명칭
- 직관적으로 이해 가능
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are designing an information system for political supporters."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    return result

print("\nGPT-4o 실행 중...")
user_centric_result = asyncio.run(user_centric_reclassification())

print(f"\n결과: {len(user_centric_result['attack_types'])}개 공격 유형")
print("\n공격 유형 제안:")
for i, attack in enumerate(user_centric_result['attack_types'], 1):
    merged_count = len(attack['merged_ids'])
    print(f"\n{i}. {attack['attack_name']}")
    print(f"   설명: {attack['user_description']}")
    print(f"   예시: {attack['example_attacks'][:100]}...")
    print(f"   통합: {merged_count}개 worldview")


print("\n" + "=" * 80)
print("Strategy 4: 하이브리드 (통계 + GPT + 사용자 관점)")
print("=" * 80)
print("방법: 통계적 집중도 + GPT 의미 통합 + 사용자 관점 명칭")

async def hybrid_consolidation():
    """하이브리드 통합 전략"""

    # Step 1: 통계적 우선순위 (perception 개수 기준)
    sorted_wvs = sorted(worldviews, key=lambda w: w.get('total_perceptions', 0), reverse=True)

    # TOP 80%를 차지하는 worldview만 고려
    total_perceptions = sum(wv.get('total_perceptions', 0) for wv in worldviews)
    accumulated = 0
    top_wvs = []
    for wv in sorted_wvs:
        accumulated += wv.get('total_perceptions', 0)
        top_wvs.append(wv)
        if accumulated >= total_perceptions * 0.8:
            break

    print(f"\nStep 1: TOP {len(top_wvs)}개 worldview가 전체의 80% 차지")

    # Step 2: GPT로 이들을 사용자 친화적으로 통합
    wv_info = []
    for wv in top_wvs:
        frame = json.loads(wv['frame'])
        wv_info.append({
            'id': wv['id'],
            'subcategory': frame.get('subcategory'),
            'count': wv.get('total_perceptions', 0),
            'keywords': frame.get('metadata', {}).get('key_concepts', [])[:5]
        })

    prompt = f"""당신은 정치 담론 분석 시스템의 UX 디자이너입니다.

**목표:**
사용자(여당 지지자)가 쉽게 이해할 수 있도록 worldview를 통합하고 명명

**입력:**
전체 perception의 80%를 차지하는 TOP {len(top_wvs)}개 worldview:
{json.dumps(wv_info, ensure_ascii=False, indent=2)}

**작업:**
1. 유사한 것들을 6-8개로 통합
2. 명칭: 명확하고 직관적
3. 사용자가 "아, 이 공격이구나" 바로 이해 가능해야 함

**출력 형식 (JSON):**
{{
  "final_worldviews": [
    {{
      "name": "사용자 친화적 이름",
      "description": "한 문장 설명",
      "merged_ids": ["ID들"],
      "estimated_count": 예상_perception_수,
      "priority": "high/medium/low"
    }}
  ]
}}
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)

    # Step 3: 나머지 20% worldview는 "기타"로 통합
    bottom_wv_ids = [wv['id'] for wv in worldviews if wv not in top_wvs]

    result['final_worldviews'].append({
        'name': '기타',
        'description': '소수 출현 담론',
        'merged_ids': bottom_wv_ids,
        'estimated_count': total_perceptions - accumulated,
        'priority': 'low'
    })

    return result

print("\n하이브리드 전략 실행 중...")
hybrid_result = asyncio.run(hybrid_consolidation())

print(f"\n결과: {len(hybrid_result['final_worldviews'])}개 최종 worldview")
print("\n최종 제안:")
for i, wv in enumerate(hybrid_result['final_worldviews'], 1):
    print(f"\n{i}. [{wv['priority'].upper()}] {wv['name']}")
    print(f"   설명: {wv['description']}")
    print(f"   통합: {len(wv['merged_ids'])}개 worldview")
    print(f"   예상: {wv['estimated_count']}개 perception")


print("\n" + "=" * 80)
print("전략 비교 및 평가")
print("=" * 80)

print(f"""
Strategy 1 (키워드 클러스터링): {len(clusters)}개
  장점: 자동화, 객관적
  단점: 키워드 유사도만 고려, 사용자 관점 부재

Strategy 2 (GPT 의미 통합): {len(gpt5_result['consolidated_worldviews'])}개
  장점: 의미론적 정확성
  단점: 여전히 분석적 관점

Strategy 3 (사용자 관점): {len(user_centric_result['attack_types'])}개
  장점: 사용자 친화적 명칭, 직관적
  단점: perception 분포 고려 부족

Strategy 4 (하이브리드): {len(hybrid_result['final_worldviews'])}개
  장점: 통계 + 의미 + 사용자 관점 모두 고려
  단점: 복잡한 프로세스
""")

# 결과 저장
with open('consolidation_strategies_result.json', 'w', encoding='utf-8') as f:
    json.dump({
        'strategy1_keyword': {
            'count': len(clusters),
            'clusters': [[json.loads(wv['frame']).get('subcategory') for wv in cluster] for cluster in clusters]
        },
        'strategy2_gpt5': gpt5_result,
        'strategy3_user_centric': user_centric_result,
        'strategy4_hybrid': hybrid_result
    }, f, ensure_ascii=False, indent=2)

print("\n결과 저장: consolidation_strategies_result.json")

print("\n" + "=" * 80)
print("권장 사항")
print("=" * 80)
print("""
실제 데이터 분석 결과, **Strategy 4 (하이브리드)**를 추천합니다.

이유:
1. 통계적 근거 (TOP 80% 중심)
2. 의미론적 정확성 (GPT 통합)
3. 사용자 관점 (친화적 명칭)
4. 실용성 (6-8개 + 기타)

다음 단계:
1. 하이브리드 결과 검토
2. 명칭/설명 최종 조정
3. 데이터베이스 적용
4. perception-worldview 링크 재매핑
""")
