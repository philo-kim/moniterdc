-- Migration 203: Create perception_worldview_links table
-- Purpose: N:M relationship between layered_perceptions and worldviews

CREATE TABLE IF NOT EXISTS perception_worldview_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign keys
    perception_id UUID REFERENCES layered_perceptions(id) ON DELETE CASCADE,
    worldview_id UUID REFERENCES worldviews(id) ON DELETE CASCADE,

    -- Relevance score: 0-1, how strongly this perception expresses this worldview
    relevance_score FLOAT DEFAULT 1.0,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_pwlinks_perception
    ON perception_worldview_links(perception_id);

CREATE INDEX IF NOT EXISTS idx_pwlinks_worldview
    ON perception_worldview_links(worldview_id);

CREATE INDEX IF NOT EXISTS idx_pwlinks_relevance
    ON perception_worldview_links(relevance_score DESC);

-- Unique constraint: one perception can link to same worldview only once
CREATE UNIQUE INDEX IF NOT EXISTS idx_pwlinks_unique
    ON perception_worldview_links(perception_id, worldview_id);

-- Comments
COMMENT ON TABLE perception_worldview_links IS 'N:M links between layered_perceptions and worldviews';
COMMENT ON COLUMN perception_worldview_links.relevance_score IS 'How strongly (0-1) this perception expresses this worldview';
