#!/bin/bash
# 전체 데이터 파이프라인 재실행 스크립트
# 계층적 세계관 v2.0 완전 재구축

set -e  # Exit on error

echo "================================================================================"
echo "MoniterDC v2.0 완전 파이프라인 재실행"
echo "================================================================================"
echo ""

# 환경 변수 확인
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_KEY" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "환경 변수를 로드 중..."
    if [ -f .env ]; then
        export $(grep -E '^(SUPABASE_URL|SUPABASE_SERVICE_KEY|OPENAI_API_KEY)=' .env | xargs)
    fi
fi

# 1. 계층적 세계관 생성 (V1+ + V14)
echo "1/4: 계층적 세계관 생성 중..."
echo "    - V1+: 상위 세계관 7개 (그들의 언어)"
echo "    - V14: 하위 세계관 44개 (구체적 사례)"
python3 scripts/generate_hierarchical_worldviews.py
echo "    ✓ 완료"
echo ""

# 2. DB에 계층적 세계관 적용
echo "2/4: DB에 계층적 세계관 적용 중..."
python3 scripts/apply_hierarchical_worldviews.py
echo "    ✓ 완료"
echo ""

# 3. Perception-Worldview 링크 생성 (계층적 매칭)
echo "3/4: Perception-Worldview 링크 생성 중..."
echo "    - Actor + Mechanism + Logic 기반 매칭"
echo "    - 하위 세계관에 직접 링크"
python3 scripts/run_hierarchical_matcher.py
echo "    ✓ 완료"
echo ""

# 4. 데이터 완결성 검증
echo "4/4: 데이터 완결성 검증 중..."
python3 scripts/verify_data_completeness.py
echo ""

echo "================================================================================"
echo "전체 파이프라인 완료!"
echo "================================================================================"
echo ""
echo "다음 단계:"
echo "  1. Dashboard에서 계층 구조 확인"
echo "  2. 새 content 추가 시: python3 scripts/process_new_content.py"
echo "  3. 주기적 세계관 진화: python3 scripts/run_worldview_evolution.py"
echo ""
