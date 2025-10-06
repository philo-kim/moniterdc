# 전체 시스템 구성 - 완전판

## 🎯 시스템 목적

**DC Gallery 사용자들의 세계관을 구성하여, 여당 지지자들이 그 맥락을 이해할 수 있게 함**

---

## 📊 데이터베이스 구조

### 현재 데이터 현황

| 테이블 | 레코드 수 | 설명 |
|--------|----------|------|
| `contents` | 297개 | DC Gallery 원본 글 |
| `layered_perceptions` | 297개 | 3-layer 분석 결과 |
| `belief_patterns` | 552개 | 정규화된 믿음 |
| `worldviews` | 16개 (신규 6개) | 세계관 |
| `perception_worldview_links` | 26개 | Perception ↔ Worldview 연결 |

---

## 🔄 전체 데이터 파이프라인

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: 데이터 수집                                         │
└─────────────────────────────────────────────────────────────┘

  DC Gallery (정치 갤러리)
         ↓
  [크롤러] → contents 테이블 (297개)
         ↓
  {
    id: UUID
    title: "민주, 지귀연 핸드폰 교체 어떻게 알았나"
    body: "유심교체를 어떻게 알았냐..."
    gallery_id: "politics"
    created_at: timestamp
  }


┌─────────────────────────────────────────────────────────────┐
│ Phase 2: 3-Layer 분석 (맥락 추출)                            │
└─────────────────────────────────────────────────────────────┘

  contents (297개)
         ↓
  [LayeredPerceptionExtractor] (GPT-4o-mini)
         ↓
  layered_perceptions 테이블 (297개)
         ↓
  {
    id: UUID
    content_id: UUID

    // 표면층: 명시적 주장
    explicit_claims: [
      {
        subject: "민주당",
        predicate: "유심교체 정보를 불법으로 얻었다",
        evidence_cited: "나경원 의원 SNS",
        quote: "유심교체를 어떻게 알아"
      }
    ],

    // 암묵층: 전제하는 사고
    implicit_assumptions: [
      "민주당은 통신사를 협박해서 개인 사찰용 정보를 얻는다",
      "맘에 안드는 판사를 제거하기 위해 사찰한다"
    ],

    // 논리 비약
    reasoning_gaps: [
      {
        from: "유심교체 정보를 알았다",
        to: "통신사 협박으로 얻었다",
        gap: "정상적 방법 가능성은 배제하고 즉시 불법으로 단정"
      }
    ],

    // 심층: 무의식적 믿음
    deep_beliefs: [
      "민주당/좌파는 과거 독재정권처럼 사찰로 반대파를 제거한다",
      "지금의 작은 사찰이 곧 전면적 감시독재 사회로 발전한다",
      "이들은 사법부까지 장악해서 완전한 권력을 차지하려 한다"
    ],

    worldview_hints: "과거 독재 → 현재 재현, 좌파 = 독재 본성"
  }


┌─────────────────────────────────────────────────────────────┐
│ Phase 3: 믿음 정규화 (패턴 발견 시도)                        │
└─────────────────────────────────────────────────────────────┘

  layered_perceptions (297개)
         ↓
  deep_beliefs 추출 (889개)
         ↓
  [BeliefNormalizer] (GPT-4o)
         ↓
  belief_patterns 테이블 (552개)
         ↓
  {
    id: UUID
    belief: "민주당/좌파는 독재정권처럼 사찰로 반대파 제거"
    frequency: 16
    example_content_ids: [UUID, UUID, ...]
    cluster_id: null
  }

  결과: 889개 → 552개 (37.9% 감소)
  문제: 여전히 58.5%가 1번만 등장 (통계적 패턴 부족)


┌─────────────────────────────────────────────────────────────┐
│ Phase 4: 세계관 구성 (핵심!)                                 │
└─────────────────────────────────────────────────────────────┘

  layered_perceptions (297개)
         ↓
  [OptimalWorldviewConstructor] (GPT-4o)
         ↓

  ┌─ 시뮬레이션 기반 최적 설계 ─┐
  │                              │
  │ 1. 매칭: Hybrid              │
  │    - Vector 70%              │
  │    - Keyword 30%             │
  │                              │
  │ 2. Metadata: 계층형          │
  │    - Core                    │
  │    - Interpretation Frame    │
  │    - Emotional Drivers       │
  │                              │
  │ 3. Narrative: 예시 중심      │
  │    - DC 해석 vs 일반 해석    │
  │    - 구체적 사례             │
  │                              │
  │ 4. 구조: 계층형              │
  │    - 3-4 대분류              │
  │    - 각 2-3 세부             │
  └──────────────────────────────┘
         ↓
  worldviews 테이블 (6개 신규)
         ↓
  {
    id: UUID
    title: "민주당/좌파에 대한 인식 > 독재 재현"

    frame: {  // JSON
      category: "민주당/좌파에 대한 인식",
      subcategory: "독재 재현",

      // 예시 중심 Narrative
      narrative: {
        summary: "민주당은 과거 독재 정권의 방식을 재현하고 있다",

        examples: [
          {
            case: "유심교체 정보",
            dc_interpretation: "민주당이 사찰을 통해 독재적 통치를 시도한다",
            normal_interpretation: "정치적 논란 속의 정보 유출 사건",
            gap: "의도적 독재 시도 vs. 정보 유출 문제"
          }
        ],

        logic_chain: "사찰 → 권력 장악 → 독재 사회",
        historical_context: "과거 독재 정권의 사찰과 권력 집중"
      },

      // 계층형 Metadata
      metadata: {
        core: {
          primary_subject: "민주당",
          primary_attribute: "독재적 성향",
          primary_action: "사찰을 통한 권력 장악"
        },

        interpretation_frame: {
          historical_lens: {
            reference_period: "과거 독재 시대",
            reference_events: ["사찰 사건", "권력 집중"],
            projection_logic: "과거 패턴 → 현재 반복"
          },

          causal_chain: [
            "사찰 시작",
            "권력 집중",
            "독재 체제"
          ],

          slippery_slope: {
            trigger: "사찰 사건",
            escalation: "권력 장악 시도",
            endpoint: "독재 사회"
          }
        },

        emotional_drivers: {
          primary: "불신",
          secondary: ["분노", "위기감"],
          urgency_level: "높음"
        },

        key_concepts: ["독재", "사찰", "권력 남용"]
      }
    },

    core_subject: "민주당",
    core_attributes: ["독재", "사찰", "권력 남용"],
    total_perceptions: 0  // 나중에 업데이트
  }


┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Perception ↔ Worldview 매칭                        │
└─────────────────────────────────────────────────────────────┘

  layered_perceptions (297개) + worldviews (6개)
         ↓
  [Hybrid Matching Algorithm]
         ↓

  ┌─ For each perception ─┐
  │                        │
  │ 1. Vector Similarity   │
  │    - Perception의      │
  │      deep_beliefs      │
  │      embedding         │
  │    - Worldview의       │
  │      narrative         │
  │      embedding         │
  │    - Cosine similarity │
  │                        │
  │ 2. Keyword Matching    │
  │    - Metadata의        │
  │      key_concepts 매칭 │
  │    - Core subject 매칭 │
  │                        │
  │ 3. Hybrid Score        │
  │    = 70% * vector      │
  │    + 30% * keyword     │
  │                        │
  │ 4. Threshold > 0.5     │
  │    → Link 생성         │
  └────────────────────────┘
         ↓
  perception_worldview_links 테이블 (26개)
         ↓
  {
    id: UUID
    perception_id: UUID
    worldview_id: UUID
    relevance_score: 0.758  // hybrid score
    created_at: timestamp
  }
```

---

## 🏗️ 계층형 세계관 구조

```
worldviews (6개)
│
├─ 📂 민주당/좌파에 대한 인식 (대분류 1)
│   │
│   ├─ 🌍 독재 재현 (세부 1-1)
│   │   │
│   │   ├─ Narrative (예시 중심)
│   │   │   ├─ 요약: "민주당은 과거 독재 정권 재현"
│   │   │   ├─ 예시 1: 유심교체 정보
│   │   │   │   ├─ DC: "사찰로 독재 시도"
│   │   │   │   ├─ 일반: "정보 유출"
│   │   │   │   └─ Gap: "독재 vs 유출"
│   │   │   ├─ 논리: 사찰 → 권력 → 독재
│   │   │   └─ 역사: 과거 독재 사찰
│   │   │
│   │   └─ Metadata (계층형)
│   │       ├─ Core: 민주당 = 독재성향
│   │       ├─ Historical: 과거 독재 시대
│   │       ├─ Causal Chain: 사찰→권력→독재
│   │       ├─ Slippery Slope: 사찰→장악→독재사회
│   │       └─ Emotion: 불신 (긴급도: 높음)
│   │
│   └─ 🌍 좌파의 사회적 위협 (세부 1-2)
│       └─ ...
│
├─ 📂 외부 세력의 위협 (대분류 2)
│   │
│   ├─ 🌍 중국의 부정적 영향 (세부 2-1)
│   │   └─ ...
│   │
│   └─ 🌍 북한의 지속적 위협 (세부 2-2)
│       └─ ...
│
└─ 📂 국내 정치적 불안정 (대분류 3)
    │
    ├─ 🌍 정치적 부패와 무능 (세부 3-1)
    │   │
    │   ├─ Narrative
    │   │   ├─ 요약: "정치인은 국민 무시"
    │   │   ├─ 예시: 국민청원 무시
    │   │   │   ├─ DC: "국회가 요구 외면"
    │   │   │   ├─ 일반: "정치적 무관심"
    │   │   │   └─ Gap: "무시 vs 무관심"
    │   │   └─ ...
    │   │
    │   └─ Metadata
    │       └─ Emotion: 불신 (긴급도: 중간)
    │
    └─ 🌍 사법부와 언론의 결탁 (세부 3-2)
        │
        └─ Metadata
            └─ Emotion: 분노 (긴급도: 높음)
```

---

## 🔗 데이터 연결 구조

```
contents (297개)
    ↓ (1:1)
layered_perceptions (297개)
    ↓ (N:1)
belief_patterns (552개)

layered_perceptions (297개)
    ↓ (N:M via links)
perception_worldview_links (26개)
    ↓
worldviews (6개)
```

### 연결 예시

```
Content: "민주, 지귀연 핸드폰 교체 어떻게 알았나"
    ↓
Layered Perception:
    explicit: "민주당이 유심교체 정보 알았다"
    implicit: "통신사 협박으로 얻었다"
    deep: "좌파는 독재정권처럼 사찰한다"
    ↓
Link (score: 0.758)
    ↓
Worldview: "민주당/좌파 > 독재 재현"
    narrative: "DC는 '사찰→독재' 로 해석"
    metadata: slippery_slope = "사찰→장악→독재"
```

---

## 🧠 핵심 엔진들

### 1. LayeredPerceptionExtractor
```python
class LayeredPerceptionExtractor:
    """
    3-Layer 분석
    - Input: content (title, body)
    - Output: layered_perception (explicit, implicit, deep)
    - Engine: GPT-4o-mini
    """
```

### 2. BeliefNormalizer
```python
class BeliefNormalizer:
    """
    믿음 정규화
    - Input: deep_beliefs (889개)
    - Output: belief_patterns (552개)
    - Engine: GPT-4o
    - Result: 37.9% 중복 제거 (but 여전히 파편화)
    """
```

### 3. OptimalWorldviewConstructor ⭐
```python
class OptimalWorldviewConstructor:
    """
    세계관 구성 (최적화)

    - Input: layered_perceptions (297개)
    - Output: hierarchical worldviews (6개)

    - Design:
      1. 계층형 구조 (대분류 → 세부)
      2. 예시 중심 Narrative
      3. 계층형 Metadata
      4. Hybrid 매칭

    - Process:
      1. _extract_hierarchical_worldviews() → GPT-4o로 계층 추출
      2. _save_worldviews() → DB 저장
      3. _match_perceptions_to_worldviews() → Hybrid 매칭
      4. _calculate_statistics() → 통계 계산
    """
```

---

## 📈 통계 요약

| 지표 | 값 |
|------|-----|
| 수집된 글 | 297개 |
| 3-layer 분석 완료 | 297개 (100%) |
| 추출된 믿음 (원본) | 889개 |
| 정규화된 믿음 | 552개 |
| 대분류 세계관 | 3개 |
| 세부 세계관 | 6개 |
| Perception-Worldview 링크 | 26개 |
| 평균 링크/세계관 | ~4.3개 |

---

## 🎯 목적 달성 현황

### ✅ 완료된 것

1. **데이터 수집**: 297개 DC Gallery 글
2. **3-Layer 분석**: 명시→암묵→심층 완전 추출
3. **세계관 구성**: 계층형 6개 세계관 생성
4. **예시 중심 Narrative**: DC vs 일반 해석 대비
5. **계층형 Metadata**: 완전한 구조 (core, frame, emotions)
6. **Hybrid 매칭**: Vector + Keyword 알고리즘

### ⚠️ 제한 사항

1. **데이터 양**: 297개는 통계적 패턴엔 부족 (but 맥락 이해엔 충분)
2. **링크 수**: 26개 (perception의 8.8%만 매칭)
   - 원인: threshold 0.5가 높음
   - 개선: threshold 조정 또는 더 많은 데이터
3. **perception_worldview_links 테이블**: 수동 생성 필요
4. **구 세계관**: 10개 옛날 방식 세계관이 남아있음 (정리 필요)

### 🚀 다음 단계 (우선순위)

1. **데이터 확장**: 297개 → 1000개+ 수집
2. **링크 증가**: threshold 조정 또는 재매칭
3. **대시보드**: 세계관 브라우징 UI
4. **반박 논리**: Deconstruction 전략 생성
5. **모니터링**: 지속적 업데이트

---

## 🔍 여당 지지자 사용 시나리오

```
1. 여당 지지자가 DC Gallery 글 발견
   "유심교체를 어떻게 알았냐" ← 무슨 말인지 모름

2. 시스템에서 해당 글 검색
   → Content 찾기

3. Layered Perception 확인
   → "아, 이들은 '통신사 협박' '사찰' '독재' 로 해석하는구나"

4. 연결된 Worldview 확인
   → "민주당/좌파 > 독재 재현" 세계관

5. Narrative 읽기
   【예시】
   DC: "사찰로 독재 시도"
   일반: "정보 유출"
   차이: "의도적 독재 vs 정보 문제"

   【논리】
   사찰 → 권력 장악 → 독재 사회

   【역사】
   과거 독재 정권의 사찰 참조

6. 이해 완료
   "아, 그래서 작은 일도 독재로 연결하는구나!"
   "과거 독재 시대를 현재에 투영하는 렌즈구나!"
```

---

**시스템 상태**: ✅ 세계관 구성 완료
**다음 목표**: 대시보드 통합 & 데이터 확장
**핵심 성과**: 시뮬레이션 기반 최적 설계로 이해 가능한 세계관 구축
