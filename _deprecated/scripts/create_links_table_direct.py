"""
perception_worldview_links 테이블 직접 생성
"""

import sys
sys.path.insert(0, '/Users/taehyeonkim/dev/minjoo/moniterdc')
from engines.utils.supabase_client import get_supabase

supabase = get_supabase()

# Create table using raw SQL
sql = """
CREATE TABLE IF NOT EXISTS perception_worldview_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    perception_id UUID REFERENCES layered_perceptions(id) ON DELETE CASCADE,
    worldview_id UUID REFERENCES worldviews(id) ON DELETE CASCADE,
    relevance_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pwlinks_perception ON perception_worldview_links(perception_id);
CREATE INDEX IF NOT EXISTS idx_pwlinks_worldview ON perception_worldview_links(worldview_id);
CREATE INDEX IF NOT EXISTS idx_pwlinks_relevance ON perception_worldview_links(relevance_score DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_pwlinks_unique ON perception_worldview_links(perception_id, worldview_id);
"""

print("perception_worldview_links 테이블 생성 중...")
print("\n다음 SQL을 Supabase SQL Editor에서 실행해주세요:")
print("="*70)
print(sql)
print("="*70)

print("\n\n또는 다음 명령으로 직접 생성:")
print("psql $DATABASE_URL <<EOF")
print(sql)
print("EOF")
