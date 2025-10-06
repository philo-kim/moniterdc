-- Migration 103: Create worldviews table (Layer 3 - Worldview)
-- Purpose: Store detected worldview patterns and their mechanisms

CREATE TABLE IF NOT EXISTS worldviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Worldview definition
    title TEXT NOT NULL,  -- "민주당=친중=안보위협"
    frame TEXT NOT NULL,  -- "대상=속성=결과" structure

    description TEXT,

    -- Core elements
    core_subject TEXT NOT NULL,  -- "민주당"
    core_attributes TEXT[] NOT NULL,  -- ["친중", "무능"]
    overall_valence TEXT NOT NULL,  -- positive, negative

    -- Constituent perceptions
    perception_ids UUID[] NOT NULL DEFAULT '{}',

    -- Multi-dimensional strength
    strength_cognitive FLOAT DEFAULT 0,      -- 0-1, cognitive strength
    strength_temporal FLOAT DEFAULT 0,       -- 0-1, temporal persistence
    strength_social FLOAT DEFAULT 0,         -- 0-1, social spread
    strength_structural FLOAT DEFAULT 0,     -- 0-1, structural coherence
    strength_overall FLOAT DEFAULT 0,        -- 0-1, overall strength

    -- Formation mechanism
    formation_phases JSONB DEFAULT '[]',
    /*
    [
      {
        "phase": "seed",
        "date": "2024-11-15",
        "description": "Initial claims",
        "perception_count": 5
      },
      {
        "phase": "growth",
        "date_start": "2024-12-01",
        "date_end": "2024-12-31",
        "tactics": ["repetition", "variation"],
        "perception_count": 19
      }
    ]
    */

    -- Cognitive mechanisms (how it works psychologically)
    cognitive_mechanisms JSONB DEFAULT '[]',
    /*
    [
      {
        "type": "confirmation_bias",
        "description": "Reinforces existing prejudices",
        "vulnerability": "People prefer confirming information"
      },
      {
        "type": "availability_heuristic",
        "description": "Repetition makes it seem important"
      },
      {
        "type": "emotional_loading",
        "emotions": ["fear", "anger"]
      }
    ]
    */

    -- Structural flaws
    structural_flaws JSONB DEFAULT '[]',
    /*
    [
      {
        "type": "term_ambiguity",
        "term": "친중",
        "issue": "Conflates economic cooperation with security compromise"
      },
      {
        "type": "logical_leap",
        "from": "친중",
        "to": "위험",
        "issue": "No logical connection between cooperation and threat"
      }
    ]
    */

    -- Deconstruction strategy
    deconstruction JSONB DEFAULT '{}',
    /*
    {
      "counter_narrative": "Economic cooperation ≠ security threat...",
      "key_rebuttals": [
        "Term manipulation: 'pro-China' is ambiguous",
        "Logical leap: cooperation ≠ threat",
        "Selective facts: actual policy by current government"
      ],
      "suggested_response": "Copyable response text...",
      "evidence_urls": ["SBS factcheck URL", "Wikipedia URL"]
    }
    */

    -- Statistics
    total_perceptions INTEGER DEFAULT 0,
    total_contents INTEGER DEFAULT 0,
    source_diversity INTEGER DEFAULT 0,  -- Number of platforms

    -- Timestamps
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,
    peak_date TIMESTAMPTZ,

    -- Trend
    trend TEXT,  -- rising, stable, falling, dead

    -- Vector embedding
    worldview_embedding vector(1536),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_worldviews_subject ON worldviews(core_subject);
CREATE INDEX IF NOT EXISTS idx_worldviews_strength ON worldviews(strength_overall DESC);
CREATE INDEX IF NOT EXISTS idx_worldviews_trend ON worldviews(trend);
CREATE INDEX IF NOT EXISTS idx_worldviews_updated ON worldviews(updated_at DESC);

-- Vector index
CREATE INDEX IF NOT EXISTS idx_worldviews_embedding ON worldviews
USING ivfflat (worldview_embedding vector_cosine_ops)
WITH (lists = 50);

-- Comments
COMMENT ON TABLE worldviews IS 'Layer 3: Worldview - Detected patterns and their mechanisms';
COMMENT ON COLUMN worldviews.frame IS 'Structure: Subject=Attribute=Result';
COMMENT ON COLUMN worldviews.formation_phases IS 'How the worldview was built over time';
COMMENT ON COLUMN worldviews.cognitive_mechanisms IS 'Psychological mechanisms exploited';
COMMENT ON COLUMN worldviews.structural_flaws IS 'Logical and structural weaknesses';
COMMENT ON COLUMN worldviews.deconstruction IS 'Strategy to deconstruct this worldview';