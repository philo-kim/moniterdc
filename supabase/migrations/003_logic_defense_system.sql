-- Logic Defense System v3.0 - Core Functions
-- 공격-방어 논리 매칭 및 벡터 검색 핵심 기능

-- 1. 벡터 유사도 검색 함수
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
    source_gallery text
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
        lr.source_gallery
    FROM logic_repository lr
    WHERE lr.vector_embedding IS NOT NULL
      AND lr.is_active = true
      AND (logic_type_filter IS NULL OR lr.logic_type = logic_type_filter)
      AND 1 - (lr.vector_embedding <=> query_embedding) > match_threshold
    ORDER BY lr.vector_embedding <=> query_embedding ASC
    LIMIT match_count;
$$;

-- 2. 공격에 대한 방어 논리 찾기
CREATE OR REPLACE FUNCTION find_defense_for_attack(
    attack_logic_id uuid,
    confidence_threshold float DEFAULT 0.7,
    max_results int DEFAULT 5
)
RETURNS TABLE (
    attack_id uuid,
    defense_id uuid,
    match_confidence float,
    defense_argument text,
    effectiveness_score int,
    match_strategy text,
    reason text
)
LANGUAGE plpgsql STABLE
AS $$
DECLARE
    attack_embedding vector(1536);
    attack_threat_level int;
BEGIN
    -- 공격 논리의 임베딩과 위협도 가져오기
    SELECT vector_embedding, threat_level
    INTO attack_embedding, attack_threat_level
    FROM logic_repository
    WHERE id = attack_logic_id AND logic_type = 'attack' AND is_active = true;

    -- 임베딩이 없으면 종료
    IF attack_embedding IS NULL THEN
        RETURN;
    END IF;

    -- 유사한 방어 논리 검색
    RETURN QUERY
    SELECT
        attack_logic_id as attack_id,
        def.id as defense_id,
        similarity as match_confidence,
        def.core_argument as defense_argument,
        def.effectiveness_score,
        CASE
            WHEN similarity >= 0.9 THEN '직접적 반박'
            WHEN similarity >= 0.8 THEN '논리적 대응'
            WHEN similarity >= 0.7 THEN '우회적 반박'
            ELSE '추가 논리 개발 필요'
        END as match_strategy,
        CASE
            WHEN similarity >= 0.9 THEN '매우 강한 논리적 연관성 - 직접 반박 가능'
            WHEN similarity >= 0.8 THEN '강한 논리적 연관성 - 효과적 대응 가능'
            WHEN similarity >= 0.7 THEN '적절한 논리적 연관성 - 우회적 접근 권장'
            ELSE '약한 연관성 - 추가 논리 개발 필요'
        END as reason
    FROM find_similar_logic(
        attack_embedding,
        confidence_threshold,
        max_results,
        'defense'
    ) def
    WHERE def.effectiveness_score >= 5  -- 최소 효과성 보장
    ORDER BY match_confidence DESC, def.effectiveness_score DESC;
END;
$$;

-- 3. 자동 매칭 및 저장 함수
CREATE OR REPLACE FUNCTION auto_match_attack_with_defense(attack_logic_id uuid)
RETURNS int
LANGUAGE plpgsql
AS $$
DECLARE
    match_record RECORD;
    inserted_count int := 0;
BEGIN
    -- 기존 매칭이 있는지 확인
    IF EXISTS (
        SELECT 1 FROM logic_matches
        WHERE attack_id = attack_logic_id AND is_active = true
    ) THEN
        -- 이미 매칭되어 있으면 0 반환
        RETURN 0;
    END IF;

    -- 방어 논리 찾아서 매칭 테이블에 저장
    FOR match_record IN
        SELECT * FROM find_defense_for_attack(attack_logic_id, 0.7, 3)
    LOOP
        INSERT INTO logic_matches (
            attack_id,
            defense_id,
            match_confidence,
            match_reason,
            match_strategy,
            match_type,
            matcher_version
        ) VALUES (
            match_record.attack_id,
            match_record.defense_id,
            match_record.match_confidence,
            match_record.reason,
            match_record.match_strategy,
            'auto',
            'v3.0'
        )
        ON CONFLICT (attack_id, defense_id) DO NOTHING;

        inserted_count := inserted_count + 1;
    END LOOP;

    RETURN inserted_count;
END;
$$;

-- 4. 임베딩 상태 확인 함수
CREATE OR REPLACE FUNCTION check_embedding_status()
RETURNS TABLE (
    logic_type text,
    total_count bigint,
    embedded_count bigint,
    embedding_rate numeric
)
LANGUAGE sql STABLE
AS $$
    SELECT
        lr.logic_type,
        COUNT(*) as total_count,
        COUNT(lr.vector_embedding) as embedded_count,
        ROUND(
            (COUNT(lr.vector_embedding)::numeric / COUNT(*)::numeric) * 100,
            2
        )::numeric as embedding_rate
    FROM logic_repository lr
    WHERE lr.is_active = true
    GROUP BY lr.logic_type
    ORDER BY lr.logic_type;
$$;

-- 5. 매칭 결과 요약 함수
CREATE OR REPLACE FUNCTION get_match_summary()
RETURNS TABLE (
    total_attacks bigint,
    matched_attacks bigint,
    total_matches bigint,
    avg_confidence numeric,
    high_confidence_matches bigint
)
LANGUAGE sql STABLE
AS $$
    SELECT
        (SELECT COUNT(*) FROM logic_repository WHERE logic_type = 'attack' AND is_active = true) as total_attacks,
        (SELECT COUNT(DISTINCT attack_id) FROM logic_matches WHERE is_active = true) as matched_attacks,
        (SELECT COUNT(*) FROM logic_matches WHERE is_active = true) as total_matches,
        (SELECT ROUND(AVG(match_confidence)::numeric, 3) FROM logic_matches WHERE is_active = true) as avg_confidence,
        (SELECT COUNT(*) FROM logic_matches WHERE match_confidence >= 0.8 AND is_active = true) as high_confidence_matches;
$$;

-- 6. 새로운 공격 논리 감지 시 자동 매칭 트리거
CREATE OR REPLACE FUNCTION trigger_auto_match_on_new_attack()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    match_count int;
    alert_id uuid;
BEGIN
    -- 새로운 공격 논리이고 임베딩이 있는 경우에만 매칭 시도
    IF NEW.logic_type = 'attack' AND NEW.vector_embedding IS NOT NULL THEN
        -- 자동 매칭 실행
        SELECT auto_match_attack_with_defense(NEW.id) INTO match_count;

        -- 매칭 결과에 따라 알림 생성
        IF match_count > 0 THEN
            -- 매칭 성공 알림
            INSERT INTO alerts (
                alert_type,
                severity,
                title,
                message,
                metadata
            ) VALUES (
                'auto_match',
                CASE
                    WHEN NEW.threat_level >= 8 THEN 'high'
                    WHEN NEW.threat_level >= 6 THEN 'medium'
                    ELSE 'low'
                END,
                '🤖 새로운 공격 논리 자동 매칭 완료',
                format('새로운 공격 논리에 대해 %s개의 방어 논리를 자동 매칭했습니다.', match_count),
                jsonb_build_object(
                    'attack_id', NEW.id,
                    'match_count', match_count,
                    'threat_level', NEW.threat_level,
                    'auto_matched', true
                )
            ) RETURNING id INTO alert_id;
        ELSE
            -- 매칭 실패 알림 (위협도가 높은 경우에만)
            IF NEW.threat_level >= 7 THEN
                INSERT INTO alerts (
                    alert_type,
                    severity,
                    title,
                    message,
                    metadata
                ) VALUES (
                    'new_attack',
                    'high',
                    '⚠️ 새로운 공격 논리 감지 - 대응 논리 없음',
                    format('위협도 %s/10의 새로운 공격 논리가 감지되었으나 적절한 방어 논리를 찾지 못했습니다.', NEW.threat_level),
                    jsonb_build_object(
                        'attack_id', NEW.id,
                        'threat_level', NEW.threat_level,
                        'requires_manual_review', true
                    )
                ) RETURNING id INTO alert_id;
            END IF;
        END IF;

        -- 통계 업데이트
        INSERT INTO system_stats (stat_type, stat_date, new_matches, attack_logics)
        VALUES ('daily', CURRENT_DATE, match_count, 1)
        ON CONFLICT (stat_type, stat_date)
        DO UPDATE SET
            new_matches = system_stats.new_matches + EXCLUDED.new_matches,
            attack_logics = system_stats.attack_logics + EXCLUDED.attack_logics;
    END IF;

    RETURN NEW;
END;
$$;

-- 트리거 생성
DROP TRIGGER IF EXISTS auto_match_new_attack ON logic_repository;
CREATE TRIGGER auto_match_new_attack
    AFTER INSERT ON logic_repository
    FOR EACH ROW
    EXECUTE FUNCTION trigger_auto_match_on_new_attack();

-- 7. 방어 논리 임베딩 업데이트 시 재매칭 트리거
CREATE OR REPLACE FUNCTION trigger_rematch_on_defense_embedding()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    unmatched_attacks RECORD;
    total_new_matches int := 0;
    match_count int;
BEGIN
    -- 방어 논리의 임베딩이 새로 추가된 경우
    IF NEW.logic_type = 'defense' AND OLD.vector_embedding IS NULL AND NEW.vector_embedding IS NOT NULL THEN
        -- 매칭되지 않은 공격들에 대해 재매칭 시도
        FOR unmatched_attacks IN
            SELECT DISTINCT lr.id as attack_id
            FROM logic_repository lr
            LEFT JOIN logic_matches lm ON lr.id = lm.attack_id AND lm.is_active = true
            WHERE lr.logic_type = 'attack'
              AND lr.vector_embedding IS NOT NULL
              AND lr.is_active = true
              AND lm.attack_id IS NULL
        LOOP
            SELECT auto_match_attack_with_defense(unmatched_attacks.attack_id) INTO match_count;
            total_new_matches := total_new_matches + match_count;
        END LOOP;

        -- 새로운 매칭이 생성된 경우 알림
        IF total_new_matches > 0 THEN
            INSERT INTO alerts (
                alert_type,
                severity,
                title,
                message,
                metadata
            ) VALUES (
                'auto_match',
                'medium',
                '🛡️ 새로운 방어 논리로 추가 매칭 완료',
                format('새로운 방어 논리 추가로 %s개의 추가 매칭이 생성되었습니다.', total_new_matches),
                jsonb_build_object(
                    'defense_id', NEW.id,
                    'new_matches', total_new_matches
                )
            );
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

-- 트리거 생성
DROP TRIGGER IF EXISTS rematch_on_defense_embedding ON logic_repository;
CREATE TRIGGER rematch_on_defense_embedding
    AFTER UPDATE ON logic_repository
    FOR EACH ROW
    EXECUTE FUNCTION trigger_rematch_on_defense_embedding();