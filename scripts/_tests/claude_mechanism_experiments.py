#!/usr/bin/env python3
"""
Claude 5 Mechanisms 추출 최적화 실험

현재 GPT-4o로 추출하는 5가지 추론 메커니즘을:
1. 즉시_단정 (Instant Conclusion)
2. 역사_투사 (Historical Projection)
3. 필연적_인과 (Inevitable Causation)
4. 네트워크_추론 (Network Reasoning)
5. 표면_부정 (Surface Negation)

Claude로 더 정확하게 추출하도록 프롬프트 최적화
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Tuple
from anthropic import Anthropic
from dotenv import load_dotenv
import sys
sys.path.insert(0, '/Users/taehyeonkim/dev/minjoo/moniterdc')

from engines.utils.supabase_client import get_supabase

load_dotenv()
claude_client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
supabase = get_supabase()


class MechanismExperiment:
    """메커니즘 추출 실험"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def build_prompt(self, content: Dict) -> str:
        raise NotImplementedError

    def extract(self, content: Dict) -> Dict:
        prompt = self.build_prompt(content)

        message = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

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
        return result


class BaselineMechanismExperiment(MechanismExperiment):
    """실험 1: Baseline - 현재 GPT 프롬프트"""

    def __init__(self):
        super().__init__(
            "Baseline-Mechanism",
            "현재 GPT 프롬프트를 그대로 사용"
        )

    def build_prompt(self, content: Dict) -> str:
        return f"""
다음은 DC Gallery 정치 담론입니다:

제목: {content['title']}
내용: {content['body'][:2000]}

---

이 담론의 **추론 구조**를 분석하세요.

## 분석 항목

### 1. Mechanisms (추론 메커니즘)
다음 5가지 메커니즘 중 사용된 것을 모두 찾으세요:

- **즉시_단정**: 관찰 → (검증 생략) → 결론
- **역사_투사**: 과거 패턴 → 현재 반복
- **필연적_인과**: X → 반드시 Y
- **네트워크_추론**: 연결 → 조직적 공모
- **표면_부정**: 표면 X / 실제 Y

### 2. Actor (행위 주체)
- subject: 누가?
- purpose: 목적은?
- methods: 수단은?

### 3. Logic Chain (추론 흐름)
단계별 추론 과정

JSON 형식:
{{
  "mechanisms": ["즉시_단정", "필연적_인과"],
  "actor": {{
    "subject": "민주당/좌파",
    "purpose": "권력 유지",
    "methods": ["사찰", "협박"]
  }},
  "logic_chain": [
    "민주당이 정보를 파악했다",
    "합법 취득 가능성을 배제했다",
    "불법 사찰로 단정했다"
  ],
  "explicit_claims": ["..."],
  "implicit_assumptions": ["..."],
  "deep_beliefs": ["..."]
}}
"""


class ExplainedMechanismExperiment(MechanismExperiment):
    """실험 2: 메커니즘별 상세 설명 제공"""

    def __init__(self):
        super().__init__(
            "Explained-Mechanism",
            "각 메커니즘을 구체적 예시와 함께 설명"
        )

    def build_prompt(self, content: Dict) -> str:
        return f"""
다음 담론의 추론 구조를 분석하세요:

제목: {content['title']}
내용: {content['body'][:2000]}

---

## 5가지 추론 메커니즘 (하나 이상 해당)

### 1. 즉시_단정 (Instant Conclusion)
**정의**: 관찰 → (검증 생략) → 결론

**예시**:
- "유심교체를 알았다" → (어떻게 알았는지 검증 X) → "통신사 협박했다"
- "판사를 안다" → (왜 아는지 확인 X) → "사찰했다"

**패턴**: "~했다면 틀림없이 ~이다"

### 2. 역사_투사 (Historical Projection)
**정의**: 과거 패턴 → 현재 동일하게 반복

**예시**:
- "과거 독재정권이 사찰했다" → "지금도 사찰한다"
- "옛날 좌파가 폭력적이었다" → "지금도 폭력적이다"

**패턴**: "과거 XX처럼 지금도..."

### 3. 필연적_인과 (Inevitable Causation)
**정의**: X → 필연적으로/반드시 Y

**예시**:
- "지금 작은 사찰" → "반드시 전면 감시사회"
- "사법부 장악" → "필연적으로 독재"

**패턴**: "~하면 반드시/필연적으로 ~한다"

### 4. 네트워크_추론 (Network Reasoning)
**정의**: 점 연결 → 조직적 공모

**예시**:
- "A가 B를 안다 + B가 C를 안다" → "조직적 네트워크"
- "여러 사건 발생" → "배후 세력의 계획"

**패턴**: "우연이 아니라 조직적으로..."

### 5. 표면_부정 (Surface Negation)
**정의**: 표면적 X / 실제로는 Y

**예시**:
- "민주주의라고 하지만 / 실제는 독재"
- "법 준수한다지만 / 사실은 불법"

**패턴**: "~라고 하지만 실제로는..."

---

JSON:
{{
  "mechanisms": ["사용된 메커니즘들"],
  "mechanism_evidence": {{
    "즉시_단정": "어떤 부분에서?",
    "역사_투사": "어떤 부분에서?"
  }},
  "actor": {{
    "subject": "...",
    "purpose": "...",
    "methods": [...]
  }},
  "logic_chain": [...],
  "explicit_claims": [...],
  "implicit_assumptions": [...],
  "deep_beliefs": [...]
}}
"""


class StepByStepMechanismExperiment(MechanismExperiment):
    """실험 3: 단계별 분석 요구"""

    def __init__(self):
        super().__init__(
            "StepByStep-Mechanism",
            "메커니즘을 단계별로 찾도록 유도"
        )

    def build_prompt(self, content: Dict) -> str:
        return f"""
다음 담론을 단계별로 분석하세요:

제목: {content['title']}
내용: {content['body'][:2000]}

---

## Step 1: 추론 흐름 파악
이 글쓴이의 생각 흐름을 단계별로 정리하세요.

예: "A를 관찰했다 → B라고 추론했다 → C라고 결론내렸다"

## Step 2: 검증 생략 확인 (즉시_단정)
어떤 검증 단계를 생략했나요?

- [ ] A → B: 중간 검증 없이 바로 단정
- [ ] B → C: 다른 가능성 배제하고 즉시 결론

## Step 3: 과거 연결 확인 (역사_투사)
과거 사례를 현재에 투사하나요?

- [ ] "과거 XX처럼 지금도..."
- [ ] "역사가 반복된다"

## Step 4: 필연성 확인 (필연적_인과)
"반드시", "필연적으로" 같은 표현이 있나요?

- [ ] "A면 반드시 B다"
- [ ] "결국 C가 될 것이다"

## Step 5: 네트워크 확인 (네트워크_추론)
여러 점을 연결해 조직적 공모를 주장하나요?

- [ ] "우연이 아니라 조직적"
- [ ] "배후에 세력이 있다"

## Step 6: 표면/실제 대비 (표면_부정)
표면과 실제를 대비하나요?

- [ ] "~라고 하지만 실제로는..."
- [ ] "겉으로는 X / 속으로는 Y"

---

JSON:
{{
  "analysis_steps": "단계별 분석 과정",
  "mechanisms": ["발견된 메커니즘"],
  "actor": {{"subject": "...", "purpose": "...", "methods": [...]}},
  "logic_chain": [...],
  "explicit_claims": [...],
  "implicit_assumptions": [...],
  "deep_beliefs": [...]
}}
"""


class PatternMatchingExperiment(MechanismExperiment):
    """실험 4: 패턴 매칭 기반"""

    def __init__(self):
        super().__init__(
            "Pattern-Matching",
            "언어 패턴으로 메커니즘 탐지"
        )

    def build_prompt(self, content: Dict) -> str:
        return f"""
다음 담론에서 추론 메커니즘을 찾으세요:

제목: {content['title']}
내용: {content['body'][:2000]}

---

## 메커니즘 탐지 패턴

각 메커니즘의 언어 패턴을 찾으세요:

### 즉시_단정
**언어 패턴**:
- "~했다면", "~라는 건"
- "틀림없이", "분명히", "확실히"
- "~일 수밖에 없다"

**논리 패턴**:
- 중간 검증 없이 A → B

### 역사_투사
**언어 패턴**:
- "과거 ~처럼", "예전 ~와 똑같이"
- "또", "또다시", "다시"
- "역사가 반복"

**논리 패턴**:
- 과거 사례 언급 + 현재 동일화

### 필연적_인과
**언어 패턴**:
- "반드시", "필연적으로", "당연히"
- "~하면 ~한다" (강한 인과)
- "결국", "결국엔"

**논리 패턴**:
- X → 필연적 Y

### 네트워크_추론
**언어 패턴**:
- "연결", "관계", "네트워크"
- "우연이 아니다", "조직적"
- "배후", "세력"

**논리 패턴**:
- 여러 점 연결 → 공모

### 표면_부정
**언어 패턴**:
- "~라고 하지만", "~인 척"
- "겉으로는 ~ / 실제로는 ~"
- "표면적", "실제로"

**논리 패턴**:
- 표면 X vs 실제 Y 대비

---

JSON:
{{
  "detected_patterns": {{
    "즉시_단정": ["발견된 언어 패턴"],
    "역사_투사": ["발견된 언어 패턴"]
  }},
  "mechanisms": ["확인된 메커니즘"],
  "actor": {{"subject": "...", "purpose": "...", "methods": [...]}},
  "logic_chain": [...],
  "explicit_claims": [...],
  "implicit_assumptions": [...],
  "deep_beliefs": [...]
}}
"""


def run_experiment(experiment: MechanismExperiment, content: Dict) -> Tuple[str, Dict, float]:
    """실험 실행"""
    import time

    print(f"\n{'='*80}")
    print(f"실험: {experiment.name}")
    print(f"{'='*80}")

    start = time.time()
    result = experiment.extract(content)
    elapsed = time.time() - start

    print(f"✓ 완료 ({elapsed:.2f}초)")

    mechanisms = result.get('mechanisms', [])
    print(f"  발견된 메커니즘: {mechanisms}")

    return experiment.name, result, elapsed


def compare_mechanism_experiments(results: List[Tuple[str, Dict, float]], content: Dict):
    """실험 결과 비교"""

    print(f"\n{'='*80}")
    print(f"메커니즘 추출 실험 비교")
    print(f"{'='*80}")

    # 메커니즘 개수 비교
    print(f"\n📊 추출된 메커니즘:")
    print(f"{'실험':<25} {'메커니즘':>40} {'개수':>6} {'시간':>8}")
    print(f"{'-'*85}")

    for name, result, elapsed in results:
        mechanisms = result.get('mechanisms', [])
        mechanism_str = ', '.join(mechanisms) if mechanisms else "없음"
        count = len(mechanisms)

        print(f"{name:<25} {mechanism_str:>40} {count:>6} {elapsed:>7.2f}s")

    # Actor 비교
    print(f"\n🎯 Actor 분석 비교:")
    for name, result, _ in results:
        actor = result.get('actor', {})
        if actor:
            print(f"\n[{name}]")
            print(f"  Subject: {actor.get('subject', 'N/A')}")
            print(f"  Purpose: {actor.get('purpose', 'N/A')}")
            print(f"  Methods: {actor.get('methods', [])}")

    # Logic Chain 비교
    print(f"\n🔗 Logic Chain 비교 (첫 3단계):")
    for name, result, _ in results:
        chain = result.get('logic_chain', [])
        if chain:
            print(f"\n[{name}]")
            for i, step in enumerate(chain[:3], 1):
                print(f"  {i}. {step}")

    # 저장
    comparison_data = {
        "content": {
            "id": content['id'],
            "title": content['title']
        },
        "experiments": [
            {
                "name": name,
                "result": result,
                "elapsed": elapsed
            }
            for name, result, elapsed in results
        ]
    }

    output_file = f"_test_results/mechanism_experiments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 비교 결과 저장: {output_file}")


def main():
    """메인 실행"""

    # Get test content
    result = supabase.table('contents').select('*').limit(1).order('published_at', desc=True).execute()
    content = result.data[0]

    print(f"테스트 Content:")
    print(f"  제목: {content['title']}")
    print(f"  내용: {content['body'][:200]}...")

    # 실험 정의
    experiments = [
        BaselineMechanismExperiment(),
        ExplainedMechanismExperiment(),
        StepByStepMechanismExperiment(),
        PatternMatchingExperiment()
    ]

    # 모든 실험 실행
    results = []
    for exp in experiments:
        try:
            name, result, elapsed = run_experiment(exp, content)
            results.append((name, result, elapsed))
        except Exception as e:
            print(f"❌ 오류: {e}")
            import traceback
            traceback.print_exc()
            continue

    # 비교
    if results:
        compare_mechanism_experiments(results, content)
    else:
        print("❌ 실행된 실험이 없습니다")


if __name__ == "__main__":
    main()
