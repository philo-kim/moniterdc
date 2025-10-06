"""
DeconstructionGenerator - 반박 논리 생성 엔진

세계관의 논리적 허점을 분석하고 건설적인 반박 논리 생성
"""

from openai import AsyncOpenAI
import os
import json
from typing import Dict
from uuid import UUID
from engines.utils.supabase_client import get_supabase

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class DeconstructionGenerator:
    """Generate logical deconstruction for worldviews"""

    def __init__(self):
        self.supabase = get_supabase()

    async def generate_for_worldview(self, worldview_id: str) -> Dict:
        """
        특정 세계관에 대한 반박 논리 생성

        Args:
            worldview_id: Worldview UUID

        Returns:
            Deconstruction data
        """

        # 세계관 로드
        wv = self.supabase.table('worldviews')\
            .select('*')\
            .eq('id', worldview_id)\
            .execute().data[0]

        frame = json.loads(wv['frame'])

        print(f"\n반박 논리 생성: {wv['title']}")

        # GPT로 반박 논리 생성
        deconstruction = await self._generate_deconstruction(wv, frame)

        # DB 저장
        await self._save_deconstruction(worldview_id, deconstruction)

        return deconstruction

    async def generate_for_all_worldviews(self) -> Dict:
        """
        모든 세계관에 대한 반박 논리 생성

        Returns:
            생성 통계
        """

        print("\n" + "="*70)
        print("전체 세계관 반박 논리 생성")
        print("="*70)

        # 신규 계층형 세계관만
        worldviews = self.supabase.table('worldviews')\
            .select('*')\
            .execute().data

        new_wvs = [wv for wv in worldviews if '>' in wv['title']]

        print(f"\n대상 세계관: {len(new_wvs)}개")

        generated = 0

        for i, wv in enumerate(new_wvs, 1):
            print(f"\n[{i}/{len(new_wvs)}] {wv['title']}")

            try:
                await self.generate_for_worldview(wv['id'])
                generated += 1
                print(f"  ✅ 생성 완료")
            except Exception as e:
                print(f"  ❌ 실패: {e}")

        print(f"\n\n✅ {generated}/{len(new_wvs)}개 생성 완료")

        return {
            'total': len(new_wvs),
            'generated': generated
        }

    async def _generate_deconstruction(self, wv: Dict, frame: Dict) -> Dict:
        """GPT로 반박 논리 생성"""

        narrative = frame.get('narrative', {})
        metadata = frame.get('metadata', {})

        prompt = f"""
다음은 DC Gallery에서 발견된 세계관입니다.

【세계관】
제목: {wv['title']}
요약: {narrative.get('summary', '')}

【구체적 해석】
{json.dumps(narrative.get('examples', []), ensure_ascii=False, indent=2)}

【논리 구조】
- Causal Chain: {metadata.get('interpretation_frame', {}).get('causal_chain', [])}
- Slippery Slope: {json.dumps(metadata.get('interpretation_frame', {}).get('slippery_slope', {}), ensure_ascii=False)}
- 감정: {metadata.get('emotional_drivers', {}).get('primary', '')} (긴급도: {metadata.get('emotional_drivers', {}).get('urgency_level', '')})

---

이 세계관에 대한 **반박 논리**를 생성해주세요.

목적: 여당 지지자가 이 세계관을 가진 사람과 대화할 때 사용할 수 있는 논리적 반박

필요한 항목:

1. **논리적 허점 분석** (Logical Flaws)
   - 이 세계관이 사용하는 논리적 오류 식별
   - 예: 슬리퍼리 슬로프, 허수아비 공격, 성급한 일반화, 인과관계 오류 등

2. **사실 확인** (Fact Check)
   - 이 세계관의 전제가 되는 "사실"들이 실제로 맞는지 검증
   - 반증 사례 제시

3. **대안적 해석** (Alternative Interpretation)
   - 같은 사건을 다르게 해석하는 방법
   - "이렇게도 볼 수 있다"

4. **역사적 맥락 교정** (Historical Context Correction)
   - 이들이 참조하는 역사가 실제와 어떻게 다른지
   - 과거와 현재의 실제 차이

5. **감정적 요소 이해** (Emotional Understanding)
   - 왜 이런 감정을 느끼는지 공감
   - 하지만 그 감정이 사실과는 다를 수 있음을 설명

6. **건설적 대화 가이드** (Constructive Dialogue)
   - 이 세계관을 가진 사람과 대화할 때 피해야 할 것
   - 효과적인 대화 전략
   - 실제 사용 가능한 응답 예시

JSON 형식:
{{
  "logical_flaws": [
    {{
      "type": "오류 유형",
      "description": "설명",
      "example": "이 세계관에서의 예시",
      "rebuttal": "반박 논리"
    }}
  ],
  "fact_checks": [
    {{
      "claim": "그들의 주장",
      "reality": "실제 사실",
      "evidence": "근거"
    }}
  ],
  "alternative_interpretations": [
    {{
      "dc_interpretation": "DC Gallery 해석",
      "alternative": "대안적 해석",
      "reasoning": "논리"
    }}
  ],
  "historical_corrections": [
    {{
      "their_reference": "그들의 역사 참조",
      "actual_difference": "실제 차이",
      "context": "맥락 설명"
    }}
  ],
  "emotional_understanding": {{
    "their_emotion": "그들의 감정",
    "why_they_feel": "왜 그렇게 느끼나",
    "empathy": "공감 표현",
    "but": "하지만..."
  }},
  "dialogue_guide": {{
    "avoid": ["피해야 할 것들"],
    "effective": ["효과적인 것들"],
    "example_response": "실제 사용 가능한 응답 예시"
  }}
}}
"""

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in political discourse analysis and constructive dialogue. Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    async def _save_deconstruction(self, worldview_id: str, deconstruction: Dict):
        """반박 논리를 DB에 저장"""

        # frame에 deconstruction 추가
        wv = self.supabase.table('worldviews')\
            .select('frame')\
            .eq('id', worldview_id)\
            .execute().data[0]

        frame = json.loads(wv['frame'])
        frame['deconstruction'] = deconstruction

        # 업데이트
        self.supabase.table('worldviews')\
            .update({'frame': json.dumps(frame, ensure_ascii=False)})\
            .eq('id', worldview_id)\
            .execute()
