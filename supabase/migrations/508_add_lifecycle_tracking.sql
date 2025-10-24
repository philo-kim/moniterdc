-- Migration 508: Lifecycle Tracking for Worldviews and Patterns
-- Purpose: Track birth, growth, decay, and death of worldviews/patterns for visualization

-- Worldview History (daily snapshots)
CREATE TABLE IF NOT EXISTS worldview_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worldview_id UUID REFERENCES worldviews(id) ON DELETE CASCADE,

    -- Time
    snapshot_date DATE NOT NULL,

    -- Status
    status TEXT NOT NULL CHECK (status IN ('active', 'evolving', 'fading', 'archived')),

    -- Statistics
    total_perceptions INT DEFAULT 0,
    total_patterns INT DEFAULT 0,
    avg_pattern_strength FLOAT DEFAULT 0.0,

    -- Changes
    new_patterns_count INT DEFAULT 0,
    dead_patterns_count INT DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint: one snapshot per worldview per day
    UNIQUE(worldview_id, snapshot_date)
);

-- Pattern Snapshots (daily snapshots)
CREATE TABLE IF NOT EXISTS pattern_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_id UUID REFERENCES worldview_patterns(id) ON DELETE CASCADE,

    -- Time
    snapshot_date DATE NOT NULL,

    -- State
    status TEXT,
    strength FLOAT,
    appearance_count INT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint: one snapshot per pattern per day
    UNIQUE(pattern_id, snapshot_date)
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_worldview_history_date
ON worldview_history(worldview_id, snapshot_date DESC);

CREATE INDEX IF NOT EXISTS idx_worldview_history_snapshot_date
ON worldview_history(snapshot_date);

CREATE INDEX IF NOT EXISTS idx_pattern_snapshots_date
ON pattern_snapshots(pattern_id, snapshot_date DESC);

CREATE INDEX IF NOT EXISTS idx_pattern_snapshots_snapshot_date
ON pattern_snapshots(snapshot_date);

-- Function: Take daily worldview snapshot
CREATE OR REPLACE FUNCTION take_worldview_snapshot(wv_id UUID, snap_date DATE DEFAULT CURRENT_DATE)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    snapshot_id UUID;
    wv_status TEXT;
    perc_count INT;
    patt_count INT;
    avg_str FLOAT;
    new_patt INT;
    dead_patt INT;
BEGIN
    -- Get worldview status
    SELECT
        CASE
            WHEN archived = true THEN 'archived'
            ELSE 'active'
        END
    INTO wv_status
    FROM worldviews WHERE id = wv_id;

    -- Count perceptions
    SELECT COUNT(*)
    INTO perc_count
    FROM perception_worldview_links
    WHERE worldview_id = wv_id;

    -- Count patterns
    SELECT COUNT(*)
    INTO patt_count
    FROM worldview_patterns
    WHERE worldview_id = wv_id
      AND status IN ('active', 'fading');

    -- Average pattern strength
    SELECT COALESCE(AVG(strength), 0.0)
    INTO avg_str
    FROM worldview_patterns
    WHERE worldview_id = wv_id
      AND status IN ('active', 'fading');

    -- New patterns (created today)
    SELECT COUNT(*)
    INTO new_patt
    FROM worldview_patterns
    WHERE worldview_id = wv_id
      AND DATE(first_seen) = snap_date;

    -- Dead patterns (became dead today)
    SELECT COUNT(*)
    INTO dead_patt
    FROM worldview_patterns
    WHERE worldview_id = wv_id
      AND status = 'dead'
      AND DATE(last_seen) = snap_date - INTERVAL '1 day';

    -- Insert or update snapshot
    INSERT INTO worldview_history (
        worldview_id,
        snapshot_date,
        status,
        total_perceptions,
        total_patterns,
        avg_pattern_strength,
        new_patterns_count,
        dead_patterns_count
    ) VALUES (
        wv_id,
        snap_date,
        wv_status,
        perc_count,
        patt_count,
        avg_str,
        new_patt,
        dead_patt
    )
    ON CONFLICT (worldview_id, snapshot_date)
    DO UPDATE SET
        status = EXCLUDED.status,
        total_perceptions = EXCLUDED.total_perceptions,
        total_patterns = EXCLUDED.total_patterns,
        avg_pattern_strength = EXCLUDED.avg_pattern_strength,
        new_patterns_count = EXCLUDED.new_patterns_count,
        dead_patterns_count = EXCLUDED.dead_patterns_count
    RETURNING id INTO snapshot_id;

    RETURN snapshot_id;
END;
$$;

-- Function: Take daily pattern snapshot
CREATE OR REPLACE FUNCTION take_pattern_snapshot(patt_id UUID, snap_date DATE DEFAULT CURRENT_DATE)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    snapshot_id UUID;
    patt_status TEXT;
    patt_strength FLOAT;
    patt_count INT;
BEGIN
    -- Get pattern state
    SELECT status, strength, appearance_count
    INTO patt_status, patt_strength, patt_count
    FROM worldview_patterns
    WHERE id = patt_id;

    -- Insert or update snapshot
    INSERT INTO pattern_snapshots (
        pattern_id,
        snapshot_date,
        status,
        strength,
        appearance_count
    ) VALUES (
        patt_id,
        snap_date,
        patt_status,
        patt_strength,
        patt_count
    )
    ON CONFLICT (pattern_id, snapshot_date)
    DO UPDATE SET
        status = EXCLUDED.status,
        strength = EXCLUDED.strength,
        appearance_count = EXCLUDED.appearance_count
    RETURNING id INTO snapshot_id;

    RETURN snapshot_id;
END;
$$;

-- Function: Get worldview lifecycle (for graphs)
CREATE OR REPLACE FUNCTION get_worldview_lifecycle(wv_id UUID, days INT DEFAULT 90)
RETURNS TABLE (
    date DATE,
    total_patterns INT,
    avg_strength FLOAT,
    status TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        wh.snapshot_date,
        wh.total_patterns,
        wh.avg_pattern_strength,
        wh.status
    FROM worldview_history wh
    WHERE wh.worldview_id = wv_id
      AND wh.snapshot_date >= CURRENT_DATE - days
    ORDER BY wh.snapshot_date;
END;
$$;

-- Comments
COMMENT ON TABLE worldview_history IS '세계관 생명주기 추적 (매일 스냅샷)';
COMMENT ON TABLE pattern_snapshots IS '패턴 생명주기 추적 (매일 스냅샷)';

COMMENT ON FUNCTION take_worldview_snapshot IS '세계관 일일 스냅샷 저장';
COMMENT ON FUNCTION take_pattern_snapshot IS '패턴 일일 스냅샷 저장';
COMMENT ON FUNCTION get_worldview_lifecycle IS '세계관 생명주기 데이터 조회 (그래프용)';
