-- Migration 101: Create perceptions table (Layer 2 - Perception)
-- Purpose: Store extracted perceptions/impressions from content

-- Enable vector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS perceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL REFERENCES contents(id) ON DELETE CASCADE,

    -- Perception data
    perceived_subject TEXT NOT NULL,
    -- "민주당", "이재명", "윤석열", "중국", "미국", etc

    perceived_attribute TEXT NOT NULL,
    -- "친중", "부패", "무능", "국가수호자", etc

    perceived_valence TEXT NOT NULL,
    -- positive, negative, neutral

    -- Extracted claims
    claims TEXT[] DEFAULT '{}',
    -- ["민주당이 중국인 무비자를 허용했다", "조선족이 집단 도주했다"]

    -- Keywords
    keywords TEXT[] DEFAULT '{}',

    -- Emotions (emotional loading detection)
    emotions TEXT[] DEFAULT '{}',
    -- ["fear", "anger", "disgust"]

    -- Vector embedding for similarity search
    perception_embedding vector(1536),

    -- Credibility & confidence
    credibility FLOAT,  -- Inherited from content's base_credibility
    confidence FLOAT,   -- GPT analysis confidence score

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_perceptions_content ON perceptions(content_id);
CREATE INDEX IF NOT EXISTS idx_perceptions_subject ON perceptions(perceived_subject);
CREATE INDEX IF NOT EXISTS idx_perceptions_valence ON perceptions(perceived_valence);
CREATE INDEX IF NOT EXISTS idx_perceptions_created ON perceptions(created_at DESC);

-- Vector index for similarity search
CREATE INDEX IF NOT EXISTS idx_perceptions_embedding ON perceptions
USING ivfflat (perception_embedding vector_cosine_ops)
WITH (lists = 100);

-- Comments
COMMENT ON TABLE perceptions IS 'Layer 2: Perception - Extracted impressions and claims from content';
COMMENT ON COLUMN perceptions.perceived_subject IS 'Who is this about? (e.g., 민주당, 이재명)';
COMMENT ON COLUMN perceptions.perceived_attribute IS 'What attribute is assigned? (e.g., 친중, 부패)';
COMMENT ON COLUMN perceptions.perceived_valence IS 'Positive, negative, or neutral perception';
COMMENT ON COLUMN perceptions.emotions IS 'Detected emotional loading (fear, anger, etc)';
COMMENT ON COLUMN perceptions.perception_embedding IS 'Vector embedding for similarity search';