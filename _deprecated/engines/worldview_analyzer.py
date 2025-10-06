"""
Real Worldview Analysis Engine
진짜 세계관 분석: 표면 주장이 아닌 구성된 믿음 체계 파악
"""
from openai import AsyncOpenAI
import os
from typing import List, Dict
from engines.utils.supabase_client import get_supabase
from uuid import UUID
import json

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class WorldviewAnalyzer:
    """
    세계관 = 연결된 믿음들의 체계

    분석 목표:
    1. 인과 구조: A는 B 때문이고, B는 C 때문이다
    2. 대립 구도: 우리 vs 그들, 선 vs 악
    3. 감정 논리: 분노/두려움/배신감이 어떻게 주장을 정당화하는가
    4. 암묵적 전제: 명시되지 않았지만 모든 주장의 기반이 되는 믿음
    """

    def __init__(self):
        self.supabase = get_supabase()

    async def analyze_worldview_from_posts(self, contents: List[Dict]) -> Dict:
        """
        글들로부터 구성된 세계관 파악

        Args:
            contents: List of content dicts with 'title' and 'body'

        Returns:
            {
                'causal_chains': [...],  # 인과 관계 체인
                'opposition_framework': {...},  # 대립 구도
                'emotional_logic': {...},  # 감정-주장 연결
                'implicit_assumptions': [...],  # 암묵적 전제
                'narrative': str  # 전체 세계관 서사
            }
        """

        # Prepare post texts
        posts_text = "\n\n---\n\n".join([
            f"제목: {c['title']}\n내용: {c['body'][:500]}"
            for c in contents
        ])

        prompt = f"""
당신은 정치 담론 분석 전문가입니다. 다음은 DC Gallery 정치 갤러리에서 수집한 글들입니다.

{posts_text}

이 글들을 쓴 사람들이 **머릿속에 구성한 세계관**을 파악해주세요.

⚠️ 중요: 단순히 "어떤 주제를 언급했는가"가 아니라, "이들이 세상을 어떻게 이해하고 있는가"를 분석하세요.

다음 4가지 차원에서 분석해주세요:

## 1. 인과 구조 (Causal Chains)
- 이들은 사건/현상을 어떤 인과관계로 설명하는가?
- 예: "민주당이 독재를 하는 이유 → 권력욕 → 좌파의 본성"
- 최소 3개의 인과 체인을 찾아주세요. 각 체인은 3단계 이상이어야 합니다.

형식:
[
  {{
    "chain": ["현상", "원인1", "원인2", "근본 원인"],
    "example_posts": ["글 제목1", "글 제목2"]
  }}
]

## 2. 대립 구도 (Opposition Framework)
- 이들의 세계에서 누가 "우리 편"이고 누가 "적"인가?
- 각 진영에 어떤 속성을 부여하는가?

형식:
{{
  "us": {{
    "identity": ["우파", "애국자", ...],
    "attributes": ["정의", "상식", ...],
    "role": "설명"
  }},
  "them": {{
    "identity": ["좌파", "민주당", ...],
    "attributes": ["독재", "사기", ...],
    "role": "설명"
  }},
  "conflict_nature": "이 대립이 왜 타협 불가능한지"
}}

## 3. 감정 논리 (Emotional Logic)
- 어떤 감정이 어떤 주장/행동을 정당화하는가?
- 감정 → 해석 → 결론의 흐름

형식:
[
  {{
    "emotion": "분노/두려움/배신감/...",
    "trigger": "무엇이 이 감정을 유발하는가",
    "interpretation": "이 감정으로 상황을 어떻게 해석하는가",
    "conclusion": "이 해석이 어떤 주장/행동으로 이어지는가",
    "example_posts": ["글 제목"]
  }}
]

## 4. 암묵적 전제 (Implicit Assumptions)
- 명시되지 않았지만 모든 주장의 기반이 되는 믿음
- "당연하게 여겨지는 것"

형식:
[
  {{
    "assumption": "전제 설명",
    "evidence": "이 전제가 어떤 주장들에서 드러나는가",
    "impact": "이 전제가 있으면 어떤 결론이 자동으로 따라오는가"
  }}
]

## 5. 전체 서사 (Narrative)
위 4가지를 종합해서, 이들이 구성한 "세계에 대한 이야기"를 3-4문단으로 서술해주세요.

반드시 JSON 형식으로 답변해주세요:
{{
  "causal_chains": [...],
  "opposition_framework": {{}},
  "emotional_logic": [...],
  "implicit_assumptions": [...],
  "narrative": "..."
}}
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in political discourse analysis. Always respond in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content

        # Debug: print raw response
        print(f"\n[DEBUG] GPT Response (first 500 chars):\n{content[:500]}\n")

        try:
            result = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            print(f"Raw content: {content[:1000]}")
            raise

        return result

    async def detect_worldviews(self) -> List[UUID]:
        """
        1. 모든 contents 가져오기
        2. 주제별로 그룹핑 (기존 방식)
        3. 각 그룹에 대해 worldview 분석
        4. DB에 저장
        """

        # Get all contents with body
        contents = self.supabase.table('contents').select('*').neq('body', '').execute().data

        if len(contents) < 20:
            print(f"⚠️ Warning: Only {len(contents)} contents available")

        # Group by manual theme analysis (reuse existing logic)
        # For now, analyze all together to find the overarching worldview

        print(f"Analyzing worldview from {len(contents)} contents...")

        worldview_data = await self.analyze_worldview_from_posts(contents)

        # Save to DB
        worldview_id = await self._save_worldview(worldview_data, contents)

        return [worldview_id]

    async def _save_worldview(self, data: Dict, contents: List[Dict]) -> UUID:
        """Save analyzed worldview to database"""

        # Create title from narrative
        title = data['narrative'].split('.')[0][:100]

        # Extract core_subject from opposition framework
        opp = data.get('opposition_framework', {})
        them_identity = opp.get('them', {}).get('identity', [])
        core_subject = them_identity[0] if them_identity else "정치"

        # Extract core_attributes
        them_attributes = opp.get('them', {}).get('attributes', [])

        worldview = {
            'title': title,
            'frame': json.dumps(opp, ensure_ascii=False),
            'description': data['narrative'],
            'core_subject': core_subject,
            'core_attributes': them_attributes[:5],  # Limit to 5
            'overall_valence': 'negative',  # Opposition framework targets are negative
            'total_contents': len(contents),
            'total_perceptions': 0,  # Will be updated later if needed
            'strength_overall': min(len(contents) / 50, 1.0),  # Strength based on data volume
            'cognitive_mechanisms': data['causal_chains'],
            'formation_phases': data['emotional_logic'],
            'structural_flaws': data['implicit_assumptions'],
            'deconstruction': {
                'counter_narrative': '',  # Will be filled by DeconstructionEngine
                'causal_chains': data['causal_chains'],
                'opposition_framework': data['opposition_framework'],
                'emotional_logic': data['emotional_logic'],
                'implicit_assumptions': data['implicit_assumptions']
            }
        }

        result = self.supabase.table('worldviews').insert(worldview).execute()

        if result.data:
            wv_id = result.data[0]['id']
            print(f"✅ Worldview saved: {title}")
            return UUID(wv_id)
        else:
            raise Exception("Failed to save worldview")
