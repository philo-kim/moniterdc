"""
전체 시스템 종합 검증

목표:
1. Layer 0 → 1 → 2 → 3 전체 파이프라인 검증
2. 9개 세계관의 연결 관계 분석
3. 시간에 따른 세계관 성장 시뮬레이션
4. 세계관 간 메타-프레임 존재 여부
5. 최종 시스템 설계 제안

방법: 실제 DB 데이터로 시뮬레이션
"""

import os
from supabase import create_client
from openai import OpenAI
import json
from dotenv import load_dotenv
from collections import defaultdict
import datetime

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("=" * 100)
print("전체 시스템 종합 검증")
print("=" * 100)

# ============================================================================
# STEP 1: 전체 데이터 로드 및 파이프라인 검증
# ============================================================================

print("\n\n" + "=" * 100)
print("STEP 1: 전체 데이터 로드 및 파이프라인 매핑")
print("=" * 100)

# Layer 0: Contents
contents = supabase.table("contents").select("*").execute().data
print(f"\n[Layer 0] Contents (원본 게시글): {len(contents)}개")

# Layer 1: Perceptions
perceptions = supabase.table("perceptions").select("*").execute().data
print(f"[Layer 1] Perceptions (추출된 인식): {len(perceptions)}개")

# Layer 2: Worldviews
worldviews = supabase.table("worldviews").select("*").execute().data
print(f"[Layer 2] Worldviews (세계관 묶음): {len(worldviews)}개")

print(f"\n변환 비율:")
print(f"  Contents → Perceptions: 1 : {len(perceptions)/max(len(contents), 1):.1f}")
print(f"  Perceptions → Worldviews: {len(perceptions)/max(len(worldviews), 1):.1f} : 1")

# ============================================================================
# STEP 2: 역방향 추적 - Perception이 어떻게 Content로 연결되는가?
# ============================================================================

print("\n\n" + "=" * 100)
print("STEP 2: 역방향 추적 (Perception → Content)")
print("=" * 100)

# Perception → Content 매핑
perception_to_content = {}
content_to_perceptions = defaultdict(list)

for p in perceptions:
    content_id = p.get('content_id')
    if content_id:
        perception_to_content[p['id']] = content_id
        content_to_perceptions[content_id].append(p)

print(f"\nContent-Perception 연결:")
print(f"  총 {len(perceptions)}개 perception 중 {len(perception_to_content)}개가 content_id 있음")
print(f"  {len(content_to_perceptions)}개 content가 perception과 연결됨")

# 샘플 추적
sample_content = contents[0] if contents else None
if sample_content:
    content_id = sample_content['id']
    related_perceptions = content_to_perceptions.get(content_id, [])

    print(f"\n샘플 추적:")
    print(f"  Content ID: {content_id}")
    print(f"  Source: {sample_content.get('source_url', 'N/A')[:80]}")
    print(f"  → 추출된 Perception: {len(related_perceptions)}개")

    if related_perceptions:
        for i, p in enumerate(related_perceptions[:3], 1):
            print(f"    {i}. [{p['perceived_valence']}] {p['perceived_subject']} - {p['perceived_attribute']}")
            print(f"       주장: {p.get('claims', [])[:2]}")

# ============================================================================
# STEP 3: 9개 세계관 전체 분석
# ============================================================================

print("\n\n" + "=" * 100)
print("STEP 3: 9개 세계관 전체 분석")
print("=" * 100)

print(f"\n세계관 목록:")
for i, wv in enumerate(worldviews, 1):
    # frame이 문자열일 수 있으므로 JSON 파싱
    frame = wv.get('frame')
    if isinstance(frame, str):
        try:
            frame = json.loads(frame)
        except:
            frame = {}
    elif frame is None:
        frame = {}

    print(f"\n{i}. {wv['title']}")
    print(f"   ID: {wv['id']}")
    print(f"   Perception IDs: {len(wv.get('perception_ids', []))}개")
    print(f"   Category: {frame.get('category', 'N/A')}")
    print(f"   Subcategory: {frame.get('subcategory', 'N/A')}")
    print(f"   Priority: {frame.get('priority', 'N/A')}")
    print(f"   Created: {wv.get('created_at', 'N/A')[:10]}")

# ============================================================================
# STEP 4: 세계관별 실제 Perception 분석
# ============================================================================

print("\n\n" + "=" * 100)
print("STEP 4: 세계관별 실제 Perception 매칭")
print("=" * 100)

# Perception ID로 매핑
perception_by_id = {p['id']: p for p in perceptions}

worldview_analysis = []

for wv in worldviews:
    wv_id = wv['id']
    wv_title = wv['title']
    perception_ids = wv.get('perception_ids', [])

    # 실제 존재하는 perception만 필터
    actual_perceptions = []
    for pid in perception_ids:
        if pid in perception_by_id:
            actual_perceptions.append(perception_by_id[pid])

    # 통계
    valence_dist = {"positive": 0, "negative": 0, "neutral": 0}
    subjects = defaultdict(int)
    keywords = []
    emotions = []

    for p in actual_perceptions:
        valence_dist[p['perceived_valence']] += 1
        subjects[p['perceived_subject']] += 1
        keywords.extend(p.get('keywords', []))
        emotions.extend(p.get('emotions', []))

    # 키워드/감정 빈도
    keyword_freq = defaultdict(int)
    for kw in keywords:
        keyword_freq[kw] += 1

    emotion_freq = defaultdict(int)
    for em in emotions:
        emotion_freq[em] += 1

    # frame 파싱
    frame = wv.get('frame')
    if isinstance(frame, str):
        try:
            frame = json.loads(frame)
        except:
            frame = {}
    elif frame is None:
        frame = {}

    analysis = {
        "id": wv_id,
        "title": wv_title,
        "category": frame.get('category', 'N/A'),
        "subcategory": frame.get('subcategory', 'N/A'),
        "priority": frame.get('priority', 'N/A'),
        "perception_ids_count": len(perception_ids),
        "actual_perceptions_count": len(actual_perceptions),
        "valence": dict(valence_dist),
        "top_subjects": dict(sorted(subjects.items(), key=lambda x: x[1], reverse=True)[:5]),
        "top_keywords": dict(sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]),
        "top_emotions": dict(sorted(emotion_freq.items(), key=lambda x: x[1], reverse=True)[:5]),
    }

    worldview_analysis.append(analysis)

    print(f"\n{wv_title}:")
    print(f"  실제 Perception: {len(actual_perceptions)}개 / {len(perception_ids)}개 IDs")
    print(f"  Valence: neg {valence_dist['negative']}, pos {valence_dist['positive']}, neu {valence_dist['neutral']}")
    print(f"  주요 주체: {list(subjects.keys())[:5]}")
    print(f"  주요 키워드: {list(keyword_freq.keys())[:5]}")

# ============================================================================
# STEP 5: 세계관 간 연결 관계 분석
# ============================================================================

print("\n\n" + "=" * 100)
print("STEP 5: 세계관 간 연결 관계 분석")
print("=" * 100)

# Category별 그룹핑
categories = defaultdict(list)
for analysis in worldview_analysis:
    cat = analysis['category']
    categories[cat].append(analysis)

print(f"\nCategory 그룹:")
for cat, wvs in categories.items():
    print(f"\n{cat}:")
    for wv in wvs:
        print(f"  - {wv['title']} (priority: {wv['priority']}, {wv['actual_perceptions_count']}개)")

# 세계관 간 키워드 중복 분석
print("\n\n세계관 간 키워드 중복 분석:")
for i, wv1 in enumerate(worldview_analysis):
    for wv2 in worldview_analysis[i+1:]:
        kw1 = set(wv1['top_keywords'].keys())
        kw2 = set(wv2['top_keywords'].keys())
        overlap = kw1 & kw2

        if len(overlap) >= 2:  # 2개 이상 중복
            print(f"\n'{wv1['title']}' ↔ '{wv2['title']}':")
            print(f"  중복 키워드: {overlap}")

# ============================================================================
# STEP 6: Perception 중복 확인
# ============================================================================

print("\n\n" + "=" * 100)
print("STEP 6: Perception 중복 확인 (하나의 Perception이 여러 세계관에?)")
print("=" * 100)

perception_to_worldviews = defaultdict(list)

for wv in worldviews:
    for pid in wv.get('perception_ids', []):
        perception_to_worldviews[pid].append(wv['title'])

# 여러 세계관에 속한 perception 찾기
multi_worldview_perceptions = {pid: wvs for pid, wvs in perception_to_worldviews.items() if len(wvs) > 1}

print(f"\n여러 세계관에 속한 Perception: {len(multi_worldview_perceptions)}개")

if multi_worldview_perceptions:
    print("\n샘플:")
    for pid, wvs in list(multi_worldview_perceptions.items())[:5]:
        if pid in perception_by_id:
            p = perception_by_id[pid]
            print(f"\n  Perception: [{p['perceived_valence']}] {p['perceived_subject']} - {p['perceived_attribute']}")
            print(f"  속한 세계관: {wvs}")

# ============================================================================
# STEP 7: 시간에 따른 세계관 형성 분석
# ============================================================================

print("\n\n" + "=" * 100)
print("STEP 7: 시간에 따른 데이터 형성 분석")
print("=" * 100)

# Content 시간 분석
content_dates = []
for c in contents:
    created = c.get('created_at')
    if created:
        content_dates.append(created)

if content_dates:
    content_dates.sort()
    print(f"\nContent 생성 시간:")
    print(f"  최초: {content_dates[0]}")
    print(f"  최근: {content_dates[-1]}")
    print(f"  총 기간: {(datetime.datetime.fromisoformat(content_dates[-1].replace('Z', '+00:00')) - datetime.datetime.fromisoformat(content_dates[0].replace('Z', '+00:00'))).days}일")

# Worldview 생성 시간
wv_dates = []
for wv in worldviews:
    created = wv.get('created_at')
    if created:
        wv_dates.append((created, wv['title']))

if wv_dates:
    wv_dates.sort()
    print(f"\nWorldview 생성 시간:")
    for date, title in wv_dates:
        print(f"  {date[:10]}: {title}")

# ============================================================================
# STEP 8: 세계관 간 메타-프레임 존재 분석 (GPT)
# ============================================================================

print("\n\n" + "=" * 100)
print("STEP 8: 세계관 간 메타-프레임 존재 분석 (GPT)")
print("=" * 100)

# 9개 세계관 요약 준비
worldview_summaries = []
for analysis in worldview_analysis:
    summary = {
        "title": analysis['title'],
        "category": analysis['category'],
        "subcategory": analysis['subcategory'],
        "perception_count": analysis['actual_perceptions_count'],
        "valence": analysis['valence'],
        "top_subjects": list(analysis['top_subjects'].keys())[:3],
        "top_keywords": list(analysis['top_keywords'].keys())[:5]
    }
    worldview_summaries.append(summary)

prompt_meta = f"""
9개의 정치 세계관이 있습니다:

{json.dumps(worldview_summaries, ensure_ascii=False, indent=2)}

질문:
1. 이 9개 세계관이 독립적인가, 아니면 상위 메타-프레임으로 묶이는가?
2. 만약 묶인다면, 몇 개의 메타-프레임으로 그룹핑되는가?
3. 각 메타-프레임의 핵심 특징은 무엇인가?

JSON 형식으로 답하세요:
{{
  "meta_frames": [
    {{
      "name": "메타-프레임 이름",
      "core_theme": "핵심 주제",
      "worldviews": ["속한 세계관들"],
      "rationale": "왜 이들이 묶이는가?"
    }}
  ],
  "independent_worldviews": ["독립적인 세계관들"],
  "overall_structure": "전체 구조 설명"
}}
"""

print("\nGPT 분석 중...")
response_meta = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt_meta}],
    response_format={"type": "json_object"},
    temperature=0.3
)

meta_analysis = json.loads(response_meta.choices[0].message.content)

print("\n메타-프레임 분석 결과:")
print(json.dumps(meta_analysis, ensure_ascii=False, indent=2))

# ============================================================================
# STEP 9: 새 게시글 추가 시뮬레이션
# ============================================================================

print("\n\n" + "=" * 100)
print("STEP 9: 새 게시글 추가 시뮬레이션")
print("=" * 100)

simulation_scenario = """
시나리오: 새 게시글 추가

현재 상태:
- 9개 세계관 존재
- "독재와 사찰의 부활": 88개 perception
  - Problem: 사회적 불안과 갈등 증가
  - Cause: 정부 정책, 외국인

새 게시글:
"윤석열 정부가 또 중국인 관광객 무비자 연장했다.
이러다가 우리 아이들 납치당하는 거 아니야?
부모들 목소리 내야 한다!"

질문:
1. 이 게시글에서 추출될 Perception은?
2. 어느 세계관에 속할 것인가?
3. 기존 세계관의 Frame이 변하는가, 강화되는가?
"""

print(simulation_scenario)

# GPT로 시뮬레이션
prompt_sim = f"""
{simulation_scenario}

현재 "독재와 사찰의 부활" 세계관:
- Problem: 사회적 불안과 갈등 증가 (confidence: 0.9)
- Cause: 정부 정책, 외국인 (confidence: 0.8)
- Moral: 정부가 국민 안전 위협 (confidence: 0.85)
- Solution: 강력한 안전 대책 (confidence: 0.75)

새 게시글 분석:
1. 추출될 Perception (Subject-Attribute-Valence)
2. 어느 세계관에 속할 것인가? (독재와 사찰의 부활? 이민 정책과 범죄 증가? 새로운?)
3. 기존 Frame에 어떤 영향? (강화? 변경? 분리?)

JSON으로 답하세요.
"""

print("\nGPT 시뮬레이션 중...")
response_sim = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt_sim}],
    response_format={"type": "json_object"},
    temperature=0.3
)

simulation_result = json.loads(response_sim.choices[0].message.content)

print("\n시뮬레이션 결과:")
print(json.dumps(simulation_result, ensure_ascii=False, indent=2))

# ============================================================================
# 결과 저장
# ============================================================================

final_validation = {
    "data_pipeline": {
        "contents": len(contents),
        "perceptions": len(perceptions),
        "worldviews": len(worldviews),
        "conversion_ratio": f"1 content → {len(perceptions)/max(len(contents), 1):.1f} perceptions"
    },
    "worldview_analysis": worldview_analysis,
    "category_grouping": {cat: [wv['title'] for wv in wvs] for cat, wvs in categories.items()},
    "perception_overlap": {
        "multi_worldview_count": len(multi_worldview_perceptions),
        "samples": list(multi_worldview_perceptions.items())[:5]
    },
    "meta_frame_analysis": meta_analysis,
    "simulation": simulation_result,
    "timestamp": datetime.datetime.now().isoformat()
}

with open("/tmp/comprehensive_system_validation.json", "w", encoding="utf-8") as f:
    json.dump(final_validation, f, ensure_ascii=False, indent=2)

print("\n\n" + "=" * 100)
print("✓ 전체 시스템 검증 완료")
print("=" * 100)
print("\n결과 저장: /tmp/comprehensive_system_validation.json")
