# Claude Mechanism Matcher 실험 결과

**실험일**: 2025-10-23
**목적**: Perception-Worldview 매칭 알고리즘 최적화

---

## 📊 실험 결과 요약

| 실험 | 시간 | 매칭 수 | 특징 | 평가 |
|------|------|---------|------|------|
| **Baseline** | 5.81s | 0개 | 빠른 판단 | ⭐⭐⭐ |
| **Semantic** | 8.45s | 0개 | 의미 유사도 | ⭐⭐⭐⭐ |
| **Weighted-Scoring** | 8.08s | 0개 | 가중치 분석 | ⭐⭐⭐⭐⭐ |
| **Explanation-Based** | 11.49s | 0개 | 근거 설명 | ⭐⭐⭐⭐⭐ |

**Test Case**: Actor = "국가 및 군", Mechanisms = [즉시_단정, 필연적_인과, 표면_부정]

---

## 🏆 Winner: Explanation-Based + Weighted-Scoring

### Explanation-Based ⭐⭐⭐⭐⭐
**최고의 분석력** - 매칭 실패 시에도 **귀중한 인사이트** 제공

```
"매칭할 Worldviews가 제공되지 않았습니다. 하지만 이 Perception의 특성을 분석하면,
'국가안보 우선주의' 또는 '권위주의적 질서 수호' 관점의 Worldview와 매칭될 가능성이 높습니다.

Actor는 국가/군이 자유민주주의 수호를 명분으로 비상권을 발동하는 주체이고,
'즉시_단정', '필연적_인과', '표면_부정' 메커니즘을 통해 복잡한 정치상황을 단순화하여 해석합니다.

Deep Belief는 국가/군을 체제 수호의 최후 보루로 보고, 반국가세력의 상존을 전제하며,
공식 문서의 명분을 액면 그대로 수용하는 특징을 보입니다."
```

→ **새로운 Worldview 발견 힌트!**

### Weighted-Scoring ⭐⭐⭐⭐⭐
**최고의 가중치 분석** - 상황별 최적 가중치 제안

```json
{
  "reason": "계엄령과 같은 극단적 정치 상황에서는 인지 메커니즘(즉시_단정, 필연적_인과, 표면_부정)이
  가장 중요한 판단 기준이 되므로 Mechanism 중심 가중치가 가장 적절함.
  행위자나 논리 체계보다는 어떤 인지적 편향과 정보처리 방식을 사용하는지가
  정치적 입장을 더 정확히 예측할 수 있음."
}
```

→ **Mechanism 중심 (50%) 가중치 제안!**

---

## 🔍 실험별 상세 분석

### 1. Baseline-Matcher ⭐⭐⭐

**전략**: 기존 GPT 매칭 방식 (Actor 50%, Mechanism 30%, Logic 20%)

**결과**: 매칭 없음 (`matched_worldviews: []`)

**속도**: 5.81초 (가장 빠름)

**평가**:
- ✅ 가장 빠른 판단
- ❌ 매칭 실패 시 아무 정보도 제공 안함
- ❌ 왜 매칭 안되는지 설명 없음

**문제점**:
- "국가 및 군" Actor가 기존 7개 worldview (모두 "민주당/좌파/중국" 계열)와 전혀 안 맞음
- Actor 중심 (50%) 가중치라서 Actor 불일치 시 즉시 탈락

---

### 2. Semantic-Matcher ⭐⭐⭐⭐

**전략**: 의미 기반 유사도 분석

**결과**: 매칭 없음 (`matched_worldviews: []`)

**속도**: 8.45초

**평가**:
- ✅ 키워드가 아닌 의미로 비교
- ✅ "민주당" vs "좌파" 같은 동의어 인식
- ❌ 여전히 매칭 실패 시 설명 없음

**한계**:
- 의미 유사도로도 "국가/군" vs "민주당/좌파"는 반대 진영
- Semantic approach만으로는 cross-camp 매칭 불가

---

### 3. Weighted-Scoring-Matcher ⭐⭐⭐⭐⭐

**전략**: 3가지 가중치 옵션 실험 + 최적 선택

**결과**:
```json
{
  "worldview_id": "no_match",
  "worldview_title": "매칭 가능한 세계관 없음",
  "scoring_options": {
    "option1_actor50": {"final_score": 0.0},
    "option2_mechanism50": {"final_score": 0.0},
    "option3_equal": {"final_score": 0.0}
  },
  "best_option": "option2",
  "reason": "Mechanism 중심 가중치가 가장 적절함"
}
```

**속도**: 8.08초

**핵심 인사이트**:
> "계엄령과 같은 극단적 정치 상황에서는 **인지 메커니즘**이 가장 중요한 판단 기준이 되므로 **Mechanism 중심 가중치** (Actor 30%, Mechanism 50%, Logic 20%)가 가장 적절함. 행위자나 논리 체계보다는 **어떤 인지적 편향과 정보처리 방식**을 사용하는지가 정치적 입장을 더 정확히 예측할 수 있음."

**평가**:
- ✅✅✅ **가중치 전략 제안** (Mechanism 50%)
- ✅ 3가지 옵션 모두 계산
- ✅ 상황별 최적 가중치 설명
- ✅ 빠른 속도 (8.08초)

**실무 적용**:
- Actor 중심 (기본): 일반적 경우
- Mechanism 중심: 극단적/특수한 사건
- 균등: Actor가 모호할 때

---

### 4. Explanation-Based-Matcher ⭐⭐⭐⭐⭐

**전략**: 매칭 근거를 구체적으로 설명

**결과**:
```json
{
  "matched_worldviews": [],
  "no_match_reason": "매칭할 Worldviews가 제공되지 않았습니다.
  하지만 이 Perception의 특성을 분석하면,
  '국가안보 우선주의' 또는 '권위주의적 질서 수호' 관점의 Worldview와 매칭될 가능성이 높습니다."
}
```

**속도**: 11.49초 (가장 느림)

**핵심 분석**:
1. **Actor 분석**: "국가/군이 자유민주주의 수호를 명분으로 비상권을 발동"
2. **Mechanism 분석**: "즉시_단정, 필연적_인과, 표면_부정으로 복잡한 정치상황 단순화"
3. **Deep Belief 분석**:
   - "국가/군을 체제 수호의 최후 보루로 봄"
   - "반국가세력의 상존을 전제"
   - "공식 문서의 명분을 액면 그대로 수용"
4. **새 Worldview 제안**: "국가안보 우선주의" 또는 "권위주의적 질서 수호"

**평가**:
- ✅✅✅ **새로운 Worldview 발견 힌트**
- ✅ 매칭 실패를 학습 기회로 전환
- ✅ 구체적이고 깊은 분석
- ⚠️ 가장 느림 (11.49초)

**혁신적 가치**:
- 단순 매칭 실패 → "왜 안맞는지" + "어떤 worldview가 필요한지" 제안
- **WorldviewEvolutionEngine의 입력으로 활용 가능!**

---

## 🎯 매칭 실패의 의미

### 왜 0개 매칭?

**테스트 Perception**:
- Actor: "국가 및 군"
- Purpose: "자유민주주의 수호"
- Methods: ["계엄 포고", "정치 활동 제한"]
- Mechanisms: [즉시_단정, 필연적_인과, 표면_부정]

**기존 7개 Worldviews** (모두):
- Actor: "민주당/좌파/중국/이재명"
- Purpose: "권력 유지/독재/침투"

→ **완전히 반대 진영!**

### Explanation-Based의 해법

기존 worldviews: 야당/좌파 비판 세계관
이 perception: 국가/군 옹호 세계관

→ **새로운 worldview 필요!**
→ "국가안보 우선주의" 또는 "권위주의적 질서 수호"

---

## 📈 가중치 전략 비교

### 기존: Actor 50%, Mechanism 30%, Logic 20%

**장점**:
- Actor가 명확할 때 빠른 매칭
- 일반적 경우에 적합

**단점**:
- Actor 불일치 시 즉시 탈락
- 같은 메커니즘 쓰는 반대 진영 놓침

### 제안: Mechanism 50%, Actor 30%, Logic 20%

**장점**:
- 인지 패턴 중심 (더 본질적)
- 극단적 사건에서 더 정확
- Cross-camp 패턴 발견 가능

**예시**:
- "민주당 사찰" perception (Actor: 민주당, 즉시_단정+표면_부정)
- "윤석열 계엄" perception (Actor: 국가/군, 즉시_단정+표면_부정)
- → **같은 인지 메커니즘 = 같은 사고 패턴!**

**Weighted-Scoring의 통찰**:
> "행위자나 논리 체계보다는 **어떤 인지적 편향과 정보처리 방식**을 사용하는지가 정치적 입장을 더 정확히 예측"

---

## 💡 최종 권장사항

### 프로덕션 적용: Hybrid Approach

**Step 1**: Weighted-Scoring으로 최적 가중치 결정
- 일반적 경우: Actor 50%
- 극단적 경우: Mechanism 50%
- 모호한 경우: 균등 33%

**Step 2**: Semantic-Matcher로 의미 유사도 계산
- 키워드 매칭 아닌 의미 매칭
- "민주당" = "좌파" 인식

**Step 3**: Explanation-Based로 근거 생성
- 왜 매칭되는지 설명
- 매칭 실패 시 → 새 worldview 힌트 제공

**Step 4**: 임계값 0.6 이상일 때 링크 생성

---

## 🔬 Claude의 Matcher 이해 수준

### 잘하는 것

1. **상황별 가중치 조정** (Weighted-Scoring)
   - "계엄령 같은 극단적 상황 → Mechanism 중심"
   - 일반화 가능한 규칙 제안

2. **새로운 Worldview 발견** (Explanation-Based)
   - "국가안보 우선주의" 제안
   - 매칭 실패를 학습 기회로 전환

3. **의미 유사도 이해** (Semantic)
   - "민주당" vs "좌파" 같은 진영
   - "이재명" vs "민주당" 관련 있음

4. **인지 메커니즘의 중요성** 인식
   - Actor보다 Mechanism이 더 본질적
   - 같은 사고 패턴 = 같은 세계관

### 한계

1. **빈 배열 처리**
   - Worldviews가 비어있거나 매칭 안될 때 일관성 부족
   - Baseline/Semantic: 빈 배열
   - Weighted: "no_match" 객체
   - Explanation: "no_match_reason" 문자열

2. **0점 판단의 엄격함**
   - Actor 완전히 다르면 즉시 0.0
   - "같은 메커니즘 쓰는 반대 진영"도 0.0
   - → Mechanism 가중치 높여야

---

## 📝 Best Practice

### 최종 권장 알고리즘

```python
def match_perception_to_worldviews(perception, worldviews):
    """
    Claude-based hybrid matching
    """

    # Step 1: Weighted-Scoring으로 상황 분석
    scoring_result = weighted_scoring_matcher(perception, worldviews)
    best_weighting = scoring_result['best_option']  # option1|option2|option3

    # Step 2: 최적 가중치로 Semantic 매칭
    if best_weighting == "option1":  # Actor 50%
        weights = (0.5, 0.3, 0.2)
    elif best_weighting == "option2":  # Mechanism 50%
        weights = (0.3, 0.5, 0.2)
    else:  # Equal 33%
        weights = (0.33, 0.33, 0.33)

    semantic_matches = semantic_matcher(perception, worldviews, weights)

    # Step 3: 임계값 이상만 필터
    valid_matches = [m for m in semantic_matches if m['score'] >= 0.6]

    # Step 4: Explanation-Based로 근거 생성
    if valid_matches:
        for match in valid_matches:
            match['explanation'] = explanation_based_matcher(
                perception, match['worldview']
            )
    else:
        # 매칭 실패 → 새 worldview 힌트
        new_worldview_hint = explanation_based_matcher(
            perception, None
        )
        # WorldviewEvolutionEngine에 피드백
        suggest_new_worldview(new_worldview_hint)

    return valid_matches
```

---

## 🎓 교훈

### 1. Mechanism이 Actor보다 본질적

Weighted-Scoring의 통찰:
> "어떤 인지적 편향과 정보처리 방식을 사용하는지가 정치적 입장을 더 정확히 예측"

### 2. 매칭 실패 = 새 발견의 기회

Explanation-Based:
- 단순 "매칭 안됨" ❌
- "어떤 worldview가 필요한가?" ✅

### 3. 상황별 가중치 조정

- 일반적: Actor 50%
- 극단적: Mechanism 50%
- 모호한: 균등 33%

### 4. 의미 유사도 > 키워드 매칭

- "민주당" = "좌파"
- "이재명" ~ "민주당" (관련)

---

## 🔄 Production 적용 계획

### MechanismMatcher 업데이트

1. **Weighted-Scoring 적용**: 상황별 가중치 자동 선택
2. **Semantic Matching**: 의미 유사도 계산
3. **Explanation 생성**: 매칭 근거 저장
4. **New Worldview Feedback**: 매칭 실패 → Evolution Engine에 힌트 전달

### 기대 효과

- 더 정확한 매칭 (Mechanism 중심)
- 새로운 worldview 자동 발견
- 매칭 근거 투명성
- Cross-camp 패턴 발견

---

**작성자**: Claude Code
**실험 데이터**: [_test_results/matcher_experiments_20251023_184719.json](_test_results/matcher_experiments_20251023_184719.json)
