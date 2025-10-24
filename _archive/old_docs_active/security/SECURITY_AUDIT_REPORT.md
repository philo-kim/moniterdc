# 보안 점검 보고서 (Security Audit Report)

**작성일**: 2025-10-23
**상태**: 🔴 CRITICAL - 퍼블릭 공개 전 필수 조치 필요

---

## 🚨 발견된 보안 문제

### 1. 하드코딩된 API 키 (CRITICAL)

다음 파일들에 실제 API 키가 하드코딩되어 있습니다:

#### OpenAI API Key 노출
- **키**: `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`
- **노출된 파일**:
  - `_archive/validation_scripts/experimental_worldview_research.py`
  - `_archive/validation_scripts/comprehensive_frame_simulation.py`
  - `_archive/validation_scripts/real_data_worldview_experiments.py`

#### Supabase Service Key 노출 (SERVICE_ROLE)
- **키**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InljbWNzZGJ4bnBtdGhla3p5cHBsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzgzMDk3NSwiZXhwIjoyMDczNDA2OTc1fQ.vrPmnQugo5tatfoGXrm3UkFe_bSesE62igCM-AXTMBA`
- **노출된 파일**:
  - `check_worldview_data.py`

#### Supabase Anon Key 노출
- **키**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InljbWNzZGJ4bnBtdGhla3p5cHBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc4MzA5NzUsImV4cCI6MjA3MzQwNjk3NX0.FNN_2LdvfbIa__swyIKgzwSDVjIqaeUQisUfsuee-48`
- **노출된 파일**:
  - `_archive/validation_scripts/experimental_worldview_research.py`
  - `_archive/validation_scripts/comprehensive_frame_simulation.py`
  - `_archive/validation_scripts/real_data_worldview_experiments.py`

---

## ⚠️ 추가 보안 우려사항

### 2. Git에 트래킹되지 않는 테스트 파일들

현재 많은 테스트 파일들이 untracked 상태입니다. 이들 중 일부가 API 키를 포함할 가능성:
- `test_*.py` (30+ 파일)
- `_*.json` (15+ 파일)
- `check_*.py`, `cleanup_*.py`, `compare_*.py` 등

**✅ 조치 완료**: `.gitignore`에 패턴 추가하여 향후 실수로 커밋되는 것 방지

### 3. GitHub Actions 워크플로우

`.github/workflows/` 파일들도 API 키 참조 가능성 확인 필요:
- `worldview_monitoring.yml`
- `logic_defense_v3.yml`

---

## 📋 즉시 조치 필요 사항

### Priority 1: API 키 교체 (MUST DO BEFORE PUBLIC)

1. **OpenAI API Key 교체**
   ```bash
   # 1. OpenAI 대시보드에서 현재 키 삭제
   # 2. 새 키 생성
   # 3. .env 파일에만 저장
   ```

2. **Supabase Keys 재생성**
   ```bash
   # Supabase 프로젝트 설정에서:
   # 1. Service Role Key 재생성
   # 2. Anon Key 재생성 (선택사항 - public이므로 덜 위험)
   ```

### Priority 2: 하드코딩된 키 제거

노출된 파일 수정:

```bash
# 1. _archive 파일들 수정 (또는 삭제)
# - _archive/validation_scripts/experimental_worldview_research.py
# - _archive/validation_scripts/comprehensive_frame_simulation.py
# - _archive/validation_scripts/real_data_worldview_experiments.py

# 2. 루트 파일 수정
# - check_worldview_data.py

# 모든 하드코딩된 키를 환경변수 사용으로 변경:
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
```

### Priority 3: Git 히스토리 정리 (권장)

이미 커밋된 파일에 키가 있다면 히스토리에서도 제거 필요:

```bash
# 옵션 1: BFG Repo-Cleaner (권장)
brew install bfg
bfg --replace-text passwords.txt  # 키 목록 파일

# 옵션 2: git filter-branch (복잡)
# 주의: 이미 push했다면 force push 필요

# 옵션 3: 새 리포지토리로 이전 (가장 안전)
# 현재 깨끗한 상태만 새 repo에 push
```

---

## ✅ 완료된 조치

1. **`.gitignore` 업데이트**
   - 테스트 파일 패턴 추가 (`test_*.py`, `_*.json` 등)
   - 향후 실수로 커밋 방지

2. **보안 취약점 분석 완료**
   - 136개 파일에서 키 패턴 검색
   - 4개 실제 노출 파일 확인

---

## 📝 권장 보안 모범 사례

### 환경변수 사용

모든 스크립트에서 다음 패턴 사용:

```python
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not all([OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Missing required environment variables")
```

### GitHub Secrets 설정

GitHub Actions 사용 시:

```yaml
# .github/workflows/example.yml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
```

Settings → Secrets and variables → Actions → New repository secret

### Pre-commit Hook 설정

API 키 실수 커밋 방지:

```bash
# .git/hooks/pre-commit
#!/bin/sh
if git diff --cached | grep -E "sk-proj-|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"; then
    echo "Error: API keys detected in staged files!"
    exit 1
fi
```

---

## 🎯 체크리스트 (퍼블릭 공개 전)

- [ ] OpenAI API Key 교체 완료
- [ ] Supabase Service Key 재생성 완료
- [ ] 하드코딩된 키 모두 제거 (4개 파일)
- [ ] `.env.example` 파일 생성 (키 없이 템플릿만)
- [ ] README.md에서 API 키 예시 제거
- [ ] CLAUDE.md에서 API 키 예시 제거
- [ ] Git 히스토리 정리 (선택사항)
- [ ] GitHub Secrets 설정 완료
- [ ] Pre-commit hook 설정 (선택사항)
- [ ] 팀원들에게 새 키 공유 (private 채널)

---

## 📞 참고 링크

- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [Supabase Project Settings](https://supabase.com/dashboard/project/_/settings/api)
- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)

---

**⚠️ 중요**: 이 리포지토리를 퍼블릭으로 만들기 전에 위의 Priority 1-2를 반드시 완료하세요!
