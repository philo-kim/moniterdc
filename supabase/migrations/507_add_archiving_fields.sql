-- Migration 507: Add Archiving Fields for 3-Month Data Retention
-- Purpose: Implement 90-day active data window with archiving

-- Add archiving fields to contents table
ALTER TABLE contents
ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP WITH TIME ZONE;

-- Add archiving field to layered_perceptions (sync with contents)
ALTER TABLE layered_perceptions
ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT false;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_contents_archived
ON contents(archived, published_at DESC)
WHERE archived = false;

CREATE INDEX IF NOT EXISTS idx_contents_archived_at
ON contents(archived_at)
WHERE archived = true;

CREATE INDEX IF NOT EXISTS idx_perceptions_archived
ON layered_perceptions(archived);

-- Create view for active contents (convenience)
CREATE OR REPLACE VIEW active_contents AS
SELECT * FROM contents
WHERE archived = false
ORDER BY published_at DESC;

-- Create view for active perceptions (convenience)
CREATE OR REPLACE VIEW active_perceptions AS
SELECT lp.* FROM layered_perceptions lp
INNER JOIN contents c ON lp.content_id = c.id
WHERE c.archived = false;

-- Function to auto-archive old contents (called by cron)
CREATE OR REPLACE FUNCTION archive_old_contents(days_threshold INTEGER DEFAULT 90)
RETURNS TABLE (
    archived_count INTEGER,
    perception_count INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    content_count INTEGER;
    perception_count INTEGER;
BEGIN
    -- Archive contents older than threshold
    WITH archived_ids AS (
        UPDATE contents
        SET archived = true,
            archived_at = NOW()
        WHERE published_at < (NOW() - (days_threshold || ' days')::INTERVAL)
          AND archived = false
        RETURNING id
    )
    SELECT COUNT(*) INTO content_count FROM archived_ids;

    -- Archive corresponding perceptions
    WITH archived_perception_ids AS (
        UPDATE layered_perceptions lp
        SET archived = true
        FROM contents c
        WHERE lp.content_id = c.id
          AND c.archived = true
          AND lp.archived = false
        RETURNING lp.id
    )
    SELECT COUNT(*) INTO perception_count FROM archived_perception_ids;

    RETURN QUERY SELECT content_count, perception_count;
END;
$$;

-- Function to restore archived content
CREATE OR REPLACE FUNCTION restore_content(content_id_param UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    -- Restore content
    UPDATE contents
    SET archived = false,
        archived_at = NULL
    WHERE id = content_id_param;

    -- Restore corresponding perceptions
    UPDATE layered_perceptions
    SET archived = false
    WHERE content_id = content_id_param;

    RETURN FOUND;
END;
$$;

-- Function to get archiving statistics
CREATE OR REPLACE FUNCTION get_archive_stats()
RETURNS TABLE (
    active_contents_count BIGINT,
    archived_contents_count BIGINT,
    active_0_30_days BIGINT,
    active_30_60_days BIGINT,
    active_60_90_days BIGINT,
    total_perceptions BIGINT,
    active_perceptions BIGINT,
    archived_perceptions BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM contents WHERE archived = false),
        (SELECT COUNT(*) FROM contents WHERE archived = true),
        (SELECT COUNT(*) FROM contents
         WHERE archived = false
           AND published_at >= NOW() - INTERVAL '30 days'),
        (SELECT COUNT(*) FROM contents
         WHERE archived = false
           AND published_at >= NOW() - INTERVAL '60 days'
           AND published_at < NOW() - INTERVAL '30 days'),
        (SELECT COUNT(*) FROM contents
         WHERE archived = false
           AND published_at >= NOW() - INTERVAL '90 days'
           AND published_at < NOW() - INTERVAL '60 days'),
        (SELECT COUNT(*) FROM layered_perceptions),
        (SELECT COUNT(*) FROM layered_perceptions WHERE archived = false),
        (SELECT COUNT(*) FROM layered_perceptions WHERE archived = true);
END;
$$;

-- Add comments for documentation
COMMENT ON COLUMN contents.archived IS '3개월 이상 오래된 contents 아카이브 여부';
COMMENT ON COLUMN contents.archived_at IS '아카이브된 시점';
COMMENT ON COLUMN layered_perceptions.archived IS 'Content 아카이브 시 함께 아카이브됨';

COMMENT ON FUNCTION archive_old_contents IS '90일 이상 된 contents를 자동으로 아카이브 (매일 실행)';
COMMENT ON FUNCTION restore_content IS '아카이브된 content를 복구';
COMMENT ON FUNCTION get_archive_stats IS '아카이브 통계 조회';
