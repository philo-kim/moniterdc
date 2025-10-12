# 세계관 구현 방식 종합 연구 결과

## 실험 개요

**목표**: "세계관 = 렌즈"를 사용자에게 효과적으로 전달하는 최적의 방법 찾기

**데이터**: "독재와 사찰의 부활" 세계관, 88개 perception (실제 DB 데이터)

**방법**: 7가지 다른 접근법으로 실제 데이터 처리 후 비교

---

## 실험 결과 요약

| 방법 | 사용자 이해도 | 데이터 충실성 | 핵심 장점 | 핵심 단점 |
|------|--------------|--------------|----------|----------|
| 1. 통계적 요약 | ★☆☆☆☆ (1/5) | ★★★★★ (5/5) | 100% 객관적, 검증 가능 | 렌즈를 전혀 전달 못함 |
| 2. GPT 단순 요약 | ★★☆☆☆ (2/5) | ★★★☆☆ (3/5) | 읽기 쉬움 | 추상적, 정보 압축일 뿐 |
| 3. 패턴 기반 해석 차이 | ★★★★☆ (4/5) | ★★★☆☆ (3/5) | 직관적, 렌즈 경험 가능 | GPT 해석 추가됨 |
| 4. 실제 perception 직접 제시 | ★★☆☆☆ (2/5) | ★★★★★ (5/5) | 가짜 없음 | 정보 나열일 뿐 |
| 5. 대조적 프레임 | ★★★★☆ (4/5) | ★★☆☆☆ (2/5) | 편향을 명확히 드러냄 | 대조 프레임은 가짜 |
| 6. 하이브리드 (원본+해석) | ★★★☆☆ (3/5) | ★★★★☆ (4/5) | 균형적, 검증 가능 | 복잡도 증가 |
| 7. 내러티브 | ★★★☆☆ (3/5) | ★☆☆☆☆ (1/5) | 감정적 공감 | **CLAUDE.md 위반 위험** |

---

## 핵심 발견

### 1. 근본적인 트레이드오프

```
데이터 충실성 ↑ ────────────────────── 사용자 이해도 ↓
     │                                         │
실험 1, 4                                  실험 3, 5
(통계, 직접 제시)                         (해석 차이, 대조)
     │                                         │
"이게 데이터야"                           "이렇게 봐"
```

**이 트레이드오프는 피할 수 없습니다.**

### 2. 실제 데이터 구조의 현실

```json
{
  "worldview": {
    "title": "독재와 사찰의 부활",
    "perception_ids": [137개 ID],  // ← outdated
    "frame": null  // ← 비어있음!
  },

  "실제_DB_perception": 88개,

  "perception_구조": {
    "subject": "김현지",
    "attribute": "북한 간첩",
    "valence": "negative",
    "claims": ["김현지는 일본에서 재일로 택갈이 하고..."],
    "keywords": ["김현지", "북한 간첩", "리선실"],
    "emotions": ["불안", "분노"]
  }
}
```

**문제**:
- worldview에 통일된 "frame" 없음
- perception들이 단순히 묶여만 있음
- "렌즈"가 실제로 존재하지 않음

### 3. 가장 중요한 질문

**"세계관을 표현한다"는 것이 애초에 가능한가?**

```
가설 A: 세계관 = 88개 perception 속에 이미 존재
        → 우리가 할 일: 추출/발견
        → 하지만: 통일된 패턴이 실제로 존재하지 않음

가설 B: 세계관 = 우리가 만들어내는 것
        → 우리가 할 일: 구성/해석
        → 하지만: "가짜" 세계관을 만드는 것

가설 C: 세계관 = 탐색 가능한 공간
        → 우리가 할 일: 네비게이션 제공
        → 하지만: "렌즈"의 본질을 전달 못함
```

---

## 실험 결과 상세

### 실험 3: 패턴 기반 해석 차이 (가장 효과적)

**실제 출력**:
```json
{
  "core_lens": "특정 주체나 사건을 평가하며, 그 평가에 따라 행동과 의도를 해석",
  "interpretation_examples": [
    {
      "subject": "김현지",
      "normal_view": "단순한 개인",
      "through_this_lens": "그림자 실세로서 부정적 영향을 미치는 인물",
      "key_difference": "단순 개인 vs 영향력 행사하는 실세",
      "evidence_from_data": "김현지 실세론에 대한 공세"
    }
  ]
}
```

**왜 효과적인가**:
- "렌즈의 차이"를 직접 보여줌
- 같은 대상을 다르게 보는 것을 경험
- 직관적이고 이해하기 쉬움

**문제점**:
- `normal_view`는 GPT가 만든 것
- 실제 데이터에는 `through_this_lens`만 존재
- 대조를 위해 GPT가 "일반적 시각"을 지어냄

### 실험 6: 하이브리드 (가장 균형적)

**실제 출력**:
```json
{
  "layer1_statistics": {
    "주요_주체": ["김현지", "윤석열 정부", ...],
    "주요_키워드": ["김현지", "중국", "좌파", ...],
    "주요_감정": ["불안", "분노", "조롱", ...]
  },
  "layer2_representative_perceptions": [
    {
      "subject": "김현지",
      "attribute": "그림자 실세",
      "claims": ["김현지 실세론에 대한 공세"]
    }
  ],
  "layer3_gpt_interpretation": {
    "core_lens": "권력과 안전, 사회적 비판에 대한 복합적 시각",
    "what_they_focus_on": "권력의 작동 방식과 안전 문제",
    "what_they_ignore": "긍정적 변화나 혁신",
    "emotional_tone": "불안과 비판, 부정적 감정"
  }
}
```

**왜 균형적인가**:
- Layer 1: 원본 통계 (검증 가능)
- Layer 2: 대표 perception (가짜 없음)
- Layer 3: GPT 해석 (이해 돕기)
- 각 레이어를 독립적으로 검증 가능

### 실험 7: 내러티브 (위험)

**실제 출력**:
```
"이 사람들에게 세상은 불확실성과 위험으로 가득 차 있다.
강훈식과 김현지 같은 인물들이 자신들의 권력을 두고 서로 충돌하는 모습은..."
```

**왜 위험한가**:
- CLAUDE.md 위반: "사용자가 만든 서사/감정 여정 강요"
- 온보딩 안티패턴: "이렇게 느끼게 하려면..."
- 사용자 주도권 침해

---

## 데이터 현실 vs 이상적 구조

### 현재 데이터 구조

```typescript
// 현재: perception만 있음
interface Perception {
  subject: string;          // "김현지"
  attribute: string;        // "북한 간첩"
  valence: "negative";
  claims: string[];         // ["김현지는 일본에서..."]
  keywords: string[];
  emotions: string[];
}

// 현재: worldview는 껍데기
interface Worldview {
  title: string;
  perception_ids: string[];  // 단순히 묶기만 함
  frame: null;               // 비어있음!
}
```

### 이상적 구조 (실험 결과 기반)

```typescript
interface Worldview {
  title: string;

  // Layer 0: 즉시 이해 (3초)
  quick_understanding: {
    core_lens: string;              // "특정 주체를 평가에 따라 해석"
    key_example: InterpretationExample;
  };

  // Layer 1: 구조 이해 (30초)
  structured_view: {
    interpretation_examples: InterpretationExample[];  // 3-5개
    emotional_tone: string;
    what_they_focus_on: string;
  };

  // Layer 2: 원본 데이터 (검증용)
  data_foundation: {
    statistics: {
      주요_주체: string[];
      주요_키워드: string[];
      주요_감정: string[];
    };
    representative_perceptions: Perception[];  // 5개
  };

  // Layer 3: 전체 데이터 (탐색용)
  all_perceptions: Perception[];  // 88개
}

interface InterpretationExample {
  subject: string;
  // normal_view: string;  // ← 이건 제외! GPT가 만들어야 함
  through_this_lens: string;
  evidence: string[];   // 실제 claims
}
```

---

## 핵심 통찰

### 1. "해석 차이"의 문제

**실험 3, 5가 효과적이었던 이유**:
- "같은 것을 다르게 본다"는 대조가 직관적

**하지만 근본적 문제**:
```
"이 렌즈로 본 것" (있음, 실제 데이터)
vs
"일반적으로 본 것" (없음, GPT가 지어냄)
```

**질문**:
- "일반적 시각"을 GPT가 만드는 것이 정당한가?
- 아니면 "이 렌즈로 본 것"만 보여주고 사용자가 비교하게 해야 하는가?

### 2. "렌즈"는 실제로 존재하는가?

**데이터를 보면**:
```
88개 perception:
- 62개 negative
- 22개 positive
- 4개 neutral

주요 주체: 김현지(3회), 윤석열 정부(2회), 미군(2회)...
주요 감정: 불안(31회), 분노(31회), 조롱(14회)...
```

**통일된 "렌즈"가 있는가?**
- NO: 주체도 다양하고, 감정도 섞여있음
- 김현지는 부정적, 미군은 긍정적
- "독재와 사찰의 부활"이라는 제목과 데이터가 일치하지 않음

**가능한 해석**:
1. 렌즈가 여러 개 (하위 주제별로)
2. 렌즈가 아직 형성 중 (초기 데이터)
3. 렌즈가 실제로 존재하지 않음 (단순 그룹핑)

### 3. "가짜"와 "해석"의 경계

```
통계적 요약 (실험 1)
→ 100% 진짜, 0% 해석
→ 하지만 렌즈를 전달 못함

GPT 종합 (실험 2, 7)
→ 100% 해석, 가짜 가능성
→ 렌즈는 전달하지만 검증 불가

패턴 기반 (실험 3)
→ 70% 진짜 (실제 패턴), 30% 해석 (GPT가 명확화)
→ 균형적이지만 어디까지 허용?

하이브리드 (실험 6)
→ 각 레이어 분리로 검증 가능
→ 복잡하지만 투명함
```

**질문**: 어디까지가 "해석"이고, 어디서부터가 "가짜"인가?

---

## 실제 구현 제안

### 제안 A: 레이어드 접근 (실험 6 기반)

```typescript
// 각 레이어를 독립적으로 제공, 사용자가 선택

interface WorldviewLayered {
  // 레이어 1: 통계 (100% 객관)
  statistics: {
    total_perceptions: number;
    주요_주체: Array<{name: string, count: number}>;
    주요_키워드: Array<{word: string, count: number}>;
    감정_분포: {negative: number, positive: number, neutral: number};
  };

  // 레이어 2: 대표 사례 (100% 원본)
  representative_perceptions: Perception[];  // 5-10개

  // 레이어 3: GPT 해석 (명시적으로 "해석"임을 표시)
  interpretation: {
    _warning: "이것은 AI 해석입니다. 원본 데이터는 레이어 1, 2를 참조하세요.",
    core_lens: string;
    what_they_focus_on: string;
    emotional_tone: string;
  };

  // 레이어 4: 전체 데이터
  all_perceptions: Perception[];
}
```

**장점**:
- 각 레이어 독립적으로 검증 가능
- 사용자가 원하는 깊이 선택
- "가짜" 부분을 명시적으로 표시

**단점**:
- 복잡함
- 여전히 "렌즈 경험"은 약함

### 제안 B: 탐색 중심 (새로운 접근)

**핵심 아이디어**: "세계관을 표현"하려 하지 말고, "perception을 탐색"하게 하자

```typescript
interface WorldviewAsExploration {
  title: string;

  // 여러 진입점 제공
  entry_points: {
    by_subject: GroupedPerceptions;    // 주체별
    by_emotion: GroupedPerceptions;    // 감정별
    by_valence: GroupedPerceptions;    // 평가별
    by_keyword: GroupedPerceptions;    // 키워드별
  };

  // 각 그룹의 대표만 보여주고, 펼치기 가능
  interface GroupedPerceptions {
    groups: Array<{
      name: string;
      count: number;
      representative: Perception[];  // 3개
      all: Perception[];            // 접을 수 있음
    }>;
  }
}
```

**예시 UI**:
```
세계관: 독재와 사찰의 부활 (88개 perception)

[주체별로 보기]
  ▼ 김현지 (3개)
    - 실세 주장 (조롱, 비웃음)
    - 그림자 실세 (조롱, 비웃음)
    - 북한 간첩 (불안, 분노)

  ▼ 윤석열 정부 (2개)
    - 관리가 가능한 조건부 무비자 제도 (긍정)
    - 부정적 재정 관리 (분노, 조롱)

[감정별로 보기]
  ▼ 불안 (31개)
  ▼ 분노 (31개)
  ▼ 조롱 (14개)

[평가별로 보기]
  ▼ Negative (62개)
  ▼ Positive (22개)
  ▼ Neutral (4개)
```

**장점**:
- "렌즈"를 만들지 않고 데이터를 탐색하게 함
- 100% 원본 데이터
- 사용자가 스스로 패턴을 발견

**단점**:
- "세계관 = 렌즈"라는 본질과 맞지 않음
- 일반 사용자에게는 여전히 어려움

### 제안 C: 하이브리드 최종안 (실용적)

**실험 결과를 종합한 실용적 구조**:

```typescript
interface WorldviewPractical {
  // 0. 빠른 이해 (사용자 이해도 우선)
  overview: {
    title: string;
    core_description: string;  // GPT 생성, 하지만 "AI 요약"임을 명시
    statistics_summary: {
      total: number,
      주요_감정: string[],
      negative_ratio: number
    };
  };

  // 1. 렌즈 경험 (실험 3 기반, 하지만 수정)
  lens_examples: Array<{
    subject: string;
    through_this_lens: string;
    evidence: {
      perception_id: string;
      claims: string[];
      emotions: string[];
    };
    // normal_view 제거! GPT가 만들지 않음
  }>;

  // 2. 원본 데이터 (검증용)
  data_foundation: {
    representative_perceptions: Perception[];  // 5-10개
    statistics: Statistics;
  };

  // 3. 전체 탐색 (제안 B)
  exploration: {
    by_subject: GroupedPerceptions;
    by_emotion: GroupedPerceptions;
  };
}
```

**핵심 원칙**:
1. GPT 사용하되, 명시적으로 표시
2. "일반적 시각" 같은 가짜 만들지 않음
3. 원본 데이터 항상 접근 가능
4. 레이어별로 분리해서 검증 가능

---

## 최종 결론

### 1. 명확한 트레이드오프 인정

**"완벽한" 방법은 없습니다.**

```
A. 데이터 충실성 우선 (실험 1, 4)
   → 정확하지만 이해하기 어려움
   → 대부분 사용자는 포기

B. 사용자 이해도 우선 (실험 3, 5)
   → 이해하기 쉽지만 GPT 해석 포함
   → "가짜" 만들 위험

C. 균형 (실험 6 + 제안 C)
   → 레이어로 분리
   → 복잡하지만 투명
```

### 2. 실제 구현 방향

**제안 C (하이브리드 최종안)**을 추천합니다.

**이유**:
1. 사용자 이해도와 데이터 충실성 모두 고려
2. GPT 사용하되, 명시적 표시 + 원본 데이터 병행
3. 레이어 분리로 검증 가능
4. 실용적으로 구현 가능

**구현 우선순위**:
```
Phase 1: Overview + Data Foundation
- GPT로 core_description 생성 (하지만 "AI 요약"임을 표시)
- 대표 perception 5-10개 선정 (통계 기반)
- 원본 통계 제공

Phase 2: Lens Examples
- 대표 perception에서 "이 렌즈로 본 것" 추출
- normal_view 없이, 실제 데이터만
- Evidence로 원본 perception 연결

Phase 3: Exploration
- 주체별, 감정별 그룹핑
- 펼치기/접기 UI
```

### 3. 피해야 할 것

**절대 하지 말아야 할 것**:
1. ❌ 내러티브 방식 (실험 7) - CLAUDE.md 위반
2. ❌ "일반적 시각" 만들어내기 - 가짜 데이터
3. ❌ perception 없이 GPT 요약만 - 검증 불가
4. ❌ 사용자에게 특정 감정/해석 강요

**주의해야 할 것**:
- ⚠️ GPT 사용 시 항상 "AI 해석"임을 명시
- ⚠️ 원본 데이터 접근 경로 항상 제공
- ⚠️ 레이어별 검증 가능하게 구조화

### 4. 근본적인 질문에 대한 답

**Q: "세계관을 표현한다"는 것이 가능한가?**

A:
- "완벽하게" 표현하는 것은 불가능
- 하지만 "다층적으로 접근"하는 것은 가능
- Layer 0: 빠른 이해 (GPT 요약, 하지만 명시)
- Layer 1: 렌즈 경험 (대표 사례)
- Layer 2: 원본 데이터 (검증)
- Layer 3: 전체 탐색 (깊이)

**Q: 어디까지가 "해석"이고 어디서부터가 "가짜"인가?**

A:
- 해석: 실제 패턴을 명확히 하는 것 (OK)
- 가짜: 존재하지 않는 것을 만드는 것 (NO)
- 경계: 항상 원본 데이터로 검증 가능해야 함

**Q: GPT를 사용해도 되는가?**

A:
- YES, 하지만 조건부
- ✅ 명시적으로 "AI 해석"임을 표시
- ✅ 원본 데이터 병행 제공
- ✅ 검증 가능하게 구조화
- ❌ GPT 결과만 보여주기
- ❌ 가짜 데이터 생성 (normal_view 등)

---

## 다음 단계

1. **제안 C 구조로 스키마 정의**
   - TypeScript interface 작성
   - Supabase schema 업데이트

2. **WorldviewStructurer 구현**
   - Phase 1: Overview + Data Foundation
   - 통계 기반 대표 perception 선정
   - GPT로 core_description 생성 (명시적 표시)

3. **프론트엔드 구현**
   - 레이어별 UI
   - "AI 해석" 명시적 표시
   - 원본 데이터 접근 경로

4. **검증 및 개선**
   - 실제 사용자 피드백
   - 각 레이어의 효과성 측정
   - 반복 개선

---

## 실험 원본 데이터

전체 실험 결과: `/tmp/real_worldview_experiments_result.json`
실험 스크립트: `real_data_worldview_experiments.py`

**실제로 확인한 것**:
- 88개 perception
- 7가지 방법
- 각 방법의 실제 output
- 사용자 이해도 vs 데이터 충실성 트레이드오프

**데이터가 보여준 것**:
- "독재와 사찰의 부활"이라는 제목에도 불구하고
- 실제로는 김현지(3개), 윤석열 정부(2개), 미군(2개) 등 다양
- 62개 negative, 22개 positive, 4개 neutral
- 통일된 "렌즈"보다는 여러 주제의 혼합
