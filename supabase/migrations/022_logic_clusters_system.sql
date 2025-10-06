-- Logic Clusters System: 맥락/이슈별 논리 그룹화

-- 1. 클러스터 테이블 생성
CREATE TABLE IF NOT EXISTS logic_clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 클러스터 정보
    cluster_name TEXT NOT NULL,  -- "2025년 한미정상회담 관련 논리들"
    context_issue TEXT NOT NULL,  -- "2025년 한미정상회담"
    common_distortion_pattern TEXT,  -- "맥락 제거 + 과장"

    -- 통계
    logic_count INTEGER DEFAULT 0,
    threat_level_avg NUMERIC(3,1) DEFAULT 0,

    -- 시간 정보
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),

    -- 상태
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. logic_repository에 cluster_id 추가
ALTER TABLE logic_repository
ADD COLUMN IF NOT EXISTS cluster_id UUID REFERENCES logic_clusters(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_logic_repository_cluster_id ON logic_repository(cluster_id);
CREATE INDEX IF NOT EXISTS idx_logic_clusters_context_issue ON logic_clusters(context_issue);

-- 3. 클러스터 통계 자동 업데이트 함수
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

    RETURN NEW;
END;
$$;

-- 4. 트리거 생성
DROP TRIGGER IF EXISTS trigger_update_cluster_stats ON logic_repository;
CREATE TRIGGER trigger_update_cluster_stats
    AFTER INSERT OR UPDATE ON logic_repository
    FOR EACH ROW
    WHEN (NEW.cluster_id IS NOT NULL)
    EXECUTE FUNCTION update_cluster_stats();

-- 5. 클러스터별 논리 조회 뷰
CREATE OR REPLACE VIEW cluster_with_logics AS
SELECT
    c.id as cluster_id,
    c.cluster_name,
    c.context_issue,
    c.common_distortion_pattern,
    c.logic_count,
    c.threat_level_avg,
    c.first_seen,
    c.last_seen,
    json_agg(
        json_build_object(
            'id', l.id,
            'core_argument', l.core_argument,
            'keywords', l.keywords,
            'threat_level', l.threat_level,
            'distortion_pattern', l.distortion_pattern,
            'original_title', l.original_title,
            'original_content', l.original_content,
            'original_url', l.original_url,
            'created_at', l.created_at
        ) ORDER BY l.created_at ASC
    ) as logics
FROM logic_clusters c
LEFT JOIN logic_repository l ON c.id = l.cluster_id AND l.is_active = true
WHERE c.is_active = true
GROUP BY c.id, c.cluster_name, c.context_issue, c.common_distortion_pattern,
         c.logic_count, c.threat_level_avg, c.first_seen, c.last_seen
ORDER BY c.last_seen DESC;

-- 6. 클러스터 검색/매칭 함수
CREATE OR REPLACE FUNCTION find_or_create_cluster(
    p_context_issue TEXT,
    p_distortion_pattern TEXT DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_cluster_id UUID;
    v_cluster_name TEXT;
BEGIN
    -- 동일한 context_issue의 클러스터 찾기
    SELECT id INTO v_cluster_id
    FROM logic_clusters
    WHERE context_issue = p_context_issue
      AND is_active = true
    LIMIT 1;

    -- 없으면 새로 생성
    IF v_cluster_id IS NULL THEN
        v_cluster_name := p_context_issue || ' 관련 논리들';

        INSERT INTO logic_clusters (
            cluster_name,
            context_issue,
            common_distortion_pattern,
            logic_count
        ) VALUES (
            v_cluster_name,
            p_context_issue,
            p_distortion_pattern,
            0
        )
        RETURNING id INTO v_cluster_id;
    END IF;

    RETURN v_cluster_id;
END;
$$;

-- 7. 논리를 클러스터에 자동 할당하는 함수
CREATE OR REPLACE FUNCTION auto_assign_logic_to_cluster()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_cluster_id UUID;
BEGIN
    -- context_issue가 있는 경우에만 클러스터링
    IF NEW.context_issue IS NOT NULL AND NEW.context_issue != '' THEN
        -- 클러스터 찾기 또는 생성
        v_cluster_id := find_or_create_cluster(
            NEW.context_issue,
            NEW.distortion_pattern
        );

        -- 논리에 클러스터 할당
        NEW.cluster_id := v_cluster_id;
    END IF;

    RETURN NEW;
END;
$$;

-- 8. 자동 클러스터 할당 트리거
DROP TRIGGER IF EXISTS trigger_auto_assign_cluster ON logic_repository;
CREATE TRIGGER trigger_auto_assign_cluster
    BEFORE INSERT ON logic_repository
    FOR EACH ROW
    EXECUTE FUNCTION auto_assign_logic_to_cluster();

DO $$
BEGIN
  RAISE NOTICE '✅ Logic Clusters System installed successfully!';
  RAISE NOTICE '📊 Clusters will be automatically created based on context_issue';
  RAISE NOTICE '🔗 Logics will be grouped by common context/issue';
END $$;