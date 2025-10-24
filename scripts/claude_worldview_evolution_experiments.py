#!/usr/bin/env python3
"""
Claude Worldview Evolution Engine 최적화 실험

WorldviewEvolutionEngine의 핵심 기능:
1. 200개 샘플 perceptions 분석
2. 공통 메커니즘 패턴 발견
3. Actor + Logic Pattern 추출
4. 새로운 worldview 자동 생성

실험 전략:
1. Baseline - 기존 GPT 프롬프트
2. Pattern-First - 메커니즘 패턴 우선 분석
3. Actor-Centric - Actor 중심으로 그룹핑
4. Data-Driven - 통계 기반 패턴 발견
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


class WorldviewExperiment:
    """Base class for worldview evolution experiments"""

    def __init__(self, name: str):
        self.name = name

    def build_prompt(self, perceptions: List[Dict]) -> str:
        raise NotImplementedError

    def extract_worldview(self, perceptions: List[Dict]) -> Dict:
        """Extract worldview pattern from perceptions"""

        prompt = self.build_prompt(perceptions)

        start_time = time.time()

        message = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            temperature=0.3,  # 약간의 creativity 필요
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


class BaselineWorldviewExperiment(WorldviewExperiment):
    """현재 GPT 프롬프트 그대로"""

    def __init__(self):
        super().__init__("Baseline-Worldview")

    def build_prompt(self, perceptions: List[Dict]) -> str:
        # 샘플 데이터 요약
        mechanism_counts = {}
        actor_subjects = {}

        for p in perceptions:
            # mechanisms
            mechs = p.get('mechanisms', [])
            if mechs is None:
                mechs = []
            for mech in mechs:
                mechanism_counts[mech] = mechanism_counts.get(mech, 0) + 1

            # actor subjects
            actor = p.get('actor', {})
            if isinstance(actor, dict):
                subj = actor.get('subject', 'Unknown')
                # Ensure subject is hashable (string)
                if isinstance(subj, list):
                    subj = ', '.join(str(s) for s in subj)
                elif not isinstance(subj, str):
                    subj = str(subj)
                actor_subjects[subj] = actor_subjects.get(subj, 0) + 1

        # Simplified sample data
        sample_data = []
        for p in perceptions[:5]:
            sample_data.append({
                'id': p.get('id'),
                'mechanisms': p.get('mechanisms', []),
                'actor': p.get('actor', {}),
                'logic_chain': p.get('logic_chain', [])[:3] if p.get('logic_chain') else []
            })

        return f"""
다음은 최근 담론에서 추출한 {len(perceptions)}개의 추론 구조입니다.

메커니즘 분포:
{json.dumps(mechanism_counts, ensure_ascii=False, indent=2)}

Actor 분포:
{json.dumps(actor_subjects, ensure_ascii=False, indent=2)}

샘플 perceptions (처음 5개):
{json.dumps(sample_data, ensure_ascii=False, indent=2)}

---

이 데이터에서 **하나의 대표적인 세계관 패턴**을 발견해주세요.

## 세계관이란?

"상대방은 틀린 게 아니라, 다른 세계를 산다"

- 같은 사건을 보고도 완전히 다른 해석이 나오는 이유
- 명시적 주장 뒤에 숨은 암묵적 추론 구조
- "당연하다고 여기는 것들"의 체계

## 찾아야 할 것

1. **공통 Actor** (누구에 대한 이야기인가?)
   - Subject: 구체적 주체 (예: "민주당/좌파", "윤석열 정권")
   - Purpose: 그들이 왜 행동한다고 믿는가?
   - Methods: 어떤 수단을 쓴다고 믿는가?

2. **공통 Mechanisms** (어떻게 추론하는가?)
   - 즉시_단정, 역사_투사, 필연적_인과, 네트워크_추론, 표면_부정 중
   - 이 세계관에서 자주 쓰는 3-4개 선택

3. **Logic Pattern** (추론 구조)
   - Trigger: 어떤 관찰에서 시작?
   - Skipped: 어떤 검증을 생략?
   - Conclusion: 어떤 결론에 도달?

JSON 형식:
{{
  "title": "30자 이내 제목",
  "description": "이 세계관의 핵심 특징 (2-3문장)",
  "actor": {{
    "subject": "구체적 주체",
    "purpose": "왜 행동하는가",
    "methods": ["수단1", "수단2", "수단3"]
  }},
  "core_mechanisms": ["메커니즘1", "메커니즘2", "메커니즘3"],
  "logic_pattern": {{
    "trigger": "시작 관찰",
    "skipped_verification": "생략된 검증",
    "conclusion": "최종 해석"
  }},
  "example_perceptions": ["perception_id1", "perception_id2", "perception_id3"],
  "confidence": 0.0-1.0
}}
"""


class PatternFirstWorldviewExperiment(WorldviewExperiment):
    """메커니즘 패턴을 먼저 찾고 → Actor 결정"""

    def __init__(self):
        super().__init__("Pattern-First-Worldview")

    def build_prompt(self, perceptions: List[Dict]) -> str:
        # 메커니즘 조합 분석
        mechanism_combos = {}
        for p in perceptions:
            mechs_raw = p.get('mechanisms', [])
            # Handle both list and None
            if mechs_raw is None:
                mechs_raw = []
            elif not isinstance(mechs_raw, list):
                mechs_raw = []
            mechs = tuple(sorted(mechs_raw))
            mechanism_combos[mechs] = mechanism_combos.get(mechs, 0) + 1

        top_combos = sorted(mechanism_combos.items(), key=lambda x: x[1], reverse=True)[:5]

        return f"""
{len(perceptions)}개 담론의 메커니즘 조합 패턴:

상위 5개 조합:
{json.dumps([(list(combo), count) for combo, count in top_combos], ensure_ascii=False, indent=2)}

전체 데이터:
{json.dumps(perceptions[:10], ensure_ascii=False, indent=2)}

---

## Step 1: 가장 강한 메커니즘 패턴 찾기

5가지 메커니즘 중 자주 함께 나타나는 3-4개 조합을 찾으세요:
- 즉시_단정 (검증 생략)
- 역사_투사 (과거 → 현재)
- 필연적_인과 (반드시 ~)
- 네트워크_추론 (조직적 연결)
- 표면_부정 (표면 vs 실제)

## Step 2: 그 패턴을 쓰는 Actor 찾기

같은 메커니즘 조합을 쓰는 담론들의 공통 Actor는?

## Step 3: Logic Pattern 추출

그 메커니즘들이 어떤 추론 흐름을 만드는가?

JSON:
{{
  "primary_mechanisms": ["메커니즘1", "메커니즘2", "메커니즘3"],
  "mechanism_explanation": "왜 이 조합이 의미있는가?",
  "actor": {{
    "subject": "이 패턴으로 주로 이야기하는 대상",
    "purpose": "목적",
    "methods": ["수단들"]
  }},
  "logic_pattern": {{
    "trigger": "어떤 관찰",
    "skipped_verification": "생략",
    "conclusion": "결론"
  }},
  "title": "세계관 제목",
  "description": "설명"
}}
"""


class ActorCentricWorldviewExperiment(WorldviewExperiment):
    """Actor를 먼저 그룹핑 → 메커니즘 패턴 발견"""

    def __init__(self):
        super().__init__("Actor-Centric-Worldview")

    def build_prompt(self, perceptions: List[Dict]) -> str:
        # Actor별 그룹핑
        actor_groups = {}
        for p in perceptions:
            actor = p.get('actor', {})
            if isinstance(actor, dict):
                subj = actor.get('subject', 'Unknown')
                # Ensure subject is hashable (string)
                if isinstance(subj, list):
                    subj = ', '.join(str(s) for s in subj)
                elif not isinstance(subj, str):
                    subj = str(subj)
                if subj not in actor_groups:
                    actor_groups[subj] = []
                actor_groups[subj].append(p)

        # 가장 큰 그룹 선택
        largest_actor = max(actor_groups.keys(), key=lambda k: len(actor_groups[k]))

        # Simplified sample data
        largest_group_simplified = []
        for p in actor_groups[largest_actor][:10]:
            largest_group_simplified.append({
                'id': p.get('id'),
                'mechanisms': p.get('mechanisms', []),
                'actor': p.get('actor', {}),
                'logic_chain': p.get('logic_chain', [])[:3] if p.get('logic_chain') else []
            })

        return f"""
{len(perceptions)}개 담론을 Actor별로 그룹핑했습니다.

가장 큰 그룹: "{largest_actor}" ({len(actor_groups[largest_actor])}개)

이 Actor에 대한 담론 샘플:
{json.dumps(largest_group_simplified, ensure_ascii=False, indent=2)}

---

## Actor 중심 세계관 추출

### Step 1: Actor 상세화

이 그룹이 "{largest_actor}"를 어떻게 보는가?
- Purpose: 왜 행동한다고 믿는가?
- Methods: 어떤 수단을 쓴다고 믿는가?
- Attributes: 본질적 특성은?

### Step 2: 이 Actor에 대해 말할 때 쓰는 메커니즘

이 담론들이 공통으로 쓰는 3-4개 메커니즘:
- 즉시_단정, 역사_투사, 필연적_인과, 네트워크_추론, 표면_부정

### Step 3: 추론 패턴

"{largest_actor}"에 대한 담론이 어떻게 전개되는가?
관찰 → (생략) → 결론

JSON:
{{
  "actor": {{
    "subject": "{largest_actor}",
    "purpose": "구체적 목적",
    "methods": ["수단1", "수단2", "수단3"],
    "perceived_attributes": ["특성1", "특성2"]
  }},
  "core_mechanisms": ["이 Actor 담론에서 자주 쓰는 메커니즘들"],
  "logic_pattern": {{
    "trigger": "시작점",
    "skipped_verification": "생략",
    "conclusion": "결론"
  }},
  "title": "세계관 제목",
  "description": "설명",
  "sample_count": {len(actor_groups[largest_actor])}
}}
"""


class DataDrivenWorldviewExperiment(WorldviewExperiment):
    """통계 기반 패턴 발견"""

    def __init__(self):
        super().__init__("Data-Driven-Worldview")

    def build_prompt(self, perceptions: List[Dict]) -> str:
        # 통계 분석
        stats = {
            "total": len(perceptions),
            "mechanisms": {},
            "actors": {},
            "logic_chains": []
        }

        for p in perceptions:
            # Mechanisms
            mechs = p.get('mechanisms', [])
            if mechs is None:
                mechs = []
            for mech in mechs:
                stats["mechanisms"][mech] = stats["mechanisms"].get(mech, 0) + 1

            # Actors
            actor = p.get('actor', {})
            if isinstance(actor, dict):
                subj = actor.get('subject', 'Unknown')
                # Ensure subject is hashable (string)
                if isinstance(subj, list):
                    subj = ', '.join(str(s) for s in subj)
                elif not isinstance(subj, str):
                    subj = str(subj)
                stats["actors"][subj] = stats["actors"].get(subj, 0) + 1

            # Logic chain 첫 단계
            logic = p.get('logic_chain', [])
            if logic and len(logic) > 0:
                stats["logic_chains"].append(logic[0])

        # Top mechanisms
        top_mechs = sorted(stats["mechanisms"].items(), key=lambda x: x[1], reverse=True)
        top_actors = sorted(stats["actors"].items(), key=lambda x: x[1], reverse=True)

        # Simplified sample data
        sample_data = []
        for p in perceptions[:5]:
            sample_data.append({
                'id': p.get('id'),
                'mechanisms': p.get('mechanisms', []),
                'actor': p.get('actor', {}),
                'logic_chain': p.get('logic_chain', [])[:3] if p.get('logic_chain') else []
            })

        return f"""
{len(perceptions)}개 담론 통계 분석:

## 메커니즘 빈도
{json.dumps(top_mechs, ensure_ascii=False, indent=2)}

## Actor 빈도
{json.dumps(top_actors, ensure_ascii=False, indent=2)}

## Logic Chain 시작점 샘플 (10개)
{json.dumps(stats["logic_chains"][:10], ensure_ascii=False, indent=2)}

전체 데이터 샘플:
{json.dumps(sample_data, ensure_ascii=False, indent=2)}

---

## 데이터 기반 세계관 발견

### 분석 기준

1. **유의미한 공출현**: 어떤 메커니즘들이 자주 함께 나타나는가?
2. **지배적 Actor**: 가장 자주 언급되는 Actor는?
3. **공통 Logic 패턴**: Logic Chain 시작점의 공통점은?

### 세계관 정의

위 통계를 바탕으로 가장 명확한 패턴을 정의하세요.

⚠️ 주의: 단순 빈도가 아닌 **의미있는 조합**을 찾으세요.
예: "즉시_단정 + 네트워크_추론"이 함께 나타나면 → "조직적 음모론 세계관"

JSON:
{{
  "pattern_type": "발견한 패턴 유형",
  "statistical_basis": {{
    "top_mechanisms": ["메커니즘들"],
    "top_actor": "Actor",
    "occurrence_count": 숫자
  }},
  "actor": {{
    "subject": "주체",
    "purpose": "목적",
    "methods": ["수단들"]
  }},
  "core_mechanisms": ["메커니즘들"],
  "logic_pattern": {{
    "trigger": "시작",
    "skipped_verification": "생략",
    "conclusion": "결론"
  }},
  "title": "세계관 제목",
  "description": "설명"
}}
"""


def run_experiments():
    """모든 실험 실행"""

    print("=" * 80)
    print("Claude Worldview Evolution 최적화 실험")
    print("=" * 80)

    # Get sample perceptions (200개 샘플)
    print("\n📊 샘플 데이터 로딩...")
    query = supabase.table('layered_perceptions')\
        .select('*')\
        .not_.is_('mechanisms', 'null')\
        .order('created_at', desc=True)\
        .limit(200)

    result = query.execute()
    perceptions = result.data

    print(f"   ✓ {len(perceptions)}개 perceptions 로딩 완료")

    # Run experiments
    experiments = [
        BaselineWorldviewExperiment(),
        PatternFirstWorldviewExperiment(),
        ActorCentricWorldviewExperiment(),
        DataDrivenWorldviewExperiment()
    ]

    results = {}

    for exp in experiments:
        print(f"\n{'=' * 80}")
        print(f"실험: {exp.name}")
        print(f"{'=' * 80}")

        try:
            worldview = exp.extract_worldview(perceptions)
            elapsed = worldview.pop('_elapsed_time', 0)

            results[exp.name] = {
                "worldview": worldview,
                "elapsed": elapsed,
                "success": True
            }

            print(f"\n✅ 완료 ({elapsed:.2f}초)")
            print(f"\n📋 결과:")
            print(f"   Title: {worldview.get('title', 'N/A')}")
            print(f"   Actor: {worldview.get('actor', {}).get('subject', 'N/A')}")
            print(f"   Mechanisms: {worldview.get('core_mechanisms', [])}")
            print(f"   Description: {worldview.get('description', 'N/A')[:100]}...")

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
        "sample_size": len(perceptions),
        "experiments": results
    }

    output_file = f"_test_results/worldview_evolution_experiments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 80}")
    print(f"✅ 실험 완료: {output_file}")
    print(f"{'=' * 80}")

    # Summary
    print(f"\n📊 요약:")
    for name, data in results.items():
        if data.get('success'):
            print(f"   {name}: {data['elapsed']:.2f}s ✅")
        else:
            print(f"   {name}: ❌ {data.get('error', 'Unknown error')}")


if __name__ == "__main__":
    run_experiments()
