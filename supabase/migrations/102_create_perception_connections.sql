-- Migration 102: Create perception_connections table
-- Purpose: Track connections between perceptions (temporal, causal, thematic)

CREATE TABLE IF NOT EXISTS perception_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    from_perception_id UUID NOT NULL REFERENCES perceptions(id) ON DELETE CASCADE,
    to_perception_id UUID NOT NULL REFERENCES perceptions(id) ON DELETE CASCADE,

    connection_type TEXT NOT NULL,
    -- temporal: Time-based sequence (A then B)
    -- causal: Causal relationship (A causes B)
    -- thematic: Thematic similarity (A and B share theme)
    -- supporting: Supporting relationship (A supports B)

    strength FLOAT DEFAULT 0.5,  -- 0-1 scale

    -- Detection method
    detected_by TEXT DEFAULT 'auto',  -- auto, manual

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(from_perception_id, to_perception_id, connection_type)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_perception_connections_from ON perception_connections(from_perception_id);
CREATE INDEX IF NOT EXISTS idx_perception_connections_to ON perception_connections(to_perception_id);
CREATE INDEX IF NOT EXISTS idx_perception_connections_type ON perception_connections(connection_type);
CREATE INDEX IF NOT EXISTS idx_perception_connections_strength ON perception_connections(strength DESC);

-- Comments
COMMENT ON TABLE perception_connections IS 'Connections between perceptions (temporal, causal, thematic)';
COMMENT ON COLUMN perception_connections.connection_type IS 'Type: temporal, causal, thematic, supporting';
COMMENT ON COLUMN perception_connections.strength IS 'Connection strength (0-1)';
COMMENT ON COLUMN perception_connections.detected_by IS 'Detection method: auto or manual';