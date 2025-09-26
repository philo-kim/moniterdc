-- LangChain RAG 시스템을 위한 추가 마이그레이션
-- 기존 logic_repository 테이블에 RAG 관련 컬럼 추가

-- 1. 일일 리포트 테이블
CREATE TABLE IF NOT EXISTS daily_reports (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    date DATE NOT NULL,
    trending_topics JSONB,
    top_attacks JSONB,
    effective_defenses JSONB,
    total_analyzed INTEGER DEFAULT 0,
    generated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

-- 2. 피드백 테이블 (논리 효과성 추적)
CREATE TABLE IF NOT EXISTS logic_feedback (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    logic_id UUID REFERENCES logic_repository(id) ON DELETE CASCADE,
    success BOOLEAN NOT NULL,
    feedback TEXT,
    context JSONB,
    created_by TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. 대화 히스토리 테이블 (RAG 컨텍스트 유지)
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('human', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_chat_session (session_id, created_at)
);

-- 4. logic_repository 테이블 업데이트
ALTER TABLE logic_repository 
ADD COLUMN IF NOT EXISTS last_used_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS feedback JSONB,
ADD COLUMN IF NOT EXISTS rag_metadata JSONB,
ADD COLUMN IF NOT EXISTS embedding_model TEXT DEFAULT 'text-embedding-3-large',
ADD COLUMN IF NOT EXISTS embedding_dimension INTEGER DEFAULT 1536;

-- 5. 벡터 검색 개선 함수
CREATE OR REPLACE FUNCTION search_similar_logic_with_metadata(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10,
    logic_type_filter text DEFAULT NULL,
    classification_filter text DEFAULT NULL,
    min_effectiveness int DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    logic_type text,
    core_argument text,
    keywords jsonb,
    ai_classification text,
    effectiveness_score int,
    similarity float,
    usage_count int,
    success_rate float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        lr.id,
        lr.logic_type,
        lr.core_argument,
        lr.keywords,
        lr.ai_classification,
        lr.effectiveness_score,
        1 - (lr.vector_embedding <=> query_embedding) as similarity,
        lr.usage_count,
        CASE 
            WHEN lr.usage_count > 0 THEN lr.success_count::float / lr.usage_count::float
            ELSE 0
        END as success_rate
    FROM logic_repository lr
    WHERE 
        (logic_type_filter IS NULL OR lr.logic_type = logic_type_filter)
        AND (classification_filter IS NULL OR lr.ai_classification = classification_filter)
        AND (min_effectiveness IS NULL OR lr.effectiveness_score >= min_effectiveness)
        AND lr.is_active = true
        AND lr.vector_embedding IS NOT NULL
        AND (1 - (lr.vector_embedding <=> query_embedding)) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

-- 6. 자동 매칭 트리거 개선
CREATE OR REPLACE FUNCTION auto_match_logic_with_context()
RETURNS TRIGGER AS $$
DECLARE
    matching_logic RECORD;
    match_confidence FLOAT;
    match_strategy TEXT;
BEGIN
    -- 공격 논리가 추가되었을 때만 실행
    IF NEW.logic_type = 'attack' AND NEW.vector_embedding IS NOT NULL THEN
        -- 가장 유사한 방어 논리 찾기
        FOR matching_logic IN 
            SELECT * FROM search_similar_logic_with_metadata(
                NEW.vector_embedding,
                0.75,  -- threshold
                3,     -- top 3
                'defense',  -- only defense logic
                NULL,  -- any classification
                7      -- minimum effectiveness
            )
        LOOP
            -- 매칭 신뢰도 계산 (유사도 * 효과성 * 성공률)
            match_confidence := matching_logic.similarity * 
                               (matching_logic.effectiveness_score / 10.0) * 
                               COALESCE(matching_logic.success_rate, 0.5);
            
            -- 전략 결정
            IF match_confidence > 0.8 THEN
                match_strategy := '직접적 반박 가능 - 높은 신뢰도';
            ELSIF match_confidence > 0.6 THEN
                match_strategy := '논리적 대응 추천 - 중간 신뢰도';
            ELSE
                match_strategy := '우회적 반박 필요 - 낮은 신뢰도';
            END IF;
            
            -- 매칭 결과 저장
            INSERT INTO logic_matches (
                attack_id,
                defense_id,
                match_confidence,
                match_reason,
                created_at
            ) VALUES (
                NEW.id,
                matching_logic.id,
                match_confidence,
                format('%s (유사도: %.2f, 효과성: %s/10, 성공률: %.0f%%)',
                    match_strategy,
                    matching_logic.similarity,
                    matching_logic.effectiveness_score,
                    matching_logic.success_rate * 100
                ),
                CURRENT_TIMESTAMP
            );
        END LOOP;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 재생성
DROP TRIGGER IF EXISTS trigger_auto_match_logic ON logic_repository;
CREATE TRIGGER trigger_auto_match_logic
    AFTER INSERT OR UPDATE OF vector_embedding
    ON logic_repository
    FOR EACH ROW
    EXECUTE FUNCTION auto_match_logic_with_context();

-- 7. 트렌딩 분석 함수
CREATE OR REPLACE FUNCTION get_trending_keywords(
    days_back int DEFAULT 7,
    top_n int DEFAULT 10
)
RETURNS TABLE (
    keyword text,
    count bigint,
    avg_effectiveness numeric,
    dominant_type text,
    trend_score numeric
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH keyword_stats AS (
        SELECT 
            jsonb_array_elements_text(keywords) as keyword,
            logic_type,
            effectiveness_score
        FROM logic_repository
        WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '1 day' * days_back
            AND keywords IS NOT NULL
    ),
    aggregated AS (
        SELECT 
            keyword,
            COUNT(*) as count,
            AVG(effectiveness_score) as avg_effectiveness,
            MODE() WITHIN GROUP (ORDER BY logic_type) as dominant_type
        FROM keyword_stats
        GROUP BY keyword
        HAVING COUNT(*) > 1
    )
    SELECT 
        keyword,
        count,
        ROUND(avg_effectiveness, 1) as avg_effectiveness,
        dominant_type,
        ROUND(count * avg_effectiveness / 10, 2) as trend_score
    FROM aggregated
    ORDER BY trend_score DESC
    LIMIT top_n;
END;
$$;

-- 8. 효과성 업데이트 함수
CREATE OR REPLACE FUNCTION update_logic_effectiveness(
    p_logic_id UUID,
    p_success BOOLEAN,
    p_feedback TEXT DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    current_usage INT;
    current_success INT;
    current_score INT;
    new_score NUMERIC;
BEGIN
    -- 현재 통계 가져오기
    SELECT usage_count, success_count, effectiveness_score
    INTO current_usage, current_success, current_score
    FROM logic_repository
    WHERE id = p_logic_id;
    
    IF FOUND THEN
        -- 사용 횟수 증가
        current_usage := COALESCE(current_usage, 0) + 1;
        current_success := COALESCE(current_success, 0) + CASE WHEN p_success THEN 1 ELSE 0 END;
        
        -- 베이지안 평균으로 새 점수 계산
        new_score := ((current_score * 10) + (current_success * 10)) / (10 + current_usage);
        new_score := LEAST(10, GREATEST(1, ROUND(new_score)));
        
        -- 업데이트
        UPDATE logic_repository
        SET 
            usage_count = current_usage,
            success_count = current_success,
            effectiveness_score = new_score::INT,
            last_used_at = CURRENT_TIMESTAMP,
            feedback = CASE 
                WHEN p_feedback IS NOT NULL 
                THEN COALESCE(feedback, '{}'::jsonb) || jsonb_build_object(
                    CURRENT_TIMESTAMP::text,
                    p_feedback
                )
                ELSE feedback
            END
        WHERE id = p_logic_id;
        
        -- 피드백 기록
        IF p_feedback IS NOT NULL THEN
            INSERT INTO logic_feedback (logic_id, success, feedback)
            VALUES (p_logic_id, p_success, p_feedback);
        END IF;
    END IF;
END;
$$;

-- 9. RLS (Row Level Security) 정책
ALTER TABLE daily_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE logic_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

-- 읽기 권한은 모두에게
CREATE POLICY "Enable read access for all users" ON daily_reports
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON logic_feedback
    FOR SELECT USING (true);

-- 쓰기 권한은 서비스 역할만
CREATE POLICY "Enable write for service role" ON daily_reports
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Enable write for service role" ON logic_feedback
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Enable write for service role" ON chat_history
    FOR ALL USING (auth.role() = 'service_role');

-- 10. 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_logic_repo_created_at ON logic_repository(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logic_repo_effectiveness ON logic_repository(effectiveness_score DESC);
CREATE INDEX IF NOT EXISTS idx_logic_repo_usage ON logic_repository(usage_count DESC);
CREATE INDEX IF NOT EXISTS idx_logic_feedback_logic_id ON logic_feedback(logic_id);
CREATE INDEX IF NOT EXISTS idx_daily_reports_date ON daily_reports(date DESC);

-- 11. 통계 뷰
CREATE OR REPLACE VIEW logic_statistics AS
SELECT 
    logic_type,
    ai_classification,
    COUNT(*) as total_count,
    AVG(effectiveness_score) as avg_effectiveness,
    AVG(threat_level) as avg_threat_level,
    SUM(usage_count) as total_usage,
    AVG(CASE 
        WHEN usage_count > 0 THEN success_count::float / usage_count::float 
        ELSE 0 
    END) as avg_success_rate,
    MAX(created_at) as last_created,
    MAX(last_used_at) as last_used
FROM logic_repository
WHERE is_active = true
GROUP BY logic_type, ai_classification;

COMMENT ON TABLE daily_reports IS 'LangChain RAG 시스템 일일 분석 리포트';
COMMENT ON TABLE logic_feedback IS '논리 사용 피드백 및 효과성 추적';
COMMENT ON TABLE chat_history IS 'RAG 대화 히스토리 (컨텍스트 유지)';
COMMENT ON FUNCTION search_similar_logic_with_metadata IS '메타데이터 필터링이 포함된 개선된 벡터 검색';
COMMENT ON FUNCTION get_trending_keywords IS '지정 기간 동안의 트렌딩 키워드 분석';
COMMENT ON FUNCTION update_logic_effectiveness IS '논리 효과성 점수 업데이트 (베이지안 평균)';
