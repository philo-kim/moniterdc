-- Migration: Add political_frame column for narrative-based clustering
-- Purpose: Store the political frame/narrative that each logic contributes to
-- This enables clustering by broader political narratives instead of specific topics

-- Add political_frame to logic_repository
ALTER TABLE logic_repository
ADD COLUMN IF NOT EXISTS political_frame TEXT;

CREATE INDEX IF NOT EXISTS idx_logic_repository_political_frame
ON logic_repository(political_frame);

-- Update logic_clusters to use political_frame
ALTER TABLE logic_clusters
ADD COLUMN IF NOT EXISTS political_frame TEXT;

-- Drop old find_or_create_cluster function
DROP FUNCTION IF EXISTS find_or_create_cluster(TEXT, TEXT);

-- Create new function that clusters by political_frame
CREATE OR REPLACE FUNCTION find_or_create_cluster_by_frame(
    p_political_frame TEXT,
    p_context_issue TEXT DEFAULT NULL,
    p_distortion_pattern TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_cluster_id UUID;
BEGIN
    -- 같은 political_frame을 가진 클러스터 찾기
    SELECT id INTO v_cluster_id
    FROM logic_clusters
    WHERE political_frame = p_political_frame
    LIMIT 1;

    -- 없으면 새로 생성
    IF v_cluster_id IS NULL THEN
        INSERT INTO logic_clusters (
            id,
            cluster_name,
            political_frame,
            context_issue,
            common_distortion_pattern,
            logic_count,
            first_seen,
            last_seen
        ) VALUES (
            gen_random_uuid(),
            p_political_frame,  -- cluster_name = political_frame
            p_political_frame,
            p_context_issue,
            p_distortion_pattern,
            0,
            NOW(),
            NOW()
        )
        RETURNING id INTO v_cluster_id;
    END IF;

    RETURN v_cluster_id;
END;
$$ LANGUAGE plpgsql;

-- Update trigger to use political_frame
CREATE OR REPLACE FUNCTION assign_logic_to_cluster()
RETURNS TRIGGER AS $$
DECLARE
    v_cluster_id UUID;
BEGIN
    -- political_frame이 있으면 클러스터 할당
    IF NEW.political_frame IS NOT NULL THEN
        v_cluster_id := find_or_create_cluster_by_frame(
            NEW.political_frame,
            NEW.context_issue,
            NEW.distortion_pattern
        );

        NEW.cluster_id := v_cluster_id;

        -- 클러스터 통계 업데이트
        UPDATE logic_clusters
        SET
            logic_count = logic_count + 1,
            last_seen = NOW()
        WHERE id = v_cluster_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop old trigger if exists
DROP TRIGGER IF EXISTS trigger_assign_cluster ON logic_repository;

-- Create new trigger
CREATE TRIGGER trigger_assign_cluster
    BEFORE INSERT ON logic_repository
    FOR EACH ROW
    EXECUTE FUNCTION assign_logic_to_cluster();

-- Update existing logic_clusters view to show political_frame
CREATE OR REPLACE VIEW cluster_stats AS
SELECT
    c.id,
    c.cluster_name,
    c.political_frame,
    c.logic_count,
    c.first_seen,
    c.last_seen,
    ROUND(AVG(l.threat_level)::numeric, 1) as avg_threat_level,
    ROUND(AVG(l.effectiveness_score)::numeric, 1) as avg_effectiveness,
    ARRAY_AGG(DISTINCT l.context_issue) FILTER (WHERE l.context_issue IS NOT NULL) as context_issues,
    COUNT(DISTINCT l.context_issue) as issue_diversity
FROM logic_clusters c
LEFT JOIN logic_repository l ON l.cluster_id = c.id
GROUP BY c.id, c.cluster_name, c.political_frame, c.logic_count, c.first_seen, c.last_seen;