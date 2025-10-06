"""
Simplified Worldview Detector
연결 관계 없이 GPT를 사용해 perceptions를 직접 클러스터링하고 worldview 탐지
"""

import logging
from typing import Dict, List
from uuid import UUID, uuid4
from datetime import datetime
import json
import os
from openai import AsyncOpenAI

from engines.utils.supabase_client import get_supabase
from engines.utils.embedding_utils import EmbeddingGenerator

logger = logging.getLogger(__name__)

class SimpleWorldviewDetector:
    """GPT 기반 단순 worldview 탐지"""

    def __init__(self):
        self.supabase = get_supabase()
        self.openai = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.embedding_generator = EmbeddingGenerator()

    async def detect_worldviews(self) -> List[UUID]:
        """모든 perception을 분석하여 worldview 패턴 탐지"""

        # Get all perceptions
        response = self.supabase.table('perceptions').select('*').execute()
        perceptions = response.data

        if len(perceptions) < 3:
            logger.warning(f"Not enough perceptions ({len(perceptions)}) to detect worldviews")
            return []

        logger.info(f"Analyzing {len(perceptions)} perceptions for worldview patterns...")

        # Call GPT to find worldview patterns
        worldviews_data = await self._analyze_with_gpt(perceptions)

        if not worldviews_data or not worldviews_data.get('worldviews'):
            logger.warning("No worldviews detected by GPT")
            return []

        # Save worldviews
        worldview_ids = []
        for wv_data in worldviews_data['worldviews']:
            wv_id = await self._save_worldview(wv_data, perceptions)
            if wv_id:
                worldview_ids.append(wv_id)

        logger.info(f"Detected {len(worldview_ids)} worldviews")
        return worldview_ids

    async def _analyze_with_gpt(self, perceptions: List[Dict]) -> Dict:
        """GPT로 worldview 패턴 분석"""

        # Prepare perception summary for GPT
        perception_summary = []
        for i, p in enumerate(perceptions[:30], 1):  # Max 30 for token limit
            perception_summary.append(
                f"{i}. {p['perceived_subject']} = {p['perceived_attribute']}\n"
                f"   주장: {', '.join(p.get('claims', []))[:100]}"
            )

        prompt = f"""다음은 DC 갤러리 정치 글에서 추출한 인식(perception) 목록입니다.

{chr(10).join(perception_summary)}

이 인식들을 분석하여 **공통된 세계관(worldview) 패턴**을 찾아주세요.

세계관 기준:
- 같은 대상을 비슷하게 인식하는 패턴
- 공통된 프레임이나 관점
- 최소 3개 이상의 연관된 인식

응답 형식 (JSON):
{{
  "worldviews": [
    {{
      "title": "세계관 제목",
      "frame": "핵심 프레임 (X = Y 형식)",
      "core_subject": "핵심 대상",
      "core_attributes": ["속성1", "속성2"],
      "perception_indices": [관련된 perception 번호들],
      "description": "세계관 설명"
    }}
  ]
}}

**중요: 중복된 세계관을 만들지 마세요. 유사한 패턴은 하나로 통합하세요.**
"""

        try:
            response = await self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 정치 담론 패턴을 분석하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=3000
            )

            result = json.loads(response.choices[0].message.content)
            logger.info(f"GPT detected {len(result.get('worldviews', []))} worldviews")
            return result

        except Exception as e:
            logger.error(f"GPT analysis failed: {e}")
            return {}

    async def _save_worldview(self, wv_data: Dict, all_perceptions: List[Dict]) -> UUID:
        """Worldview를 DB에 저장"""

        try:
            # Get related perceptions by indices
            perception_indices = wv_data.get('perception_indices', [])
            related_perceptions = []

            for idx in perception_indices:
                if 0 < idx <= len(all_perceptions):
                    related_perceptions.append(all_perceptions[idx - 1])

            if len(related_perceptions) < 2:
                logger.warning(f"Worldview '{wv_data['title']}' has less than 2 perceptions, skipping")
                return None

            # Calculate stats
            perception_ids = [p['id'] for p in related_perceptions]
            content_ids = list(set([p['content_id'] for p in related_perceptions]))

            # Generate embedding
            embedding_text = f"{wv_data['title']} {wv_data['frame']} {wv_data.get('description', '')}"
            embedding = await self.embedding_generator.generate(embedding_text)

            # Create worldview
            worldview_id = uuid4()
            worldview = {
                'id': str(worldview_id),
                'title': wv_data['title'],
                'frame': wv_data['frame'],
                'description': wv_data.get('description', ''),
                'core_subject': wv_data.get('core_subject', ''),
                'core_attributes': wv_data.get('core_attributes', []),
                'overall_valence': 'neutral',
                'perception_ids': perception_ids,
                'total_perceptions': len(related_perceptions),
                'total_contents': len(content_ids),
                'worldview_embedding': embedding,
                'strength_cognitive': 0.5,
                'strength_temporal': 0,
                'strength_social': 0,
                'strength_structural': 0,
                'strength_overall': 0.5,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            self.supabase.table('worldviews').insert(worldview).execute()
            logger.info(f"Saved worldview: {wv_data['title']} ({len(related_perceptions)} perceptions)")

            return worldview_id

        except Exception as e:
            logger.error(f"Error saving worldview: {e}")
            return None
