#!/usr/bin/env python3
"""
CounterNarrativeGenerator - 대안 내러티브 생성

왜곡된 세계관에 대한 대안적 관점과 반박 전략 생성
"""

import os
import json
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from engines.utils.supabase_client import get_supabase
from engines.utils.logger import get_logger

logger = get_logger(__name__)


class CounterNarrativeGenerator:
    """
    Generate counter-narratives and rebuttals using GPT-4

    Generates:
    1. Alternative narrative (same facts, different frame)
    2. Key rebuttal points (3-5 points)
    3. Suggested response (copyable text)
    4. Evidence requirements (what to ask for)
    """

    def __init__(self):
        self.supabase = get_supabase()
        self.openai = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    async def generate_from_worldview(self, worldview: Dict) -> Dict:
        """
        Generate counter-narrative directly from worldview data
        (without requiring perceptions)

        Args:
            worldview: Worldview dict with cognitive_mechanisms, formation_phases, etc.

        Returns:
            Counter-narrative dict
        """
        try:
            prompt = f"""
당신은 정치 담론 분석 및 팩트체크 전문가입니다.

다음은 DC Gallery 정치 갤러리에서 탐지된 왜곡된 세계관입니다:

제목: {worldview['title']}
전체 서사: {worldview.get('description', '')}

인과 구조:
{json.dumps(worldview.get('cognitive_mechanisms', []), ensure_ascii=False, indent=2)}

대립 구도:
{json.dumps(json.loads(worldview['frame']) if isinstance(worldview['frame'], str) else worldview['frame'], ensure_ascii=False, indent=2)}

감정 논리:
{json.dumps(worldview.get('formation_phases', []), ensure_ascii=False, indent=2)}

암묵적 전제:
{json.dumps(worldview.get('structural_flaws', []), ensure_ascii=False, indent=2)}

이 세계관에 대한 다음을 생성해주세요:

1. **대안 서사 (counter_narrative)**:
   - 같은 상황을 왜곡 없이 설명하는 대안적 관점 (200-300자)
   - 감정적 반응이 아닌 사실과 논리에 기반

2. **핵심 반박 포인트 (key_rebuttals)**:
   - 3-5개의 구체적 반박 포인트
   - 각 포인트는 명확하고 검증 가능해야 함

3. **제안 응답문 (suggested_response)**:
   - 이 세계관을 가진 사람과 대화할 때 사용할 수 있는 응답문 (100-150자)
   - 공격적이지 않고 대화를 유도하는 톤

4. **필요한 증거 (evidence_needed)**:
   - 이 세계관을 반박하기 위해 필요한 증거나 데이터 (3-5개)

5. **행동 가이드 (action_guide)**:
   - fact_checkers: 팩트체커를 위한 조언
   - journalists: 언론인을 위한 조언
   - general_public: 일반인을 위한 조언

JSON 형식으로 답변해주세요:
{{
  "counter_narrative": "...",
  "key_rebuttals": ["...", "..."],
  "suggested_response": "...",
  "evidence_needed": ["...", "..."],
  "action_guide": {{
    "fact_checkers": "...",
    "journalists": "...",
    "general_public": "..."
  }}
}}
"""

            response = await self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in political discourse analysis and fact-checking. Always respond in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.error(f"Error generating counter-narrative from worldview: {e}")
            return {
                'counter_narrative': '',
                'key_rebuttals': [],
                'suggested_response': '',
                'evidence_needed': [],
                'action_guide': {}
            }

    async def generate(
        self,
        worldview: Dict,
        perceptions: List[Dict],
        flaws: List[Dict]
    ) -> Dict:
        """
        Generate complete counter-narrative package

        Args:
            worldview: Worldview dict
            perceptions: List of perceptions
            flaws: List of detected flaws

        Returns:
            Counter-narrative dict with all components
        """
        try:
            # Generate main counter-narrative
            counter_narrative = await self._generate_counter_narrative(
                worldview,
                perceptions,
                flaws
            )

            # Generate rebuttal points
            rebuttals = await self._generate_rebuttals(
                worldview,
                flaws
            )

            # Generate suggested response
            suggested_response = await self._generate_suggested_response(
                worldview,
                rebuttals
            )

            # Generate evidence requirements
            evidence_needed = self._generate_evidence_requirements(flaws)

            result = {
                'counter_narrative': counter_narrative,
                'key_rebuttals': rebuttals,
                'suggested_response': suggested_response,
                'evidence_needed': evidence_needed,
                'action_guide': self._generate_action_guide(worldview)
            }

            logger.info(f"Generated counter-narrative for {worldview.get('title')}")
            return result

        except Exception as e:
            logger.error(f"Error generating counter-narrative: {e}")
            return {}

    async def _generate_counter_narrative(
        self,
        worldview: Dict,
        perceptions: List[Dict],
        flaws: List[Dict]
    ) -> str:
        """
        Generate alternative narrative using GPT-4

        Args:
            worldview: Worldview dict
            perceptions: List of perceptions
            flaws: List of flaws

        Returns:
            Counter-narrative text
        """
        try:
            # Prepare flaw summary
            flaw_summary = '\n'.join([
                f"- {f.get('name', f.get('type'))}: {f.get('description', '')}"
                for f in flaws[:5]
            ])

            prompt = f"""다음 왜곡된 세계관에 대한 대안 내러티브를 생성하세요.

왜곡된 세계관:
제목: {worldview.get('title')}
프레임: {worldview.get('frame')}
핵심 주장: {worldview.get('core_subject')}는 {', '.join(worldview.get('core_attributes', []))}

발견된 논리적 오류:
{flaw_summary}

**요구사항:**
1. 같은 사실을 다른 관점에서 재해석
2. 논리적 오류를 지적하며 더 균형잡힌 시각 제시
3. 감정적이지 않고 객관적인 톤
4. 2-3문단, 각 100-150자

대안 내러티브를 작성하세요:"""

            response = await self.openai.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {
                        'role': 'system',
                        'content': '당신은 왜곡된 내러티브를 분석하고 균형잡힌 대안을 제시하는 전문가입니다.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.5,
                max_tokens=800
            )

            counter_narrative = response.choices[0].message.content.strip()
            return counter_narrative

        except Exception as e:
            logger.error(f"Error generating counter-narrative: {e}")
            return ""

    async def _generate_rebuttals(
        self,
        worldview: Dict,
        flaws: List[Dict]
    ) -> List[str]:
        """
        Generate key rebuttal points

        Args:
            worldview: Worldview dict
            flaws: List of flaws

        Returns:
            List of rebuttal points
        """
        try:
            flaw_summary = '\n'.join([
                f"{i+1}. {f.get('name', f.get('type'))}: {f.get('description', '')}"
                for i, f in enumerate(flaws[:5])
            ])

            prompt = f"""다음 세계관의 핵심 약점을 반박하는 포인트를 생성하세요.

세계관: {worldview.get('title')}
프레임: {worldview.get('frame')}

발견된 오류:
{flaw_summary}

**요구사항:**
1. 3-5개의 핵심 반박 포인트
2. 각 포인트는 1-2문장
3. 구체적이고 실행 가능한 반박

JSON 형식으로 반환:
{{
  "rebuttals": [
    "첫 번째 반박 포인트",
    "두 번째 반박 포인트",
    ...
  ]
}}"""

            response = await self.openai.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {
                        'role': 'system',
                        'content': '당신은 논리적 반박을 작성하는 전문가입니다.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.4,
                response_format={'type': 'json_object'}
            )

            result = json.loads(response.choices[0].message.content)
            rebuttals = result.get('rebuttals', [])

            return rebuttals

        except Exception as e:
            logger.error(f"Error generating rebuttals: {e}")
            return []

    async def _generate_suggested_response(
        self,
        worldview: Dict,
        rebuttals: List[str]
    ) -> str:
        """
        Generate copyable suggested response

        Args:
            worldview: Worldview dict
            rebuttals: List of rebuttal points

        Returns:
            Suggested response text
        """
        try:
            rebuttals_text = '\n'.join([f"{i+1}. {r}" for i, r in enumerate(rebuttals)])

            prompt = f"""다음 왜곡된 주장에 대한 간결한 답변을 작성하세요.

왜곡된 주장: {worldview.get('frame')}

반박 포인트:
{rebuttals_text}

**요구사항:**
1. 2-3문장으로 간결하게
2. 복사해서 바로 사용 가능한 형태
3. 공손하지만 명확한 톤
4. 핵심 반박만 포함

답변을 작성하세요:"""

            response = await self.openai.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {
                        'role': 'system',
                        'content': '당신은 간결하고 효과적인 답변을 작성하는 전문가입니다.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.4,
                max_tokens=300
            )

            suggested_response = response.choices[0].message.content.strip()
            return suggested_response

        except Exception as e:
            logger.error(f"Error generating suggested response: {e}")
            return ""

    def _generate_evidence_requirements(self, flaws: List[Dict]) -> List[str]:
        """
        Generate list of evidence to request

        Args:
            flaws: List of flaws

        Returns:
            List of evidence requirements
        """
        requirements = []

        for flaw in flaws:
            flaw_type = flaw.get('type')

            if flaw_type == 'missing_evidence':
                requirements.append('구체적인 출처와 날짜를 요구하세요')
            elif flaw_type == 'hasty_generalization':
                requirements.append('더 많은 사례와 통계 데이터를 요구하세요')
            elif flaw_type == 'selective_facts':
                requirements.append('반대 증거와 전체 맥락을 요구하세요')
            elif flaw_type == 'term_ambiguity':
                terms = flaw.get('terms', [])
                if terms:
                    requirements.append(f"'{terms[0]}'의 명확한 정의를 요구하세요")
            elif flaw_type == 'logical_leap':
                requirements.append('논리적 연결의 근거를 요구하세요')

        # Deduplicate
        return list(set(requirements))

    def _generate_action_guide(self, worldview: Dict) -> Dict:
        """
        Generate 4-step action guide

        Args:
            worldview: Worldview dict

        Returns:
            Action guide dict
        """
        return {
            'step_1': {
                'title': '논리적 오류 지적',
                'description': '감정적 반응 대신 구조적 약점을 차분하게 지적',
                'example': '"이 주장은 [구체적 오류]를 포함하고 있습니다."'
            },
            'step_2': {
                'title': '증거 요구',
                'description': '구체적 근거와 출처를 요청',
                'example': '"이 주장의 근거가 되는 자료를 공유해주실 수 있나요?"'
            },
            'step_3': {
                'title': '대안 제시',
                'description': '같은 사실을 다른 관점에서 해석',
                'example': '"다른 관점에서 보면 [대안적 해석]도 가능합니다."'
            },
            'step_4': {
                'title': '건설적 대화 유도',
                'description': '공격 대신 이해를 목표로',
                'example': '"함께 더 정확한 이해에 도달해봅시다."'
            }
        }

    async def generate_for_worldview(self, worldview_id: str) -> Dict:
        """
        Generate counter-narrative for specific worldview (convenience method)

        Args:
            worldview_id: Worldview UUID

        Returns:
            Counter-narrative dict
        """
        try:
            # Get worldview
            response = self.supabase.table('worldviews')\
                .select('*')\
                .eq('id', worldview_id)\
                .execute()

            if not response.data:
                logger.error(f"Worldview {worldview_id} not found")
                return {}

            worldview = response.data[0]

            # Get perceptions
            perception_ids = worldview.get('perception_ids', [])
            if not perception_ids:
                return {}

            response = self.supabase.table('perceptions')\
                .select('*')\
                .in_('id', perception_ids)\
                .execute()

            perceptions = response.data

            # Get existing flaws from worldview
            flaws = worldview.get('structural_flaws', [])

            # Generate counter-narrative
            result = await self.generate(worldview, perceptions, flaws)

            return result

        except Exception as e:
            logger.error(f"Error generating counter-narrative for worldview: {e}")
            return {}
