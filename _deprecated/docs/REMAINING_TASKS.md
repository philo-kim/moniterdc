# 남은 작업 정리

## ✅ 완료된 핵심 작업

### 1. 데이터 파이프라인 구축 ✅
- DC Gallery 글 수집: 297개
- 3-Layer 분석 (LayeredPerceptionExtractor): 297개 완료
- 믿음 정규화 (BeliefNormalizer): 889→552개

### 2. 세계관 구성 시스템 ✅
- **시뮬레이션 기반 최적 설계**: 3가지 방법론 테스트 후 선택
- **OptimalWorldviewConstructor 구현**:
  - 계층형 구조 (3 대분류 × 6 세부)
  - 예시 중심 Narrative (DC vs 일반 해석 대비)
  - 계층형 Metadata (core + interpretation_frame + emotions)
  - Hybrid 매칭 (Vector 70% + Keyword 30%)

### 3. 지속 업데이트 전략 ✅
- **4가지 시나리오 시뮬레이션**: A/B/C/D 테스트
- **하이브리드 전략 설계**: 점진적 병합 + 임계값 기반
- **WorldviewUpdater 구현**:
  - daily_update(): 일상 운영
  - weekly_update(): 주간 예시 추가
  - check_and_rebuild_if_needed(): 월간 재구성
  - detect_and_create_new_worldviews(): 새 세계관 발견

### 4. 문서화 ✅
- SYSTEM_ARCHITECTURE_COMPLETE.md
- WORLDVIEW_CONSTRUCTION_COMPLETE.md
- WORLDVIEW_UPDATE_STRATEGY.md

---

## ⚠️ 남은 작업

### 우선순위 1: 데이터베이스 완성

#### 1-1. perception_worldview_links 테이블 생성 ❌
**현재 상태**:
- 테이블이 없어서 세계관-perception 연결 불가
- 26개 링크가 생성되었지만 저장 실패

**필요한 작업**:
```sql
CREATE TABLE perception_worldview_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    perception_id UUID REFERENCES layered_perceptions(id) ON DELETE CASCADE,
    worldview_id UUID REFERENCES worldviews(id) ON DELETE CASCADE,
    relevance_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**실행 방법**:
- Supabase Dashboard → SQL Editor에서 실행
- 또는 `supabase/migrations/203_create_perception_worldview_links.sql` 적용

**중요도**: ⭐⭐⭐ (없으면 업데이트 시스템 작동 불가)

#### 1-2. 전체 perception-worldview 매칭 완료 ❌
**현재 상태**:
- 297개 perception 중 26개만 매칭됨 (8.8%)

**필요한 작업**:
```python
# OptimalWorldviewConstructor 재실행 (테이블 생성 후)
python -c "
import asyncio
from engines.analyzers.optimal_worldview_constructor import OptimalWorldviewConstructor

async def main():
    constructor = OptimalWorldviewConstructor()
    await constructor._match_perceptions_to_worldviews(
        all_perceptions,
        all_worldviews
    )

asyncio.run(main())
"
```

**중요도**: ⭐⭐ (세계관별 perception 개수 통계에 필요)

---

### 우선순위 2: 대시보드 통합

#### 2-1. 세계관 브라우징 UI ❌
**목적**: 여당 지지자가 세계관을 탐색하고 이해

**필요한 컴포넌트**:

```tsx
// dashboard/app/worldviews/page.tsx

1. 계층형 네비게이션
   - 3개 대분류 표시
   - 클릭 시 세부 세계관 표시

2. 세계관 상세 페이지
   - Narrative (예시 중심)
     • DC 해석 vs 일반 해석 대비
     • 논리 체인
     • 역사적 맥락

   - Metadata 시각화
     • Core (주체 = 속성)
     • Slippery Slope 다이어그램
     • Emotional Drivers

3. 연결된 글 목록
   - 이 세계관과 매칭된 perception 목록
   - 원본 content 링크
```

**참고 파일**:
- `dashboard/app/worldviews/` (새로 생성 필요)
- 기존 `dashboard/app/page.tsx` 구조 참고

**중요도**: ⭐⭐⭐ (핵심 사용자 경험)

#### 2-2. 검색 기능 ❌
**목적**: 특정 주제로 세계관 찾기

**기능**:
```tsx
// 검색창
<input
  placeholder="예: 민주당, 독재, 사찰"
  onChange={handleSearch}
/>

// 검색 로직
- worldviews.metadata.key_concepts 검색
- worldviews.narrative.summary 검색
- 관련도 순 정렬
```

**중요도**: ⭐⭐

#### 2-3. API 엔드포인트 ❌
**필요한 API**:

```typescript
// dashboard/app/api/worldviews/route.ts
GET /api/worldviews
  → 모든 세계관 (계층형 구조)

GET /api/worldviews/[id]
  → 특정 세계관 상세

GET /api/worldviews/[id]/perceptions
  → 해당 세계관과 연결된 perception 목록

GET /api/worldviews/search?q=민주당
  → 검색 결과
```

**중요도**: ⭐⭐⭐

---

### 우선순위 3: 자동화

#### 3-1. GitHub Actions 워크플로우 ❌
**목적**: 매일 자동으로 새 글 수집 및 분석

**필요한 파일**:
```yaml
# .github/workflows/daily_update.yml

name: Daily Worldview Update

on:
  schedule:
    - cron: '0 2 * * *'  # 매일 오전 2시 (KST 11시)
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run daily update
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python -c "
          import asyncio
          from engines.analyzers.worldview_updater import WorldviewUpdater

          async def main():
              updater = WorldviewUpdater()
              await updater.daily_update()

          asyncio.run(main())
          "
```

**중요도**: ⭐⭐

#### 3-2. 주간/월간 워크플로우 ❌
```yaml
# .github/workflows/weekly_update.yml (주 1회)
# .github/workflows/monthly_check.yml (월 1회)
```

**중요도**: ⭐

---

### 우선순위 4: 반박 논리 생성

#### 4-1. Deconstruction Engine ❌
**목적**: 각 세계관에 대한 반박 논리 생성

**필요한 작업**:
```python
# engines/analyzers/deconstruction_generator.py

class DeconstructionGenerator:
    async def generate_deconstruction(worldview):
        """
        세계관의 논리적 허점 분석 및 반박 생성

        Output:
        {
          "logical_flaws": [
            "슬리퍼리 슬로프 오류",
            "허수아비 공격"
          ],
          "counter_narrative": "...",
          "evidence": ["팩트체크 링크"],
          "suggested_response": "..."
        }
        """
```

**중요도**: ⭐ (추후 단계)

---

## 📋 작업 우선순위 정리

### 즉시 필요 (시스템 작동 위해)
1. ⭐⭐⭐ **perception_worldview_links 테이블 생성**
2. ⭐⭐⭐ **대시보드 API 엔드포인트**
3. ⭐⭐⭐ **세계관 브라우징 UI**

### 중요 (핵심 기능)
4. ⭐⭐ **전체 perception 매칭 완료**
5. ⭐⭐ **검색 기능**
6. ⭐⭐ **GitHub Actions (daily)**

### 향후 개선
7. ⭐ **주간/월간 자동화**
8. ⭐ **반박 논리 생성**
9. ⭐ **모니터링 대시보드**

---

## 🎯 다음 작업 추천 순서

### Step 1: 테이블 생성 (5분)
```sql
-- Supabase Dashboard에서 실행
CREATE TABLE perception_worldview_links (...);
```

### Step 2: 전체 매칭 실행 (10분)
```python
python -c "
from engines.analyzers.optimal_worldview_constructor import OptimalWorldviewConstructor
# 매칭 실행
"
```

### Step 3: 대시보드 API 구현 (1시간)
```typescript
// dashboard/app/api/worldviews/route.ts
// GET /api/worldviews
```

### Step 4: 세계관 브라우징 UI (2시간)
```tsx
// dashboard/app/worldviews/page.tsx
// 계층형 네비게이션 + 상세 페이지
```

### Step 5: GitHub Actions 설정 (30분)
```yaml
# .github/workflows/daily_update.yml
```

---

## 📊 예상 소요 시간

| 작업 | 소요 시간 | 중요도 |
|------|----------|--------|
| 테이블 생성 | 5분 | ⭐⭐⭐ |
| 전체 매칭 | 10분 | ⭐⭐ |
| 대시보드 API | 1시간 | ⭐⭐⭐ |
| 세계관 UI | 2시간 | ⭐⭐⭐ |
| 검색 기능 | 1시간 | ⭐⭐ |
| GitHub Actions | 30분 | ⭐⭐ |
| **총계** | **~5시간** | |

---

## ✅ 완료 기준

### 최소 기능 (MVP)
- ✅ 세계관 6개 생성됨
- ❌ 대시보드에서 세계관 탐색 가능
- ❌ perception-worldview 연결 완료
- ❌ 매일 자동 업데이트

### 완전 기능
- ❌ 검색 기능
- ❌ 주간/월간 자동 업데이트
- ❌ 반박 논리 생성
- ❌ 모니터링 대시보드

---

**현재 진행률**: 약 70% 완료 (핵심 엔진 완성, UI 작업 남음)
