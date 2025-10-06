-- Add context and distortion pattern analysis fields to logic_repository

ALTER TABLE logic_repository
ADD COLUMN IF NOT EXISTS context_issue TEXT,
ADD COLUMN IF NOT EXISTS distortion_pattern TEXT;

COMMENT ON COLUMN logic_repository.context_issue IS '관련된 실제 사건/이슈 (GPT 분석)';
COMMENT ON COLUMN logic_repository.distortion_pattern IS '사용된 왜곡 기법 패턴 (GPT 분석)';

-- 기존 레코드는 NULL로 유지 (새로 크롤링되는 것만 채워짐)

DO $$
BEGIN
  RAISE NOTICE '✅ Context analysis fields added to logic_repository';
END $$;