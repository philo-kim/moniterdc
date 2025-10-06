# Phase 1 완료 보고서

## 개요
**기간**: 2025-10-01 (Day 1-10)
**목표**: Worldview Deconstruction Engine의 기본 인프라 구축
**상태**: ✅ 완료

---

## 구현 내용

### 1. 데이터베이스 스키마 (Day 1-2) ✅

**위치**: `supabase/migrations/`

#### 구현된 테이블:

1. **contents** (100_create_contents.sql)
   - 모든 소스의 콘텐츠를 source-independent 방식으로 저장
   - `source_type`, `source_url`, `title`, `body`, `metadata`
   - `base_credibility`: 소스별 기본 신뢰도 (DC Gallery: 0.2)

2. **perceptions** (101_create_perceptions.sql)
   - 콘텐츠에서 추출된 인식 저장
   - `perceived_subject`, `perceived_attribute`, `perceived_valence`
   - `claims[]`, `keywords[]`, `emotions[]`
   - `perception_embedding` (vector 1536): 의미적 유사도 검색용

3. **perception_connections** (102_create_perception_connections.sql)
   - 인식 간 연결 관계 저장
   - `connection_type`: temporal, thematic, causal, semantic, social
   - `strength`: 0.0~1.0 연결 강도

4. **worldviews** (103_create_worldviews.sql)
   - 누적된 인식 패턴에서 감지된 세계관 저장
   - `frame`: 핵심 프레임 (예: "민주당 = 친중 매국 세력")
   - `strength_cognitive`, `strength_temporal`, `strength_social`, `strength_structural`
   - `formation_phases`: 씨앗/성장/정점 단계
   - `cognitive_mechanisms`: 인지편향 메커니즘
   - `structural_flaws`: 구조적 결함
   - `deconstruction`: 해체 전략

5. **rebuttals** (104_create_rebuttals.sql)
   - 세계관에 대한 반박 저장
   - `rebuttal_type`: fact_check, counter_narrative, structural_analysis

#### RPC Functions (105_create_rpc_functions.sql):
- `search_similar_perceptions()`: Vector 유사도 검색
- `search_similar_worldviews()`: 세계관 유사도 검색
- `update_worldview_stats()`: 세계관 통계 업데이트
- `get_perception_connections()`: 양방향 연결 조회
- `calculate_rebuttal_quality()`: 반박 품질 점수 계산

#### Indexes:
- Vector 검색 성능을 위한 HNSW 인덱스
- `subject`, `valence`, `created_at` 등에 B-tree 인덱스

**적용 상태**: Supabase에 성공적으로 적용 완료

---

### 2. Content Collector (Day 3-4) ✅

**위치**: `engines/collectors/content_collector.py`

#### 구현 내용:
- **Source-Independent Architecture**: 다양한 소스를 통합 처리
- **Adapter Pattern**: `BaseAdapter` 추상 클래스 + 각 소스별 구현
- **DC Gallery Adapter**:
  - mgallery 지원 (uspolitics는 mgallery)
  - 개념글(concept posts) 필터링 (`exception_mode=recommend`)
  - HTML 파싱 및 전문 수집
  - 중복 체크 (source_url 기준)

#### 테스트 결과:
```
✅ 5개 posts 수집 성공
- Source: DC Gallery (uspolitics - 미국정치 갤러리)
- 신뢰도: 0.2 (익명 커뮤니티)
- 수집 시간: ~3초
```

---

### 3. Perception Extractor (Day 5-6) ✅

**위치**:
- `engines/extractors/perception_extractor.py` (LLM 기반)
- `engines/extractors/perception_extractor_simple.py` (규칙 기반)

#### 구현 내용:
- **LLM 기반 추출** (OpenAI GPT-4 / Claude):
  - 정치 콘텐츠 분석 전문 프롬프트
  - JSON 구조화된 출력
  - Subject, Attribute, Valence, Claims, Keywords, Emotions 추출

- **규칙 기반 추출** (API quota 없이 테스트용):
  - 키워드 매칭
  - 정치 주체 감지 (민주당, 윤석열, 이재명 등)
  - 부정/긍정 속성 분류

#### Embedding 생성:
- OpenAI `text-embedding-3-small` (1536 차원)
- 의미적 유사도 검색을 위한 벡터화

#### 테스트 결과:
```
✅ 6개 perceptions 추출 (5개 contents에서)
- Subject: 정치권, 민주당, 정부 등
- Attributes: 친중, 무능, 독재 등
- Valence: negative, neutral, positive
```

---

### 4. Connection Detector (Day 7-8) ✅

**위치**: `engines/detectors/connection_detector.py`

#### 구현 내용:
1. **Temporal Connections**:
   - 7일 이내 생성된 인식 간 연결
   - 시간적 맥락 파악

2. **Thematic Connections**:
   - 동일 subject를 가진 인식 연결
   - 특정 주체에 대한 누적된 인식 추적

3. **Semantic Connections**:
   - Vector similarity search (cosine similarity)
   - Threshold: 0.7 이상
   - 의미적으로 유사한 인식 그룹화

#### 테스트 결과:
```
✅ 147개 connections 감지
- Temporal: 시간대별 그룹화
- Thematic: 동일 주체별 클러스터링
- Semantic: 유사 내용 연결
```

---

### 5. Analysis Pipeline (Day 9-10) ✅

**위치**: `engines/pipeline/analysis_pipeline.py`

#### 구현 내용:
완전히 통합된 분석 파이프라인:

```
[Content Collection] → [Perception Extraction] → [Connection Detection] → (Worldview Formation)
```

**주요 기능**:
- `run_collection()`: 콘텐츠 수집 단계
- `run_extraction()`: 인식 추출 단계
- `run_connection()`: 연결 감지 단계
- `run_full_pipeline()`: 전체 파이프라인 실행
- `get_pipeline_stats()`: 시스템 통계 조회

#### 파이프라인 흐름:
1. **Content Source** (DC Gallery, 향후 YouTube, News 등)
   ↓
2. **Parse & Store** (contents 테이블)
   ↓
3. **LLM Analysis** (GPT/Claude로 인식 추출)
   ↓
4. **Perception Storage** (perceptions 테이블 + embedding)
   ↓
5. **Connection Detection** (temporal, thematic, semantic)
   ↓
6. **Graph Building** (perception_connections 테이블)

#### 테스트 결과:
```
📊 최종 시스템 상태:
- Total Contents: 9
- Total Perceptions: 11
- Total Connections: 195
- Total Worldviews: 0 (Phase 2에서 구현 예정)
```

---

## 기술 스택

### Backend:
- **Python 3.12**
- **Supabase** (PostgreSQL + pgvector)
- **OpenAI API** (GPT-4o-mini, text-embedding-3-small)
- **BeautifulSoup4** (HTML 파싱)
- **aiohttp** (비동기 HTTP 요청)

### Database:
- **PostgreSQL 15+**
- **pgvector extension** (벡터 유사도 검색)
- **HNSW 인덱스** (빠른 벡터 검색)

---

## 디렉토리 구조

```
moniterdc/
├── supabase/
│   └── migrations/          # DB 스키마 정의
│       ├── 100_create_contents.sql
│       ├── 101_create_perceptions.sql
│       ├── 102_create_perception_connections.sql
│       ├── 103_create_worldviews.sql
│       ├── 104_create_rebuttals.sql
│       └── 105_create_rpc_functions.sql
│
├── engines/                 # 핵심 엔진 코드
│   ├── utils/               # 유틸리티
│   │   ├── supabase_client.py
│   │   └── embedding_utils.py
│   ├── adapters/            # 소스 어댑터
│   │   ├── base_adapter.py
│   │   └── dc_gallery_adapter.py
│   ├── collectors/          # 콘텐츠 수집기
│   │   └── content_collector.py
│   ├── extractors/          # 인식 추출기
│   │   ├── perception_extractor.py
│   │   └── perception_extractor_simple.py
│   ├── detectors/           # 연결 감지기
│   │   └── connection_detector.py
│   └── pipeline/            # 통합 파이프라인
│       └── analysis_pipeline.py
│
└── tests/                   # 테스트 코드
    ├── test_new_schema.py
    ├── test_content_collector.py
    ├── test_perception_extractor.py
    ├── test_simple_extractor.py
    ├── test_connection_detector.py
    ├── test_full_pipeline.py
    ├── test_analysis_pipeline.py
    └── test_pipeline_with_existing.py
```

---

## 핵심 설계 원칙

### 1. Source-Independent Architecture
모든 콘텐츠 소스를 동일한 방식으로 처리:
- DC Gallery, YouTube, News, Instagram 등 모두 `contents` 테이블에 저장
- `source_type` + `metadata`로 소스별 특성 보존
- Adapter Pattern으로 소스 추가 용이

### 2. 3-Layer Architecture
```
Layer 1 (Reality): Physical content
    ↓
Layer 2 (Perception): Extracted impressions
    ↓
Layer 3 (Worldview): Accumulated patterns
```

### 3. Vector-Based Similarity
- Embedding으로 의미적 유사도 측정
- HNSW 인덱스로 빠른 검색 (O(log n))
- Threshold 기반 연결 생성

### 4. Extensibility
- 새로운 소스 추가: `BaseAdapter` 상속
- 새로운 연결 타입: `connection_type` 추가
- 새로운 분석 메커니즘: Pipeline 단계 추가

---

## 다음 단계 (Phase 2)

### Phase 2 목표: Worldview Detection & Mechanism Analysis

1. **Worldview Detector**:
   - 연결된 인식 그룹에서 패턴 감지
   - Frame 추출 (예: "민주당 = 친중")
   - 강도 계산 (cognitive, temporal, social, structural)

2. **Mechanism Analyzer**:
   - 인지 편향 감지 (confirmation bias, availability heuristic)
   - 시간적 패턴 분석 (씨앗 → 성장 → 정점)
   - 사회적 확산 추적 (cross-platform)

3. **Structure Analyzer**:
   - 논리적 결함 탐지
   - 구조적 취약점 분석
   - 해체 전략 생성

---

## 성과

✅ **완전히 작동하는 3-layer 인프라 구축**
✅ **Source-independent 아키텍처로 확장성 확보**
✅ **Vector 기반 의미적 유사도 검색 구현**
✅ **End-to-end 파이프라인 검증 완료**

---

## 문서

- [시스템 아키텍처](SYSTEM_ARCHITECTURE.md)
- [구현 계획](IMPLEMENTATION_PLAN.md)
- [Worldview Engine 설계](WORLDVIEW_ENGINE_FINAL.md)

---

**작성일**: 2025-10-01
**Phase 1 완료일**: 2025-10-01
**다음 마일스톤**: Phase 2 - Worldview Detection (예정)
