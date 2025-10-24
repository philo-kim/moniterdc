"""
LayeredPerceptionExtractor v2.1 - With Quality Filtering

2-stage extraction process:
1. Extract explicit_claims from content
2. Filter out low-quality claims
3. Re-extract implicit/deep layers based on filtered claims only

This ensures implicit and deep layers are based on high-quality surface claims only.
"""

from anthropic import Anthropic
import os
import json
import asyncio
from typing import Dict, List, Tuple
from uuid import UUID
from engines.utils.supabase_client import get_supabase

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


class LayeredPerceptionExtractorV2:
    """Extract 3-layer perception with quality filtering"""

    def __init__(self):
        self.supabase = get_supabase()

    def _fast_filter_claim(self, claim_text: str) -> Tuple[bool, str]:
        """Filter low-quality explicit claims"""
        # Handle both string and dict formats
        if isinstance(claim_text, dict):
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

    async def extract(self, content: Dict) -> Dict:
        """
        2-stage extraction with filtering

        Stage 1: Extract explicit claims
        Stage 2: Filter claims + Re-extract implicit/deep based on filtered claims

        Returns:
            Perception dict with filtered data + stats
        """
        # ========== Stage 1: Extract explicit claims ==========
        prompt_stage1 = f"""
다음은 DC Gallery 정치 갤러리의 글입니다:

제목: {content['title']}
내용: {content['body'][:2000]}

이 글의 **표면층 (Explicit Layer)**만 추출하세요.
글에서 직접 말하고 있는 명시적 주장들을 추출하세요.

JSON 형식:
{{
  "explicit_claims": [
    "민주당이 통신사를 협박해 개인정보를 불법 취득했다",
    "계엄은 평화적으로 이루어졌다"
  ]
}}
"""

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                temperature=0,
                messages=[{"role": "user", "content": prompt_stage1}]
            )
        )

        response_text = response.content[0].text

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

        result_stage1 = json.loads(json_str)

        # ========== Filter explicit claims ==========
        all_claims = result_stage1.get('explicit_claims', [])
        filtered_claims = []
        filter_stats = {'total': len(all_claims), 'kept': 0, 'filtered': 0}

        for claim in all_claims:
            should_keep, reason = self._fast_filter_claim(claim)
            if should_keep:
                filtered_claims.append(claim)
                filter_stats['kept'] += 1
            else:
                filter_stats['filtered'] += 1

        # If no claims left after filtering, return empty perception
        if len(filtered_claims) == 0:
            return {
                'content_id': content['id'],
                'explicit_claims': [],
                'implicit_assumptions': [],
                'reasoning_gaps': [],
                'deep_beliefs': [],
                'worldview_hints': '',
                'filter_stats': filter_stats
            }

        # ========== Stage 2: Re-extract implicit/deep based on filtered claims ==========
        filtered_claims_text = "\n".join([f"- {c}" for c in filtered_claims])

        prompt_stage2 = f"""
다음은 한 글의 명시적 주장들입니다:

{filtered_claims_text}

이 주장들을 기반으로 **암묵층**과 **심층**을 분석하세요:

## 암묵층 (Implicit Layer)
말하지 않았지만 당연하게 전제하는 사고

## 심층 (Deep Layer)
이 진영만의 무의식적 세계관

JSON 형식:
{{
  "implicit_assumptions": [
    "민주당은 통신사를 협박해서 사찰용 정보를 얻는다"
  ],
  "reasoning_gaps": [
    {{
      "from": "유심교체 정보를 알았다",
      "to": "통신사 협박으로 얻었다",
      "gap": "정상적 방법 가능성 배제하고 즉시 불법으로 단정"
    }}
  ],
  "deep_beliefs": [
    "민주당/좌파는 과거 독재정권처럼 사찰로 반대파를 제거한다"
  ],
  "worldview_hints": "과거 독재 → 현재 재현"
}}
"""

        response2 = await loop.run_in_executor(
            None,
            lambda: client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                temperature=0,
                messages=[{"role": "user", "content": prompt_stage2}]
            )
        )

        response_text2 = response2.content[0].text

        # Parse JSON
        if "```json" in response_text2:
            json_start = response_text2.find("```json") + 7
            json_end = response_text2.find("```", json_start)
            json_str = response_text2[json_start:json_end].strip()
        elif "{" in response_text2:
            json_start = response_text2.find("{")
            json_end = response_text2.rfind("}") + 1
            json_str = response_text2[json_start:json_end]
        else:
            json_str = response_text2

        result_stage2 = json.loads(json_str)

        # ========== Combine results ==========
        perception = {
            'content_id': content['id'],
            'explicit_claims': filtered_claims,  # Filtered claims only
            'implicit_assumptions': result_stage2.get('implicit_assumptions', []),
            'reasoning_gaps': result_stage2.get('reasoning_gaps', []),
            'deep_beliefs': result_stage2.get('deep_beliefs', []),
            'worldview_hints': result_stage2.get('worldview_hints', ''),
            'filter_stats': filter_stats
        }

        return perception

    async def save_perception(self, perception: Dict) -> UUID:
        """Save perception to database"""
        # Remove filter_stats before saving
        filter_stats = perception.pop('filter_stats', None)

        result = self.supabase.table('layered_perceptions').insert(perception).execute()

        if result.data:
            return UUID(result.data[0]['id'])
        else:
            raise Exception("Failed to save layered perception")

    async def extract_and_save(self, content: Dict) -> Tuple[UUID, Dict]:
        """Extract and save perception, return ID and filter stats"""
        perception = await self.extract(content)
        filter_stats = perception.get('filter_stats', {})
        perception_id = await self.save_perception(perception)

        return perception_id, filter_stats
