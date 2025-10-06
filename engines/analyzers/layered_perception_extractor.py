"""
LayeredPerceptionExtractor - 3층 구조 분석

각 글을 3개 층위로 분석:
1. 표면층 (Explicit): 명시적 주장
2. 암묵층 (Implicit): 전제하는 사고
3. 심층 (Deep): 무의식적 믿음
"""

from openai import AsyncOpenAI
import os
import json
from typing import Dict, List
from uuid import UUID
from engines.utils.supabase_client import get_supabase

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class LayeredPerceptionExtractor:
    """Extract 3-layer perception from content"""

    def __init__(self):
        self.supabase = get_supabase()

    async def extract(self, content: Dict) -> UUID:
        """
        Extract layered perception from a single content

        Args:
            content: Content dict with title and body

        Returns:
            UUID of created layered_perception
        """

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

JSON 형식:
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

        # GPT-5 only (no fallback as requested)
        response = await client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are an expert in discourse analysis. Always respond in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Save to DB
        perception_id = await self._save_perception(content['id'], result)

        return perception_id

    async def _save_perception(self, content_id: str, data: Dict) -> UUID:
        """Save layered perception to database"""

        perception = {
            'content_id': content_id,
            'explicit_claims': data.get('explicit_claims', []),
            'implicit_assumptions': data.get('implicit_assumptions', []),
            'reasoning_gaps': data.get('reasoning_gaps', []),
            'deep_beliefs': data.get('deep_beliefs', []),
            'worldview_hints': data.get('worldview_hints', '')
        }

        result = self.supabase.table('layered_perceptions').insert(perception).execute()

        if result.data:
            return UUID(result.data[0]['id'])
        else:
            raise Exception("Failed to save layered perception")

    async def extract_all(self, limit: int = None, batch_size: int = 10) -> List[UUID]:
        """
        Extract layered perceptions from all contents

        Args:
            limit: Max number of contents to process (None = all)
            batch_size: Number of parallel requests (default 10)

        Returns:
            List of created perception IDs
        """
        import asyncio

        # Get contents without layered_perception
        query = self.supabase.table('contents')\
            .select('id, title, body')\
            .neq('body', '')

        if limit:
            query = query.limit(limit)

        contents = query.execute().data

        print(f"\n총 {len(contents)}개 글 분석 시작 (병렬 {batch_size}개)...")

        perception_ids = []

        # Process in batches
        for batch_start in range(0, len(contents), batch_size):
            batch = contents[batch_start:batch_start + batch_size]

            print(f"\n배치 {batch_start//batch_size + 1}/{(len(contents)-1)//batch_size + 1}")

            # Run batch in parallel
            tasks = []
            for content in batch:
                tasks.append(self.extract(content))

            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        print(f"  ❌ {batch[i]['title'][:40]}: {result}")
                    else:
                        perception_ids.append(result)
                        print(f"  ✓ {batch[i]['title'][:40]}")

            except Exception as e:
                print(f"\n  ❌ 배치 오류: {e}")
                continue

        print(f"\n\n✅ {len(perception_ids)}개 분석 완료")

        return perception_ids
