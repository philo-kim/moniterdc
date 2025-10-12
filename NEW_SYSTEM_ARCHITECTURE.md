# 세계관 분석 시스템 아키텍처 v2.0

**살아있는 세계관 시스템 - Mechanism-based Evolution**

---

## 시스템 개요

DC Gallery 정치 커뮤니티의 담론을 실시간으로 분석하여 **살아있는 세계관**을 추적하는 시스템입니다.

**핵심 특징:**
- ✅ **메커니즘 기반**: 주제가 아닌 사고 구조 분석
- ✅ **실시간 진화**: 주기적으로 세계관 재구성
- ✅ **자동 감지**: 새로운 패턴 자동 발견
- ✅ **버전 관리**: 담론 변화 추적

---

## 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      Data Collection                         │
│  DC Gallery Crawler → Contents (title, body, metadata)      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Reasoning Analysis                         │
│  ReasoningStructureExtractor (GPT-4o)                       │
│  → 5 Mechanisms + Actor + Logic Chain                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Worldview Matching                        │
│  MechanismMatcher                                            │
│  → Perception ↔ Worldview Links                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 Periodic Evolution (Weekly)                  │
│  WorldviewEvolutionEngine (GPT-5)                           │
│  → Detect Changes → Update Worldviews                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Visualization                           │
│  Next.js Dashboard                                           │
│  → Worldview Explorer + Evolution Timeline                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 핵심 컴포넌트

### 1. ReasoningStructureExtractor

**파일**: `engines/analyzers/reasoning_structure_extractor.py`

**역할**: Content → Reasoning Structure 변환

**입력**:
```json
{
  "id": "content-uuid",
  "title": "민주, 지귀연 핸드폰 교체 어떻게 알았나",
  "body": "..."
}
```

**출력** (`layered_perceptions` 테이블):
```json
{
  "mechanisms": ["즉시_단정", "역사_투사", "네트워크_추론"],
  "skipped_steps": ["정보 출처 탐색", "합법 가능성 검토"],
  "actor": {
    "subject": "민주당/좌파",
    "purpose": "권력 유지",
    "methods": ["사찰", "협박"]
  },
  "logic_chain": [
    "유심교체 정보 파악",
    "불법으로 단정",
    "독재 시도"
  ],
  "consistency_pattern": "정보_파악_불법_해석"
}
```

**사용**:
```python
from engines.analyzers.reasoning_structure_extractor import ReasoningStructureExtractor

extractor = ReasoningStructureExtractor()
perception_id = await extractor.extract(content)
```

---

### 2. WorldviewEvolutionEngine

**파일**: `engines/analyzers/worldview_evolution_engine.py`

**역할**: 주기적으로 세계관 재구성 및 변화 감지

**프로세스**:
1. 최근 200개 perception 로드
2. GPT-5로 새 세계관 추출
3. 기존 세계관과 비교
4. 변화 감지 (신규/소멸/진화/유지)
5. 유의미한 변화 시 업데이트

**출력**:
```json
{
  "timestamp": "2025-01-11T12:00:00",
  "changes_detected": true,
  "summary": "새로운 '온라인 반복 패턴 → 댓글부대' 세계관 등장",
  "new_count": 1,
  "disappeared_count": 0,
  "evolved_count": 2,
  "stable_count": 6
}
```

**사용**:
```python
from engines.analyzers.worldview_evolution_engine import WorldviewEvolutionEngine

engine = WorldviewEvolutionEngine()
report = await engine.run_evolution_cycle(sample_size=200)
```

---

### 3. MechanismMatcher

**파일**: `engines/analyzers/mechanism_matcher.py`

**역할**: Perception을 Worldview에 매칭

**매칭 알고리즘**:
```
Score = 0.5 × Actor_match + 0.3 × Mechanism_match + 0.2 × Logic_match
```

**Threshold**: 0.4 (조정 가능)

**사용**:
```python
from engines.analyzers.mechanism_matcher import MechanismMatcher

matcher = MechanismMatcher()
links_created = await matcher.match_all_perceptions(threshold=0.4)
```

---

## 운영 가이드

### 초기 설정

**1. Schema Migration**
```bash
# supabase/migrations/301_add_reasoning_structure_fields.sql 실행
```

**2. 데이터 마이그레이션**
```bash
python scripts/migrate_to_new_system.py
```

---

### 일상 운영

**1. 새 Content 처리**
```bash
python scripts/process_new_content.py
```

**2. 주기적 세계관 업데이트 (매주)**
```bash
python scripts/run_worldview_evolution.py
```

---

## 상세 문서

전체 상세 내용은 다음 파일 참조:
- [SYSTEM_TRANSITION_PLAN.md](SYSTEM_TRANSITION_PLAN.md) - 전환 계획
- [FINAL_ANALYSIS_RESULTS.md](FINAL_ANALYSIS_RESULTS.md) - 분석 결과
