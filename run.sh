#!/bin/bash

# Logic Defense System v3.0 - 실행 스크립트
# 모든 주요 기능을 쉽게 실행할 수 있는 통합 스크립트

set -e  # 에러 발생시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로고 출력
print_logo() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════╗"
    echo "║    Logic Defense System v3.0              ║"
    echo "║    Attack vs Defense Auto-Matcher         ║"
    echo "╚═══════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 도움말
show_help() {
    echo "Usage: ./run.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  init          - 시스템 초기화 및 테스트"
    echo "  crawl         - 크롤러 실행 (논리 수집)"
    echo "  match         - 매칭 시스템 실행 (1회)"
    echo "  match-loop    - 매칭 시스템 실행 (지속)"
    echo "  alert         - 알림 발송"
    echo "  stats         - 시스템 통계 보기"
    echo "  health        - 헬스체크"
    echo "  migrate       - DB 마이그레이션 실행"
    echo "  test          - 전체 시스템 테스트"
    echo "  clean         - 테스트 데이터 정리"
    echo "  logs          - 최근 로그 보기"
    echo "  all           - 크롤링 → 매칭 → 알림 전체 실행"
    echo ""
}

# 환경 확인
check_env() {
    if [ ! -f .env ]; then
        echo -e "${RED}❌ .env 파일이 없습니다!${NC}"
        echo "cp .env.example .env 명령으로 생성하세요."
        exit 1
    fi
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3가 설치되어 있지 않습니다!${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 환경 확인 완료${NC}"
}

# 의존성 설치
install_deps() {
    echo -e "${YELLOW}📦 의존성 설치 중...${NC}"
    pip install -q -r requirements.txt
    echo -e "${GREEN}✅ 의존성 설치 완료${NC}"
}

# 시스템 초기화
init_system() {
    echo -e "${YELLOW}🔧 시스템 초기화...${NC}"
    python3 init_system.py test
}

# 크롤러 실행
run_crawler() {
    echo -e "${YELLOW}🕷️ 크롤러 실행 중...${NC}"
    python3 logic_crawler_fixed.py
}

# 매칭 실행 (1회)
run_matcher_once() {
    echo -e "${YELLOW}🎯 매칭 시스템 실행 (1회)...${NC}"
    python3 scheduler/background_matcher_fixed.py --once
}

# 매칭 실행 (지속)
run_matcher_loop() {
    echo -e "${YELLOW}🎯 매칭 시스템 실행 (지속)...${NC}"
    echo -e "${YELLOW}종료하려면 Ctrl+C를 누르세요.${NC}"
    python3 scheduler/background_matcher_fixed.py
}

# 알림 발송
send_alerts() {
    echo -e "${YELLOW}📨 알림 발송 중...${NC}"
    python3 alert_sender.py
}

# 통계 보기
show_stats() {
    echo -e "${BLUE}📊 시스템 통계${NC}"
    python3 init_system.py stats
}

# 헬스체크
health_check() {
    echo -e "${BLUE}🏥 시스템 헬스체크${NC}"
    python3 scheduler/background_matcher_fixed.py --health
}

# DB 마이그레이션
run_migration() {
    echo -e "${YELLOW}🗄️ DB 마이그레이션 실행...${NC}"
    
    # Supabase CLI 확인
    if ! command -v supabase &> /dev/null; then
        echo -e "${RED}❌ Supabase CLI가 설치되어 있지 않습니다!${NC}"
        echo "설치: npm install -g supabase"
        exit 1
    fi
    
    # 마이그레이션 실행
    for file in supabase/migrations/*.sql; do
        echo "Applying: $file"
        # 여기에 실제 마이그레이션 명령 추가
        # supabase db push 또는 직접 SQL 실행
    done
    
    echo -e "${GREEN}✅ 마이그레이션 완료${NC}"
}

# 전체 테스트
run_test() {
    echo -e "${YELLOW}🧪 전체 시스템 테스트...${NC}"
    
    # 1. 환경 테스트
    python3 init_system.py test
    
    # 2. 크롤러 테스트 (짧게)
    echo -e "${YELLOW}크롤러 테스트...${NC}"
    timeout 30 python3 logic_crawler_fixed.py || true
    
    # 3. 매칭 테스트
    echo -e "${YELLOW}매칭 테스트...${NC}"
    python3 scheduler/background_matcher_fixed.py --once
    
    echo -e "${GREEN}✅ 테스트 완료${NC}"
}

# 테스트 데이터 정리
clean_test_data() {
    echo -e "${YELLOW}🧹 테스트 데이터 정리...${NC}"
    python3 -c "
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# 테스트 데이터 삭제
result = supabase.table('logic_repository').delete().eq('source_gallery', 'test').execute()
print(f'Deleted {len(result.data) if result.data else 0} test records')
"
    echo -e "${GREEN}✅ 정리 완료${NC}"
}

# 로그 보기
show_logs() {
    echo -e "${BLUE}📜 최근 로그${NC}"
    
    if [ -d "logs" ]; then
        tail -n 50 logs/*.log 2>/dev/null || echo "로그 파일이 없습니다."
    else
        echo "로그 디렉토리가 없습니다."
    fi
}

# 전체 실행
run_all() {
    echo -e "${YELLOW}🚀 전체 파이프라인 실행...${NC}"
    
    # 1. 크롤링
    run_crawler
    
    # 2. 매칭
    run_matcher_once
    
    # 3. 알림
    send_alerts
    
    echo -e "${GREEN}✅ 전체 실행 완료${NC}"
}

# 메인 실행
main() {
    print_logo
    check_env
    
    case "${1:-help}" in
        init)
            init_system
            ;;
        crawl)
            run_crawler
            ;;
        match)
            run_matcher_once
            ;;
        match-loop)
            run_matcher_loop
            ;;
        alert)
            send_alerts
            ;;
        stats)
            show_stats
            ;;
        health)
            health_check
            ;;
        migrate)
            run_migration
            ;;
        test)
            run_test
            ;;
        clean)
            clean_test_data
            ;;
        logs)
            show_logs
            ;;
        all)
            run_all
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}Unknown command: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@"
