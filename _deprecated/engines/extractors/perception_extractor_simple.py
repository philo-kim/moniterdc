"""
Simple Perception Extractor - Rule-based (for testing without API quota)
"""

import logging
import re
from typing import Dict, List, Optional
from uuid import UUID

from engines.utils.supabase_client import get_supabase
from engines.utils.embedding_utils import EmbeddingGenerator

logger = logging.getLogger(__name__)

class SimplePerceptionExtractor:
    """Rule-based perception extractor for testing"""

    def __init__(self):
        self.supabase = get_supabase()
        self.embedding_generator = EmbeddingGenerator()

        # 주요 정치 주체
        self.subjects = ["민주당", "이재명", "윤석열", "국민의힘", "정부", "야당", "여당"]

        # 부정적 속성 키워드
        self.negative_attributes = {
            "친중": ["중국", "짱깨", "시진핑"],
            "무능": ["무능", "멍청", "바보"],
            "독재": ["독재", "파쇼"],
            "부패": ["부패", "비리", "횡령"],
        }

        # 긍정적 속성 키워드
        self.positive_attributes = {
            "유능": ["능력", "실력", "성과"],
            "청렴": ["청렴", "깨끗"],
        }

    async def extract(self, content_id: UUID) -> List[UUID]:
        """Extract perceptions using simple rules"""
        try:
            # Fetch content
            response = self.supabase.table('contents').select('*').eq('id', str(content_id)).execute()

            if not response.data:
                logger.error(f"Content not found: {content_id}")
                return []

            content = response.data[0]
            text = f"{content.get('title', '')} {content.get('body', '')}"

            if not text.strip():
                return []

            # Extract perceptions
            perceptions = self._extract_perceptions(text)

            # Save to database
            perception_ids = []
            for perception in perceptions:
                pid = await self._save_perception(content_id, content, perception)
                if pid:
                    perception_ids.append(pid)

            logger.info(f"Extracted {len(perception_ids)} perceptions from {content_id}")
            return perception_ids

        except Exception as e:
            logger.error(f"Error extracting perceptions: {e}")
            return []

    def _extract_perceptions(self, text: str) -> List[Dict]:
        """Extract perceptions using keywords"""
        perceptions = []

        # Find subjects
        found_subjects = [s for s in self.subjects if s in text]

        if not found_subjects:
            found_subjects = ["정치권"]  # Default subject

        for subject in found_subjects:
            # Check negative attributes
            for attr, keywords in self.negative_attributes.items():
                if any(kw in text for kw in keywords):
                    perceptions.append({
                        "perceived_subject": subject,
                        "perceived_attribute": attr,
                        "perceived_valence": "negative",
                        "claims": [f"{subject}의 {attr} 관련 내용"],
                        "keywords": [kw for kw in keywords if kw in text],
                        "emotions": ["분노", "비판"]
                    })

            # Check positive attributes
            for attr, keywords in self.positive_attributes.items():
                if any(kw in text for kw in keywords):
                    perceptions.append({
                        "perceived_subject": subject,
                        "perceived_attribute": attr,
                        "perceived_valence": "positive",
                        "claims": [f"{subject}의 {attr} 관련 내용"],
                        "keywords": [kw for kw in keywords if kw in text],
                        "emotions": ["긍정", "지지"]
                    })

        # If no perceptions found, create a generic one
        if not perceptions:
            perceptions.append({
                "perceived_subject": "정치권",
                "perceived_attribute": "일반 정치 담론",
                "perceived_valence": "neutral",
                "claims": ["정치 관련 내용"],
                "keywords": self._extract_keywords(text),
                "emotions": []
            })

        return perceptions

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract simple keywords"""
        # Simple tokenization (just split by whitespace and take nouns)
        words = text.split()
        keywords = [w for w in words if len(w) >= 2 and len(w) <= 10]
        return keywords[:10]  # Top 10

    async def _save_perception(self, content_id: UUID, content: Dict, perception: Dict) -> Optional[UUID]:
        """Save perception to database"""
        try:
            subject = perception['perceived_subject']
            attribute = perception['perceived_attribute']
            claims = perception['claims']

            # Generate real embedding using OpenAI
            embedding_text = f"{subject} {attribute} {' '.join(claims)}"
            embedding = await self.embedding_generator.generate(embedding_text)

            perception_data = {
                'content_id': str(content_id),
                'perceived_subject': subject,
                'perceived_attribute': attribute,
                'perceived_valence': perception['perceived_valence'],
                'claims': claims,
                'keywords': perception['keywords'],
                'emotions': perception['emotions'],
                'perception_embedding': embedding,
                'credibility': content.get('base_credibility', 0.5),
                'confidence': 0.5,  # Lower confidence for rule-based
            }

            response = self.supabase.table('perceptions').insert(perception_data).execute()

            if response.data:
                pid = response.data[0]['id']
                logger.info(f"Saved perception: {pid}")
                return UUID(pid)

            return None

        except Exception as e:
            logger.error(f"Error saving perception: {e}")
            return None
