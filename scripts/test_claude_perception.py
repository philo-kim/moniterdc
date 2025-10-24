#!/usr/bin/env python3
"""
Claude로 v2.0 알고리즘 검증

기존 GPT로 돌린 결과가 DB에 있으니,
Claude로 새로 돌려서 비교
"""

import os
import asyncio
import json
from datetime import datetime
from typing import Dict
from anthropic import Anthropic
from dotenv import load_dotenv
import sys
sys.path.insert(0, '/Users/taehyeonkim/dev/minjoo/moniterdc')

from engines.utils.supabase_client import get_supabase

# Load environment
load_dotenv()

# Initialize Claude
claude_client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# Supabase
supabase = get_supabase()


def extract_with_claude(content: Dict) -> Dict:
    """Claude로 3-layer perception 추출"""

    prompt = f"""
다음은 DC Gallery 정치 갤러리의 글입니다:

제목: {content['title']}
내용: {content['body'][:2000]}

이 글을 **3개 층위**로 분석해주세요.

⚠️ 중요: 일반론이 아닌, **이 글쓴이가 실제로 믿는 구체적인 내용**을 추출하세요.

## 1. 표면층 (Explicit Layer) - 명시적 주장
**글에서 직접 말하고 있는 것**
- 누가/무엇을 비난하는가?
- 어떤 행동/사건을 문제 삼는가?
- 구체적인 인물/조직/사건 이름 포함

## 2. 암묵층 (Implicit Layer) - 전제하는 사고
**말하지 않았지만 당연하게 여기는 것**

❌ 나쁜 예: "비공개 정보를 안다 = 불법"
✅ 좋은 예: "민주당은 통신사를 협박해서 개인정보를 얻는다"

**구체적으로:**
- 누가 어떤 방법으로 무엇을 한다고 믿는가?
- 그들의 의도/목적은 무엇이라고 생각하는가?

## 3. 심층 (Deep Layer) - 무의식적 믿음
**이 글쓴이 진영만의 세계관**

❌ 나쁜 예: "권력은 부패한다" (누구나 하는 말)
✅ 좋은 예: "민주당/좌파는 과거 독재정권처럼 사찰과 탄압으로 권력을 유지하려 한다"

**구체적으로:**
- 이 진영이 **역사를 어떻게 보는가**? (과거 사례 → 현재 연결)
- **상대편의 본질**을 어떻게 규정하는가?
- **세상의 작동 원리**를 어떻게 이해하는가?

JSON 형식으로만 응답:
{{
  "explicit_claims": [
    {{
      "subject": "민주당",
      "predicate": "유심교체 정보를 불법으로 얻었다",
      "evidence_cited": "나경원 의원 SNS",
      "quote": "유심교체를 어떻게 알아"
    }}
  ],
  "implicit_assumptions": [
    "민주당은 통신사를 협박해서 개인 사찰용 정보를 얻는다"
  ],
  "reasoning_gaps": [
    {{
      "from": "유심교체 정보를 알았다",
      "to": "통신사 협박으로 얻었다",
      "gap": "정상적 방법 가능성은 배제하고 즉시 불법으로 단정"
    }}
  ],
  "deep_beliefs": [
    "민주당/좌파는 과거 독재정권처럼 사찰로 반대파를 제거한다"
  ],
  "worldview_hints": "과거 독재 → 현재 재현"
}}
"""

    # Claude API call
    message = claude_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        temperature=0,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text

    # Parse JSON
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        json_str = response_text[json_start:json_end].strip()
    elif "{" in response_text:
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        json_str = response_text[json_start:json_end]
    else:
        json_str = response_text

    result = json.loads(json_str)
    return result


def test_single_content(content_id: str = None):
    """단일 content로 Claude 테스트"""

    print("=" * 80)
    print("Claude v2.0 알고리즘 검증")
    print("=" * 80)

    # Get test content
    if content_id:
        query = supabase.table('contents').select('*').eq('id', content_id)
    else:
        # Get random recent content
        query = supabase.table('contents').select('*').limit(1).order('published_at', desc=True)

    result = query.execute()

    if not result.data:
        print("❌ Content not found")
        return

    content = result.data[0]

    print(f"\n📄 테스트 Content:")
    print(f"   ID: {content['id']}")
    print(f"   제목: {content['title']}")
    print(f"   내용 미리보기:")
    print(f"   {content['body'][:300]}...")

    # Get existing GPT perception from DB
    perception_query = supabase.table('layered_perceptions')\
        .select('*')\
        .eq('content_id', content['id'])\
        .execute()

    gpt_perception = perception_query.data[0] if perception_query.data else None

    # Run Claude
    print(f"\n🧠 Claude Sonnet 4.5 분석 중...")
    claude_result = extract_with_claude(content)
    print(f"   ✓ 완료")

    # Display results
    print(f"\n" + "=" * 80)
    print("Claude 분석 결과")
    print("=" * 80)

    print(f"\n📝 Explicit Claims ({len(claude_result.get('explicit_claims', []))}개):")
    for i, claim in enumerate(claude_result.get('explicit_claims', [])[:5], 1):
        if isinstance(claim, dict):
            print(f"   {i}. [{claim.get('subject', 'N/A')}] {claim.get('predicate', 'N/A')}")
            if claim.get('quote'):
                print(f"      인용: \"{claim.get('quote')}\"")
        else:
            print(f"   {i}. {claim}")

    print(f"\n💭 Implicit Assumptions ({len(claude_result.get('implicit_assumptions', []))}개):")
    for i, assumption in enumerate(claude_result.get('implicit_assumptions', [])[:5], 1):
        print(f"   {i}. {assumption}")

    print(f"\n🔍 Reasoning Gaps ({len(claude_result.get('reasoning_gaps', []))}개):")
    for i, gap in enumerate(claude_result.get('reasoning_gaps', [])[:3], 1):
        if isinstance(gap, dict):
            print(f"   {i}. {gap.get('from')} → {gap.get('to')}")
            print(f"      Gap: {gap.get('gap')}")
        else:
            print(f"   {i}. {gap}")

    print(f"\n🌍 Deep Beliefs ({len(claude_result.get('deep_beliefs', []))}개):")
    for i, belief in enumerate(claude_result.get('deep_beliefs', [])[:5], 1):
        print(f"   {i}. {belief}")

    print(f"\n💡 Worldview Hints:")
    print(f"   {claude_result.get('worldview_hints', 'N/A')}")

    # Compare with GPT if exists
    if gpt_perception:
        print(f"\n" + "=" * 80)
        print("GPT vs Claude 비교 (DB에 저장된 GPT 결과)")
        print("=" * 80)

        print(f"\n📊 레이어별 추출 개수:")
        print(f"   Explicit Claims:  GPT {len(gpt_perception.get('explicit_claims', [])):2d} | Claude {len(claude_result.get('explicit_claims', [])):2d}")
        print(f"   Implicit Assume:  GPT {len(gpt_perception.get('implicit_assumptions', [])):2d} | Claude {len(claude_result.get('implicit_assumptions', [])):2d}")
        print(f"   Deep Beliefs:     GPT {len(gpt_perception.get('deep_beliefs', [])):2d} | Claude {len(claude_result.get('deep_beliefs', [])):2d}")

        print(f"\n📝 GPT Explicit Claims (비교):")
        for claim in gpt_perception.get('explicit_claims', [])[:3]:
            if isinstance(claim, dict):
                print(f"   - [{claim.get('subject', 'N/A')}] {claim.get('predicate', 'N/A')}")
            else:
                print(f"   - {claim}")

        print(f"\n💭 GPT Deep Beliefs (비교):")
        for belief in gpt_perception.get('deep_beliefs', [])[:3]:
            print(f"   - {belief}")

    # Save results
    comparison = {
        "content": {
            "id": content['id'],
            "title": content['title'],
            "body_preview": content['body'][:500]
        },
        "claude_result": claude_result,
        "gpt_result": {
            "explicit_claims": gpt_perception.get('explicit_claims', []) if gpt_perception else [],
            "implicit_assumptions": gpt_perception.get('implicit_assumptions', []) if gpt_perception else [],
            "deep_beliefs": gpt_perception.get('deep_beliefs', []) if gpt_perception else [],
            "worldview_hints": gpt_perception.get('worldview_hints', '') if gpt_perception else ''
        } if gpt_perception else None
    }

    output_file = f"_test_results/claude_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 결과 저장: {output_file}")

    return comparison


if __name__ == "__main__":
    import sys
    content_id = sys.argv[1] if len(sys.argv) > 1 else None
    test_single_content(content_id)
