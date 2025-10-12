# 배포 준비 완료

**날짜**: 2025-01-11
**버전**: v2.0
**상태**: ✅ 배포 준비 완료

---

## 실행 순서

### Step 1: Schema Migration (5분)

```bash
# Supabase Dashboard → SQL Editor에서 실행:
# supabase/migrations/301_add_reasoning_structure_fields.sql
```

실행할 SQL:
```sql
ALTER TABLE layered_perceptions
  ADD COLUMN mechanisms TEXT[],
  ADD COLUMN skipped_steps TEXT[],
  ADD COLUMN actor JSONB,
  ADD COLUMN logic_chain TEXT[],
  ADD COLUMN consistency_pattern TEXT;

ALTER TABLE worldviews
  ADD COLUMN version INTEGER DEFAULT 1,
  ADD COLUMN last_updated TIMESTAMP DEFAULT NOW(),
  ADD COLUMN evolution_history JSONB DEFAULT '[]',
  ADD COLUMN archived BOOLEAN DEFAULT FALSE,
  ADD COLUMN archived_at TIMESTAMP;
```

**확인**:
```sql
SELECT column_name FROM information_schema.columns
WHERE table_name = 'layered_perceptions' AND column_name = 'mechanisms';
-- 결과가 나와야 함
```

---

### Step 2: 데이터 마이그레이션 (10분)

```bash
cd /Users/taehyeonkim/dev/minjoo/moniterdc
python scripts/migrate_to_new_system.py
```

**예상 출력**:
```
================================================================================
세계관 시스템 마이그레이션
================================================================================

[Step 1] Schema Migration
--------------------------------------------------------------------------------
⚠️  다음 SQL 파일을 Supabase에서 수동으로 실행하세요:
   supabase/migrations/301_add_reasoning_structure_fields.sql

실행 완료했습니까? (yes/no): yes

[Step 2] Populate Reasoning Structures
--------------------------------------------------------------------------------
분석 결과 로드 중...
✅ 501개 분석 결과 로드 완료

기존 perception 업데이트 중...
  진행: 50/501
  진행: 100/501
  ...
  진행: 500/501

✅ 501개 perception 업데이트 완료

[Step 3] Archive Old Worldviews
--------------------------------------------------------------------------------
기존 세계관: 9개
  - 독재와 사찰의 부활
  - 중국 산업 불신
  ...

이 세계관들을 아카이브할까요? (yes/no): yes
✅ 9개 세계관 아카이브 완료

[Step 4] Insert New Worldviews
--------------------------------------------------------------------------------
새 세계관 로드 중...
✅ 9개 새 세계관 로드 완료

새 세계관 생성 중...
  ✓ 민주당/좌파의 정보 파악 → 즉시 불법 사찰·장악으로 해석
  ✓ 정부·수사·사법 조치 → 표면 설명 부정 후 정치보복/탄압으로 귀결
  ...

✅ 9개 새 세계관 생성 완료

[Step 5] Re-match with Mechanism Matcher
--------------------------------------------------------------------------------

메커니즘 기반 매칭 시작
================================================================================

✅ 501개 perception 로드
✅ 9개 worldview 로드

기존 links 삭제 중...

매칭 시작 (threshold=0.4)...
  진행: 50/501 (87 links)
  진행: 100/501 (178 links)
  ...
  진행: 500/501 (912 links)

✅ 912개 링크 생성 완료
   평균: 1.82 links/perception

세계관 통계 업데이트 중...
  민주당/좌파의 정보 파악 → 즉시 불법 사찰·장악으로 해석: 156개
  중국·중국계 관찰 → 조직적 침투/범죄·여론조작으로 일반화: 143개
  ...

================================================================================
마이그레이션 완료!
================================================================================

요약:
  - Reasoning structures 업데이트: 501개
  - 기존 세계관 아카이브: 9개
  - 새 세계관 생성: 9개
  - Perception-Worldview 링크: 912개

커버리지 확인:
  민주당/좌파의 정보 파악 → 즉시 불법 사찰·장악으로 해석: 156개 (31.1%)
  중국·중국계 관찰 → 조직적 침투/범죄·여론조작으로 일반화: 143개 (28.5%)
  ...

  평균: 1.82 links/perception

✅ 시스템 전환 완료!
   Dashboard에서 새 세계관을 확인하세요.
```

**예상 커버리지**: 80-90% (평균 1.5-2 links/perception)

---

### Step 3: 검증 (5분)

**1. Supabase에서 확인**
```sql
-- 새 세계관 확인
SELECT title, total_perceptions
FROM worldviews
WHERE archived = FALSE
ORDER BY total_perceptions DESC;

-- 상위 5개 정도 나와야 함
```

**2. Dashboard 확인**
```bash
cd dashboard
npm run dev
# http://localhost:3002 접속
# 세계관 목록 확인
```

**3. 샘플 perception 확인**
```sql
-- Reasoning structure가 추가되었는지 확인
SELECT id, mechanisms, actor, consistency_pattern
FROM layered_perceptions
WHERE mechanisms IS NOT NULL
LIMIT 5;
```

---

### Step 4: 자동화 설정 (선택)

**Cron Job 설정** (주간 세계관 업데이트)
```bash
crontab -e

# 매주 일요일 00:00에 실행
0 0 * * 0 cd /Users/taehyeonkim/dev/minjoo/moniterdc && python scripts/run_worldview_evolution.py >> /tmp/worldview_evolution.log 2>&1
```

**또는 Python Scheduler**
```python
# 별도 스크립트 작성
from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', day_of_week='sun', hour=0)
def run_evolution():
    subprocess.run(['python', 'scripts/run_worldview_evolution.py'])

scheduler.start()
```

---

## 문제 발생 시

### 문제 1: Migration 실패

**증상**: "column already exists"

**해결**:
```sql
-- 기존 컬럼 확인
SELECT column_name FROM information_schema.columns
WHERE table_name = 'layered_perceptions';

-- 이미 있으면 migration 스킵
```

---

### 문제 2: 매칭률 낮음 (<50%)

**증상**: 링크 개수가 너무 적음

**해결**:
```python
# scripts/migrate_to_new_system.py 수정
# threshold 낮춤
links_created = await matcher.match_all_perceptions(threshold=0.3)  # 0.4 → 0.3
```

---

### 문제 3: 분석 결과 파일 없음

**증상**: "_reasoning_structures_analysis.json not found"

**해결**:
```bash
# 파일이 archive로 이동했을 수 있음
cp _archive/analysis_results_20250111/_reasoning_structures_analysis.json .
cp _archive/analysis_results_20250111/_consolidated_worldviews_gpt5.json .

# 다시 실행
python scripts/migrate_to_new_system.py
```

---

## 롤백 방법

만약 문제가 생기면:

**1. 세계관 롤백**
```sql
-- 새 세계관 아카이브
UPDATE worldviews SET archived = TRUE
WHERE version = 1 AND archived = FALSE;

-- 기존 세계관 복원
UPDATE worldviews SET archived = FALSE
WHERE version IS NULL OR version = 0;
```

**2. 데이터 롤백**
```sql
-- Reasoning structure 필드 NULL로
UPDATE layered_perceptions
SET mechanisms = NULL,
    skipped_steps = NULL,
    actor = NULL,
    logic_chain = NULL,
    consistency_pattern = NULL;
```

**3. 링크 삭제**
```sql
DELETE FROM perception_worldview_links;
```

---

## 배포 후 확인사항

**✅ 체크리스트**

- [ ] Schema migration 성공 (새 컬럼 존재)
- [ ] 501개 perception에 mechanisms 추가됨
- [ ] 9개 새 세계관 생성됨
- [ ] 링크 생성 (500+ 개)
- [ ] 커버리지 80% 이상
- [ ] Dashboard에서 세계관 확인 가능
- [ ] 새 content 처리 테스트 성공

**📊 예상 메트릭**

- **Perception with reasoning structure**: 501/501 (100%)
- **Worldviews (active)**: 9개
- **Links**: 500-1000개
- **Avg links/perception**: 1.5-2.0
- **Coverage**: 80-90%

---

## 다음 단계

**즉시 (배포 후)**
1. 모니터링 (첫 주)
2. 커버리지 확인
3. 매칭 품질 검토

**단기 (1-2주)**
1. Dashboard 업데이트 (메커니즘 시각화)
2. 첫 진화 사이클 실행
3. 피드백 수집

**중기 (1개월)**
1. 자동화 완성 (Cron)
2. 알림 시스템
3. 성능 최적화

---

## 연락처

문제 발생 시:
- [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) 참조
- [NEW_SYSTEM_ARCHITECTURE.md](NEW_SYSTEM_ARCHITECTURE.md) 트러블슈팅 섹션

---

**배포 준비 완료! 🚀**
