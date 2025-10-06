#!/usr/bin/env python3
"""
FlawDetector - 구조적 허점 감지

세계관의 논리적 오류와 구조적 약점을 심층 분석
"""

import os
import json
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from engines.utils.supabase_client import get_supabase
from engines.utils.logger import get_logger

logger = get_logger(__name__)


class FlawDetector:
    """
    Detect structural flaws in worldviews using GPT-4 analysis

    Detects:
    1. Term Ambiguity (용어 모호성)
    2. Logical Leap (논리 비약)
    3. False Dichotomy (이분법/흑백논리)
    4. Selective Facts (선택적 사실)
    5. Causal Reversal (인과 역전)
    6. Ad Hominem (인신공격)
    7. Hasty Generalization (성급한 일반화)
    """

    def __init__(self):
        self.supabase = get_supabase()
        self.openai = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    async def detect_flaws(self, worldview: Dict, perceptions: List[Dict]) -> List[Dict]:
        """
        Detect all structural flaws in a worldview

        Args:
            worldview: Worldview dict
            perceptions: List of perception dicts

        Returns:
            List of detected flaws with details
        """
        try:
            flaws = []

            # 1. Rule-based detection (fast)
            rule_based_flaws = self._detect_rule_based(worldview, perceptions)
            flaws.extend(rule_based_flaws)

            # 2. GPT-4 deep analysis (slow but thorough)
            gpt_flaws = await self._detect_with_gpt(worldview, perceptions)
            flaws.extend(gpt_flaws)

            # Deduplicate
            flaws = self._deduplicate_flaws(flaws)

            logger.info(f"Detected {len(flaws)} structural flaws for worldview {worldview.get('title')}")
            return flaws

        except Exception as e:
            logger.error(f"Error detecting flaws: {e}")
            return []

    def _detect_rule_based(self, worldview: Dict, perceptions: List[Dict]) -> List[Dict]:
        """
        Rule-based flaw detection (fast heuristics)

        Args:
            worldview: Worldview dict
            perceptions: List of perception dicts

        Returns:
            List of detected flaws
        """
        flaws = []

        # 1. Term Ambiguity - check for vague terms
        vague_terms = self._detect_term_ambiguity(worldview, perceptions)
        if vague_terms:
            flaws.append({
                'type': 'term_ambiguity',
                'name': '용어 모호성',
                'description': '핵심 용어의 정의가 불명확하여 자의적 해석 가능',
                'terms': vague_terms,
                'severity': 'high',
                'counter': f"'{', '.join(vague_terms[:3])}'의 명확한 정의를 요구하세요"
            })

        # 2. Overgeneralization - too few perceptions for strong claims
        if len(perceptions) < 5 and worldview.get('strength_overall', 0) > 0.7:
            flaws.append({
                'type': 'hasty_generalization',
                'name': '성급한 일반화',
                'description': f'단 {len(perceptions)}개 사례로 강한 주장',
                'evidence_count': len(perceptions),
                'severity': 'high',
                'counter': '더 많은 사례와 통계적 근거를 요구하세요'
            })

        # 3. Echo chamber - all same valence
        valences = [p.get('perceived_valence') for p in perceptions]
        if valences and len(set(valences)) == 1:
            flaws.append({
                'type': 'selective_facts',
                'name': '선택적 사실 제시',
                'description': '모든 정보가 한쪽 방향으로만 편향',
                'valence': valences[0],
                'severity': 'high',
                'counter': '반대 증거와 다양한 관점을 요구하세요'
            })

        # 4. Missing sources - no credible sources
        has_sources = any(
            p.get('metadata', {}).get('source_credibility', 0) > 0.5
            for p in perceptions
        )
        if not has_sources:
            flaws.append({
                'type': 'missing_evidence',
                'name': '증거 부족',
                'description': '검증 가능한 출처나 데이터 없이 주장만 반복',
                'severity': 'medium',
                'counter': '구체적인 출처와 데이터를 요구하세요'
            })

        return flaws

    def _detect_term_ambiguity(self, worldview: Dict, perceptions: List[Dict]) -> List[str]:
        """
        Detect ambiguous terms

        Args:
            worldview: Worldview dict
            perceptions: List of perceptions

        Returns:
            List of ambiguous terms
        """
        # Common ambiguous terms in Korean political discourse
        AMBIGUOUS_TERMS = [
            '친중', '친북', '좌파', '우파', '민주', '자유',
            '독재', '민주주의', '빨갱이', '토착왜구',
            '매국노', '애국', '친일', '종북'
        ]

        found_terms = []

        # Check in title and frame
        title = worldview.get('title', '')
        frame = worldview.get('frame', '')

        for term in AMBIGUOUS_TERMS:
            if term in title or term in frame:
                found_terms.append(term)

        # Check in perceptions
        for p in perceptions:
            attr = p.get('perceived_attribute', '')
            for term in AMBIGUOUS_TERMS:
                if term in attr and term not in found_terms:
                    found_terms.append(term)

        return found_terms

    async def _detect_with_gpt(self, worldview: Dict, perceptions: List[Dict]) -> List[Dict]:
        """
        Deep flaw analysis using GPT-4

        Args:
            worldview: Worldview dict
            perceptions: List of perceptions

        Returns:
            List of detected flaws
        """
        try:
            # Prepare perception summary
            perception_summary = self._summarize_perceptions(perceptions[:10])  # Limit to 10 for token efficiency

            prompt = f"""다음 세계관의 논리적 오류와 구조적 약점을 분석하세요.

세계관: {worldview.get('title')}
프레임: {worldview.get('frame')}
주체: {worldview.get('core_subject')}
속성: {', '.join(worldview.get('core_attributes', []))}

구성 인식들:
{perception_summary}

다음 항목을 검토하여 발견된 오류만 JSON으로 반환하세요:

1. **논리 비약 (Logical Leap)**: A에서 B로의 논리적 연결이 약한가?
2. **이분법 (False Dichotomy)**: A 아니면 B라는 극단적 이분법인가?
3. **인과 역전 (Causal Reversal)**: 원인과 결과가 뒤바뀐 것은 없는가?
4. **인신공격 (Ad Hominem)**: 논리 대신 인신공격을 사용하는가?
5. **순환논증 (Circular Reasoning)**: 결론이 전제에 포함되어 있는가?

JSON 형식 (발견된 것만):
{{
  "flaws": [
    {{
      "type": "logical_leap",
      "name": "논리 비약",
      "description": "구체적 설명",
      "from": "전제",
      "to": "결론",
      "severity": "high|medium|low",
      "counter": "반박 방법"
    }}
  ]
}}

오류가 없으면 빈 배열을 반환하세요."""

            response = await self.openai.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {
                        'role': 'system',
                        'content': '당신은 논리적 오류를 분석하는 전문가입니다. 객관적이고 정확하게 분석하세요.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.3,
                response_format={'type': 'json_object'}
            )

            result = json.loads(response.choices[0].message.content)
            flaws = result.get('flaws', [])

            logger.info(f"GPT detected {len(flaws)} flaws")
            return flaws

        except Exception as e:
            logger.error(f"Error in GPT flaw detection: {e}")
            return []

    def _summarize_perceptions(self, perceptions: List[Dict]) -> str:
        """
        Summarize perceptions for GPT prompt

        Args:
            perceptions: List of perceptions

        Returns:
            Formatted string
        """
        lines = []
        for i, p in enumerate(perceptions, 1):
            subject = p.get('perceived_subject', '')
            attribute = p.get('perceived_attribute', '')
            valence = p.get('perceived_valence', '')
            lines.append(f"{i}. {subject} → {attribute} ({valence})")

        return '\n'.join(lines)

    def _deduplicate_flaws(self, flaws: List[Dict]) -> List[Dict]:
        """
        Remove duplicate flaws

        Args:
            flaws: List of flaws

        Returns:
            Deduplicated list
        """
        seen = set()
        unique = []

        for flaw in flaws:
            key = flaw['type']
            if key not in seen:
                seen.add(key)
                unique.append(flaw)

        return unique

    async def analyze_worldview_flaws(self, worldview_id: str) -> List[Dict]:
        """
        Analyze flaws for a specific worldview (convenience method)

        Args:
            worldview_id: Worldview UUID

        Returns:
            List of detected flaws
        """
        try:
            # Get worldview
            response = self.supabase.table('worldviews')\
                .select('*')\
                .eq('id', worldview_id)\
                .execute()

            if not response.data:
                logger.error(f"Worldview {worldview_id} not found")
                return []

            worldview = response.data[0]

            # Get perceptions
            perception_ids = worldview.get('perception_ids', [])
            if not perception_ids:
                return []

            response = self.supabase.table('perceptions')\
                .select('*')\
                .in_('id', perception_ids)\
                .execute()

            perceptions = response.data

            # Detect flaws
            flaws = await self.detect_flaws(worldview, perceptions)

            return flaws

        except Exception as e:
            logger.error(f"Error analyzing worldview flaws: {e}")
            return []
