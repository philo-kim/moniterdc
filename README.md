# 담론 세계관 분석 시스템 v2.0 (Discourse Worldview Analyzer)

> **"상대방은 틀린 게 아니라, 다른 세계를 산다"**
> 같은 사건을 보고도 완전히 다르게 해석하는 이유를 이해하기 위한 살아있는 세계관 분석 시스템

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

**🎉 v2.0 배포 완료 (2025-10-12): 메커니즘 기반 살아있는 세계관 시스템**
- ✅ 501개 perception 분석 완료 (5개 핵심 메커니즘 추출)
- ✅ 9개 v2.0 세계관 생성 및 운영 중
- ✅ 910개 perception-worldview 링크 (84.2% 커버리지)
- ✅ Dashboard 운영: http://localhost:3000

---

## 📋 목차

- [핵심 통찰](#-핵심-통찰)
- [왜 세계관인가](#-왜-세계관인가)
- [3-Layer 분석 방법론](#-3-layer-분석-방법론)
- [시스템 개요](#-시스템-개요)
- [빠른 시작](#-빠른-시작)
- [사례: DC Gallery 분석](#-사례-dc-gallery-분석)
- [기술 아키텍처](#-기술-아키텍처)
- [개발 가이드](#-개발-가이드)

---

## 💡 핵심 통찰

### 문제: 대화가 통하지 않는 이유

같은 뉴스를 보고도 사람들은 완전히 다르게 반응합니다:

**사건**: "정치인 A가 발언 B를 했다"

**반응 1**: "이건 명백한 독재 시도다"
**반응 2**: "정상적인 정치 활동이잖아"

→ 단순히 "사실"을 제시해도 대화가 안 됩니다. 왜일까요?

### 답: 서로 다른 해석 프레임워크(세계관)

사람들은 **같은 사실을 다른 세계관으로 해석**합니다:

```
같은 사건
   ↓
세계관 A: "과거 독재 → 현재 재현" 프레임으로 해석
세계관 B: "민주주의 절차" 프레임으로 해석
   ↓
완전히 다른 의미 도출
```

**표면적 반박은 효과가 없습니다. 심층 세계관이 다르기 때문입니다.**

### 해결: 세계관 구조 이해

이 시스템은:
1. 담론에서 **세계관 구조를 자동으로 추출**
2. **표면 주장 ↔ 심층 믿음의 연결고리** 시각화
3. **왜 그렇게 생각하는지**의 논리 연쇄 재구성

→ **비로소 대화가 가능한 층위를 찾을 수 있습니다**

---

## 🌍 왜 세계관인가?

### 기존 접근의 한계

| 기존 방식 | 문제점 | 결과 |
|---------|--------|------|
| 팩트체크 | "사실"만 제시 | 해석 프레임이 다르면 소용없음 |
| 개별 반박 | 표면 주장만 공격 | 심층 믿음은 그대로 남음 |
| 논리 지적 | 형식적 오류 지적 | 감정적 확신은 변하지 않음 |

**→ 평행선을 긋습니다**

### 세계관 접근

```
표면층 (Explicit)
  "민주당이 유심교체 정보를 불법으로 얻었다"
     ↓ (전제)
암묵층 (Implicit)
  "민주당은 권력을 위해 불법을 서슴지 않는다"
     ↓ (믿음)
심층 (Deep Belief)
  "좌파/민주당은 본질적으로 독재 성향을 가지고 있다"
```

**심층 믿음을 이해하지 못하면, 표면 주장을 아무리 반박해도 변하지 않습니다.**

### 이 시스템이 제공하는 것

1. **구조 이해**: 주장의 3층 구조 자동 분석
2. **맥락 파악**: 왜 그렇게 생각하게 됐는지 논리 연쇄 추적
3. **대화 전략**: 어느 층위에서 대화가 가능한지 판단

---

## 🔬 분석 방법론

### v2.0 새로운 접근: 메커니즘 기반 분석

담론을 **5개 핵심 메커니즘**으로 분해합니다:

#### 5개 사고 메커니즘

1. **즉시_단정**: 관찰 → (검증 생략) → 결론
2. **역사_투사**: 과거 패턴 → 현재 반복
3. **필연적_인과**: X → 반드시 Y
4. **네트워크_추론**: 연결 → 조직적 공모
5. **표면_부정**: 표면 X / 실제 Y

### 실제 발견 (DC Gallery 분석)

- **즉시_단정**: 100% (모든 글)
- **역사_투사**: 60.7%
- **필연적_인과**: 59.9%
- **네트워크_추론**: 52.3%
- **표면_부정**: 24.0%

→ 이 커뮤니티의 **핵심 사고 구조**를 수치로 드러냄

### 기존 3-Layer 분석 (호환성 유지)

담론은 **3개 층위**로도 구성됩니다:

#### Layer 1: 표면층 (Explicit Layer)
**글에서 직접 말하는 것**

```json
{
  "subject": "민주당",
  "predicate": "유심교체 정보를 불법으로 얻었다",
  "quote": "유심교체를 어떻게 알아"
}
```

#### Layer 2: 암묵층 (Implicit Assumptions)
**당연하다고 전제하는 것**

```json
[
  "민주당은 통신사를 협박해서 정보를 얻는다",
  "이런 사찰은 독재의 시작이다"
]
```

#### Layer 3: 심층 (Deep Beliefs)
**무의식적으로 믿는 것**

```json
[
  "민주당/좌파는 과거 독재정권처럼 사찰로 반대파를 제거한다",
  "지금의 작은 사찰이 곧 전면적 감시독재 사회로 발전한다"
]
```

### 왜 3층인가?

```
표면만 공격 → "그건 그렇고 말고!" (방어)
암묵 전제 건드림 → "음... 그럴 수도?" (재고)
심층 믿음 이해 → "아 그렇게 보는구나" (대화 가능)
```

**같은 층위에서 대화해야 통합니다.**

### 세계관 자동 발견

시스템은 고정된 카테고리를 강요하지 않습니다:

1. **패턴 발견**: 여러 글의 심층 믿음에서 공통 패턴 추출
2. **자동 구성**: AI가 세계관 구조를 데이터 기반으로 생성
3. **동적 업데이트**: 새로운 담론 패턴이 나타나면 세계관 추가/수정

**→ 데이터가 말하게 합니다, 분석자의 편견을 강요하지 않습니다**

---

## 🎯 시스템 개요

### 전체 플로우

```mermaid
graph TB
    A[담론 수집] -->|크롤링/입력| B[원문 저장]
    B -->|3-Layer 분석| C[세계관 구조 추출]
    C -->|패턴 발견| D[세계관 자동 구성]
    D -->|시각화| E[대시보드]

    F[GPT-4o] -.->|분석| C
    F -.->|구성| D
```

### 주요 컴포넌트 (v2.0)

#### 1. ReasoningStructureExtractor ✨ NEW
각 글의 추론 구조 분석
- 5개 메커니즘 자동 추출
- GPT-4o 활용 (빠름)
- 비용: ~$0.05/글

#### 2. WorldviewEvolutionEngine ✨ NEW
살아있는 세계관 시스템
- 주기적 자동 업데이트
- 변화 감지 및 추적
- GPT-5 활용 (정확함)

#### 3. MechanismMatcher ✨ NEW
메커니즘 기반 매칭
- Actor (50%) + Mechanism (30%) + Logic (20%)
- 해석 가능한 점수
- 기존 임베딩 방식 대체

#### 4. Dashboard (업데이트 예정)
세계관 탐색 + 진화 추적 UI
- 메커니즘 분포 차트
- 세계관 진화 타임라인
- 실시간 담론 변화 추적

---

## 🚀 빠른 시작

### v2.0 시스템 배포

**1. Schema Migration**
```bash
# Supabase Dashboard에서 SQL 실행
# supabase/migrations/301_add_reasoning_structure_fields.sql
```

**2. 데이터 마이그레이션**
```bash
python scripts/migrate_to_new_system.py

# 이 스크립트는:
# - 501개 perception에 reasoning structure 추가
# - 기존 세계관 아카이브
# - 새 9개 세계관 생성
# - Mechanism 기반 재매칭
```

**3. 일상 운영**
```bash
# 새 content 처리
python scripts/process_new_content.py

# 주간 세계관 업데이트 (매주 일요일)
python scripts/run_worldview_evolution.py
```

### 상세 가이드

- [SYSTEM_TRANSITION_PLAN.md](SYSTEM_TRANSITION_PLAN.md) - 전환 계획
- [NEW_SYSTEM_ARCHITECTURE.md](NEW_SYSTEM_ARCHITECTURE.md) - 아키텍처
- [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) - 완료 보고서

---

### 기존 설치 방법 (참고)

```bash
# 저장소 클론
git clone https://github.com/yourusername/moniterdc.git
cd moniterdc

# Python 환경
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 대시보드 환경
cd dashboard
npm install
```

### 환경변수

```bash
# .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_KEY=sk-proj-...

# dashboard/.env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### 3. 실행

```bash
# 1. 데이터 수집 (예: DC Gallery)
python scripts/collect_500_posts.py

# 2. 3-Layer 분석
python -c "
import asyncio
from engines.analyzers.layered_perception_extractor import LayeredPerceptionExtractor

async def main():
    extractor = LayeredPerceptionExtractor()
    # 수집된 데이터 분석

asyncio.run(main())
"

# 3. 세계관 자동 구성
python -c "
import asyncio
from engines.analyzers.optimal_worldview_constructor import OptimalWorldviewConstructor

async def main():
    constructor = OptimalWorldviewConstructor()
    await constructor.build_hierarchical_worldviews()

asyncio.run(main())
"

# 4. 대시보드
cd dashboard
npm run dev
# http://localhost:3000
```

---

## 📱 사례: DC Gallery 분석

### 적용 대상

**DC Inside 정치 커뮤니티** (예: 미국정치 갤러리)
- 강한 정치적 성향의 담론
- 체계적인 세계관 기반 해석
- 일반 담론과의 해석 격차가 큼

### 발견된 세계관 예시 (2025-01 기준)

#### 세계관: "독재 재현"

**Narrative (이야기 구조)**
```
민주당은 과거 독재 정권의 방식을 재현하고 있다.

예시: 유심교체 정보 사건
- DC Gallery 해석:
  사찰을 통한 독재적 통치를 시도하고 있다

- 일반적 해석:
  정치적 논란 속의 정보 유출 사건

- 해석 차이의 핵심:
  의도적 독재 시도 vs 정보 유출 문제

논리 연쇄: 사찰 → 권력 장악 → 독재 사회
```

**Metadata (구조 분석)**
```json
{
  "core": {
    "primary_subject": "민주당",
    "primary_attribute": "독재적 성향"
  },

  "interpretation_frame": {
    "historical_lens": {
      "reference_period": "과거 독재 시대",
      "projection_logic": "과거 패턴 → 현재 반복"
    },

    "slippery_slope": {
      "trigger": "사찰 사건",
      "escalation": "권력 장악 시도",
      "endpoint": "독재 사회"
    }
  },

  "emotional_drivers": {
    "primary": "불신",
    "urgency_level": "높음"
  }
}
```

### 통계

- **원본 글**: 297개
- **분석 완료**: 297개 (3-Layer)
- **발견된 세계관**: 6개 (계층형)
- **세계관별 분포**:
  - 중국의 부정적 영향: 10개
  - 좌파의 사회적 위협: 7개
  - 독재 재현: 5개
  - 북한의 지속적 위협: 3개
  - 사법부와 언론의 결탁: 1개

---

## 🏗 기술 아키텍처

### 기술 스택

**백엔드**
- Python 3.11+ (asyncio)
- OpenAI GPT-4o / GPT-4o-mini
- Supabase (PostgreSQL + pgvector)

**프론트엔드**
- Next.js 14 (App Router)
- TypeScript
- TailwindCSS

**인프라**
- GitHub Actions (자동화)
- Vercel (배포)

### 데이터베이스 스키마

```sql
-- 원본 글
CREATE TABLE contents (
    id UUID PRIMARY KEY,
    title TEXT,
    body TEXT,
    source_url TEXT,
    published_at TIMESTAMPTZ
);

-- 3-Layer 분석 결과
CREATE TABLE layered_perceptions (
    id UUID PRIMARY KEY,
    content_id UUID REFERENCES contents(id),
    explicit_claims JSONB,
    implicit_assumptions JSONB,
    deep_beliefs JSONB,
    worldview_hints TEXT
);

-- 세계관
CREATE TABLE worldviews (
    id UUID PRIMARY KEY,
    title TEXT,
    frame JSONB,  -- { category, subcategory, narrative, metadata }
    strength_overall FLOAT,
    total_perceptions INT
);

-- perception ↔ worldview 연결
CREATE TABLE perception_worldview_links (
    id UUID PRIMARY KEY,
    perception_id UUID REFERENCES layered_perceptions(id),
    worldview_id UUID REFERENCES worldviews(id),
    relevance_score FLOAT
);
```

### 프로젝트 구조

```
moniterdc/
├── engines/                    # 핵심 분석 엔진
│   ├── analyzers/
│   │   ├── layered_perception_extractor.py  # 3-Layer 분석
│   │   ├── optimal_worldview_constructor.py # 세계관 자동 발견
│   │   ├── hybrid_perception_matcher.py     # 매칭 엔진
│   │   └── worldview_updater.py            # 자동 업데이트
│   ├── collectors/
│   │   └── content_collector.py            # 데이터 수집
│   └── utils/
│
├── dashboard/                  # Next.js 대시보드
│   ├── app/
│   │   ├── page.tsx           # 메인: 세계관 맵
│   │   └── worldviews/[id]/page.tsx  # 상세
│   └── components/
│
├── supabase/migrations/        # DB 스키마
│
└── scripts/                    # 실행 스크립트
```

---

## 👨‍💻 개발 가이드

### 핵심 클래스 사용법

#### LayeredPerceptionExtractor

```python
from engines.analyzers.layered_perception_extractor import LayeredPerceptionExtractor

extractor = LayeredPerceptionExtractor()
perception = await extractor.extract({
    'id': '...',
    'title': '...',
    'body': '...'
})
```

#### OptimalWorldviewConstructor

```python
from engines.analyzers.optimal_worldview_constructor import OptimalWorldviewConstructor

constructor = OptimalWorldviewConstructor()

# 세계관 자동 발견
worldviews = await constructor.build_hierarchical_worldviews()

# perception 매칭
await constructor.match_perceptions_to_worldviews()
```

#### WorldviewUpdater

```python
from engines.analyzers.worldview_updater import WorldviewUpdater

updater = WorldviewUpdater()

# 일일 업데이트
await updater.daily_update()

# 재구성 필요 시
await updater.check_and_rebuild_if_needed()
```

### API 엔드포인트

```typescript
// 세계관 목록
GET /api/worldviews
Response: { worldviews: [...], pagination: {...} }

// 세계관 상세
GET /api/worldviews/:id
Response: {
  ...worldview,
  perceptions: [...],     // 연결된 perception
  contents: [...],        // 원본 글
  strength_history: [...] // 강도 변화
}
```

### 자동화 (GitHub Actions)

```yaml
# .github/workflows/daily_update.yml
name: Daily Worldview Update

on:
  schedule:
    - cron: '0 2 * * *'  # 매일 오전 2시
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run daily update
        run: |
          python -c "
          import asyncio
          from engines.analyzers.worldview_updater import WorldviewUpdater
          asyncio.run(WorldviewUpdater().daily_update())
          "
```

---

## 🔄 확장 가능성

### 다른 도메인 적용

이 방법론은 DC Gallery에만 국한되지 않습니다:

**적용 가능 영역**
- 온라인 커뮤니티 담론 분석
- 소셜 미디어 해석 프레임 연구
- 정치/사회 이슈 세계관 매핑
- 조직 내부 커뮤니케이션 갈등 분석

**필요한 것**
1. 담론 데이터 수집 어댑터 구현
2. 도메인 특성에 맞는 프롬프트 조정
3. 세계관 카테고리는 자동 발견되므로 수정 불필요

### 개발 중 기능

#### 1. 반박 논리 생성 (Deconstruction)
각 세계관에 대한 대응 전략:
- 논리적 결함 지적
- 팩트체크
- 대안적 해석 제시
- 감정적 이해
- 대화 가이드

#### 2. 검색 및 추천
- 키워드로 세계관 검색
- 관련 세계관 추천
- 유사 담론 패턴 발견

#### 3. 트렌드 분석
- 세계관 강도 변화 추적
- 새로운 세계관 발견 알림
- 담론 지형 변화 시각화

---

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이센스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 📞 문의

- Issues: [GitHub Issues](https://github.com/yourusername/moniterdc/issues)
- Email: your.email@example.com

---

## 🙏 감사의 말

이 프로젝트는 다음 기술과 철학을 기반으로 합니다:
- OpenAI GPT-4o (분석 엔진)
- Supabase (데이터 저장)
- Next.js (시각화)
- **"이해는 동의가 아니다. 이해는 대화의 시작이다"**

---

**Built with ❤️ for bridging epistemic gaps**

*"The goal is not to prove who is right, but to understand why we see differently"*

Last Updated: 2025-01-05
