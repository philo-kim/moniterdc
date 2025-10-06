-- Migration 104: Create rebuttals table
-- Purpose: Store rebuttals (both perception-level and worldview-level)

CREATE TABLE IF NOT EXISTS rebuttals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Target (what this rebuttal addresses)
    target_type TEXT NOT NULL,  -- perception, worldview
    target_id UUID NOT NULL,

    -- Rebuttal content
    title TEXT NOT NULL,
    content TEXT NOT NULL,

    -- Source
    rebuttal_type TEXT NOT NULL,  -- factcheck, official, user_submitted
    source_url TEXT,

    -- Quality metrics
    credibility FLOAT DEFAULT 0.5,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_rebuttals_target ON rebuttals(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_rebuttals_type ON rebuttals(rebuttal_type);
CREATE INDEX IF NOT EXISTS idx_rebuttals_quality ON rebuttals((upvotes - downvotes) DESC);

-- Voting table
CREATE TABLE IF NOT EXISTS rebuttal_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rebuttal_id UUID NOT NULL REFERENCES rebuttals(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,  -- Session ID or user ID
    vote INTEGER NOT NULL,  -- 1 (upvote) or -1 (downvote)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(rebuttal_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_rebuttal_votes_rebuttal ON rebuttal_votes(rebuttal_id);

-- Comments
COMMENT ON TABLE rebuttals IS 'Rebuttals for perceptions and worldviews';
COMMENT ON COLUMN rebuttals.target_type IS 'Type: perception or worldview';
COMMENT ON COLUMN rebuttals.rebuttal_type IS 'Source: factcheck, official, or user_submitted';
COMMENT ON TABLE rebuttal_votes IS 'User votes on rebuttals for quality assessment';