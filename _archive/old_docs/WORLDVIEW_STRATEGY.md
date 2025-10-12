# 세계관 구축 전략 (모든 요구사항 종합)

## 핵심 요구사항 정리

### 1. 세계관이란 무엇인가?
- ❌ 게시글별 분석 결과
- ❌ Topic 카테고리
- ✅ **100개 글을 관통하는 일관된 논리 구조**
- ✅ **"세상이 이렇게 작동한다"는 믿음 체계**

### 2. "특정한" 세계관이란?
- ❌ 일반론: "권력은 부패한다"
- ✅ 특수론: "좌파는 사찰로 반대파를 제거한다"
- → **이 진영만의 특수한 시각**

### 3. 왜곡된 세계관
- ❌ "그들은 이렇게 생각한다" (중립적 서술)
- ✅ **"왜곡된" 무언가를 발견**
- → 그들의 논리가 현실과 어떻게 괴리되는가

### 4. 표현이 아닌 구조
- ❌ "유심교체를 어떻게 알아ㅋㅋ미친" (표현 보존)
- ✅ **"어떻게 알아?"라는 질문 자체가 전제를 드러냄**
- → 전제된 사고 구조 포착

### 5. 데이터 기반 검증
- ❌ 추상적 설계만 하고 작동 확인 안 함
- ✅ **실제 데이터로 시뮬레이션하며 개선**
- → 10개, 100개로 점진적 검증

### 6. 실시간 모니터링
- ❌ 한 번 분석하고 끝
- ✅ **글 수집할 때마다 유기적으로 점검**
- → 계속 모니터링하면서 확인

---

## 전략: 3단계 구조

### Phase A: 논리 구조 추출 (개별 글 → 구조)
**목표**: 각 글에서 "그들만의 논리 구조" 추출

**방법**: Layered Perception (이미 구현됨)
```
Explicit (표면): 직접 말한 것
  ↓
Implicit (암묵): 당연하게 여기는 전제
  ↓
Reasoning (연결): 어떻게 추론하는가
  ↓
Deep (심층): 세상 작동 원리에 대한 믿음
```

**핵심**:
- "유심교체를 어떻게 알아?" → Explicit
- "통신사만 알 수 있다" → Implicit (전제)
- "민주당이 알았다 → 협박했다" → Reasoning (추론)
- "사찰로 반대파 제거" → Deep (믿음)

**이게 그들의 완벽한 논리**

---

### Phase B: 왜곡 패턴 발견 (구조 → 왜곡)
**목표**: 그들의 논리가 현실과 어디서 괴리되는가

**방법**: Reasoning Gaps 분석

**예시**:
```
현실 A: "민주당이 유심교체 정보를 알았다"
  ↓ (그들의 추론)
전제 B: "통신사만 알 수 있다" ← 왜곡 1: 다른 경로 배제
  ↓
결론 C: "통신사를 협박했다" ← 왜곡 2: 근거 없는 단정
  ↓
확대 D: "사찰로 권력 유지" ← 왜곡 3: 극단으로 비약
```

**왜곡의 유형**:
1. **대안 배제**: 합법적 가능성 무시
2. **의도 단정**: 악의적 의도로만 해석
3. **극단 비약**: 작은 징후 → 체제 위협

**이 왜곡 패턴이 반복되는가?**

---

### Phase C: 세계관 정의 (왜곡 → 세계관)
**목표**: 100개 글에서 일관된 왜곡 패턴 = 세계관

**구조**:
```
세계관 = 논리 구조 + 왜곡 패턴

예시:
- 논리: X 관찰 → Y 전제 → Z 추론 → W 믿음
- 왜곡: 항상 "대안 배제" → "악의 단정" → "위협 확대"
→ 세계관: "세상은 숨겨진 악의적 세력이 지배한다"
```

**세계관의 구성 요소**:
```json
{
  "name": "권력 음모론적 세계관",

  "logic_structure": {
    "관찰": "작은 현상 포착 (유심교체 정보)",
    "전제": "특정 조건 단정 (통신사만 알 수 있다)",
    "추론": "배후 세력 상정 (협박했다)",
    "믿음": "체제 위협 확대 (독재 재현)"
  },

  "distortion_pattern": {
    "type_1": "대안 배제 (합법적 경로 무시)",
    "type_2": "악의 단정 (항상 나쁜 의도)",
    "type_3": "위협 확대 (항상 체제 위협)"
  },

  "core_belief": "세상은 표면적 설명이 아니라 숨겨진 악의적 세력의 음모로 작동한다",

  "actors": {
    "villain": ["민주당", "좌파", "중국", "카르텔"],
    "mechanism": ["사찰", "협박", "은폐", "네트워크"],
    "victim": ["국민", "반대파", "보수"]
  },

  "evidence": {
    "supporting_perceptions": 150,  // 458개 중 몇 개가 이 패턴
    "coverage": "33%",
    "consistency": "95%"  // 패턴 일치도
  }
}
```

---

## 구체적 실행 계획

### Step 1: 논리 구조 추출 (458개)
**작업**: Layered Perception Extractor 실행

```python
# 이미 검증된 extractor 사용
extractor = LayeredPerceptionExtractor()

# 458개 content 처리
for content in contents:
    perception = await extractor.extract(content)
    # 결과:
    # - explicit_claims
    # - implicit_assumptions  ← 그들의 전제
    # - reasoning_gaps        ← 그들의 추론 (+ 왜곡)
    # - deep_beliefs          ← 그들의 믿음
```

**검증** (10개마다):
- [ ] Implicit이 실제 "전제"를 포착하는가?
- [ ] Reasoning gaps가 "추론 과정"을 보여주는가?
- [ ] Deep beliefs가 "일반론"이 아닌 "특수론"인가?

**Stop 조건**:
- 특수성 < 6/10
- 전제 포착 < 6/10
→ Prompt 수정 후 재시작

---

### Step 2: 왜곡 패턴 분석 (100개 샘플)
**작업**: Reasoning Gaps에서 왜곡 유형 추출

```python
# 100개 perception에서 모든 reasoning gaps 수집
all_gaps = []
for p in perceptions[:100]:
    all_gaps.extend(p['reasoning_gaps'])

# 왜곡 유형 clustering
distortion_types = analyze_distortion_patterns(all_gaps)
# 결과:
# - "대안 배제": 70/100 (70%)
# - "악의 단정": 65/100 (65%)
# - "극단 비약": 80/100 (80%)
```

**분석**:
```python
# 각 왜곡 유형별로
for dtype in distortion_types:
    # 어떤 현실 → 어떤 왜곡?
    pattern = extract_pattern(dtype)

    # 예시:
    # "연결 존재" → "음모 상정" (90% 일치)
    # "정보 획득" → "불법 단정" (85% 일치)
    # "비리 발견" → "카르텔 존재" (75% 일치)
```

**검증**:
- [ ] 왜곡 패턴이 50% 이상 글에서 반복되는가?
- [ ] 패턴이 일관된가? (같은 유형의 왜곡)
- [ ] 이게 "우연"이 아닌 "구조"인가?

---

### Step 3: 세계관 정의 (왜곡 패턴 → 세계관)
**작업**: 왜곡 패턴을 세계관으로 구조화

```python
# 왜곡 패턴들을 세계관으로 clustering
worldviews = []

# 예시 1: "권력 음모론적 세계관"
worldview_1 = {
    "name": "권력 음모론적 세계관",
    "trigger": ["정보 획득", "연결 발견", "절차 강행"],
    "logic": "X를 보면 → 대안 배제하고 → 악의로 단정하고 → 음모로 확대",
    "distortions": [
        "대안_배제: 합법적 경로 무시",
        "악의_단정: 항상 나쁜 의도",
        "음모_확대: 숨겨진 세력 상정"
    ],
    "belief": "권력은 합법적으로 작동하지 않고 음모와 사찰로 유지된다",
    "actors": ["민주당", "좌파"],
    "supporting_count": 150  // 458개 중 150개가 이 패턴
}

# 예시 2: "외부 위협 확대 세계관"
worldview_2 = {
    "name": "외부 위협 확대 세계관",
    "trigger": ["외국인 유입", "국제 협력", "국경 정책"],
    "logic": "X를 보면 → 위험 가정하고 → 조직범죄 연결하고 → 치안 붕괴로 확대",
    "distortions": [
        "위험_가정: 중립적 정책 → 위협으로",
        "범죄_연결: 유입 → 범죄로 단정",
        "붕괴_확대: 작은 징후 → 사회 붕괴"
    ],
    "belief": "외부 세력은 항상 위협이며 국가 안보를 훼손한다",
    "actors": ["중국", "불법체류자"],
    "supporting_count": 120
}

# 예시 3: "제도 카르텔 세계관"
worldview_3 = {
    "name": "제도 카르텔 세계관",
    "trigger": ["기관 비리", "예산 집행", "인허가"],
    "logic": "X를 보면 → 개별 일탈 아닌 → 구조로 단정하고 → 카르텔로 확대",
    "distortions": [
        "구조_단정: 반복 → 체계로 단정",
        "유착_가정: 연결 → 부패로 해석",
        "카르텔_확대: 비리 → 전체 장악"
    ],
    "belief": "공공기관은 카르텔에 장악되어 국민을 배신한다",
    "actors": ["복지부", "건보공단", "회계법인"],
    "supporting_count": 100
}

# ... 5-10개 worldview
```

**검증**:
- [ ] 각 worldview가 30개 이상 perception 지지하는가?
- [ ] Worldview들이 Topic이 아닌 "논리+왜곡 구조"인가?
- [ ] 전체 coverage 80% 이상인가?

---

### Step 4: Perception → Worldview 연결
**작업**: 각 perception을 worldview에 매칭

```python
for perception in perceptions:
    # 이 perception의 reasoning gaps 패턴이
    # 어느 worldview와 가장 유사한가?

    scores = {}
    for wv in worldviews:
        score = calculate_similarity(
            perception['reasoning_gaps'],
            wv['distortions']
        )
        scores[wv.name] = score

    # 가장 높은 점수의 worldview에 연결
    best_match = max(scores, key=scores.get)
    if scores[best_match] > 0.7:
        link(perception.id, worldview[best_match].id)
```

**검증**:
- [ ] Coverage: 80% 이상 연결되는가?
- [ ] Precision: 10개 샘플 수동 확인 (제대로 매칭?)

---

### Step 5: 실시간 파이프라인
**작업**: 새 글 → 자동 분류

```python
def process_new_content(content):
    # 1. Perception 추출
    perception = extractor.extract(content)

    # 2. 왜곡 패턴 분석
    gaps = perception['reasoning_gaps']

    # 3. Worldview 매칭
    for wv in worldviews:
        if matches(gaps, wv.distortions):
            link(perception, wv)
            notify(f"새 글: {wv.name}")
            break
    else:
        # 매칭 안 되면
        flag_for_review(perception)
```

---

### Step 6: 유기적 점검
**작업**: 매일 실행, 지속적 개선

```python
# 매일 실행
def daily_check():
    # 1. 오늘 새 글들 처리
    new_perceptions = process_today()

    # 2. 매칭 실패 누적 체크
    unmatched = get_unmatched()
    if len(unmatched) > 50:
        # 새 worldview 후보 발견?
        analyze_new_pattern(unmatched)

    # 3. 기존 worldview 변화 추적
    for wv in worldviews:
        trend = get_trend(wv, last_7_days)
        if trend == 'surge':
            alert(f"담론 급증: {wv.name}")
        elif trend == 'decline':
            log(f"담론 감소: {wv.name}")

    # 4. 왜곡 패턴 변화 감지
    new_distortions = detect_new_distortions()
    if new_distortions:
        review_queue.add(new_distortions)
```

---

## 성공 기준

### Perception 품질
- [x] 특수성: 8/10 (검증 완료)
- [x] 전제 포착: 8/10 (검증 완료)
- [x] Reality gap: 9/10 (검증 완료)

### Worldview 품질
- [ ] Who/How/Pattern 구조: 7/10 이상
- [ ] 왜곡 패턴 명확: 각 worldview마다 3개 이상 왜곡 유형
- [ ] 지지도: 각 worldview당 30개 이상 perception

### 시스템 성능
- [ ] Coverage: 80% perception이 worldview에 연결
- [ ] Precision: 수동 검증 10개 중 8개 정확
- [ ] 실시간: 새 글 처리 1분 이내
- [ ] 유기적: 매일 자동 점검 실행

---

## 핵심 차별점 (다른 접근과의 차이)

### ❌ 잘못된 접근
1. **Topic 분류**: "독재", "중국", "카르텔" 등 주제별 분류
   → 세계관이 아님

2. **Keyword 추출**: "사찰", "협박", "음모" 등 단어 빈도
   → 구조 파악 안 됨

3. **Sentiment 분석**: 긍정/부정/중립
   → 왜곡 포착 안 됨

4. **답변 생성**: "그들 시각으로 답변"
   → 목적이 아님

### ✅ 우리의 접근
1. **논리 구조**: Explicit → Implicit → Reasoning → Deep
   → 그들의 완벽한 논리 체계 포착

2. **왜곡 패턴**: Reasoning Gaps 분석
   → 현실과 괴리 지점 발견

3. **일관성**: 100개에서 반복되는 패턴
   → 우연이 아닌 구조적 왜곡

4. **모니터링**: 실시간 추적 + 유기적 점검
   → 변화 감지 및 대응

---

## 최종 결과물

### Worldview 예시
```json
{
  "worldview_id": "wv_001",
  "name": "권력 음모론적 세계관",
  "description": "모든 권력 행위를 음모와 사찰로 해석하는 세계관",

  "logic_structure": {
    "trigger": "권력자의 정보 획득/행동",
    "assumption": "합법적 경로는 불가능",
    "inference": "불법/음모로 단정",
    "conclusion": "독재/사찰로 확대"
  },

  "distortion_patterns": [
    {
      "type": "대안_배제",
      "frequency": "85%",
      "example": "유심정보 → 합법 경로 무시 → 협박 단정"
    },
    {
      "type": "악의_단정",
      "frequency": "90%",
      "example": "정보 획득 → 선의 배제 → 사찰 의도"
    }
  ],

  "core_belief": "권력은 표면적 법과 절차가 아니라 음모와 사찰로 유지된다",

  "statistics": {
    "supporting_perceptions": 150,
    "coverage": "33%",
    "consistency": "95%",
    "trend": "stable"
  },

  "examples": [
    "유심교체 사찰",
    "법사위 강행 → 독재",
    "판사 인사 → 사법부 장악"
  ]
}
```

### Dashboard 표시
```
[권력 음모론적 세계관] 33% (150건)
  최신: "민주 법사위 강행 또..." (2시간 전)
  추이: ━━━━━━━━━━ (안정)

[외부 위협 확대 세계관] 26% (120건)
  최신: "중국인 무비자 실종..." (3시간 전)
  추이: ━━━━━━━━━━ ↑ (증가)

[제도 카르텔 세계관] 22% (100건)
  최신: "복지부 카르텔..." (5시간 전)
  추이: ━━━━━━━━━━ (안정)
```

---

## 다음 단계

### 지금 즉시
1. ✅ 전략 문서 완성 (이것)
2. ⏳ 유저 승인 대기

### 승인 후
1. **10개 Perception 추출 및 검증** (30분)
2. **100개 Perception 추출** (2시간)
3. **왜곡 패턴 분석** (1시간)
4. **Worldview 정의** (2시간)
5. **나머지 358개 처리** (6시간)
6. **실시간 파이프라인 구축** (4시간)
7. **Dashboard 연동** (4시간)

**총 예상 시간: 1-2일**
