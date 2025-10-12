# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🤖 AI Collaboration Philosophy

> **IMPORTANT: Read [.claude/philosophy.md](.claude/philosophy.md) FIRST**
>
> All development in this project follows the principles defined in the philosophy file.
> This is NOT optional - it defines:
> - How we think and work together
> - Core collaboration principles
> - Respect for existing code and decisions
> - Evolution over revolution approach
>
> **Read it before making any changes.**

---

## 📋 Project: MoniterDC (담론 세계관 분석 시스템)

**Mission**: "상대방은 틀린 게 아니라, 다른 세계를 산다"
- 담론의 3-layer 구조 자동 분석 (표면층/암묵층/심층)
- 메커니즘 기반 세계관 자동 발견 및 진화 추적
- DC Gallery 등 온라인 커뮤니티 담론 분석

---

## 🏗 Architecture

### Two-Part System

**1. Python Analysis Engines** (`engines/`)
- GPT-4o/GPT-5 기반 담론 분석
- 비동기 처리 (asyncio)
- Supabase와 직접 통신

**2. Next.js Dashboard** (`dashboard/`)
- App Router (Next.js 14)
- TypeScript + TailwindCSS
- Supabase client-side queries

### Key Components

```
engines/
├── analyzers/
│   ├── layered_perception_extractor.py    # 3-Layer 분석
│   ├── reasoning_structure_extractor.py   # 5개 메커니즘 추출
│   ├── worldview_evolution_engine.py      # 세계관 자동 업데이트
│   ├── mechanism_matcher.py               # 메커니즘 기반 매칭
│   └── optimal_worldview_constructor.py   # 세계관 자동 발견
├── collectors/
│   └── content_collector.py               # 담론 수집
└── utils/
    └── supabase_client.py                 # DB 클라이언트

dashboard/
├── app/
│   ├── page.tsx                           # 세계관 맵
│   ├── worldviews/[id]/page.tsx           # 세계관 상세
│   └── api/
│       └── worldviews/                    # API routes
└── components/worldviews/                 # 시각화 컴포넌트
```

---

## 🚀 Development Commands

### Python Engines

```bash
# 환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 환경 변수 (.env)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
OPENAI_API_KEY=sk-proj-...

# 새 content 처리
python scripts/process_new_content.py

# 세계관 업데이트 (주간)
python scripts/run_worldview_evolution.py

# 마이그레이션
python scripts/migrate_to_new_system.py
```

### Dashboard

```bash
cd dashboard

# 설치
npm install

# 개발 서버
npm run dev          # http://localhost:3000

# 빌드
npm run build
npm start

# Lint
npm run lint

# 환경 변수 (.env.local)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Database

```bash
# Supabase Dashboard에서 SQL 실행
# supabase/migrations/*.sql 파일 순서대로 실행
# 특히 301_add_reasoning_structure_fields.sql (v2.0 스키마)
```

---

## 🎯 Core Concepts

### 3-Layer Analysis
모든 담론은 3개 층위로 분석됩니다:
- **Explicit**: 직접 말하는 것
- **Implicit**: 전제하는 것
- **Deep Beliefs**: 무의식적으로 믿는 것

### 5 Thinking Mechanisms (v2.0)
각 담론의 추론 구조를 5개 메커니즘으로 분해:
1. 즉시_단정: 관찰 → 결론 (검증 생략)
2. 역사_투사: 과거 → 현재 반복
3. 필연적_인과: X → 반드시 Y
4. 네트워크_추론: 연결 → 조직적 공모
5. 표면_부정: 표면 X / 실제 Y

### Worldview Evolution
세계관은 고정되지 않고 진화합니다:
- 주기적 자동 업데이트 (WorldviewEvolutionEngine)
- 새로운 패턴 자동 발견
- 변화 추적 및 기록

---

## 💡 Development Guidelines

### When Working with Analysis Engines

**Pattern Matching**
- 기존 analyzer 패턴 따르기
- 모든 analyzer는 async/await 사용
- OpenAI API 호출은 try/except로 감싸기
- 결과를 Supabase에 저장

**GPT Model Selection**
- GPT-4o: 빠른 분석 (LayeredPerceptionExtractor, ReasoningStructureExtractor)
- GPT-5: 정교한 구성 (WorldviewEvolutionEngine)
- Cost-aware: 불필요한 재분석 방지

**Database Interactions**
- `engines/utils/supabase_client.py` 사용
- Service key로 서버 측 작업
- Anon key는 dashboard에서만

### When Working with Dashboard

**Data Fetching**
- useEffect + fetch 패턴 사용 (SWR 제거됨)
- API routes: `/api/worldviews/*`
- 에러 처리 필수

**Component Patterns**
- TypeScript 인터페이스는 실제 API 응답 구조와 정확히 일치해야 함
- TailwindCSS for styling
- Lucide React for icons

**API Design**
- RESTful routes in `app/api/`
- Supabase client with anon key
- Return JSON with proper error handling

---

## 🔄 Current State (2025-10-12)

### ✅ Deployment Status: LIVE
**v2.0 System is DEPLOYED and OPERATIONAL**

### Deployed Features
✅ 3-Layer perception extraction (501 perceptions)
✅ 5 Mechanism extraction system
✅ Worldview auto-discovery engine
✅ Mechanism-based matching (910 links, 84.2% coverage)
✅ Evolution tracking system
✅ 9 active v2.0 worldviews
✅ Dashboard running at http://localhost:3000

### Deployment Statistics (2025-10-12)
- **Perceptions analyzed**: 501 with reasoning structures
- **Active worldviews**: 9 mechanism-based worldviews
- **Perception-worldview links**: 910 connections
- **Coverage**: 422/501 perceptions matched (84.2%)
- **Average links**: 1.82 links per perception
- **Old worldviews archived**: 9

### Top Worldviews by Perception Count
1. 온라인 반복 패턴 → 조직적 댓글부대 (182)
2. 민주당/좌파 정보 파악 → 불법 사찰 (159)
3. 정치인 상충 발언 → 의도적 기만 (140)
4. 보수 진영 규모 → 민심 지표 (111)
5. 중국·중국계 관찰 → 침투/범죄 (94)

### Future Enhancements
🚧 Deconstruction logic (반박 논리 생성)
🚧 Dashboard evolution timeline visualization
🚧 Real-time discourse tracking
🚧 Automated weekly evolution cron job
🚧 Multi-community comparison

### Database Schema
- v1.0: migrations 100-106 (legacy)
- v2.0: migrations 201-203, 301 (current)
- See `supabase/migrations/` for details

---

## 📚 Important Files

**Documentation**
- [README.md](README.md) - Project overview
- [.claude/philosophy.md](.claude/philosophy.md) - **Development philosophy (READ FIRST)**
- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) - Technical deep dive
- [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) - v2.0 completion report

**Configuration**
- `.env` - Python environment variables
- `dashboard/.env.local` - Next.js environment variables
- `requirements.txt` - Python dependencies
- `dashboard/package.json` - Node dependencies

---

## 🎯 Testing Philosophy

**Currently**: Manual testing and observation
**Future**: Automated tests for critical analyzers

When adding features:
1. Test with real DC Gallery data
2. Verify Supabase storage
3. Check dashboard rendering
4. Monitor OpenAI costs

---

## 🚨 Critical Notes

**DO NOT**
- 기존 세계관 구조 임의 변경 (진화 시스템 사용)
- 분석 로직 변경 시 기존 데이터와 호환성 확인 필수
- Cost-heavy operations without batching
- Dashboard에서 service key 사용

**ALWAYS**
- Follow [.claude/philosophy.md](.claude/philosophy.md) principles
- Match existing code patterns
- Consider OpenAI API costs
- Test with real discourse data
- Respect the 3-layer + mechanism structure

---

**Last Updated**: 2025-01-05
**Version**: 2.0 (Mechanism-based Evolution System)
