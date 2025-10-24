#!/usr/bin/env python3
"""
Claude vs GPT 알고리즘 검증 스크립트

v2.0 파이프라인을 두 모델로 실행하고 결과 비교:
1. Layered Perception Extraction (3-layer)
2. Reasoning Structure Extraction (5 mechanisms)
"""

import os
import asyncio
import json
from datetime import datetime
from typing import Dict, List
from openai import AsyncOpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
from engines.utils.supabase_client import get_supabase

# Load environment
load_dotenv()

# Initialize clients
openai_client = AsyncOpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
claude_client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# Supabase
supabase = get_supabase()


class ClaudeLayeredPerceptionExtractor:
    """Claude 버전 3-layer perception extractor"""

    def __init__(self):
        self.client = claude_client

    async def extract(self, content: Dict) -> Dict:
        """Extract 3-layer perception using Claude"""

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

❌ 나쁜 예: "사찰은 나쁘다"
✅ 좋은 예: "이들은 맘에 안드는 판사까지 사찰한다 (사법부 장악 시도)"

**구체적으로:**
- 누가 어떤 방법으로 무엇을 한다고 믿는가?
- 그들의 의도/목적은 무엇이라고 생각하는가?
- 어떤 패턴/전략이 있다고 보는가?

## 3. 심층 (Deep Layer) - 무의식적 믿음
**이 글쓴이 진영만의 세계관**

❌ 나쁜 예: "권력은 부패한다" (누구나 하는 말)
✅ 좋은 예: "민주당/좌파는 과거 독재정권처럼 사찰과 탄압으로 권력을 유지하려 한다"

❌ 나쁜 예: "작은 문제가 커진다"
✅ 좋은 예: "지금의 작은 사찰이 과거 독재시대처럼 전면적 감시국가로 발전한다"

**구체적으로:**
- 이 진영이 **역사를 어떻게 보는가**? (과거 사례 → 현재 연결)
- **상대편의 본질**을 어떻게 규정하는가? (민주당/좌파/중국 = ?)
- **세상의 작동 원리**를 어떻게 이해하는가? (A가 일어나면 반드시 B가 일어난다)

JSON 형식으로만 응답:
{{
  "explicit_claims": [
    {{
      "subject": "민주당",
      "predicate": "유심교체 정보를 불법으로 얻었다",
      "evidence_cited": "나경원 의원 SNS - 어떻게 알았나",
      "quote": "유심교체를 어떻게 알아"
    }}
  ],
  "implicit_assumptions": [
    "민주당은 통신사를 협박해서 개인 사찰용 정보를 얻는다",
    "맘에 안드는 판사를 제거하기 위해 사찰한다 (사법부 장악 시도)"
  ],
  "reasoning_gaps": [
    {{
      "from": "유심교체 정보를 알았다",
      "to": "통신사 협박으로 얻었다",
      "gap": "정상적 방법 가능성은 배제하고 즉시 불법으로 단정"
    }}
  ],
  "deep_beliefs": [
    "민주당/좌파는 과거 독재정권처럼 사찰로 반대파를 제거한다",
    "지금의 작은 사찰이 곧 전면적 감시독재 사회로 발전한다 (역사 반복)",
    "이들은 사법부까지 장악해서 완전한 권력을 차지하려 한다"
  ],
  "worldview_hints": "과거 독재 → 현재 재현, 좌파 = 독재 본성, 사법부 장악 시도"
}}
"""

        # Claude API call (sync)
        message = self.client.messages.create(
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


class GPTLayeredPerceptionExtractor:
    """GPT 버전 (기존 알고리즘)"""

    def __init__(self):
        self.client = openai_client

    async def extract(self, content: Dict) -> Dict:
        """Extract 3-layer perception using GPT"""

        # Same prompt as Claude
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

## 3. 심층 (Deep Layer) - 무의식적 믿음
**이 글쓴이 진영만의 세계관**

JSON 형식:
{{
  "explicit_claims": [...],
  "implicit_assumptions": [...],
  "reasoning_gaps": [...],
  "deep_beliefs": [...],
  "worldview_hints": "..."
}}
"""

        response = await self.client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are an expert in discourse analysis. Always respond in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result


async def test_single_content(content_id: str = None):
    """단일 content로 GPT vs Claude 비교"""

    print("=" * 80)
    print("Claude vs GPT 검증 테스트")
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
    print(f"   내용: {content['body'][:200]}...")

    # Initialize extractors
    gpt_extractor = GPTLayeredPerceptionExtractor()
    claude_extractor = ClaudeLayeredPerceptionExtractor()

    # Run GPT
    print(f"\n🤖 GPT-5 분석 중...")
    gpt_result = await gpt_extractor.extract(content)
    print(f"   ✓ 완료")

    # Run Claude
    print(f"\n🧠 Claude Sonnet 4.5 분석 중...")
    claude_result = await claude_extractor.extract(content)
    print(f"   ✓ 완료")

    # Compare results
    print(f"\n" + "=" * 80)
    print("결과 비교")
    print("=" * 80)

    comparison = {
        "content": {
            "id": content['id'],
            "title": content['title'],
            "body_preview": content['body'][:500]
        },
        "gpt_result": gpt_result,
        "claude_result": claude_result,
        "comparison": {
            "explicit_claims": {
                "gpt_count": len(gpt_result.get('explicit_claims', [])),
                "claude_count": len(claude_result.get('explicit_claims', []))
            },
            "implicit_assumptions": {
                "gpt_count": len(gpt_result.get('implicit_assumptions', [])),
                "claude_count": len(claude_result.get('implicit_assumptions', []))
            },
            "deep_beliefs": {
                "gpt_count": len(gpt_result.get('deep_beliefs', [])),
                "claude_count": len(claude_result.get('deep_beliefs', []))
            }
        }
    }

    # Print comparison
    print(f"\n📊 레이어별 추출 개수:")
    print(f"   Explicit Claims:  GPT {comparison['comparison']['explicit_claims']['gpt_count']:2d} | Claude {comparison['comparison']['explicit_claims']['claude_count']:2d}")
    print(f"   Implicit Assume:  GPT {comparison['comparison']['implicit_assumptions']['gpt_count']:2d} | Claude {comparison['comparison']['implicit_assumptions']['claude_count']:2d}")
    print(f"   Deep Beliefs:     GPT {comparison['comparison']['deep_beliefs']['gpt_count']:2d} | Claude {comparison['comparison']['deep_beliefs']['claude_count']:2d}")

    # Show actual content
    print(f"\n📝 GPT Explicit Claims:")
    for claim in gpt_result.get('explicit_claims', [])[:3]:
        if isinstance(claim, dict):
            print(f"   - {claim.get('subject', 'N/A')}: {claim.get('predicate', 'N/A')}")
        else:
            print(f"   - {claim}")

    print(f"\n📝 Claude Explicit Claims:")
    for claim in claude_result.get('explicit_claims', [])[:3]:
        if isinstance(claim, dict):
            print(f"   - {claim.get('subject', 'N/A')}: {claim.get('predicate', 'N/A')}")
        else:
            print(f"   - {claim}")

    print(f"\n💭 GPT Deep Beliefs:")
    for belief in gpt_result.get('deep_beliefs', [])[:3]:
        print(f"   - {belief}")

    print(f"\n💭 Claude Deep Beliefs:")
    for belief in claude_result.get('deep_beliefs', [])[:3]:
        print(f"   - {belief}")

    # Save results
    output_file = f"_test_results/claude_vs_gpt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 결과 저장: {output_file}")

    return comparison


async def main():
    """Main execution"""

    import sys

    content_id = sys.argv[1] if len(sys.argv) > 1 else None

    await test_single_content(content_id)


if __name__ == "__main__":
    asyncio.run(main())
