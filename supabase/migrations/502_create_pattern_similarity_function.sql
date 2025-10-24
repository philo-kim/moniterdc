-- 502: Create RPC function for pattern similarity search
-- Purpose: Find similar patterns using vector embeddings

CREATE OR REPLACE FUNCTION find_similar_patterns(
    target_worldview_id UUID,
    target_layer TEXT,
    target_embedding vector(1536),
    max_distance FLOAT DEFAULT 0.3,
    limit_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    worldview_id UUID,
    layer TEXT,
    text TEXT,
    strength FLOAT,
    status TEXT,
    appearance_count INT,
    last_seen TIMESTAMP,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        wp.id,
        wp.worldview_id,
        wp.layer,
        wp.text,
        wp.strength,
        wp.status,
        wp.appearance_count,
        wp.last_seen,
        1 - (wp.embedding <=> target_embedding) AS similarity
    FROM worldview_patterns wp
    WHERE wp.worldview_id = target_worldview_id
        AND wp.layer = target_layer
        AND wp.status IN ('active', 'fading')
        AND wp.embedding IS NOT NULL
        AND wp.embedding <=> target_embedding <= max_distance
    ORDER BY wp.embedding <=> target_embedding
    LIMIT limit_count;
END;
$$;

COMMENT ON FUNCTION find_similar_patterns IS 'Find patterns similar to target embedding using cosine distance';
