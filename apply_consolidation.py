"""
Worldview 통합 적용 스크립트

Strategy 4 (하이브리드) 결과를 데이터베이스에 적용:
- 24개 worldview → 9개 통합
- perception-worldview 링크 재매핑
- 사용자 친화적 명칭 적용
"""

import os
from supabase import create_client
import json
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# Strategy 4 결과 로드
with open('consolidation_strategies_result.json', 'r', encoding='utf-8') as f:
    strategies = json.load(f)

strategy4 = strategies['strategy4_hybrid']['final_worldviews']

print("=" * 80)
print("Worldview 통합 적용")
print("=" * 80)

# 현재 worldview와 링크 정보
current_worldviews = supabase.table('worldviews').select('*').execute().data
current_links = supabase.table('perception_worldview_links').select('*').execute().data

print(f"\n현재 상태:")
print(f"- Worldviews: {len(current_worldviews)}개")
print(f"- Links: {len(current_links)}개")

# 새로운 worldview 생성 및 매핑
print(f"\n새로운 통합 worldview 생성: {len(strategy4)}개")

new_worldview_mapping = {}  # old_id -> new_id

for i, new_wv in enumerate(strategy4, 1):
    print(f"\n{i}. {new_wv['name']} ({new_wv['priority'].upper()})")
    print(f"   설명: {new_wv['description']}")
    print(f"   통합: {len(new_wv['merged_ids'])}개 worldview")
    print(f"   예상: {new_wv['estimated_count']}개 perception")

    # 새 worldview 생성
    new_frame = {
        "category": "통합된 공격 유형",
        "subcategory": new_wv['name'],
        "description": new_wv['description'],
        "priority": new_wv['priority'],
        "metadata": {
            "merged_from": new_wv['merged_ids'],
            "estimated_count": new_wv['estimated_count']
        }
    }

    # DB에 삽입
    result = supabase.table('worldviews').insert({
        'title': new_wv['name'],
        'frame': json.dumps(new_frame, ensure_ascii=False),
        'description': new_wv['description'],
        'core_subject': '정치적 담론',  # 기본값
        'core_attributes': [],  # 기본값
        'overall_valence': 'negative',  # 기본값 (공격 유형이므로)
        'total_perceptions': 0,  # 링크 재매핑 후 업데이트
        'perception_ids': []
    }).execute()

    new_wv_id = result.data[0]['id']
    print(f"   새 ID: {new_wv_id}")

    # 매핑 저장
    for old_id in new_wv['merged_ids']:
        new_worldview_mapping[old_id] = new_wv_id

print(f"\n총 {len(new_worldview_mapping)}개 worldview 매핑 완료")

# Perception-Worldview 링크 재매핑
print("\n" + "=" * 80)
print("Perception-Worldview 링크 재매핑")
print("=" * 80)

# 기존 링크를 새 worldview로 재매핑
new_links_dict = {}  # (perception_id, new_worldview_id) -> relevance_score

for link in current_links:
    old_wv_id = link['worldview_id']
    perception_id = link['perception_id']
    relevance_score = link.get('relevance_score', 0.5)

    if old_wv_id in new_worldview_mapping:
        new_wv_id = new_worldview_mapping[old_wv_id]
        key = (perception_id, new_wv_id)

        # 같은 perception이 여러 old worldview를 통해 같은 new worldview로 매핑되면
        # 가장 높은 relevance_score 유지
        if key not in new_links_dict or new_links_dict[key] < relevance_score:
            new_links_dict[key] = relevance_score

print(f"\n기존 링크: {len(current_links)}개")
print(f"재매핑된 링크: {len(new_links_dict)}개")
print(f"중복 제거: {len(current_links) - len(new_links_dict)}개")

# 기존 링크 삭제
print("\n기존 링크 삭제 중...")
supabase.table('perception_worldview_links').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()

# 새 링크 삽입
print("새 링크 삽입 중...")
new_links = [
    {
        'perception_id': perception_id,
        'worldview_id': worldview_id,
        'relevance_score': score
    }
    for (perception_id, worldview_id), score in new_links_dict.items()
]

# 배치 삽입 (100개씩)
batch_size = 100
for i in range(0, len(new_links), batch_size):
    batch = new_links[i:i+batch_size]
    supabase.table('perception_worldview_links').insert(batch).execute()
    print(f"  진행: {min(i+batch_size, len(new_links))}/{len(new_links)}")

# Worldview별 perception 개수 업데이트
print("\n" + "=" * 80)
print("Worldview별 perception 개수 업데이트")
print("=" * 80)

from collections import defaultdict

perception_counts = defaultdict(list)

for (perception_id, worldview_id), _ in new_links_dict.items():
    perception_counts[worldview_id].append(perception_id)

for worldview_id, perception_ids in perception_counts.items():
    count = len(perception_ids)
    supabase.table('worldviews').update({
        'total_perceptions': count,
        'perception_ids': perception_ids
    }).eq('id', worldview_id).execute()

    # worldview 이름 확인
    wv = supabase.table('worldviews').select('frame').eq('id', worldview_id).execute()
    if wv.data:
        frame = json.loads(wv.data[0]['frame'])
        print(f"✓ {frame['subcategory']}: {count}개 perception")

# 기존 worldview 삭제
print("\n" + "=" * 80)
print("기존 worldview 삭제")
print("=" * 80)

print(f"\n삭제할 worldview: {len(current_worldviews)}개")

for old_wv in current_worldviews:
    supabase.table('worldviews').delete().eq('id', old_wv['id']).execute()

print("✓ 기존 worldview 삭제 완료")

# 최종 상태 확인
print("\n" + "=" * 80)
print("최종 상태")
print("=" * 80)

final_worldviews = supabase.table('worldviews').select('*').order('total_perceptions', desc=True).execute().data
final_links = supabase.table('perception_worldview_links').select('id', count='exact').execute()

print(f"\n✓ Worldviews: {len(final_worldviews)}개 (24개 → {len(final_worldviews)}개)")
print(f"✓ Links: {final_links.count}개 (487개 → {final_links.count}개)")

print("\n최종 worldview 목록 (perception 개수 순):")
for i, wv in enumerate(final_worldviews, 1):
    frame = json.loads(wv['frame'])
    print(f"{i}. [{frame['priority'].upper():6s}] {frame['subcategory']}: {wv['total_perceptions']}개")

print("\n" + "=" * 80)
print("✓ 통합 완료!")
print("=" * 80)

print("""
다음 단계:
1. 대시보드에서 새로운 worldview 확인
2. 사용자 테스트
3. 필요시 명칭 조정
""")
