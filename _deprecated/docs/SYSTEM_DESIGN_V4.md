# 세계관 분석 시스템 V4 - 최종 설계

## 1. 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: 데이터 수집                                          │
│ ContentCollector → 충분한 양의 실제 글 수집 (목표: 500+)      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: 층위별 분석                                          │
│ LayeredPerceptionExtractor                                   │
│ - 표면층: 명시적 주장                                         │
│ - 암묵층: 전제하는 사고                                       │
│ - 심층: 무의식적 믿음                                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: 패턴 탐지                                            │
│ BeliefPatternDetector                                        │
│ - 반복되는 심층 믿음 찾기 (통계적 유의미성)                    │
│ - 믿음 간 연결 구조 파악                                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: 세계관 구성                                          │
│ WorldviewSynthesizer                                         │
│ - 공통 믿음들이 어떻게 세계관을 구성하는가                     │
│ - 수직적 연결: 믿음 → 사고 → 주장                            │
│ - 수평적 연결: 믿음들 간의 관계                               │
└─────────────────────────────────────────────────────────────┘
```

## 2. 각 컴포넌트 상세

### 2.1 ContentCollector (기존 유지)

**목표**: 충분한 양의 데이터
- 현재: 81개 → 목표: 500개 이상
- 다양한 시기, 다양한 주제
- 본문이 있는 글만 수집

### 2.2 LayeredPerceptionExtractor (신규)

**입력**: 1개 글 (title + body)

**출력**:
```python
{
  "content_id": "uuid",

  # 표면층
  "explicit": {
    "claims": [
      {
        "subject": "민주당",
        "predicate": "사찰했다",
        "evidence_cited": "유심교체 정보를 알았다"
      }
    ]
  },

  # 암묵층
  "implicit": {
    "assumptions": [
      "비공개 정보를 안다 = 불법으로 얻었다",
      "사찰은 독재의 시작이다"
    ],
    "reasoning_gaps": [
      "정보를 안다 → 사찰했다 (중간 추론 생략)"
    ]
  },

  # 심층
  "deep": {
    "beliefs": [
      "권력은 본질적으로 부패한다",
      "작은 월권은 큰 독재로 발전한다"
    ],
    "worldview_hints": "권력 비관론, 슬리퍼리 슬로프"
  }
}
```

**구현 방식**:
- GPT-4o 사용
- 프롬프트: 3개 층위를 명확히 구분해서 추출
- 각 층위마다 구체적 문장 인용 요구

### 2.3 BeliefPatternDetector (신규)

**입력**: 500개의 LayeredPerception

**처리**:
1. **심층 믿음 빈도 분석**
```python
belief_frequency = {
  "권력은 부패한다": 234개 글 (46.8%),
  "역사는 반복된다": 189개 글 (37.8%),
  "선과 악은 타협 불가": 267개 글 (53.4%),
  ...
}
```

2. **믿음 간 co-occurrence 분석**
```python
# "권력은 부패한다"와 함께 나타나는 다른 믿음들
co_occurrence = {
  ("권력은 부패한다", "감시는 독재의 시작"): 156개 글,
  ("권력은 부패한다", "작은 징조를 막아야"): 142개 글,
  ...
}
```

3. **믿음 클러스터링**
```python
belief_clusters = [
  {
    "cluster_name": "권력 비관론",
    "core_beliefs": [
      "권력은 부패한다",
      "감시는 독재의 시작",
      "작은 월권은 큰 독재로 발전"
    ],
    "frequency": 234개 글,
    "percentage": 46.8%
  },
  {
    "cluster_name": "역사 순환론",
    "core_beliefs": [
      "역사는 반복된다",
      "과거 패턴이 미래를 예측한다",
      "조선의 사대주의 = 현재 친중"
    ],
    "frequency": 189개 글,
    "percentage": 37.8%
  }
]
```

**통계적 유의미성 판단**:
- 30% 이상 출현: 핵심 믿음
- 10-30%: 부분 믿음
- 10% 미만: 개별 의견

### 2.4 WorldviewSynthesizer (신규)

**입력**: BeliefPatternDetector 결과

**출력**: 세계관 구조

```python
{
  "worldview_id": "uuid",
  "title": "DC Gallery 우파 정치 담론의 세계관",

  # 핵심 믿음 체계
  "core_beliefs": [
    {
      "belief": "권력은 본질적으로 부패한다",
      "frequency": "46.8% (234/500 글)",
      "evidence": "핵심 믿음",
      "function": "모든 권력 행위를 의심하는 기반"
    },
    {
      "belief": "역사는 반복된다",
      "frequency": "37.8% (189/500 글)",
      "evidence": "핵심 믿음",
      "function": "과거 사례를 현재에 투사하는 근거"
    }
  ],

  # 수직적 연결 (층위 간)
  "vertical_structure": [
    {
      "deep_belief": "권력은 부패한다",
      "↓": "생성하는 암묵적 사고",
      "implicit_thoughts": [
        "권력자는 감시 수단을 악용한다",
        "비공개 정보를 안다 = 불법"
      ],
      "↓": "나타나는 표면 주장",
      "explicit_claims": [
        "민주당이 사찰했다",
        "독재 시대 예고편"
      ],
      "frequency": "234개 글에서 이 구조 발견"
    }
  ],

  # 수평적 연결 (믿음 간)
  "horizontal_structure": [
    {
      "belief_1": "권력은 부패한다",
      "belief_2": "작은 징조를 막아야 한다",
      "relationship": "belief_1이 belief_2를 정당화",
      "how": "권력이 부패하므로, 작은 월권도 큰 독재로 발전",
      "co_occurrence": "156개 글 (66.7% of belief_1)"
    }
  ],

  # 세계관의 전체 구조
  "overall_structure": {
    "foundation": "권력 비관론 + 역사 순환론",
    "reasoning_pattern": "과거 패턴 → 현재 의심 → 미래 예측 → 즉각 행동",
    "moral_framework": "선악 대립, 타협 불가",
    "action_logic": "예방적 과잉 반응 = 합리적",

    "how_it_works": `
      이들의 세계에서:

      1. 기본 공리
         - 권력은 본질적으로 부패한다
         - 역사는 반복된다
         - 선과 악은 타협할 수 없다

      2. 추론 규칙
         - 과거 사례 → 현재 적용 (조선 사대주의 = 현재 친중)
         - 의심 → 확신 (정보를 안다 = 사찰했다)
         - 작은 징조 → 큰 재앙 (슬리퍼리 슬로프)

      3. 행동 원리
         - 작은 것도 막아야 한다 (예방)
         - 타협하면 배신이다 (순수성)
         - 우리만 진실을 본다 (선택받은 자)

      4. 순환 구조
         권력 부패 → 의심 → 징조 발견 → 예방 행동 →
         타협 거부 → 대립 심화 → 권력 부패 확신 강화
    `
  },

  # 통계적 신뢰도
  "statistical_confidence": {
    "total_posts_analyzed": 500,
    "core_beliefs_count": 5,
    "average_frequency": "42.3%",
    "confidence_level": "높음 (30% 이상)",
    "limitations": [
      "단일 갤러리 데이터",
      "2024년 12월-2025년 1월 기간",
      "개념글 중심"
    ]
  }
}
```

## 3. 데이터베이스 스키마

### 3.1 layered_perceptions (신규 테이블)

```sql
CREATE TABLE layered_perceptions (
  id UUID PRIMARY KEY,
  content_id UUID REFERENCES contents(id),

  -- 표면층
  explicit_claims JSONB,

  -- 암묵층
  implicit_assumptions JSONB,
  reasoning_gaps JSONB,

  -- 심층
  deep_beliefs TEXT[],
  worldview_hints TEXT,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_layered_perceptions_content ON layered_perceptions(content_id);
CREATE INDEX idx_layered_perceptions_beliefs ON layered_perceptions USING GIN(deep_beliefs);
```

### 3.2 belief_patterns (신규 테이블)

```sql
CREATE TABLE belief_patterns (
  id UUID PRIMARY KEY,

  belief TEXT UNIQUE,
  frequency INTEGER,  -- 출현 횟수
  percentage REAL,    -- 전체 대비 비율

  -- 함께 나타나는 믿음들
  co_occurring_beliefs JSONB,

  -- 이 믿음이 생성하는 암묵적 사고들
  generated_thoughts TEXT[],

  -- 이 믿음이 나타나는 주장들
  manifested_claims TEXT[],

  cluster_id UUID,  -- 어느 클러스터에 속하는가

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_belief_patterns_frequency ON belief_patterns(frequency DESC);
CREATE INDEX idx_belief_patterns_cluster ON belief_patterns(cluster_id);
```

### 3.3 worldviews (기존 테이블 재설계)

```sql
ALTER TABLE worldviews ADD COLUMN IF NOT EXISTS
  core_beliefs JSONB,
  vertical_structure JSONB,
  horizontal_structure JSONB,
  overall_structure JSONB,
  statistical_confidence JSONB;
```

## 4. 실행 파이프라인

### 4.1 초기 수집 (1회)

```bash
# 500개 글 수집
python3 scripts/collect_500_posts.py
```

### 4.2 분석 파이프라인 (정기 실행)

```bash
# 전체 파이프라인
python3 pipelines/full_worldview_analysis.py

# 단계별:
# 1. Layer 2: 층위별 분석
python3 engines/analyzers/layered_perception_extractor.py

# 2. Layer 3: 패턴 탐지
python3 engines/analyzers/belief_pattern_detector.py

# 3. Layer 4: 세계관 구성
python3 engines/analyzers/worldview_synthesizer.py
```

## 5. Dashboard 표시

### 5.1 메인 페이지

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DC Gallery 세계관 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

분석 데이터: 500개 글
분석 기간: 2024-12-01 ~ 2025-01-31

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
핵심 믿음 체계 (Core Beliefs)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. "권력은 본질적으로 부패한다"
   출현: 234개 글 (46.8%)
   [상세 보기]

2. "역사는 반복된다"
   출현: 189개 글 (37.8%)
   [상세 보기]

3. "선과 악은 타협할 수 없다"
   출현: 267개 글 (53.4%)
   [상세 보기]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
세계관 구조
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[시각화: 믿음 간 연결 그래프]

[상세 분석 보기]
```

### 5.2 상세 페이지

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
믿음: "권력은 본질적으로 부패한다"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

출현: 234개 글 (46.8%)
신뢰도: 높음

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
이 믿음이 생성하는 사고 (암묵층)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- "권력자는 감시 수단을 악용한다" (187개 글)
- "비공개 정보를 안다 = 불법으로 얻었다" (142개 글)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
나타나는 주장 (표면층)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- "민주당이 사찰했다" (89개 글)
- "독재 시대 예고편" (67개 글)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
함께 나타나는 믿음
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- "작은 징조를 막아야 한다" (156개 글, 66.7%)
- "예방적 행동은 합리적이다" (134개 글, 57.3%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
실제 글 예시
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[글 제목 1] - 2024-12-15
[글 제목 2] - 2024-12-20
...
```

## 6. 장점

### 6.1 통계적 신뢰성
- 500개 글 분석 → 충분한 데이터
- 빈도/비율로 정량화 → 객관적
- 유의미성 판단 기준 명확 (30% 이상)

### 6.2 층위별 분석
- 표면만이 아닌 심층까지
- 숨어있는 믿음 체계 파악
- 왜 그렇게 생각하는지 이해

### 6.3 구조적 이해
- 수직적: 믿음 → 사고 → 주장
- 수평적: 믿음들 간 연결
- 전체: 세계관의 작동 원리

### 6.4 검증 가능
- 각 단계 결과 DB 저장
- 추론 과정 추적 가능
- 구체적 글 인용

## 7. 구현 우선순위

### Phase 1: 데이터 수집 (1일)
- collect_500_posts.py
- 실제 500개 수집 및 저장

### Phase 2: 층위별 추출 (2일)
- LayeredPerceptionExtractor
- 500개 글 분석
- layered_perceptions 테이블 채우기

### Phase 3: 패턴 탐지 (1일)
- BeliefPatternDetector
- 빈도 분석, 클러스터링
- belief_patterns 테이블 채우기

### Phase 4: 세계관 구성 (1일)
- WorldviewSynthesizer
- 구조 합성
- worldviews 테이블 업데이트

### Phase 5: Dashboard (1일)
- API 엔드포인트
- UI 구현
- 시각화

**총 6일 작업**

## 8. 다음 단계

이 설계를 승인하시면:

1. Phase 1부터 순차적으로 구현
2. 각 Phase마다 결과 확인 및 조정
3. 실제 데이터로 검증

시작할까요?
