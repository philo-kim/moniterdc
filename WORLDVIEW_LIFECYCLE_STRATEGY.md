# 세계관 & 패턴 3개월 라이프사이클 전략

## 문제 정의

현재:
- ✅ Contents: 3개월 아카이빙
- ✅ Perceptions: Contents와 동기화
- ❌ Patterns: 무한 누적 (문제!)
- ❌ Worldviews: 계속 유지 (재생성 필요)

**핵심 문제**: 오래된 contents의 패턴이 계속 남아서 노이즈

---

## 올바른 전략

### 1. Patterns: 3개월 윈도우

**원칙**: Active contents의 perceptions만 패턴 생성

```
매일:
  - 새 contents 수집
  - Perceptions 추출
  - Active perceptions만 패턴 업데이트 ← 중요!

매일 아카이브:
  - 90일 이상 contents → archived
  - 해당 perceptions → archived
  - Archived perceptions의 패턴 → 삭제! ← 새로 필요
```

### 2. Worldviews: 매월 재생성

**원칙**: Active perceptions (3개월)만 사용해서 매월 재발견

```
매월 1일:
  - Active perceptions (최근 90일, ~200개)로 Evolution 실행
  - 새로운 세계관 발견
  - 사라진 세계관 아카이브
  - 진화한 세계관 업데이트
```

---

## 구현 방안

### Option A: Pattern 소속 기반 삭제 (추천)

**개념**: Archived perception에서 나온 패턴만 삭제

```python
def cleanup_archived_patterns(worldview_id):
    """
    Archived perceptions의 패턴만 삭제

    로직:
    1. Archived perceptions 조회
    2. 해당 perceptions의 claims/assumptions/beliefs 추출
    3. 매칭되는 패턴 삭제
    """
```

**장점**:
- ✅ 정확함 (archived perception의 패턴만 삭제)
- ✅ Active perception의 같은 패턴은 유지

**단점**:
- ⚠️ 복잡함 (패턴 매칭 필요)
- ⚠️ 느림

### Option B: Pattern 전체 재생성 (더 간단, 추천!)

**개념**: 매월 Evolution 시 패턴도 전부 재생성

```python
def regenerate_all_patterns(worldview_id):
    """
    매월 Evolution 시:
    1. 기존 패턴 전부 삭제
    2. Active perceptions만으로 패턴 재생성
    3. 자연스럽게 3개월 윈도우 유지
    """
```

**장점**:
- ✅ 매우 간단
- ✅ 빠름
- ✅ 확실함 (3개월 데이터만)
- ✅ Evolution과 동기화

**단점**:
- ⚠️ 패턴 strength 히스토리 손실 (재생성이므로)
  → 하지만 3개월 윈도우라 상관없음

---

## 추천 전략: Option B (매월 패턴 재생성)

### 이유

1. **담론 변화 속도**: 3개월이면 담론 완전히 바뀜
2. **패턴 의미**: 오래된 패턴 strength는 의미 없음
3. **단순성**: 복잡한 매칭 로직 불필요
4. **정확성**: 항상 최근 3개월 데이터만

### 구현

```python
# monthly_worldview_evolution.py

# 1. Evolution 실행 (Active perceptions만)
evolution_engine.run(sample_size=200)

# 2. 모든 worldview의 패턴 재생성
for worldview in new_worldviews:
    # 기존 패턴 삭제
    delete_all_patterns(worldview.id)

    # Active perceptions로 패턴 재생성
    active_perceptions = get_active_perceptions(worldview.id)
    for perception in active_perceptions:
        pattern_manager.integrate_perception(worldview.id, perception)
```

---

## 데이터 라이프사이클 (완전판)

### 일일 사이클

```
[Contents 수집]
    ↓
[Perceptions 추출] (v2.1 필터링)
    ↓
[Patterns 업데이트] ← Active perceptions만
    ↓
[아카이브] (90일 이상)
    Contents → archived
    Perceptions → archived
    Patterns → 그대로 (매월 정리)
```

### 월간 사이클

```
[Worldview Evolution]
    Active perceptions (3개월) → 세계관 재발견
    ↓
[패턴 재생성]
    기존 패턴 전부 삭제
    Active perceptions → 패턴 재생성
    ↓
[Mechanism Matcher]
    Perceptions ↔ Worldviews 재연결
```

---

## 구체적 동작

### 예시: 2025년 10월

**Active Data (7월~10월)**:
- Contents: 1,800개
- Perceptions: 1,800개
- Patterns: ~500개 (3개월 데이터 기반)
- Worldviews: 7개 (매월 재발견)

**10월 1일 Evolution**:
1. Active perceptions (7월~9월, 200개) 샘플링
2. 세계관 재발견 → 새 worldviews
3. 기존 패턴 전부 삭제
4. Active perceptions로 패턴 재생성
5. Mechanism Matcher 실행

**결과**:
- ✅ 세계관: 최신 3개월 담론 반영
- ✅ 패턴: 최신 3개월 데이터만
- ✅ 오래된 담론 노이즈 제거

---

## 비교: Option A vs Option B

| 항목 | Option A (소속 기반) | Option B (전체 재생성) |
|------|---------------------|----------------------|
| **복잡도** | 높음 (매칭 로직) | 낮음 (삭제/재생성) |
| **정확도** | 매우 높음 | 높음 (충분) |
| **속도** | 느림 (매칭) | 빠름 |
| **유지보수** | 어려움 | 쉬움 |
| **데이터 정확성** | 100% | 100% (재생성이므로) |
| **추천도** | △ | ✅ |

---

## 실행 계획

### 1. 매월 스크립트 수정

```python
# scripts/monthly_worldview_evolution.py

# Before
evolution_engine.run()

# After
evolution_engine.run()

# 패턴 재생성 추가
regenerate_all_patterns_for_all_worldviews()
```

### 2. 패턴 재생성 함수

```python
def regenerate_all_patterns_for_all_worldviews():
    """
    모든 worldview의 패턴을 Active perceptions로 재생성
    """
    for worldview in worldviews:
        # 1. 기존 패턴 삭제
        # 2. Active perceptions 조회
        # 3. 패턴 재생성
```

---

## 예상 효과

### Before (패턴 무한 누적)

```
6개월 후:
- Patterns: ~2,000개 (6개월 누적)
- 노이즈: 오래된 담론 패턴 포함
- 품질: 낮음
```

### After (3개월 윈도우)

```
항상:
- Patterns: ~500개 (3개월만)
- 노이즈: 없음
- 품질: 높음 (최신 담론만)
```

---

## 결론

**Option B (매월 패턴 전체 재생성)** 을 추천합니다.

이유:
- ✅ 단순하고 확실함
- ✅ 3개월 윈도우 완벽히 유지
- ✅ Evolution과 동기화
- ✅ 오래된 담론 노이즈 완전 제거

**구현**: 매월 Evolution 시 패턴도 함께 재생성
