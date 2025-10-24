#!/usr/bin/env python3
"""
Claude Mechanism Matcher 최적화 실험

MechanismMatcher의 핵심 기능:
- Perception과 Worldview를 매칭
- Actor 유사도 (50%) + Mechanism 겹침 (30%) + Logic 유사도 (20%)
- 임계값 이상일 때 링크 생성

실험 전략:
1. Baseline - 기존 GPT 매칭 방식
2. Semantic-Matching - 의미 기반 유사도
3. Weighted-Scoring - 가중치 조정
4. Explanation-Based - 매칭 근거 설명
"""

import os
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List
from anthropic import Anthropic
from dotenv import load_dotenv
import sys
sys.path.insert(0, '/Users/taehyeonkim/dev/minjoo/moniterdc')

from engines.utils.supabase_client import get_supabase

load_dotenv()

claude_client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
supabase = get_supabase()


class MatcherExperiment:
    """Base class for mechanism matcher experiments"""

    def __init__(self, name: str):
        self.name = name

    def build_prompt(self, perception: Dict, worldviews: List[Dict]) -> str:
        raise NotImplementedError

    def match_perception(self, perception: Dict, worldviews: List[Dict]) -> Dict:
        """Match perception to worldviews"""

        prompt = self.build_prompt(perception, worldviews)

        start_time = time.time()

        message = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        elapsed = time.time() - start_time

        response_text = message.content[0].text

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

        result = json.loads(json_str)
        result['_elapsed_time'] = elapsed

        return result


class BaselineMatcherExperiment(MatcherExperiment):
    """현재 GPT 매칭 방식"""

    def __init__(self):
        super().__init__("Baseline-Matcher")

    def build_prompt(self, perception: Dict, worldviews: List[Dict]) -> str:
        # Simplify worldviews for prompt
        wv_summaries = []
        for wv in worldviews:
            frame = wv.get('frame', {})
            if isinstance(frame, dict):
                wv_summaries.append({
                    'id': wv['id'],
                    'title': wv['title'],
                    'actor': frame.get('actor', {}),
                    'mechanisms': frame.get('core_mechanisms', [])
                })

        return f"""
다음 Perception을 가장 잘 설명하는 Worldview를 찾으세요.

## Perception

ID: {perception['id']}
Actor: {perception.get('actor', {})}
Mechanisms: {perception.get('mechanisms', [])}
Logic Chain: {perception.get('logic_chain', [])[:3]}

## 후보 Worldviews ({len(worldviews)}개)

{json.dumps(wv_summaries, ensure_ascii=False, indent=2)}

---

## 매칭 기준

1. **Actor 유사도 (50%)**: 같은 subject를 다루는가?
2. **Mechanism 겹침 (30%)**: 공통 메커니즘이 있는가?
3. **Logic 유사도 (20%)**: 추론 패턴이 비슷한가?

## 임계값

- 0.6 이상: 매칭
- 0.6 미만: 매칭 안됨

JSON 형식:
{{
  "matched_worldviews": [
    {{
      "worldview_id": "uuid",
      "worldview_title": "제목",
      "match_score": 0.0-1.0,
      "reasons": {{
        "actor_similarity": 0.0-1.0,
        "mechanism_overlap": 0.0-1.0,
        "logic_similarity": 0.0-1.0
      }}
    }}
  ]
}}
"""


class SemanticMatcherExperiment(MatcherExperiment):
    """의미 기반 유사도 매칭"""

    def __init__(self):
        super().__init__("Semantic-Matcher")

    def build_prompt(self, perception: Dict, worldviews: List[Dict]) -> str:
        # Simplify
        wv_summaries = []
        for wv in worldviews:
            frame = wv.get('frame', {})
            if isinstance(frame, dict):
                wv_summaries.append({
                    'id': wv['id'],
                    'title': wv['title'],
                    'description': wv.get('description', ''),
                    'actor': frame.get('actor', {}),
                    'mechanisms': frame.get('core_mechanisms', [])
                })

        return f"""
Perception과 Worldview의 **의미적 유사도**를 분석하세요.

## Perception

Actor: {perception.get('actor', {})}
Mechanisms: {perception.get('mechanisms', [])}
Deep Beliefs: {perception.get('deep_beliefs', [])[:3]}

## Worldviews

{json.dumps(wv_summaries, ensure_ascii=False, indent=2)}

---

## 의미 기반 매칭

단순 키워드 매칭이 아닌 **의미 유사도**를 평가하세요.

### Actor 의미 비교

예시:
- "민주당" vs "좌파" → 높은 유사도 (같은 진영)
- "이재명" vs "민주당" → 중간 유사도 (관련 있음)
- "중국" vs "민주당" → 낮은 유사도 (다른 대상)

### Mechanism 의미

- 같은 메커니즘 = 1.0
- 보완적 메커니즘 = 0.5 (예: 즉시_단정 + 표면_부정)
- 무관 = 0.0

### Deep Belief vs Worldview Description

Perception의 Deep Beliefs가 Worldview의 설명과 얼마나 겹치는가?

JSON:
{{
  "matched_worldviews": [
    {{
      "worldview_id": "uuid",
      "worldview_title": "제목",
      "match_score": 0.0-1.0,
      "semantic_analysis": {{
        "actor_semantic_similarity": 0.0-1.0,
        "mechanism_overlap": 0.0-1.0,
        "belief_description_similarity": 0.0-1.0
      }},
      "explanation": "왜 이 worldview가 매칭되는가 (1-2문장)"
    }}
  ]
}}
"""


class WeightedScoringMatcherExperiment(MatcherExperiment):
    """가중치 조정 실험"""

    def __init__(self):
        super().__init__("Weighted-Scoring-Matcher")

    def build_prompt(self, perception: Dict, worldviews: List[Dict]) -> str:
        wv_summaries = []
        for wv in worldviews:
            frame = wv.get('frame', {})
            if isinstance(frame, dict):
                wv_summaries.append({
                    'id': wv['id'],
                    'title': wv['title'],
                    'actor': frame.get('actor', {}),
                    'mechanisms': frame.get('core_mechanisms', []),
                    'logic_pattern': frame.get('logic_pattern', {})
                })

        return f"""
다음 **3가지 가중치**로 매칭 점수를 계산하세요.

## Perception

Actor: {perception.get('actor', {})}
Mechanisms: {perception.get('mechanisms', [])}
Logic Chain: {perception.get('logic_chain', [])[:3]}

## Worldviews

{json.dumps(wv_summaries, ensure_ascii=False, indent=2)}

---

## 가중치 실험

### 옵션 1: 기존 (Actor 50%, Mechanism 30%, Logic 20%)
### 옵션 2: Mechanism 중심 (Actor 30%, Mechanism 50%, Logic 20%)
### 옵션 3: 균등 (Actor 33%, Mechanism 33%, Logic 33%)

**각 옵션별로 점수를 계산하고, 어느 것이 가장 적절한지 판단하세요.**

## 점수 계산 방법

### Actor Similarity (0.0-1.0)
- 정확히 같음: 1.0
- 같은 진영 (예: 민주당 vs 좌파): 0.8
- 관련 있음 (예: 이재명 vs 민주당): 0.6
- 다름: 0.0

### Mechanism Overlap (0.0-1.0)
- 겹치는 메커니즘 수 / 전체 메커니즘 수

### Logic Similarity (0.0-1.0)
- Perception의 Logic Chain이 Worldview의 Logic Pattern과 얼마나 일치?
  - Trigger 유사: +0.4
  - Skipped 유사: +0.3
  - Conclusion 유사: +0.3

JSON:
{{
  "matched_worldviews": [
    {{
      "worldview_id": "uuid",
      "worldview_title": "제목",
      "scoring_options": {{
        "option1_actor50": {{
          "actor_sim": 0.0-1.0,
          "mechanism_overlap": 0.0-1.0,
          "logic_sim": 0.0-1.0,
          "final_score": 0.0-1.0
        }},
        "option2_mechanism50": {{
          "actor_sim": 0.0-1.0,
          "mechanism_overlap": 0.0-1.0,
          "logic_sim": 0.0-1.0,
          "final_score": 0.0-1.0
        }},
        "option3_equal": {{
          "actor_sim": 0.0-1.0,
          "mechanism_overlap": 0.0-1.0,
          "logic_sim": 0.0-1.0,
          "final_score": 0.0-1.0
        }}
      }},
      "best_option": "option1|option2|option3",
      "reason": "왜 이 가중치가 가장 적절한가"
    }}
  ]
}}
"""


class ExplanationBasedMatcherExperiment(MatcherExperiment):
    """매칭 근거 설명 중심"""

    def __init__(self):
        super().__init__("Explanation-Based-Matcher")

    def build_prompt(self, perception: Dict, worldviews: List[Dict]) -> str:
        wv_summaries = []
        for wv in worldviews:
            frame = wv.get('frame', {})
            if isinstance(frame, dict):
                wv_summaries.append({
                    'id': wv['id'],
                    'title': wv['title'],
                    'description': wv.get('description', ''),
                    'actor': frame.get('actor', {}),
                    'mechanisms': frame.get('core_mechanisms', [])
                })

        return f"""
Perception이 어떤 Worldview에 속하는지 **근거를 들어** 설명하세요.

## Perception

Actor: {perception.get('actor', {})}
Mechanisms: {perception.get('mechanisms', [])}
Deep Beliefs: {perception.get('deep_beliefs', [])[:2]}
Implicit Assumptions: {perception.get('implicit_assumptions', [])[:2]}

## Worldviews

{json.dumps(wv_summaries, ensure_ascii=False, indent=2)}

---

## 매칭 근거 설명

각 Worldview에 대해:

1. **왜 매칭되는가?**
   - Actor가 일치하는가? (구체적으로)
   - Mechanism이 겹치는가? (어떤 메커니즘?)
   - Deep Belief가 Worldview 설명과 일치하는가?

2. **얼마나 강하게 매칭되는가?**
   - Strong (0.8-1.0): Actor + Mechanism + Belief 모두 일치
   - Medium (0.6-0.8): 2개 이상 일치
   - Weak (0.4-0.6): 1개만 일치
   - None (< 0.4): 매칭 안됨

3. **대안 Worldview는?**
   - 다른 Worldview가 더 적합한가?

JSON:
{{
  "matched_worldviews": [
    {{
      "worldview_id": "uuid",
      "worldview_title": "제목",
      "match_score": 0.0-1.0,
      "match_strength": "strong|medium|weak",
      "explanation": {{
        "actor_match": "Actor 매칭 근거",
        "mechanism_match": "Mechanism 매칭 근거",
        "belief_match": "Deep Belief 매칭 근거"
      }},
      "why_this_worldview": "종합 설명 (2-3문장)"
    }}
  ],
  "no_match_reason": "매칭 안되는 경우 이유"
}}
"""


def run_experiments():
    """모든 실험 실행"""

    print("=" * 80)
    print("Claude Mechanism Matcher 최적화 실험")
    print("=" * 80)

    # Get test perception
    print("\n📊 테스트 데이터 로딩...")

    perception_query = supabase.table('layered_perceptions')\
        .select('*')\
        .not_.is_('mechanisms', 'null')\
        .not_.is_('actor', 'null')\
        .limit(1)\
        .order('created_at', desc=True)

    perception_result = perception_query.execute()
    perception = perception_result.data[0]

    print(f"   ✓ Perception: {perception['id'][:8]}...")
    print(f"     Actor: {perception.get('actor', {}).get('subject', 'N/A')}")
    print(f"     Mechanisms: {perception.get('mechanisms', [])}")

    # Get worldviews
    worldview_query = supabase.table('worldviews')\
        .select('*')\
        .eq('archived', False)\
        .limit(7)

    worldview_result = worldview_query.execute()
    worldviews = worldview_result.data

    print(f"   ✓ {len(worldviews)}개 Worldviews 로딩")

    # Run experiments
    experiments = [
        BaselineMatcherExperiment(),
        SemanticMatcherExperiment(),
        WeightedScoringMatcherExperiment(),
        ExplanationBasedMatcherExperiment()
    ]

    results = {}

    for exp in experiments:
        print(f"\n{'=' * 80}")
        print(f"실험: {exp.name}")
        print(f"{'=' * 80}")

        try:
            matches = exp.match_perception(perception, worldviews)
            elapsed = matches.pop('_elapsed_time', 0)

            results[exp.name] = {
                "matches": matches,
                "elapsed": elapsed,
                "success": True
            }

            print(f"\n✅ 완료 ({elapsed:.2f}초)")
            print(f"\n📋 매칭 결과:")

            matched_wvs = matches.get('matched_worldviews', [])
            if matched_wvs:
                for m in matched_wvs[:3]:
                    score = m.get('match_score', 0)
                    title = m.get('worldview_title', 'N/A')
                    print(f"   - {title}: {score:.2f}")
            else:
                print(f"   매칭 안됨: {matches.get('no_match_reason', 'N/A')}")

        except Exception as e:
            import traceback
            print(f"\n❌ 실패: {e}")
            print(f"\n🔍 Traceback:")
            traceback.print_exc()
            results[exp.name] = {
                "error": str(e),
                "success": False
            }

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "perception": {
            "id": perception['id'],
            "actor": perception.get('actor'),
            "mechanisms": perception.get('mechanisms')
        },
        "worldviews_count": len(worldviews),
        "experiments": results
    }

    output_file = f"_test_results/matcher_experiments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 80}")
    print(f"✅ 실험 완료: {output_file}")
    print(f"{'=' * 80}")

    # Summary
    print(f"\n📊 요약:")
    for name, data in results.items():
        if data.get('success'):
            matches = data['matches'].get('matched_worldviews', [])
            match_count = len(matches)
            print(f"   {name}: {data['elapsed']:.2f}s, {match_count}개 매칭 ✅")
        else:
            print(f"   {name}: ❌ {data.get('error', 'Unknown error')}")


if __name__ == "__main__":
    run_experiments()
