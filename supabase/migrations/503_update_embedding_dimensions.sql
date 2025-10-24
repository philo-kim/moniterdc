-- 503: Update embedding dimensions from 1536 to 1024 for Voyage AI
-- Purpose: Switch from OpenAI ada-002 (1536) to Voyage AI voyage-3 (1024)

-- Drop existing embedding column and index
DROP INDEX IF EXISTS idx_patterns_embedding;
ALTER TABLE worldview_patterns DROP COLUMN IF EXISTS embedding;

-- Add new embedding column with 1024 dimensions
ALTER TABLE worldview_patterns ADD COLUMN embedding vector(1024);

-- Recreate vector index
CREATE INDEX idx_patterns_embedding
ON worldview_patterns USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100)
WHERE status = 'active' AND embedding IS NOT NULL;

-- Update comment
COMMENT ON COLUMN worldview_patterns.embedding IS 'Text embedding for similarity matching (Voyage AI voyage-3: 1024 dimensions)';
