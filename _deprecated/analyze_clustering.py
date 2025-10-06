#!/usr/bin/env python3
"""클러스터링 데이터 분석 및 최적 방안 제시"""
import os
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

print("=" * 80)
print("📊 클러스터링 데이터 분석")
print("=" * 80)

# 1. 전체 논리 데이터 가져오기
logics = supabase.table('logic_repository')\
    .select('id, core_argument, context_issue, keywords, vector_embedding, created_at')\
    .not_.is_('vector_embedding', 'null')\
    .order('created_at', desc=False)\
    .limit(100)\
    .execute()

print(f"\n📝 분석 대상: {len(logics.data)}개 논리\n")

# 2. Context_issue 분포 확인
context_issues = [l.get('context_issue') for l in logics.data if l.get('context_issue')]
context_counter = Counter(context_issues)

print("🏷️  Context_issue 분포 (상위 10개):")
for issue, count in context_counter.most_common(10):
    print(f"   {count:2d}개: {issue[:60]}")

print(f"\n   총 {len(context_counter)}개의 서로 다른 context_issue")
print(f"   평균: {len(context_issues)/len(context_counter):.1f}개/이슈")

# 3. 키워드 중복도 확인
all_keywords = []
for l in logics.data:
    if l.get('keywords'):
        all_keywords.extend(l['keywords'])

keyword_counter = Counter(all_keywords)
print(f"\n🔑 키워드 중복도 (상위 15개):")
for kw, count in keyword_counter.most_common(15):
    print(f"   {count:2d}회: {kw}")

# 4. 벡터 유사도 분석 (샘플)
print(f"\n🧮 벡터 유사도 분석 (샘플 20개):")
print("   같은 키워드를 공유하는 논리 쌍의 유사도:\n")

similarities = []
for i in range(min(20, len(logics.data))):
    for j in range(i+1, min(i+10, len(logics.data))):
        l1 = logics.data[i]
        l2 = logics.data[j]

        # 공통 키워드가 있는가?
        kw1 = set(l1.get('keywords', []))
        kw2 = set(l2.get('keywords', []))
        common_kw = kw1 & kw2

        if not common_kw:
            continue

        # 벡터 유사도 계산
        try:
            v1 = np.array(l1['vector_embedding'], dtype=float)
            v2 = np.array(l2['vector_embedding'], dtype=float)

            # 코사인 유사도
            similarity = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            similarities.append(similarity)

            if len(similarities) <= 10:  # 처음 10개만 출력
                print(f"   유사도 {similarity:.3f} | 공통키워드: {list(common_kw)[:2]}")
                print(f"      A: {l1['core_argument'][:50]}...")
                print(f"      B: {l2['core_argument'][:50]}...")
                print()
        except Exception as e:
            continue

if similarities:
    print(f"   📈 통계:")
    print(f"      평균 유사도: {np.mean(similarities):.3f}")
    print(f"      중앙값: {np.median(similarities):.3f}")
    print(f"      최소값: {np.min(similarities):.3f}")
    print(f"      최대값: {np.max(similarities):.3f}")
    print(f"      표준편차: {np.std(similarities):.3f}")

# 5. 최적 임계값 제안
print("\n" + "=" * 80)
print("💡 분석 결과 및 제안")
print("=" * 80)

if similarities:
    avg_sim = np.mean(similarities)
    std_sim = np.std(similarities)

    print(f"\n1️⃣  벡터 유사도 기반:")
    print(f"   현재 임계값: 0.75 (너무 높음)")
    print(f"   실제 평균: {avg_sim:.3f}")
    print(f"   제안 임계값: {avg_sim - 0.5*std_sim:.3f} ~ {avg_sim:.3f}")

print(f"\n2️⃣  Context_issue 기반:")
print(f"   총 {len(context_counter)}개 서로 다른 이슈")
print(f"   문제: 너무 세분화되어 있음")
print(f"   제안: GPT 프롬프트 수정 → 짧은 키워드")

print(f"\n3️⃣  키워드 기반:")
print(f"   상위 키워드 중복도가 높음")
print(f"   제안: 공통 키워드 2개 이상 → 같은 클러스터")

print("\n" + "=" * 80)
print("🎯 최적 클러스터링 전략 제안")
print("=" * 80)

print("""
전략 A: 하이브리드 매칭 (권장)
  1. 공통 키워드 2개 이상 → 즉시 같은 클러스터
  2. 벡터 유사도 > 0.5 → 같은 클러스터
  3. Context_issue 일치 → 같은 클러스터
  → 하나라도 만족하면 묶음

전략 B: 점진적 성장 + 주기적 재조정
  1. 새 논리 추가 시 느슨한 기준으로 매칭 (유사도 0.4)
  2. 매일 밤 전체 재클러스터링 (K-means 등)
  3. 클러스터 대표 벡터 재계산

전략 C: 2단계 클러스터링
  1. 키워드 기반 1차 그룹화 (빠름)
  2. 각 그룹 내에서 벡터 기반 세분화 (정확함)
""")