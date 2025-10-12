# 전체 시스템 설계: 종합 정리

## 원래 목적 (처음부터 끝까지 모든 대화에서)

### 핵심 목적
**DC 갤러리 사용자들의 왜곡된 세계관을 이해하고 모니터링하는 시스템**

- "저들의 특정한 시각" 이해
- "유심교체를 어떻게 알아?"라는 질문 자체가 세계관을 드러낸다
- 글을 수집할 때마다 유기적으로 점검하고 확인
- 계속 모니터링하면서 확인할 수 있는 시스템

### 왜 만들었나?
1. 실시간으로 글이 올라옴
2. 각 글에서 "저들만의 시선"을 추출
3. 그 시선들이 모여서 "세계관" 형성
4. 새 글이 오면 어떤 세계관에 속하는지 자동 분류
5. Dashboard에서 실시간 모니터링

## 현재 상황 (있는 것 vs 없는 것)

### ✅ 있는 것
1. **데이터 수집**: 458개 Content
2. **Old Perception**: 88개 (Phase 1 방식)
3. **Layered Perception**: 3개 추출됨 (Phase 2 방식)
4. **Worldview 테이블**: 9개 (Topic 카테고리, perception_count=0)

### ❌ 없는 것
1. **458개 Content → Layered Perception 추출**: 3개만 됨
2. **Perception → Worldview Clustering**: 0개 연결
3. **새 글 올라오면 자동 분류**: 없음
4. **실시간 모니터링 Dashboard**: 작동 안 함

### 💡 핵심 문제
**Perception이 있어도 Worldview로 clustering 안 됨**
→ Worldview가 "Topic 카테고리"지 실제 "세계관 구조"가 아님

## 세계관이란 무엇인가? (모든 대화에서 강조된 것)

### 세계관 ≠ Topic
- ❌ "독재와 사찰의 부활" (주제)
- ✅ "좌파는 사찰과 협박으로 권력을 유지하려 한다" (믿음 구조)

### 세계관 = 사고 구조
```
현상 발견 (Explicit)
  ↓
합법적 설명 배제 (Implicit - 추론 규칙)
  ↓
숨겨진 악의적 세력 상정 (Implicit - 전제)
  ↓
체제적 위협으로 확대 (Deep - 세상 작동 원리)
```

### 세계관의 3가지 요소
1. **Who**: 누가 (민주당, 좌파, 중국, 카르텔)
2. **How**: 어떻게 (사찰, 협박, 은폐, 네트워크)
3. **Pattern**: 항상 이렇게 작동한다 (독재 재현, 치안 붕괴, 제도 포획)

## 지금까지 발견한 것

### 테스트 결과 (3개 Layered Perception)

**공통 구조:**
```
작은 단서 포착
  ↓ (추론 규칙)
합법·우연 배제 → 악의·의도 가정
  ↓ (연결 논리)
배후에 조직적 네트워크 상정
  ↓ (확대 논리)
체제 수준의 위협으로 비약
```

**핵심 믿음:**
"세상은 노출된 규칙이 아니라 은밀한 네트워크의 동기·역량·기회에 의해 운영된다"

**3개 세계관 후보:**
1. "국경 완화는 중국발 조직범죄의 잠입과 치안 붕괴를 초래한다"
2. "복지·보건 영역은 카르텔이 자원과 제도를 사적으로 배분한다"
3. "좌파/민주당은 사찰과 압박으로 권력 유지와 사법 장악을 시도한다"

**검증 기준 통과:**
- ✅ 특수성: 8/10
- ✅ 전제 포착: 8/10
- ✅ Reality gap: 9/10
- ✅ Belief 구조: 8/10
- ✅ 일관성: 80%

## 전체 시스템 아키텍처 (원래 설계)

### Phase 1: 수집 (완료)
```
DC Gallery → Crawler → Contents (458개)
```

### Phase 2: 3-Layer 추출 (3개만 완료)
```
Contents → LayeredPerceptionExtractor → Layered Perceptions
  - Explicit Claims
  - Implicit Assumptions
  - Reasoning Gaps
  - Deep Beliefs
```

### Phase 3: Worldview Clustering (미완성)
```
Layered Perceptions → Clustering → Worldviews
  - 공통 구조 추출
  - Who/How/Pattern 정의
  - Belief system 형성
```

### Phase 4: 실시간 분류 (없음)
```
새 Content → LayeredPerception 추출 → 기존 Worldview에 매칭
```

### Phase 5: 모니터링 (없음)
```
Dashboard → Worldview별 Content 표시 → 실시간 추적
```

## 지금 해야 할 일 (단계별, 검증 포함)

### 1단계: Layered Perception 추출 완료
**목표**: 458개 → 458개 Layered Perception

**작업:**
- `layered_perception_extractor.py` 사용 (이미 검증됨)
- 병렬 10개씩 처리
- 실패 시 재시도 로직

**검증:**
- 10개 추출 후 spot check
- 특수성/전제/gap 포착 확인
- 문제 있으면 멈추고 prompt 수정

### 2단계: Worldview 구조 정의
**목표**: 458개 perception → 5-10개 Worldview

**작업:**
```python
# All deep_beliefs 수집
all_beliefs = []
for p in perceptions:
    all_beliefs.extend(p['deep_beliefs'])

# GPT-5로 clustering
# 기준: Who/How/Why/Pattern 구조
# 최소 지지: 30개 이상 perception에서 발견
worldviews = cluster_into_worldviews(all_beliefs)
```

**검증:**
- Worldview가 Topic 카테고리인가?
- Who/How/Pattern 구조 있는가?
- 30개 이상 perception이 지지하는가?

### 3단계: Perception → Worldview 연결
**목표**: 각 perception을 가장 가까운 worldview에 연결

**작업:**
```python
for perception in perceptions:
    for worldview in worldviews:
        similarity = calculate_similarity(
            perception['deep_beliefs'],
            worldview['core_belief']
        )
        if similarity > 0.7:
            link(perception.id, worldview.id)
```

**검증:**
- Coverage: 몇 %가 연결되었나? (목표 80% 이상)
- Precision: 연결이 맞는가? (샘플 10개 수동 확인)

### 4단계: 실시간 파이프라인 구축
**목표**: 새 글 → 자동 분류

**작업:**
```python
def process_new_content(content):
    # 1. Layered perception 추출
    perception = extractor.extract(content)

    # 2. 가장 가까운 worldview 찾기
    matched_worldview = find_best_match(perception, worldviews)

    # 3. 연결
    if matched_worldview:
        link(perception.id, matched_worldview.id)
    else:
        # 새로운 worldview 후보?
        flag_for_review(perception)

    return matched_worldview
```

**검증:**
- 10개 새 글로 테스트
- 매칭률 80% 이상
- 잘못 매칭된 경우 분석

### 5단계: Dashboard 연동
**목표**: 실시간 모니터링

**작업:**
- Worldview별 최신 content 표시
- 시간별 추이 그래프
- 새 글 알림

### 6단계: 유기적 점검 시스템
**목표**: 계속 모니터링하면서 개선

**작업:**
```python
# 매일 실행
def daily_check():
    # 1. 새 perception 추출 (오늘 글들)
    new_perceptions = extract_today()

    # 2. Worldview 매칭
    for p in new_perceptions:
        matched = find_match(p)
        if not matched:
            # 새 worldview 후보 발견?
            review_queue.add(p)

    # 3. Worldview 업데이트 필요성 체크
    if len(review_queue) > 50:
        # 50개 이상 매칭 안 되면 새 worldview 추가 필요
        trigger_reanalysis()

    # 4. 기존 worldview 변화 추적
    for wv in worldviews:
        trend = analyze_trend(wv, last_7_days)
        if trend == 'emerging':
            alert('새 담론 증가:', wv.core_belief)
```

## 성공 기준 (5개 검증 기준)

### 기준 1: 특수성
이 진영만의 특수한 시각인가?
- 목표: 평균 6/10 이상
- 측정: 10개 샘플 수동 평가

### 기준 2: 전제 포착
질문/진술이 전제하는 믿음을 포착하는가?
- 목표: 평균 6/10 이상
- 측정: Implicit assumptions 품질 평가

### 기준 3: Reality Gap
실제 세상과의 차이(왜곡/과장)를 포착하는가?
- 목표: 평균 6/10 이상
- 측정: Reasoning gaps 품질 평가

### 기준 4: Belief 구조
Topic이 아닌 Who/How/Pattern 구조인가?
- 목표: 7/10 이상
- 측정: Worldview 정의 평가

### 기준 5: 일관성
새 글에서도 일관되게 나타나는가?
- 목표: 매칭률 80% 이상
- 측정: 실시간 매칭 통계

## 위험 요소 및 대응

### 위험 1: Perception 추출 실패
**증상**: 일반론 추출, 특수성 부족
**대응**: 10개마다 검증, prompt 즉시 수정

### 위험 2: Worldview가 Topic 카테고리로 변질
**증상**: "독재와 사찰" 같은 주제 분류
**대응**: Who/How/Pattern 구조 강제, Bad example 제시

### 위험 3: Coverage 낮음
**증상**: 50% 이하만 worldview에 매칭
**대응**: Worldview 정의 너무 좁음, 재분석 필요

### 위험 4: 시간 경과 후 worldview 변화
**증상**: 새 담론 등장, 기존 worldview로 설명 안 됨
**대응**: 유기적 점검 시스템으로 감지, 재clustering

## 다음 실행 계획 (구체적 단계)

### 지금 즉시
1. ✅ 3개 perception 검증 완료 (5개 기준 통과)
2. ✅ 공통 구조 발견 완료
3. ⏳ 이제 할 일 정리 (이 문서)

### 오늘 안에
1. **10개 perception 추출 및 검증**
   - 실패 시 prompt 수정
   - 성공 시 다음 단계

2. **100개 perception 추출 시작**
   - 병렬 10개씩
   - 10개마다 spot check
   - 문제 발견 시 즉시 멈춤

### 내일
1. **Worldview clustering**
   - 100개 deep_beliefs로
   - 5-10개 worldview 생성
   - Who/How/Pattern 구조 검증

2. **Perception → Worldview 연결**
   - Coverage 80% 목표
   - 수동 검증 10개

### 모레
1. **나머지 358개 perception 추출**
2. **Worldview 재조정** (필요시)
3. **실시간 파이프라인 구축**

### 1주일 내
1. **Dashboard 연동**
2. **유기적 점검 시스템 구축**
3. **매일 자동 실행 설정**

## 체크리스트 (절대 틀리지 않기 위해)

### 매 단계마다 확인
- [ ] 원래 목적을 달성하는가? (저들의 특정한 시각 이해)
- [ ] 5개 검증 기준을 통과하는가?
- [ ] 게시글별 분석이 아닌 구조 분석인가?
- [ ] Topic이 아닌 Belief system인가?
- [ ] 실시간 모니터링 가능한가?
- [ ] 유기적으로 점검 가능한가?

### 진행 전 질문
- 이게 왜 필요한가?
- 전체 시스템에서 어떤 역할인가?
- 검증은 어떻게 하는가?
- 실패하면 어떻게 대응하는가?

### 완료 후 확인
- 다음 단계로 넘어갈 수 있는가?
- 문제점은 없는가?
- 개선 필요한 부분은?

## 최종 목표

**DC 갤러리의 왜곡된 세계관을 실시간으로 모니터링하고, 새 글이 올라올 때마다 자동으로 분류하여 그들의 담론이 어떻게 변화하는지 추적하는 시스템**

- 458개 Content → 458개 Layered Perception
- 458개 Perception → 5-10개 Worldview
- 새 글 → 자동 분류
- Dashboard → 실시간 모니터링
- 매일 → 유기적 점검 및 업데이트
