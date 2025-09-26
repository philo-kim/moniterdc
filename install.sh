#!/bin/bash

# Logic Defense System v3.0 - 설치 스크립트
# DC갤러리 정치 AI 모니터링 시스템 자동 설치

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
    echo "║    DC갤러리 정치 AI 모니터링 시스템         ║"
    echo "║    Attack vs Defense Auto-Matcher         ║"
    echo "╚═══════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# 시스템 요구사항 확인
check_requirements() {
    echo -e "${YELLOW}🔍 시스템 요구사항 확인 중...${NC}"

    # Python 3.8+ 확인
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3가 설치되어 있지 않습니다!${NC}"
        echo "Python 3.8 이상을 설치해주세요."
        exit 1
    fi

    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    major=$(echo $python_version | cut -d. -f1)
    minor=$(echo $python_version | cut -d. -f2)

    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 8 ]); then
        echo -e "${RED}❌ Python 3.8 이상이 필요합니다. 현재: $python_version${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Python $python_version 확인됨${NC}"

    # pip 확인
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}❌ pip3가 설치되어 있지 않습니다!${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ pip3 확인됨${NC}"

    # Node.js 확인 (Supabase CLI용)
    if ! command -v node &> /dev/null; then
        echo -e "${YELLOW}⚠️ Node.js가 설치되어 있지 않습니다.${NC}"
        echo "Supabase CLI 설치를 위해 Node.js가 필요합니다."
        echo "설치하시겠습니까? (y/n)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            install_nodejs
        else
            echo -e "${YELLOW}⚠️ Node.js 없이 계속 진행합니다. 나중에 수동 설치가 필요할 수 있습니다.${NC}"
        fi
    else
        echo -e "${GREEN}✅ Node.js 확인됨${NC}"
    fi
}

# Node.js 설치
install_nodejs() {
    echo -e "${YELLOW}📦 Node.js 설치 중...${NC}"

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install node
        else
            echo -e "${RED}❌ Homebrew가 설치되어 있지 않습니다.${NC}"
            echo "https://nodejs.org 에서 직접 설치해주세요."
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        sudo apt-get install -y nodejs
    else
        echo -e "${RED}❌ 지원되지 않는 운영체제입니다.${NC}"
        echo "https://nodejs.org 에서 직접 설치해주세요."
        exit 1
    fi

    echo -e "${GREEN}✅ Node.js 설치 완료${NC}"
}

# Python 의존성 설치
install_python_deps() {
    echo -e "${YELLOW}📦 Python 의존성 설치 중...${NC}"

    # requirements.txt가 없으면 생성
    if [ ! -f "requirements.txt" ]; then
        echo -e "${YELLOW}📄 requirements.txt 생성 중...${NC}"
        cat > requirements.txt << EOF
# Core dependencies
aiohttp>=3.8.0
beautifulsoup4>=4.12.0
supabase>=1.0.0
openai>=1.0.0
python-dotenv>=1.0.0

# Telegram bot
python-telegram-bot>=20.0

# Database & Vector
psycopg2-binary>=2.9.0
numpy>=1.21.0

# Utilities
schedule>=1.2.0
colorama>=0.4.6
requests>=2.28.0
lxml>=4.9.0
EOF
    fi

    # 가상환경 생성 (선택사항)
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}🐍 Python 가상환경 생성 중...${NC}"
        python3 -m venv venv
        echo -e "${GREEN}✅ 가상환경 생성 완료${NC}"
        echo -e "${BLUE}💡 가상환경 활성화: source venv/bin/activate${NC}"
    fi

    # 의존성 설치
    pip3 install -r requirements.txt
    echo -e "${GREEN}✅ Python 의존성 설치 완료${NC}"
}

# Supabase CLI 설치
install_supabase_cli() {
    echo -e "${YELLOW}🗄️ Supabase CLI 설치 중...${NC}"

    if command -v supabase &> /dev/null; then
        echo -e "${GREEN}✅ Supabase CLI가 이미 설치되어 있습니다.${NC}"
        return
    fi

    # npm으로 설치
    if command -v npm &> /dev/null; then
        npm install -g supabase
        echo -e "${GREEN}✅ Supabase CLI 설치 완료${NC}"
    else
        echo -e "${RED}❌ npm이 없어서 Supabase CLI를 설치할 수 없습니다.${NC}"
        echo "Node.js와 npm을 먼저 설치해주세요."
        exit 1
    fi
}

# 환경변수 파일 설정
setup_env_file() {
    echo -e "${YELLOW}⚙️ 환경변수 설정 중...${NC}"

    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}📄 .env 파일 생성 중...${NC}"
        cat > .env << EOF
# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key-here

# OpenAI 설정
OPENAI_API_KEY=sk-your-openai-key-here
GPT_FILTER_MODEL=gpt-5-nano
GPT_ANALYSIS_MODEL=gpt-5-mini
GPT_STRATEGY_MODEL=gpt-5

# Telegram 설정 (선택사항)
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_CHAT_ID=your-chat-id-here

# 크롤링 설정
CRAWL_INTERVAL_MINUTES=60
MAX_PAGES_PER_GALLERY=15
BATCH_SIZE=20

# 매칭 설정
MATCH_THRESHOLD=0.8
MAX_MATCHES_PER_ATTACK=5
AUTO_MATCH_ENABLED=true
EOF
        echo -e "${GREEN}✅ .env 파일 생성 완료${NC}"
        echo -e "${YELLOW}⚠️ .env 파일에서 실제 API 키들을 설정해주세요!${NC}"
    else
        echo -e "${GREEN}✅ .env 파일이 이미 존재합니다.${NC}"
    fi
}

# 데이터베이스 마이그레이션
setup_database() {
    echo -e "${YELLOW}🗄️ 데이터베이스 설정 중...${NC}"

    # .env 파일 로드
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '#' | xargs)
    else
        echo -e "${RED}❌ .env 파일이 없습니다!${NC}"
        exit 1
    fi

    # Supabase URL/Key 확인
    if [[ "$SUPABASE_URL" == "https://your-project.supabase.co" ]] || [[ "$SUPABASE_SERVICE_KEY" == "your-service-key-here" ]]; then
        echo -e "${YELLOW}⚠️ Supabase 설정이 기본값입니다.${NC}"
        echo "실제 Supabase 프로젝트 정보를 .env에 설정한 후 다시 실행해주세요."
        return
    fi

    # 마이그레이션 실행
    echo -e "${YELLOW}📊 데이터베이스 마이그레이션 실행 중...${NC}"
    python3 init_system.py migrate

    echo -e "${GREEN}✅ 데이터베이스 설정 완료${NC}"
}

# 실행 권한 설정
setup_permissions() {
    echo -e "${YELLOW}🔐 실행 권한 설정 중...${NC}"

    chmod +x run.sh
    chmod +x install.sh

    # Python 스크립트들 실행 권한
    find . -name "*.py" -exec chmod +x {} \;

    echo -e "${GREEN}✅ 권한 설정 완료${NC}"
}

# 초기 테스트
run_initial_test() {
    echo -e "${YELLOW}🧪 초기 테스트 실행 중...${NC}"

    # 환경변수 확인
    if python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

required = ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY', 'OPENAI_API_KEY']
missing = [k for k in required if not os.getenv(k) or os.getenv(k).startswith('your-')]

if missing:
    print(f'Missing env vars: {missing}')
    exit(1)
else:
    print('Environment check passed')
"; then
        echo -e "${GREEN}✅ 환경변수 확인 완료${NC}"

        # 시스템 테스트 실행
        python3 test_system.py
    else
        echo -e "${YELLOW}⚠️ 환경변수가 완전히 설정되지 않았습니다.${NC}"
        echo ".env 파일을 완성한 후 './run.sh test'를 실행해주세요."
    fi
}

# 설치 완료 메시지
print_completion() {
    echo ""
    echo -e "${GREEN}🎉 Logic Defense System v3.0 설치 완료!${NC}"
    echo ""
    echo -e "${BLUE}다음 단계:${NC}"
    echo "1. .env 파일에서 실제 API 키들을 설정"
    echo "2. 데이터베이스 마이그레이션: ./run.sh migrate"
    echo "3. 시스템 테스트: ./run.sh test"
    echo "4. 크롤링 시작: ./run.sh crawl"
    echo "5. 매칭 시스템 시작: ./run.sh match-loop"
    echo ""
    echo -e "${BLUE}전체 파이프라인 실행: ./run.sh all${NC}"
    echo ""
    echo -e "${YELLOW}📖 자세한 사용법: ./run.sh help${NC}"
    echo ""
}

# 메인 설치 프로세스
main() {
    print_logo

    echo -e "${BLUE}Logic Defense System v3.0 설치를 시작합니다...${NC}"
    echo ""

    # 1. 시스템 요구사항 확인
    check_requirements

    # 2. Python 의존성 설치
    install_python_deps

    # 3. Supabase CLI 설치
    install_supabase_cli

    # 4. 환경변수 파일 설정
    setup_env_file

    # 5. 실행 권한 설정
    setup_permissions

    # 6. 데이터베이스 설정 (환경변수가 설정된 경우에만)
    setup_database

    # 7. 초기 테스트
    run_initial_test

    # 8. 완료 메시지
    print_completion
}

# 스크립트 실행
main "$@"