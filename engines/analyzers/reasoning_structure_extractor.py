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

from openai import AsyncOpenAI
import os
import json
from typing import Dict, List
from uuid import UUID
from engines.utils.supabase_client import get_supabase

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))


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
다음은 DC Gallery 정치 글의 추론 구조 분석 결과입니다:

제목: {content['title']}
내용: {content['body'][:2000]}

---

이 글의 **추론 구조**를 분석해주세요:

1. **추론 메커니즘** (해당되는 것 모두):
   - 즉시_단정: 관찰 → (중간 과정 생략) → 결론
   - 필연적_인과: X → 반드시/곧/필연적으로 → Y
   - 표면_부정: 표면은 X / 실제는 Y
   - 역사_투사: 과거 패턴 → 현재 반복
   - 네트워크_추론: 연결 → 조직적 공모

2. **생략된 추론 단계** (무엇을 검증하지 않았나?):
   - 예: 정보 출처 탐색, 합법 가능성, 직접 증거 등

3. **행위자 규정**:
   - 주체: 누가 행동하는가?
   - 목적: 왜 그렇게 한다고 보는가?
   - 방법: 어떤 수단을 쓴다고 보는가?

4. **논리 체인** (관찰 → ... → 결론):
   - Step 1: 구체적 관찰
   - Step 2, 3, ...: 중간 추론 (있다면)
   - Final: 최종 결론

5. **일관성 패턴** (이 글의 핵심 논리를 한 줄로):
   - 예: "정보_파악_불법_해석", "관찰_즉시_단정"

JSON 형식으로 출력:
{{
  "mechanisms": ["즉시_단정", ...],
  "skipped_steps": ["출처 탐색 안 함", ...],
  "actor": {{
    "subject": "민주당/좌파",
    "purpose": "권력 유지",
    "methods": ["사찰", "협박"]
  }},
  "logic_chain": [
    "정보 파악",
    "불법으로 단정",
    "독재 시도"
  ],
  "consistency_pattern": "정보_파악_불법_해석",

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
  "worldview_hints": "과거 독재 → 현재 재현, 좌파 = 독재 본성"
}}
"""

        try:
            response = await client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4o for speed (gpt-5 too slow)
                messages=[
                    {"role": "system", "content": "You are an expert in analyzing reasoning structures in political discourse. Always respond in valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)

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

            # Keep legacy fields for compatibility
            'explicit_claims': data.get('explicit_claims', []),
            'implicit_assumptions': data.get('implicit_assumptions', []),
            'reasoning_gaps': data.get('reasoning_gaps', []),
            'deep_beliefs': data.get('deep_beliefs', []),
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
