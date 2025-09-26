# 🚀 Logic Defense RAG System - IDE 실행 가이드

> **초보자도 따라할 수 있는 단계별 설치 및 실행 가이드**  
> IDE(VSCode, PyCharm 등)에서 바로 실행 가능한 완벽한 설명서

## 📌 빠른 시작 체크리스트

```bash
□ Python 3.11 이상 설치
□ Node.js 18 이상 설치  
□ Git 설치
□ Supabase 계정 생성
□ OpenAI API 키 발급
□ Telegram Bot 생성 (선택)
```

---

## 🔧 Part 1: 초기 환경 설정

### 1.1 필수 프로그램 설치

#### **Python 3.11 설치**
```bash
# macOS (Homebrew)
brew install python@3.11

# Windows (공식 사이트에서 다운로드)
# https://www.python.org/downloads/

# 설치 확인
python --version  # 또는 python3 --version
# 출력: Python 3.11.x
```

#### **Node.js 설치**
```bash
# macOS
brew install node

# Windows (공식 사이트에서 다운로드)
# https://nodejs.org/

# 설치 확인
node --version  # v18.x.x 이상
npm --version   # 9.x.x 이상
```

### 1.2 프로젝트 다운로드

```bash
# 작업 디렉토리로 이동
cd ~/dev  # 또는 원하는 디렉토리

# Git으로 클론 (이미 있다면 스킵)
# git clone [your-repository-url] minjoo/moniterdc

# 프로젝트 폴더로 이동
cd minjoo/moniterdc
```

### 1.3 Python 가상환경 설정

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# (venv) 표시가 터미널에 나타나면 성공!
```

### 1.4 Python 패키지 설치

```bash
# pip 업그레이드
pip install --upgrade pip

# 필수 패키지 설치
pip install -r requirements.txt

# 설치 확인
pip list | grep langchain
# langchain, langchain-openai 등이 표시되면 성공
```

**⚠️ 오류 해결:**
```bash
# M1 Mac에서 psycopg2 오류 시
brew install postgresql
pip install psycopg2-binary

# Windows에서 오류 시
pip install --upgrade setuptools wheel
pip install -r requirements.txt --no-cache-dir
```

---

## 🔑 Part 2: API 키 및 서비스 설정

### 2.1 환경변수 파일 생성

```bash
# .env 파일 복사
cp .env.example .env

# VSCode에서 편집
code .env

# 또는 nano/vim 사용
nano .env
```

### 2.2 Supabase 설정

#### **계정 생성 및 프로젝트 설정**
1. [https://supabase.com](https://supabase.com) 접속
2. 무료 계정 생성 (GitHub 연동 가능)
3. "New Project" 클릭
4. 프로젝트 정보 입력:
   - Project Name: `logic-defense`
   - Database Password: 강력한 비밀번호 (저장 필수!)
   - Region: `Northeast Asia (Seoul)` 선택

#### **API 키 찾기**
1. 프로젝트 대시보드 → Settings → API
2. 다음 정보 복사:
   ```
   Project URL: https://xxxxx.supabase.co
   anon public: eyJhbGc...
   service_role: eyJhbGc... (비공개 유지!)
   ```

#### **pgvector 설치 및 테이블 생성**
1. SQL Editor 탭 클릭
2. 다음 명령 실행:

```sql
-- 1단계: pgvector 확장 설치
CREATE EXTENSION IF NOT EXISTS vector;

-- 확인
SELECT * FROM pg_extension WHERE extname = 'vector';
```

3. 마이그레이션 파일 실행:
```bash
# 터미널에서
cat supabase/migrations/003_logic_defense_system.sql
# 내용 복사 → Supabase SQL Editor에 붙여넣기 → Run

cat supabase/migrations/010_langchain_rag_system.sql  
# 내용 복사 → Supabase SQL Editor에 붙여넣기 → Run
```

### 2.3 OpenAI API 설정

#### **API 키 발급**
1. [https://platform.openai.com](https://platform.openai.com) 접속
2. 로그인 → API keys
3. "Create new secret key" 클릭
4. 키 복사 (한 번만 표시됨!)

#### **사용량 한도 설정 (중요!)**
1. Usage → Limits
2. Hard limit: $10 설정 (초과 방지)
3. Soft limit: $5 설정 (알림)

### 2.4 Telegram Bot 설정 (선택사항)

#### **Bot 생성**
1. Telegram에서 @BotFather 검색
2. `/newbot` 명령
3. Bot 이름 입력: `Logic Defense Bot`
4. Username 입력: `logic_defense_bot` (고유해야 함)
5. 토큰 복사: `7234567890:AAF...`

#### **Chat ID 찾기**
1. 생성한 봇에 메시지 전송
2. 브라우저에서 접속:
   ```
   https://api.telegram.org/bot[YOUR_TOKEN]/getUpdates
   ```
3. "chat":{"id": 숫자} 찾기

### 2.5 .env 파일 완성

```bash
# .env 파일 내용
# Supabase Configuration
SUPABASE_URL=https://ycmcsdbxnpmthekzyppl.supabase.co  # 실제 URL로 변경
SUPABASE_ANON_KEY=eyJhbGc...  # 실제 anon key로 변경
SUPABASE_SERVICE_KEY=eyJhbGc...  # 실제 service key로 변경

# OpenAI Configuration  
OPENAI_API_KEY=sk-proj-...  # 실제 API 키로 변경

# Telegram Bot Configuration (선택사항)
TELEGRAM_BOT_TOKEN=7234567890:AAF...  # 실제 토큰으로 변경
TELEGRAM_CHAT_ID=123456789  # 실제 Chat ID로 변경

# 나머지는 기본값 유지
ENABLE_AI_ANALYSIS=true
ENABLE_TELEGRAM_ALERTS=true
DEBUG_MODE=false
```

---

## 🏃‍♂️ Part 3: 시스템 실행

### 3.1 데이터베이스 초기화 확인

```python
# test_db_connection.py 파일 생성
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# 연결 테스트
try:
    result = supabase.table('logic_repository').select("*").limit(1).execute()
    print("✅ Supabase 연결 성공!")
    print(f"테이블 상태: {len(result.data)} rows")
except Exception as e:
    print(f"❌ Supabase 연결 실패: {e}")
```

```bash
# 실행
python test_db_connection.py
```

### 3.2 RAG 시스템 테스트

```bash
# RAG 시스템 단독 테스트
python rag_system/rag_logic_system.py

# 예상 출력:
# === 공격 논리 분석 ===
# {
#   "core_argument": "...",
#   "keywords": [...],
#   ...
# }
```

### 3.3 크롤러 실행

```bash
# 전체 크롤링 + RAG 분석 실행
python rag_crawler.py

# 특정 갤러리만 테스트 (빠른 테스트용)
python -c "
import asyncio
from rag_crawler import RAGCrawler

async def test():
    async with RAGCrawler() as crawler:
        posts = await crawler.fetch_concept_posts('minjoo', pages=1)
        print(f'수집된 게시글: {len(posts)}개')
        if posts:
            result = await crawler.process_with_rag(posts[:2])
            print(f'RAG 분석 완료: {len(result)}개')

asyncio.run(test())
"
```

### 3.4 대시보드 실행

```bash
# 새 터미널 창/탭 열기
cd dashboard

# 패키지 설치 (처음 한 번만)
npm install

# 환경변수 설정
cp .env.local.example .env.local
# .env.local 편집하여 Supabase URL과 anon key 입력

# 개발 서버 실행
npm run dev

# 브라우저에서 http://localhost:3000 접속
```

---

## 🐛 Part 4: 일반적인 문제 해결

### 4.1 ModuleNotFoundError

```bash
# 오류: ModuleNotFoundError: No module named 'langchain'
# 해결:
pip install langchain langchain-openai langchain-community

# 가상환경 확인
which python  # venv/bin/python이어야 함
```

### 4.2 OpenAI API 오류

```python
# 오류: Invalid API key
# 해결: .env 파일 확인
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv('OPENAI_API_KEY'))  # sk-로 시작해야 함

# 오류: Rate limit exceeded
# 해결: 대기 시간 추가
await asyncio.sleep(1)  # API 호출 사이에 추가
```

### 4.3 Supabase 연결 오류

```sql
-- 오류: relation "logic_repository" does not exist
-- 해결: 테이블 생성 확인
SELECT * FROM information_schema.tables 
WHERE table_name = 'logic_repository';

-- 테이블이 없으면 마이그레이션 재실행
```

### 4.4 pgvector 오류

```sql
-- 오류: type "vector" does not exist
-- 해결: Extension 설치
CREATE EXTENSION IF NOT EXISTS vector;

-- 권한 오류시 Supabase 대시보드에서 실행
```

---

## 📊 Part 5: IDE 설정 (VSCode)

### 5.1 추천 Extensions

```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance", 
    "ms-python.black-formatter",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "mtxr.sqltools",
    "mtxr.sqltools-driver-pg"
  ]
}
```

### 5.2 디버깅 설정

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: RAG Crawler",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/rag_crawler.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      },
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "name": "Python: Test RAG System",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/rag_system/rag_logic_system.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      },
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

### 5.3 작업 자동화

```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Install Dependencies",
      "type": "shell",
      "command": "pip install -r requirements.txt",
      "group": "build"
    },
    {
      "label": "Run RAG Crawler",
      "type": "shell",
      "command": "python rag_crawler.py",
      "group": {
        "kind": "build",
        "isDefault": true
      }
    },
    {
      "label": "Start Dashboard",
      "type": "shell",
      "command": "cd dashboard && npm run dev",
      "group": "test"
    }
  ]
}
```

---

## 🎯 Part 6: 실행 시나리오

### 시나리오 1: 빠른 테스트

```bash
# 1. 가상환경 활성화
source venv/bin/activate

# 2. 간단한 분석 테스트
python -c "
from rag_system.rag_logic_system import get_rag_system
import asyncio

async def quick_test():
    rag = get_rag_system()
    result = await rag.analyze_logic(
        '정부 정책이 실패했다',
        {'logic_type': 'attack', 'source': 'test'}
    )
    print('분석 완료:', result['analysis']['core_argument'])

asyncio.run(quick_test())
"
```

### 시나리오 2: 전체 시스템 실행

```bash
# Terminal 1: 크롤러 실행
source venv/bin/activate
python rag_crawler.py

# Terminal 2: 대시보드 실행  
cd dashboard
npm run dev

# Terminal 3: 실시간 로그 모니터링
tail -f *.log

# 브라우저: http://localhost:3000
```

### 시나리오 3: 프로덕션 배포

```bash
# GitHub Actions 설정
# .github/workflows/rag_system.yml 파일이 자동 실행됨

# Secrets 설정 (GitHub 저장소 → Settings → Secrets)
SUPABASE_URL
SUPABASE_SERVICE_KEY
OPENAI_API_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

---

## ✅ Part 7: 작동 확인 체크리스트

### 기본 기능 확인

```python
# check_system.py 생성
import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client
from openai import AsyncOpenAI
from rag_system.rag_logic_system import get_rag_system

load_dotenv()

async def check_all():
    print("🔍 시스템 체크 시작...\n")
    
    # 1. 환경변수
    print("1️⃣ 환경변수 체크")
    checks = [
        ('SUPABASE_URL', os.getenv('SUPABASE_URL')),
        ('SUPABASE_SERVICE_KEY', os.getenv('SUPABASE_SERVICE_KEY')),
        ('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))
    ]
    for name, value in checks:
        status = "✅" if value else "❌"
        print(f"  {status} {name}: {'설정됨' if value else '누락'}")
    
    # 2. Supabase 연결
    print("\n2️⃣ Supabase 연결 체크")
    try:
        supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_KEY')
        )
        result = supabase.table('logic_repository').select("count").execute()
        print(f"  ✅ 연결 성공")
    except Exception as e:
        print(f"  ❌ 연결 실패: {e}")
    
    # 3. OpenAI API
    print("\n3️⃣ OpenAI API 체크")
    try:
        client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        print(f"  ✅ API 작동 확인")
    except Exception as e:
        print(f"  ❌ API 오류: {e}")
    
    # 4. RAG 시스템
    print("\n4️⃣ RAG 시스템 체크")
    try:
        rag = get_rag_system()
        print(f"  ✅ RAG 시스템 초기화 완료")
    except Exception as e:
        print(f"  ❌ RAG 시스템 오류: {e}")
    
    print("\n✨ 체크 완료!")

# 실행
asyncio.run(check_all())
```

```bash
# 실행
python check_system.py
```

---

## 📚 Part 8: 추가 리소스

### 유용한 명령어 모음

```bash
# 로그 실시간 확인
tail -f *.log | grep ERROR  # 에러만 확인
tail -f *.log | grep SUCCESS  # 성공 메시지만

# 프로세스 확인
ps aux | grep python  # 실행 중인 Python 프로세스
lsof -i :3000  # 3000 포트 사용 프로세스

# 데이터베이스 상태 확인 (Python)
python -c "
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()
s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
r = s.table('logic_repository').select('count').execute()
print(f'총 {len(r.data)}개 논리 저장됨')
"

# Git 상태 확인
git status
git diff  # 변경사항 확인
```

### 트러블슈팅 연락처

```
📧 이메일: [프로젝트 담당자 이메일]
💬 Telegram: [담당자 텔레그램]
🐛 Issues: https://github.com/[your-repo]/issues
```

---

## 🎉 축하합니다!

모든 설정이 완료되었습니다. 이제 다음을 할 수 있습니다:

1. **크롤링**: DC갤러리에서 정치 논리 자동 수집
2. **분석**: LangChain RAG로 논리 구조 분석
3. **매칭**: 공격 논리에 대한 최적 방어 논리 자동 추천
4. **모니터링**: 실시간 대시보드에서 결과 확인
5. **알림**: Telegram으로 중요 이벤트 알림

문제가 발생하면 이 문서의 Part 4 (문제 해결)를 참고하거나, check_system.py를 실행하여 시스템 상태를 확인하세요.

**Happy Coding! 🚀**
