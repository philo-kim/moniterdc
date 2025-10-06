# 프로젝트 최종 정리

> **2025-01-05 기준 최종 버전 문서**

---

## 📋 필수 문서 (반드시 읽어야 함)

### 1. [README.md](README.md) - 사용 가이드
- **대상**: 이 프로젝트를 사용하려는 모든 사람
- **내용**:
  - 프로젝트 개요 및 목적
  - 빠른 시작 가이드
  - 주요 기능 설명
  - API 문서
  - 데이터베이스 스키마
  - 개발 가이드

### 2. [ARCHITECTURE.md](ARCHITECTURE.md) - 설계 근거
- **대상**: 시스템을 수정/확장하려는 개발자
- **내용**:
  - 왜 이렇게 만들어졌는가 (의사결정 근거)
  - 시행착오와 교훈
  - 알고리즘 선택 이유
  - 미래 개발 가이드

### 3. [QUICKSTART.md](QUICKSTART.md) - 5분 요약
- **대상**: 빠르게 프로젝트를 이해하고 실행하려는 사람
- **내용**:
  - 10분 실행 가이드
  - 핵심 개념 1분 요약
  - 자주 묻는 질문

---

## 🗂 프로젝트 구조

```
moniterdc/
│
├── README.md                    ← 📖 전체 가이드
├── ARCHITECTURE.md              ← 🏗 설계 문서
├── QUICKSTART.md                ← ⚡ 빠른 시작
├── PROJECT_SUMMARY.md           ← 📄 이 문서
│
├── engines/                     ← 🤖 핵심 AI 엔진
│   └── analyzers/
│       ├── layered_perception_extractor.py    # 3-Layer 분석
│       ├── optimal_worldview_constructor.py   # 세계관 구성
│       ├── worldview_updater.py               # 자동 업데이트
│       └── deconstruction_generator.py        # 반박 논리 (개발 중)
│
├── dashboard/                   ← 🖥 Next.js 대시보드
│   ├── app/
│   │   ├── page.tsx            # 메인 페이지
│   │   ├── worldviews/[id]/   # 세계관 상세
│   │   └── api/worldviews/    # API
│   └── components/
│
├── supabase/migrations/         ← 🗄 데이터베이스 스키마
│   ├── 100_create_contents.sql
│   ├── 101_create_perceptions.sql
│   ├── 103_create_worldviews.sql
│   └── 203_create_perception_worldview_links.sql
│
├── _deprecated/                 ← 🗑 사용 안 하는 파일들
│   ├── docs/                   # 중간 과정 문서
│   ├── scripts/                # 테스트 스크립트
│   └── README.md               # 왜 보관하는지 설명
│
└── .env                         ← 🔐 환경변수 (git ignore)
```

---

## 🎯 핵심 개념 정리

### 프로젝트 목적
> DC Inside 정치 커뮤니티 담론의 **세계관 구조**를 자동으로 모니터링하고 분석하여, 일반인(특히 더불어민주당 지지자)이 상대방의 사고 체계를 이해할 수 있도록 지원

### 타겟 사용자
- **일반인**: 정치 담론을 이해하고 싶은 비전문가
- **민주당 지지자**: 반대 진영의 논리 구조를 파악하고 싶은 사람
- **온/오프라인 대화 참여자**: 효과적인 대화를 위해 맥락을 이해하고 싶은 사람

### 왜 세계관인가?
- 표면적 주장 반박만으로는 효과 없음
- 심층 믿음(deep beliefs)을 이해해야 함
- 세계관 = 해석 프레임워크 = "왜 그렇게 생각하는가"의 답
- **동적 발견**: 고정된 카테고리가 아닌, 데이터에서 자동으로 패턴 발견

### 3-Layer 분석
```
표면층 (Explicit Claims)
  ↓
암묵층 (Implicit Assumptions)
  ↓
심층 (Deep Beliefs) ← 세계관의 핵심
```

### 계층형 세계관 구조
```
자동 발견된 세계관 (2025-01 기준)
  ├─ 민주당/좌파에 대한 인식
  │   ├─ 독재 재현
  │   └─ 좌파의 사회적 위협
  ├─ 외부 세력의 위협
  │   ├─ 중국의 부정적 영향
  │   └─ 북한의 지속적 위협
  └─ 국내 정치적 불안정
      ├─ 정치적 부패와 무능
      └─ 사법부와 언론의 결탁

※ 세계관은 고정되지 않음 - 새로운 담론 패턴 발견 시 자동 추가/변경
```

---

## 💻 기술 스택

### Backend
- **Python 3.11+** (asyncio)
- **OpenAI GPT-5** (세계관 구성)
- **OpenAI GPT-5-mini** (3-Layer 분석)
- **Supabase** (PostgreSQL + pgvector)

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **TailwindCSS**
- **SWR** (data fetching)

### Infrastructure
- **GitHub Actions** (자동화)
- **Vercel** (대시보드 배포)

---

## 📊 현재 데이터 현황

| 항목 | 개수 | 설명 |
|------|------|------|
| 원본 글 (contents) | 297개 | DC Gallery 정치 갤러리 글 |
| Perception | 297개 | 3-Layer 분석 결과 |
| 세계관 (worldviews) | 6개 | 계층형 구조 (3 대분류) |
| 링크 | 26개 | perception ↔ worldview 연결 |

---

## 🔑 핵심 알고리즘

### 1. 3-Layer 분석 (LayeredPerceptionExtractor)
- **모델**: GPT-5-mini
- **비용**: ~$0.05/글
- **프롬프트**: Structured output + Chain-of-Thought

### 2. 세계관 구성 (OptimalWorldviewConstructor)
- **모델**: GPT-5
- **방식**: Narrative (예시 중심) + Metadata (구조화)
- **구조**: 계층형 (대분류 → 세부)

### 3. Hybrid 매칭
```python
hybrid_score = 0.7 * vector_similarity + 0.3 * keyword_match
```
- **Vector (70%)**: 의미적 유사도
- **Keyword (30%)**: 명시적 매칭
- **임계값**: 0.5 이상만 링크 생성

### 4. 자동 업데이트 (WorldviewUpdater)
- **일일**: 새 글 수집 → 분석 → 매칭
- **주간**: 예시 보강 (Narrative 업데이트)
- **월간**: 세계관 표류 감지 → 재구성 판단

---

## 🚀 실행 명령어 요약

### 자동 모니터링
- GitHub Actions가 자동으로 실행 (설정 완료 시)
- DC Inside uspolitics 갤러리 모니터링
- 새 게시글 자동 수집 → 분석 → 세계관 업데이트

### 수동 실행 (개발자용)

**1. 데이터 수집**
```bash
python scripts/collect_500_posts.py
```

**2. 3-Layer 분석**
```python
import asyncio
from engines.analyzers.layered_perception_extractor import LayeredPerceptionExtractor

async def analyze_all():
    extractor = LayeredPerceptionExtractor()
    # contents 테이블에서 분석되지 않은 글들을 가져와서
    # 각각에 대해 extract_layered_perception() 실행

asyncio.run(analyze_all())
```

**3. 세계관 구성 (자동 발견)**
```python
import asyncio
from engines.analyzers.optimal_worldview_constructor import OptimalWorldviewConstructor

async def main():
    constructor = OptimalWorldviewConstructor()
    await constructor.construct_all()

asyncio.run(main())
```

**4. 지속적 업데이트**
```python
import asyncio
from engines.analyzers.worldview_updater import WorldviewUpdater

async def main():
    updater = WorldviewUpdater()
    await updater.daily_update()

asyncio.run(main())
```

### 대시보드 실행
```bash
cd dashboard
npm run dev
# http://localhost:3000
```

---

## 📈 비용 분석 (월 기준, 일일 100개 글 수집)

| 작업 | 모델 | 단가 | 월 비용 |
|------|------|------|---------|
| 3-Layer 분석 | GPT-4o-mini | $0.05/글 | $150 |
| 세계관 업데이트 | GPT-4o | $0.30/주 | $1.2 |
| **Total** | | | **$151.2** |

---

## 🚧 개발 중 기능

### 1. 반박 논리 생성 (Deconstruction)
- 논리적 결함 분석
- 팩트체크
- 대안적 해석
- 대화 가이드

### 2. 검색 기능
- 키워드로 세계관 검색
- 관련 세계관 추천

### 3. 트렌드 분석
- 세계관 강도 변화 추적
- 새로운 세계관 발견 알림

---

## 🔄 버전 히스토리

| 버전 | 날짜 | 주요 변경사항 |
|------|------|---------------|
| v1.0 | 2024-09 | 공격-방어 논리 매칭 (실패) |
| v2.0 | 2024-10 | RAG 기반 대응 시스템 (한계 발견) |
| v3.0 | 2024-11 | 3-Layer 분석 도입 |
| **v4.0** | **2025-01** | **세계관 구성 시스템 (현재)** |

---

## 📞 문의 및 기여

### Issues
[GitHub Issues](https://github.com/yourusername/moniterdc/issues)

### 기여 방법
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

## 🎓 참고 자료

### 문서
- [README.md](README.md) - 전체 가이드
- [ARCHITECTURE.md](ARCHITECTURE.md) - 설계 문서
- [QUICKSTART.md](QUICKSTART.md) - 빠른 시작

### 코드
- `engines/analyzers/` - 핵심 AI 엔진
- `dashboard/app/` - 대시보드
- `supabase/migrations/` - DB 스키마

### 이론적 배경
- Lakoff & Johnson (1980): *Metaphors We Live By*
- van Dijk (2006): *Discourse and Context*

---

## ✅ 체크리스트 (새로운 개발자용)

### 시스템 이해
- [ ] README.md 전체 읽기
- [ ] QUICKSTART.md로 10분 실행 성공
- [ ] ARCHITECTURE.md "프로젝트 진화 과정" 섹션 읽기

### 코드 파악
- [ ] `LayeredPerceptionExtractor` 코드 읽기
- [ ] `OptimalWorldviewConstructor` 코드 읽기
- [ ] 대시보드 `/worldviews/[id]/page.tsx` 확인

### 데이터 확인
- [ ] Supabase에서 테이블 구조 확인
- [ ] 샘플 perception 데이터 조회
- [ ] 샘플 worldview 데이터 조회

### 실행 테스트
- [ ] 환경변수 설정 완료
- [ ] 대시보드 로컬 실행 성공
- [ ] 세계관 상세 페이지에서 원본 글 확인

---

## 🙏 마지막 말

이 프로젝트는:
- ✅ **3-Layer 분석**으로 담론의 심층 구조 파악
- ✅ **계층형 세계관**으로 해석 프레임워크 조직화
- ✅ **Hybrid 매칭**으로 자동 분류 + 설명 가능성 확보
- ✅ **지속 업데이트**로 동적 세계관 추적
- ✅ **대시보드**로 시각화 및 탐색 가능

**를 달성했습니다.**

하지만 완성된 것이 아닙니다. **진행 중**입니다.

새로운 시도, 실패, 개선을 계속해주세요.
그리고 그 과정을 **문서화**해주세요.

---

**Last Updated**: 2025-01-05
**Version**: 4.0 (Worldview System)
**Status**: Production Ready
