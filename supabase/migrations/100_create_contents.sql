-- Migration 100: Create contents table (Layer 1 - Reality)
-- Purpose: Store all source content in a source-independent way

CREATE TABLE IF NOT EXISTS contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source information
    source_type TEXT NOT NULL,
    -- dc_gallery, youtube, article, instagram, namuwiki, twitter, etc

    source_url TEXT NOT NULL UNIQUE,
    source_id TEXT,  -- Source-specific ID (DC post_num, YouTube video_id, etc)

    -- Content
    title TEXT,
    body TEXT NOT NULL,

    -- Source-specific metadata (flexible JSONB)
    metadata JSONB DEFAULT '{}',
    /*
    Examples:
    DC Gallery: {"gallery": "uspolitics", "post_num": 123, "view_count": 1000}
    YouTube: {"channel_id": "...", "video_id": "...", "view_count": 5000}
    Article: {"publisher": "SBS", "author": "...", "category": "politics"}
    */

    -- Credibility (base score by source type)
    base_credibility FLOAT DEFAULT 0.5,
    -- dc_gallery: 0.2, youtube: 0.3-0.6, article: 0.5-0.9, factcheck: 0.9

    -- Timestamps
    published_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ DEFAULT NOW(),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_contents_source_type ON contents(source_type);
CREATE INDEX IF NOT EXISTS idx_contents_published ON contents(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_contents_url ON contents(source_url);
CREATE INDEX IF NOT EXISTS idx_contents_collected ON contents(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_contents_active ON contents(is_active);

-- Comments
COMMENT ON TABLE contents IS 'Layer 1: Reality - All source content stored in source-independent format';
COMMENT ON COLUMN contents.source_type IS 'Type of source: dc_gallery, youtube, article, etc';
COMMENT ON COLUMN contents.metadata IS 'Source-specific metadata stored as JSONB for flexibility';
COMMENT ON COLUMN contents.base_credibility IS 'Base credibility score determined by source type';