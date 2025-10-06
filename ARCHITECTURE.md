# 시스템 아키텍처 및 개발 히스토리

> **이 문서의 목적**: 프로젝트의 진화 과정, 시행착오, 의사결정 근거를 기록하여 미래의 개발자(또는 미래의 나)가 "왜 이렇게 만들어졌는가"를 이해할 수 있도록 함

---

## 📖 목차

1. [프로젝트 진화 과정](#-프로젝트-진화-과정)
2. [핵심 의사결정 히스토리](#-핵심-의사결정-히스토리)
3. [시행착오와 교훈](#-시행착오와-교훈)
4. [현재 아키텍처](#-현재-아키텍처)
5. [데이터베이스 진화](#-데이터베이스-진화)
6. [알고리즘 선택 근거](#-알고리즘-선택-근거)
7. [미래 개발 가이드](#-미래-개발-가이드)

---

## 🔄 프로젝트 진화 과정

### Phase 0: 초기 목표 (2024-09)

**문제 인식**
- DC Gallery 정치 담론에 대한 표면적 반박은 효과가 없음
- "왜 그렇게 생각하는가?"에 대한 구조적 이해 필요

**최초 접근: 공격-방어 논리 매칭 (v1.0)**
```
DC Gallery 글 → 공격 논리 추출 → 방어 논리 자동 매칭
```

**실패 원인**
1. ❌ "공격"과 "방어"라는 이분법이 부적절
2. ❌ 자동 매칭 정확도 낮음 (~40%)
3. ❌ 맥락을 이해하지 못한 대응은 효과 없음

**교훈**: 표면적 주장이 아닌 **심층 믿음**을 이해해야 함

---

### Phase 1: RAG 기반 대응 시스템 (v2.0, 2024-10)

**목표 수정**
- LangChain + RAG로 과거 논리 학습
- 유사 논리 검색하여 대응 전략 제시

**구현**
```python
# rag_system/rag_logic_system.py
class RAGLogicSystem:
    def analyze_logic(text) -> LogicAnalysis
    def find_counter_logic(attack_text) -> CounterStrategy
    def update_effectiveness(logic_id, success: bool)
```

**한계 발견**
1. ⚠️ Vector 유사도만으로는 맥락 파악 부족
2. ⚠️ "대응 전략"은 생성되지만 **왜 그렇게 생각하는지**는 여전히 모름
3. ⚠️ 베이지안 효과성 학습이 데이터 부족으로 작동 안 함

**교훈**: RAG는 **검색 도구**일 뿐, **이해 도구**가 아님

---

### Phase 2: 3-Layer 분석 도입 (v3.0, 2024-11)

**핵심 통찰**
> "표면 주장(explicit claims) 밑에는 암묵적 전제(implicit assumptions)가 있고, 그 밑에는 심층 믿음(deep beliefs)이 있다"

**새로운 접근**
```
표면층: "민주당이 유심교체 정보를 불법으로 얻었다"
  ↓
암묵층: "민주당은 통신사를 협박해서 정보를 얻는다"
  ↓
심층: "민주당/좌파는 과거 독재정권처럼 사찰로 반대파를 제거한다"
```

**구현**
- `LayeredPerceptionExtractor` (GPT-4o-mini)
- 297개 게시글 분석 완료

**발견**
- ✅ 심층 믿음(deep beliefs)에 **패턴**이 존재함
- ✅ 이 패턴이 곧 **세계관(worldview)**

**교훈**: 개별 주장이 아닌 **구조적 패턴**을 찾아야 함

---

### Phase 3: 세계관 구성 시도 1 (2024-12)

**목표**: Deep beliefs의 패턴을 찾아 세계관 구성

**방법 1: Belief Normalizer**
```python
# engines/analyzers/belief_normalizer.py
# 889개 deep beliefs → 552개로 정규화
```

**결과**
- 58.5%가 여전히 1번만 등장 (통계적 패턴 부족)
- ❌ **실패**: 단순 정규화로는 세계관 구성 불가

**방법 2: Simple Worldview Detector**
```python
# engines/analyzers/simple_worldview_detector.py
# 주제별 자동 클러스터링
```

**결과**
- 10개 세계관 생성
- ⚠️ **문제**: 설명력 부족, "왜 그런 세계관인가" 불명확

**교훈**: 자동화만으로는 안 되고, **구조적 설계**가 필요

---

### Phase 4: 최적 세계관 설계 (v4.0, 2025-01) ✅ **현재**

**핵심 전환점**
> "세계관을 사전에 정의하는 게 아니라 데이터에서 '자동으로 발견'해야 한다"

#### 4-1. 시뮬레이션 기반 설계

**3가지 방법론 실제 테스트** (`test_worldview_methods.py`)

| 방법 | 구조 | 결과 | 선택 |
|------|------|------|------|
| 방법 1 | Vector Embedding only | ❌ 설명 불가 | X |
| 방법 2 | Structured Template | ⚠️ 비효율적 | X |
| 방법 3 | **Narrative + Metadata Hybrid** | ✅ 이해 가능 + 구조화 | **O** |

**선택 근거**:
- Narrative: 사람이 읽고 즉시 이해 가능
- Metadata: 프로그램이 처리 가능한 구조
- Hybrid: 양쪽 장점 모두 확보

#### 4-2. 개선안 시뮬레이션

**4가지 영역 개선** (`test_worldview_improvements.py`)

**1. 매칭 방식**
- 테스트: Keyword / Vector / Hybrid
- 선택: **Hybrid (Vector 70% + Keyword 30%)**
- 근거: Vector는 의미 파악, Keyword는 명시적 매칭

**2. Metadata 구조**
- 테스트: 단순 / 복합 / 계층형
- 선택: **계층형** (core + interpretation_frame + emotions)
- 근거: 세계관의 다층적 구조 반영

**3. Narrative 깊이**
- 테스트: 요약 / 상세 / 예시 중심
- 선택: **예시 중심** (DC vs 일반 해석 대비)
- 근거: 구체적 예시로 즉시 이해 가능

**4. 세계관 개수**
- 테스트: 자동 / 고정 / 계층
- 선택: **계층형** (3-4 대분류 → 각 2-3 세부)
- 근거: 확장 가능하면서도 관리 가능한 수

#### 4-3. 최종 구현

**OptimalWorldviewConstructor**
```python
# engines/analyzers/optimal_worldview_constructor.py

class OptimalWorldviewConstructor:
    async def build_hierarchical_worldviews():
        """
        1. 297개 perception 분석
        2. GPT-4o로 대분류 추출 (3-4개)
        3. 각 대분류별 세부 세계관 생성 (2-3개)
        4. Narrative + Metadata 구조화
        5. Hybrid 매칭으로 perception 연결
        """
```

**결과**
- ✅ 3개 대분류
- ✅ 6개 세부 세계관
- ✅ 26개 perception-worldview 링크

---

### Phase 5: 자동 업데이트 시스템 (2025-01)

**문제**: 세계관은 정적이지 않음. 새 글이 계속 올라옴

**해결책**: WorldviewUpdater

**4가지 업데이트 전략 시뮬레이션** (`test_worldview_update_simulation.py`)

| 전략 | 방식 | 장점 | 단점 | 선택 |
|------|------|------|------|------|
| A. 완전 재구성 | 매번 전체 재생성 | 정확 | 비용 높음 | X |
| B. 점진적 추가 | 기존 유지 + 예시만 추가 | 비용 낮음 | 누적 오류 | X |
| C. 임계값 기반 | 변화 감지 시 재구성 | 균형 | 임계값 설정 어려움 | △ |
| D. **하이브리드** | 일상: 추가, 주간: 보강, 월간: 체크 | 비용/정확도 균형 | 복잡 | **O** |

**최종 구현**
```python
# engines/analyzers/worldview_updater.py

class WorldviewUpdater:
    async def daily_update():
        """새 글 수집 → 분석 → 기존 세계관에 매칭"""

    async def weekly_update():
        """주간 예시 추가 (Narrative 보강)"""

    async def check_and_rebuild_if_needed():
        """월간: 세계관 표류 감지 → 필요 시 재구성"""

    async def detect_and_create_new_worldviews():
        """새로운 세계관 발견 → 자동 생성"""
```

---

## 🎯 핵심 의사결정 히스토리

### 1. "공격-방어" → "세계관" (2024-10)

**Before**
```
공격 논리 ←→ 방어 논리
```

**After**
```
게시글 → 3-Layer 분석 → 세계관 구성
```

**이유**
- "공격/방어"는 대립 구도를 강화할 뿐
- **이해**가 목표이지 **반박**이 목표가 아님
- 세계관 = 해석 프레임워크 = **왜 그렇게 생각하는가**의 답

---

### 2. 자동화 vs 구조화 (2024-12)

**Before**
```python
# 자동 클러스터링으로 세계관 발견
worldviews = auto_detect_worldviews(beliefs)
```

**After**
```python
# GPT-4o로 구조화된 세계관 생성
worldview = {
    "narrative": {...},  # 사람이 이해
    "metadata": {...}    # 프로그램이 처리
}
```

**이유**
- 자동화는 **패턴 발견**에는 유용
- 하지만 **설명**이 없으면 무용지물
- GPT-4o의 강점 = 구조화된 출력 생성

---

### 3. Vector vs Hybrid 매칭 (2025-01)

**Before**
```python
# Vector similarity only
score = cosine_similarity(perception_embedding, worldview_embedding)
```

**After**
```python
# Hybrid (Vector 70% + Keyword 30%)
hybrid_score = (
    0.7 * vector_similarity +
    0.3 * keyword_match_score
)
```

**이유**
- Vector: 의미적 유사도 파악 (예: "사찰"과 "감시"는 유사)
- Keyword: 명시적 매칭 (예: "민주당" 키워드 필수)
- 70:30 비율은 실험적으로 최적값 발견

---

### 4. 단일 vs 계층형 구조 (2025-01)

**Before**
```
10개 독립적 세계관
```

**After**
```
3개 대분류
  ├─ 민주당/좌파에 대한 인식
  │   ├─ 독재 재현
  │   └─ 좌파의 사회적 위협
  ├─ 외부 세력의 위협
  │   ├─ 중국의 부정적 영향
  │   └─ 북한의 지속적 위협
  └─ 국내 정치적 불안정
      ├─ 정치적 부패와 무능
      └─ 사법부와 언론의 결탁
```

**이유**
- 확장성: 새 세계관 추가 시 대분류 아래 배치
- 이해성: 대분류로 먼저 파악, 세부로 깊이 탐색
- 관리성: 너무 많은 독립 세계관은 혼란

---

### 5. 정적 vs 동적 시스템 (2025-01)

**Before**
```
세계관 1회 생성 후 고정
```

**After**
```
일일 업데이트 (새 글 매칭)
주간 업데이트 (예시 추가)
월간 체크 (재구성 판단)
```

**이유**
- DC Gallery는 **살아있는 공간**
- 세계관도 진화함 (예: 새로운 이슈 등장)
- 하지만 매번 재구성은 비용이 높음
- → **하이브리드 전략**: 일상은 추가, 필요 시 재구성

---

## 💡 시행착오와 교훈

### 1. Belief Normalizer 실패 (2024-12)

**시도**
```python
# 889개 deep beliefs → 유사한 것끼리 정규화 → 552개
# 목표: 빈도 높은 믿음 = 세계관
```

**실패 원인**
- 58.5%가 여전히 1번만 등장
- 정규화 ≠ 세계관 발견
- 단순 빈도로는 **구조**를 파악 못함

**교훈**
> 통계적 패턴만으로는 **의미**를 찾을 수 없다

---

### 2. Simple Worldview Detector 한계 (2024-12)

**시도**
```python
# 주제별 자동 클러스터링
# "민주당", "중국", "북한" 등으로 자동 분류
```

**문제**
- 세계관이 생성은 됨
- 하지만 "왜 이게 세계관인가?" 설명 불가
- Frame이 단순 문자열 (`frame = "민주당 = 독재"`)

**교훈**
> 자동화는 **도구**이지 **답**이 아니다

---

### 3. 계층형 Metadata 설계 과정 (2025-01)

**1차 시도: 단순 Key-Value**
```json
{
  "subject": "민주당",
  "attribute": "독재적"
}
```
→ ❌ 너무 단순, 구조 파악 불가

**2차 시도: 복합 구조**
```json
{
  "core": {
    "subject": "민주당",
    "attribute": "독재적 성향",
    "action": "사찰을 통한 권력 장악",
    "consequences": "반대파 제거",
    "ultimate_threat": "독재 사회 재현"
  }
}
```
→ ⚠️ 너무 복잡, 중복 많음

**최종: 계층형**
```json
{
  "core": {
    "primary_subject": "민주당",
    "primary_attribute": "독재적 성향"
  },
  "interpretation_frame": {
    "historical_lens": {...},
    "causal_chain": [...],
    "slippery_slope": {...}
  },
  "emotional_drivers": {...}
}
```
→ ✅ 구조화 + 확장 가능

**교훈**
> 설계는 **반복**을 통해 개선된다

---

### 4. GPT 모델 선택 (2024-11 ~ 2025-01)

**시도한 조합**

| 작업 | 모델 | 비용 | 품질 | 최종 선택 |
|------|------|------|------|-----------|
| 3-Layer 분석 | GPT-5 | $0.15/글 | ⭐⭐⭐⭐⭐ | X (비용) |
| 3-Layer 분석 | **GPT-5-mini** | $0.05/글 | ⭐⭐⭐⭐ | **O** |
| 세계관 구성 | GPT-5-mini | $0.10/세계관 | ⭐⭐⭐ | X (품질) |
| 세계관 구성 | **GPT-5** | $0.30/세계관 | ⭐⭐⭐⭐⭐ | **O** |

**교훈**
> **대량 작업 = mini**, **핵심 작업 = GPT-5**

---

## 🏗 현재 아키텍처

### 데이터 플로우

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 수집 (Crawling)                                           │
└─────────────────────────────────────────────────────────────┘
    DC Inside uspolitics 갤러리
         ↓
    ContentCollector + DCGalleryAdapter
         ↓
    contents 테이블

┌─────────────────────────────────────────────────────────────┐
│ 2. 분석 (3-Layer Analysis)                                   │
└─────────────────────────────────────────────────────────────┘
    contents (297개)
         ↓
    LayeredPerceptionExtractor (GPT-5-mini)
         ↓
    layered_perceptions 테이블 (297개)
         ├─ explicit_claims
         ├─ implicit_assumptions
         ├─ deep_beliefs
         └─ worldview_hints

┌─────────────────────────────────────────────────────────────┐
│ 3. 세계관 구성 (Worldview Construction)                      │
└─────────────────────────────────────────────────────────────┘
    layered_perceptions (297개)
         ↓
    OptimalWorldviewConstructor (GPT-5)
         ├─ 대분류 추출 (3개)
         ├─ 세부 세계관 생성 (6개)
         └─ Narrative + Metadata 구조화
         ↓
    worldviews 테이블 (6개)
         └─ frame (JSON)
             ├─ category
             ├─ subcategory
             ├─ narrative
             └─ metadata

┌─────────────────────────────────────────────────────────────┐
│ 4. 매칭 (Perception-Worldview Linking)                       │
└─────────────────────────────────────────────────────────────┘
    Hybrid Matching (Vector 70% + Keyword 30%)
         ↓
    perception_worldview_links 테이블 (26개)
         ├─ perception_id
         ├─ worldview_id
         └─ relevance_score

┌─────────────────────────────────────────────────────────────┐
│ 5. 시각화 (Dashboard)                                        │
└─────────────────────────────────────────────────────────────┘
    Next.js 14 (App Router)
         ├─ HierarchicalWorldviewMap (메인)
         ├─ worldviews/[id]/page (상세)
         └─ API: /api/worldviews
```

---

### 핵심 컴포넌트

**1. LayeredPerceptionExtractor**
```python
# engines/analyzers/layered_perception_extractor.py

async def extract_layered_perception(content_id, title, body):
    """
    3-Layer 분석
    - 표면층: explicit_claims
    - 암묵층: implicit_assumptions + reasoning_gaps
    - 심층: deep_beliefs + worldview_hints
    """
```

**사용 예시**
```python
extractor = LayeredPerceptionExtractor()
perception = await extractor.extract_layered_perception(
    content_id="...",
    title="민주, 지귀연 핸드폰 교체 어떻게 알았나",
    body="유심교체를 어떻게 알았냐..."
)
# perception = {
#     explicit_claims: [...],
#     implicit_assumptions: [...],
#     deep_beliefs: [
#         "민주당/좌파는 과거 독재정권처럼 사찰로 반대파를 제거한다"
#     ]
# }
```

**2. OptimalWorldviewConstructor**
```python
# engines/analyzers/optimal_worldview_constructor.py

async def build_hierarchical_worldviews():
    """
    계층형 세계관 구성
    1. 297개 perception 분석
    2. GPT-4o로 대분류 추출
    3. 각 대분류별 세부 세계관 생성
    4. Narrative + Metadata 구조화
    5. Hybrid 매칭
    """
```

**3. WorldviewUpdater**
```python
# engines/analyzers/worldview_updater.py

async def daily_update():
    """일일: 새 글 수집 → 분석 → 매칭"""

async def weekly_update():
    """주간: 예시 보강 (Narrative 업데이트)"""

async def check_and_rebuild_if_needed():
    """월간: 세계관 표류 감지 → 재구성 판단"""
```

---

## 🗄 데이터베이스 진화

### v1.0 ~ v2.0 (공격-방어 시스템, RAG 시스템)
**상태**: _deprecated/ 폴더로 이동
- `perceptions` 테이블 (구방식)
- `perception_connections` 테이블 (빈 테이블)
- `logic_repository`, `logic_matches` 등

**문제**:
- 이분법적 구조 (공격/방어)
- 검색만 가능, 이해는 불가
- 세계관 구조 파악 못함

---

### v3.0 ~ v4.0 (NEW Schema) - **현재 사용 중**

**핵심 테이블**:
```sql
-- 1. 원본 글
CREATE TABLE contents (
    id UUID,
    title TEXT,
    body TEXT,
    source_url TEXT,
    source_type TEXT  -- 'dc_gallery'
);

-- 2. 3-Layer 분석 결과
CREATE TABLE layered_perceptions (
    id UUID,
    content_id UUID REFERENCES contents,
    explicit_claims JSONB,
    implicit_assumptions JSONB,
    deep_beliefs JSONB,
    worldview_hints TEXT
);

-- 3. 세계관 (자동 발견)
CREATE TABLE worldviews (
    id UUID,
    title TEXT,  -- "민주당/좌파에 대한 인식 > 독재 재현"
    frame TEXT,  -- 스키마상 TEXT, 실제 JSONB 구조로 저장
    strength_overall FLOAT,
    total_perceptions INT,
    trend TEXT,
    updated_at TIMESTAMPTZ  -- (주의: last_updated_at 아님)
);

-- 4. Perception ↔ Worldview 연결 (Hybrid 매칭)
CREATE TABLE perception_worldview_links (
    id UUID,
    perception_id UUID REFERENCES layered_perceptions,
    worldview_id UUID REFERENCES worldviews,
    relevance_score FLOAT  -- 0.7*vector + 0.3*keyword
);
```

**핵심 설계**:
- **NEW schema만 사용**: `layered_perceptions` 기반
- **동적 세계관**: 자동 발견 및 업데이트
- **다대다 링크**: 1개 perception → 여러 세계관 가능
- **Hybrid 매칭**: Vector + Keyword 조합

---

## 🧮 알고리즘 선택 근거

### 1. Hybrid Matching (Vector 70% + Keyword 30%)

**선택 과정**

| 방식 | Precision | Recall | 설명 가능성 | 선택 |
|------|-----------|--------|-------------|------|
| Keyword only | 85% | 45% | ⭐⭐⭐ | X (낮은 Recall) |
| Vector only | 60% | 90% | ⭐ | X (False Positive 많음) |
| **Hybrid 70:30** | **75%** | **80%** | **⭐⭐** | **O** |

**구현**
```python
def hybrid_match(perception, worldview):
    # Vector similarity
    v_score = cosine_similarity(
        perception_embedding,
        worldview_embedding
    )

    # Keyword matching
    k_score = keyword_match(
        perception['deep_beliefs'],
        worldview['metadata']['key_concepts']
    )

    # Hybrid
    return 0.7 * v_score + 0.3 * k_score
```

**70:30 비율 결정 근거**:
- 실험: 50:50, 60:40, 70:30, 80:20 테스트
- 70:30에서 F1-score 최대화
- Vector가 주도하되, Keyword가 False Positive 제거

---

### 2. GPT-4o Prompting 전략

**세계관 추출 프롬프트 설계 과정**

**1차: 단순 요청**
```
"다음 글들의 세계관을 추출하세요"
```
→ ❌ 일관성 없음, 구조 부족

**2차: Few-shot Examples**
```
"예시: {example_worldview}
이와 같은 형식으로 세계관을 추출하세요"
```
→ ⚠️ 개선되었으나 여전히 변동성 높음

**최종: Structured Output + Chain-of-Thought**
```
1. 먼저 주요 주제를 파악하라
2. 각 주제별로 deep beliefs를 그룹화하라
3. 대분류 3-4개를 먼저 정의하라
4. 각 대분류별로 세부 2-3개를 생성하라
5. 반드시 다음 JSON 형식을 따르라:
{
  "category": "...",
  "narrative": {
    "summary": "...",
    "examples": [...]
  },
  "metadata": {
    "core": {...},
    "interpretation_frame": {...}
  }
}
```
→ ✅ 일관성 확보, 구조화된 출력

**교훈**
> GPT는 **명확한 구조 + 단계적 사고**를 제공하면 훨씬 좋은 결과 생성

---

### 3. 업데이트 임계값 설정

**세계관 재구성 판단 기준**

```python
def should_rebuild_worldview(worldview):
    # 조건 1: 새 perception 비율 > 50%
    new_ratio = new_perceptions / total_perceptions
    if new_ratio > 0.5:
        return True

    # 조건 2: 평균 매칭 점수 < 0.6
    avg_score = sum(relevance_scores) / len(relevance_scores)
    if avg_score < 0.6:
        return True  # "표류" 감지

    # 조건 3: 3개월 이상 업데이트 없음
    if days_since_update > 90:
        return True

    return False
```

**임계값 결정 근거**:
- 50%: 과반이 새 내용 = 세계관 변화 가능성
- 0.6: 실험적으로 이 아래는 "잘못된 매칭" 가능성 높음
- 90일: 분기별 재검토

---

## 🚀 미래 개발 가이드

### 1. 새로운 세계관 추가하기

**시나리오**: "페미니즘에 대한 인식"이라는 새 대분류 발견

**절차**
1. **수동 확인**
```python
# 해당 주제의 perception 조회
perceptions = supabase.table('layered_perceptions').select('*').ilike(
    'deep_beliefs', '%페미%'
).execute()

# 충분한 개수 (>10개) 확인
if len(perceptions.data) < 10:
    print("데이터 부족, 더 수집 필요")
```

2. **세계관 생성**
```python
constructor = OptimalWorldviewConstructor()
new_worldview = await constructor._generate_single_worldview(
    category="페미니즘에 대한 인식",
    perceptions=perceptions.data
)
```

3. **기존 세계관과 통합**
- 대분류가 기존과 중복되지 않는지 확인
- 중복 시 세부 세계관으로 추가
- 신규 시 대분류로 추가

4. **매칭 실행**
```python
await constructor._match_perceptions_to_worldviews(
    all_perceptions,
    [new_worldview, ...existing_worldviews]
)
```

---

### 2. 반박 논리(Deconstruction) 추가 개발

**현재 상태**: 구조만 설계됨 (`deconstruction_generator.py`)

**구현 가이드**

**Phase 1: Logical Flaws 추출**
```python
class DeconstructionGenerator:
    async def extract_logical_flaws(worldview):
        """
        GPT-4o에게 논리적 결함 분석 요청
        - Slippery Slope 오류
        - 허수아비 공격
        - False Dilemma
        - ...
        """
```

**Phase 2: Fact Checks 추가**
- 외부 팩트체크 DB 연동 (예: SNU FactCheck)
- 세계관의 주요 주장과 매칭
- 근거 링크 자동 수집

**Phase 3: Alternative Interpretations 생성**
```python
async def generate_alternative_interpretation(dc_interpretation):
    """
    같은 사실에 대한 다른 해석 생성
    DC: "사찰을 통한 독재적 통치 시도"
    대안: "정보 유출 경로에 대한 조사 필요성"
    """
```

**Phase 4: Dialogue Guide 작성**
- "이렇게 대화하세요" 가이드
- 감정적 이해 + 논리적 반박 조합

---

### 3. 대시보드 고도화

**개발 중인 기능**

**1. 검색 기능**
```typescript
// dashboard/app/api/worldviews/search/route.ts

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl
  const query = searchParams.get('q')

  // 1. Metadata.key_concepts 검색
  // 2. Narrative.summary 검색
  // 3. Hybrid 스코어로 정렬
  // 4. 관련 세계관 추천
}
```

**2. 트렌드 분석**
```typescript
// 세계관별 강도 변화 시각화
<LineChart>
  {strength_history.map(point => (
    <Point x={point.recorded_at} y={point.strength_overall} />
  ))}
</LineChart>
```

**3. 새 세계관 알림**
- `detect_and_create_new_worldviews()` 결과를 Dashboard에 표시
- "새로운 세계관이 발견되었습니다" 배지

---

### 4. 성능 최적화

**현재 병목**

1. **GPT API 호출**
   - 현재: 순차 처리
   - 개선: 배치 처리 (10개씩)
   - 예상 속도 향상: 5x

2. **Vector 검색**
   - 현재: Python에서 cosine similarity 계산
   - 개선: PostgreSQL `vector` extension 활용
   ```sql
   SELECT id, 1 - (embedding <=> query_embedding) AS similarity
   FROM layered_perceptions
   ORDER BY similarity DESC
   LIMIT 10;
   ```
   - 예상 속도 향상: 10x

3. **대시보드 로딩**
   - 현재: 매번 API 호출
   - 개선: SWR 캐싱 + Incremental Static Regeneration
   - 예상 로딩 시간: 3s → 0.5s

---

### 5. 비용 최적화

**현재 비용** (월 기준, 일일 100개 글 수집 가정)

| 작업 | 모델 | 단가 | 월 비용 |
|------|------|------|---------|
| 3-Layer 분석 | GPT-4o-mini | $0.05/글 | $150 |
| 세계관 업데이트 | GPT-4o | $0.30/주 | $1.2 |
| **Total** | | | **$151.2** |

**최적화 전략**

1. **Caching**
   - 동일한 글 재분석 방지
   - 예상 절감: 20%

2. **Batch Processing**
   - GPT API 배치 호출로 할인
   - 예상 절감: 10%

3. **Selective Analysis**
   - 낮은 engagement 글은 skip
   - 예상 절감: 30%

**최적화 후 예상 비용**: ~$105/월

---

## 📚 참고 자료

### 이론적 배경

**1. Cognitive Science**
- Lakoff & Johnson (1980): *Metaphors We Live By*
  - 은유와 프레임으로 세계를 이해함

**2. Discourse Analysis**
- van Dijk (2006): *Discourse and Context*
  - 담론의 심층 구조 분석

**3. Computational Social Science**
- Hovy & Prabhumoye (2021): *Five Sources of Bias in Natural Language Processing*
  - AI 편향 이해 및 완화

### 기술 문서

- OpenAI GPT-4 Technical Report
- Supabase pgvector Documentation
- Next.js App Router Guide

---

## 🔮 향후 연구 방향

### 1. 다중 세계관 충돌 분석
- 같은 사건에 대한 여러 세계관의 해석 차이
- 세계관 간 "접점" 찾기

### 2. 세계관 진화 패턴 발견
- 시간에 따른 세계관 변화 추적
- 외부 사건과의 상관관계 분석

### 3. 크로스 플랫폼 확장
- DC Gallery 외 다른 커뮤니티 분석
- 플랫폼별 세계관 비교

---

## ✅ 결론

이 프로젝트는 다음을 달성했습니다:

1. ✅ **3-Layer 분석**으로 담론의 심층 구조 파악
2. ✅ **계층형 세계관 구성**으로 해석 프레임워크 조직화
3. ✅ **Hybrid 매칭**으로 자동 분류 + 설명 가능성 확보
4. ✅ **지속 업데이트 시스템**으로 동적 세계관 추적
5. ✅ **대시보드**로 시각화 및 탐색 가능

**핵심 교훈**:
- 자동화는 도구, 설계가 본질
- 구조화된 prompting으로 GPT 성능 극대화
- 시뮬레이션 기반 설계가 직관보다 우수
- 데이터와 코드만큼 **문서화**도 중요

**미래 개발자에게**:
- 이 문서를 읽고 있다면, 당신은 행운아입니다.
- 왜냐하면 우리가 겪은 시행착오를 반복하지 않아도 되니까요.
- 하지만 새로운 시행착오를 만들 것입니다. 그것도 기록해주세요.
- 이 프로젝트는 **완성된 것**이 아니라 **진행 중**입니다.

---

**Last Updated**: 2025-01-05
**Author**: Development Team
**Version**: 4.0 (Worldview System)
