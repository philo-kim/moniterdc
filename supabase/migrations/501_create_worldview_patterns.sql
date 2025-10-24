-- 501: Create worldview_patterns table for dynamic pattern management
-- Purpose: Store living patterns that evolve over time (surface/implicit/deep layers)

CREATE TABLE IF NOT EXISTS worldview_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  worldview_id UUID NOT NULL REFERENCES worldviews(id) ON DELETE CASCADE,
  layer TEXT NOT NULL CHECK (layer IN ('surface', 'implicit', 'deep')),
  text TEXT NOT NULL,

  -- Dynamic state
  strength FLOAT NOT NULL DEFAULT 1.0 CHECK (strength >= 0 AND strength <= 10.0),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'fading', 'dead')),

  -- Embedding for similarity matching (OpenAI ada-002: 1536 dimensions)
  embedding vector(1536),

  -- Lifecycle tracking
  first_seen TIMESTAMP NOT NULL DEFAULT now(),
  last_seen TIMESTAMP NOT NULL DEFAULT now(),
  appearance_count INT NOT NULL DEFAULT 1,

  -- Metadata
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  updated_at TIMESTAMP NOT NULL DEFAULT now(),

  -- Unique constraint: one pattern per worldview + layer + text
  UNIQUE(worldview_id, layer, text)
);

-- Indexes for fast queries
CREATE INDEX idx_patterns_worldview_layer
ON worldview_patterns(worldview_id, layer, status)
WHERE status IN ('active', 'fading');

CREATE INDEX idx_patterns_last_seen
ON worldview_patterns(layer, last_seen)
WHERE status = 'active';

-- Vector index for similarity search (requires pgvector extension)
CREATE INDEX idx_patterns_embedding
ON worldview_patterns USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100)
WHERE status = 'active' AND embedding IS NOT NULL;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_worldview_patterns_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_worldview_patterns_timestamp
BEFORE UPDATE ON worldview_patterns
FOR EACH ROW
EXECUTE FUNCTION update_worldview_patterns_updated_at();

-- Comments
COMMENT ON TABLE worldview_patterns IS 'Dynamic patterns for each worldview layer (surface/implicit/deep) with lifecycle management';
COMMENT ON COLUMN worldview_patterns.layer IS 'Pattern layer: surface (events, fast), implicit (assumptions, medium), deep (beliefs, slow)';
COMMENT ON COLUMN worldview_patterns.strength IS 'Pattern strength 0-10, increases with reinforcement, decreases with time';
COMMENT ON COLUMN worldview_patterns.status IS 'Pattern lifecycle: active (appearing), fading (weakening), dead (removed)';
COMMENT ON COLUMN worldview_patterns.embedding IS 'Text embedding for similarity matching';
COMMENT ON COLUMN worldview_patterns.appearance_count IS 'How many perceptions contain this pattern';
