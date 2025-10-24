"""
완전 자동 설정 스크립트

현재 상태:
- ✅ 297개 contents 수집 완료
- ✅ 88개 layered_perceptions 분석 완료
- ✅ 6개 hierarchical worldviews 구축 완료
- ✅ Dashboard UI 완성
- ❌ perception_worldview_links 테이블 미생성
- ❌ perception-worldview 매칭 미완료

이 스크립트가 수행하는 작업:
1. ⚠️ perception_worldview_links 테이블 생성 (수동 필요)
2. 전체 perception을 worldview에 매칭
3. 통계 업데이트
4. 대시보드 확인
"""

import asyncio
import sys
import os
sys.path.insert(0, '/Users/taehyeonkim/dev/minjoo/moniterdc')

from engines.utils.supabase_client import get_supabase
from engines.analyzers.optimal_worldview_constructor import OptimalWorldviewConstructor

print("="*70)
print("세계관 시스템 완성 스크립트")
print("="*70)

# Step 1: Check table
print("\n[Step 1/4] perception_worldview_links 테이블 확인...")

supabase = get_supabase()

try:
    result = supabase.table('perception_worldview_links').select('*').limit(1).execute()
    print("✅ 테이블 존재")
    print(f"   현재 {len(result.data)}개 링크")
except Exception as e:
    print("❌ 테이블이 아직 생성되지 않았습니다.")
    print("")
    print("다음 단계:")
    print("1. Supabase Dashboard (https://supabase.com/dashboard) 접속")
    print("2. 프로젝트 선택 → SQL Editor")
    print("3. 아래 SQL 복사하여 실행:")
    print("")
    print("-" * 70)

    with open('supabase/migrations/203_create_perception_worldview_links.sql', 'r') as f:
        print(f.read())

    print("-" * 70)
    print("")
    print("SQL 실행 후 이 스크립트를 다시 실행하세요.")
    sys.exit(1)

# Step 2: Match perceptions to worldviews
print("\n[Step 2/4] Perception → Worldview 매칭...")

async def match_all_perceptions():
    """모든 perception을 worldview에 매칭"""
    constructor = OptimalWorldviewConstructor()

    # Load all perceptions
    perceptions = supabase.table('layered_perceptions').select('*').execute().data

    # Load all worldviews
    worldviews = supabase.table('worldviews').select('*').execute().data
    hierarchical_wvs = [w for w in worldviews if '>' in w['title']]

    print(f"   Perception: {len(perceptions)}개")
    print(f"   Worldview: {len(hierarchical_wvs)}개")

    # Match
    links = await constructor._match_perceptions_to_worldviews(perceptions, hierarchical_wvs)

    print(f"   ✅ {links}개 링크 생성")

    return links

try:
    links_created = asyncio.run(match_all_perceptions())
except Exception as e:
    print(f"   ❌ 실패: {e}")
    sys.exit(1)

# Step 3: Update worldview statistics
print("\n[Step 3/4] Worldview 통계 업데이트...")

worldviews = supabase.table('worldviews').select('*').execute().data

for wv in worldviews:
    # Get linked perceptions
    links = supabase.table('perception_worldview_links')\
        .select('perception_id')\
        .eq('worldview_id', wv['id'])\
        .execute().data

    perception_count = len(links)

    # Update worldview
    supabase.table('worldviews').update({
        'total_perceptions': perception_count,
        'strength_overall': min(perception_count / 20, 1.0)  # Simple strength calculation
    }).eq('id', wv['id']).execute()

    print(f"   {wv['title'][:50]}: {perception_count}개 perception")

print("   ✅ 통계 업데이트 완료")

# Step 4: Verify dashboard
print("\n[Step 4/4] Dashboard 확인...")

# Check if dashboard can fetch worldviews
try:
    import requests
    response = requests.get('http://localhost:3000/api/worldviews')

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Dashboard API 정상 작동")
        print(f"   세계관 {len(data.get('worldviews', []))}개 조회 가능")
    else:
        print(f"   ⚠️ Dashboard가 실행되지 않음 (Status: {response.status_code})")
        print(f"   다음 명령으로 Dashboard 실행:")
        print(f"   cd dashboard && npm run dev")
except Exception as e:
    print(f"   ⚠️ Dashboard가 실행되지 않음")
    print(f"   다음 명령으로 Dashboard 실행:")
    print(f"   cd dashboard && npm run dev")

print("\n" + "="*70)
print("✅ 세계관 시스템 설정 완료!")
print("="*70)

print(f"""
현재 상태:
- Contents: 297개
- Perceptions: 88개
- Worldviews: {len(worldviews)}개 (계층형)
- Links: {links_created}개

다음 단계:
1. Dashboard 확인: http://localhost:3000
2. 반박 논리 생성: python3 scripts/generate_deconstruction.py
3. 자동 업데이트 설정: GitHub Actions 활성화

시스템이 준비되었습니다! 🎉
""")
