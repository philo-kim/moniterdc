# 프로젝트 정리 계획

**현재 상태**: 루트에 55개 파일 난잡하게 존재
**목표**: 깔끔한 v2.0 프로젝트 구조

---

## 📊 현재 문제점

### 루트 디렉토리 (55개 파일)
- **테스트 파일**: 22개 (`test_*.py`)
- **결과 JSON**: 23개 (`_*.json`)
- **문서**: 10개 (`*.md`)
- **스크립트**: 5개 (`*.py`)

**문제**:
- 어떤 파일이 실제로 사용되는지 불분명
- 실험/테스트 파일이 프로덕션 코드와 섞여있음
- 문서가 분산되어 있음

---

## 🎯 정리 계획

### Phase 1: 실험/테스트 파일 정리

#### 1.1 테스트 파일 → `_experiments/`
```bash
# 22개 test_*.py 파일들
test_all_children.py
test_child_*.py (5개)
test_v*.py (14개)
test_prompts*.py (2개)
test_worldview_naming.py
```

**이동 위치**: `_experiments/prompt_tests/`

#### 1.2 결과 JSON → `_test_results/`
```bash
# 23개 _*.json 파일들
_child_*.json (4개)
_v*_results.json (14개)
_evolution_report_*.json
_hierarchical_worldviews_*.json
_claude_security_verification_*.json
등등
```

**이동 위치**: `_test_results/`

#### 1.3 실험 스크립트 → `_experiments/`
```bash
check_worldview_data.py
cleanup_duplicate_children.py
compare_old_vs_new.py
reanalyze_*.py (2개)
verify_hierarchy.py
```

**이동 위치**: `_experiments/one_off_scripts/`

---

### Phase 2: 문서 정리

#### 2.1 보관할 핵심 문서 (루트 유지)
```
README.md                    # 프로젝트 소개
CLAUDE.md                    # Claude Code 가이드
CLEANUP_COMPLETE.md          # v2.0 정리 기록
```

#### 2.2 이동할 문서 → `docs/`
```
SECURITY_AUDIT_REPORT.md         → docs/security/
SECURITY_CLEANUP_SUMMARY.md      → docs/security/
CLAUDE_VS_GPT_COMPARISON.md      → docs/analysis/
DATA_COMPLETENESS_REPORT.md      → docs/reports/
NEW_SYSTEM_ARCHITECTURE.md       → docs/archive/
SYSTEM_ARCHITECTURE.md           → docs/archive/
analyze_good_cases.md            → docs/analysis/
```

---

### Phase 3: 디렉토리 구조 최종

```
moniterdc/
├── README.md                    # 프로젝트 소개
├── CLAUDE.md                    # Claude Code 가이드
├── CLEANUP_COMPLETE.md          # v2.0 정리
├── setup.py                     # 설치 스크립트
├── requirements.txt
├── .env.example
├── .gitignore
│
├── engines/                     # 핵심 분석 엔진
│   ├── analyzers/
│   │   ├── layered_perception_extractor.py
│   │   ├── reasoning_structure_extractor.py
│   │   ├── worldview_evolution_engine.py
│   │   ├── mechanism_matcher.py
│   │   └── _deprecated/
│   └── utils/
│
├── scripts/                     # 프로덕션 스크립트만
│   ├── process_new_content.py
│   ├── run_worldview_evolution.py
│   ├── run_mechanism_matcher.py
│   └── claude_security_verification.py
│
├── dashboard/                   # Next.js 대시보드
│
├── supabase/                    # DB 마이그레이션
│
├── tests/                       # 실제 테스트만
│   ├── test_openai_api.py
│   └── test_new_schema.py
│
├── docs/                        # 📁 문서 (새로 정리)
│   ├── security/
│   │   ├── SECURITY_AUDIT_REPORT.md
│   │   └── SECURITY_CLEANUP_SUMMARY.md
│   ├── analysis/
│   │   ├── CLAUDE_VS_GPT_COMPARISON.md
│   │   └── analyze_good_cases.md
│   ├── reports/
│   │   └── DATA_COMPLETENESS_REPORT.md
│   └── archive/
│       ├── NEW_SYSTEM_ARCHITECTURE.md
│       └── SYSTEM_ARCHITECTURE.md
│
├── _experiments/                # 📁 실험 파일 (새로 생성)
│   ├── prompt_tests/
│   │   ├── test_v1-v14.py (14개)
│   │   ├── test_child_*.py (8개)
│   │   └── test_prompts*.py
│   └── one_off_scripts/
│       ├── check_worldview_data.py
│       ├── cleanup_duplicate_children.py
│       ├── compare_old_vs_new.py
│       ├── reanalyze_*.py
│       └── verify_hierarchy.py
│
├── _test_results/               # 📁 테스트 결과 (새로 생성)
│   ├── prompt_evolution/
│   │   ├── _v1-v14_results.json (14개)
│   │   └── _child_*.json (4개)
│   ├── worldview_tests/
│   │   ├── _evolution_report_*.json
│   │   └── _hierarchical_worldviews_*.json
│   └── security/
│       └── _claude_security_verification_*.json
│
├── _archive/                    # 이미 있음 (유지)
└── _deprecated/                 # 이미 있음 (유지)
```

---

## 🚀 실행 계획

### 단계별 작업

**Step 1**: 디렉토리 생성
```bash
mkdir -p docs/{security,analysis,reports,archive}
mkdir -p _experiments/{prompt_tests,one_off_scripts}
mkdir -p _test_results/{prompt_evolution,worldview_tests,security}
```

**Step 2**: 테스트 파일 이동
```bash
mv test_*.py _experiments/prompt_tests/
```

**Step 3**: 결과 JSON 이동
```bash
mv _*_results.json _test_results/prompt_evolution/
mv _child_*.json _test_results/prompt_evolution/
mv _evolution_report_*.json _test_results/worldview_tests/
mv _hierarchical_worldviews_*.json _test_results/worldview_tests/
mv _claude_security_verification_*.json _test_results/security/
```

**Step 4**: 실험 스크립트 이동
```bash
mv check_worldview_data.py _experiments/one_off_scripts/
mv cleanup_duplicate_children.py _experiments/one_off_scripts/
mv compare_old_vs_new.py _experiments/one_off_scripts/
mv comparison_old_vs_new.json _test_results/
mv reanalyze_*.py _experiments/one_off_scripts/
mv verify_hierarchy.py _experiments/one_off_scripts/
```

**Step 5**: 문서 정리
```bash
mv SECURITY_*.md docs/security/
mv CLAUDE_VS_GPT_COMPARISON.md docs/analysis/
mv analyze_good_cases.md docs/analysis/
mv DATA_COMPLETENESS_REPORT.md docs/reports/
mv *_ARCHITECTURE.md docs/archive/
```

**Step 6**: .gitignore 업데이트
```gitignore
# Experiments and test results (gitignored)
_experiments/
_test_results/
```

---

## ✅ 정리 후 루트 디렉토리

**Before**: 55개 파일
**After**: 7개 파일

```
moniterdc/
├── README.md
├── CLAUDE.md
├── CLEANUP_COMPLETE.md
├── setup.py
├── requirements.txt
├── .env.example
└── .gitignore
```

**폴더**:
- `engines/` - 핵심 엔진
- `scripts/` - 프로덕션 스크립트만
- `dashboard/` - UI
- `supabase/` - DB
- `tests/` - 실제 테스트만
- `docs/` - 모든 문서
- `_experiments/` - 실험 코드 (gitignored)
- `_test_results/` - 테스트 결과 (gitignored)
- `_archive/` - 과거 코드
- `_deprecated/` - 더 이상 안 쓰는 코드

---

## 🎯 기대 효과

1. **명확성**: 어떤 파일이 프로덕션인지 한눈에 파악
2. **깔끔함**: 루트에서 48개 파일 제거
3. **보안**: 실험 파일들 자동 gitignore
4. **문서화**: docs/ 폴더로 모든 문서 체계화
5. **유지보수**: 새 개발자도 쉽게 이해

---

**승인하시면 바로 실행하겠습니다!**
