# Phase 2: DB 스키마 준비

## 목표
새로운 분석 결과를 저장할 테이블 생성

## 실행 방법

### 1. Supabase Dashboard 접속
https://supabase.com/dashboard/project/ycmcsdbxnpmthekzyppl

### 2. SQL Editor 열기
좌측 메뉴 → SQL Editor

### 3. 마이그레이션 1 실행

**파일**: `supabase/migrations/201_create_layered_perceptions.sql`

```sql
-- Migration 201: Create layered_perceptions table
CREATE TABLE IF NOT EXISTS layered_perceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES contents(id) ON DELETE CASCADE,

    -- 표면층 (Explicit Layer)
    explicit_claims JSONB DEFAULT '[]'::jsonb,

    -- 암묵층 (Implicit Layer)
    implicit_assumptions JSONB DEFAULT '[]'::jsonb,
    reasoning_gaps JSONB DEFAULT '[]'::jsonb,

    -- 심층 (Deep Layer)
    deep_beliefs TEXT[] DEFAULT '{}',
    worldview_hints TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_layered_perceptions_content
    ON layered_perceptions(content_id);

CREATE INDEX IF NOT EXISTS idx_layered_perceptions_beliefs
    ON layered_perceptions USING GIN(deep_beliefs);

CREATE INDEX IF NOT EXISTS idx_layered_perceptions_created
    ON layered_perceptions(created_at DESC);

-- Comments
COMMENT ON TABLE layered_perceptions IS 'Layer-by-layer analysis of content';
COMMENT ON COLUMN layered_perceptions.explicit_claims IS 'Surface-level explicit claims';
COMMENT ON COLUMN layered_perceptions.implicit_assumptions IS 'Unstated but presupposed thoughts';
COMMENT ON COLUMN layered_perceptions.deep_beliefs IS 'Unconscious beliefs taken for granted';
```

### 4. 마이그레이션 2 실행

**파일**: `supabase/migrations/202_create_belief_patterns.sql`

```sql
-- Migration 202: Create belief_patterns table
CREATE TABLE IF NOT EXISTS belief_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    belief TEXT UNIQUE NOT NULL,

    -- Frequency statistics
    frequency INTEGER DEFAULT 0,
    percentage REAL DEFAULT 0.0,

    -- Co-occurrence with other beliefs
    co_occurring_beliefs JSONB DEFAULT '{}'::jsonb,

    -- What this belief generates
    generated_thoughts TEXT[] DEFAULT '{}',
    manifested_claims TEXT[] DEFAULT '{}',

    -- Clustering
    cluster_id UUID,
    cluster_name TEXT,

    -- Example content IDs
    example_content_ids UUID[] DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_belief_patterns_frequency
    ON belief_patterns(frequency DESC);

CREATE INDEX IF NOT EXISTS idx_belief_patterns_percentage
    ON belief_patterns(percentage DESC);

CREATE INDEX IF NOT EXISTS idx_belief_patterns_cluster
    ON belief_patterns(cluster_id);

-- Comments
COMMENT ON TABLE belief_patterns IS 'Aggregated patterns of deep beliefs';
COMMENT ON COLUMN belief_patterns.frequency IS 'How many posts contain this belief';
COMMENT ON COLUMN belief_patterns.co_occurring_beliefs IS 'Other beliefs that appear together';
```

### 5. 테이블 생성 확인

SQL Editor에서 실행:
```sql
SELECT * FROM layered_perceptions LIMIT 1;
SELECT * FROM belief_patterns LIMIT 1;
```

둘 다 정상적으로 실행되면 ✅ 완료!

## 완료 후

터미널에서 확인:
```bash
python3 phase2_verify_schema.py
```
