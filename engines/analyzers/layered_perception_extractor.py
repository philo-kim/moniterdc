"""
LayeredPerceptionExtractor - 3층 구조 분석

각 글을 3개 층위로 분석:
1. 표면층 (Explicit): 명시적 주장
2. 암묵층 (Implicit): 전제하는 사고
3. 심층 (Deep): 무의식적 믿음

v2.1: Fast filter 통합
- explicit_claims 추출 후 품질 필터링
- 필터링된 좋은 claims만으로 implicit/deep 재추출
"""

from anthropic import Anthropic
import os
import json
import asyncio
from typing import Dict, List, Tuple
from uuid import UUID
from engines.utils.supabase_client import get_supabase

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

class LayeredPerceptionExtractor:
    """Extract 3-layer perception from content with quality filtering"""

    def __init__(self):
        self.supabase = get_supabase()

    def _fast_filter_claim(self, claim_text: str) -> Tuple[bool, str]:
        """
        Filter low-quality explicit claims

        Same logic as PatternManager._fast_filter_surface()

        Returns:
            (should_keep, reason_if_filtered)
        """
        # Handle both string and dict formats
        if isinstance(claim_text, dict):
            # Extract predicate or combine subject + predicate
            text = claim_text.get('predicate', '')
            if not text and 'subject' in claim_text:
                text = f"{claim_text.get('subject', '')} {claim_text.get('predicate', '')}"
        else:
            text = claim_text

        text_clean = str(text).strip()

        # 1. 길이 체크
        if len(text_clean) < 10:
            return (False, "길이 < 10")

        # 2. 지시대명사로 시작
        pronouns_start = [
            '이는 ', '이는,', '이것은 ', '이것이 ', '그것은 ', '그것이 ',
            '여기는 ', '거기는 ', '저기는 '
        ]
        for p in pronouns_start:
            if text_clean.startswith(p):
                return (False, "지시대명사 시작")

        if text_clean.startswith('이 ') or text_clean.startswith('그 ') or text_clean.startswith('저 '):
            if not any(text_clean.startswith(p) for p in ['이 사건', '이 사람', '이 일', '그 사건', '그 사람']):
                return (False, "지시대명사 시작")

        # 3. 막연한 주어
        vague_subjects = [
            '우리가 ', '우리는 ', '이들은 ', '이들이 ', '그들은 ', '그들이 ',
            '엄마들이 ', '좌파들이 ', '보수들이 ', '사람들이 '
        ]
        for s in vague_subjects:
            if text_clean.startswith(s):
                return (False, "막연한 주어")

        # 4. 당위문
        normative = ['해야 한다', '해야한다', '하자', '드리자', '말아야', '되어야']
        for n in normative:
            if n in text_clean:
                return (False, "당위문")

        # 5. 막연한 평가
        vague_eval = ['웃기다', '다행', '부당', '적절', '나쁜', '좋은',
                      '이상하다', '복잡하다', '어렵다', '쉽다']

        concrete_subjects = ['민주당', '국민의힘', '윤석열', '이재명',
                            '경찰', '검찰', '법원', '정부', '국회',
                            '대통령', '의원', '장관', '판사', '검사']

        has_concrete_subject = any(subj in text_clean for subj in concrete_subjects)

        if not has_concrete_subject:
            for v in vague_eval:
                if v in text_clean:
                    return (False, "막연한 평가")

        # 6. 불완전한 문장
        endings = ['다.', '다,', '다"', '다\'', '다!', '다?',
                   '까.', '까,', '까?', '냐.', '냐,', '냐?',
                   '요.', '요,', '요!', '음.', '음,']

        has_ending = any(text_clean.endswith(end) for end in endings)

        if not has_ending and not text_clean.endswith('다'):
            return (False, "불완전한 문장")

        # 7. 자음 이니셜
        korean_consonants = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
        if any(c in korean_consonants for c in text_clean[:3]):
            return (False, "자음 이니셜")

        return (True, "")

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

## 1. 표면층 (Explicit Layer) - 명시적 주장
글에서 직접 말하고 있는 것

## 2. 암묵층 (Implicit Layer) - 전제하는 사고
말하지 않았지만 당연하게 여기는 것

## 3. 심층 (Deep Layer) - 무의식적 믿음
이 글쓴이 진영만의 세계관

JSON 형식:
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

        # Claude Sonnet 4.5 (Baseline 프롬프트 - "Less is More")
        # Run in thread pool to make it async
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
