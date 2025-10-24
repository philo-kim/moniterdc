-- Migration 509: Fix ambiguous column reference in get_worldview_lifecycle
-- Purpose: Qualify column names to avoid ambiguity error

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

COMMENT ON FUNCTION get_worldview_lifecycle IS '세계관 생명주기 데이터 조회 (그래프용) - 수정됨';
