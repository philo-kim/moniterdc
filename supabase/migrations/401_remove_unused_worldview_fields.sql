-- Migration 401: Remove unused worldview fields
-- Purpose: Clean up fields that are not being calculated or used in the UI

-- Remove worldview_strength_history table (not being used)
DROP TABLE IF EXISTS worldview_strength_history CASCADE;

-- Remove strength-related columns (all showing 0, not calculated)
ALTER TABLE worldviews DROP COLUMN IF EXISTS strength_cognitive;
ALTER TABLE worldviews DROP COLUMN IF EXISTS strength_temporal;
ALTER TABLE worldviews DROP COLUMN IF EXISTS strength_social;
ALTER TABLE worldviews DROP COLUMN IF EXISTS strength_structural;
ALTER TABLE worldviews DROP COLUMN IF EXISTS strength_overall;

-- Remove temporal fields (all NULL, not being tracked)
ALTER TABLE worldviews DROP COLUMN IF EXISTS first_seen;
ALTER TABLE worldviews DROP COLUMN IF EXISTS last_seen;
ALTER TABLE worldviews DROP COLUMN IF EXISTS peak_date;
ALTER TABLE worldviews DROP COLUMN IF EXISTS trend;

-- Remove unused indexes
DROP INDEX IF EXISTS idx_worldviews_strength;
DROP INDEX IF EXISTS idx_worldviews_trend;

COMMENT ON TABLE worldviews IS 'Layer 3: Worldview - Detected patterns focused on reasoning structure and mechanisms (v2.0)';
