# Quick Start Guide

> 5분 안에 시스템을 이해하고 실행하기

## 🎯 이 프로젝트는 무엇인가?

**DC Gallery 정치 담론의 세계관을 분석하는 AI 시스템**

```
DC Gallery 글 →  GPT 분석 → 세계관 구성 → 대시보드 표시
```

## 📂 핵심 파일 3개

| 파일 | 역할 |
|------|------|
| `README.md` | 전체 시스템 사용 가이드 |
| `ARCHITECTURE.md` | 왜 이렇게 만들어졌는가 (개발 의사결정) |
| `engines/analyzers/` | 핵심 AI 엔진 |

## 🚀 10분 만에 실행하기

### 1. 환경 설정 (3분)

```bash
# 1. Python 환경
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 환경변수 (.env)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-key
OPENAI_API_KEY=sk-proj-...

# 3. 대시보드 (.env.local)
cd dashboard
npm install
```

### 2. 데이터베이스 설정 (2분)

```bash
# Supabase Dashboard에서 SQL 실행
# supabase/migrations/*.sql 파일들을 순서대로 실행
```

### 3. 시스템 실행 (5분)

```bash
# 데이터 수집
python phase1_collect_data.py

# 3-Layer 분석
python phase3_layered_analysis.py

# 세계관 구성
python -c "
import asyncio
from engines.analyzers.optimal_worldview_constructor import OptimalWorldviewConstructor

async def main():
    constructor = OptimalWorldviewConstructor()
    await constructor.build_hierarchical_worldviews()

asyncio.run(main())
"

# 대시보드 실행
cd dashboard && npm run dev
# → http://localhost:3000
```

## 💡 핵심 개념 1분 요약

### 세계관이란?

특정 집단이 공유하는 **해석 프레임워크**

```
예시: "민주당 = 독재 재현" 세계관

사실: "유심교체 정보 유출"

DC 해석: "사찰을 통한 독재적 통치 시도"
일반 해석: "정보 유출 사건"

→ 왜 다른가? "민주당 = 독재" 세계관 때문
```

### 3-Layer 분석이란?

```
표면층 (Explicit Claims)
  "민주당이 유심교체 정보를 불법으로 얻었다"
  ↓
암묵층 (Implicit Assumptions)
  "민주당은 통신사를 협박해서 정보를 얻는다"
  ↓
심층 (Deep Beliefs) ← 세계관의 핵심
  "민주당/좌파는 독재정권처럼 사찰로 반대파를 제거한다"
```

## 📊 현재 데이터

- **원본 글**: 297개
- **Perception**: 297개 (3-Layer 분석)
- **세계관**: 6개 (계층형)
  - 민주당/좌파에 대한 인식 (2개 세부)
  - 외부 세력의 위협 (2개 세부)
  - 국내 정치적 불안정 (2개 세부)

## 🎨 대시보드 미리보기

**메인 페이지**: 계층형 세계관 맵
**상세 페이지**:
- Narrative (예시 중심 설명)
- **원본 글 목록** (실제 DC Gallery 게시글)
- Metadata 시각화
- 반박 논리 (개발 중)

## 🔧 주요 엔진

| 엔진 | 역할 | 파일 |
|------|------|------|
| LayeredPerceptionExtractor | 3-Layer 분석 | `engines/analyzers/layered_perception_extractor.py` |
| OptimalWorldviewConstructor | 세계관 구성 | `engines/analyzers/optimal_worldview_constructor.py` |
| WorldviewUpdater | 자동 업데이트 | `engines/analyzers/worldview_updater.py` |

## 📖 더 알아보기

- **전체 가이드**: [README.md](README.md)
- **아키텍처 상세**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **개발 히스토리**: [ARCHITECTURE.md - 프로젝트 진화 과정](ARCHITECTURE.md#-프로젝트-진화-과정)

## ❓ 자주 묻는 질문

**Q: 왜 "공격-방어"가 아니라 "세계관"인가?**
A: 표면적 반박은 효과가 없음. 심층 믿음을 이해해야 함.

**Q: GPT 비용은 얼마나 드나?**
A: 월 $150 정도 (일일 100개 글 기준)

**Q: 대시보드에서 원본 글을 볼 수 있나?**
A: 네! `/worldviews/[id]` 페이지에서 실제 DC Gallery 링크 제공

**Q: 자동 업데이트는 어떻게 되나?**
A: 일일/주간/월간 자동 업데이트 (WorldviewUpdater)

---

**프로젝트 시작**: 2024-09
**현재 버전**: v4.0 (Worldview System)
**마지막 업데이트**: 2025-01-05
