"""
Phase 0: 사전 준비 및 검증

목표:
- 현재 시스템 상태 파악
- 데이터 품질 확인
- API 연결 테스트
"""

import os
from engines.utils.supabase_client import get_supabase
from openai import OpenAI

def check_environment():
    """환경 변수 및 API 연결 확인"""
    print("="*80)
    print("Phase 0: 사전 준비 및 검증")
    print("="*80)

    print("\n[0.1] 환경 변수 확인")
    print("-"*80)

    # OpenAI API Key
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f"✅ OPENAI_API_KEY: {openai_key[:20]}...")
    else:
        print("❌ OPENAI_API_KEY not found")
        return False

    # Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    if supabase_url:
        print(f"✅ SUPABASE_URL: {supabase_url}")
    else:
        print("❌ SUPABASE_URL not found")
        return False

    return True

def check_database():
    """데이터베이스 상태 확인"""
    print("\n[0.2] 데이터베이스 상태 확인")
    print("-"*80)

    supabase = get_supabase()

    # Contents 개수
    try:
        all_contents = supabase.table('contents').select('id', count='exact').execute()
        total = all_contents.count or 0
        print(f"전체 contents: {total}개")

        # 본문 있는 contents
        with_body = supabase.table('contents').select('id', count='exact').neq('body', '').execute()
        body_count = with_body.count or 0
        print(f"본문 있는 contents: {body_count}개")

        if body_count < 50:
            print(f"⚠️ 경고: 본문 있는 글이 {body_count}개로 부족합니다 (최소 50개 권장)")
            print("   → Phase 1에서 데이터 수집 필요")
        else:
            print(f"✅ 충분한 데이터 ({body_count}개)")

        return body_count

    except Exception as e:
        print(f"❌ 데이터베이스 오류: {e}")
        return 0

def check_sample_quality():
    """샘플 데이터 품질 확인"""
    print("\n[0.3] 샘플 데이터 품질 확인")
    print("-"*80)

    supabase = get_supabase()

    # 샘플 10개 가져오기
    samples = supabase.table('contents')\
        .select('id, title, body')\
        .neq('body', '')\
        .limit(10)\
        .execute()

    if not samples.data:
        print("❌ 샘플 데이터 없음")
        return False

    print(f"샘플 {len(samples.data)}개 확인:\n")

    good_count = 0
    for i, content in enumerate(samples.data, 1):
        title = content['title']
        body = content['body']
        body_len = len(body)

        status = "✅" if body_len > 100 else "⚠️"
        print(f"{status} [{i}] {title[:50]}")
        print(f"     본문 길이: {body_len}자")

        if body_len > 100:
            good_count += 1

    print(f"\n품질: {good_count}/10 (본문 100자 이상)")

    if good_count >= 7:
        print("✅ 샘플 품질 양호")
        return True
    else:
        print("⚠️ 샘플 품질 미흡 - 데이터 재수집 권장")
        return False

def test_openai_api():
    """OpenAI API 연결 테스트"""
    print("\n[0.4] OpenAI API 연결 테스트")
    print("-"*80)

    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Hello"}
            ],
            max_tokens=10
        )

        print(f"✅ OpenAI API 정상 작동")
        print(f"   응답: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"❌ OpenAI API 오류: {e}")
        return False

def check_existing_tables():
    """기존 테이블 확인"""
    print("\n[0.5] 기존 테이블 확인")
    print("-"*80)

    supabase = get_supabase()

    tables_to_check = [
        'contents',
        'perceptions',
        'worldviews',
        'layered_perceptions',
        'belief_patterns'
    ]

    existing = []
    missing = []

    for table in tables_to_check:
        try:
            result = supabase.table(table).select('id', count='exact').limit(0).execute()
            count = result.count or 0
            existing.append((table, count))
            print(f"✅ {table}: {count}개 레코드")
        except:
            missing.append(table)
            print(f"❌ {table}: 테이블 없음")

    return existing, missing

def main():
    """Phase 0 실행"""

    # 0.1 환경 변수
    if not check_environment():
        print("\n❌ 환경 변수 설정 필요")
        return False

    # 0.2 데이터베이스
    body_count = check_database()

    # 0.3 샘플 품질
    quality_ok = check_sample_quality()

    # 0.4 OpenAI API
    api_ok = test_openai_api()

    # 0.5 기존 테이블
    existing, missing = check_existing_tables()

    # 최종 판정
    print("\n" + "="*80)
    print("Phase 0 완료")
    print("="*80)

    print("\n✅ 통과 항목:")
    if body_count > 0:
        print(f"  - 본문 있는 데이터: {body_count}개")
    if quality_ok:
        print(f"  - 샘플 품질 양호")
    if api_ok:
        print(f"  - OpenAI API 정상")

    print("\n⚠️ 주의 항목:")
    if body_count < 200:
        print(f"  - 데이터 부족 ({body_count}개) → Phase 1 수집 필요")
    if not quality_ok:
        print(f"  - 샘플 품질 미흡 → 데이터 재수집 권장")
    if missing:
        print(f"  - 누락 테이블: {', '.join(missing)} → Phase 2 생성 필요")

    print("\n다음 단계:")
    if body_count < 200:
        print("  → Phase 1: 데이터 수집 (목표 200개)")
    if 'layered_perceptions' in missing:
        print("  → Phase 2: DB 스키마 생성")
    if body_count >= 200 and 'layered_perceptions' not in missing:
        print("  → Phase 3: 3층 구조 분석 시작 가능")

    print("\n" + "="*80)

    return True

if __name__ == '__main__':
    main()
