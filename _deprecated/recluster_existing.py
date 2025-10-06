#!/usr/bin/env python3
"""기존 논리들을 벡터 기반으로 재클러스터링"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

print("🔄 기존 논리 재클러스터링 시작...\n")

# 1. 기존 클러스터 모두 삭제
print("1️⃣ 기존 클러스터 초기화...")
supabase.table('logic_repository').update({'cluster_id': None}).neq('id', '00000000-0000-0000-0000-000000000000').execute()
supabase.table('logic_clusters').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
print("   ✅ 초기화 완료\n")

# 2. 벡터 임베딩이 있는 논리 가져오기
print("2️⃣ 벡터 임베딩 있는 논리 조회...")
logics = supabase.table('logic_repository')\
    .select('id, core_argument, context_issue, vector_embedding')\
    .not_.is_('vector_embedding', 'null')\
    .order('created_at', desc=False)\
    .execute()

print(f"   📊 총 {len(logics.data)}개 논리 발견\n")

# 3. 각 논리를 순차적으로 처리하며 클러스터링
print("3️⃣ 벡터 유사도 기반 클러스터링...")
clusters_created = 0
logics_clustered = 0

for i, logic in enumerate(logics.data, 1):
    try:
        # find_similar_cluster 함수로 유사한 클러스터 찾기
        result = supabase.rpc('find_similar_cluster', {
            'p_embedding': logic['vector_embedding'],
            'p_similarity_threshold: 0.6
        }).execute()

        cluster_id = result.data

        if cluster_id:
            # 기존 클러스터에 추가
            supabase.table('logic_repository').update({
                'cluster_id': cluster_id
            }).eq('id', logic['id']).execute()
            logics_clustered += 1
        else:
            # 새 클러스터 생성
            cluster_name = (logic.get('context_issue') or logic['core_argument'][:50]) + ' 관련 논리들'
            new_cluster = supabase.table('logic_clusters').insert({
                'cluster_name': cluster_name,
                'context_issue': logic.get('context_issue'),
                'representative_embedding': logic['vector_embedding'],
                'logic_count': 0
            }).execute()

            cluster_id = new_cluster.data[0]['id']

            # 논리에 클러스터 할당
            supabase.table('logic_repository').update({
                'cluster_id': cluster_id
            }).eq('id', logic['id']).execute()

            clusters_created += 1
            logics_clustered += 1

        if i % 10 == 0:
            print(f"   진행: {i}/{len(logics.data)} (클러스터 {clusters_created}개 생성)")

    except Exception as e:
        print(f"   ⚠️  논리 {logic['id']} 처리 실패: {e}")
        continue

print(f"\n✅ 재클러스터링 완료!")
print(f"   📊 처리된 논리: {logics_clustered}개")
print(f"   🔗 생성된 클러스터: {clusters_created}개")

# 4. 각 클러스터의 통계와 대표 벡터 업데이트
print("\n4️⃣ 클러스터 통계 및 대표 벡터 업데이트...")
clusters = supabase.table('logic_clusters').select('id').execute()
for cluster in clusters.data:
    supabase.rpc('update_cluster_representative_embedding', {
        'p_cluster_id': cluster['id']
    }).execute()

# 5. 최종 결과
final_clusters = supabase.table('logic_clusters').select('*').execute()
print(f"   ✅ {len(final_clusters.data)}개 클러스터 업데이트 완료\n")

print("=" * 60)
print("📊 최종 클러스터 목록:")
for cluster in final_clusters.data:
    print(f"  - {cluster['cluster_name'][:60]}... ({cluster['logic_count']}개 논리)")

print("\n✨ 대시보드에서 확인하세요: http://localhost:3001")