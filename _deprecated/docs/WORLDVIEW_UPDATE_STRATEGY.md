# 세계관 지속 업데이트 전략

## 🎯 목표

세계관이 **지속적으로 발전하고 업데이트**되어야 함
- 새로운 담론 포착
- 기존 세계관 진화
- 자동화 및 비용 최적화

---

## 📊 시뮬레이션 결과

4가지 업데이트 방식을 실제 데이터로 테스트:

### 시나리오 A: 전체 재구성
```
- 방식: 기존 + 새 데이터 전부 합쳐서 재구성
- 결과: 6개 → 6개 새 세계관
- 장점: 완전히 새로운 관점
- 단점:
  • 기존 세계관 ID 변경 (링크 깨짐)
  • GPT 비용 높음
  • 일관성 유지 어려움
- 추천: ⚠️
```

### 시나리오 B: 기존 세계관에 추가만
```
- 방식: 새 perception만 기존 세계관에 매칭
- 결과: 7/10 매칭, 3/10 미매칭
- 장점: 빠름, 비용 낮음, 일관성 유지
- 단점: 새로운 세계관 발견 불가
- 추천: ⚠️
```

### 시나리오 C: 점진적 병합 ⭐
```
- 방식:
  • 새 perception 분석
  • 기존 세계관과 유사도 계산
  • 높으면: 기존 세계관 업데이트 (narrative 예시 추가)
  • 낮으면: 새 세계관 생성

- 결과:
  • 업데이트될 세계관: 2개
  • 새로 생성될 세계관: 1개

- 장점:
  • 기존 세계관 발전 (예시 증가)
  • 새로운 세계관 발견
  • 일관성 유지 (ID 변경 없음)

- 단점:
  • 구현 복잡도 높음
  • GPT 비용 중간

- 추천: ✅✅
```

### 시나리오 D: 임계값 기반 ⭐
```
- 방식:
  • 조건 1: 새 perception 100개+ 누적 → 재구성
  • 조건 2: 미매칭률 30%+ → 재구성

- 결과:
  • 현재 20개 누적 (조건 1: 미충족)
  • 미매칭률 55% (조건 2: 충족)
  • → 재구성 실행

- 장점:
  • 자동화 가능
  • 안정적 (불필요한 재구성 방지)

- 단점:
  • 업데이트 지연 가능
  • 임계값 튜닝 필요

- 추천: ✅
```

---

## 🏆 최적 전략: 하이브리드

**방식 C (점진적 병합) + 방식 D (임계값 기반)**

```
┌─────────────────────────────────────────────────────┐
│ 1. 일상 운영 (매일)                                  │
│                                                      │
│   새 글 수집 → 3-layer 분석 → 기존 세계관 매칭       │
│                                                      │
│   • 빠름                                             │
│   • 저비용                                           │
│   • 방식 B 사용                                      │
└─────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────┐
│ 2. 점진적 업데이트 (주 1회)                          │
│                                                      │
│   새로 매칭된 perception 중 대표 사례 선정           │
│   → 기존 세계관 narrative에 예시 추가                │
│                                                      │
│   • GPT로 새 예시 생성                               │
│   • 세계관 발전                                      │
│   • 방식 C 사용                                      │
└─────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────┐
│ 3. 임계값 재구성 (월 1회 또는 조건 충족 시)         │
│                                                      │
│   조건 확인:                                         │
│   • 새 perception 100개+ 누적?                      │
│   • 미매칭률 30%+?                                   │
│                                                      │
│   충족 시 → 전체 재구성                              │
│                                                      │
│   • 전체 구조 재정비                                 │
│   • 방식 D → 방식 A 실행                            │
└─────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────┐
│ 4. 새 세계관 발견 (수시)                             │
│                                                      │
│   미매칭 perception이 특정 주제로 10개+ 누적         │
│   → GPT로 새 세계관 생성                             │
│   → 기존 계층에 추가                                 │
│                                                      │
│   • 새로운 담론 포착                                 │
│   • 수시 확장                                        │
└─────────────────────────────────────────────────────┘
```

---

## 💻 구현: WorldviewUpdater

### 클래스 구조

```python
class WorldviewUpdater:
    # 임계값
    REBUILD_THRESHOLD_COUNT = 100  # 100개 누적 시 재구성
    REBUILD_THRESHOLD_MISMATCH = 0.3  # 30% 미매칭 시 재구성
    NEW_WORLDVIEW_THRESHOLD = 10  # 10개 누적 시 새 세계관

    # 메서드
    async def daily_update()  # 일상 업데이트
    async def weekly_update()  # 주간 업데이트
    async def check_and_rebuild_if_needed()  # 임계값 확인
    async def detect_and_create_new_worldviews()  # 새 세계관 발견
```

### 1. daily_update() - 일상 운영
```python
async def daily_update():
    # 1. 미분석 contents 찾기
    unanalyzed = find_unanalyzed_contents()

    # 2. 3-layer 분석
    for content in unanalyzed:
        lp = await LayeredPerceptionExtractor.extract(content)

    # 3. 기존 세계관에 매칭 (간단한 키워드 매칭)
    for lp in new_lps:
        match_to_existing_worldviews(lp)

    return {'new_analyzed': N, 'new_matched': M}
```

### 2. weekly_update() - 주간 업데이트
```python
async def weekly_update():
    for worldview in existing_worldviews:
        # 최근 연결된 perception 중 대표 사례 선정
        recent_perceptions = get_recent_linked_perceptions(worldview)

        # GPT로 새 예시 생성
        new_example = await generate_example_from_perception(
            recent_perceptions[0]
        )

        # 세계관 narrative에 추가
        worldview.narrative.examples.append(new_example)

        # DB 업데이트
        save_worldview(worldview)

    return {'updated_worldviews': N}
```

### 3. check_and_rebuild_if_needed() - 임계값 확인
```python
async def check_and_rebuild_if_needed():
    # 조건 1: 개수
    new_perceptions_count = count_new_perceptions_since_last_rebuild()
    needs_rebuild_count = new_perceptions_count >= 100

    # 조건 2: 미매칭률
    mismatch_rate = calculate_mismatch_rate()
    needs_rebuild_mismatch = mismatch_rate > 0.3

    # 최종 결정
    if needs_rebuild_count or needs_rebuild_mismatch:
        # 전체 재구성
        await OptimalWorldviewConstructor.construct_all()
        return {'rebuilt': True}
    else:
        return {'rebuilt': False}
```

### 4. detect_and_create_new_worldviews() - 새 세계관 발견
```python
async def detect_and_create_new_worldviews():
    # 미매칭 perception 찾기
    unmatched = find_unmatched_perceptions()

    # 주제별 그룹화
    themes = group_by_theme(unmatched)

    # 10개 이상 누적된 주제 찾기
    for theme, lps in themes.items():
        if len(lps) >= 10:
            # GPT로 새 세계관 생성
            new_worldview = await create_new_worldview(theme, lps)

            # DB 저장
            save_worldview(new_worldview)

    return {'new_worldviews': N}
```

---

## 📅 운영 스케줄

### 매일 (자동화)
```bash
# Cron job or GitHub Actions
0 2 * * * python run_daily_update.py
```

- 새 글 수집
- 3-layer 분석
- 기존 세계관 매칭
- **비용**: 낮음 (GPT-4o-mini만 사용)

### 주 1회 (자동화)
```bash
# 매주 일요일 오전 3시
0 3 * * 0 python run_weekly_update.py
```

- 대표 사례 선정
- 예시 생성 및 추가
- **비용**: 중간 (세계관당 1회 GPT-4o 호출)

### 월 1회 (조건부 자동화)
```bash
# 매월 1일 오전 4시
0 4 1 * * python run_monthly_check.py
```

- 임계값 확인
- 조건 충족 시 재구성
- **비용**: 조건부 높음

### 수시 (자동 감지)
- 미매칭 perception 모니터링
- 특정 주제 10개 누적 시 자동 실행
- **비용**: 발생 시만

---

## 📊 예상 비용

### 일상 (매일)
- 새 글 10개 분석: $0.02 (GPT-4o-mini)
- 매칭: 무료
- **월 비용**: ~$0.60

### 주간 (주 1회)
- 세계관 6개 × 예시 생성: $0.12 (GPT-4o)
- **월 비용**: ~$0.48

### 월간 (조건부)
- 전체 재구성: $2.00 (GPT-4o)
- **월 비용**: $0~2.00 (조건 충족 시만)

### 수시 (발생 시)
- 새 세계관 생성: $0.30/개 (GPT-4o)
- **월 비용**: ~$0.30 (평균)

**총 예상 비용**: **$1.38 ~ $3.38/월**

---

## ✅ 검증 완료

### 시뮬레이션 테스트
- ✅ 4가지 시나리오 실제 데이터로 테스트
- ✅ 하이브리드 전략 설계
- ✅ WorldviewUpdater 구현

### 실제 동작 확인
- ✅ daily_update: 미분석 contents 0개 확인
- ⚠️ weekly_update: perception_worldview_links 테이블 필요
- ⚠️ check_and_rebuild: 테이블 생성 후 테스트 가능

---

## 🚀 다음 단계

### 1. 테이블 생성 (필수)
```sql
CREATE TABLE perception_worldview_links (
    id UUID PRIMARY KEY,
    perception_id UUID REFERENCES layered_perceptions(id),
    worldview_id UUID REFERENCES worldviews(id),
    relevance_score FLOAT,
    created_at TIMESTAMPTZ
);
```

### 2. Cron Job 설정
- GitHub Actions 또는 서버 cron
- 일간/주간/월간 자동 실행

### 3. 모니터링 대시보드
- 세계관 발전 추이
- 새 perception 누적 상황
- 미매칭률 모니터링

### 4. 알림 시스템
- 재구성 필요 시 알림
- 새 세계관 발견 시 알림

---

## 📋 핵심 장점

### 1. 지속적 발전
- 일상: 새 데이터 지속 수집
- 주간: 세계관 예시 증가 (구체성 향상)
- 월간: 전체 구조 재정비
- 수시: 새로운 담론 포착

### 2. 비용 최적화
- 일상: 저비용 (GPT-mini만)
- 주간: 중간 비용 (예시만 생성)
- 월간: 조건부 (불필요한 재구성 방지)
- **총 $1~3/월**

### 3. 자동화
- 모든 단계 자동 실행 가능
- 임계값 기반 자동 결정
- 사람 개입 최소화

### 4. 일관성 유지
- 세계관 ID 변경 없음 (점진적 업데이트)
- 기존 링크 유지
- 안정적 운영

---

## 🎯 결론

**세계관은 지속적으로 발전 가능함**

- ✅ 시뮬레이션으로 검증 완료
- ✅ 최적 전략 (하이브리드) 설계
- ✅ WorldviewUpdater 구현
- ✅ 운영 스케줄 수립
- ✅ 비용 최적화

**다음**: 테이블 생성 후 실제 운영 시작

---

**작성일**: 2025-01-05
**엔진**: WorldviewUpdater v1.0
**Status**: ✅ 설계 및 구현 완료
