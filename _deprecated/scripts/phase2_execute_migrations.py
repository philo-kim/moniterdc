"""
Phase 2: DB 스키마 생성 (자동 실행)

Supabase REST API를 통해 직접 테이블 생성
"""

from engines.utils.supabase_client import get_supabase
import os

def execute_migration():
    print("="*80)
    print("Phase 2: DB 스키마 생성")
    print("="*80)

    supabase = get_supabase()

    # Migration 201: layered_perceptions
    print("\n[2.1] layered_perceptions 테이블 생성")
    print("-"*80)

    migration_201 = """
CREATE TABLE IF NOT EXISTS layered_perceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES contents(id) ON DELETE CASCADE,
    explicit_claims JSONB DEFAULT '[]'::jsonb,
    implicit_assumptions JSONB DEFAULT '[]'::jsonb,
    reasoning_gaps JSONB DEFAULT '[]'::jsonb,
    deep_beliefs TEXT[] DEFAULT '{}',
    worldview_hints TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_layered_perceptions_content ON layered_perceptions(content_id);
CREATE INDEX IF NOT EXISTS idx_layered_perceptions_beliefs ON layered_perceptions USING GIN(deep_beliefs);
CREATE INDEX IF NOT EXISTS idx_layered_perceptions_created ON layered_perceptions(created_at DESC);
"""

    try:
        # Supabase에서는 직접 SQL 실행이 제한되므로,
        # 테이블이 없으면 insert를 시도해서 확인
        test = supabase.table('layered_perceptions').select('id').limit(1).execute()
        print("✅ layered_perceptions 테이블 이미 존재")
    except Exception as e:
        if 'relation' in str(e).lower() and 'does not exist' in str(e).lower():
            print("❌ layered_perceptions 테이블 없음")
            print("\n다음 SQL을 Supabase Dashboard에서 실행하세요:")
            print("-"*80)
            print(migration_201)
            print("-"*80)
            return False
        else:
            print(f"⚠️ 확인 중 오류: {e}")

    # Migration 202: belief_patterns
    print("\n[2.2] belief_patterns 테이블 생성")
    print("-"*80)

    migration_202 = """
CREATE TABLE IF NOT EXISTS belief_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    belief TEXT UNIQUE NOT NULL,
    frequency INTEGER DEFAULT 0,
    percentage REAL DEFAULT 0.0,
    co_occurring_beliefs JSONB DEFAULT '{}'::jsonb,
    generated_thoughts TEXT[] DEFAULT '{}',
    manifested_claims TEXT[] DEFAULT '{}',
    cluster_id UUID,
    cluster_name TEXT,
    example_content_ids UUID[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_belief_patterns_frequency ON belief_patterns(frequency DESC);
CREATE INDEX IF NOT EXISTS idx_belief_patterns_percentage ON belief_patterns(percentage DESC);
CREATE INDEX IF NOT EXISTS idx_belief_patterns_cluster ON belief_patterns(cluster_id);
"""

    try:
        test = supabase.table('belief_patterns').select('id').limit(1).execute()
        print("✅ belief_patterns 테이블 이미 존재")
    except Exception as e:
        if 'relation' in str(e).lower() and 'does not exist' in str(e).lower():
            print("❌ belief_patterns 테이블 없음")
            print("\n다음 SQL을 Supabase Dashboard에서 실행하세요:")
            print("-"*80)
            print(migration_202)
            print("-"*80)
            return False
        else:
            print(f"⚠️ 확인 중 오류: {e}")

    print("\n" + "="*80)
    print("✅ Phase 2 완료")
    print("="*80)
    print("\n다음 단계: Phase 3 (3층 구조 분석)")
    print("="*80)

    return True

if __name__ == '__main__':
    # Supabase REST API로는 직접 CREATE TABLE 불가능
    # PostgreSQL 클라이언트 필요

    print("⚠️ Supabase REST API로는 CREATE TABLE을 직접 실행할 수 없습니다.")
    print("\n대안 방법:")
    print("1. Supabase Dashboard SQL Editor 사용 (권장)")
    print("2. psycopg2로 직접 연결")
    print("\npsycopg2 방법을 시도합니다...\n")

    try:
        import psycopg2

        # Supabase PostgreSQL 연결 정보
        conn = psycopg2.connect(
            host="aws-0-ap-northeast-2.pooler.supabase.com",
            database="postgres",
            user="postgres.ycmcsdbxnpmthekzyppl",
            password=os.getenv('SUPABASE_DB_PASSWORD', ''),  # 환경변수 필요
            port=6543
        )

        print("✅ PostgreSQL 연결 성공")

        cursor = conn.cursor()

        # Migration 201
        print("\n[201] layered_perceptions 생성 중...")
        with open('supabase/migrations/201_create_layered_perceptions.sql', 'r') as f:
            cursor.execute(f.read())
        print("✅ 완료")

        # Migration 202
        print("\n[202] belief_patterns 생성 중...")
        with open('supabase/migrations/202_create_belief_patterns.sql', 'r') as f:
            cursor.execute(f.read())
        print("✅ 완료")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "="*80)
        print("✅ Phase 2 완료 - 테이블 생성 성공")
        print("="*80)

    except ImportError:
        print("\n❌ psycopg2가 설치되지 않았습니다.")
        print("\n설치: pip3 install psycopg2-binary")
        print("\n또는 Supabase Dashboard에서 수동 실행:")
        print("  https://supabase.com/dashboard/project/ycmcsdbxnpmthekzyppl/sql")
        execute_migration()
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        print("\nSupabase Dashboard에서 수동 실행이 필요합니다:")
        execute_migration()
