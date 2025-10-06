# 세계관 분석 엔진 설계

## 핵심 개념

### 세계관이란?
정치 커뮤니티에서 **반복적으로 구성되는 인식의 틀**

```
개별 게시글 → 주체에 대한 평가 → 시간에 따라 누적 → 세계관 형성
```

### 구조
```
세계관 = 주체들(Subjects) + 속성들(Attributes) + 관계망(Relations) + 시간에 따른 강화
```

---

## 1. 데이터 구조

### 1.1 주체 (Subject)
정치적 행위자/집단

```json
{
  "name": "민주당",
  "type": "정당",
  "aliases": ["민주", "더불어민주당", "민노"]
}
```

**주요 주체들:**
- 정당: 민주당, 국민의힘
- 인물: 이재명, 윤석열, 한동훈
- 국가: 중국, 미국, 북한
- 집단: 좌파, 우파, 언론

### 1.2 속성 (Attribute)
주체를 규정하는 특성

```json
{
  "subject": "민주당",
  "attribute": "친중",
  "sentiment": "negative",
  "strength": 0.85,  // 0-1, 얼마나 강하게 연관되는지
  "evidence_count": 47,  // 이 속성을 뒷받침하는 글 개수
  "first_mentioned": "2024-01-15",
  "last_mentioned": "2025-01-30"
}
```

**속성 카테고리:**
- 정치적: 친중, 친미, 반미, 좌파, 우파
- 도덕적: 부패, 범죄자, 무능, 위선
- 능력: 유능, 무능, 강단있음
- 안보: 위협, 수호자, 배신자

### 1.3 관계 (Relation)
주체들 간의 연결

```json
{
  "subject1": "민주당",
  "relation_type": "결탁",
  "subject2": "중국",
  "strength": 0.78,
  "evidence_count": 34,
  "examples": ["중국인무비자", "조선족도망", "간첩의혹"]
}
```

**관계 유형:**
- 결탁 (collusion)
- 공격 (attack)
- 옹호 (support)
- 대립 (opposition)
- 허용 (enable)

---

## 2. 분석 파이프라인

### Phase 1: 추출 (Extraction)
```
게시글 → GPT 분석 → {주체, 속성, 관계, 감정}
```

**GPT 프롬프트 핵심:**
- "이 글의 주인공은 누구인가?" (주체)
- "그들을 어떻게 묘사하는가?" (속성)
- "긍정/부정/중립?" (감정)
- "주체들 간 관계는?" (관계)

### Phase 2: 집계 (Aggregation)
```
개별 평가들 → 주체별 집계 → 강도 계산
```

**집계 로직:**
- 같은 주체에 대한 평가 모으기
- 속성별 빈도수 카운트
- 감정 분포 계산 (긍정:부정:중립 비율)
- 시간에 따른 변화 추적

### Phase 3: 그래프 구성 (Graph Building)
```
주체 + 관계 → 지식 그래프
```

**그래프 구조:**
```
[민주당] --친중--> [중국]
   |                  |
   |--무능            |--위협
   |                  |
   |--결탁-------------|
```

### Phase 4: 세계관 도출 (Worldview Extraction)
```
그래프 분석 → 주요 내러티브 추출
```

**내러티브 식별:**
- 가장 강한 주체-속성 연결
- 가장 많이 언급되는 관계
- 시간에 따라 강화되는 패턴

---

## 3. 데이터베이스 스키마

### 3.1 주체 클러스터
```sql
CREATE TABLE subject_clusters (
  id UUID PRIMARY KEY,
  subject_name TEXT NOT NULL,  -- 민주당, 이재명, 윤석열 등
  subject_type TEXT,  -- 정당, 인물, 국가, 집단
  aliases TEXT[],  -- 별칭들

  -- 통계
  total_mentions INTEGER DEFAULT 0,
  positive_count INTEGER DEFAULT 0,
  negative_count INTEGER DEFAULT 0,
  neutral_count INTEGER DEFAULT 0,

  -- 속성 집계
  common_attributes JSONB,  -- {"친중": 47, "무능": 23, ...}

  -- 시간
  first_seen TIMESTAMPTZ,
  last_seen TIMESTAMPTZ,

  UNIQUE(subject_name)
);
```

### 3.2 주체-논리 매핑
```sql
CREATE TABLE subject_logic_mapping (
  id UUID PRIMARY KEY,
  subject_cluster_id UUID REFERENCES subject_clusters(id),
  logic_id UUID REFERENCES logic_repository(id),

  sentiment TEXT,  -- positive, negative, neutral
  attributes TEXT[],  -- 이 글에서 부여된 속성들

  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.3 관계 그래프
```sql
CREATE TABLE subject_relations (
  id UUID PRIMARY KEY,
  subject1_id UUID REFERENCES subject_clusters(id),
  relation_type TEXT,  -- 결탁, 공격, 옹호 등
  subject2_id UUID REFERENCES subject_clusters(id),

  strength FLOAT,  -- 0-1
  evidence_count INTEGER,
  evidence_logic_ids UUID[],  -- 뒷받침하는 글들

  first_seen TIMESTAMPTZ,
  last_seen TIMESTAMPTZ,

  UNIQUE(subject1_id, relation_type, subject2_id)
);
```

---

## 4. 분석 엔진

### 4.1 주체 식별 엔진
```python
def identify_subjects(text: str) -> List[Subject]:
    """
    글에서 주체들 추출
    - GPT로 엔티티 추출
    - 별칭 정규화 (민주 → 민주당)
    - 주체 타입 분류
    """
```

### 4.2 속성 집계 엔진
```python
def aggregate_attributes(subject_id: UUID) -> Dict:
    """
    주체에 대한 모든 평가 집계

    반환:
    {
      "친중": {"count": 47, "strength": 0.85},
      "무능": {"count": 23, "strength": 0.62},
      ...
    }
    """
```

### 4.3 관계 추론 엔진
```python
def infer_relations() -> List[Relation]:
    """
    주체들 간 관계 추론

    방법:
    1. 같은 글에 등장하는 주체들
    2. 관계 동사 추출 (결탁, 공격, 옹호)
    3. 빈도수로 강도 계산
    """
```

### 4.4 세계관 요약 엔진
```python
def summarize_worldview(subject_id: UUID) -> Worldview:
    """
    주체에 대한 세계관 요약

    반환:
    {
      "subject": "민주당",
      "core_narrative": "민주당은 중국과 결탁하여 국가안보를 위협한다",
      "key_attributes": ["친중", "무능", "부패"],
      "key_relations": [
        {"with": "중국", "type": "결탁"},
        {"with": "미국", "type": "대립"}
      ],
      "evidence_strength": 0.85,
      "timeline": [...]
    }
    """
```

---

## 5. 대시보드 UI

### 5.1 주체 중심 뷰
```
[주체 목록]           [선택된 주체 상세]              [시간 흐름]
┌──────────┐        ┌────────────────────┐       ┌──────────┐
│민주당 (47)│   →   │민주당에 대한 세계관    │  →   │Jan ──▲   │
│이재명 (34)│        │                    │       │Feb ──▲▲  │
│윤석열 (28)│        │핵심 속성:          │       │Mar ──▲▲▲ │
│중국 (23)  │        │• 친중 (85%)        │       └──────────┘
└──────────┘        │• 무능 (62%)        │
                    │• 부패 (47%)        │
                    │                    │
                    │주요 관계:          │
                    │• 중국과 결탁       │
                    │• 미국과 대립       │
                    └────────────────────┘
```

### 5.2 관계망 그래프 뷰
```
        [중국]
          ↑
         결탁
          |
      [민주당] ──대립──→ [미국]
          |              ↑
         공격           옹호
          ↓              |
      [윤석열]──────────┘
```

### 5.3 시간 흐름 뷰
```
민주당=친중 세계관 강화 과정

2024-11 │ 중국인무비자 허용
        ├──→ "민주당이 중국인 유입 허용" (5건)

2024-12 │ 조선족 집단 도주
        ├──→ "민주당 친중정책 때문" (8건)

2025-01 │ 간첩 의혹
        └──→ "민주당=친중=안보위협" (12건)

강화도: ▓▓▓▓▓▓▓▓▓░ 85%
```

---

## 6. 구현 우선순위

### MVP (최소 기능)
1. ✅ 주체 추출 GPT 프롬프트
2. ✅ subject_clusters 테이블
3. ✅ subject_logic_mapping 테이블
4. 주체별 집계 뷰
5. 주체 중심 대시보드

### Phase 2
1. 관계 추론 엔진
2. 관계 그래프 DB
3. 관계망 시각화

### Phase 3
1. 시간 흐름 분석
2. 세계관 강화 패턴 감지
3. 자동 요약 생성

---

## 7. 기대 효과

### 현재 방식의 문제
- 53개 프레임 → 대부분 1개씩 → 파편화
- 같은 세계관인데 문자열이 달라 분리됨

### 주체 중심 방식의 장점
✅ **"민주당"에 대한 모든 평가가 한곳에 모임**
✅ **시간에 따라 세계관이 어떻게 강화되는지 보임**
✅ **관계망으로 전체 구조 파악 가능**
✅ **대응할 때 "주체 전체 왜곡"에 대응**

---

## 8. 다음 단계

1. migration: subject_clusters, subject_logic_mapping 테이블 생성
2. 크롤러 수정: worldview 분석 적용
3. 집계 스크립트: 주체별 통계 계산
4. 대시보드: 주체 중심 뷰 구현
5. 테스트: 실제 데이터로 세계관 추출 검증