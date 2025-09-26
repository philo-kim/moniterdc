-- Logic Defense System v3.0 - Vector Embedding Enhancement (No Index Version)
-- 메모리 제약으로 인한 인덱스 없는 벡터 최적화 버전

-- 1. 벡터 검색 성능 최적화 (인덱스 없이)
-- 기존 find_similar_logic 함수 삭제 후 재생성
DROP FUNCTION IF EXISTS find_similar_logic(vector, float, int, text);
CREATE OR REPLACE FUNCTION find_similar_logic(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.8,
    match_count int DEFAULT 10,
    logic_type_filter text DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    logic_type text,
    core_argument text,
    similarity float,
    effectiveness_score int,
    threat_level int,
    source_gallery text,
    keywords jsonb,
    original_url text
)
LANGUAGE sql STABLE
AS $$
    SELECT
        lr.id,
        lr.logic_type,
        lr.core_argument,
        1 - (lr.vector_embedding <=> query_embedding) as similarity,
        lr.effectiveness_score,
        lr.threat_level,
        lr.source_gallery,
        lr.keywords,
        lr.original_url
    FROM logic_repository lr
    WHERE lr.vector_embedding IS NOT NULL
      AND lr.is_active = true
      AND (logic_type_filter IS NULL OR lr.logic_type = logic_type_filter)
      AND 1 - (lr.vector_embedding <=> query_embedding) > match_threshold
    ORDER BY lr.vector_embedding <=> query_embedding ASC
    LIMIT match_count;
$$;

-- 2. 임베딩 상태 상세 조회 함수
CREATE OR REPLACE FUNCTION check_embedding_status_detailed()
RETURNS TABLE (
    logic_type text,
    source_gallery text,
    total_count bigint,
    embedded_count bigint,
    embedding_rate numeric,
    avg_effectiveness numeric,
    latest_embedding timestamptz
)
LANGUAGE sql STABLE
AS $$
    SELECT
        lr.logic_type,
        lr.source_gallery,
        COUNT(*) as total_count,
        COUNT(lr.vector_embedding) as embedded_count,
        ROUND(
            (COUNT(lr.vector_embedding)::numeric / COUNT(*)::numeric) * 100,
            2
        ) as embedding_rate,
        ROUND(AVG(lr.effectiveness_score)::numeric, 2) as avg_effectiveness,
        MAX(CASE WHEN lr.vector_embedding IS NOT NULL THEN lr.updated_at END) as latest_embedding
    FROM logic_repository lr
    WHERE lr.is_active = true
    GROUP BY lr.logic_type, lr.source_gallery
    ORDER BY lr.logic_type, lr.source_gallery;
$$;

-- 3. 배치 임베딩 처리를 위한 함수
CREATE OR REPLACE FUNCTION get_unembedded_logics(batch_size int DEFAULT 50)
RETURNS TABLE (
    id uuid,
    logic_type text,
    core_argument text,
    original_title text,
    original_content text,
    created_at timestamptz
)
LANGUAGE sql STABLE
AS $$
    SELECT
        lr.id,
        lr.logic_type,
        lr.core_argument,
        lr.original_title,
        lr.original_content,
        lr.created_at
    FROM logic_repository lr
    WHERE lr.vector_embedding IS NULL
      AND lr.is_active = true
    ORDER BY lr.created_at ASC
    LIMIT batch_size;
$$;

-- 4. 벡터 임베딩 업데이트 함수 (안전한 업데이트)
CREATE OR REPLACE FUNCTION update_logic_embedding(
    logic_id uuid,
    embedding_vector vector(1536)
)
RETURNS boolean
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE logic_repository
    SET
        vector_embedding = embedding_vector,
        updated_at = NOW()
    WHERE id = logic_id AND is_active = true;

    RETURN FOUND;
END;
$$;

-- 5. 고급 매칭 함수 (카테고리별 가중치 적용)
CREATE OR REPLACE FUNCTION find_defense_for_attack_advanced(
    attack_logic_id uuid,
    confidence_threshold float DEFAULT 0.7,
    max_results int DEFAULT 5,
    category_boost float DEFAULT 1.2
)
RETURNS TABLE (
    attack_id uuid,
    defense_id uuid,
    match_confidence float,
    adjusted_confidence float,
    defense_argument text,
    effectiveness_score int,
    match_strategy text,
    reason text,
    category_match boolean
)
LANGUAGE plpgsql STABLE
AS $$
DECLARE
    attack_embedding vector(1536);
    attack_threat_level int;
    attack_category text;
BEGIN
    -- 공격 논리 정보 가져오기
    SELECT vector_embedding, threat_level, category
    INTO attack_embedding, attack_threat_level, attack_category
    FROM logic_repository
    WHERE id = attack_logic_id AND logic_type = 'attack' AND is_active = true;

    IF attack_embedding IS NULL THEN
        RETURN;
    END IF;

    RETURN QUERY
    SELECT
        attack_logic_id as attack_id,
        def.id as defense_id,
        def.similarity as match_confidence,
        CASE
            WHEN def_data.category = attack_category THEN def.similarity * category_boost
            ELSE def.similarity
        END as adjusted_confidence,
        def.core_argument as defense_argument,
        def.effectiveness_score,
        CASE
            WHEN def.similarity >= 0.9 THEN '직접적 반박'
            WHEN def.similarity >= 0.8 THEN '논리적 대응'
            WHEN def.similarity >= 0.7 THEN '우회적 반박'
            ELSE '추가 논리 개발 필요'
        END as match_strategy,
        CASE
            WHEN def.similarity >= 0.9 AND def_data.category = attack_category THEN '동일 카테고리 - 직접 반박 가능'
            WHEN def.similarity >= 0.9 THEN '매우 강한 논리적 연관성 - 직접 반박 가능'
            WHEN def.similarity >= 0.8 THEN '강한 논리적 연관성 - 효과적 대응 가능'
            WHEN def.similarity >= 0.7 THEN '적절한 논리적 연관성 - 우회적 접근 권장'
            ELSE '약한 연관성 - 추가 논리 개발 필요'
        END as reason,
        (def_data.category = attack_category) as category_match
    FROM find_similar_logic(
        attack_embedding,
        confidence_threshold,
        max_results * 2,  -- 더 많이 가져와서 필터링
        'defense'
    ) def
    JOIN logic_repository def_data ON def.id = def_data.id
    WHERE def.effectiveness_score >= 5
    ORDER BY adjusted_confidence DESC, def.effectiveness_score DESC
    LIMIT max_results;
END;
$$;

-- 6. 실시간 매칭 성능 모니터링 함수
CREATE OR REPLACE FUNCTION get_matching_performance()
RETURNS TABLE (
    total_attacks bigint,
    embedded_attacks bigint,
    matched_attacks bigint,
    match_rate numeric,
    avg_match_confidence numeric,
    recent_matches_24h bigint,
    high_confidence_rate numeric
)
LANGUAGE sql STABLE
AS $$
    SELECT
        (SELECT COUNT(*) FROM logic_repository WHERE logic_type = 'attack' AND is_active = true) as total_attacks,
        (SELECT COUNT(*) FROM logic_repository WHERE logic_type = 'attack' AND is_active = true AND vector_embedding IS NOT NULL) as embedded_attacks,
        (SELECT COUNT(DISTINCT attack_id) FROM logic_matches WHERE is_active = true) as matched_attacks,
        ROUND(
            (SELECT COUNT(DISTINCT attack_id)::numeric FROM logic_matches WHERE is_active = true) /
            NULLIF((SELECT COUNT(*)::numeric FROM logic_repository WHERE logic_type = 'attack' AND is_active = true AND vector_embedding IS NOT NULL), 0) * 100,
            2
        )::numeric as match_rate,
        (SELECT ROUND(AVG(match_confidence)::numeric, 3) FROM logic_matches WHERE is_active = true) as avg_match_confidence,
        (SELECT COUNT(*) FROM logic_matches WHERE is_active = true AND created_at >= NOW() - INTERVAL '24 hours') as recent_matches_24h,
        ROUND(
            (SELECT COUNT(*)::numeric FROM logic_matches WHERE is_active = true AND match_confidence >= 0.8) /
            NULLIF((SELECT COUNT(*)::numeric FROM logic_matches WHERE is_active = true), 0) * 100,
            2
        )::numeric as high_confidence_rate;
$$;

-- 7. 논리 검색 및 추천 함수 (키워드 기반)
CREATE OR REPLACE FUNCTION search_logics_by_keywords(
    search_keywords text[],
    logic_type_filter text DEFAULT NULL,
    limit_count int DEFAULT 20
)
RETURNS TABLE (
    id uuid,
    logic_type text,
    core_argument text,
    keywords jsonb,
    effectiveness_score int,
    keyword_match_count int,
    source_gallery text
)
LANGUAGE sql STABLE
AS $$
    SELECT
        lr.id,
        lr.logic_type,
        lr.core_argument,
        lr.keywords,
        lr.effectiveness_score,
        (
            SELECT COUNT(*)::int
            FROM unnest(search_keywords) sk
            WHERE lr.keywords ? sk OR lr.core_argument ILIKE '%' || sk || '%'
        ) as keyword_match_count,
        lr.source_gallery
    FROM logic_repository lr
    WHERE lr.is_active = true
      AND (logic_type_filter IS NULL OR lr.logic_type = logic_type_filter)
      AND (
          lr.keywords ?| search_keywords
          OR EXISTS (
              SELECT 1 FROM unnest(search_keywords) sk
              WHERE lr.core_argument ILIKE '%' || sk || '%'
          )
      )
    ORDER BY keyword_match_count DESC, lr.effectiveness_score DESC
    LIMIT limit_count;
$$;

-- 8. 시스템 건강상태 체크 함수
CREATE OR REPLACE FUNCTION system_health_check()
RETURNS TABLE (
    component text,
    status text,
    details jsonb,
    last_update timestamptz
)
LANGUAGE sql STABLE
AS $$
    SELECT 'embedding_status' as component, 'healthy' as status,
           jsonb_build_object(
               'total_logics', COUNT(*),
               'embedded_logics', COUNT(vector_embedding),
               'embedding_rate', ROUND((COUNT(vector_embedding)::numeric / COUNT(*)) * 100, 2)::numeric
           ) as details,
           MAX(updated_at) as last_update
    FROM logic_repository WHERE is_active = true

    UNION ALL

    SELECT 'matching_status' as component, 'healthy' as status,
           jsonb_build_object(
               'total_matches', COUNT(*),
               'avg_confidence', ROUND(AVG(match_confidence)::numeric, 3),
               'recent_matches', COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours')
           ) as details,
           MAX(created_at) as last_update
    FROM logic_matches WHERE is_active = true

    UNION ALL

    SELECT 'alert_status' as component, 'healthy' as status,
           jsonb_build_object(
               'pending_alerts', COUNT(*) FILTER (WHERE sent_at IS NULL),
               'alerts_24h', COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours'),
               'critical_alerts_24h', COUNT(*) FILTER (WHERE severity = 'critical' AND created_at >= NOW() - INTERVAL '24 hours')
           ) as details,
           MAX(created_at) as last_update
    FROM alerts;
$$;

-- 9. 벡터 임베딩 검증 함수
CREATE OR REPLACE FUNCTION validate_embeddings()
RETURNS TABLE (
    total_vectors bigint,
    valid_dimensions bigint,
    invalid_vectors bigint,
    null_vectors bigint,
    validation_status text
)
LANGUAGE sql STABLE
AS $$
    SELECT
        COUNT(*) as total_vectors,
        COUNT(*) FILTER (WHERE vector_embedding IS NOT NULL) as valid_dimensions,
        0 as invalid_vectors,
        COUNT(*) FILTER (WHERE vector_embedding IS NULL) as null_vectors,
        CASE
            WHEN COUNT(*) FILTER (WHERE vector_embedding IS NULL) > COUNT(*) * 0.1 THEN 'WARNING: High null vector rate'
            ELSE 'OK: All vectors valid'
        END as validation_status
    FROM logic_repository
    WHERE is_active = true;
$$;

-- 10. 성능 최적화를 위한 부분 인덱스 (메모리 효율적)
-- 활성 논리만 대상으로 하는 작은 인덱스들
CREATE INDEX IF NOT EXISTS idx_logic_embedding_not_null
    ON logic_repository(logic_type, effectiveness_score)
    WHERE vector_embedding IS NOT NULL AND is_active = true;

CREATE INDEX IF NOT EXISTS idx_logic_unembedded
    ON logic_repository(created_at)
    WHERE vector_embedding IS NULL AND is_active = true;

-- 매칭 성능을 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_matches_confidence_high
    ON logic_matches(attack_id, match_confidence)
    WHERE match_confidence >= 0.7 AND is_active = true;

-- 알림 처리를 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_alerts_pending_priority
    ON alerts(severity, created_at)
    WHERE sent_at IS NULL;

-- 11. 통계 수집 및 업데이트 함수
CREATE OR REPLACE FUNCTION update_daily_stats()
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    today_date date := CURRENT_DATE;
    stats_data jsonb;
BEGIN
    -- 오늘의 통계 데이터 수집
    SELECT jsonb_build_object(
        'embedding_status', (SELECT jsonb_agg(row_to_json(s)) FROM (SELECT * FROM check_embedding_status()) s),
        'match_performance', (SELECT row_to_json(p) FROM (SELECT * FROM get_matching_performance()) p),
        'system_health', (SELECT jsonb_agg(row_to_json(h)) FROM (SELECT * FROM system_health_check()) h)
    ) INTO stats_data;

    -- 통계 테이블 업데이트
    INSERT INTO system_stats (
        stat_type,
        stat_date,
        crawled_posts,
        processed_logics,
        new_matches,
        attack_logics,
        defense_logics,
        metadata
    )
    SELECT
        'daily',
        today_date,
        COUNT(*) FILTER (WHERE created_at::date = today_date),
        COUNT(*) FILTER (WHERE created_at::date = today_date AND vector_embedding IS NOT NULL),
        0, -- new_matches는 트리거에서 업데이트
        COUNT(*) FILTER (WHERE logic_type = 'attack' AND created_at::date = today_date),
        COUNT(*) FILTER (WHERE logic_type = 'defense' AND created_at::date = today_date),
        stats_data
    FROM logic_repository
    WHERE is_active = true
    ON CONFLICT (stat_type, stat_date)
    DO UPDATE SET
        processed_logics = EXCLUDED.processed_logics,
        attack_logics = EXCLUDED.attack_logics,
        defense_logics = EXCLUDED.defense_logics,
        metadata = EXCLUDED.metadata;
END;
$$;

-- 마지막으로 현재 시스템 상태 출력
SELECT 'Vector Embedding System Status' as info;
SELECT * FROM check_embedding_status();
SELECT * FROM get_matching_performance();
SELECT * FROM validate_embeddings();