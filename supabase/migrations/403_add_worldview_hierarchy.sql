-- Add hierarchical structure to worldviews table
-- Parent-child relationship for worldviews

-- Add columns for hierarchy
ALTER TABLE worldviews
  ADD COLUMN parent_worldview_id UUID REFERENCES worldviews(id) ON DELETE CASCADE,
  ADD COLUMN level INTEGER NOT NULL DEFAULT 1,
  ADD COLUMN specific_case TEXT,
  ADD COLUMN method TEXT,
  ADD COLUMN target TEXT;

-- Add index for parent lookup
CREATE INDEX idx_worldviews_parent ON worldviews(parent_worldview_id);

-- Add index for level lookup
CREATE INDEX idx_worldviews_level ON worldviews(level);

-- Add check constraint for level (1 = parent, 2 = child)
ALTER TABLE worldviews
  ADD CONSTRAINT check_worldview_level CHECK (level IN (1, 2));

-- Add constraint: parent worldviews must have level = 1
ALTER TABLE worldviews
  ADD CONSTRAINT check_parent_level CHECK (
    (parent_worldview_id IS NULL AND level = 1) OR
    (parent_worldview_id IS NOT NULL AND level = 2)
  );

-- Comments
COMMENT ON COLUMN worldviews.parent_worldview_id IS 'Parent worldview ID (NULL for top-level worldviews)';
COMMENT ON COLUMN worldviews.level IS 'Hierarchy level: 1 = parent (broad belief), 2 = child (specific case)';
COMMENT ON COLUMN worldviews.specific_case IS 'Specific event/case for child worldviews (e.g., "지귀연 유심교체")';
COMMENT ON COLUMN worldviews.method IS 'Specific method for child worldviews (e.g., "통신사 협박")';
COMMENT ON COLUMN worldviews.target IS 'Specific target for child worldviews (e.g., "개인 통신정보")';
