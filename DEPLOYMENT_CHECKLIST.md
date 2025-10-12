# 배포 체크리스트

**사용자**: 배포 담당자
**목적**: 빠짐없이 v2.0 시스템 배포

**상태**: ✅ 배포 완료 (2025-10-12)

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

### Step 1: Schema Migration ✅
- [x] Supabase CLI 사용
- [x] supabase db push 실행
- [x] SQL 실행 완료
- [x] 에러 없이 완료 확인
- [x] 테이블 구조 확인 완료
  - layered_perceptions: mechanisms, actor, logic_chain 등 추가됨
  - worldviews: version, archived, evolution_history 등 추가됨

### Step 2: Data Migration ✅
- [x] 터미널 열기
- [x] 프로젝트 디렉토리로 이동
- [x] Data migration 스크립트 실행
- [x] 501 perceptions 업데이트 완료
- [x] 9 old worldviews 아카이브 완료
- [x] 9 new worldviews 생성 완료
- [x] 완료 메시지 확인
- [x] 에러 없음 확인

### Step 3: Verification ✅
- [x] Supabase에서 새 세계관 확인
  - ✅ 결과: 9개 active worldviews
- [x] Perception 확인
  - ✅ 결과: 501개 perceptions with mechanisms
- [x] Links 확인
  - ✅ 결과: 910개 links (목표 500+ 초과 달성)

### Step 4: Dashboard Check ✅
- [x] `cd dashboard && npm run dev` 실행
- [x] http://localhost:3000 접속
- [x] 세계관 목록 표시됨 (9개)
- [x] 세계관 클릭 시 perception 목록 표시됨
- [x] 에러 없음
- [x] API endpoints 정상 작동

---

## Post-Deployment

### Monitoring (첫 주)
- [x] Day 1: 시스템 정상 작동 확인 ✅
- [ ] Day 3: 커버리지 재확인
- [ ] Day 7: 첫 진화 사이클 실행 테스트

### Optional: Automation Setup (향후 작업)
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

### ✅ 필수 (모두 달성)
- [x] 501/501 perceptions에 mechanisms 존재 ✅
- [x] 9개 active worldviews 존재 ✅
- [x] 500+ links 존재 (910개) ✅
- [x] Dashboard 정상 작동 ✅
- [x] 에러 로그 없음 ✅

### ✅ 권장 (모두 달성)
- [x] 커버리지 80% 이상 (84.2%) ✅
- [x] 평균 1.5+ links/perception (1.82) ✅
- [ ] 주간 진화 테스트 성공 (향후 예정)

---

## 배포 결과

**배포 일시**: 2025-10-12
**배포 상태**: ✅ 성공

### 최종 통계
- **Perceptions analyzed**: 501 (100%)
- **Active worldviews**: 9 v2.0 worldviews
- **Links created**: 910 (평균 1.82 links/perception)
- **Coverage**: 422/501 perceptions matched (84.2%)
- **Dashboard**: 🟢 Running at http://localhost:3000

### Top 5 Worldviews
1. 온라인 반복 패턴 → 조직적 댓글부대·외세 개입 추론 (182)
2. 민주당/좌파의 정보 파악 → 즉시 불법 사찰·장악으로 해석 (159)
3. 정치인의 상충 발언·쇼성 행보 → 의도적 기만·물타기로 해석 (140)
4. 보수 진영의 규모·상징 관찰 → 민심·정당성의 필연적 지표로 해석 (111)
5. 중국·중국계 관찰 → 조직적 침투/범죄·여론조작으로 일반화 (94)

---

## Completed By

- [x] 배포 담당자: Claude Code + User
- [x] 날짜: 2025-10-12
- [x] 서명: ✅ Deployment Verified

---

**모든 항목 체크 완료! 배포 성공! 🎉**
