-- Migration 105: Create RPC functions for vector search and utilities
-- Purpose: Helper functions for similarity search and statistics

-- Function: Search similar perceptions by embedding
CREATE OR REPLACE FUNCTION search_similar_perceptions(
    query_embedding vector(1536),
    similarity_threshold float DEFAULT 0.7,
    max_results int DEFAULT 10
)
RETURNS TABLE (
    id uuid,
    perceived_subject text,
    perceived_attribute text,
    perceived_valence text,
    similarity float
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.perceived_subject,
        p.perceived_attribute,
        p.perceived_valence,
        1 - (p.perception_embedding <=> query_embedding) AS similarity
    FROM perceptions p
    WHERE p.perception_embedding IS NOT NULL
        AND 1 - (p.perception_embedding <=> query_embedding) >= similarity_threshold
    ORDER BY p.perception_embedding <=> query_embedding ASC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function: Search similar worldviews by embedding
CREATE OR REPLACE FUNCTION search_similar_worldviews(
    query_embedding vector(1536),
    similarity_threshold float DEFAULT 0.7,
    max_results int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    title text,
    frame text,
    core_subject text,
    similarity float
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        w.id,
        w.title,
        w.frame,
        w.core_subject,
        1 - (w.worldview_embedding <=> query_embedding) AS similarity
    FROM worldviews w
    WHERE w.worldview_embedding IS NOT NULL
        AND 1 - (w.worldview_embedding <=> query_embedding) >= similarity_threshold
    ORDER BY w.worldview_embedding <=> query_embedding ASC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function: Update worldview statistics
CREATE OR REPLACE FUNCTION update_worldview_stats(worldview_id uuid)
RETURNS void AS $$
DECLARE
    perception_count int;
    content_count int;
    platform_count int;
BEGIN
    -- Count perceptions
    SELECT COUNT(*)
    INTO perception_count
    FROM perceptions
    WHERE id = ANY(
        SELECT unnest(perception_ids)
        FROM worldviews
        WHERE id = worldview_id
    );

    -- Count unique contents
    SELECT COUNT(DISTINCT content_id)
    INTO content_count
    FROM perceptions
    WHERE id = ANY(
        SELECT unnest(perception_ids)
        FROM worldviews
        WHERE id = worldview_id
    );

    -- Count unique platforms
    SELECT COUNT(DISTINCT c.source_type)
    INTO platform_count
    FROM contents c
    INNER JOIN perceptions p ON p.content_id = c.id
    WHERE p.id = ANY(
        SELECT unnest(perception_ids)
        FROM worldviews
        WHERE id = worldview_id
    );

    -- Update worldview
    UPDATE worldviews
    SET
        total_perceptions = perception_count,
        total_contents = content_count,
        source_diversity = platform_count,
        updated_at = NOW()
    WHERE id = worldview_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Get perception connections (both directions)
CREATE OR REPLACE FUNCTION get_perception_connections(perception_id uuid)
RETURNS TABLE (
    connection_id uuid,
    from_id uuid,
    to_id uuid,
    connection_type text,
    strength float,
    direction text
) AS $$
BEGIN
    RETURN QUERY
    -- Outgoing connections
    SELECT
        pc.id AS connection_id,
        pc.from_perception_id AS from_id,
        pc.to_perception_id AS to_id,
        pc.connection_type,
        pc.strength,
        'outgoing'::text AS direction
    FROM perception_connections pc
    WHERE pc.from_perception_id = perception_id

    UNION ALL

    -- Incoming connections
    SELECT
        pc.id AS connection_id,
        pc.from_perception_id AS from_id,
        pc.to_perception_id AS to_id,
        pc.connection_type,
        pc.strength,
        'incoming'::text AS direction
    FROM perception_connections pc
    WHERE pc.to_perception_id = perception_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Calculate rebuttal quality score
CREATE OR REPLACE FUNCTION calculate_rebuttal_quality(rebuttal_id uuid)
RETURNS float AS $$
DECLARE
    upvote_count int;
    downvote_count int;
    total_votes int;
    credibility_score float;
    quality_score float;
BEGIN
    -- Get vote counts
    SELECT upvotes, downvotes, credibility
    INTO upvote_count, downvote_count, credibility_score
    FROM rebuttals
    WHERE id = rebuttal_id;

    total_votes := upvote_count + downvote_count;

    -- Calculate quality score
    -- Formula: (credibility * 0.5) + (vote_ratio * 0.5)
    IF total_votes > 0 THEN
        quality_score := (credibility_score * 0.5) + ((upvote_count::float / total_votes) * 0.5);
    ELSE
        quality_score := credibility_score * 0.5;
    END IF;

    RETURN quality_score;
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON FUNCTION search_similar_perceptions IS 'Search perceptions by vector similarity';
COMMENT ON FUNCTION search_similar_worldviews IS 'Search worldviews by vector similarity';
COMMENT ON FUNCTION update_worldview_stats IS 'Update worldview statistics (counts, diversity)';
COMMENT ON FUNCTION get_perception_connections IS 'Get all connections for a perception (both directions)';
COMMENT ON FUNCTION calculate_rebuttal_quality IS 'Calculate quality score for a rebuttal based on votes and credibility';