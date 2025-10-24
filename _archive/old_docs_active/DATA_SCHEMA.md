# MoniterDC v2.0 데이터 스키마 및 연결 관계

**버전**: v2.0
**날짜**: 2025-10-15

---

## 📊 전체 데이터 구조

MoniterDC v2.0은 **4개 핵심 테이블**로 구성됩니다:

```
contents (456개)
  ↓ 1:1
layered_perceptions (499개)
  ↓ 1:N
perception_worldview_links (541개)
  ↓ N:1
worldviews (63개)
  ├─ level 1: 7개 상위 세계관
  └─ level 2: 44개 하위 세계관 (parent_worldview_id)
```

---

## 1️⃣ CONTENTS (원본 게시글)

**개수**: 456개

### 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID | Primary key |
| `source_type` | TEXT | 출처 유형 (예: "dc_gallery") |
| `source_url` | TEXT | 원본 URL |
| `source_id` | TEXT | 원본 게시글 ID |
| `title` | TEXT | 게시글 제목 |
| `body` | TEXT | 게시글 본문 |
| `metadata` | JSONB | 추가 메타데이터 |
| `published_at` | TIMESTAMPTZ | 게시 시각 |
| `collected_at` | TIMESTAMPTZ | 수집 시각 |
| `created_at` | TIMESTAMPTZ | DB 생성 시각 |

### 연결

- **→ layered_perceptions** (1:1)
  - `id` → `layered_perceptions.content_id`
  - 각 content는 정확히 1개의 perception을 가짐

### 예시

```json
{
  "id": "b65616e1-3b65-46f4-a756-bd27b53886f7",
  "title": "민주, 지귀연 핸드폰 교체 어떻게 알았나…독재시대 예고편",
  "source_url": "https://gall.dcinside.com/mgallery/board/view/?id=...",
  "published_at": "2025-01-10T12:34:56Z"
}
```

---

## 2️⃣ LAYERED_PERCEPTIONS (3층 분석 + 추론 구조)

**개수**: 499개 (content 대비 100% 커버리지)

### 핵심 필드 (v2.0)

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID | Primary key |
| `content_id` | UUID | Foreign key → contents.id |
| **v2.0 추론 구조** | | |
| `mechanisms` | TEXT[] | 5개 추론 메커니즘 배열 |
| `actor` | JSONB | 행위 주체 (subject, purpose, methods) |
| `logic_chain` | TEXT[] | 추론 단계 배열 |
| **3층 구조** | | |
| `explicit_claims` | TEXT[] | 표면층: 명시적 주장 |
| `implicit_assumptions` | TEXT[] | 암묵층: 전제 |
| `deep_beliefs` | TEXT[] | 심층: 세계관 |
| **기타** | | |
| `created_at` | TIMESTAMPTZ | 생성 시각 |

### 5개 추론 메커니즘

1. **즉시_단정**: 관찰 → (검증 생략) → 결론
2. **역사_투사**: 과거 패턴 → 현재 반복
3. **필연적_인과**: X → 반드시 Y
4. **네트워크_추론**: 연결 → 조직적 공모
5. **표면_부정**: 표면 X / 실제 Y

### Actor 구조

```json
{
  "subject": "민주당/좌파",
  "purpose": "권력 유지",
  "methods": ["사찰", "협박", "조작"]
}
```

### 연결

- **← contents** (N:1)
  - `content_id` → `contents.id`
- **→ perception_worldview_links** (1:N)
  - `id` → `perception_worldview_links.perception_id`
  - 하나의 perception이 여러 worldview에 링크 가능

### 예시

```json
{
  "id": "437107a1-...",
  "content_id": "b65616e1-...",
  "mechanisms": ["역사_투사", "필연적_인과", "즉시_단정"],
  "actor": {
    "subject": "민주당/좌파",
    "purpose": "권력 유지 및 친중 정책",
    "methods": ["친중 외교", "반미 성향"]
  },
  "logic_chain": [
    "민주당이 지귀연 핸드폰 교체 정보를 파악했다",
    "합법적 취득 가능성을 배제했다",
    "불법 사찰로 단정했다"
  ],
  "explicit_claims": [
    "민주당이 지귀연의 핸드폰 교체 사실을 알고 있다",
    "이는 통신사를 통한 불법 사찰의 증거다"
  ],
  "implicit_assumptions": [
    "민주당은 통신사를 통제할 수 있다"
  ],
  "deep_beliefs": [
    "좌파는 과거 독재정권처럼 사찰로 권력을 유지한다"
  ]
}
```

---

## 3️⃣ WORLDVIEWS (계층적 세계관)

**개수**: 63개
- **Level 1 (상위)**: 7개
- **Level 2 (하위)**: 44개

### 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID | Primary key |
| `title` | TEXT | 세계관 제목 (완전한 문장) |
| `description` | TEXT | 설명 |
| `frame` | JSONB | 구조화된 프레임 |
| `core_subject` | TEXT | 핵심 주체 |
| `core_attributes` | TEXT[] | 핵심 속성 (mechanisms) |
| **계층 구조** | | |
| `level` | INTEGER | 1=상위, 2=하위 |
| `parent_worldview_id` | UUID | 부모 세계관 ID (level 2만) |
| `version` | INTEGER | 버전 (v2.0 = 2) |
| **통계** | | |
| `perception_ids` | UUID[] | 연결된 perception ID 배열 |
| `archived` | BOOLEAN | 보관 여부 |

### 계층 구조 제약

```sql
CHECK (
  (parent_worldview_id IS NULL AND level = 1) OR
  (parent_worldview_id IS NOT NULL AND level = 2)
)
```

### Frame 구조

**Level 1 (상위 세계관)**:
```json
{
  "actor": "민주당/좌파",
  "core_mechanisms": ["즉시_단정", "역사_투사"],
  "logic_pattern": {
    "trigger": "민주당이 정보를 파악",
    "skipped_verification": "합법 취득 가능성",
    "conclusion": "불법 사찰로 단정"
  }
}
```

**Level 2 (하위 세계관)**:
```json
{
  "subject": "민주당",
  "action": "통신사를 협박해 사찰한다",
  "object": "지귀연",
  "examples": ["지귀연 핸드폰 교체 정보 파악"]
}
```

### 연결

- **→ perception_worldview_links** (1:N)
  - `id` → `perception_worldview_links.worldview_id`
- **자기 참조** (계층 구조)
  - Level 2의 `parent_worldview_id` → Level 1의 `id`

### 예시

**상위 세계관 (Level 1)**:
```json
{
  "id": "dc6f1515-5004-4619-9444-99f22860d0f5",
  "title": "민주당은 불법 사찰로 국민을 감시한다",
  "level": 1,
  "version": 2,
  "frame": {
    "actor": "민주당/좌파",
    "core_mechanisms": ["즉시_단정", "역사_투사"],
    "logic_pattern": {
      "trigger": "민주당이 정보를 파악",
      "skipped_verification": "합법 취득 가능성",
      "conclusion": "불법 사찰로 단정"
    }
  },
  "perception_ids": ["437107a1-...", "8fa29bc3-...", ...]
}
```

**하위 세계관 (Level 2)**:
```json
{
  "id": "bb37e39e-9e05-4b47-8ad8-8201ca483c03",
  "title": "민주당은 통신사를 협박해 지귀연을 사찰했다",
  "level": 2,
  "parent_worldview_id": "dc6f1515-5004-4619-9444-99f22860d0f5",
  "version": 2,
  "frame": {
    "subject": "민주당",
    "action": "통신사를 협박해 사찰한다",
    "object": "지귀연"
  },
  "perception_ids": ["437107a1-...", "2a3f8bc1-...", ...]
}
```

---

## 4️⃣ PERCEPTION_WORLDVIEW_LINKS (N:M 관계)

**개수**: 541개

### 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID | Primary key |
| `perception_id` | UUID | Foreign key → layered_perceptions.id |
| `worldview_id` | UUID | Foreign key → worldviews.id |
| `relevance_score` | FLOAT | 관련도 점수 (0-1) |
| `created_at` | TIMESTAMPTZ | 생성 시각 |

### Unique 제약

```sql
UNIQUE (perception_id, worldview_id)
```
→ 동일한 perception-worldview 쌍은 1개만 존재

### 연결

- **← layered_perceptions** (N:1)
  - `perception_id` → `layered_perceptions.id`
- **← worldviews** (N:1)
  - `worldview_id` → `worldviews.id`

### 매칭 알고리즘

**Semantic Similarity 기반**:
- **Actor match** (60%): Subject 키워드 일치
- **Action match** (30%): Methods/Action 일치
- **Object match** (10%): 기본 점수

**Threshold**: 0.4 (40% 이상 일치 시 링크 생성)

### 예시

```json
{
  "id": "f8a92bc3-...",
  "perception_id": "437107a1-...",
  "worldview_id": "bb37e39e-...",
  "relevance_score": 0.63,
  "created_at": "2025-10-15T04:12:34Z"
}
```

---

## 🔄 데이터 흐름 예시

### 1. Content 수집 → Perception 생성

```python
# 1. Content 수집
content = {
  "title": "민주, 지귀연 핸드폰...",
  "body": "...",
  "source_url": "..."
}
→ contents 테이블에 삽입

# 2. Perception 분석 (ReasoningStructureExtractor)
→ GPT-4o 분석
→ layered_perceptions 테이블에 삽입
  - 3층 구조 추출
  - mechanisms, actor, logic_chain 추출
```

### 2. Worldview 매칭

```python
# 3. Hierarchical Matcher
→ 각 perception과 하위 세계관 비교
→ Semantic similarity 계산
→ Threshold 0.4 이상이면 링크 생성
→ perception_worldview_links 테이블에 삽입
```

### 3. Dashboard 조회

```typescript
// API: GET /api/worldviews/[id]
{
  worldview: {
    id: "dc6f1515-...",
    title: "민주당은 불법 사찰로 국민을 감시한다",
    level: 1,
    children: [
      { id: "bb37e39e-...", title: "민주당은 통신사를..." },
      ...
    ]
  },
  layered_perceptions: [
    {
      id: "437107a1-...",
      mechanisms: [...],
      actor: {...},
      logic_chain: [...],
      explicit_claims: [...],
      content: {
        title: "민주, 지귀연 핸드폰...",
        source_url: "..."
      }
    },
    ...
  ]
}
```

---

## 📈 통계

| 메트릭 | 값 |
|--------|-----|
| **Contents** | 456개 |
| **Perceptions** | 499개 |
| **Coverage** | 100% (456/456 content) |
| **Worldviews** | 63개 (7 상위 + 44 하위 + 12 archived) |
| **Links** | 541개 |
| **평균 links/perception** | 1.08개 |
| **평균 perceptions/worldview** | 10.6개 |

---

## 🔗 참고 문서

- [README.md](../README.md) - 프로젝트 개요
- [CLAUDE.md](../CLAUDE.md) - 개발 가이드
- [DATA_COMPLETENESS_REPORT.md](../DATA_COMPLETENESS_REPORT.md) - 완결성 보고서
