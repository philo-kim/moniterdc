"""
ContextGuideBuilder - 맥락 번역 가이드 생성기

목적:
- DC Gallery 글의 3-layer 분석을 주제별로 그룹화
- 여당 지지자들이 이해할 수 있도록 맥락을 정리
- "왜 저렇게 말하는지" 이해할 수 있는 번역 가이드

이것은 worldview 탐지가 아니라 **맥락 번역**입니다.
"""

from openai import AsyncOpenAI
import os
import json
from typing import Dict, List
from uuid import UUID
from engines.utils.supabase_client import get_supabase

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class ContextGuideBuilder:
    """Build context translation guides from layered perceptions"""

    def __init__(self):
        self.supabase = get_supabase()

    async def build_guides(self) -> List[UUID]:
        """
        Build context guides by clustering layered_perceptions by theme

        Returns:
            List of created guide IDs
        """

        # Get all layered_perceptions
        lps = self.supabase.table('layered_perceptions')\
            .select('id, content_id, deep_beliefs, worldview_hints, implicit_assumptions')\
            .execute().data

        print(f"\n총 {len(lps)}개 분석 결과를 주제별로 그룹화합니다...")

        # Cluster by theme using GPT
        guides = await self._cluster_by_theme(lps)

        # Save guides
        guide_ids = []
        for guide in guides:
            guide_id = await self._save_guide(guide)
            guide_ids.append(guide_id)

        print(f"\n✅ {len(guide_ids)}개 맥락 가이드 생성 완료")

        return guide_ids

    async def _cluster_by_theme(self, lps: List[Dict], max_themes: int = 10) -> List[Dict]:
        """
        Cluster layered_perceptions by thematic similarity

        Goal: Create 5-10 thematic groups that help ruling party supporters
        understand "why they talk this way"
        """

        # Extract key beliefs and hints
        belief_samples = []
        for lp in lps[:100]:  # Sample first 100 for clustering
            beliefs = lp.get('deep_beliefs', [])
            hint = lp.get('worldview_hints', '')
            assumptions = lp.get('implicit_assumptions', [])

            belief_samples.append({
                'id': lp['id'],
                'deep_beliefs': beliefs[:3],  # Top 3 beliefs
                'worldview_hints': hint,
                'implicit_assumptions': assumptions[:2]  # Top 2 assumptions
            })

        # Ask GPT to identify major themes
        prompt = f"""
다음은 DC Gallery 정치 글들의 분석 결과입니다.

샘플 {len(belief_samples)}개의 deep_beliefs와 worldview_hints를 보고,
**5-10개의 주요 테마**로 그룹화해주세요.

목적: 여당 지지자들이 "왜 저렇게 말하는지" 이해할 수 있도록 맥락을 정리

각 테마는:
1. **주제명** (예: "민주당=독재재현", "좌파=친중매국")
2. **핵심 프레임** (그들이 세상을 보는 렌즈)
3. **역사적 참조** (어떤 과거 사건을 현재에 투영하는가)
4. **핵심 가정** (무엇을 당연하게 여기는가)
5. **포함되는 belief IDs** (이 테마에 속하는 분석 결과 ID들)

샘플 데이터:
{json.dumps(belief_samples[:30], ensure_ascii=False, indent=2)}

JSON 형식으로 응답:
{{
  "themes": [
    {{
      "title": "민주당=독재재현",
      "frame": "현 정권은 과거 독재정권과 동일한 방식으로 권력을 남용한다",
      "historical_reference": "박정희/전두환 시대 사찰, 탄압",
      "core_assumptions": [
        "권력은 본질적으로 부패한다",
        "작은 월권이 전면적 독재로 발전한다"
      ],
      "perception_ids": ["uuid1", "uuid2", ...]
    }}
  ]
}}
"""

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in political discourse analysis. Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        themes = result.get('themes', [])

        # For each theme, collect ALL matching perceptions (not just sample)
        for theme in themes:
            theme['perception_ids'] = await self._find_matching_perceptions(theme, lps)

        return themes

    async def _find_matching_perceptions(self, theme: Dict, all_lps: List[Dict]) -> List[str]:
        """
        Find all perceptions that match this theme

        Uses semantic similarity of deep_beliefs
        """

        theme_keywords = theme['title'] + ' ' + theme['frame'] + ' ' + ' '.join(theme.get('core_assumptions', []))

        matching_ids = []

        for lp in all_lps:
            beliefs_text = ' '.join(lp.get('deep_beliefs', []))
            hint_text = lp.get('worldview_hints', '')

            # Simple keyword matching for now
            # TODO: Use vector similarity for better matching
            combined_text = beliefs_text + ' ' + hint_text

            # Check if theme keywords overlap
            if any(keyword in combined_text for keyword in theme['title'].split('=')):
                matching_ids.append(lp['id'])

        return matching_ids

    async def _save_guide(self, theme: Dict) -> UUID:
        """
        Save context guide to database

        This creates a "translation guide" for ruling party supporters
        """

        guide = {
            'title': theme['title'],
            'frame': theme['frame'],
            'description': f"주제: {theme['title']}\n\n"
                         f"프레임: {theme['frame']}\n\n"
                         f"역사적 참조: {theme.get('historical_reference', 'N/A')}\n\n"
                         f"핵심 가정:\n" + '\n'.join(f"- {a}" for a in theme.get('core_assumptions', [])),

            # Link to layered_perceptions (store as JSONB metadata)
            'perception_ids': theme.get('perception_ids', []),
            'total_perceptions': len(theme.get('perception_ids', [])),

            # Store theme metadata
            'core_subject': theme['title'].split('=')[0] if '=' in theme['title'] else theme['title'],
            'core_attributes': theme.get('core_assumptions', []),
            'overall_valence': 'negative',  # Most DC Gallery themes are negative
        }

        # Insert into worldviews table (reusing structure for context guides)
        result = self.supabase.table('worldviews').insert(guide).execute()

        if result.data:
            return UUID(result.data[0]['id'])
        else:
            raise Exception(f"Failed to save guide: {theme['title']}")
