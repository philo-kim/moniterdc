-- Migration 201: Create layered_perceptions table
-- Purpose: Store 3-layer analysis of each content (explicit, implicit, deep)

CREATE TABLE IF NOT EXISTS layered_perceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES contents(id) ON DELETE CASCADE,

    -- 표면층 (Explicit Layer)
    explicit_claims JSONB DEFAULT '[]'::jsonb,
    /*
    [
      {
        "subject": "민주당",
        "predicate": "사찰했다",
        "evidence_cited": "유심교체 정보를 알았다",
        "quote": "original text from post"
      }
    ]
    */

    -- 암묵층 (Implicit Layer)
    implicit_assumptions JSONB DEFAULT '[]'::jsonb,
    /*
    [
      "비공개 정보를 안다 = 불법으로 얻었다",
      "사찰은 독재의 시작이다"
    ]
    */

    reasoning_gaps JSONB DEFAULT '[]'::jsonb,
    /*
    [
      {
        "from": "정보를 안다",
        "to": "사찰했다",
        "gap": "중간 추론 생략"
      }
    ]
    */

    -- 심층 (Deep Layer)
    deep_beliefs TEXT[] DEFAULT '{}',
    /*
    [
      "권력은 본질적으로 부패한다",
      "작은 월권은 큰 독재로 발전한다"
    ]
    */

    worldview_hints TEXT,
    -- "권력 비관론, 슬리퍼리 슬로프"

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_layered_perceptions_content
    ON layered_perceptions(content_id);

CREATE INDEX IF NOT EXISTS idx_layered_perceptions_beliefs
    ON layered_perceptions USING GIN(deep_beliefs);

CREATE INDEX IF NOT EXISTS idx_layered_perceptions_created
    ON layered_perceptions(created_at DESC);

-- Comments
COMMENT ON TABLE layered_perceptions IS 'Layer-by-layer analysis of content: explicit claims, implicit assumptions, deep beliefs';
COMMENT ON COLUMN layered_perceptions.explicit_claims IS 'Surface-level explicit claims';
COMMENT ON COLUMN layered_perceptions.implicit_assumptions IS 'Unstated but presupposed thoughts';
COMMENT ON COLUMN layered_perceptions.deep_beliefs IS 'Unconscious beliefs taken for granted';
