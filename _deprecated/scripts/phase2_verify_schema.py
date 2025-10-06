"""
Phase 2: DB 스키마 검증

Supabase Dashboard에서 마이그레이션 실행 후 확인
"""

from engines.utils.supabase_client import get_supabase

def verify_schema():
    print("="*80)
    print("Phase 2: DB 스키마 검증")
    print("="*80)

    supabase = get_supabase()

    print("\n테이블 존재 확인:")
    print("-"*80)

    # layered_perceptions 확인
    try:
        result = supabase.table('layered_perceptions').select('id').limit(0).execute()
        print("✅ layered_perceptions 테이블 존재")
    except Exception as e:
        print(f"❌ layered_perceptions 테이블 없음")
        print(f"   에러: {e}")
        print("\n   → Supabase Dashboard SQL Editor에서 201번 마이그레이션 실행 필요")
        return False

    # belief_patterns 확인
    try:
        result = supabase.table('belief_patterns').select('id').limit(0).execute()
        print("✅ belief_patterns 테이블 존재")
    except Exception as e:
        print(f"❌ belief_patterns 테이블 없음")
        print(f"   에러: {e}")
        print("\n   → Supabase Dashboard SQL Editor에서 202번 마이그레이션 실행 필요")
        return False

    print("\n" + "="*80)
    print("✅ Phase 2 완료")
    print("="*80)
    print("\n다음 단계: Phase 3 (3층 구조 분석)")
    print("  실행: python3 phase3_layered_analysis.py")
    print("="*80)

    return True

if __name__ == '__main__':
    verify_schema()
