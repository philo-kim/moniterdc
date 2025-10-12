"""
88개 Perception으로 Worldview 재구성 및 전체 시스템 검증

실제 데이터로 Layer 1 → Layer 2 → Layer 3 전체 파이프라인 구축
"""

import os
from supabase import create_client
from openai import OpenAI
import json
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("=" * 100)
print("88개 Perception으로 Worldview 재구성 및 전체 파이프라인 검증")
print("=" * 100)

# ============================================================================
# STEP 1: 현재 88개 Perception 로드
# ============================================================================

print("\n\nSTEP 1: 현재 88개 Perception 로드")
print("-" * 100)

perceptions = supabase.table("perceptions").select("*").execute().data
print(f"총 Perception: {len(perceptions)}개")

# 통계
valence_dist = {"positive": 0, "negative": 0, "neutral": 0}
subjects = defaultdict(int)
keywords_all = []

for p in perceptions:
    valence_dist[p['perceived_valence']] += 1
    subjects[p['perceived_subject']] += 1
    keywords_all.extend(p.get('keywords', []))

print(f"\nValence 분포:")
for v, count in valence_dist.items():
    print(f"  {v}: {count}개 ({count/len(perceptions)*100:.1f}%)")

print(f"\n주요 주체 (Top 10):")
for subj, count in sorted(subjects.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {subj}: {count}개")

# ============================================================================
# STEP 2: GPT로 Worldview 재구성
# ============================================================================

print("\n\nSTEP 2: GPT로 Worldview 재구성")
print("-" * 100)

# Perception 요약
perception_summaries = []
for p in perceptions:
    summary = f"[{p['perceived_valence']}] {p['perceived_subject']} - {p['perceived_attribute']}"
    perception_summaries.append({
        "id": p['id'],
        "summary": summary,
        "keywords": p.get('keywords', [])[:5],
        "claims": p.get('claims', [])[:2]
    })

prompt_cluster = f"""
88개의 정치 perception이 있습니다.

샘플 (전체 중 30개):
{json.dumps(perception_summaries[:30], ensure_ascii=False, indent=2)}

이 88개 perception을 **의미적으로 유사한 그룹**으로 묶어서 세계관을 구성하세요.

요구사항:
1. 너무 세분화하지 말고, 3-7개 정도의 **큰 세계관**으로 묶기
2. 각 세계관은:
   - title: 세계관 이름
   - core_theme: 핵심 주제
   - perception_ids: 속할 perception ID 리스트 (전체 88개 중 해당되는 것들)

JSON 형식:
{{
  "worldviews": [
    {{
      "title": "...",
      "core_theme": "...",
      "perception_ids": ["id1", "id2", ...]
    }}
  ],
  "rationale": "왜 이렇게 묶었는지 설명"
}}

IMPORTANT: perception_ids는 위 88개 perception의 실제 ID를 사용하세요.
샘플에 없는 perception도 keywords와 subject를 보고 유추해서 적절한 세계관에 배치하세요.
"""

print("\nGPT로 클러스터링 중...")
print("(이 작업은 전체 88개 perception을 분석하므로 시간이 걸릴 수 있습니다)")

# 전체 perception 정보 제공
all_perception_info = []
for p in perceptions:
    all_perception_info.append({
        "id": p['id'],
        "subject": p['perceived_subject'],
        "attribute": p['perceived_attribute'],
        "valence": p['perceived_valence'],
        "keywords": p.get('keywords', [])[:5]
    })

prompt_cluster_full = f"""
88개의 정치 perception:
{json.dumps(all_perception_info, ensure_ascii=False, indent=2)}

이 88개를 3-7개의 큰 세계관으로 그룹핑하세요.

각 세계관:
- title: 세계관 이름
- core_theme: 핵심 주제
- perception_ids: 속할 perception ID 리스트

JSON:
{{
  "worldviews": [...]
}}
"""

response_cluster = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt_cluster_full}],
    response_format={"type": "json_object"},
    temperature=0.3
)

clustering_result = json.loads(response_cluster.choices[0].message.content)

print(f"\nGPT가 생성한 세계관: {len(clustering_result['worldviews'])}개")
for i, wv in enumerate(clustering_result['worldviews'], 1):
    print(f"\n{i}. {wv['title']}")
    print(f"   Theme: {wv['core_theme']}")
    print(f"   Perceptions: {len(wv['perception_ids'])}개")

# ============================================================================
# STEP 3: 각 Worldview에 Layer 3 (Frame) 구조 추가
# ============================================================================

print("\n\nSTEP 3: 각 Worldview에 Frame 구조 추가")
print("-" * 100)

perception_by_id = {p['id']: p for p in perceptions}

worldviews_with_frames = []

for wv in clustering_result['worldviews']:
    title = wv['title']
    perception_ids = wv['perception_ids']

    # 실제 perception 로드
    actual_perceptions = []
    for pid in perception_ids:
        if pid in perception_by_id:
            actual_perceptions.append(perception_by_id[pid])

    if not actual_perceptions:
        print(f"\n{title}: Perception 0개 - 스킵")
        continue

    print(f"\n{title}: {len(actual_perceptions)}개 perception 분석 중...")

    # Valence 통계
    wv_valence = {"positive": 0, "negative": 0, "neutral": 0}
    for p in actual_perceptions:
        wv_valence[p['perceived_valence']] += 1

    # 샘플 주장
    sample_claims = []
    for p in actual_perceptions[:20]:
        sample_claims.extend(p.get('claims', []))

    # Frame 구조 생성 (Entman + Competition)
    prompt_frame = f"""
세계관: {title}
Theme: {wv['core_theme']}

{len(actual_perceptions)}개 perception 분석:
- Valence: negative {wv_valence['negative']}, positive {wv_valence['positive']}, neutral {wv_valence['neutral']}
- 샘플 주장:
{json.dumps(sample_claims[:20], ensure_ascii=False, indent=2)}

Entman + Competition 프레임 구조를 JSON 형식으로 생성:

JSON 구조:
{{
  "entman": {{
    "problem": {{"what": "...", "confidence": 0.9, "evidence": ["...", "..."]}},
    "cause": {{"who": ["..."], "how": "...", "confidence": 0.8, "evidence": ["..."]}},
    "moral": {{"judgment": "...", "victims": ["..."], "responsible": ["..."], "confidence": 0.85, "evidence": ["..."]}},
    "solution": {{"what": "...", "who_acts": ["..."], "confidence": 0.75, "evidence": ["..."]}}
  }},
  "competition": {{
    "dominant_frame": {{
      "name": "...",
      "strength": {wv_valence['negative']/(wv_valence['negative']+wv_valence['positive']+wv_valence['neutral']):.2f},
      "core_view": "..."
    }},
    "competing_frames": [{{
      "name": "...",
      "strength": {wv_valence['positive']/(wv_valence['negative']+wv_valence['positive']+wv_valence['neutral']):.2f},
      "key_difference": "..."
    }}]
  }}
}}
"""

    response_frame = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt_frame}],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    frame = json.loads(response_frame.choices[0].message.content)

    worldview_complete = {
        "title": title,
        "core_theme": wv['core_theme'],
        "perception_ids": perception_ids,
        "perception_count": len(actual_perceptions),
        "valence_distribution": wv_valence,
        "frame": frame
    }

    worldviews_with_frames.append(worldview_complete)

    print(f"  ✓ Frame 생성 완료")
    print(f"    Problem: {frame['entman']['problem']['what']}")
    print(f"    Dominant Frame: {frame['competition']['dominant_frame']['name']} ({frame['competition']['dominant_frame']['strength']})")

# ============================================================================
# STEP 4: 사용자 시뮬레이션
# ============================================================================

print("\n\nSTEP 4: 사용자 시뮬레이션 - 민주세력이 세계관 이해하기")
print("-" * 100)

# 첫 번째 세계관으로 시뮬레이션
if worldviews_with_frames:
    test_wv = worldviews_with_frames[0]

    print(f"\n테스트 세계관: {test_wv['title']}")
    print(f"Perception: {test_wv['perception_count']}개")

    user_questions = [
        f"'{test_wv['title']}' 세계관을 가진 사람들은 무엇을 문제로 보나요?",
        f"이들과 나(민주세력)는 어떻게 다른가요?",
        f"이들과 대화할 때 주의할 점은 무엇인가요?"
    ]

    for q in user_questions:
        print(f"\nQ: {q}")

        prompt_qa = f"""
세계관: {test_wv['title']}
Frame:
- Problem: {test_wv['frame']['entman']['problem']['what']} (confidence: {test_wv['frame']['entman']['problem']['confidence']})
- Cause: {test_wv['frame']['entman']['cause']['who']}
- Moral: {test_wv['frame']['entman']['moral']['judgment']}
- Solution: {test_wv['frame']['entman']['solution']['what']}
- Dominant Frame: {test_wv['frame']['competition']['dominant_frame']['name']} ({test_wv['frame']['competition']['dominant_frame']['strength']})
- Competing Frame: {test_wv['frame']['competition']['competing_frames'][0]['name']} ({test_wv['frame']['competition']['competing_frames'][0]['strength']})

사용자 질문: {q}

위 프레임 정보로 2-3문장으로 답하세요.
"""

        response_qa = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_qa}],
            temperature=0.3
        )

        print(f"A: {response_qa.choices[0].message.content.strip()}")

# ============================================================================
# 결과 저장
# ============================================================================

final_result = {
    "original_perceptions": len(perceptions),
    "worldviews_created": len(worldviews_with_frames),
    "worldviews": worldviews_with_frames,
    "pipeline_verified": {
        "layer1_perceptions": f"{len(perceptions)}개",
        "layer2_worldviews": f"{len(worldviews_with_frames)}개",
        "layer3_frames": "각 worldview마다 Entman + Competition 구조"
    }
}

with open("/tmp/rebuilt_worldviews_complete_system.json", "w", encoding="utf-8") as f:
    json.dump(final_result, f, ensure_ascii=False, indent=2)

print("\n\n" + "=" * 100)
print("✓ 전체 시스템 재구성 완료")
print("=" * 100)
print(f"\n88개 Perception → {len(worldviews_with_frames)}개 Worldview (각각 Frame 구조 포함)")
print("\n결과 저장: /tmp/rebuilt_worldviews_complete_system.json")
