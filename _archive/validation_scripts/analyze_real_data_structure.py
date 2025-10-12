"""
실제 DB 데이터를 보고 레이어 구조 총괄 분석

목표:
1. 실제 DB에서 전체 데이터 파이프라인 확인
2. Layer 0 (원본) → Layer 1 (Perception) → Layer 2 (Worldview) → Layer 3 (Frame) 구조 설계
3. 실제 사용자 질문에 어떻게 답할 수 있는지 시뮬레이션
"""

import os
from supabase import create_client
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Supabase 설정
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

print("=" * 80)
print("1단계: 실제 DB 데이터 구조 파악")
print("=" * 80)

# 1. Content (Layer 0: 원본 데이터)
print("\n[Layer 0] Content - 원본 유튜브 댓글")
print("-" * 80)
contents = supabase.table("contents").select("*").limit(3).execute()
for i, content in enumerate(contents.data, 1):
    print(f"\n{i}. Content ID: {content['id']}")
    print(f"   Type: {content.get('type')}")
    print(f"   Text (처음 200자): {content.get('text', '')[:200]}...")
    print(f"   Source: {content.get('source_url', 'N/A')[:80]}...")

# 2. Perception (Layer 1: 주체-속성-평가 추출)
print("\n\n[Layer 1] Perception - 댓글에서 추출한 인식")
print("-" * 80)
perceptions = supabase.table("perceptions").select("*").limit(5).execute()
print(f"전체 Perception 개수: {len(supabase.table('perceptions').select('id').execute().data)}")

for i, p in enumerate(perceptions.data, 1):
    print(f"\n{i}. Perception ID: {p['id'][:8]}...")
    print(f"   주체: {p['perceived_subject']}")
    print(f"   속성: {p['perceived_attribute']}")
    print(f"   평가: {p['perceived_valence']}")
    print(f"   주장: {p.get('claims', [])[:2]}")
    print(f"   키워드: {p.get('keywords', [])[:5]}")
    print(f"   감정: {p.get('emotions', [])[:3]}")

# 3. Worldview (Layer 2: Perception 묶음)
print("\n\n[Layer 2] Worldview - Perception 묶음")
print("-" * 80)
worldviews = supabase.table("worldviews").select("*").execute()
print(f"전체 Worldview 개수: {len(worldviews.data)}")

for i, wv in enumerate(worldviews.data[:3], 1):
    print(f"\n{i}. Worldview: {wv['title']}")
    print(f"   ID: {wv['id']}")
    print(f"   Perception IDs 개수: {len(wv.get('perception_ids', []))}")
    print(f"   Frame: {wv.get('frame')}")  # 현재 비어있을 것
    print(f"   Created: {wv.get('created_at', '')[:19]}")

# 4. "독재와 사찰의 부활" 세계관 상세 분석
print("\n\n" + "=" * 80)
print("2단계: '독재와 사찰의 부활' 세계관 상세 분석")
print("=" * 80)

target_worldview = None
for wv in worldviews.data:
    if "독재" in wv['title']:
        target_worldview = wv
        break

if target_worldview:
    print(f"\n세계관: {target_worldview['title']}")
    print(f"Perception IDs: {len(target_worldview.get('perception_ids', []))}개")

    # 실제 perception 로드
    all_perceptions = supabase.table("perceptions").select("*").execute().data

    print(f"\n실제 DB에 있는 Perception: {len(all_perceptions)}개")

    # 5. 데이터 분포 분석
    print("\n" + "-" * 80)
    print("데이터 분포 분석")
    print("-" * 80)

    subjects = {}
    attributes = {}
    valences = {"positive": 0, "negative": 0, "neutral": 0}
    all_keywords = []
    all_emotions = []
    all_claims = []

    for p in all_perceptions:
        # 주체
        subj = p['perceived_subject']
        subjects[subj] = subjects.get(subj, 0) + 1

        # 속성
        attr = p['perceived_attribute']
        attributes[attr] = attributes.get(attr, 0) + 1

        # 평가
        valences[p['perceived_valence']] += 1

        # 키워드, 감정, 주장
        all_keywords.extend(p.get('keywords', []))
        all_emotions.extend(p.get('emotions', []))
        all_claims.extend(p.get('claims', []))

    print(f"\n주체 분포 (Top 10):")
    for subj, count in sorted(subjects.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {subj}: {count}개")

    print(f"\n속성 분포 (Top 10):")
    for attr, count in sorted(attributes.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {attr}: {count}개")

    print(f"\nValence 분포:")
    for v, count in valences.items():
        print(f"  {v}: {count}개 ({count/len(all_perceptions)*100:.1f}%)")

    # 키워드 빈도
    keyword_freq = {}
    for kw in all_keywords:
        keyword_freq[kw] = keyword_freq.get(kw, 0) + 1

    print(f"\n키워드 Top 15:")
    for kw, count in sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {kw}: {count}회")

    # 감정 빈도
    emotion_freq = {}
    for em in all_emotions:
        emotion_freq[em] = emotion_freq.get(em, 0) + 1

    print(f"\n감정 Top 10:")
    for em, count in sorted(emotion_freq.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {em}: {count}회")

# 6. 실제 Perception 샘플 보기
print("\n\n" + "=" * 80)
print("3단계: 실제 Perception 샘플 (원문 확인)")
print("=" * 80)

for i, p in enumerate(all_perceptions[:10], 1):
    print(f"\n{i}. [{p['perceived_valence']}] {p['perceived_subject']} - {p['perceived_attribute']}")
    print(f"   주장: {p.get('claims', [])}")
    print(f"   키워드: {p.get('keywords', [])}")
    print(f"   감정: {p.get('emotions', [])}")

# 7. Content와 Perception 연결 확인
print("\n\n" + "=" * 80)
print("4단계: Content(원본) → Perception 연결 확인")
print("=" * 80)

sample_perception = all_perceptions[0]
content_id = sample_perception.get('content_id')

if content_id:
    original_content = supabase.table("contents").select("*").eq("id", content_id).execute()
    if original_content.data:
        content = original_content.data[0]
        print(f"\nPerception: [{sample_perception['perceived_valence']}] {sample_perception['perceived_subject']} - {sample_perception['perceived_attribute']}")
        print(f"주장: {sample_perception.get('claims', [])}")
        print(f"\n원본 Content:")
        print(f"Type: {content.get('type')}")
        print(f"Text: {content.get('text', '')[:300]}...")

# 저장
results = {
    "total_contents": len(contents.data),
    "total_perceptions": len(all_perceptions),
    "total_worldviews": len(worldviews.data),
    "target_worldview": target_worldview['title'] if target_worldview else None,
    "subjects_distribution": dict(sorted(subjects.items(), key=lambda x: x[1], reverse=True)[:20]),
    "attributes_distribution": dict(sorted(attributes.items(), key=lambda x: x[1], reverse=True)[:20]),
    "valence_distribution": valences,
    "top_keywords": dict(sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:20]),
    "top_emotions": dict(sorted(emotion_freq.items(), key=lambda x: x[1], reverse=True)[:10]),
}

with open("/tmp/real_data_structure_analysis.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n\n✓ 분석 완료. 결과 저장: /tmp/real_data_structure_analysis.json")
