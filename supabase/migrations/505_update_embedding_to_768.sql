-- 505: Update embedding dimensions to 768 for sentence-transformers
-- Purpose: Use paraphrase-multilingual-mpnet-base-v2 (768 dimensions, Korean support)

-- Drop existing embedding column and index
DROP INDEX IF EXISTS idx_patterns_embedding;
ALTER TABLE worldview_patterns DROP COLUMN IF EXISTS embedding;

-- Add new embedding column with 768 dimensions
ALTER TABLE worldview_patterns ADD COLUMN embedding vector(768);

-- Recreate vector index
CREATE INDEX idx_patterns_embedding
ON worldview_patterns USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100)
WHERE status = 'active' AND embedding IS NOT NULL;

-- Update comment
COMMENT ON COLUMN worldview_patterns.embedding IS 'Text embedding for similarity matching (sentence-transformers multilingual: 768 dimensions)';
