# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 📋 Project: MoniterDC v2.0

**Mission**: "상대방은 틀린 게 아니라, 다른 세계를 산다" (People aren't wrong, they live in different worlds)

A living worldview analysis system that:
- Extracts 3-layer discourse structures (explicit/implicit/deep beliefs)
- Discovers worldview patterns through mechanism-based analysis
- Tracks worldview evolution over time
- Analyzes online community discourse (DC Gallery, etc.)

**Current Status (2025-10-14)**: v2.0 deployed and operational
- 501 perceptions analyzed with 5 mechanisms
- 7 active worldviews
- Clean architecture after major cleanup

---

## 🏗 Architecture

### Two-Part System

**1. Python Analysis Engines** (`engines/analyzers/`)
- GPT-4o/GPT-5 based discourse analysis
- Async processing (asyncio)
- Direct Supabase communication

**2. Next.js Dashboard** (`dashboard/`)
- Next.js 14 App Router
- TypeScript + TailwindCSS
- Client-side Supabase queries

### Core Components (v2.0 Clean State)

```
engines/analyzers/           # 4 active engines only
├── layered_perception_extractor.py     # 3-layer analysis
├── reasoning_structure_extractor.py    # Extract 5 mechanisms + actor + logic_chain
├── worldview_evolution_engine.py       # Auto-discover/update worldviews
└── mechanism_matcher.py                # Link perceptions to worldviews

dashboard/
├── app/
│   ├── page.tsx                        # Main: ActorCentricWorldviewMap
│   ├── worldviews/[id]/page.tsx        # Detail page
│   └── api/worldviews/                 # API routes
└── components/worldviews/              # 5 active components only
    ├── ActorCentricWorldviewMap.tsx
    ├── InterpretationComparison.tsx
    ├── LogicChainVisualizer.tsx
    ├── MechanismBadge.tsx
    └── MechanismMatchingExplanation.tsx
```

---

## 🚀 Development Commands

### Python Engines

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Environment (.env)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
OPENAI_API_KEY=sk-proj-...

# Process new content
python3 scripts/process_new_content.py

# Run evolution cycle (weekly recommended)
python3 scripts/run_worldview_evolution.py

# Run mechanism matcher
python3 scripts/run_mechanism_matcher.py
```

### Dashboard

```bash
cd dashboard

# Install
npm install

# Dev server
npm run dev          # http://localhost:3000

# Build
npm run build
npm start

# Lint
npm run lint

# Environment (.env.local)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Database

```bash
# Push migrations to Supabase
supabase db push

# Migrations are in supabase/migrations/
# - 201-203: v2.0 core schema (layered_perceptions)
# - 301: Reasoning structure fields (mechanisms, actor, logic_chain)
# - 401: Removed unused strength/temporal fields
# - 402: Removed deprecated tables (12 tables cleaned up)
```

---

## 🎯 Core Concepts

### 3-Layer Analysis

Every discourse is analyzed into 3 layers:
- **Explicit**: What is directly stated
- **Implicit**: What is assumed/presupposed
- **Deep Beliefs**: What is unconsciously believed (worldview)

### 5 Thinking Mechanisms (v2.0)

Each discourse's reasoning structure is decomposed into 5 mechanisms:
1. **즉시_단정** (Instant Conclusion): Observation → Conclusion (skipping verification)
2. **역사_투사** (Historical Projection): Past pattern → Present repetition
3. **필연적_인과** (Inevitable Causation): X → Necessarily Y
4. **네트워크_추론** (Network Reasoning): Connections → Organized conspiracy
5. **표면_부정** (Surface Negation): Surface X / Actually Y

### Worldview Evolution

Worldviews are living entities that evolve:
- **Periodic auto-update** (WorldviewEvolutionEngine)
- **New pattern discovery** (data-driven, not predefined)
- **Change tracking** (new/disappeared/evolved worldviews)
- **Sample-based analysis** (200 recent perceptions for current discourse)

### Actor Structure

Each worldview focuses on an Actor with:
- **Subject**: Who/what is the focus (e.g., "민주당/좌파")
- **Purpose**: Why they act (from logic_pattern conclusion)
- **Methods**: How they act (from examples)

### Logic Pattern

Each worldview has a reasoning structure:
- **Trigger**: Starting observation
- **Skipped Verification**: What verification steps are skipped
- **Conclusion**: Final interpretation

---

## 💾 Database Schema (v2.0 Clean)

### 4 Tables Only

```sql
-- Original content
contents (id, title, body, source_url, published_at)

-- 3-layer analysis + v2.0 fields
layered_perceptions (
    id, content_id,
    -- 3-layer structure
    explicit_claims, implicit_assumptions, deep_beliefs,
    -- v2.0 additions
    mechanisms,      -- Array of 5 mechanism types
    actor,           -- JSON: {subject, purpose, methods}
    logic_chain      -- Array of reasoning steps
)

-- Worldviews
worldviews (
    id, title, description,
    frame,              -- JSON with v2.0 structure
    core_subject,       -- Actor subject
    core_attributes,    -- Mechanisms array
    version, archived
)

-- Links
perception_worldview_links (
    perception_id, worldview_id,
    match_score  -- Actor(50%) + Mechanism(30%) + Logic(20%)
)
```

### Removed in Cleanup (2025-10-14)

- 12 deprecated tables deleted
- 10 unused worldviews fields removed
- Old strength/temporal tracking removed

---

## 💡 Development Guidelines

### When Working with Analysis Engines

**Core Engines (v2.0)**
1. `layered_perception_extractor.py` - Creates 3-layer analysis
2. `reasoning_structure_extractor.py` - Extracts mechanisms, actor, logic_chain
3. `worldview_evolution_engine.py` - Discovers and evolves worldviews
4. `mechanism_matcher.py` - Links perceptions to worldviews

**Pattern to Follow**
- All analyzers use async/await
- OpenAI API calls wrapped in try/except
- Results stored in Supabase
- Use `engines/utils/supabase_client.py` with service key

**Model Selection**
- GPT-4o: Fast analysis (perception extraction, structure analysis)
- GPT-5: Sophisticated reasoning (worldview evolution)
- Cost-aware: Avoid unnecessary re-analysis

### When Working with Dashboard

**Data Fetching**
- Use `useEffect + fetch` pattern (SWR removed)
- API routes: `/api/worldviews/*`
- Always handle errors and loading states

**Component Patterns**
- TypeScript interfaces must match exact API response structure
- TailwindCSS for styling
- Lucide React for icons

**Key Points**
- API routes parse `frame` JSON field from worldviews table
- Worldview detail page shows:
  - Worldview-level logic_pattern (trigger → skipped → conclusion)
  - Individual perception-level 3-layer + logic_chain
- Main page uses Actor-centric grouping

### API Structure

```typescript
// GET /api/worldviews
{
  worldviews: [
    {
      ...dbFields,
      mechanisms: parsed from frame.core_mechanisms,
      actor: parsed from frame.actor,
      logic_chain: parsed from frame.logic_pattern
    }
  ]
}

// GET /api/worldviews/[id]
{
  ...worldview,
  mechanisms, actor, logic_chain, // parsed from frame
  layered_perceptions: [...],     // with 3-layer + logic_chain
  contents: [...],                // original posts
  stats: { total_perceptions, total_contents }
}
```

---

## 🔄 System Evolution Workflow

### Weekly Evolution Cycle

```bash
# 1. Run evolution engine
python3 scripts/run_worldview_evolution.py
# → Generates _evolution_report_YYYYMMDD_HHMMSS.json
# → Detects: new worldviews, disappeared, evolved, stable
# → Auto-applies if significant changes detected

# 2. Run mechanism matcher
python3 scripts/run_mechanism_matcher.py
# → Re-links perceptions to worldviews
# → Updates worldview perception counts
```

### Evolution Report Structure

```json
{
  "changes_detected": true,
  "new_count": 1,
  "disappeared_count": 5,
  "evolved_count": 13,
  "stable_count": 1,
  "summary": "Description of changes..."
}
```

### Living System Philosophy

- Worldviews are NOT fixed categories
- They emerge from discourse patterns
- They evolve as discourse changes
- They disappear when no longer present
- Sample size: 200 recent perceptions (not all data)
- Coverage: ~63% is normal (not all perceptions form worldviews)

---

## 🚨 Critical Notes

**DO NOT**
- Change existing worldview structures manually (use evolution system)
- Add back removed tables/fields (they were carefully cleaned up)
- Use service key in dashboard client code
- Run expensive operations without batching
- Assume 100% coverage is the goal (it's a living system)

**ALWAYS**
- Match existing code patterns exactly
- Consider OpenAI API costs
- Test with real discourse data
- Respect the 3-layer + mechanism structure
- Use async/await for all engine operations

**Recent Cleanup (2025-10-14)**
- Removed 12 deprecated tables
- Removed 10 unused worldview fields
- Moved 5 deprecated engines to `_deprecated/`
- Moved 3 deprecated pages to `_deprecated/`
- Moved 6 deprecated components to `_deprecated/`
- System is now clean v2.0 architecture only

---

## 📚 Important Files

**Core Documentation**
- `README.md` - Project overview and concepts
- `CLEANUP_COMPLETE.md` - Recent cleanup summary
- `CLAUDE.md` (this file) - Development guide

**Configuration**
- `.env` - Python environment (service key)
- `dashboard/.env.local` - Next.js environment (anon key)
- `requirements.txt` - Python dependencies
- `dashboard/package.json` - Node dependencies

**Migrations**
- `supabase/migrations/201-203_*.sql` - Core v2.0 schema
- `supabase/migrations/301_*.sql` - Reasoning structure fields
- `supabase/migrations/401_*.sql` - Remove unused fields
- `supabase/migrations/402_*.sql` - Remove deprecated tables

---

## 🔧 Common Tasks

### Adding New Content

```bash
# Collect new posts
python3 scripts/collect_500_posts.py

# Process through pipeline
python3 scripts/process_new_content.py
# → Creates layered_perceptions
# → Extracts reasoning structures
# → Links to existing worldviews
```

### Updating Worldviews

```bash
# Weekly or when discourse shifts significantly
python3 scripts/run_worldview_evolution.py
python3 scripts/run_mechanism_matcher.py
```

### Deploying Dashboard

```bash
cd dashboard
npm run build
# Deploy to Vercel or your hosting

# Ensure environment variables are set:
# - NEXT_PUBLIC_SUPABASE_URL
# - NEXT_PUBLIC_SUPABASE_ANON_KEY
```

---

**Last Updated**: 2025-10-14
**Version**: 2.0 (Post-cleanup, clean architecture)
**Status**: Operational with 7 active worldviews

---

## 🔄 자동화 시스템 (GitHub Actions)

### Worldview Monitoring (.github/workflows/worldview_monitoring.yml)

**스케줄**: 10분마다 자동 실행

**프로세스**:
```
1. DC 갤러리 크롤링 (collect_500_posts.py)
2. 새 글 분석 (process_new_contents.py)
   - v2.1 perception 추출 (필터링 적용)
   - Reasoning structure 추출
   - Mechanism matching
3. Vercel 배포 트리거
```

**필요한 GitHub Secrets**:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `ANTHROPIC_API_KEY` (Claude API)
- `VERCEL_DEPLOY_HOOK`

---

## 📅 운영 스케줄

### GitHub Actions (자동)
- **10분마다**: 크롤링 + 분석 + 배포
  - DC 갤러리 새 글 수집
  - v2.1 필터링으로 perception 추출
  - 세계관에 자동 매칭

### Cron Jobs (수동 설정 필요)
- **매일 새벽 3시**: Daily Maintenance
  ```bash
  0 3 * * * python3 scripts/daily_maintenance.py >> logs/daily.log 2>&1
  ```
  - Contents/Perceptions 아카이빙 (90일)
  - Pattern decay
  - Dead patterns cleanup
  - Lifecycle snapshots

### 수동 실행 (필요시)
- **매월**: Worldview Evolution
  ```bash
  python3 scripts/run_worldview_evolution.py
  python3 scripts/run_mechanism_matcher.py
  ```

