-- Migration 202: Create belief_patterns table
-- Purpose: Store aggregated patterns of deep beliefs across all contents

CREATE TABLE IF NOT EXISTS belief_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    belief TEXT UNIQUE NOT NULL,

    -- Frequency statistics
    frequency INTEGER DEFAULT 0,  -- Number of posts containing this belief
    percentage REAL DEFAULT 0.0,  -- Percentage of total posts

    -- Co-occurrence with other beliefs
    co_occurring_beliefs JSONB DEFAULT '{}'::jsonb,
    /*
    {
      "권력은 부패한다": 156,
      "작은 징조를 막아야": 142
    }
    */

    -- What this belief generates
    generated_thoughts TEXT[] DEFAULT '{}',  -- Implicit thoughts generated
    manifested_claims TEXT[] DEFAULT '{}',   -- Explicit claims manifested

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
COMMENT ON TABLE belief_patterns IS 'Aggregated patterns of deep beliefs found across all contents';
COMMENT ON COLUMN belief_patterns.frequency IS 'How many posts contain this belief';
COMMENT ON COLUMN belief_patterns.co_occurring_beliefs IS 'Other beliefs that appear together';
