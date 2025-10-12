#!/usr/bin/env python3
"""
Layer-by-Layer Authentic Voice Validation (FIXED)

DB에서 직접 데이터를 로드하여 실제 검증 수행
"""

import os
import sys
import json
from pathlib import Path
from supabase import create_client
from openai import OpenAI
from collections import defaultdict, Counter

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def call_gpt(prompt, model="gpt-4o-mini", response_format=None):
    try:
        kwargs = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        if response_format:
            kwargs["response_format"] = response_format

        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    except Exception as e:
        print(f"GPT error: {e}")
        return None

print("="*80)
print("LAYER-BY-LAYER AUTHENTIC VOICE VALIDATION (DB Direct Load)")
print("="*80)

# ==============================================================================
# LOAD ALL DATA FROM DB
# ==============================================================================
print("\n[Loading Data from DB]")

# Load perceptions with claims
print("  Loading perceptions...")
response = supabase.table('perceptions').select('*').limit(100).execute()
all_perceptions = response.data
print(f"  Loaded {len(all_perceptions)} perceptions")

# Filter perceptions with claims
perceptions_with_claims = []
for p in all_perceptions:
    claims = p.get('claims', [])
    if isinstance(claims, str):
        try:
            claims = json.loads(claims)
        except:
            claims = []

    if isinstance(claims, list) and len(claims) > 0:
        p['claims'] = claims  # Ensure it's a list
        perceptions_with_claims.append(p)

print(f"  Perceptions with claims: {len(perceptions_with_claims)}")

# Load contents for these perceptions
content_ids = list(set([p['content_id'] for p in perceptions_with_claims if p.get('content_id')]))[:20]
print(f"  Loading {len(content_ids)} contents...")
response = supabase.table('contents').select('*').in_('id', content_ids).execute()
contents_map = {c['id']: c for c in response.data}
print(f"  Loaded {len(contents_map)} contents")

# Load worldviews
print("  Loading worldviews...")
with open('/tmp/rebuilt_worldviews_complete_system.json', 'r', encoding='utf-8') as f:
    worldviews_data = json.load(f)
worldviews = worldviews_data.get('worldviews', [])
print(f"  Loaded {len(worldviews)} worldviews")

# ==============================================================================
# LAYER 0→1: Raw Content → Perception (Claims Extraction)
# ==============================================================================
print("\n" + "="*80)
print("LAYER 0→1: Raw Content → Perception Claims Extraction")
print("="*80)

layer01_results = []

for p in perceptions_with_claims[:5]:  # Test first 5
    content_id = p.get('content_id')
    content = contents_map.get(content_id)

    if not content:
        continue

    raw_text = content.get('content', '')
    claims = p.get('claims', [])

    if not raw_text or not claims:
        continue

    # GPT Evaluation: Voice preservation
    prompt = f"""
원본 게시글:
{raw_text[:800]}

추출된 주장들:
{json.dumps(claims, ensure_ascii=False, indent=2)}

평가 (JSON 형식):
{{
  "구체적_표현_보존": {{"점수": 1-10, "보존된_예시": ["예시1", "예시2"]}},
  "어투_유지": {{"점수": 1-10, "분석": "설명"}},
  "핵심_논리": {{"점수": 1-10, "분석": "설명"}},
  "특정성_손실": {{"점수": 1-10, "손실": "있다면"}},
  "authentic_voice_점수": 1-10
}}
"""

    result = call_gpt(prompt, model="gpt-4o", response_format={"type": "json_object"})
    if result:
        try:
            eval_data = json.loads(result)
            layer01_results.append({
                "perception_id": p['id'],
                "content_preview": raw_text[:150],
                "claims": claims,
                "evaluation": eval_data
            })

            score = eval_data.get('authentic_voice_점수', 0)
            print(f"\nPerception {p['id'][:8]}: {score}/10")
        except Exception as e:
            print(f"  Parse error: {e}")

avg01 = sum([r['evaluation'].get('authentic_voice_점수', 0) for r in layer01_results]) / len(layer01_results) if layer01_results else 0
print(f"\n[Layer 0→1] 평균 점수: {avg01:.1f}/10 {'✓ PASS' if avg01 >= 7 else '✗ FAIL'}")

with open('/tmp/layer01_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(layer01_results, f, ensure_ascii=False, indent=2)

# ==============================================================================
# LAYER 1→2: Cluster perceptions into worldviews
# ==============================================================================
print("\n" + "="*80)
print("LAYER 1→2: Perception → Worldview Clustering")
print("="*80)

# For each worldview, get its perception_ids from Frame evidence
layer12_results = []

for wv in worldviews[:3]:
    title = wv.get('title', '')
    frame = wv.get('frame', {})

    # Extract perception subjects from frame evidence
    evidence = frame.get('entman', {}).get('problem', {}).get('evidence', [])

    if not evidence:
        continue

    # Find matching perceptions by claims
    matching_perceptions = []
    for p in perceptions_with_claims:
        p_claims = p.get('claims', [])
        # Check if any claim matches evidence
        for claim in p_claims:
            if any(ev in claim or claim in ev for ev in evidence):
                matching_perceptions.append(p)
                break

    if len(matching_perceptions) < 2:
        continue

    # Collect all claims
    all_claims = []
    for p in matching_perceptions:
        all_claims.extend(p.get('claims', []))

    # GPT Evaluation
    prompt = f"""
"{title}" 세계관으로 묶인 주장들:
{json.dumps(all_claims[:40], ensure_ascii=False, indent=2)}

평가 (JSON 형식):
{{
  "세계관_일관성": {{"점수": 1-10, "분석": ""}},
  "부적절한_혼합": {{"점수": 1-10, "문제": ""}},
  "다양성_유지": {{"점수": 1-10, "예시": []}},
  "고유명사_보존": {{"점수": 1-10, "핵심_용어": []}},
  "clustering_quality_점수": 1-10
}}
"""

    result = call_gpt(prompt, model="gpt-4o", response_format={"type": "json_object"})
    if result:
        try:
            eval_data = json.loads(result)
            layer12_results.append({
                "worldview": title,
                "perception_count": len(matching_perceptions),
                "claims_count": len(all_claims),
                "evaluation": eval_data
            })

            score = eval_data.get('clustering_quality_점수', 0)
            print(f"\n{title}: {score}/10 ({len(matching_perceptions)} perceptions)")
        except Exception as e:
            print(f"  Parse error: {e}")

avg12 = sum([r['evaluation'].get('clustering_quality_점수', 0) for r in layer12_results]) / len(layer12_results) if layer12_results else 0
print(f"\n[Layer 1→2] 평균 점수: {avg12:.1f}/10 {'✓ PASS' if avg12 >= 7 else '✗ FAIL'}")

with open('/tmp/layer12_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(layer12_results, f, ensure_ascii=False, indent=2)

# ==============================================================================
# LAYER 2→3: Generate Authentic Voice Layer
# ==============================================================================
print("\n" + "="*80)
print("LAYER 2→3: Worldview → Frame + Authentic Voice Layer")
print("="*80)

layer23_results = []

for wv in worldviews:
    title = wv.get('title', '')
    frame = wv.get('frame', {})
    evidence = frame.get('entman', {}).get('problem', {}).get('evidence', [])

    if not evidence:
        print(f"\n✗ {title}: No evidence")
        continue

    # Use evidence as claims (they ARE the actual claims from DB)
    all_claims = evidence  # These are the raw claims

    # GPT: Generate Authentic Voice Layer
    prompt = f"""
"{title}" 세계관의 Authentic Voice Layer 생성

실제 주장들:
{json.dumps(all_claims, ensure_ascii=False, indent=2)}

JSON 형식:
{{
  "raw_claims": [가장 구체적인 주장 20개, 원문 그대로],
  "key_phrases": [반복되는 핵심 표현 10개],
  "signature_terms": [특유의 용어/인물명 10개],
  "recurring_patterns": {{
    "논리패턴": ["패턴1", "패턴2"],
    "어투패턴": ["패턴1", "패턴2"]
  }},
  "example_voices": [대표 예시 5개]
}}

반드시 원문 표현 그대로 유지. 추상화 금지.
"""

    result = call_gpt(prompt, model="gpt-4o", response_format={"type": "json_object"})
    if result:
        try:
            authentic_voice = json.loads(result)

            # Enhanced Frame
            enhanced_frame = {
                "entman": frame.get('entman', {}),
                "competition": frame.get('competition', {}),
                "authentic_voice": authentic_voice
            }

            layer23_results.append({
                "worldview": title,
                "frame": enhanced_frame,
                "raw_claims_count": len(authentic_voice.get('raw_claims', [])),
                "key_phrases_count": len(authentic_voice.get('key_phrases', [])),
                "signature_terms_count": len(authentic_voice.get('signature_terms', []))
            })

            print(f"\n✓ {title}")
            print(f"  Raw claims: {len(authentic_voice.get('raw_claims', []))}개")
            print(f"  Key phrases: {len(authentic_voice.get('key_phrases', []))}개")
            print(f"  Signature terms: {len(authentic_voice.get('signature_terms', []))}개")

        except Exception as e:
            print(f"\n✗ {title}: {e}")

print(f"\n[Layer 2→3] Enhanced: {len(layer23_results)}/{len(worldviews)} worldviews")

with open('/tmp/layer23_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(layer23_results, f, ensure_ascii=False, indent=2)

# ==============================================================================
# END-TO-END: User Question Answering
# ==============================================================================
print("\n" + "="*80)
print("END-TO-END: User Question Answering")
print("="*80)

test_q = "조희대 대법원장을 국정감사에 부르는것을 나경원 의원이 반대하고 있어. 그들은 어떻게 생각하기에 이렇게 행동하는거 같아?"
print(f"\n질문: {test_q}")

end_results = []

for result in layer23_results[:3]:
    title = result['worldview']
    frame = result['frame']
    authentic = frame.get('authentic_voice', {})

    print(f"\n[{title}]")

    # OLD: Frame only
    prompt_old = f"""
당신은 "{title}" 세계관을 분석하는 AI입니다.
질문: {test_q}
이 세계관을 가진 사람들은 어떻게 생각할까요? 2-3문장.
"""

    answer_old = call_gpt(prompt_old, model="gpt-4o-mini")

    # NEW: Authentic Voice
    prompt_new = f"""
당신은 "{title}" 세계관을 가진 사람입니다.

실제 주장들:
{json.dumps(authentic.get('raw_claims', [])[:20], ensure_ascii=False, indent=2)}

핵심 표현:
{json.dumps(authentic.get('key_phrases', []), ensure_ascii=False)}

특징 용어:
{json.dumps(authentic.get('signature_terms', []), ensure_ascii=False)}

질문: {test_q}

위 주장들의 표현과 논리를 그대로 사용해 답하세요. 2-3문장.
"""

    answer_new = call_gpt(prompt_new, model="gpt-4o-mini")

    # Evaluation
    eval_prompt = f"""
질문: {test_q}

답변1 (Frame만): {answer_old}
답변2 (Authentic Voice): {answer_new}

JSON 평가:
{{
  "답변1": {{"특정성": 1-10, "authenticity": 1-10}},
  "답변2": {{"특정성": 1-10, "authenticity": 1-10}},
  "최고_답변": 1 or 2,
  "improvement_score": 1-10
}}
"""

    comparison = call_gpt(eval_prompt, model="gpt-4o", response_format={"type": "json_object"})
    if comparison:
        try:
            comp_data = json.loads(comparison)
            end_results.append({
                "worldview": title,
                "answer_old": answer_old,
                "answer_new": answer_new,
                "evaluation": comp_data
            })

            print(f"  OLD: {answer_old[:80]}...")
            print(f"  NEW: {answer_new[:80]}...")
            print(f"  Best: {comp_data.get('최고_답변')}, Improvement: {comp_data.get('improvement_score')}/10")
        except Exception as e:
            print(f"  Eval error: {e}")

with open('/tmp/end_to_end_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(end_results, f, ensure_ascii=False, indent=2)

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "="*80)
print("VALIDATION SUMMARY")
print("="*80)

summary = {
    "layer01": {
        "tested": len(layer01_results),
        "avg_score": avg01,
        "status": "PASS" if avg01 >= 7 else "FAIL"
    },
    "layer12": {
        "tested": len(layer12_results),
        "avg_score": avg12,
        "status": "PASS" if avg12 >= 7 else "FAIL"
    },
    "layer23": {
        "enhanced": len(layer23_results),
        "status": "COMPLETED"
    },
    "end_to_end": {
        "tested": len(end_results),
        "improvement_avg": sum([r['evaluation'].get('improvement_score', 0) for r in end_results]) / len(end_results) if end_results else 0
    }
}

print(f"\n[Layer 0→1] {summary['layer01']['tested']}개 테스트 - 평균 {summary['layer01']['avg_score']:.1f}/10 - {summary['layer01']['status']}")
print(f"[Layer 1→2] {summary['layer12']['tested']}개 테스트 - 평균 {summary['layer12']['avg_score']:.1f}/10 - {summary['layer12']['status']}")
print(f"[Layer 2→3] {summary['layer23']['enhanced']}개 강화 완료")
print(f"[End-to-End] {summary['end_to_end']['tested']}개 테스트 - 평균 개선도 {summary['end_to_end']['improvement_avg']:.1f}/10")

with open('/tmp/validation_summary_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("\n파일:")
print("  - /tmp/layer01_fixed.json")
print("  - /tmp/layer12_fixed.json")
print("  - /tmp/layer23_fixed.json")
print("  - /tmp/end_to_end_fixed.json")
print("  - /tmp/validation_summary_fixed.json")

print("\n" + "="*80)
print("COMPLETE")
print("="*80)
