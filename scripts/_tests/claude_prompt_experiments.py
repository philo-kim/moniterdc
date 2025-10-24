#!/usr/bin/env python3
"""
Claude 프롬프트 개선 실험

여러 프롬프트 전략을 테스트하여 최적의 결과를 찾음:
1. Baseline: 현재 GPT 프롬프트 그대로
2. Structured: 더 구조화된 예시와 단계별 가이드
3. Chain-of-Thought: 추론 과정을 명시적으로 요구
4. Korean-Optimized: 한국어 담론에 특화된 프롬프트
5. Expert Persona: 전문가 페르소나 부여
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


class PromptExperiment:
    """프롬프트 실험 베이스 클래스"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def build_prompt(self, content: Dict) -> str:
        """프롬프트 생성 (각 실험에서 구현)"""
        raise NotImplementedError

    def extract(self, content: Dict) -> Dict:
        """Claude로 추출"""
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


class BaselineExperiment(PromptExperiment):
    """실험 1: Baseline - 현재 GPT 프롬프트 그대로"""

    def __init__(self):
        super().__init__(
            "Baseline",
            "현재 GPT 프롬프트를 Claude에 그대로 적용"
        )

    def build_prompt(self, content: Dict) -> str:
        return f"""
다음은 DC Gallery 정치 갤러리의 글입니다:

제목: {content['title']}
내용: {content['body'][:2000]}

이 글을 **3개 층위**로 분석해주세요.

⚠️ 중요: 일반론이 아닌, **이 글쓴이가 실제로 믿는 구체적인 내용**을 추출하세요.

## 1. 표면층 (Explicit Layer) - 명시적 주장
**글에서 직접 말하고 있는 것**

## 2. 암묵층 (Implicit Layer) - 전제하는 사고
**말하지 않았지만 당연하게 여기는 것**

## 3. 심층 (Deep Layer) - 무의식적 믿음
**이 글쓴이 진영만의 세계관**

JSON 형식:
{{
  "explicit_claims": [...],
  "implicit_assumptions": [...],
  "reasoning_gaps": [...],
  "deep_beliefs": [...],
  "worldview_hints": "..."
}}
"""


class StructuredExperiment(PromptExperiment):
    """실험 2: Structured - 더 구조화된 예시와 단계별 가이드"""

    def __init__(self):
        super().__init__(
            "Structured",
            "구체적인 예시와 체크리스트를 제공하여 더 정확한 추출 유도"
        )

    def build_prompt(self, content: Dict) -> str:
        return f"""
당신은 한국 정치 담론 분석 전문가입니다.

다음 DC Gallery 글을 **3개 층위**로 분석하세요:

제목: {content['title']}
내용: {content['body'][:2000]}

---

## 분석 프레임워크

### Layer 1: Explicit (표면층) - 직접 말한 것
**추출 기준:**
- [ ] 구체적 인물/조직 이름이 명시되었는가?
- [ ] 특정 행동/사건을 지적하는가?
- [ ] 원문에서 직접 인용 가능한가?

**예시:**
- ✅ "민주당이 통신사를 협박해서 정보를 얻었다"
- ❌ "정치인들은 권력을 남용한다" (너무 일반적)

### Layer 2: Implicit (암묵층) - 전제하는 것
**추출 기준:**
- [ ] 명시되지 않았지만 **당연하게 가정**하는 것
- [ ] "왜 이런 결론에 도달했는가?"의 답
- [ ] 생략된 중간 단계

**예시:**
- ✅ "이들은 사법부까지 장악하려 한다" (목적 추론)
- ❌ "사찰은 나쁘다" (누구나 동의하는 일반론)

### Layer 3: Deep (심층) - 세계관
**추출 기준:**
- [ ] **이 진영만의** 독특한 역사 해석
- [ ] 상대편의 **본질**에 대한 규정
- [ ] 세상의 **작동 원리**에 대한 믿음

**예시:**
- ✅ "좌파는 본질적으로 독재적이다" (진영 고유의 관점)
- ❌ "권력은 부패한다" (보편적 격언)

---

## 출력 형식

각 층위마다:
1. **구체성**: 일반론 피하고 이 글 고유의 내용
2. **인용 근거**: 원문의 어느 부분에서 나왔는지
3. **명확성**: 모호한 표현 피하기

JSON:
{{
  "explicit_claims": [
    {{
      "subject": "구체적 주체",
      "predicate": "구체적 행위/주장",
      "evidence_cited": "원문 근거",
      "quote": "직접 인용"
    }}
  ],
  "implicit_assumptions": [
    "구체적이고 이 글 고유의 전제"
  ],
  "reasoning_gaps": [
    {{
      "from": "A",
      "to": "B",
      "gap": "생략된 검증 단계"
    }}
  ],
  "deep_beliefs": [
    "이 진영만의 독특한 세계관"
  ],
  "worldview_hints": "핵심 패턴 요약"
}}
"""


class ChainOfThoughtExperiment(PromptExperiment):
    """실험 3: Chain-of-Thought - 추론 과정을 단계별로 요구"""

    def __init__(self):
        super().__init__(
            "Chain-of-Thought",
            "분석 과정을 단계별로 명시하도록 요구하여 더 깊은 이해 유도"
        )

    def build_prompt(self, content: Dict) -> str:
        return f"""
다음 글을 3개 층위로 분석하되, **생각 과정을 단계별로 보여주세요**.

제목: {content['title']}
내용: {content['body'][:2000]}

---

## Step 1: 원문 이해
먼저 이 글의 핵심 메시지를 한 문장으로 요약하세요.

## Step 2: Explicit Layer (표면층)
글에서 **직접 언급된** 것을 찾으세요:
- 누구를 비난하는가?
- 무엇을 문제 삼는가?
- 어떤 증거를 제시하는가?

**생각 과정:**
1. 주어 찾기: [누가?]
2. 서술어 찾기: [무엇을 했다?]
3. 근거 찾기: [어떤 증거?]

## Step 3: Implicit Layer (암묵층)
**"왜?"를 3번 물어보세요:**
1. 왜 이런 주장을 하는가?
   → 전제: [...]
2. 왜 이것이 문제인가?
   → 전제: [...]
3. 왜 이런 방식으로 표현했는가?
   → 전제: [...]

## Step 4: Reasoning Gaps
A에서 B로 가는 논리를 검증하세요:
- 생략된 단계는 무엇인가?
- 어떤 가정이 숨어있는가?

## Step 5: Deep Layer (심층)
이 진영의 독특한 관점을 찾으세요:
- **역사 해석**: 과거를 어떻게 보는가?
- **본질 규정**: 상대를 어떻게 규정하는가?
- **인과 구조**: 세상이 어떻게 작동한다고 보는가?

---

최종 출력 (JSON):
{{
  "thinking_process": "단계별 분석 과정 요약",
  "explicit_claims": [...],
  "implicit_assumptions": [...],
  "reasoning_gaps": [...],
  "deep_beliefs": [...],
  "worldview_hints": "..."
}}
"""


class KoreanOptimizedExperiment(PromptExperiment):
    """실험 4: Korean-Optimized - 한국어 담론 특성에 최적화"""

    def __init__(self):
        super().__init__(
            "Korean-Optimized",
            "한국 정치 담론의 특수성을 고려한 프롬프트"
        )

    def build_prompt(self, content: Dict) -> str:
        return f"""
당신은 한국 정치 담론 전문 분석가입니다.

**한국 온라인 정치 담론의 특징:**
- 과거사(독재, 민주화)를 현재에 투사
- 진영 간 본질적 차이 강조 (좌파 vs 우파)
- 극단적 표현과 은유 사용
- 음모론적 사고 패턴

다음 DC 갤러리 글을 분석하세요:

제목: {content['title']}
내용: {content['body'][:2000]}

---

## 분석 가이드

### 1. 표면층 (명시적 주장)
**이 글이 직접 말하는 것:**
- 비난 대상: [누구?]
- 비난 내용: [무엇을 했다?]
- 제시 증거: [어떤 근거?]

### 2. 암묵층 (숨은 전제)
**한국 정치 담론에서 흔한 패턴:**
- [ ] 과거사 연결: "과거 XX처럼 지금도..."
- [ ] 본질 규정: "이들은 원래..."
- [ ] 음모 추론: "배후에는...", "사실은..."
- [ ] 도미노 논리: "이것이 계속되면..."

**이 글의 숨은 전제:**

### 3. 추론 간극
**비약된 논리:**
- 어떤 검증을 생략했는가?
- 다른 가능성은 왜 배제했는가?

### 4. 심층 (세계관)
**이 진영의 독특한 관점:**
- 역사 인식: [과거 → 현재 연결]
- 본질론: [상대 = ?]
- 작동 원리: [세상은 어떻게 돌아가는가]

---

JSON 형식:
{{
  "explicit_claims": [
    {{
      "subject": "구체적 주체",
      "predicate": "구체적 행위",
      "evidence_cited": "원문 근거",
      "quote": "직접 인용"
    }}
  ],
  "implicit_assumptions": [
    "한국 정치 담론 특성이 반영된 구체적 전제"
  ],
  "reasoning_gaps": [
    {{
      "from": "관찰된 사실",
      "to": "내린 결론",
      "gap": "생략된 검증 (한국 맥락 고려)"
    }}
  ],
  "deep_beliefs": [
    "한국 현대사 인식이 반영된 세계관"
  ],
  "worldview_hints": "핵심 패턴 (과거사/본질론/음모론 중 어느 것)"
}}
"""


class ExpertPersonaExperiment(PromptExperiment):
    """실험 5: Expert Persona - 전문가 역할 부여"""

    def __init__(self):
        super().__init__(
            "Expert-Persona",
            "구체적인 전문가 페르소나를 부여하여 더 깊은 분석 유도"
        )

    def build_prompt(self, content: Dict) -> str:
        return f"""
당신은 다음 전문성을 가진 분석가입니다:

**전문 분야:**
- 담론 분석 (Discourse Analysis) 박사
- 한국 현대 정치사 연구 15년
- 온라인 커뮤니티 담론 전문가
- 인지심리학 기반 세계관 연구

**분석 접근:**
당신은 표면적 주장 이면의 **인지 구조**를 파악합니다.
사람들이 "왜 이렇게 생각하는가"에 집중합니다.

---

다음 글을 분석하세요:

제목: {content['title']}
내용: {content['body'][:2000]}

---

## 전문가 분석 프레임

### Phase 1: 텍스트 표면 분석
**질문:** 이 사람은 무엇을 말하고 있는가?
**방법:** 명시적 주장, 인용, 증거 추출

### Phase 2: 인지 구조 분석
**질문:** 이 사람은 어떤 사고 틀을 가지고 있는가?
**방법:**
- Schema: 어떤 틀로 세상을 보는가?
- Heuristics: 어떤 사고 지름길을 쓰는가?
- Confirmation Bias: 무엇을 선택적으로 보는가?

### Phase 3: 세계관 추론
**질문:** 이 진영은 세상을 어떻게 이해하는가?
**방법:**
- 역사 내러티브 재구성
- 인과 모델 추출
- 본질주의적 범주화 발견

---

**전문가 의견:**

{{
  "surface_analysis": {{
    "explicit_claims": [
      {{
        "subject": "...",
        "predicate": "...",
        "evidence_cited": "...",
        "quote": "..."
      }}
    ]
  }},
  "cognitive_structure": {{
    "implicit_assumptions": ["..."],
    "reasoning_gaps": [
      {{
        "from": "...",
        "to": "...",
        "gap": "...",
        "cognitive_bias": "어떤 편향?"
      }}
    ]
  }},
  "worldview_analysis": {{
    "deep_beliefs": ["..."],
    "historical_narrative": "과거를 어떻게 보는가",
    "causal_model": "세상의 작동 원리",
    "worldview_hints": "..."
  }},
  "expert_assessment": "이 담론의 핵심 특징은..."
}}
"""


def run_experiment(experiment: PromptExperiment, content: Dict) -> Tuple[str, Dict, float]:
    """실험 실행 및 결과 반환"""
    import time

    print(f"\n{'='*80}")
    print(f"실험: {experiment.name}")
    print(f"설명: {experiment.description}")
    print(f"{'='*80}")

    start = time.time()
    result = experiment.extract(content)
    elapsed = time.time() - start

    print(f"✓ 완료 ({elapsed:.2f}초)")

    # 결과 요약
    explicit_count = len(result.get('explicit_claims', []))
    implicit_count = len(result.get('implicit_assumptions', []))
    deep_count = len(result.get('deep_beliefs', []))

    print(f"  추출: Explicit {explicit_count} | Implicit {implicit_count} | Deep {deep_count}")

    return experiment.name, result, elapsed


def compare_experiments(results: List[Tuple[str, Dict, float]], content: Dict):
    """실험 결과 비교"""

    print(f"\n{'='*80}")
    print(f"실험 결과 비교")
    print(f"{'='*80}")

    # 추출 개수 비교
    print(f"\n📊 레이어별 추출 개수:")
    print(f"{'실험':<20} {'Explicit':>10} {'Implicit':>10} {'Deep':>10} {'시간':>8}")
    print(f"{'-'*70}")

    for name, result, elapsed in results:
        explicit_count = len(result.get('explicit_claims', []))
        implicit_count = len(result.get('implicit_assumptions', []))
        deep_count = len(result.get('deep_beliefs', []))

        print(f"{name:<20} {explicit_count:>10} {implicit_count:>10} {deep_count:>10} {elapsed:>7.2f}s")

    # 품질 비교 (Deep Beliefs 샘플)
    print(f"\n💭 Deep Beliefs 비교 (각 실험의 첫 2개):")
    for name, result, _ in results:
        print(f"\n[{name}]")
        for i, belief in enumerate(result.get('deep_beliefs', [])[:2], 1):
            print(f"  {i}. {belief}")

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

    output_file = f"_test_results/prompt_experiments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
        BaselineExperiment(),
        StructuredExperiment(),
        ChainOfThoughtExperiment(),
        KoreanOptimizedExperiment(),
        ExpertPersonaExperiment()
    ]

    # 모든 실험 실행
    results = []
    for exp in experiments:
        try:
            name, result, elapsed = run_experiment(exp, content)
            results.append((name, result, elapsed))
        except Exception as e:
            print(f"❌ 오류: {e}")
            continue

    # 비교
    compare_experiments(results, content)


if __name__ == "__main__":
    main()
