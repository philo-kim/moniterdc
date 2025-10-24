# 동적 패턴 관리 시스템 구현 완료

**날짜**: 2025-10-24
**상태**: ✅ 기본 구현 완료 (테스트 대기)

---

## 📊 구현 개요

### 목표
표면/암묵/심층이 각각 다른 속도로 변화하는 **"살아있는 세계관 생태계"** 구현

### 핵심 원리
- **표면층**: 구체적 사건 → 매일 들어오고 나감 (7일 생명주기)
- **암묵층**: 해석 틀/전제 → 주간 변화 (30일 생명주기)
- **심층**: 근본 믿음 → 거의 불변 (180일 생명주기)

---

## 🏗 구현된 컴포넌트

### 1. 데이터베이스 스키마

**파일**: `supabase/migrations/501_create_worldview_patterns.sql`

```sql
CREATE TABLE worldview_patterns (
  id UUID PRIMARY KEY,
  worldview_id UUID REFERENCES worldviews(id),
  layer TEXT,  -- 'surface' | 'implicit' | 'deep'
  text TEXT,

  -- 동적 상태
  strength FLOAT (0-10),
  status TEXT,  -- 'active' | 'fading' | 'dead'

  -- 임베딩 (유사도 검색)
  embedding vector(1536),

  -- 생명주기
  first_seen TIMESTAMP,
  last_seen TIMESTAMP,
  appearance_count INT
);
```

**특징**:
- pgvector 사용한 임베딩 유사도 검색
- 층별 인덱스 최적화
- 자동 updated_at 트리거

### 2. PatternManager 엔진

**파일**: `engines/analyzers/pattern_manager.py`

**주요 메서드**:
```python
class PatternManager:
    # 새 perception 통합
    def integrate_perception(worldview_id, perception)

    # 유사 패턴 찾기 (층별 threshold)
    def find_similar_pattern(worldview_id, layer, text)

    # 패턴 강화
    def reinforce_pattern(pattern_id)

    # 새 패턴 생성
    def create_pattern(worldview_id, layer, text)

    # 패턴 약화 (시간 경과)
    def decay_patterns(worldview_id=None)

    # 죽은 패턴 제거
    def cleanup_dead_patterns(worldview_id=None)
```

**층별 설정**:
```python
# 유사도 임계값
SIMILARITY_THRESHOLDS = {
    'surface': 0.85,   # 엄격 (구체적)
    'implicit': 0.70,  # 중간 (패턴)
    'deep': 0.60       # 관대 (근본)
}

# Decay rate (per day)
DECAY_RATES = {
    'surface': 0.7,    # 30%/일
    'implicit': 0.9,   # 10%/주
    'deep': 0.95       # 5%/월
}

# 만료 기간
EXPIRATION_DAYS = {
    'surface': 7,
    'implicit': 30,
    'deep': 180
}
```

### 3. SQL 함수

**파일**: `supabase/migrations/502_create_pattern_similarity_function.sql`

```sql
CREATE FUNCTION find_similar_patterns(
    target_worldview_id UUID,
    target_layer TEXT,
    target_embedding vector(1536),
    max_distance FLOAT,
    limit_count INT
)
RETURNS TABLE (...)
```

**기능**: Vector 임베딩 기반 코사인 유사도 검색

### 4. Daily Cron Job

**파일**: `scripts/daily_pattern_update.py`

**실행 순서**:
1. 어제 새 contents 가져오기
2. 3층 분석 (LayeredPerceptionExtractor)
3. 구조 추출 (ReasoningStructureExtractor)
4. 세계관 매칭 (MechanismMatcher)
5. 패턴 통합 (PatternManager.integrate_perception)
6. 패턴 decay (PatternManager.decay_patterns)
7. 죽은 패턴 정리 (PatternManager.cleanup_dead_patterns)

**설치 방법**:
```bash
# Crontab 등록
crontab -e

# 매일 자정 실행
0 0 * * * cd /path/to/moniterdc && python3 scripts/daily_pattern_update.py >> logs/daily_update.log 2>&1
```

---

## 🔄 시스템 플로우

### 일일 흐름

```
새 글 수집 (매일)
    ↓
LayeredPerceptionExtractor
    → explicit_claims[], implicit_assumptions[], deep_beliefs[]
    ↓
ReasoningStructureExtractor
    → mechanisms[], actor, logic_chain[]
    ↓
MechanismMatcher
    → perception_worldview_links 생성
    ↓
PatternManager.integrate_perception() ✨ NEW
    → 각 층별로:
       - 기존 패턴과 유사도 계산
       - 매칭되면 → 강화 (strength +0.5)
       - 안되면 → 새 패턴 추가
    ↓
PatternManager.decay_patterns() ✨ NEW
    → 시간 경과한 패턴들 약화
    ↓
PatternManager.cleanup_dead_patterns() ✨ NEW
    → strength < 0.1 패턴 제거
```

### 패턴 생명주기

```
Day 1: 새 사건 "OO 사건" 등장
    → create_pattern(strength=1.0, status='active')

Day 2-5: 계속 등장
    → reinforce_pattern(strength 1.0 → 1.5 → 2.0 → 2.5 → 3.0)

Day 6: 언급 없음
    → decay_patterns(strength 3.0 → 2.1)

Day 7: 언급 없음
    → decay_patterns(strength 2.1 → 1.47)

Day 8: 언급 없음, 7일 경과
    → status='dead', cleanup_dead_patterns() → 제거됨
```

---

## 📈 예상 결과

### 세계관 상세 페이지

```
세계관: "중국/좌파가 댓글부대로 여론을 조작한다"

┌─ 심층 (90일, 거의 불변) ───────────┐
│ 💎 핵심 믿음                        │
│ • "외세가 한국을 조종한다"          │
│   강도 ██████████ 10.0 (122개 글)  │
│   → 새 글의 95%가 이 믿음과 매칭    │
└─────────────────────────────────────┘

┌─ 암묵층 (30일, 천천히 변화) ───────┐
│ 🔸 주요 전제                        │
│ • "조직적 댓글부대가 존재한다"      │
│   강도 ███████░░░ 7.2 (112개 글)   │
│   → 새 글의 70%가 이 전제 포함      │
│                                     │
│ • "정부가 묵인한다" (강화 중 ↗)     │
│   강도 ████░░░░░░ 4.1 (67개 글)    │
└─────────────────────────────────────┘

┌─ 표면층 (7일, 빠르게 변화) ────────┐
│ 🔥 급상승                           │
│ • "OO 사건 댓글 조작"               │
│   강도 ███░░░░░░░ 3.5 (45개 글)    │
│   5일간 계속 등장                   │
│                                     │
│ ✨ 신규 사건                        │
│ • "XX IP 추적 결과"                 │
│   강도 █░░░░░░░░░ 1.2 (12개 글)    │
│   2일 전 등장                       │
│                                     │
│ 📉 소멸 예정                        │
│ • "△△ 계정 정지"                   │
│   강도 ░░░░░░░░░░ 0.4 (5개 글)     │
│   6일간 안 나옴 (내일 제거 예정)    │
└─────────────────────────────────────┘
```

---

## ✅ 다음 단계

### 1. 데이터베이스 마이그레이션 적용

```bash
# Supabase 마이그레이션 적용
supabase db push

# 또는 수동으로
psql < supabase/migrations/501_create_worldview_patterns.sql
psql < supabase/migrations/502_create_pattern_similarity_function.sql
```

### 2. pgvector 확장 설치 확인

```sql
-- Supabase SQL Editor에서 실행
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. 기존 데이터 백필 (선택사항)

기존 455개 perceptions를 패턴 풀에 추가:

```bash
python3 scripts/backfill_existing_patterns.py
```

**주의**: 이 스크립트는 아직 작성 안됨. 필요시 작성.

### 4. Daily Cron Job 등록

```bash
# Crontab 등록
crontab -e

# 추가
0 0 * * * cd /Users/taehyeonkim/dev/minjoo/moniterdc && python3 scripts/daily_pattern_update.py >> logs/daily_update.log 2>&1
```

### 5. 테스트

```bash
# 샘플 데이터로 테스트
python3 scripts/test_pattern_system.py
```

**주의**: 테스트 스크립트는 아직 작성 안됨.

### 6. 대시보드 API 업데이트

`/api/worldviews/[id]`에서 worldview_patterns 조회 추가:

```typescript
// dashboard/app/api/worldviews/[id]/route.ts

// 패턴 가져오기
const { data: patterns } = await supabase
  .table('worldview_patterns')
  .select('*')
  .eq('worldview_id', id)
  .in('status', ['active', 'fading'])
  .order('strength', { desc: true });

// layer별로 그룹화
const surface_patterns = patterns.filter(p => p.layer === 'surface');
const implicit_patterns = patterns.filter(p => p.layer === 'implicit');
const deep_patterns = patterns.filter(p => p.layer === 'deep');
```

---

## 🔍 검증 방법

### 1. 패턴이 생성되는가?

```sql
SELECT layer, COUNT(*), AVG(strength)
FROM worldview_patterns
WHERE status = 'active'
GROUP BY layer;
```

예상 결과:
```
layer     | count | avg
----------+-------+-----
surface   | ~200  | 2.5
implicit  | ~50   | 5.0
deep      | ~10   | 8.5
```

### 2. Decay가 작동하는가?

```sql
-- 3일 안 나온 표면층 패턴들
SELECT text, strength, last_seen
FROM worldview_patterns
WHERE layer = 'surface'
  AND status = 'active'
  AND last_seen < NOW() - INTERVAL '3 days'
ORDER BY last_seen;
```

### 3. 매칭률이 적절한가?

Daily job 로그 확인:
```
Pattern Statistics:
   surface : 15 matched (20%), 60 new
   implicit: 45 matched (65%), 25 new
   deep    : 18 matched (95%), 1 new
```

- 표면: 20-30% 매칭 (나머지는 새 사건)
- 암묵: 60-70% 매칭 (전제는 반복됨)
- 심층: 90%+ 매칭 (믿음은 거의 같음)

---

## 📚 관련 파일

### 새로 생성된 파일
- `supabase/migrations/501_create_worldview_patterns.sql`
- `supabase/migrations/502_create_pattern_similarity_function.sql`
- `engines/analyzers/pattern_manager.py`
- `scripts/daily_pattern_update.py`
- `docs/dynamic_pattern_system_design.md`
- `DYNAMIC_PATTERN_IMPLEMENTATION.md` (this file)

### 수정된 파일
- `engines/analyzers/__init__.py` (PatternManager 추가)

### 수정 필요 (향후)
- `dashboard/app/api/worldviews/[id]/route.ts` (패턴 조회 추가)
- `dashboard/app/worldviews/[id]/page.tsx` (패턴 표시 추가)

---

## 💡 핵심 인사이트

### 왜 이 방식이 본질적인가?

1. **프롬프트가 본질을 반영**
   - 표면층: "구체적 사건만" → 자연히 개별성 높음
   - 암묵층: "해석 틀" → 자연히 패턴화됨
   - 심층: "근본 믿음" → 자연히 공통적임

2. **유사도 기준이 본질을 반영**
   - 표면: 0.85 엄격 → 날짜/장소 다르면 다른 사건
   - 암묵: 0.70 중간 → 표현 달라도 같은 전제
   - 심층: 0.60 관대 → 본질만 같으면 OK

3. **생명주기가 본질을 반영**
   - 표면: 7일 → 사건은 빨리 지나감
   - 암묵: 30일 → 전제는 천천히 변화
   - 심층: 180일 → 믿음은 쉽게 안 변함

**결과**: 목표치를 하드코딩하지 않아도, 시스템이 본질적으로 그렇게 동작함!

---

**Status**: ✅ 구현 완료, 테스트 및 배포 대기
