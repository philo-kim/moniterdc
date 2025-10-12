-- Migration: Add reasoning structure fields to layered_perceptions
-- Date: 2025-01-11
-- Purpose: Support mechanism-based worldview system

-- Add new columns for reasoning structure
ALTER TABLE layered_perceptions
ADD COLUMN IF NOT EXISTS mechanisms TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS skipped_steps TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS actor JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS logic_chain TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS consistency_pattern TEXT DEFAULT '';

-- Add worldview evolution tracking fields
ALTER TABLE worldviews
ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS evolution_history JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_layered_perceptions_mechanisms ON layered_perceptions USING GIN (mechanisms);
CREATE INDEX IF NOT EXISTS idx_worldviews_archived ON worldviews (archived) WHERE archived = FALSE;

-- Add comment
COMMENT ON COLUMN layered_perceptions.mechanisms IS '5 core mechanisms: 즉시_단정, 역사_투사, 필연적_인과, 네트워크_추론, 표면_부정';
COMMENT ON COLUMN layered_perceptions.actor IS 'Actor structure: {subject, purpose, methods}';
COMMENT ON COLUMN worldviews.version IS 'Worldview version number for tracking evolution';
COMMENT ON COLUMN worldviews.evolution_history IS 'History of worldview changes over time';
