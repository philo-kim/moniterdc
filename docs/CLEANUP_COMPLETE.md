# 코드베이스 정리 완료 ✅

**날짜**: 2025-10-14
**작업**: MoniterDC v2.0 아키텍처로 정리

---

## 정리 항목

### 1. DB 테이블 제거 (12개)
**Migration**: `supabase/migrations/402_remove_deprecated_tables.sql`

- ✅ perceptions (→ layered_perceptions로 대체)
- ✅ belief_patterns (사용처 없음)
- ✅ perception_connections (사용처 없음)
- ✅ logic_clusters (구 시스템)
- ✅ logic_repository (구 시스템)
- ✅ logic_matches (구 시스템)
- ✅ counter_arguments (구 시스템)
- ✅ rebuttals (사용처 없음)
- ✅ rebuttal_votes (사용처 없음)
- ✅ counter_argument_votes (사용처 없음)
- ✅ alerts (사용처 없음)
- ✅ system_stats (사용처 없음)

### 2. 엔진 정리 (5개)
**위치**: `engines/analyzers/_deprecated/`

- ✅ belief_normalizer.py
- ✅ optimal_worldview_constructor.py
- ✅ hybrid_perception_matcher.py
- ✅ context_guide_builder.py
- ✅ worldview_updater.py

### 3. 페이지 정리 (3개)
**위치**: `dashboard/app/_deprecated/`

- ✅ attacks-with-comments.tsx
- ✅ clusters-view.tsx
- ✅ rag-dashboard.tsx

### 4. 컴포넌트 정리 (6개)
**위치**: `dashboard/components/worldviews/_deprecated/`

- ✅ WorldviewCard.tsx
- ✅ WorldviewMap.tsx
- ✅ StrengthMeter.tsx
- ✅ ConsolidatedWorldviewMap.tsx
- ✅ MechanismGroupedWorldviewMap.tsx
- ✅ HierarchicalWorldviewMap.tsx

### 5. 필드 정리 (worldviews 테이블)
**Migration**: `supabase/migrations/401_remove_unused_worldview_fields.sql`

- ✅ strength_cognitive, strength_temporal, strength_social, strength_structural, strength_overall
- ✅ first_seen, last_seen, peak_date, trend
- ✅ worldview_strength_history 테이블 전체

---

## 현재 시스템 구조 (v2.0)

### DB 테이블 (4개만 사용)
1. **contents** - 원본 글
2. **layered_perceptions** - 3층 분석 (explicit/implicit/deep)
3. **worldviews** - 세계관 (actor + mechanisms + logic_pattern)
4. **perception_worldview_links** - 연결 테이블

### 엔진 (4개만 사용)
1. **layered_perception_extractor.py** - 3층 분석 생성
2. **reasoning_structure_extractor.py** - mechanisms, actor, logic_chain 추출
3. **worldview_evolution_engine.py** - 세계관 생성/진화 감지
4. **mechanism_matcher.py** - perception-worldview 연결

### 실행 스크립트 (2개)
1. **run_mechanism_matcher.py** - 매칭 실행
2. **run_worldview_evolution.py** - 진화 사이클 실행

### 페이지 (2개)
1. **/** - ActorCentricWorldviewMap
2. **/worldviews/[id]** - 상세 페이지

### 컴포넌트 (5개)
1. **ActorCentricWorldviewMap** - 메인 지도
2. **InterpretationComparison** - 해석 비교
3. **LogicChainVisualizer** - 논리 연쇄 시각화
4. **MechanismBadge** - 메커니즘 배지
5. **MechanismMatchingExplanation** - 매칭 설명

---

## 정리 효과

### 삭제/이동된 항목
- DB 테이블: 12개 삭제
- DB 필드: 10개 삭제
- 엔진: 5개 이동
- 페이지: 3개 이동
- 컴포넌트: 6개 이동

**총 36개 deprecated 항목 정리 완료**

### 시스템 상태
✅ 테스트 완료: API 정상 작동 (7개 세계관 로드)
✅ 개발 서버 정상 작동
✅ v2.0 아키텍처로 깔끔하게 정리됨

---

## 참고

- Deprecated 항목들은 `_deprecated` 폴더에 보관
- 필요시 복구 가능
- Migration 파일들은 보존 (rollback 가능)
