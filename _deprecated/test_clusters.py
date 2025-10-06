#!/usr/bin/env python3
"""클러스터링 시스템 테스트"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

print("=" * 60)
print("📊 현재 데이터베이스 상태")
print("=" * 60)

# 1. 전체 논리 수
logics = supabase.table('logic_repository').select('id', count='exact').execute()
print(f"\n📝 전체 논리: {logics.count}개")

# 2. context_issue가 있는 논리 수
with_context = supabase.table('logic_repository').select('id', count='exact').not_.is_('context_issue', 'null').execute()
print(f"✅ context_issue 있음: {with_context.count}개")
print(f"❌ context_issue 없음: {logics.count - with_context.count}개")

# 3. 클러스터 수
clusters = supabase.table('logic_clusters').select('*').execute()
print(f"\n🔗 생성된 클러스터: {len(clusters.data)}개")

if clusters.data:
    print("\n클러스터 목록:")
    for cluster in clusters.data:
        print(f"  - {cluster['context_issue']} ({cluster['logic_count']}개 논리, 평균 위협도 {cluster['threat_level_avg']})")

# 4. 샘플 논리 확인
print("\n📋 샘플 논리 5개:")
sample = supabase.table('logic_repository').select('core_argument, context_issue, cluster_id').limit(5).execute()
for i, logic in enumerate(sample.data, 1):
    print(f"\n{i}. {logic['core_argument'][:50]}...")
    print(f"   이슈: {logic.get('context_issue', 'N/A')}")
    print(f"   클러스터: {'있음' if logic.get('cluster_id') else '없음'}")

print("\n" + "=" * 60)
print("💡 결과 해석:")
if with_context.count == 0:
    print("⚠️  기존 데이터에는 context_issue가 없습니다.")
    print("   → 새로운 크롤링을 실행해야 클러스터가 생성됩니다.")
elif len(clusters.data) == 0:
    print("⚠️  context_issue는 있지만 클러스터가 생성되지 않았습니다.")
    print("   → 트리거가 제대로 작동하지 않았을 수 있습니다.")
else:
    print(f"✅ 클러스터링 시스템이 작동 중입니다!")
    print(f"   {len(clusters.data)}개 클러스터에 논리들이 그룹화되어 있습니다.")

print("=" * 60)