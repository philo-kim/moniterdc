# 담론 세계관 분석 시스템 아키텍처

**버전**: 2.0
**작성일**: 2025-10-10
**목적**: 현실 왜곡 인과 패턴 추적 시스템

---

## 1. 시스템 목적

### 1.1 핵심 목표

**"저들이 현실을 어떻게 왜곡하는가"의 인과 패턴을 추적하고 예측**

### 1.2 구체적 사례

**사실 (Real World)**:
- 국회 법사위가 조희대 대법원장 국정감사 추진

**저들의 해석 (Their World)**:
- "또 판사 사찰하려는 거야"
- 근거: "지귀연 유심 교체를 어떻게 알았나 = 통신사 협박 = 사찰의 증거"
- 논리: "민주당은 언제나 사찰로 정적을 제거한다"

**왜곡의 구조**:
1. 사실 선택: 지귀연 정보 획득만 선택
2. 인과 부여: "어떻게 알았나" → "사찰했다" (다른 가능성 배제)
3. 패턴 일반화: "민주당은 언제나 사찰한다"
4. 새 사건 해석: 조희대 국감 → "또 사찰"

---

## 2. 시스템 구조

### 2.1 전체 파이프라인

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 0: Raw Content (DC 게시글)                             │
│ - 458개 수집됨                                               │
│ - 실시간 크롤링 중                                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Perception Extraction                               │
│ - 사실 추출                                                  │
│ - 주장 추출                                                  │
│ - 감정/어조 추출                                             │
│ - ★ 인과 관계 암시 추출 (NEW)                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Causal Pattern Detection (NEW)                      │
│ - 인과 관계 추출 (A → B)                                     │
│ - 왜곡 논리 추출 ("왜냐하면 X는 Y하기 때문")                │
│ - 증거 선택 패턴 (포함/배제)                                │
│ - 일반화 패턴 ("X는 언제나 Y한다")                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Worldview Construction                              │
│ - 세계관 = 반복되는 인과 패턴 집합                          │
│ - 패턴 clustering                                            │
│ - 해석 로직 명시화                                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Event Interpretation Engine (NEW)                   │
│ - 새 사건 입력                                               │
│ - 관련 패턴 검색                                             │
│ - 패턴 적용 및 해석 생성                                     │
│ - 과거 증거 인용                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Layer 별 상세 설계

### Layer 0: Raw Content

**데이터**: DC 게시글 원문

**구조**:
```json
{
  "id": "uuid",
  "title": "민주, 지귀연 핸드폰 교체 어떻게 알았나",
  "body": "유심교체를 어떻게 알아ㅋㅋ 지들 맘에 안드는 판사 사찰하려고 통신사 협박해서...",
  "source_url": "https://...",
  "published_at": "2025-01-01T00:00:00Z"
}
```

**현황**:
- 458개 수집됨
- 커버리지: 9.8% (45개만 Perception 추출됨)

**개선 필요**:
- 나머지 413개도 Perception 추출 필요

---

### Layer 1: Perception Extraction

**목적**: 원문에서 사실, 주장, 감정, 인과 관계 추출

**현재 구조**:
```json
{
  "perceived_subject": "민주당",
  "perceived_attribute": "개인정보 사찰",
  "perceived_valence": "negative",
  "claims": [
    "민주당이 개인정보를 맘대로 들춰보고 있다",
    "지들 맘에 안드는 판사 사찰하려고 통신사 협박해서 정보를 얻어냈다"
  ],
  "keywords": ["민주당", "사찰", "통신사", "협박"],
  "emotions": ["분노", "경악"]
}
```

**문제점**:
- Claims에 인과 관계 없음 (키워드 0%)
- 단순 주장 나열

**개선안**:
```json
{
  "perceived_subject": "민주당",
  "perceived_attribute": "개인정보 사찰",
  "perceived_valence": "negative",
  "claims": [...],
  "keywords": [...],
  "emotions": [...],
  "causal_hints": {  // ★ NEW
    "trigger": "지귀연 유심 교체 정보를 알고 있었다",
    "inference": "통신사를 협박해서 얻었다",
    "evidence_for": "민주당이 사찰한다는 증거",
    "generalizes_to": "민주당은 언제나 불법적 방법을 쓴다"
  }
}
```

**구현**:
- `engines/analyzers/layered_perception_extractor.py` 개선
- GPT 프롬프트 추가: "인과 관계 암시를 추출하세요"

---

### Layer 2: Causal Pattern Detection (NEW)

**목적**: Perception들에서 반복되는 인과 왜곡 패턴 추출

**Causal Pattern 구조**:
```json
{
  "pattern_id": "uuid",
  "pattern_type": "causal_distortion",
  "title": "민주당 사찰 권력 유지 패턴",

  "structure": {
    "trigger": "민주당이 X 정보를 알고 있다",
    "inference": "불법적 방법으로 얻었다",
    "assumption": "정상적 경로는 불가능하다",
    "generalization": "민주당은 언제나 불법적 방법을 쓴다",
    "motivation": "사찰을 통한 정적 제거"
  },

  "evidence_selection": {
    "included": [
      "지귀연 유심 교체 정보 획득",
      "과거 사찰 의혹 사건들"
    ],
    "excluded": [
      "국회 정보 요청권",
      "합법적 조사 경로",
      "공개된 정보 가능성"
    ],
    "distortion_type": "selective_evidence"
  },

  "recurrence": {
    "past_events": [
      {
        "event": "지귀연 유심 교체 정보",
        "date": "2025-01-01",
        "perception_ids": ["..."]
      }
    ],
    "frequency": 15,
    "confidence": 0.85
  },

  "application_logic": {
    "when_sees": "민주당의 권한 행사",
    "interprets_as": "사찰의 시도",
    "reasoning": "과거 패턴 (지귀연) 반복"
  }
}
```

**추출 방법**:
1. 88개 Perception 로드
2. GPT-4o로 인과 관계 패턴 추출
3. 유사 패턴 clustering
4. 10-15개 핵심 패턴 생성

**구현**:
- `engines/analyzers/causal_pattern_detector.py` (신규)
- DB: `causal_patterns` 테이블 추가

---

### Layer 3: Worldview Construction

**목적**: 세계관 = 반복적으로 사용되는 인과 패턴들의 집합

**기존 문제**:
- 세계관 = 주제 분류 (토픽 모델링)
- "독재와 사찰의 부활", "이민 정책과 범죄 증가" 등 → 단순 카테고리

**새로운 Worldview 구조**:
```json
{
  "worldview_id": "uuid",
  "title": "독재와 사찰의 부활",
  "core_belief": "민주당은 불법 사찰로 권력을 유지한다",

  "causal_patterns": [  // ★ 핵심
    {
      "pattern_id": "...",
      "pattern_title": "민주당 사찰 권력 유지",
      "weight": 0.9,
      "frequency": 15,
      "representative_claims": [
        "지들 맘에 안드는 판사 사찰하려고 통신사 협박해서...",
        "민주당이 개인정보를 맘대로 들춰보고..."
      ]
    },
    {
      "pattern_id": "...",
      "pattern_title": "정치보복 패턴",
      "weight": 0.7,
      "frequency": 8
    }
  ],

  "interpretation_logic": {
    "core_question": "민주당의 권한 행사를 어떻게 해석하는가?",
    "answer": "사찰의 시도로 해석",
    "reasoning_template": "{trigger}를 봤을 때, {past_evidence} 때문에 {interpretation}이라고 판단",
    "example": "조희대 국감을 봤을 때, 지귀연 사건 때문에 또 판사 사찰이라고 판단"
  },

  "evidence_base": {
    "core_events": [
      {
        "event": "지귀연 유심 교체 정보 획득",
        "role": "핵심 증거",
        "quoted_frequency": 15
      }
    ]
  },

  "perception_ids": [137개],
  "created_at": "...",
  "updated_at": "..."
}
```

**구축 방법**:
1. Layer 2의 패턴들을 유사도 기준 clustering
2. 각 cluster = 하나의 세계관
3. 세계관별 해석 로직 생성

**구현**:
- `engines/analyzers/causal_worldview_constructor.py` (재작성)
- 기존 9개 세계관 재구축

---

### Layer 4: Event Interpretation Engine (NEW)

**목적**: 새로운 사건에 대해 특정 세계관으로 해석 생성

**Input**:
```json
{
  "event": "조희대 대법원장을 국정감사에 부르는 것을 나경원 의원이 반대",
  "worldview_id": "독재와 사찰의 부활"
}
```

**처리 과정**:
1. **사건 분석**: 주체(민주당), 행위(국감 추진), 대상(조희대)
2. **패턴 매칭**: 어떤 인과 패턴이 적용되는가?
   - "민주당 사찰 권력 유지" 패턴 매칭 (0.9 similarity)
3. **증거 검색**: 과거 사건 중 유사한 것
   - 지귀연 유심 교체 사건 (핵심 증거)
4. **해석 생성**: 패턴 + 증거 → 답변

**Output**:
```json
{
  "interpretation": "또 판사 사찰하려는 거야. 지귀연 유심 교체를 어떻게 알았는지 봐봐. 통신사 협박해서 개인정보 얻어낸 거 뻔한데, 조희대도 똑같이 하려는 거지. 나경원이 반대하는 건 당연하지.",

  "applied_pattern": {
    "pattern_id": "...",
    "pattern_title": "민주당 사찰 권력 유지",
    "confidence": 0.85
  },

  "cited_evidence": [
    {
      "event": "지귀연 유심 교체",
      "role": "과거 패턴 증거",
      "quote": "유심 교체를 어떻게 알았나"
    }
  ],

  "reasoning_chain": [
    "1. 민주당이 조희대 국감 추진 (trigger)",
    "2. 과거 지귀연 때 사찰 증거 있음 (evidence)",
    "3. 따라서 이번에도 사찰 목적 (inference)",
    "4. 민주당은 언제나 사찰함 (generalization)"
  ]
}
```

**구현**:
- `engines/interpreters/event_interpreter.py` (신규)
- API: `POST /api/interpret`

---

## 4. 데이터베이스 스키마

### 4.1 기존 테이블 (유지)

**contents**: DC 게시글 원문
**perceptions**: 추출된 인식
**worldviews**: 세계관

### 4.2 새 테이블

**causal_patterns**: 인과 패턴
```sql
CREATE TABLE causal_patterns (
  id UUID PRIMARY KEY,
  pattern_type VARCHAR NOT NULL,  -- 'causal_distortion', 'evidence_selection', etc.
  title VARCHAR NOT NULL,
  structure JSONB NOT NULL,  -- trigger, inference, assumption, generalization
  evidence_selection JSONB,  -- included, excluded, distortion_type
  recurrence JSONB,  -- past_events, frequency, confidence
  application_logic JSONB,  -- when_sees, interprets_as, reasoning
  perception_ids UUID[] NOT NULL,
  worldview_ids UUID[],
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_causal_patterns_type ON causal_patterns(pattern_type);
CREATE INDEX idx_causal_patterns_worldview ON causal_patterns USING GIN(worldview_ids);
```

**pattern_applications**: 패턴 적용 이력
```sql
CREATE TABLE pattern_applications (
  id UUID PRIMARY KEY,
  pattern_id UUID REFERENCES causal_patterns(id),
  event_description TEXT NOT NULL,
  interpretation TEXT NOT NULL,
  confidence FLOAT,
  cited_evidence JSONB,
  reasoning_chain JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 4.3 기존 테이블 수정

**perceptions**: causal_hints 컬럼 추가
```sql
ALTER TABLE perceptions
ADD COLUMN causal_hints JSONB;
```

**worldviews**: 구조 변경
```sql
ALTER TABLE worldviews
ADD COLUMN core_belief TEXT,
ADD COLUMN causal_pattern_ids UUID[],
ADD COLUMN interpretation_logic JSONB,
ADD COLUMN evidence_base JSONB;
```

---

## 5. API 엔드포인트

### 5.1 Event Interpretation

```
POST /api/interpret
Content-Type: application/json

{
  "event": "조희대 대법원장 국정감사 추진",
  "worldview": "독재와 사찰의 부활"  // optional, 없으면 모든 세계관
}

Response:
{
  "interpretations": [
    {
      "worldview": "독재와 사찰의 부활",
      "interpretation": "또 판사 사찰하려는 거야...",
      "confidence": 0.85,
      "pattern": {...},
      "evidence": [...]
    }
  ]
}
```

### 5.2 Pattern Search

```
GET /api/patterns?worldview={id}

Response:
{
  "patterns": [
    {
      "id": "...",
      "title": "민주당 사찰 권력 유지",
      "frequency": 15,
      "confidence": 0.9
    }
  ]
}
```

### 5.3 Worldview Detail

```
GET /api/worldviews/{id}

Response:
{
  "id": "...",
  "title": "독재와 사찰의 부활",
  "core_belief": "...",
  "causal_patterns": [...],
  "interpretation_logic": {...}
}
```

---

## 6. 성공 기준

### 6.1 정량적

1. **Layer 1**: 원문 보존도 8/10 이상, 인과 암시 추출률 50% 이상
2. **Layer 2**: 10-15개 핵심 인과 패턴 추출
3. **Layer 3**: 9개 세계관 재구축 완료
4. **Layer 4**: Authenticity 8/10, 특정성 8/10 이상

### 6.2 정성적

**Test Case**:
```
Input: "조희대 대법원장 국정감사 추진"
Expected: "또 판사 사찰하려는 거야. 지귀연 유심 교체를 어떻게 알았는지 봐봐..."
GPT Evaluation: 실제 DC 게시글과 구별 불가능
```

---

## 7. 구현 우선순위

### Phase 1 (완료)
✓ 파일 정리
✓ 현황 분석
✓ 문서 작성

### Phase 2 (다음)
- [ ] Perception Extractor 개선 (causal_hints 추가)
- [ ] 88개 Perception 재추출

### Phase 3
- [ ] Causal Pattern Detector 구현
- [ ] 10-15개 패턴 추출

### Phase 4
- [ ] Worldview Constructor 재작성
- [ ] 9개 세계관 재구축

### Phase 5
- [ ] Event Interpreter 구현
- [ ] API 엔드포인트 추가

### Phase 6
- [ ] End-to-end 검증
- [ ] 대시보드 업데이트

---

## 8. 위험 요소

### 8.1 인과 패턴 추출 정확도
- **위험**: GPT가 패턴을 잘못 추출
- **대응**: 샘플 검증, 프롬프트 반복 개선

### 8.2 패턴 과잉 일반화
- **위험**: "민주당은 언제나 X한다" → 너무 포괄적
- **대응**: 패턴별 증거 카운트, confidence score

### 8.3 시스템 복잡도
- **위험**: Layer가 많아져 유지보수 어려움
- **대응**: 각 Layer 독립 테스트, 명확한 인터페이스

---

## 9. 향후 확장

### 9.1 실시간 모니터링
- 새 게시글 → 새 패턴 감지 → 알림

### 9.2 패턴 진화 추적
- 시간에 따른 패턴 변화
- 새로운 세계관 출현 감지

### 9.3 대응 전략 생성
- 패턴별 효과적인 반박 방법
- 프레임 깨기 전략

---

**다음 문서**: `CAUSAL_PATTERN_SPEC.md`
