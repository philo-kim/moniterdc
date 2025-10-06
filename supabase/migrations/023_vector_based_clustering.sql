-- Vector-based clustering: 벡터 유사도로 논리 그룹화

-- 1. 클러스터에 대표 벡터 추가
ALTER TABLE logic_clusters
ADD COLUMN IF NOT EXISTS representative_embedding vector(1536);

COMMENT ON COLUMN logic_clusters.representative_embedding IS '클러스터 대표 벡터 (클러스터 내 모든 논리의 평균 벡터)';

-- 2. 클러스터 대표 벡터 업데이트 함수
CREATE OR REPLACE FUNCTION update_cluster_representative_embedding(p_cluster_id UUID)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_avg_embedding vector(1536);
BEGIN
    -- 클러스터 내 모든 논리의 평균 벡터 계산
    SELECT AVG(vector_embedding)::vector(1536)
    INTO v_avg_embedding
    FROM logic_repository
    WHERE cluster_id = p_cluster_id
      AND vector_embedding IS NOT NULL
      AND is_active = true;

    -- 클러스터 대표 벡터 업데이트
    IF v_avg_embedding IS NOT NULL THEN
        UPDATE logic_clusters
        SET representative_embedding = v_avg_embedding,
            updated_at = NOW()
        WHERE id = p_cluster_id;
    END IF;
END;
$$;

-- 3. 벡터 유사도로 클러스터 찾기
CREATE OR REPLACE FUNCTION find_similar_cluster(
    p_embedding vector(1536),
    p_similarity_threshold float DEFAULT 0.75
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_cluster_id UUID;
    v_max_similarity float;
BEGIN
    -- 가장 유사한 클러스터 찾기
    SELECT
        id,
        1 - (representative_embedding <=> p_embedding) as similarity
    INTO v_cluster_id, v_max_similarity
    FROM logic_clusters
    WHERE representative_embedding IS NOT NULL
      AND is_active = true
    ORDER BY representative_embedding <=> p_embedding ASC
    LIMIT 1;

    -- 유사도가 임계값 이상이면 해당 클러스터 반환
    IF v_max_similarity >= p_similarity_threshold THEN
        RETURN v_cluster_id;
    END IF;

    -- 유사한 클러스터가 없으면 NULL 반환
    RETURN NULL;
END;
$$;

-- 4. 벡터 기반 자동 클러스터 할당 (기존 함수 대체)
CREATE OR REPLACE FUNCTION auto_assign_logic_to_cluster()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_cluster_id UUID;
    v_cluster_name TEXT;
BEGIN
    -- vector_embedding이 있는 경우에만 클러스터링
    IF NEW.vector_embedding IS NOT NULL THEN
        -- 1. 먼저 벡터 유사도로 기존 클러스터 검색
        v_cluster_id := find_similar_cluster(NEW.vector_embedding, 0.75);

        -- 2. 유사한 클러스터가 없으면 context_issue로 검색
        IF v_cluster_id IS NULL AND NEW.context_issue IS NOT NULL AND NEW.context_issue != '' THEN
            SELECT id INTO v_cluster_id
            FROM logic_clusters
            WHERE context_issue = NEW.context_issue
              AND is_active = true
            LIMIT 1;
        END IF;

        -- 3. 여전히 없으면 새 클러스터 생성
        IF v_cluster_id IS NULL THEN
            -- context_issue가 있으면 사용, 없으면 core_argument 사용
            v_cluster_name := COALESCE(
                NEW.context_issue || ' 관련 논리들',
                LEFT(NEW.core_argument, 50) || '... 관련 논리들'
            );

            INSERT INTO logic_clusters (
                cluster_name,
                context_issue,
                common_distortion_pattern,
                representative_embedding,
                logic_count
            ) VALUES (
                v_cluster_name,
                NEW.context_issue,
                NEW.distortion_pattern,
                NEW.vector_embedding,  -- 첫 논리의 벡터를 대표 벡터로
                0
            )
            RETURNING id INTO v_cluster_id;
        END IF;

        -- 4. 논리에 클러스터 할당
        NEW.cluster_id := v_cluster_id;
    END IF;

    RETURN NEW;
END;
$$;

-- 5. 클러스터 통계 업데이트 시 대표 벡터도 업데이트
CREATE OR REPLACE FUNCTION update_cluster_stats()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- 클러스터 통계 업데이트
    UPDATE logic_clusters
    SET
        logic_count = (
            SELECT COUNT(*)
            FROM logic_repository
            WHERE cluster_id = NEW.cluster_id AND is_active = true
        ),
        threat_level_avg = (
            SELECT AVG(threat_level)::numeric(3,1)
            FROM logic_repository
            WHERE cluster_id = NEW.cluster_id AND is_active = true
        ),
        last_seen = NOW(),
        updated_at = NOW()
    WHERE id = NEW.cluster_id;

    -- 대표 벡터 업데이트 (2개 이상 논리가 있을 때만)
    IF (SELECT logic_count FROM logic_clusters WHERE id = NEW.cluster_id) >= 2 THEN
        PERFORM update_cluster_representative_embedding(NEW.cluster_id);
    END IF;

    RETURN NEW;
END;
$$;

-- 6. 기존 트리거 재생성 (함수가 업데이트되었으므로)
DROP TRIGGER IF EXISTS trigger_auto_assign_cluster ON logic_repository;
CREATE TRIGGER trigger_auto_assign_cluster
    BEFORE INSERT ON logic_repository
    FOR EACH ROW
    EXECUTE FUNCTION auto_assign_logic_to_cluster();

DROP TRIGGER IF EXISTS trigger_update_cluster_stats ON logic_repository;
CREATE TRIGGER trigger_update_cluster_stats
    AFTER INSERT OR UPDATE ON logic_repository
    FOR EACH ROW
    WHEN (NEW.cluster_id IS NOT NULL)
    EXECUTE FUNCTION update_cluster_stats();

DO $$
BEGIN
  RAISE NOTICE '✅ Vector-based clustering system installed!';
  RAISE NOTICE '🔍 Logics will be grouped by vector similarity (threshold: 0.75)';
  RAISE NOTICE '📊 Cluster representative embeddings will be updated automatically';
END $$;