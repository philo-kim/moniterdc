-- Migration 106: Create worldview strength history table
-- Purpose: Track worldview strength over time for trend analysis

CREATE TABLE IF NOT EXISTS worldview_strength_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worldview_id UUID NOT NULL REFERENCES worldviews(id) ON DELETE CASCADE,

    -- Strength snapshot
    strength_cognitive FLOAT NOT NULL,
    strength_temporal FLOAT NOT NULL,
    strength_social FLOAT NOT NULL,
    strength_structural FLOAT NOT NULL,
    strength_overall FLOAT NOT NULL,

    -- Context
    perception_count INTEGER NOT NULL,
    content_count INTEGER NOT NULL,

    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_strength_history_worldview ON worldview_strength_history(worldview_id);
CREATE INDEX IF NOT EXISTS idx_strength_history_time ON worldview_strength_history(recorded_at DESC);

-- Comments
COMMENT ON TABLE worldview_strength_history IS 'Historical snapshots of worldview strength for trend analysis';
