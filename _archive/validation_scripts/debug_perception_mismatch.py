"""
Perception ID 불일치 문제 디버깅
"""

import os
from supabase import create_client
import json
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

print("=" * 100)
print("Perception ID 불일치 문제 디버깅")
print("=" * 100)

# 데이터 로드
perceptions = supabase.table("perceptions").select("*").execute().data
worldviews = supabase.table("worldviews").select("*").execute().data

print(f"\n총 Perception: {len(perceptions)}개")
print(f"총 Worldview: {len(worldviews)}개")

# 실제 perception ID들
actual_perception_ids = set([p['id'] for p in perceptions])
print(f"\n실제 Perception ID 샘플 (처음 5개):")
for pid in list(actual_perception_ids)[:5]:
    print(f"  {pid}")

# Worldview의 perception_ids 확인
wv = worldviews[0]  # "독재와 사찰의 부활"
print(f"\n\nWorldview: {wv['title']}")
print(f"perception_ids 필드 타입: {type(wv.get('perception_ids'))}")
print(f"perception_ids 개수: {len(wv.get('perception_ids', []))}")

worldview_perception_ids = wv.get('perception_ids', [])
print(f"\nWorldview의 Perception ID 샘플 (처음 5개):")
for pid in worldview_perception_ids[:5]:
    print(f"  {pid} (타입: {type(pid)})")

# 매칭 확인
matches = 0
for pid in worldview_perception_ids[:10]:
    if pid in actual_perception_ids:
        matches += 1
        print(f"  ✓ {pid} - 매칭됨")
    else:
        print(f"  ✗ {pid} - 매칭 안됨")

print(f"\n\n매칭 통계:")
print(f"  Worldview perception_ids: {len(worldview_perception_ids)}개")
print(f"  실제 Perception IDs: {len(actual_perception_ids)}개")
print(f"  매칭된 개수 (샘플 10개 중): {matches}개")

# 전체 매칭 확인
total_matches = len(set(worldview_perception_ids) & actual_perception_ids)
print(f"  전체 매칭: {total_matches}개 / {len(worldview_perception_ids)}개")

# 역방향 확인: 실제 perception들이 어디에 속하는가?
print(f"\n\n역방향 확인: 실제 88개 perception은 어디에 속하는가?")

perception_in_worldviews = 0
for p in perceptions[:10]:
    pid = p['id']
    found_in = []
    for wv in worldviews:
        if pid in wv.get('perception_ids', []):
            found_in.append(wv['title'])

    if found_in:
        perception_in_worldviews += 1
        print(f"  ✓ Perception {pid[:8]}... → {found_in}")
    else:
        print(f"  ✗ Perception {pid[:8]}... → 세계관 없음")
        print(f"     Subject: {p['perceived_subject']}, Attribute: {p['perceived_attribute']}")

# 전체 통계
total_in_worldviews = 0
for p in perceptions:
    pid = p['id']
    for wv in worldviews:
        if pid in wv.get('perception_ids', []):
            total_in_worldviews += 1
            break

print(f"\n전체 통계:")
print(f"  88개 perception 중 {total_in_worldviews}개가 worldview에 속함")
print(f"  {len(perceptions) - total_in_worldviews}개가 orphan")

# 결론
print(f"\n\n" + "=" * 100)
print("결론")
print("=" * 100)

if total_matches == 0:
    print("\n❌ Worldview의 perception_ids와 실제 Perception IDs가 전혀 매칭되지 않음")
    print("\n가능한 원인:")
    print("  1. Worldview가 생성된 시점과 현재 Perception이 다름 (DB 재생성?)")
    print("  2. Perception ID가 변경됨")
    print("  3. Worldview의 perception_ids가 오래된 데이터를 참조")

    print("\n해결 방안:")
    print("  1. OptimalWorldviewConstructor를 다시 실행해서 worldview 재생성")
    print("  2. 현재 88개 perception으로 새로운 worldview 구성")
    print("  3. Worldview의 perception_ids를 현재 perception에 맞게 업데이트")
else:
    print(f"\n✓ {total_matches}개 매칭됨")
    print(f"  매칭 비율: {total_matches/len(worldview_perception_ids)*100:.1f}%")
