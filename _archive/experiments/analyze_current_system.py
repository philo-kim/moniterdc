#!/usr/bin/env python3
"""
현재 시스템 상세 분석

목적: 재구축을 위한 현황 파악
- DB 구조 분석
- 실제 데이터 샘플 확인
- 인과 패턴 추출 가능성 검토
"""

import os
import json
from supabase import create_client
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))

print("="*80)
print("현재 시스템 상세 분석")
print("="*80)

# ==============================================================================
# 1. 데이터베이스 구조 분석
# ==============================================================================
print("\n[1] 데이터베이스 구조")
print("-"*80)

# Contents
contents = supabase.table('contents').select('*').limit(1).execute()
if contents.data:
    print("\n[Contents 테이블]")
    print(f"  총 개수: {supabase.table('contents').select('id').execute().data.__len__()}")
    print(f"  컬럼: {list(contents.data[0].keys())}")

# Perceptions
perceptions = supabase.table('perceptions').select('*').limit(1).execute()
if perceptions.data:
    print("\n[Perceptions 테이블]")
    print(f"  총 개수: {supabase.table('perceptions').select('id').execute().data.__len__()}")
    print(f"  컬럼: {list(perceptions.data[0].keys())}")

# Worldviews
worldviews = supabase.table('worldviews').select('*').limit(1).execute()
if worldviews.data:
    print("\n[Worldviews 테이블]")
    print(f"  총 개수: {supabase.table('worldviews').select('id').execute().data.__len__()}")
    print(f"  컬럼: {list(worldviews.data[0].keys())}")

# ==============================================================================
# 2. 실제 DC 게시글 샘플 분석
# ==============================================================================
print("\n\n[2] DC 게시글 원문 샘플 (인과 관계 추출 가능성 검토)")
print("-"*80)

contents_sample = supabase.table('contents').select('title, body').limit(5).execute()

for i, content in enumerate(contents_sample.data, 1):
    print(f"\n[게시글 {i}]")
    print(f"제목: {content.get('title', '')}")
    body = content.get('body', '')[:400]
    print(f"내용: {body}...")
    print()

    # 인과 관계 패턴 가능성 체크
    causal_keywords = ['왜냐하면', '때문에', '그래서', '따라서', '~하면', '~하기에']
    found_patterns = [kw for kw in causal_keywords if kw in body]
    if found_patterns:
        print(f"  → 인과 키워드 발견: {found_patterns}")

    print("-"*80)

# ==============================================================================
# 3. Perception 구조 상세 분석
# ==============================================================================
print("\n\n[3] Perception 구조 상세 분석")
print("-"*80)

all_perceptions = supabase.table('perceptions').select('*').execute().data

print(f"\n총 {len(all_perceptions)}개 Perception")

# Claims 분석
claims_count = []
for p in all_perceptions:
    claims = p.get('claims', [])
    if isinstance(claims, str):
        try:
            claims = json.loads(claims)
        except:
            claims = []
    if isinstance(claims, list):
        claims_count.append(len(claims))

print(f"\nClaims 통계:")
print(f"  평균: {sum(claims_count)/len(claims_count):.1f}개/perception")
print(f"  최소: {min(claims_count)}개")
print(f"  최대: {max(claims_count)}개")

# 샘플 Perception 출력
print(f"\n샘플 Perception (상세):")
sample_p = all_perceptions[0]
print(json.dumps(sample_p, ensure_ascii=False, indent=2)[:1000])

# ==============================================================================
# 4. Worldview 구조 분석
# ==============================================================================
print("\n\n[4] Worldview 구조 분석")
print("-"*80)

all_worldviews = supabase.table('worldviews').select('*').execute().data

print(f"\n총 {len(all_worldviews)}개 Worldview:")
for wv in all_worldviews:
    title = wv.get('title', '')
    frame = wv.get('frame', {})
    if isinstance(frame, str):
        try:
            frame = json.loads(frame)
        except:
            frame = {}

    perception_ids = wv.get('perception_ids', [])
    if isinstance(perception_ids, str):
        try:
            perception_ids = json.loads(perception_ids)
        except:
            perception_ids = []

    print(f"\n  [{title}]")
    print(f"    Perception 개수: {len(perception_ids)}")
    print(f"    Frame 존재: {bool(frame)}")

    if frame:
        print(f"    Frame 구조: {list(frame.keys())}")

# ==============================================================================
# 5. 인과 관계 추출 가능성 평가
# ==============================================================================
print("\n\n[5] 인과 관계 추출 가능성 평가")
print("-"*80)

# Content → Perception 연결 확인
content_perception_map = defaultdict(list)
for p in all_perceptions:
    content_id = p.get('content_id')
    if content_id:
        content_perception_map[content_id].append(p['id'])

linked_contents = len(content_perception_map)
total_contents = len(supabase.table('contents').select('id').execute().data)

print(f"\nContent → Perception 연결:")
print(f"  전체 Contents: {total_contents}")
print(f"  Perception 있는 Contents: {linked_contents}")
print(f"  커버리지: {linked_contents/total_contents*100:.1f}%")

# Perception → Worldview 연결 확인
perception_worldview_map = defaultdict(list)
for wv in all_worldviews:
    perception_ids = wv.get('perception_ids', [])
    if isinstance(perception_ids, str):
        try:
            perception_ids = json.loads(perception_ids)
        except:
            perception_ids = []

    for pid in perception_ids:
        perception_worldview_map[pid].append(wv['title'])

linked_perceptions = len(perception_worldview_map)
total_perceptions = len(all_perceptions)

print(f"\nPerception → Worldview 연결:")
print(f"  전체 Perceptions: {total_perceptions}")
print(f"  Worldview에 속한 Perceptions: {linked_perceptions}")
print(f"  커버리지: {linked_perceptions/total_perceptions*100:.1f}%")

# ==============================================================================
# 6. 인과 패턴 추출을 위한 데이터 품질 체크
# ==============================================================================
print("\n\n[6] 인과 패턴 추출을 위한 데이터 품질 체크")
print("-"*80)

# Claims에 인과 관계 표현이 있는지
causal_claims = 0
total_claims = 0

for p in all_perceptions:
    claims = p.get('claims', [])
    if isinstance(claims, str):
        try:
            claims = json.loads(claims)
        except:
            claims = []

    if isinstance(claims, list):
        for claim in claims:
            total_claims += 1
            causal_keywords = ['왜냐하면', '때문에', '그래서', '따라서', '~하면', '~면', '~기에']
            if any(kw in str(claim) for kw in causal_keywords):
                causal_claims += 1

print(f"\nClaims 분석:")
print(f"  전체 Claims: {total_claims}")
print(f"  인과 키워드 포함 Claims: {causal_claims}")
print(f"  비율: {causal_claims/total_claims*100:.1f}%" if total_claims > 0 else "  비율: N/A")

# ==============================================================================
# 7. 결론 및 권장사항
# ==============================================================================
print("\n\n[7] 결론 및 권장사항")
print("="*80)

print("""
현황:
✓ Contents: 458개 (DC 게시글 원문)
✓ Perceptions: 88개 (추출된 인식)
✓ Worldviews: 9개 (주제 기반 clustering)

문제점:
✗ Worldview = 주제 분류 (인과 관계 없음)
✗ Frame 구조 존재하지만 추상적
✗ 새로운 사건 해석 불가능

다음 단계:
1. Perception Extractor 개선 (인과 관계 추출 추가)
2. Causal Pattern Detector 신규 구현
3. Worldview Constructor 재작성 (패턴 기반)
4. Event Interpreter 신규 구현
""")

# 결과 저장
results = {
    "database_structure": {
        "contents_count": total_contents,
        "perceptions_count": total_perceptions,
        "worldviews_count": len(all_worldviews)
    },
    "coverage": {
        "content_perception": f"{linked_contents/total_contents*100:.1f}%",
        "perception_worldview": f"{linked_perceptions/total_perceptions*100:.1f}%"
    },
    "data_quality": {
        "total_claims": total_claims,
        "causal_claims": causal_claims,
        "causal_ratio": f"{causal_claims/total_claims*100:.1f}%" if total_claims > 0 else "N/A"
    },
    "worldviews": [wv['title'] for wv in all_worldviews]
}

with open('_current_system_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n결과 저장: _current_system_analysis.json")
print("="*80)
