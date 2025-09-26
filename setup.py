#!/usr/bin/env python3
"""
Logic Defense RAG System - 초기 설정 도우미
이 스크립트를 실행하면 시스템 설정을 단계별로 진행합니다.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Optional
import shutil

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text: str, color: str = Colors.OKGREEN):
    """색상이 있는 텍스트 출력"""
    print(f"{color}{text}{Colors.ENDC}")

def print_header(text: str):
    """헤더 출력"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")

def check_command(command: str) -> bool:
    """명령어 존재 확인"""
    return shutil.which(command) is not None

def run_command(command: str, shell: bool = True) -> bool:
    """명령어 실행"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def check_python_version() -> bool:
    """Python 버전 확인"""
    import sys
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print_colored(f"✅ Python {version.major}.{version.minor}.{version.micro} 확인")
        return True
    else:
        print_colored(f"❌ Python 3.11 이상 필요 (현재: {version.major}.{version.minor})", Colors.FAIL)
        return False

def setup_venv():
    """가상환경 설정"""
    print_header("가상환경 설정")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print_colored("✅ 가상환경이 이미 존재합니다")
        response = input("재생성하시겠습니까? (y/N): ")
        if response.lower() != 'y':
            return True
        
        # 기존 가상환경 삭제
        shutil.rmtree(venv_path)
    
    print("가상환경 생성 중...")
    if run_command(f"{sys.executable} -m venv venv"):
        print_colored("✅ 가상환경 생성 완료")
        
        # 활성화 스크립트 경로 출력
        if sys.platform == "win32":
            activate_cmd = "venv\\Scripts\\activate"
        else:
            activate_cmd = "source venv/bin/activate"
        
        print_colored(f"\n활성화 명령어: {activate_cmd}", Colors.OKCYAN)
        return True
    else:
        print_colored("❌ 가상환경 생성 실패", Colors.FAIL)
        return False

def install_requirements():
    """패키지 설치"""
    print_header("Python 패키지 설치")
    
    # pip 업그레이드
    print("pip 업그레이드 중...")
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip"
    else:
        pip_path = "venv/bin/pip"
    
    if not Path(pip_path).exists():
        print_colored("⚠️  가상환경을 먼저 활성화하세요", Colors.WARNING)
        return False
    
    run_command(f"{pip_path} install --upgrade pip")
    
    # requirements.txt 설치
    print("패키지 설치 중... (시간이 걸릴 수 있습니다)")
    if run_command(f"{pip_path} install -r requirements.txt"):
        print_colored("✅ 패키지 설치 완료")
        return True
    else:
        print_colored("❌ 패키지 설치 실패", Colors.FAIL)
        
        # M1 Mac 특별 처리
        if sys.platform == "darwin":
            print("\nM1 Mac에서 psycopg2 오류가 발생한 경우:")
            print("1. brew install postgresql")
            print(f"2. {pip_path} install psycopg2-binary")
        
        return False

def setup_env_file():
    """환경변수 파일 설정"""
    print_header("환경변수 설정")
    
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print_colored("✅ .env 파일이 이미 존재합니다")
        response = input("기존 파일을 유지하시겠습니까? (Y/n): ")
        if response.lower() != 'n':
            return True
    
    if not env_example_path.exists():
        print_colored("⚠️  .env.example 파일이 없습니다", Colors.WARNING)
        print("수동으로 .env 파일을 생성해주세요")
        return False
    
    # .env.example 복사
    shutil.copy(env_example_path, env_path)
    print_colored("✅ .env 파일 생성됨")
    
    print("\n다음 정보를 .env 파일에 입력해주세요:")
    print("1. Supabase URL과 키")
    print("2. OpenAI API 키")
    print("3. Telegram Bot 토큰 (선택)")
    
    response = input("\n지금 설정하시겠습니까? (y/N): ")
    if response.lower() == 'y':
        env_data = {}
        
        print("\n[Supabase 설정]")
        env_data['SUPABASE_URL'] = input("SUPABASE_URL: ").strip()
        env_data['SUPABASE_SERVICE_KEY'] = input("SUPABASE_SERVICE_KEY: ").strip()
        
        print("\n[OpenAI 설정]")
        env_data['OPENAI_API_KEY'] = input("OPENAI_API_KEY: ").strip()
        
        print("\n[Telegram 설정 (선택, 엔터로 스킵)]")
        env_data['TELEGRAM_BOT_TOKEN'] = input("TELEGRAM_BOT_TOKEN: ").strip()
        env_data['TELEGRAM_CHAT_ID'] = input("TELEGRAM_CHAT_ID: ").strip()
        
        # .env 파일 업데이트
        with open(env_path, 'r') as f:
            content = f.read()
        
        for key, value in env_data.items():
            if value:
                # 기존 값 대체
                import re
                pattern = f"{key}=.*"
                replacement = f"{key}={value}"
                content = re.sub(pattern, replacement, content)
        
        with open(env_path, 'w') as f:
            f.write(content)
        
        print_colored("✅ 환경변수 설정 완료")
    else:
        print_colored(f"📝 나중에 {env_path} 파일을 직접 편집하세요", Colors.WARNING)
    
    return True

def setup_dashboard():
    """대시보드 설정"""
    print_header("대시보드 설정")
    
    dashboard_path = Path("dashboard")
    
    if not dashboard_path.exists():
        print_colored("⚠️  dashboard 폴더가 없습니다", Colors.WARNING)
        return False
    
    # Node.js 확인
    if not check_command("node"):
        print_colored("❌ Node.js가 설치되지 않았습니다", Colors.FAIL)
        print("https://nodejs.org 에서 설치하세요")
        return False
    
    # npm 패키지 설치
    print("npm 패키지 설치 중...")
    os.chdir(dashboard_path)
    
    if run_command("npm install"):
        print_colored("✅ 대시보드 패키지 설치 완료")
        
        # .env.local 파일 생성
        env_local = Path(".env.local")
        if not env_local.exists():
            # .env.local 생성
            with open("../.env", 'r') as f:
                env_content = f.read()
            
            # Supabase 정보 추출
            supabase_url = ""
            supabase_anon_key = ""
            
            for line in env_content.split('\n'):
                if 'SUPABASE_URL=' in line:
                    supabase_url = line.split('=')[1].strip()
                elif 'SUPABASE_ANON_KEY=' in line:
                    supabase_anon_key = line.split('=')[1].strip()
            
            # .env.local 작성
            with open(env_local, 'w') as f:
                f.write(f"NEXT_PUBLIC_SUPABASE_URL={supabase_url}\n")
                f.write(f"NEXT_PUBLIC_SUPABASE_ANON_KEY={supabase_anon_key}\n")
            
            print_colored("✅ dashboard/.env.local 파일 생성됨")
        
        os.chdir("..")
        return True
    else:
        os.chdir("..")
        print_colored("❌ npm 설치 실패", Colors.FAIL)
        return False

def create_quick_start_scripts():
    """빠른 시작 스크립트 생성"""
    print_header("빠른 시작 스크립트 생성")
    
    # start.sh (Unix/Mac)
    start_sh = """#!/bin/bash
# Logic Defense RAG System - 빠른 시작 스크립트

echo "🚀 Logic Defense RAG System 시작..."

# 가상환경 활성화
source venv/bin/activate

# 시스템 체크
echo "📋 시스템 체크 중..."
python check_system.py

echo ""
echo "시스템을 시작하시겠습니까? (Y/n)"
read response

if [[ "$response" != "n" ]]; then
    # 크롤러 백그라운드 실행
    echo "🕷️ 크롤러 시작..."
    python rag_crawler.py &
    CRAWLER_PID=$!
    
    # 대시보드 실행
    echo "📊 대시보드 시작..."
    cd dashboard && npm run dev &
    DASHBOARD_PID=$!
    
    echo ""
    echo "✅ 시스템이 실행 중입니다"
    echo "   크롤러 PID: $CRAWLER_PID"
    echo "   대시보드 PID: $DASHBOARD_PID"
    echo ""
    echo "📌 대시보드: http://localhost:3000"
    echo ""
    echo "종료하려면 Ctrl+C를 누르세요"
    
    # 종료 대기
    wait
fi
"""

    # start.bat (Windows)
    start_bat = """@echo off
REM Logic Defense RAG System - 빠른 시작 스크립트

echo 🚀 Logic Defense RAG System 시작...

REM 가상환경 활성화
call venv\\Scripts\\activate

REM 시스템 체크
echo 📋 시스템 체크 중...
python check_system.py

echo.
set /p response="시스템을 시작하시겠습니까? (Y/n): "

if /i not "%response%"=="n" (
    REM 크롤러 실행
    echo 🕷️ 크롤러 시작...
    start /b python rag_crawler.py
    
    REM 대시보드 실행
    echo 📊 대시보드 시작...
    cd dashboard
    start /b npm run dev
    cd ..
    
    echo.
    echo ✅ 시스템이 실행 중입니다
    echo 📌 대시보드: http://localhost:3000
    echo.
    echo 종료하려면 이 창을 닫으세요
    pause
)
"""

    # 스크립트 저장
    if sys.platform != "win32":
        with open("start.sh", "w") as f:
            f.write(start_sh)
        os.chmod("start.sh", 0o755)
        print_colored("✅ start.sh 생성됨 (./start.sh 로 실행)")
    else:
        with open("start.bat", "w") as f:
            f.write(start_bat)
        print_colored("✅ start.bat 생성됨 (start.bat 로 실행)")
    
    return True

def print_next_steps():
    """다음 단계 안내"""
    print_header("✨ 설정 완료!")
    
    print(f"\n{Colors.BOLD}다음 단계:{Colors.ENDC}")
    print("\n1. 가상환경 활성화:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. Supabase 마이그레이션:")
    print("   - Supabase 대시보드 → SQL Editor")
    print("   - CREATE EXTENSION IF NOT EXISTS vector;")
    print("   - supabase/migrations/*.sql 파일들 실행")
    
    print("\n3. 시스템 체크:")
    print("   python check_system.py")
    
    print("\n4. 빠른 시작:")
    if sys.platform == "win32":
        print("   start.bat")
    else:
        print("   ./start.sh")
    
    print(f"\n{Colors.OKGREEN}📚 자세한 가이드는 IDE_SETUP_GUIDE.md 를 참고하세요{Colors.ENDC}")

def main():
    """메인 실행 함수"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       Logic Defense RAG System - 초기 설정 도우미         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    success = True
    
    # 1. Python 버전 체크
    print_header("시스템 요구사항 체크")
    if not check_python_version():
        print_colored("Python 3.11 이상을 설치하세요", Colors.FAIL)
        return
    
    # 2. 가상환경 설정
    if not setup_venv():
        success = False
        print_colored("가상환경 설정 실패", Colors.FAIL)
    
    # 3. 패키지 설치
    if success:
        if not install_requirements():
            success = False
            print_colored("패키지 설치 실패", Colors.FAIL)
    
    # 4. 환경변수 설정
    if success:
        if not setup_env_file():
            success = False
            print_colored("환경변수 설정 실패", Colors.FAIL)
    
    # 5. 대시보드 설정
    if success:
        if not setup_dashboard():
            print_colored("대시보드 설정 실패 (선택사항)", Colors.WARNING)
    
    # 6. 빠른 시작 스크립트 생성
    if success:
        create_quick_start_scripts()
    
    # 7. 완료 메시지
    if success:
        print_next_steps()
    else:
        print_colored("\n⚠️  일부 설정이 실패했습니다. 위의 오류를 확인하세요.", Colors.FAIL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}설정 중단됨{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}오류 발생: {e}{Colors.ENDC}")
