-- Allow NULL for context_issue (for old logics without context analysis)

ALTER TABLE logic_clusters
ALTER COLUMN context_issue DROP NOT NULL;

COMMENT ON COLUMN logic_clusters.context_issue IS '관련된 실제 사건/이슈 (NULL 가능 - 구 데이터 호환)';

DO $$
BEGIN
  RAISE NOTICE '✅ context_issue now allows NULL values';
  RAISE NOTICE '🔄 Old logics can now be clustered';
END $$;