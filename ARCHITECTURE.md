# MoniterDC v2.0 Architecture

> Last Updated: 2025-10-24
> Version: 2.0 (Post-Refactoring)

## 🎯 Mission

**"상대방은 틀린 게 아니라, 다른 세계를 산다"**
(People aren't wrong, they live in different worlds)

A living worldview analysis system that discovers and tracks how different communities perceive the same reality through fundamentally different interpretive frameworks.

---

## 📐 System Architecture

### Two-Part System

```
┌─────────────────────────────────────────────────────────────┐
│                     MoniterDC v2.0                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐         ┌───────────────────────┐   │
│  │  Python Engines  │────────>│  Next.js Dashboard    │   │
│  │                  │         │                       │   │
│  │  - Crawling      │         │  - Visualization      │   │
│  │  - Analysis      │         │  - User Interface     │   │
│  │  - Evolution     │         │  - API Routes         │   │
│  └────────┬─────────┘         └──────────┬────────────┘   │
│           │                              │                │
│           └──────────┬───────────────────┘                │
│                      ▼                                     │
│              ┌──────────────┐                             │
│              │   Supabase   │                             │
│              │  PostgreSQL  │                             │
│              └──────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Project Structure

```
moniterdc/
├── 📁 engines/                  # Python Analysis Engines
│   ├── adapters/               # Data Collection
│   │   ├── base_adapter.py
│   │   └── dc_gallery_adapter.py
│   ├── analyzers/              # Core Analysis (5 engines)
│   │   ├── layered_perception_extractor_v2.py
│   │   ├── reasoning_structure_extractor.py
│   │   ├── worldview_evolution_engine.py
│   │   ├── mechanism_matcher.py
│   │   └── pattern_manager.py
│   ├── archiving/              # Data Lifecycle
│   │   └── content_archiver.py
│   ├── collectors/             # Collection Coordination
│   │   └── content_collector.py
│   └── utils/                  # Utilities
│       ├── supabase_client.py
│       └── embedding_utils.py
│
├── 📁 scripts/                  # Operational Scripts (6 active)
│   ├── auto_collect_recent.py          # 10분마다 자동 수집
│   ├── collect_dc_posts.py             # 수동 수집 도구
│   ├── daily_maintenance.py            # 매일 아카이빙
│   ├── process_new_contents.py         # 분석 파이프라인
│   ├── run_mechanism_matcher.py        # Mechanism matching
│   └── run_worldview_evolution.py      # Worldview evolution
│
├── 📁 dashboard/                # Next.js 14 Dashboard
│   ├── app/                    # App Router
│   │   ├── page.tsx           # Main: ActorCentricWorldviewMap
│   │   ├── worldviews/[id]/   # Detail Page
│   │   └── api/               # API Routes
│   └── components/worldviews/  # 5 active components
│       ├── ActorCentricWorldviewMap.tsx
│       ├── InterpretationComparison.tsx
│       ├── LogicChainVisualizer.tsx
│       ├── MechanismBadge.tsx
│       └── MechanismMatchingExplanation.tsx
│
├── 📁 supabase/                 # Database
│   └── migrations/             # Schema migrations
│
├── 📁 _archive/                 # Archived/Deprecated Code
├── 📁 _deprecated/              # v1.0 deprecated code
└── 📁 _experiments/             # Experimental scripts
```

---

## 🔄 Data Flow

### 1. Collection (10분마다 자동)

```
DC Gallery
    │
    ▼
auto_collect_recent.py
    │ 1. DB에서 max_no 확인
    │ 2. DC에서 100개 가져오기
    │ 3. no > max_no만 필터링
    │ 4. 메타데이터 포함 저장
    ▼
Supabase (contents)
    - published_at ✅
    - author ✅
    - view_count ✅
    - comment_count ✅
    - recommend_count ✅
```

### 2. Analysis Pipeline

```
process_new_contents.py
    │
    ├─> LayeredPerceptionExtractorV2
    │   └─> 3-layer analysis (explicit/implicit/deep)
    │
    ├─> ReasoningStructureExtractor
    │   └─> mechanisms, actor, logic_chain
    │
    └─> MechanismMatcher
        └─> Link perceptions to worldviews
```

### 3. Evolution (매월 수동)

```
run_worldview_evolution.py
    │
    └─> WorldviewEvolutionEngine
        ├─> Analyze 200 recent perceptions
        ├─> Discover new patterns
        ├─> Update existing worldviews
        └─> Archive disappeared worldviews
```

### 4. Lifecycle (매일 자동)

```
daily_maintenance.py
    │
    ├─> Delete contents/perceptions > 90 days
    └─> Print statistics
```

---

## 💾 Database Schema (v2.0)

### Core Tables (4개만 유지)

```sql
-- Original content
contents (
    id UUID PRIMARY KEY,
    source_type TEXT,
    source_url TEXT UNIQUE,
    source_id TEXT,
    title TEXT,
    body TEXT,
    metadata JSONB,              -- author, view_count, comment_count, recommend_count
    published_at TIMESTAMPTZ,    -- ✅ v2.0 추가
    collected_at TIMESTAMPTZ,
    base_credibility FLOAT,
    is_active BOOLEAN DEFAULT true
)

-- 3-layer analysis + v2.0 reasoning structure
layered_perceptions (
    id UUID PRIMARY KEY,
    content_id UUID REFERENCES contents(id),
    -- 3-layer structure
    explicit_claims TEXT[],
    implicit_assumptions TEXT[],
    deep_beliefs TEXT[],
    -- v2.0 reasoning structure
    mechanisms TEXT[],            -- 5 mechanism types
    actor JSONB,                  -- {subject, purpose, methods}
    logic_chain JSONB[],          -- Array of reasoning steps
    extracted_at TIMESTAMPTZ
)

-- Worldviews (living entities)
worldviews (
    id UUID PRIMARY KEY,
    title TEXT,
    description TEXT,
    frame JSONB,                  -- v2.0 structure
    core_subject TEXT,            -- Actor subject
    core_attributes TEXT[],       -- Mechanisms array
    version INTEGER,
    archived BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)

-- Links between perceptions and worldviews
perception_worldview_links (
    id UUID PRIMARY KEY,
    perception_id UUID REFERENCES layered_perceptions(id),
    worldview_id UUID REFERENCES worldviews(id),
    match_score FLOAT,            -- Actor(50%) + Mechanism(30%) + Logic(20%)
    matched_at TIMESTAMPTZ
)
```

---

## 🧠 Core Concepts

### 3-Layer Perception Analysis

Every discourse is analyzed into 3 layers:

```
┌──────────────────────────────────────┐
│ EXPLICIT                             │
│ What is directly stated              │
├──────────────────────────────────────┤
│ IMPLICIT                             │
│ What is assumed/presupposed          │
├──────────────────────────────────────┤
│ DEEP BELIEFS                         │
│ What is unconsciously believed       │
│ (Worldview)                          │
└──────────────────────────────────────┘
```

### 5 Thinking Mechanisms

Each discourse's reasoning structure is decomposed:

1. **즉시_단정 (Instant Conclusion)**
   Observation → Conclusion (skipping verification)

2. **역사_투사 (Historical Projection)**
   Past pattern → Present repetition

3. **필연적_인과 (Inevitable Causation)**
   X → Necessarily Y

4. **네트워크_추론 (Network Reasoning)**
   Connections → Organized conspiracy

5. **표면_부정 (Surface Negation)**
   Surface X / Actually Y

### Actor Structure

Each worldview focuses on an Actor:

```json
{
  "subject": "민주당/좌파",
  "purpose": "권력 유지를 위한 국민 기만",
  "methods": ["언론 장악", "여론 조작", "법 악용"]
}
```

### Logic Pattern

Each worldview has a reasoning structure:

```json
{
  "trigger": "민주당의 행동 관찰",
  "skipped_verification": "실제 근거 확인, 다른 해석 가능성",
  "conclusion": "민주당은 항상 권력을 위해 국민을 속인다"
}
```

---

## 🤖 Automation System

### GitHub Actions (Every 10 minutes)

```yaml
# .github/workflows/worldview_monitoring.yml

1. auto_collect_recent.py
   - Collect new posts (max_no 기준)
   - With metadata

2. process_new_contents.py
   - Extract perceptions (v2.1)
   - Extract reasoning structures
   - Match to worldviews

3. Trigger Vercel deployment
   - Update dashboard
```

### Cron Jobs (Daily at 3 AM)

```bash
# daily_maintenance.py
- Archive contents/perceptions > 90 days
- Print statistics
```

### Manual (Monthly)

```bash
# Worldview Evolution
python3 scripts/run_worldview_evolution.py
python3 scripts/run_mechanism_matcher.py
```

---

## 📊 Data Lifecycle (3-Month Window)

```
Day 0                Day 90               Day 180
  │                    │                    │
  │  Active Data       │   Archived         │  Deleted
  │  (Analyzed)        │   (Read-only)      │
  │                    │                    │
  ▼                    ▼                    ▼
┌────────────────────┬────────────────────┬──────────┐
│ Contents           │ Archive            │          │
│ Perceptions        │ (via is_active)    │   ∅      │
│ Worldview Links    │                    │          │
└────────────────────┴────────────────────┴──────────┘
```

---

## 🎨 Dashboard Architecture

### Tech Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Icons**: Lucide React
- **Database**: Supabase (PostgreSQL)

### Key Pages

**1. Main Page** (`/`)
```tsx
ActorCentricWorldviewMap
├─ Worldview Cards (Actor별 그룹화)
│  ├─ Actor Subject
│  ├─ Mechanisms (badges)
│  └─ Perception Count
└─ Stats
```

**2. Detail Page** (`/worldviews/[id]`)
```tsx
WorldviewDetail
├─ Worldview-level Logic Pattern
│  ├─ Trigger
│  ├─ Skipped Verification
│  └─ Conclusion
├─ Perceptions List
│  ├─ 3-layer Structure
│  ├─ Logic Chain Visualizer
│  └─ Interpretation Comparison
└─ Linked Contents
```

### API Routes

```
GET /api/worldviews
├─ Returns all active worldviews
└─ Parses frame JSON (mechanisms, actor, logic_pattern)

GET /api/worldviews/[id]
├─ Returns worldview details
├─ Linked perceptions (with 3-layer + logic_chain)
├─ Original contents
└─ Stats
```

---

## 🔧 Development

### Python Engines

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Environment (.env)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
ANTHROPIC_API_KEY=your-claude-key

# Run scripts
python3 scripts/auto_collect_recent.py
python3 scripts/process_new_contents.py
python3 scripts/run_worldview_evolution.py
```

### Dashboard

```bash
cd dashboard

# Install
npm install

# Dev
npm run dev              # http://localhost:3000

# Build
npm run build
npm start

# Environment (.env.local)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Database

```bash
# Push migrations
supabase db push

# Migrations
supabase/migrations/
├── 201-203_*.sql    # v2.0 core schema
├── 301_*.sql        # Reasoning structure
├── 401_*.sql        # Remove unused fields
└── 402_*.sql        # Remove deprecated tables
```

---

## 📈 Performance & Scalability

### Current Stats
- **Contents**: 2,312 (1 month)
- **Perceptions**: 0 (분석 전)
- **Worldviews**: 70
- **DB Size**: ~6 MB

### 10-Year Projection

**With 3-month lifecycle:**
- Contents: ~17 MB (90 days rolling)
- Perceptions: ~36 MB
- **Total: ~60-80 MB** (well within 500MB free tier)

**Without lifecycle (theoretical):**
- Total: ~2.5 GB (10 years accumulation)

---

## 🚨 Critical Design Decisions

### 1. Max_No-Based Collection
- ✅ Prevents duplicate collection
- ✅ Works regardless of posting frequency
- ❌ Doesn't handle "끌올" (bumped posts) well

### 2. Metadata Collection
- ✅ `published_at` enables lifecycle management
- ✅ `author`, `view_count` enables quality filtering
- ❌ Requires full page fetch (slower)

### 3. 3-Month Lifecycle
- ✅ Keeps data fresh and relevant
- ✅ Manages database size
- ❌ Loses historical data (acceptable for current analysis)

### 4. Living Worldviews
- ✅ Adapts to discourse changes
- ✅ Data-driven (not pre-defined categories)
- ❌ Requires monthly evolution runs
- ❌ ~63% coverage is normal (not all perceptions form worldviews)

---

## 📚 Key Files

### Documentation
- [README.md](README.md) - Project overview
- [CLAUDE.md](CLAUDE.md) - Claude Code development guide
- [REFACTORING.md](REFACTORING.md) - Latest refactoring summary
- [CLEANUP_COMPLETE.md](CLEANUP_COMPLETE.md) - v2.0 cleanup

### Configuration
- `.env` - Python environment
- `dashboard/.env.local` - Next.js environment
- `requirements.txt` - Python dependencies
- `dashboard/package.json` - Node dependencies

### Migrations
- `supabase/migrations/` - All database schema changes

---

## 🔄 Version History

- **v2.0** (2025-10-14): Clean architecture, 3-layer + 5 mechanisms
- **v2.1** (2025-10-24): Metadata collection, auto-collection, refactoring

---

## 🎯 Next Steps

1. ✅ Metadata collection
2. ✅ Auto-collection system
3. ✅ Project refactoring
4. ⏳ v2.1 perception analysis
5. ⏳ Dashboard enhancements
6. ⏳ Multi-source support (beyond DC Gallery)

---

**Last Updated**: 2025-10-24
**Status**: Operational and clean
