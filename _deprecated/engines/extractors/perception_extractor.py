"""
Perception Extractor - Layer 2 Engine
Analyzes content and extracts perceptions (subject, attribute, valence, claims, emotions)
"""

import os
import json
import logging
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime
from openai import AsyncOpenAI

from engines.utils.supabase_client import get_supabase
from engines.utils.embedding_utils import EmbeddingGenerator

logger = logging.getLogger(__name__)

class PerceptionExtractor:
    """Extracts perceptions from content using GPT-4"""

    def __init__(self):
        self.supabase = get_supabase()
        self.openai = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.embedding_generator = EmbeddingGenerator()

        # GPT prompt for perception extraction
        self.system_prompt = """당신은 정치 콘텐츠를 분석하여 인식(perception)을 추출하는 전문가입니다.

주어진 콘텐츠를 분석하여 다음을 추출하세요:

1. **perceived_subject**: 누구/무엇에 대한 이야기인가? (예: "민주당", "이재명", "윤석열 정부")
2. **perceived_attribute**: 어떤 속성/특성을 부여하는가? (예: "무능함", "친중", "독재적")
3. **perceived_valence**: 긍정/부정/중립 (positive/negative/neutral)
4. **claims**: 구체적인 주장들 (배열)
5. **keywords**: 핵심 키워드들 (배열)
6. **emotions**: 감정 표현들 (배열, 예: ["분노", "조롱", "불안"])

응답은 반드시 JSON 형식으로 하되, 하나의 콘텐츠에서 여러 인식이 추출될 수 있습니다.

예시:
{
  "perceptions": [
    {
      "perceived_subject": "민주당",
      "perceived_attribute": "친중 성향",
      "perceived_valence": "negative",
      "claims": ["중국 편을 든다", "국익을 해친다"],
      "keywords": ["민주당", "친중", "배신"],
      "emotions": ["분노", "배신감"]
    }
  ]
}
"""

    async def extract(self, content_id: UUID) -> List[UUID]:
        """
        Extract perceptions from a content item

        Args:
            content_id: UUID of the content to analyze

        Returns:
            List of created perception UUIDs
        """
        try:
            # Fetch content from database
            response = self.supabase.table('contents').select('*').eq('id', str(content_id)).execute()

            if not response.data:
                logger.error(f"Content not found: {content_id}")
                return []

            content = response.data[0]

            # Skip if no body
            if not content.get('body'):
                logger.warning(f"Content has no body: {content_id}")
                return []

            # Call GPT to extract perceptions
            perceptions_data = await self._call_gpt(content)

            if not perceptions_data or not perceptions_data.get('perceptions'):
                logger.warning(f"No perceptions extracted from content: {content_id}")
                return []

            # Save perceptions to database
            perception_ids = []
            for perception in perceptions_data['perceptions']:
                perception_id = await self._save_perception(content_id, content, perception)
                if perception_id:
                    perception_ids.append(perception_id)

            logger.info(f"Extracted {len(perception_ids)} perceptions from content {content_id}")
            return perception_ids

        except Exception as e:
            logger.error(f"Error extracting perceptions from {content_id}: {e}")
            return []

    async def _call_gpt(self, content: Dict) -> Optional[Dict]:
        """Call LLM (Claude or GPT-4) to analyze content and extract perceptions"""
        try:
            title = content.get('title', '')
            body = content.get('body', '')
            text = f"제목: {title}\n\n내용: {body}"

            # Truncate if too long
            if len(text) > 8000:
                text = text[:8000] + "..."

            # Use OpenAI GPT-4
            response = await self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return None

    async def _save_perception(self, content_id: UUID, content: Dict, perception: Dict) -> Optional[UUID]:
        """Save a single perception to database with embedding"""
        try:
            # Generate text for embedding
            subject = perception.get('perceived_subject', '')
            attribute = perception.get('perceived_attribute', '')
            claims = perception.get('claims', [])
            embedding_text = f"{subject} {attribute} {' '.join(claims)}"

            # Generate embedding
            embedding = await self.embedding_generator.generate(embedding_text)

            # Prepare perception data
            perception_data = {
                'content_id': str(content_id),
                'perceived_subject': subject,
                'perceived_attribute': attribute,
                'perceived_valence': perception.get('perceived_valence', 'neutral'),
                'claims': perception.get('claims', []),
                'keywords': perception.get('keywords', []),
                'emotions': perception.get('emotions', []),
                'perception_embedding': embedding,
                'credibility': content.get('base_credibility', 0.5),
                'confidence': 0.7,  # Default confidence
            }

            # Insert into database
            response = self.supabase.table('perceptions').insert(perception_data).execute()

            if response.data:
                perception_id = response.data[0]['id']
                logger.info(f"Saved perception: {perception_id} (subject: {subject})")
                return UUID(perception_id)

            return None

        except Exception as e:
            logger.error(f"Error saving perception: {e}")
            return None

    async def batch_extract(self, content_ids: List[UUID]) -> Dict[UUID, List[UUID]]:
        """
        Extract perceptions from multiple contents

        Args:
            content_ids: List of content UUIDs

        Returns:
            Dictionary mapping content_id -> list of perception_ids
        """
        results = {}

        for content_id in content_ids:
            perception_ids = await self.extract(content_id)
            results[content_id] = perception_ids

        total_perceptions = sum(len(pids) for pids in results.values())
        logger.info(f"Batch extracted {total_perceptions} perceptions from {len(content_ids)} contents")

        return results
