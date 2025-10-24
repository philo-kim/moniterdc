# 세계관 생명주기 추적 시스템

## 🎯 목표

**"세계관의 탄생, 성장, 쇠퇴, 소멸을 추적하여 그래프로 시각화"**

- 패턴의 생성/소멸 기록
- 세계관의 등장/사라짐 추적
- 시간에 따른 변화 그래프

---

## 📊 추적할 데이터

### 1. 패턴 라이프사이클
```
생성 (first_seen) → 강화/약화 (strength) → 소멸 (status=dead)
```

### 2. 세계관 라이프사이클
```
발견 (created_at) → 진화 (updated) → 아카이브 (archived)
```

### 3. 시계열 데이터
```
- 매일: 패턴 strength 변화
- 매월: 세계관 등장/소멸
- 분기: 담론 지형 변화
```

---

## 🗄️ 히스토리 테이블 설계

### worldview_history (세계관 히스토리)
```sql
CREATE TABLE worldview_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    worldview_id UUID REFERENCES worldviews(id),

    -- 시점
    snapshot_date DATE NOT NULL,

    -- 상태
    status TEXT NOT NULL,  -- 'active', 'evolving', 'fading', 'archived'

    -- 통계
    total_perceptions INT,
    total_patterns INT,
    avg_pattern_strength FLOAT,

    -- 변화
    new_patterns_count INT,
    dead_patterns_count INT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_worldview_history_date ON worldview_history(worldview_id, snapshot_date);
```

### pattern_snapshots (패턴 스냅샷)
```sql
CREATE TABLE pattern_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_id UUID REFERENCES worldview_patterns(id) ON DELETE CASCADE,

    -- 시점
    snapshot_date DATE NOT NULL,

    -- 상태
    status TEXT,
    strength FLOAT,
    appearance_count INT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_pattern_snapshots_date ON pattern_snapshots(pattern_id, snapshot_date);
```

---

## 🔄 데이터 수집 방식

### 매일 스냅샷 (Daily Snapshot)

```python
# scripts/daily_snapshot.py

def take_daily_snapshot():
    """매일 패턴과 세계관 상태 기록"""

    today = date.today()

    for worldview in active_worldviews:
        # 1. 패턴 스냅샷
        for pattern in worldview.patterns:
            save_pattern_snapshot(
                pattern_id=pattern.id,
                snapshot_date=today,
                status=pattern.status,
                strength=pattern.strength,
                appearance_count=pattern.appearance_count
            )

        # 2. 세계관 스냅샷
        save_worldview_snapshot(
            worldview_id=worldview.id,
            snapshot_date=today,
            status=worldview.status,
            total_perceptions=count_perceptions(worldview.id),
            total_patterns=count_patterns(worldview.id),
            avg_pattern_strength=avg_strength(worldview.id)
        )
```

---

## 📈 그래프 시각화 데이터

### 1. 세계관 생명주기 그래프

```sql
-- 세계관의 패턴 수 변화 (지난 90일)
SELECT
    snapshot_date,
    total_patterns,
    avg_pattern_strength
FROM worldview_history
WHERE worldview_id = $1
  AND snapshot_date >= NOW() - INTERVAL '90 days'
ORDER BY snapshot_date;
```

**그래프**:
```
패턴 수
  ^
  |     *****
  |  ***     ****
  | *            **
  |*               ***
  +-------------------> 시간
  7/1  8/1  9/1  10/1

  탄생 → 성장 → 유지 → 쇠퇴
```

### 2. 세계관 비교 그래프

```sql
-- 여러 세계관의 강도 비교
SELECT
    w.title,
    wh.snapshot_date,
    wh.avg_pattern_strength
FROM worldview_history wh
JOIN worldviews w ON wh.worldview_id = w.id
WHERE wh.snapshot_date >= NOW() - INTERVAL '30 days'
ORDER BY wh.snapshot_date, w.title;
```

**그래프**:
```
강도
  ^
  | A: ****-----
  | B:  --*****--
  | C:    ---****
  +-------------------> 시간

  A: "독재 회귀" (성장 → 쇠퇴)
  B: "사법 사찰" (등장 → 성장 → 유지)
  C: "친중 침투" (신규 등장)
```

### 3. 패턴 개별 추적

```sql
-- 특정 패턴의 strength 변화
SELECT
    snapshot_date,
    strength,
    status
FROM pattern_snapshots
WHERE pattern_id = $1
ORDER BY snapshot_date;
```

**그래프**:
```
Strength
  ^
10|
  |    **
  |  **  **
 5|**      **
  |          **
 0|            **
  +-------------------> 시간

  생성 → 강화 → 유지 → 약화 → 소멸
```

---

## 🔧 구현 계획

### Step 1: Migration (508)
```sql
-- 히스토리 테이블 생성
CREATE TABLE worldview_history (...);
CREATE TABLE pattern_snapshots (...);
```

### Step 2: Daily Snapshot Script
```python
# scripts/daily_snapshot.py
# - 매일 패턴/세계관 상태 기록
# - Cron: 매일 새벽 4시
```

### Step 3: Decay + Snapshot 통합
```python
# scripts/daily_maintenance.py

# 1. Contents 아카이빙
archive_old_contents()

# 2. Pattern decay
decay_patterns()

# 3. Dead patterns cleanup
cleanup_dead_patterns()

# 4. 스냅샷 저장
take_daily_snapshot()
```

### Step 4: API 엔드포인트
```typescript
// GET /api/worldviews/[id]/history
// → 지난 90일 히스토리

// GET /api/worldviews/timeline
// → 모든 세계관 타임라인

// GET /api/patterns/[id]/history
// → 패턴 개별 히스토리
```

### Step 5: Dashboard 시각화
```tsx
// components/WorldviewLifecycleChart.tsx
// - Recharts로 라인 그래프
// - 세계관별 색상 구분
// - 생성/소멸 이벤트 표시
```

---

## 📊 예시: 세계관 타임라인

### 2025년 7월 - 10월

```
세계관 A "독재 회귀":
  7/1: 발견 (패턴 10개)
  7/15: 성장 (패턴 25개, 강도 5.2)
  8/1: 정점 (패턴 35개, 강도 6.8)
  8/15: 유지 (패턴 32개, 강도 6.5)
  9/1: 쇠퇴 시작 (패턴 20개, 강도 4.2)
  10/1: 아카이브 (패턴 5개, 강도 1.8)

세계관 B "사법 사찰":
  8/1: 발견 (패턴 15개)
  8/15: 성장 (패턴 30개, 강도 5.5)
  9/1: 정점 (패턴 45개, 강도 7.2)
  10/1: 유지 (패턴 42개, 강도 7.0) ← 현재 강함

세계관 C "친중 침투":
  9/15: 발견 (패턴 8개)
  10/1: 성장 (패턴 18개, 강도 4.5) ← 신규 등장
```

---

## 🎨 시각화 예시

### Timeline View (Gantt Chart)
```
세계관 타임라인 (2025년 7월 - 10월)

독재 회귀   ████████▓▓▓▒▒░░
사법 사찰       ████████████████
친중 침투               ██████

           7월  8월  9월  10월

█ 강함 (6+)
▓ 중간 (4-6)
▒ 약함 (2-4)
░ 소멸 (<2)
```

### Strength Graph (Line Chart)
```
강도 변화

8 |           B████
  |        B██    ██B
6 |    A██
  | A██
4 |              C██
  |
2 |
  +-------------------
  7월  8월  9월  10월

A: 독재 회귀
B: 사법 사찰
C: 친중 침투
```

---

## 💡 인사이트 도출

### 1. 세계관 수명 분석
```sql
-- 평균 세계관 수명
SELECT
    AVG(EXTRACT(DAY FROM archived_at - created_at)) as avg_lifetime_days
FROM worldviews
WHERE archived = true;
```

### 2. 패턴 변화율
```sql
-- 세계관별 패턴 변화 속도
SELECT
    worldview_id,
    STDDEV(total_patterns) as pattern_volatility
FROM worldview_history
GROUP BY worldview_id;
```

### 3. 담론 지형 변화
```sql
-- 월별 활성 세계관 수
SELECT
    DATE_TRUNC('month', snapshot_date) as month,
    COUNT(DISTINCT worldview_id) as active_worldviews
FROM worldview_history
WHERE status = 'active'
GROUP BY month;
```

---

## 🚀 실행 계획

1. ✅ Migration 508 작성 (히스토리 테이블)
2. ✅ daily_snapshot.py 구현
3. ✅ daily_maintenance.py 통합
4. ✅ API 엔드포인트 추가
5. ✅ Dashboard 그래프 컴포넌트
6. ✅ Cron 등록

---

## 📅 운영 스케줄 (최종)

```bash
# 매일 새벽 3시: 아카이빙
0 3 * * * python3 scripts/daily_archiving.py

# 매일 새벽 4시: Decay + Snapshot
0 4 * * * python3 scripts/daily_maintenance.py

# 매주 일요일: Phase 2 Claude 검증
0 5 * * 0 python3 scripts/cleanup_low_quality_patterns.py

# 매월 1일: Evolution
0 6 1 * * python3 scripts/run_worldview_evolution.py
```

---

**목표**: 세계관의 생명주기를 추적하여 담론의 변화를 시각적으로 이해
