"""
Worldview category 수정 스크립트

"통합된 공격 유형" → 적절한 카테고리로 분류
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

# 카테고리 매핑
category_mapping = {
    "독재와 사찰의 부활": "정치 권력과 민주주의",
    "표현의 자유 억압": "정치 권력과 민주주의",
    "정치보복과 인권 침해": "정치 권력과 민주주의",

    "이민 정책과 범죄 증가": "외부 위협과 국가 안보",
    "온라인 여론 조작": "외부 위협과 국가 안보",
    "중국 산업 불신": "외부 위협과 국가 안보",
    "체제 취약성과 안보 위기": "외부 위협과 국가 안보",

    "복지·보건 카르텔 해체": "사회 제도와 정책",

    "기타": "기타"
}

print("=" * 80)
print("Worldview Category 업데이트")
print("=" * 80)

# 모든 worldviews 가져오기
worldviews = supabase.table('worldviews').select('*').execute().data

print(f"\n총 {len(worldviews)}개 worldview")

updated_count = 0

for wv in worldviews:
    title = wv['title']
    frame = json.loads(wv['frame'])

    old_category = frame.get('category')

    if title in category_mapping:
        new_category = category_mapping[title]
        frame['category'] = new_category

        # frame JSON 업데이트
        supabase.table('worldviews').update({
            'frame': json.dumps(frame, ensure_ascii=False)
        }).eq('id', wv['id']).execute()

        print(f"✓ {title}")
        print(f"  {old_category} → {new_category}")

        updated_count += 1
    else:
        print(f"⚠ {title} - 매핑 없음")

print(f"\n{updated_count}개 업데이트 완료")

# 결과 확인
print("\n" + "=" * 80)
print("카테고리별 분포")
print("=" * 80)

from collections import defaultdict

worldviews = supabase.table('worldviews').select('*').execute().data
category_counts = defaultdict(list)

for wv in worldviews:
    frame = json.loads(wv['frame'])
    category = frame.get('category')
    category_counts[category].append(wv['title'])

for cat, titles in sorted(category_counts.items()):
    print(f"\n{cat} ({len(titles)}개):")
    for title in titles:
        print(f"  - {title}")

print("\n" + "=" * 80)
print("✓ 완료!")
print("=" * 80)
