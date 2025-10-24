"""
ReasoningStructureExtractor - 추론 구조 분석 엔진

Content → Reasoning Structure 변환
5개 메커니즘 기반 분석:
1. 즉시_단정: 관찰 → (검증 생략) → 결론
2. 역사_투사: 과거 패턴 → 현재 반복
3. 필연적_인과: X → 반드시 Y
4. 네트워크_추론: 연결 → 조직적 공모
5. 표면_부정: 표면 X / 실제 Y
"""

from anthropic import Anthropic
import os
import json
import asyncio
from typing import Dict, List
from uuid import UUID
from engines.utils.supabase_client import get_supabase

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


class ReasoningStructureExtractor:
    """Extract reasoning structure with 5 core mechanisms"""

    def __init__(self):
        self.supabase = get_supabase()

    async def extract(self, content: Dict) -> UUID:
        """
        Extract reasoning structure from a single content

        Args:
            content: Content dict with title and body

        Returns:
            UUID of created/updated layered_perception
        """

        prompt = f"""
다음 담론을 단계별로 분석하세요:

제목: {content['title']}
내용: {content['body'][:2000]}

## Step 1: 추론 흐름 파악

이 글의 논리 전개를 추적하세요:
- 어떤 관찰에서 시작?
- 어떤 결론에 도달?
- 중간에 생략된 검증은?

## Step 2: 검증 생략 확인 (즉시_단정)

□ 즉시_단정: A를 관찰 → 검증 없이 B로 단정했나요?
- 예: "정보를 알고있다" → "불법으로 얻었다" (정상적 취득 가능성 배제)

## Step 3: 과거 연결 확인 (역사_투사)

□ 역사_투사: 과거 사례를 현재에 투사했나요?
- 예: "과거 독재정권의 사찰" → "지금도 똑같이 한다"

## Step 4: 필연성 확인 (필연적_인과)

□ 필연적_인과: X가 일어나면 필연적으로 Y가 일어난다고 믿나요?
- 예: "작은 사찰" → "반드시 전면적 독재로 발전"

## Step 5: 네트워크 확인 (네트워크_추론)

□ 네트워크_추론: 개별 사건들을 조직적 음모로 연결했나요?
- 예: "여러 사건들" → "계획된 조직적 행동"

## Step 6: 표면/실제 대비 (표면_부정)

□ 표면_부정: 표면적 명분과 실제 의도를 대비시켰나요?
- 예: "표면: 자유민주주의 수호 / 실제: 권력 유지"

## Step 7: Actor 추출

이 담론이 다루는 주요 행위자:
- Subject: 누구?
- Purpose: 왜 행동?
- Methods: 어떤 수단?

JSON 형식:
{{
  "mechanisms": ["즉시_단정", "필연적_인과"],
  "actor": {{
    "subject": "민주당/좌파",
    "purpose": "권력 유지",
    "methods": ["사찰", "협박"]
  }},
  "logic_chain": [
    "민주당이 정보를 파악했다",
    "합법 취득 가능성을 배제했다",
    "불법 사찰로 단정했다",
    "독재 시도로 해석했다"
  ],
  "explicit_claims": [
    "이번에 민주당이 통신사를 협박해 개인정보를 불법 취득했다",
    "민주당이 맘에 안드는 판사를 표적 사찰한다"
  ],
  "implicit_assumptions": [
    "민주당은 항상 통신사를 협박해 반대파 정보를 얻는다",
    "사법부 인사까지 사찰 대상으로 삼는다"
  ],
  "deep_beliefs": [
    "좌파는 과거 독재정권처럼 사찰로 권력을 유지한다",
    "지금의 작은 사찰이 전면적 감시독재 사회로 발전한다"
  ]
}}
"""

        try:
            # Claude Sonnet 4.5 (StepByStep 프롬프트 - 100% 메커니즘 탐지)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    temperature=0,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
            )

            response_text = response.content[0].text

            # Parse JSON from response
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

            # Save to DB
            perception_id = await self._save_perception(content['id'], result)

            return perception_id

        except Exception as e:
            print(f"  ❌ 분석 실패 ({content.get('title', '')[:40]}): {e}")
            raise

    async def _save_perception(self, content_id: str, data: Dict) -> UUID:
        """Save reasoning structure to layered_perceptions table"""

        # Check if perception already exists
        existing = self.supabase.table('layered_perceptions')\
            .select('id')\
            .eq('content_id', content_id)\
            .execute().data

        perception_data = {
            'content_id': content_id,

            # New reasoning structure fields
            'mechanisms': data.get('mechanisms', []),
            'skipped_steps': data.get('skipped_steps', []),
            'actor': data.get('actor', {}),
            'logic_chain': data.get('logic_chain', []),
            'consistency_pattern': data.get('consistency_pattern', ''),

            # 3-layer structure (simplified to string arrays for V5+)
            'explicit_claims': data.get('explicit_claims', []),
            'implicit_assumptions': data.get('implicit_assumptions', []),
            'deep_beliefs': data.get('deep_beliefs', []),

            # Legacy fields (keep for backward compatibility but not used in V5+)
            'reasoning_gaps': data.get('reasoning_gaps', []),
            'worldview_hints': data.get('worldview_hints', '')
        }

        if existing:
            # Update existing
            result = self.supabase.table('layered_perceptions')\
                .update(perception_data)\
                .eq('id', existing[0]['id'])\
                .execute()
            return UUID(existing[0]['id'])
        else:
            # Insert new
            result = self.supabase.table('layered_perceptions')\
                .insert(perception_data)\
                .execute()

            if result.data:
                return UUID(result.data[0]['id'])
            else:
                raise Exception("Failed to save layered perception")

    async def extract_batch(self, contents: List[Dict], batch_size: int = 5) -> List[UUID]:
        """
        Extract reasoning structures from multiple contents in parallel

        Args:
            contents: List of content dicts
            batch_size: Number of parallel GPT requests

        Returns:
            List of created perception IDs
        """
        import asyncio

        print(f"\n총 {len(contents)}개 글 추론 구조 분석 시작 (병렬 {batch_size}개)...")

        perception_ids = []

        # Process in batches to respect API rate limits
        for batch_start in range(0, len(contents), batch_size):
            batch = contents[batch_start:batch_start + batch_size]

            print(f"\n배치 {batch_start//batch_size + 1}/{(len(contents)-1)//batch_size + 1}")

            # Run batch in parallel
            tasks = [self.extract(content) for content in batch]

            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        print(f"  ❌ {batch[i].get('title', '')[:40]}: {result}")
                    else:
                        perception_ids.append(result)
                        print(f"  ✓ {batch[i].get('title', '')[:40]}")

            except Exception as e:
                print(f"\n  ❌ 배치 오류: {e}")
                continue

            # Rate limiting
            await asyncio.sleep(1)

        print(f"\n\n✅ {len(perception_ids)}개 분석 완료")

        return perception_ids

    async def extract_all_new(self, limit: int = None) -> List[UUID]:
        """
        Extract reasoning structures from all contents that don't have one yet

        Args:
            limit: Max number to process (None = all)

        Returns:
            List of created perception IDs
        """

        # Get contents without reasoning structure
        # (contents that don't have a layered_perception or have one without mechanisms field)
        all_contents = self.supabase.table('contents')\
            .select('id, title, body')\
            .neq('body', '')\
            .execute().data

        # Filter out contents that already have reasoning structure
        existing_perception_content_ids = set()
        perceptions = self.supabase.table('layered_perceptions')\
            .select('content_id, mechanisms')\
            .execute().data

        for p in perceptions:
            # Only skip if mechanisms field exists and is not empty
            if p.get('mechanisms') and len(p.get('mechanisms', [])) > 0:
                existing_perception_content_ids.add(p['content_id'])

        contents_to_process = [
            c for c in all_contents
            if c['id'] not in existing_perception_content_ids
        ]

        if limit:
            contents_to_process = contents_to_process[:limit]

        print(f"전체: {len(all_contents)}개")
        print(f"이미 분석됨: {len(existing_perception_content_ids)}개")
        print(f"처리 대상: {len(contents_to_process)}개")

        if not contents_to_process:
            print("처리할 content가 없습니다.")
            return []

        return await self.extract_batch(contents_to_process)
