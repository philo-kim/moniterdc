# Refactoring Summary (2025-10-24)

## 🎯 목표
v2.0 시스템에 맞춰 프로젝트 구조를 정리하고 자동화 시스템을 최적화

## ✅ 완료된 작업

### 1. DC Crawler 메타데이터 수집 추가
**문제**: 크롤러가 `published_at` 등 메타데이터를 수집하지 않음
**해결**:
- `dc_gallery_adapter.py` 수정
  - JSON-LD에서 `published_at`, `view_count`, `comment_count` 파싱
  - HTML에서 `author`, `recommend_count` 파싱
- `content_collector.py` 수정
  - 메타데이터를 DB에 저장하도록 수정

**파일**:
- [engines/adapters/dc_gallery_adapter.py](engines/adapters/dc_gallery_adapter.py)
- [engines/collectors/content_collector.py](engines/collectors/content_collector.py)

### 2. 자동 수집 로직 개선
**문제**: 기간 필터링 없이 무한 증가, 중복 수집
**해결**:
- `auto_collect_recent.py` 생성
  - DB 최대 글 번호(max_no) 기준으로 새 글만 수집
  - 메타데이터 포함 저장
  - 중복 자동 스킵

**파일**:
- [scripts/auto_collect_recent.py](scripts/auto_collect_recent.py)

### 3. Daily Maintenance v2.0 호환
**문제**: 기존 `daily_maintenance.py`가 v1.0 시스템 사용 (PatternManager, worldview_patterns)
**해결**:
- `daily_maintenance_v2.py` 생성
  - `published_at` 기준으로 90일 이상 된 contents/perceptions 삭제
  - v2.0 테이블만 사용
  - 통계 출력

**파일**:
- [scripts/daily_maintenance_v2.py](scripts/daily_maintenance_v2.py)

### 4. GitHub Actions 워크플로우 수정
**문제**: `collect_500_posts.py` 사용 (기간 필터링 없음)
**해결**:
- `worldview_monitoring.yml` 수정
  - `auto_collect_recent.py` 사용으로 변경

**파일**:
- [.github/workflows/worldview_monitoring.yml](.github/workflows/worldview_monitoring.yml)

### 5. 1개월 기간 범위 밖 데이터 삭제
**작업**: DB에서 3,650개 불필요한 글 삭제
**결과**: 2,312개 글만 유지 (no=2,535,000~2,611,060)

### 6. 메타데이터 일괄 업데이트
**작업**: 2,312개 글의 메타데이터 업데이트
**스크립트**: `update_missing_metadata.py` (일회성)

## 📁 프로젝트 구조 (리팩토링 후)

### Active Scripts (6개)
```
scripts/
├── auto_collect_recent.py         # 10분마다 자동 수집 (max_no 기준)
├── collect_dc_posts.py            # 수동 수집 도구 (범용)
├── daily_maintenance_v2.py        # 매일 아카이빙 (v2.0)
├── process_new_contents.py        # 분석 파이프라인
├── run_mechanism_matcher.py       # Mechanism matching
└── run_worldview_evolution.py     # Worldview evolution
```

### Deprecated/Archived
```
_old_scripts/                      # 25개 deprecated scripts
_tests/                            # 테스트 스크립트들
_archive/                          # Legacy scripts
_deprecated/                       # Deprecated engines
_experiments/                      # 실험용 one-off scripts
```

### Active Engines
```
engines/
├── adapters/                      # DC crawler adapter
│   ├── base_adapter.py
│   └── dc_gallery_adapter.py     # ✅ 메타데이터 수집 추가
├── analyzers/                     # 5개 핵심 분석기
│   ├── layered_perception_extractor_v2.py
│   ├── reasoning_structure_extractor.py
│   ├── worldview_evolution_engine.py
│   ├── mechanism_matcher.py
│   └── pattern_manager.py
├── archiving/                     # 아카이빙
│   └── content_archiver.py
├── collectors/                    # 수집기
│   └── content_collector.py      # ✅ 메타데이터 저장 추가
└── utils/                         # 유틸리티
    ├── supabase_client.py
    └── embedding_utils.py
```

## 🔄 자동화 시스템 (최종)

### 10분마다 (GitHub Actions)
```
1. auto_collect_recent.py
   ├─ DB 최대 no 확인
   ├─ DC에서 100개 가져오기
   ├─ no > max_no만 필터링
   └─ 메타데이터 포함 저장

2. process_new_contents.py
   ├─ v2.1 perception 추출
   ├─ Reasoning structure 추출
   └─ Mechanism matching

3. Vercel 배포 트리거
```

### 매일 (Cron Job)
```
daily_maintenance_v2.py
├─ published_at < 90일 전 → 삭제
└─ 통계 출력
```

### 매월 (수동)
```
run_worldview_evolution.py
└─ Worldview 진화 분석
```

## 🗑️ 제거 예정

### Scripts
- `daily_maintenance.py` → v1.0 시스템 사용, `_old_scripts/`로 이동
- `update_missing_metadata.py` → 일회성 완료, `_old_scripts/`로 이동

## 📊 데이터 현황

### DB 통계
- Contents: 2,312개 (1개월, 9/24~10/24)
- Perceptions: 0개 (분석 전)
- Worldviews: 70개
- 예상 용량: ~6 MB

### 메타데이터 커버리지
- ✅ `published_at`: 100%
- ✅ `author`: 100%
- ✅ `view_count`: 100%
- ✅ `comment_count`: 100%
- ✅ `recommend_count`: 100%

## 🎓 주요 교훈

### 1. 메타데이터의 중요성
- **문제**: 작성일시 없이는 3개월 lifecycle 불가능
- **해결**: 크롤링 시점에 모든 메타데이터 수집

### 2. 기간 필터링 전략
- **문제**: limit 기반 수집은 무한 증가
- **해결**: max_no 기준 + published_at 기반 삭제

### 3. v2.0 시스템 단순화
- **제거**: PatternManager, worldview_patterns, decay 로직
- **유지**: 핵심 3-layer + 5 mechanisms + actor + logic_chain

### 4. 일회성 vs 반복 작업 분리
- **일회성**: `update_missing_metadata.py` → `_old_scripts/`
- **반복**: `auto_collect_recent.py`, `daily_maintenance_v2.py`

## 📝 다음 단계

1. ✅ 메타데이터 업데이트 완료 확인
2. ✅ `daily_maintenance.py`, `update_missing_metadata.py` → `_old_scripts/` 이동
3. ⏳ ARCHITECTURE.md 업데이트
4. ⏳ README.md 업데이트
5. ⏳ `auto_collect_recent.py` 테스트
6. ⏳ v2.1 perception 분석 시작

## 🔗 관련 파일

- [ARCHITECTURE.md](ARCHITECTURE.md) - 시스템 구조
- [README.md](README.md) - 프로젝트 개요
- [CLAUDE.md](CLAUDE.md) - Claude Code 가이드
- [CLEANUP_COMPLETE.md](CLEANUP_COMPLETE.md) - v2.0 Cleanup 요약
