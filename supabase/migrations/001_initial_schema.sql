-- Logic Defense System v3.0 - Initial Schema
-- DC갤러리 정치 AI 모니터링 시스템 기본 스키마

-- pgvector 확장 설치
CREATE EXTENSION IF NOT EXISTS vector;

-- 논리 저장소 테이블 (핵심 테이블)
CREATE TABLE IF NOT EXISTS logic_repository (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 기본 분류
    logic_type TEXT NOT NULL CHECK (logic_type IN ('attack', 'defense')),
    source_gallery TEXT NOT NULL, -- 'uspolitics', 'minjudang'
    ai_classification TEXT NOT NULL DEFAULT '분석필요',

    -- 논리 내용
    core_argument TEXT NOT NULL,
    keywords JSONB DEFAULT '[]'::jsonb,
    category TEXT DEFAULT 'other',

    -- 점수/품질
    evidence_quality INTEGER DEFAULT 5 CHECK (evidence_quality >= 1 AND evidence_quality <= 10),
    threat_level INTEGER DEFAULT 3 CHECK (threat_level >= 1 AND threat_level <= 10),
    effectiveness_score INTEGER DEFAULT 5 CHECK (effectiveness_score >= 1 AND effectiveness_score <= 10),

    -- 원본 정보
    original_title TEXT NOT NULL,
    original_content TEXT,
    original_url TEXT,
    original_post_num INTEGER,

    -- 벡터 임베딩 (1536 차원)
    vector_embedding vector(1536),

    -- 사용 통계
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,

    -- 상태
    is_active BOOLEAN DEFAULT true,

    -- 시간 정보
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 논리 매칭 테이블
CREATE TABLE IF NOT EXISTS logic_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    attack_id UUID NOT NULL REFERENCES logic_repository(id) ON DELETE CASCADE,
    defense_id UUID NOT NULL REFERENCES logic_repository(id) ON DELETE CASCADE,

    -- 매칭 정보
    match_confidence REAL NOT NULL CHECK (match_confidence >= 0 AND match_confidence <= 1),
    match_reason TEXT,
    match_strategy TEXT, -- '직접적 반박', '논리적 대응', '우회적 반박', '추가 논리 개발 필요'

    -- 매칭 방식
    match_type TEXT DEFAULT 'auto', -- 'auto', 'manual'
    matcher_version TEXT DEFAULT 'v3.0',

    -- 효과성 추적
    effectiveness_rating INTEGER CHECK (effectiveness_rating >= 1 AND effectiveness_rating <= 5),
    usage_count INTEGER DEFAULT 0,

    -- 상태
    is_active BOOLEAN DEFAULT true,

    -- 시간 정보
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 중복 방지
    UNIQUE(attack_id, defense_id)
);

-- 알림 테이블
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 알림 내용
    alert_type TEXT NOT NULL, -- 'new_attack', 'auto_match', 'instant_match', 'system_error'
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,

    -- 메타데이터
    metadata JSONB DEFAULT '{}'::jsonb,

    -- 발송 정보
    sent_at TIMESTAMPTZ NULL,
    send_channel TEXT DEFAULT 'telegram', -- 'telegram', 'email', 'webhook'

    -- 시간 정보
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 시스템 통계 테이블
CREATE TABLE IF NOT EXISTS system_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 통계 타입
    stat_type TEXT NOT NULL, -- 'daily', 'hourly', 'crawl_session'
    stat_date DATE NOT NULL,

    -- 크롤링 통계
    crawled_posts INTEGER DEFAULT 0,
    processed_logics INTEGER DEFAULT 0,
    failed_analysis INTEGER DEFAULT 0,

    -- 매칭 통계
    new_matches INTEGER DEFAULT 0,
    high_confidence_matches INTEGER DEFAULT 0,

    -- 갤러리별 통계
    attack_logics INTEGER DEFAULT 0,
    defense_logics INTEGER DEFAULT 0,

    -- 메타데이터
    metadata JSONB DEFAULT '{}'::jsonb,

    -- 시간 정보
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- 중복 방지
    UNIQUE(stat_type, stat_date)
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_logic_repository_type ON logic_repository(logic_type);
CREATE INDEX IF NOT EXISTS idx_logic_repository_gallery ON logic_repository(source_gallery);
CREATE INDEX IF NOT EXISTS idx_logic_repository_active ON logic_repository(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_logic_repository_created ON logic_repository(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logic_repository_effectiveness ON logic_repository(effectiveness_score DESC);

CREATE INDEX IF NOT EXISTS idx_logic_matches_attack ON logic_matches(attack_id);
CREATE INDEX IF NOT EXISTS idx_logic_matches_defense ON logic_matches(defense_id);
CREATE INDEX IF NOT EXISTS idx_logic_matches_confidence ON logic_matches(match_confidence DESC);
CREATE INDEX IF NOT EXISTS idx_logic_matches_active ON logic_matches(is_active) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_alerts_unsent ON alerts(created_at) WHERE sent_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity, created_at);

-- 벡터 검색을 위한 인덱스는 별도 마이그레이션에서 생성 (메모리 요구사항으로 인해)

-- updated_at 자동 업데이트 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_logic_repository_updated_at
    BEFORE UPDATE ON logic_repository
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_logic_matches_updated_at
    BEFORE UPDATE ON logic_matches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 기본 뷰 생성
CREATE OR REPLACE VIEW logic_summary AS
SELECT
    logic_type,
    source_gallery,
    COUNT(*) as total_count,
    COUNT(vector_embedding) as embedded_count,
    AVG(effectiveness_score) as avg_effectiveness,
    AVG(threat_level) as avg_threat_level,
    MAX(created_at) as latest_created
FROM logic_repository
WHERE is_active = true
GROUP BY logic_type, source_gallery;

CREATE OR REPLACE VIEW recent_matches AS
SELECT
    lm.*,
    la.core_argument as attack_argument,
    ld.core_argument as defense_argument,
    la.threat_level,
    ld.effectiveness_score
FROM logic_matches lm
JOIN logic_repository la ON lm.attack_id = la.id
JOIN logic_repository ld ON lm.defense_id = ld.id
WHERE lm.is_active = true
ORDER BY lm.created_at DESC;

-- 초기 데이터 설정
INSERT INTO system_stats (stat_type, stat_date, metadata)
VALUES ('daily', CURRENT_DATE, jsonb_build_object('system_version', 'v3.0', 'initialized_at', NOW()))
ON CONFLICT (stat_type, stat_date) DO NOTHING;