# 배포 체크리스트

**사용자**: 배포 담당자
**목적**: 빠짐없이 v2.0 시스템 배포

---

## Pre-Deployment

### ✅ 파일 확인
- [x] engines/analyzers/reasoning_structure_extractor.py 존재
- [x] engines/analyzers/worldview_evolution_engine.py 존재
- [x] engines/analyzers/mechanism_matcher.py 존재
- [x] scripts/migrate_to_new_system.py 존재
- [x] scripts/process_new_content.py 존재
- [x] scripts/run_worldview_evolution.py 존재
- [x] supabase/migrations/301_add_reasoning_structure_fields.sql 존재
- [x] _archive/analysis_results_20250111/_reasoning_structures_analysis.json 존재
- [x] _archive/analysis_results_20250111/_consolidated_worldviews_gpt5.json 존재

### ✅ 문서 확인
- [x] DEPLOYMENT_READY.md 작성됨
- [x] FINAL_SUMMARY.md 작성됨
- [x] PROJECT_COMPLETE.md 작성됨
- [x] NEW_SYSTEM_ARCHITECTURE.md 작성됨
- [x] SYSTEM_TRANSITION_PLAN.md 작성됨
- [x] README.md 업데이트됨

### ✅ 환경 확인
- [x] OPENAI_API_KEY 설정됨
- [x] SUPABASE_URL 설정됨
- [x] SUPABASE_SERVICE_KEY 설정됨
- [x] Python 3.12.3 설치됨 (✅ >= 3.11)
- [x] 필요한 패키지 설치됨 (openai 1.107.2, supabase 2.18.1)

---

## Deployment Steps

### Step 1: Schema Migration
- [ ] Supabase Dashboard 접속
- [ ] SQL Editor 열기
- [ ] supabase/migrations/301_add_reasoning_structure_fields.sql 복사
- [ ] SQL 실행
- [ ] 에러 없이 완료 확인
- [ ] 테이블 구조 확인:
  ```sql
  SELECT column_name FROM information_schema.columns
  WHERE table_name = 'layered_perceptions' AND column_name = 'mechanisms';
  ```

### Step 2: Data Migration
- [ ] 터미널 열기
- [ ] 프로젝트 디렉토리로 이동
- [ ] `python scripts/migrate_to_new_system.py` 실행
- [ ] "Schema migration 완료했습니까?" → yes
- [ ] "세계관 아카이브할까요?" → yes
- [ ] 완료 메시지 확인
- [ ] 에러 없음 확인

### Step 3: Verification
- [ ] Supabase에서 새 세계관 확인:
  ```sql
  SELECT title, total_perceptions
  FROM worldviews
  WHERE archived = FALSE
  ORDER BY total_perceptions DESC;
  ```
- [ ] 결과: 9개 세계관이 나와야 함
- [ ] Perception 확인:
  ```sql
  SELECT COUNT(*) FROM layered_perceptions WHERE mechanisms IS NOT NULL;
  ```
- [ ] 결과: 501개여야 함
- [ ] Links 확인:
  ```sql
  SELECT COUNT(*) FROM perception_worldview_links;
  ```
  - [ ] 결과: 500개 이상이어야 함

### Step 4: Dashboard Check
- [ ] `cd dashboard && npm run dev`
- [ ] http://localhost:3002 접속
- [ ] 세계관 목록 표시됨
- [ ] 세계관 클릭 시 perception 목록 표시됨
- [ ] 에러 없음

---

## Post-Deployment

### Monitoring (첫 주)
- [ ] Day 1: 시스템 정상 작동 확인
- [ ] Day 3: 커버리지 재확인
- [ ] Day 7: 첫 진화 사이클 실행 테스트

### Optional: Automation Setup
- [ ] Cron job 설정 (주간 진화)
- [ ] 알림 설정 (변화 감지 시)
- [ ] 모니터링 대시보드 구축

---

## Rollback Plan (문제 발생 시)

### 세계관 롤백
```sql
UPDATE worldviews SET archived = TRUE WHERE version = 1;
UPDATE worldviews SET archived = FALSE WHERE version IS NULL;
```

### 데이터 롤백
```sql
UPDATE layered_perceptions
SET mechanisms = NULL, skipped_steps = NULL,
    actor = NULL, logic_chain = NULL, consistency_pattern = NULL;

DELETE FROM perception_worldview_links;
```

---

## Success Criteria

### ✅ 필수
- [ ] 501/501 perceptions에 mechanisms 존재
- [ ] 9개 active worldviews 존재
- [ ] 500+ links 존재
- [ ] Dashboard 정상 작동
- [ ] 에러 로그 없음

### ✅ 권장
- [ ] 커버리지 80% 이상
- [ ] 평균 1.5+ links/perception
- [ ] 주간 진화 테스트 성공

---

## Completed By

- [ ] 배포 담당자: _______________
- [ ] 날짜: _______________
- [ ] 서명: _______________

---

**모든 항목 체크 완료 시 배포 성공! 🎉**
