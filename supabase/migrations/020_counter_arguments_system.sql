-- =====================================================
-- Counter Arguments System (크라우드소싱 대응 논리)
-- =====================================================

-- 1. counter_arguments 테이블 생성
CREATE TABLE IF NOT EXISTS counter_arguments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 연결된 공격 논리
    attack_id UUID NOT NULL REFERENCES logic_repository(id) ON DELETE CASCADE,

    -- 대응 논리 내용
    content TEXT NOT NULL,

    -- 소스 타입 (article, video, tweet, custom)
    source_type TEXT CHECK (source_type IN ('article', 'video', 'tweet', 'text', 'other')),

    -- 외부 링크 (선택)
    source_url TEXT,

    -- 링크 메타데이터 (제목, 이미지 등 - JSON)
    link_preview JSONB DEFAULT '{}'::jsonb,

    -- 작성자 정보
    author_name TEXT DEFAULT 'Anonymous',
    author_id UUID,  -- 나중에 인증 추가시 사용

    -- 평가 시스템
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    quality_score NUMERIC(3,2) DEFAULT 0.00,  -- 0.00 ~ 10.00

    -- 상태
    is_verified BOOLEAN DEFAULT FALSE,  -- 관리자 검증
    is_best BOOLEAN DEFAULT FALSE,      -- 베스트 대응
    is_active BOOLEAN DEFAULT TRUE,

    -- 메타
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 인덱스
    CONSTRAINT content_not_empty CHECK (LENGTH(TRIM(content)) > 0)
);

-- 인덱스 생성
CREATE INDEX idx_counter_arguments_attack_id ON counter_arguments(attack_id);
CREATE INDEX idx_counter_arguments_created_at ON counter_arguments(created_at DESC);
CREATE INDEX idx_counter_arguments_quality_score ON counter_arguments(quality_score DESC);
CREATE INDEX idx_counter_arguments_best ON counter_arguments(is_best) WHERE is_best = TRUE;

-- 2. 투표 기록 테이블 (중복 투표 방지)
CREATE TABLE IF NOT EXISTS counter_argument_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    counter_argument_id UUID NOT NULL REFERENCES counter_arguments(id) ON DELETE CASCADE,

    -- 투표자 식별 (임시: IP 또는 세션, 나중에 user_id)
    voter_identifier TEXT NOT NULL,  -- IP 주소 또는 세션 ID

    -- 투표 타입 (1: upvote, -1: downvote)
    vote_type INTEGER CHECK (vote_type IN (1, -1)),

    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- 중복 방지
    UNIQUE(counter_argument_id, voter_identifier)
);

CREATE INDEX idx_votes_counter_argument ON counter_argument_votes(counter_argument_id);

-- 3. updated_at 자동 업데이트 트리거
CREATE OR REPLACE FUNCTION update_counter_arguments_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_counter_arguments_updated_at
    BEFORE UPDATE ON counter_arguments
    FOR EACH ROW
    EXECUTE FUNCTION update_counter_arguments_updated_at();

-- 4. 투표 시 자동으로 quality_score 업데이트하는 함수
CREATE OR REPLACE FUNCTION update_counter_argument_score()
RETURNS TRIGGER AS $$
DECLARE
    total_votes INTEGER;
    up_votes INTEGER;
    down_votes INTEGER;
    calculated_score NUMERIC;
BEGIN
    -- 투표 집계
    SELECT
        COUNT(*) FILTER (WHERE vote_type = 1),
        COUNT(*) FILTER (WHERE vote_type = -1)
    INTO up_votes, down_votes
    FROM counter_argument_votes
    WHERE counter_argument_id = COALESCE(NEW.counter_argument_id, OLD.counter_argument_id);

    total_votes := up_votes + down_votes;

    -- Wilson score 간소화 버전 (0~10 스케일)
    IF total_votes > 0 THEN
        calculated_score := (up_votes::NUMERIC / total_votes) * 10;
    ELSE
        calculated_score := 0;
    END IF;

    -- counter_arguments 테이블 업데이트
    UPDATE counter_arguments
    SET
        upvotes = up_votes,
        downvotes = down_votes,
        quality_score = calculated_score
    WHERE id = COALESCE(NEW.counter_argument_id, OLD.counter_argument_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_score_on_vote
    AFTER INSERT OR DELETE ON counter_argument_votes
    FOR EACH ROW
    EXECUTE FUNCTION update_counter_argument_score();

-- 5. 공격 논리별 베스트 대응 자동 선정 함수
CREATE OR REPLACE FUNCTION update_best_counter_arguments()
RETURNS void AS $$
BEGIN
    -- 모든 공격별로 최고 점수 대응을 is_best = TRUE로 설정
    WITH best_counters AS (
        SELECT DISTINCT ON (attack_id)
            id,
            attack_id
        FROM counter_arguments
        WHERE is_active = TRUE
        ORDER BY attack_id, quality_score DESC, upvotes DESC, created_at ASC
    )
    UPDATE counter_arguments ca
    SET is_best = CASE
        WHEN ca.id IN (SELECT id FROM best_counters) THEN TRUE
        ELSE FALSE
    END;
END;
$$ LANGUAGE plpgsql;

-- 6. 공격 논리에 대응 개수 추가하는 뷰
CREATE OR REPLACE VIEW attack_logic_with_counters AS
SELECT
    lr.*,
    COUNT(ca.id) AS counter_count,
    COUNT(ca.id) FILTER (WHERE ca.is_best = TRUE) AS has_best_counter,
    MAX(ca.quality_score) AS best_counter_score
FROM logic_repository lr
LEFT JOIN counter_arguments ca ON lr.id = ca.attack_id AND ca.is_active = TRUE
WHERE lr.logic_type = 'attack' AND lr.is_active = TRUE
GROUP BY lr.id;

-- 7. RPC: 투표하기
CREATE OR REPLACE FUNCTION vote_counter_argument(
    p_counter_argument_id UUID,
    p_voter_identifier TEXT,
    p_vote_type INTEGER
)
RETURNS JSON AS $$
DECLARE
    v_existing_vote INTEGER;
    v_result JSON;
BEGIN
    -- 기존 투표 확인
    SELECT vote_type INTO v_existing_vote
    FROM counter_argument_votes
    WHERE counter_argument_id = p_counter_argument_id
      AND voter_identifier = p_voter_identifier;

    -- 같은 투표면 취소
    IF v_existing_vote = p_vote_type THEN
        DELETE FROM counter_argument_votes
        WHERE counter_argument_id = p_counter_argument_id
          AND voter_identifier = p_voter_identifier;

        v_result := json_build_object('action', 'removed', 'vote_type', NULL);

    -- 다른 투표면 업데이트
    ELSIF v_existing_vote IS NOT NULL THEN
        UPDATE counter_argument_votes
        SET vote_type = p_vote_type, created_at = NOW()
        WHERE counter_argument_id = p_counter_argument_id
          AND voter_identifier = p_voter_identifier;

        v_result := json_build_object('action', 'updated', 'vote_type', p_vote_type);

    -- 신규 투표
    ELSE
        INSERT INTO counter_argument_votes (counter_argument_id, voter_identifier, vote_type)
        VALUES (p_counter_argument_id, p_voter_identifier, p_vote_type);

        v_result := json_build_object('action', 'created', 'vote_type', p_vote_type);
    END IF;

    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- 8. RPC: 공격 논리의 대응들 조회 (정렬된)
CREATE OR REPLACE FUNCTION get_counter_arguments_for_attack(
    p_attack_id UUID,
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    source_type TEXT,
    source_url TEXT,
    link_preview JSONB,
    author_name TEXT,
    upvotes INTEGER,
    downvotes INTEGER,
    quality_score NUMERIC,
    is_best BOOLEAN,
    is_verified BOOLEAN,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ca.id,
        ca.content,
        ca.source_type,
        ca.source_url,
        ca.link_preview,
        ca.author_name,
        ca.upvotes,
        ca.downvotes,
        ca.quality_score,
        ca.is_best,
        ca.is_verified,
        ca.created_at
    FROM counter_arguments ca
    WHERE ca.attack_id = p_attack_id
      AND ca.is_active = TRUE
    ORDER BY
        ca.is_best DESC,
        ca.quality_score DESC,
        ca.upvotes DESC,
        ca.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- 9. 권한 설정 (Supabase RLS)
ALTER TABLE counter_arguments ENABLE ROW LEVEL SECURITY;
ALTER TABLE counter_argument_votes ENABLE ROW LEVEL SECURITY;

-- 모두 읽기 가능
CREATE POLICY "Public read access" ON counter_arguments
    FOR SELECT USING (is_active = TRUE);

CREATE POLICY "Public read votes" ON counter_argument_votes
    FOR SELECT USING (TRUE);

-- 누구나 작성 가능 (익명)
CREATE POLICY "Anyone can create" ON counter_arguments
    FOR INSERT WITH CHECK (TRUE);

-- 투표도 누구나 가능
CREATE POLICY "Anyone can vote" ON counter_argument_votes
    FOR ALL USING (TRUE);

-- Service role은 모든 권한
CREATE POLICY "Service role all access" ON counter_arguments
    USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Service role votes access" ON counter_argument_votes
    USING (auth.jwt() ->> 'role' = 'service_role');

-- 완료 메시지
DO $$
BEGIN
    RAISE NOTICE '✅ Counter Arguments System 설치 완료!';
    RAISE NOTICE '테이블: counter_arguments, counter_argument_votes';
    RAISE NOTICE '뷰: attack_logic_with_counters';
    RAISE NOTICE 'RPC: vote_counter_argument, get_counter_arguments_for_attack';
END $$;
