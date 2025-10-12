# 세계관 시스템 전면 개편 계획

## 현재 상태 분석

### 기존 시스템 (Old - 폐기 대상)
```
Content → LayeredPerceptionExtractor (3층 분석)
  → OptimalWorldviewConstructor (계층형 세계관)
  → Hybrid Matching (Vector 70% + Keyword 30%)
```

**문제점:**
1. ❌ 세계관이 **주제 기반** ("독재와 사찰" 등)
2. ❌ 세계관이 **고정됨** (한번 만들면 업데이트 없음)
3. ❌ 매칭이 임베딩 기반 (메커니즘 무시)
4. ❌ GPT-5 프롬프트가 구체적 메커니즘을 요구하지 않음

### 새 시스템 (New - 구현 대상)
```
Content → ReasoningStructureExtractor (5개 메커니즘 분석)
  → WorldviewEvolutionEngine (실시간 세계관 통합/분리/병합)
  → MechanismMatcher (메커니즘 기반 매칭)
```

**장점:**
1. ✅ 세계관이 **메커니즘 기반** (사고 구조)
2. ✅ 세계관이 **살아있음** (주기적 업데이트)
3. ✅ 매칭이 메커니즘 기반 (정확함)
4. ✅ 실제 사고 방식을 드러냄

---

## 전환 계획

### Phase 1: 새 엔진 구현 ✅ (완료)

**1.1. 추론 구조 분석 엔진**
- [x] `analyze_reasoning_structures.py` 구현
- [x] 5개 메커니즘 정의 (즉시_단정, 역사_투사, 필연적_인과, 네트워크_추론, 표면_부정)
- [x] 501개 전체 데이터 분석 완료
- [x] 결과: `_reasoning_structures_analysis.json`

**1.2. 세계관 통합 엔진**
- [x] `consolidate_worldviews_gpt5.py` 구현
- [x] GPT-5로 9개 핵심 세계관 추출
- [x] 결과: `_consolidated_worldviews_gpt5.json`

**1.3. 검증**
- [x] 목적 달성 확인 (FINAL_ANALYSIS_RESULTS.md)

---

### Phase 2: 프로덕션 코드 작성 (진행중)

**2.1. 새 엔진 클래스 작성**

파일 구조:
```
engines/
  analyzers/
    reasoning_structure_extractor.py     ← NEW (기존 layered_perception_extractor.py 대체)
    worldview_evolution_engine.py        ← NEW (기존 optimal_worldview_constructor.py 대체)
    mechanism_matcher.py                 ← NEW (기존 hybrid_perception_matcher.py 대체)
```

**2.2. 각 클래스 역할**

#### `ReasoningStructureExtractor`
- Content → Reasoning Structure 변환
- GPT-5로 5개 메커니즘 추출
- DB: `layered_perceptions` 테이블에 새 필드 추가
  - `mechanisms: List[str]`
  - `skipped_steps: List[str]`
  - `actor: Dict`
  - `logic_chain: List[str]`
  - `consistency_pattern: str`

#### `WorldviewEvolutionEngine`
- 주기적으로 실행 (예: 주 1회)
- 전체 perception의 reasoning_structure 분석
- GPT-5로 세계관 재통합
- 변화 감지:
  - 새 세계관 등장
  - 기존 세계관 변화
  - 세계관 사라짐
- DB: `worldviews` 테이블 업데이트
  - `frame` 필드에 새 구조 저장
  - `version` 필드 추가 (변화 추적)
  - `last_updated` 타임스탬프

#### `MechanismMatcher`
- Perception → Worldview 매칭
- 메커니즘 기반 매칭:
  - Actor 일치 (50%)
  - Mechanism 일치 (30%)
  - Logic pattern 일치 (20%)
- DB: `perception_worldview_links` 업데이트

---

### Phase 3: 데이터베이스 마이그레이션

**3.1. Schema 변경**

```sql
-- layered_perceptions 테이블에 필드 추가
ALTER TABLE layered_perceptions
ADD COLUMN mechanisms TEXT[] DEFAULT '{}',
ADD COLUMN skipped_steps TEXT[] DEFAULT '{}',
ADD COLUMN actor JSONB DEFAULT '{}',
ADD COLUMN logic_chain TEXT[] DEFAULT '{}',
ADD COLUMN consistency_pattern TEXT DEFAULT '';

-- worldviews 테이블에 필드 추가
ALTER TABLE worldviews
ADD COLUMN version INTEGER DEFAULT 1,
ADD COLUMN last_updated TIMESTAMP DEFAULT NOW(),
ADD COLUMN evolution_history JSONB DEFAULT '[]';

-- 기존 데이터는 유지 (호환성)
```

**3.2. 데이터 마이그레이션**

1. 기존 501개 perception에 reasoning_structure 추가
   - `_reasoning_structures_analysis.json` 데이터 사용

2. 기존 9개 worldview 삭제
   - 새 9개 worldview 삽입
   - `_consolidated_worldviews_gpt5.json` 데이터 사용

3. Links 재생성
   - 기존 links 삭제
   - 새 Mechanism 기반 매칭으로 재생성

---

### Phase 4: 자동화 파이프라인

**4.1. 실시간 Content 처리**

```python
# crawler가 새 content 수집 시
async def process_new_content(content):
    # 1. Reasoning structure 추출
    extractor = ReasoningStructureExtractor()
    perception = await extractor.extract(content)

    # 2. 기존 세계관에 매칭
    matcher = MechanismMatcher()
    await matcher.match_to_worldviews(perception)

    # 3. 매칭 실패 시 임시 보관
    if not matched:
        await store_unmatched(perception)
```

**4.2. 주기적 세계관 업데이트**

```python
# 매주 일요일 자정 실행
async def weekly_worldview_update():
    engine = WorldviewEvolutionEngine()

    # 1. 전체 perception 분석
    all_perceptions = await load_all_perceptions()

    # 2. 새 세계관 추출 (GPT-5)
    new_worldviews = await engine.consolidate(all_perceptions)

    # 3. 기존과 비교
    changes = await engine.compare_with_existing(new_worldviews)

    # 4. 변화 적용
    if changes.significant:
        await engine.update_worldviews(new_worldviews)
        await notify_admin(changes)  # 관리자에게 알림

    # 5. Unmatched perception 재매칭
    await rematch_unmatched_perceptions()
```

**4.3. Scheduler 설정**

```python
# engines/scheduler/worldview_scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# 매주 일요일 00:00
scheduler.add_job(
    weekly_worldview_update,
    'cron',
    day_of_week='sun',
    hour=0,
    minute=0
)
```

---

### Phase 5: Dashboard 업데이트

**5.1. 새 Worldview 구조 표시**

현재:
```typescript
// dashboard/app/worldviews/[id]/page.tsx
// 계층형 구조 + Narrative 표시
```

새로운 구조:
```typescript
interface NewWorldview {
  title: string
  actor: string
  mechanisms: string[]
  logic_pattern: {
    trigger: string
    skipped_verification: string[]
    conclusion: string
  }
  examples: string[]
  estimated_coverage: number
  version: number
  last_updated: string
}
```

**5.2. 세계관 진화 히스토리**

- 타임라인 형태로 세계관 변화 추적
- 어떤 세계관이 생겼고, 사라졌고, 변화했는지

**5.3. Mechanism 시각화**

- 5개 메커니즘 분포 차트
- 각 메커니즘별 대표 사례

---

### Phase 6: 문서화

**6.1. 시스템 아키텍처 문서**
- [x] SYSTEM_ARCHITECTURE.md (생성 예정)

**6.2. API 문서**
- [ ] engines/analyzers/README.md
- [ ] API 사용법 및 예시

**6.3. 운영 가이드**
- [ ] 세계관 업데이트 주기 설정
- [ ] 모니터링 방법
- [ ] 트러블슈팅

---

### Phase 7: 정리

**7.1. 폐기 파일 아카이브**

이동할 파일:
```
_deprecated/
  layered_perception_extractor.py (기존)
  optimal_worldview_constructor.py (기존)
  hybrid_perception_matcher.py (기존)
  worldview_updater.py (기존)
```

**7.2. 임시 분석 파일 정리**

삭제할 파일:
```
analyze_reasoning_structures.py → engines/analyzers/reasoning_structure_extractor.py로 통합
consolidate_worldviews_gpt5.py → engines/analyzers/worldview_evolution_engine.py로 통합
construct_worldviews_from_reasoning.py (삭제)
define_worldview_structure.py (삭제)
extract_*.py (모두 삭제)
test_*.py (필요한 것만 tests/ 폴더로 이동)
simulation_*.py (삭제)
_*.json (결과 파일들 - _archive/로 이동)
```

**7.3. README 업데이트**
- [ ] 새 시스템 설명
- [ ] 사용법 업데이트

---

## 실행 순서

### 즉시 실행 (오늘)
1. ✅ Phase 1 완료 확인
2. ⏳ Phase 2 시작: 새 엔진 클래스 작성
3. ⏳ Phase 3: DB 마이그레이션 스크립트 작성

### 내일
4. Phase 2 완료: 모든 클래스 구현
5. Phase 3 실행: DB 마이그레이션 수행
6. Phase 4: 자동화 파이프라인 구현

### 모레
7. Phase 5: Dashboard 업데이트
8. Phase 6: 문서화
9. Phase 7: 정리 및 배포

---

## 위험 요소 및 대응

### 위험 1: GPT-5 API 비용
- **대응**: 주기적 업데이트 빈도 조정 (주 1회 → 월 2회)
- **대응**: 샘플링 사용 (전체가 아닌 최근 200개만)

### 위험 2: 세계관 급변
- **대응**: 변화 감지 시 관리자 승인 필요
- **대응**: 버전 관리로 롤백 가능

### 위험 3: 기존 데이터 손실
- **대응**: 마이그레이션 전 백업
- **대응**: 기존 컬럼 유지 (새 컬럼 추가만)

---

## 성공 기준

✅ **기술적 성공**
- [ ] 새 content가 들어오면 자동으로 reasoning structure 추출
- [ ] 매주 세계관이 자동 업데이트
- [ ] Dashboard에서 세계관 진화 확인 가능

✅ **목적 달성**
- [ ] 세계관이 실제 사고 메커니즘을 드러냄
- [ ] 시간에 따른 담론 변화 추적 가능
- [ ] 새로운 패턴 발견 시 자동 반영
