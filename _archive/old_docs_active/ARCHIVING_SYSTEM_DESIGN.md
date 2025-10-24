# 3개월 아카이빙 시스템 설계

## 목표

- **Active 데이터**: 최근 3개월 (90일) - 세계관 분석 대상
- **Archived 데이터**: 3개월 이상 - 보관만 (분석 제외)
- **DB 크기**: ~1,800개 contents 유지
- **비용 절감**: 오래된 데이터 재분석 방지

---

## 아키텍처

### 데이터 라이프사이클

```
[수집] → [Active 90일] → [Archive] → [선택적 삭제]
   ↓           ↓              ↓
 신규글     분석대상        보관만
```

### 테이블 구조

```sql
contents {
    id
    title
    body
    source_url
    published_at     ← 기준 날짜
    created_at
    archived         ← 새 필드 (boolean)
    archived_at      ← 새 필드 (timestamp)
}

layered_perceptions {
    id
    content_id
    ...
    archived         ← 새 필드 (boolean, contents와 동기화)
}

worldview_patterns {
    ...
    (아카이브 영향 없음 - 패턴은 계속 유지)
}
```

---

## 아카이빙 규칙

### 1. 아카이브 조건

```sql
published_at < NOW() - INTERVAL '90 days'
AND archived = false
```

### 2. 아카이브 동작

**Contents**:
- `archived = true`
- `archived_at = NOW()`
- 데이터는 삭제 안 함 (복구 가능)

**Layered Perceptions**:
- `archived = true` (contents와 동기화)

**Worldview Patterns**:
- 영향 없음 (패턴은 계속 유지)
- 이미 추출된 패턴은 계속 살아있음

### 3. 분석 시 제외

모든 분석 쿼리에서:
```sql
WHERE archived = false
```

---

## 구현 계획

### Step 1: Database Migration

```sql
-- 507_add_archiving_fields.sql

-- Contents 테이블에 아카이빙 필드 추가
ALTER TABLE contents
ADD COLUMN archived BOOLEAN DEFAULT false,
ADD COLUMN archived_at TIMESTAMP WITH TIME ZONE;

-- Layered perceptions에도 추가
ALTER TABLE layered_perceptions
ADD COLUMN archived BOOLEAN DEFAULT false;

-- 인덱스 추가 (성능)
CREATE INDEX idx_contents_archived ON contents(archived, published_at);
CREATE INDEX idx_perceptions_archived ON layered_perceptions(archived);

-- View: Active contents만
CREATE OR REPLACE VIEW active_contents AS
SELECT * FROM contents
WHERE archived = false;

-- View: Active perceptions만
CREATE OR REPLACE VIEW active_perceptions AS
SELECT * FROM layered_perceptions
WHERE archived = false;
```

### Step 2: Archiving Engine

```python
# engines/archiving/content_archiver.py

class ContentArchiver:
    """
    3개월 아카이빙 시스템

    - 90일 이상 contents 자동 아카이브
    - Layered perceptions 동기화
    - 복구 기능
    """

    def archive_old_contents(self, dry_run=False):
        """90일 이상 contents 아카이브"""

    def restore_content(self, content_id):
        """아카이브된 content 복구"""

    def get_archive_stats(self):
        """아카이브 통계"""
```

### Step 3: Daily Cron Job

```bash
# scripts/daily_archiving.py

# 매일 새벽 3시 실행
# - 90일 이상 contents 아카이브
# - 통계 로깅
```

### Step 4: Code Updates

모든 분석 코드에서 archived 필터링:

```python
# Before
contents = supabase.table('contents').select('*').execute()

# After
contents = supabase.table('contents').select('*').eq('archived', False).execute()
```

---

## 운영 시나리오

### 일일 운영

```
00:00 - 새 글 수집 (20개)
01:00 - Layered perception 추출 (v2.1)
02:00 - Pattern 업데이트
03:00 - 아카이빙 실행 ← 새로 추가
       └─ 90일 이상 → archived = true
```

### 월간 운영

```
매월 1일:
  - Worldview Evolution 실행
  - Mechanism Matcher 실행
  - Pattern cleanup (Phase 2 Claude)
  - 아카이브 통계 리포트
```

---

## 데이터 흐름

### 신규 Content 생명주기

```
Day 0: 수집
  ↓
Day 0-90: Active
  - 세계관 분석 대상
  - Pattern 생성/업데이트
  ↓
Day 90: 아카이브
  - archived = true
  - 분석에서 제외
  - 패턴은 그대로 유지
  ↓
Day 90+: Archived
  - 보관만
  - 필요시 복구 가능
```

### Pattern 생명주기 (독립적)

```
Pattern 생성 (from perception)
  ↓
강화/약화 (자체 lifecycle)
  ↓
Dead pattern cleanup
  ↓
삭제

※ Content 아카이브 여부와 무관
```

---

## 복구 시나리오

### 특정 기간 데이터 복구

```python
# 예: 2024년 10월 데이터 복구
archiver.restore_period(
    start_date='2024-10-01',
    end_date='2024-10-31'
)

# 복구 후:
# - archived = false
# - 다시 분석 대상에 포함
```

---

## 통계 및 모니터링

### 일일 아카이빙 리포트

```
=== Archiving Report 2025-10-24 ===

Active contents: 1,823개 (최근 90일)
Archived today: 25개
Total archived: 3,456개

Breakdown by age:
  0-30 days: 612개
  30-60 days: 589개
  60-90 days: 622개
  90+ days (archived): 3,456개

DB size: ~2.5GB (5GB → 2.5GB 절감)
```

---

## 비용 영향

### Before (무제한 누적)

```
6개월 후: 3,600개 contents
Evolution 비용: $36
Pattern 재분석: $36
총: $72/month
```

### After (3개월 아카이빙)

```
항상: ~1,800개 contents
Evolution 비용: $18
Pattern 재분석: $18
총: $36/month

절감: 50%
```

---

## 안전장치

### 1. Dry Run 모드

```bash
# 실제 아카이브 전 미리보기
python3 scripts/daily_archiving.py --dry-run
```

### 2. 복구 기능

```python
# 실수로 아카이브한 경우 복구
archiver.restore_content(content_id)
```

### 3. 백업

```bash
# 아카이브 전 자동 백업
pg_dump -t contents -t layered_perceptions > backup_$(date +%Y%m%d).sql
```

---

## 향후 확장

### Hard Delete (선택사항)

```sql
-- 1년 이상 archived → 완전 삭제
DELETE FROM contents
WHERE archived = true
  AND archived_at < NOW() - INTERVAL '1 year';
```

### 별도 Archive DB (선택사항)

```
Active DB: PostgreSQL (빠름, 비쌈)
Archive DB: S3 + Parquet (느림, 저렴)
```

---

## 실행 순서

1. ✅ Migration 실행 (507)
2. ✅ ContentArchiver 구현
3. ✅ daily_archiving.py 작성
4. ✅ 기존 코드 archived 필터 추가
5. ✅ 테스트 (dry-run)
6. ✅ 실제 아카이빙 실행
7. ✅ Cron 등록

---

**Last Updated**: 2025-10-24
**Status**: Design Complete, Ready for Implementation
