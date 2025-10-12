# 10가지 프레임 구조화 방식 종합 평가

## 실험 개요
- 실제 데이터: 88개 perception
- 10가지 다른 방식으로 GPT 프레임 구조화 실행
- 각 결과물을 민주세력 이해 관점에서 평가

---

## 결과물 비교

### 방식 1: Foundation Only (순수 데이터)

**결과**:
```
- 88개 perception
- 주요 주체: 김현지, 윤석열 정부, 미군...
- 주요 키워드: 김현지, 중국, 좌파...
- 감정: 불안, 분노, 조롱...
- Valence: negative 62, positive 22
```

**민주세력 이해도**: ★☆☆☆☆ (1/5)

**평가**:
- ✗ 프레임을 전혀 이해 못함
- ✗ 통계만 나열
- ✓ 100% 객관적

**민주세력의 반응**:
> "숫자는 봤는데... 이게 '독재와 사찰의 부활'이랑 무슨 관계야?"

---

### 방식 2: Entman 직접 질문

**결과**:
```json
{
  "problem": "국가 안보와 사회 안전이 위협받고 있다",
  "cause": "중국 정부, 북한 정부, 국내 정책 결정자",
  "moral": "부적절하며 국가와 국민에게 위협적",
  "solution": "국경 안전 강화, 무비자 정책 재검토"
}
```

**민주세력 이해도**: ★★★☆☆ (3/5)

**평가**:
- ✓ Entman 4가지 기능 충족
- ✓ 구조화됨
- △ "독재와 사찰"과 연결이 약함
- △ 중국 무비자에 집중 (제목과 다름)

**민주세력의 반응**:
> "아, 이들은 안보와 안전을 문제로 보는구나. 근데 '독재와 사찰'은 어디 갔지?"

**문제점**:
- 실제 데이터가 "중국 무비자" 이슈가 많아서 GPT가 그것을 문제로 정의
- "독재와 사찰의 부활"이라는 제목과 불일치
- **데이터가 제목을 지지하지 않음**

---

### 방식 3: Competition Frame (대조)

**결과**:
```json
{
  "frame_A": "중국 무비자 위험성 강조 (0.8)",
  "frame_B": "중국 무비자 경제적 이점 (0.6)",
  "frame_C": "관리 필요성 강조 (0.7)",
  "key_differences": "위험 vs 이점 vs 균형"
}
```

**민주세력 이해도**: ★★★★☆ (4/5)

**평가**:
- ✓ 경쟁하는 프레임 명확히 보여줌
- ✓ 대조를 통한 이해 용이
- ✓ Strength score로 비교 가능
- △ "독재와 사찰"은 없음

**민주세력의 반응**:
> "아! 같은 무비자 정책을 '위험(0.8)' vs '이점(0.6)' vs '관리(0.7)'로 다르게 보는구나. 나는 '이점' 쪽인데, 이들은 '위험' 쪽이네!"

**강점**:
- 대조가 명확
- 나와 이들의 차이를 즉시 파악

**문제점**:
- 제목 "독재와 사찰의 부활"을 반영하지 못함
- GPT가 데이터에서 찾은 프레임 (중국 무비자)

---

### 방식 4: Goffman "What's Happening"

**결과**:
```
"사회적, 정치적, 안전 관련 이슈들이
다양한 이해관계자들 사이에서 논의되고 있다"
```

**민주세력 이해도**: ★★☆☆☆ (2/5)

**평가**:
- △ 너무 일반적
- △ "무엇이 일어나고 있는가" 명확하지 않음
- ✗ 프레임 특성 안 보임

**민주세력의 반응**:
> "음... 그래서 뭐가 일어나고 있는거야? 너무 추상적이야."

---

### 방식 5: Lakoff Metaphors

**결과**:
```json
{
  "metaphors": [
    "POLITICS IS WAR (공세, 탄압, 실세)",
    "NATION IS FAMILY (나라, 부모)",
    "IMMIGRATION IS A THREAT (불법체류, 위험, 잠입)"
  ]
}
```

**민주세력 이해도**: ★★★☆☆ (3/5)

**평가**:
- ✓ 은유 발견 흥미로움
- ✓ "IMMIGRATION IS A THREAT" 명확
- △ 은유만으로는 프레임 전체 이해 어려움

**민주세력의 반응**:
> "아, 이들은 '이민 = 위협'으로 보는구나. 나는 '이민 = 기회'로 보는데."

**강점**:
- 언어 패턴으로 프레임 파악
- 트리거 단어 식별

---

### 방식 6: Gamson Package

**결과**:
```json
{
  "core_position": "특정 정치적 인물과 정책에 대한 비판과 의혹",
  "metaphors": ["국경의 문", "희생양", "불법체류의 그림자"],
  "catchphrases": ["김현지 실세론", "중국인 무비자 정책의 위험"],
  "exemplars": ["중국 무비자 정책", "국정자원 화재"],
  "roots": ["과거 국가안보 위기 사례"]
}
```

**민주세력 이해도**: ★★★☆☆ (3/5)

**평가**:
- ✓ 프레임의 구성 요소 잘 보여줌
- ✓ Catchphrases 식별력 있음
- △ 여전히 "독재와 사찰"은 약함

**민주세력의 반응**:
> "패키지로 보니 이해가 좀 더 되네. '김현지 실세론', '무비자 위험'이 핵심이구나."

---

### 방식 7: Hybrid (Foundation + Entman)

**결과**:
```json
{
  "layer1_foundation": {
    "주요_주체": ["김현지", "윤석열 정부"...],
    "valence": {"negative": 62, "positive": 22}
  },
  "layer2_entman": {
    "problem": {
      "what": "중국 무비자로 인한 위험",
      "confidence": 0.9
    },
    "cause": {
      "who": ["중국인 무비자 정책", "윤석열 정부"],
      "confidence": 0.8
    },
    "moral": {
      "judgment": "위험성이 크고 관리가 약하다",
      "confidence": 0.85
    },
    "solution": {
      "what": "정책 재검토 및 관리 강화",
      "confidence": 0.75
    }
  }
}
```

**민주세력 이해도**: ★★★★☆ (4/5)

**평가**:
- ✓ Foundation (데이터) + Entman (해석) 조합
- ✓ **Confidence score** 명시 - 투명성 ⭐
- ✓ 검증 가능
- △ 여전히 중국 무비자 중심

**민주세력의 반응**:
> "Layer 1에서 데이터를 보고, Layer 2에서 해석을 봤어.
> Confidence score가 있으니 얼마나 확실한지 알겠네.
> Problem (0.9), Cause (0.8), Moral (0.85), Solution (0.75)
> 해결책이 제일 약하구나!"

**강점**:
- **Confidence score로 강약 표시** - 매우 중요!
- 데이터와 해석 분리
- 투명함

---

### 방식 8: Hybrid (Foundation + Competition)

**결과**:
```json
{
  "layer1_foundation": {
    "valence_분포": {"negative": 62, "positive": 22}
  },
  "layer2_competition": {
    "dominant_frame": {
      "name": "Negative Perception Frame",
      "strength": 0.74,
      "core_view": "위협, 비판, 잠재적 위험에 집중"
    },
    "competing_frames": [
      {
        "name": "Positive Policy Frame",
        "strength": 0.26,
        "core_view": "정책의 이점과 긍정적 결과 강조"
      }
    ]
  }
}
```

**민주세력 이해도**: ★★★★★ (5/5) ⭐⭐⭐

**평가**:
- ✓ 경쟁 프레임 명확
- ✓ Strength 비율로 즉시 이해 (74% vs 26%)
- ✓ 나와 이들의 차이 즉시 파악
- ✓ 데이터 기반 (valence 분포와 일치)

**민주세력의 반응**:
> "와! 명확하다!
>
> 이 데이터는:
> - Negative Frame (74%) ← 이들
> - Positive Frame (26%) ← 나
>
> 나는 26% 소수 프레임이었구나.
> 이들과 나는 74% vs 26%로 갈라져 있어.
>
> 이제 왜 소통이 안 되는지 알겠어!"

**강점**:
- **가장 명확한 대조**
- **숫자로 표현** (74% vs 26%)
- 즉시 이해 가능
- 데이터 기반 (실제 valence 분포: 70% negative)

---

### 방식 9: Full Integration (Foundation + Entman + Competition)

**결과**:
```json
{
  "layer1_foundation": {...},
  "layer2_entman": {
    "problem": {
      "what": "정치적 감시와 권력 남용",
      "confidence": 0.9
    },
    "cause": {
      "who": ["김현지", "윤석열 정부", "중국", "더불어민주당"],
      "confidence": 0.85
    },
    "moral": {
      "judgment": "권력 남용과 부실한 정책 관리 비판",
      "confidence": 0.88
    },
    "solution": {
      "what": "정책의 투명성 강화",
      "confidence": 0.9
    }
  },
  "layer3_competition": {
    "this_frame": {
      "name": "정치적 감시와 권력 남용에 대한 우려",
      "strength": 0.85
    },
    "competing_frames": [
      {
        "name": "경제 활성화를 위한 정책 필요성",
        "strength": 0.7
      },
      {
        "name": "국가 안보 강화 필요성",
        "strength": 0.75
      }
    ]
  }
}
```

**민주세력 이해도**: ★★★★☆ (4.5/5)

**평가**:
- ✓ 3개 레이어 모두 포함
- ✓ Confidence score 있음
- ✓ Competition도 있음
- ✓ **"정치적 감시와 권력 남용"** ← 제목과 연결!
- △ 복잡함

**민주세력의 반응**:
> "Layer 1: 데이터 확인
> Layer 2: 이들의 프레임
>   - Problem: 권력 남용 (0.9) ← 강함!
>   - Solution: 투명성 강화 (0.9) ← 이것도 강함!
>
> Layer 3: 경쟁 프레임
>   - 이들: 권력 남용 우려 (0.85)
>   - 나: 경제 활성화 (0.7) or 안보 강화 (0.75)
>
> 완전히 이해했어!"

**강점**:
- **제목과 연결** ("정치적 감시와 권력 남용")
- 3개 레이어로 깊이 있음
- Confidence + Competition 모두 있음

**문제점**:
- 복잡함 (3개 레이어)
- 읽는 시간이 길어짐

---

### 방식 10: Democratic Audience (대조 중심)

**결과**:
```json
{
  "quick_summary": "독재와 사찰의 부활 프레임은 현 정부가 민주주의를 위협한다는 시각",
  "key_contrasts": [
    {
      "topic": "무비자 정책",
      "common_view": "관광 활성화",
      "this_frame_view": "국경 안전 위협",
      "why_different": "국가 안보 위협"
    },
    {
      "topic": "언론 관계",
      "common_view": "공정하게 보도",
      "this_frame_view": "정부가 언론 통제",
      "why_different": "여론 조작"
    },
    {
      "topic": "사회 단체",
      "common_view": "다양한 단체와 협력",
      "this_frame_view": "특정 단체를 탄압",
      "why_different": "반대 의견 억압"
    }
  ],
  "what_to_understand": "정부의 행동이 민주주의 원칙을 어떻게 위협하는지",
  "communication_tip": "민주주의의 중요성을 강조하며 접근"
}
```

**민주세력 이해도**: ★★★★★ (5/5) ⭐⭐⭐

**평가**:
- ✓ **민주세력을 위해 맞춤 설계**
- ✓ **Quick summary 즉시 이해**
- ✓ **3가지 대조 예시** 명확
- ✓ **Communication tip까지 제공**
- ✓ 실용적

**민주세력의 반응**:
> "완벽해!
>
> Quick summary: 정부가 민주주의를 위협한다는 시각
>
> 대조:
> 1. 무비자: 나는 '관광', 이들은 '위협'
> 2. 언론: 나는 '공정', 이들은 '통제'
> 3. 단체: 나는 '협력', 이들은 '탄압'
>
> 3가지 핵심 차이를 즉시 파악했어.
> Communication tip까지 있네!"

**강점**:
- **가장 실용적**
- 민주세력 맞춤형
- 즉시 이해 + 행동 가능
- Quick summary 있음

---

## 종합 비교표

| 방식 | 민주세력 이해도 | 프레임 이론 부합도 | 데이터 충실성 | 실용성 | 제목 반영 |
|------|----------------|-------------------|--------------|--------|---------|
| 1. Foundation Only | ★☆☆☆☆ | 0% | ★★★★★ | ★★☆☆☆ | ✗ |
| 2. Entman Direct | ★★★☆☆ | 80% (Entman) | ★★★☆☆ | ★★★☆☆ | △ |
| 3. Competition | ★★★★☆ | 70% (Chong) | ★★★★☆ | ★★★★☆ | ✗ |
| 4. Goffman | ★★☆☆☆ | 60% (Goffman) | ★★★☆☆ | ★★☆☆☆ | ✗ |
| 5. Lakoff | ★★★☆☆ | 70% (Lakoff) | ★★★☆☆ | ★★★☆☆ | △ |
| 6. Gamson | ★★★☆☆ | 75% (Gamson) | ★★★☆☆ | ★★★☆☆ | △ |
| 7. Hybrid F+E | ★★★★☆ | 85% | ★★★★☆ | ★★★★☆ | △ |
| 8. Hybrid F+C | ★★★★★ | 80% | ★★★★★ | ★★★★★ | △ |
| 9. Full Integration | ★★★★☆ | 90% | ★★★★☆ | ★★★☆☆ | ✓ |
| 10. Democratic | ★★★★★ | 75% | ★★★☆☆ | ★★★★★ | ✓ |

---

## 핵심 발견

### 1. 제목 vs 데이터 불일치 문제

**문제**: "독재와 사찰의 부활" vs 실제 데이터 (중국 무비자, 김현지 등)

**GPT 분석 결과**:
- 방식 2, 7: "중국 무비자 정책"이 문제 (데이터 충실)
- 방식 9, 10: "정치적 감시와 권력 남용" (제목 충실)

**결론**:
- 데이터가 제목을 충분히 지지하지 않음
- GPT에게 제목을 명시적으로 주지 않으면 데이터에서 찾은 패턴 반환
- **제목을 명시해야 함**

### 2. Confidence Score의 중요성

**방식 7, 9**에서 Confidence score 사용:

```
Problem: 0.9 (매우 확실)
Cause: 0.8 (확실)
Moral: 0.85 (확실)
Solution: 0.75 (약간 약함)
```

**효과**:
- 투명성: "이게 얼마나 확실한가" 보여줌
- 신뢰성: GPT 해석의 강약 표시
- 민주세력: "해결책이 약하구나" 즉시 파악

**결론**: **Confidence score는 필수!**

### 3. Competition의 강력함

**방식 3, 8, 10**: 경쟁 프레임 대조

**방식 8**의 효과:
```
Negative Frame: 74%
Positive Frame: 26%
```

→ 민주세력: "나는 26% 소수였구나!"

**결론**: **대조가 가장 명확한 이해**

### 4. 민주세력 맞춤형의 효과

**방식 10**: 민주세력을 위해 설계

**특징**:
- Quick summary
- Key contrasts (나 vs 이들)
- Communication tip

**결론**: **청중 맞춤형이 가장 실용적**

---

## 최종 추천

### 🥇 1위: 방식 8 (Hybrid Foundation + Competition)

**이유**:
- ✅ 민주세력 이해도 최고 (5/5)
- ✅ 데이터 충실성 최고 (5/5)
- ✅ 실용성 최고 (5/5)
- ✅ 숫자로 명확 (74% vs 26%)
- ✅ 즉시 이해 가능

**구조**:
```typescript
{
  layer1_foundation: {
    주요_주체: [...],
    주요_키워드: [...],
    valence_분포: {negative: 62, positive: 22}
  },
  layer2_competition: {
    dominant_frame: {
      name: "...",
      strength: 0.74,
      core_view: "..."
    },
    competing_frames: [...]
  }
}
```

**장점**:
- 데이터 기반 (valence 70% negative → frame 74% negative)
- 대조 명확
- 검증 가능
- 간결함

---

### 🥈 2위: 방식 10 (Democratic Audience)

**이유**:
- ✅ 민주세력 이해도 최고 (5/5)
- ✅ 실용성 최고 (5/5)
- ✅ Quick summary
- ✅ Communication tip
- ✅ 행동 가능

**구조**:
```typescript
{
  quick_summary: "한 문장 요약",
  key_contrasts: [
    {
      topic: "...",
      common_view: "일반적 시각",
      this_frame_view: "이 프레임 시각",
      why_different: "차이점"
    }
  ],
  communication_tip: "소통 방법"
}
```

**장점**:
- 청중 맞춤형
- 즉시 이해
- 실용적
- Communication tip

**단점**:
- 데이터 충실성 약함 (GPT가 "common_view" 만듦)

---

### 🥉 3위: 방식 9 (Full Integration)

**이유**:
- ✅ 프레임 이론 부합도 최고 (90%)
- ✅ 3개 레이어로 깊이
- ✅ Confidence + Competition
- ✅ 제목 반영 ("정치적 감시와 권력 남용")

**구조**:
```typescript
{
  layer1_foundation: {...},
  layer2_entman: {
    problem: {what: "...", confidence: 0.9},
    cause: {who: [...], confidence: 0.85},
    moral: {judgment: "...", confidence: 0.88},
    solution: {what: "...", confidence: 0.9}
  },
  layer3_competition: {...}
}
```

**장점**:
- 이론적으로 완벽
- Confidence score
- 제목 반영

**단점**:
- 복잡함 (3개 레이어)
- 읽는 시간 김

---

## 최종 구현 제안

### Phase 1: 방식 8 구현 (Foundation + Competition)

**이유**: 가장 명확하고 즉시 이해 가능

```typescript
interface WorldviewFrameV1 {
  // Layer 1: Foundation (데이터)
  foundation: {
    total_perceptions: number;
    주요_주체: string[];
    주요_키워드: string[];
    주요_감정: string[];
    valence_분포: {
      negative: number;
      positive: number;
      neutral: number;
    };
  };

  // Layer 2: Competition (GPT)
  competition: {
    dominant_frame: {
      name: string;
      strength: number;  // 0-1
      core_view: string;
      evidence: string[];  // 실제 perception에서
    };
    competing_frames: Array<{
      name: string;
      strength: number;
      core_view: string;
      key_difference: string;
    }>;
    interpretation: string;
  };
}
```

**GPT Prompt**:
```
Foundation (실제 데이터):
- Valence: 62 negative, 22 positive, 4 neutral
- 주요 키워드: [...]

이 데이터는 하나의 통일된 프레임인가, 여러 프레임이 경쟁하는가?

Valence 분포를 바탕으로:
- Dominant frame의 strength (예: 0.70 = 70%)
- Competing frames의 strength

JSON으로 반환.
```

---

### Phase 2: 방식 10 추가 (Democratic Audience)

**이유**: 실용적 가치

```typescript
interface WorldviewFrameV2 {
  // V1 전체 포함
  ...WorldviewFrameV1;

  // 추가: 민주세력용 요약
  for_democratic_audience: {
    quick_summary: string;
    key_contrasts: Array<{
      topic: string;
      common_view: string;
      this_frame_view: string;
      why_different: string;
      evidence: string[];
    }>;
    communication_tip: string;
  };
}
```

---

### Phase 3: 방식 9 추가 (Entman Layer)

**이유**: 깊이 있는 이해를 원하는 사용자용

```typescript
interface WorldviewFrameV3 {
  ...WorldviewFrameV2;

  // 추가: Entman 구조 (선택적)
  entman_structure: {
    problem: {
      what: string;
      confidence: number;
      evidence: string[];
    };
    cause: {
      who: string[];
      how: string;
      confidence: number;
      evidence: string[];
    };
    moral: {
      judgment: string;
      victims: string[];
      responsible: string[];
      confidence: number;
      evidence: string[];
    };
    solution: {
      what: string;
      who_acts: string[];
      confidence: number;
      evidence: string[];
    };
  };
}
```

---

## 구현 우선순위

1. **Phase 1 (필수)**: Foundation + Competition
   - 가장 명확
   - 즉시 이해
   - 데이터 기반

2. **Phase 2 (중요)**: + Democratic Audience
   - 실용적
   - Quick summary
   - Communication tip

3. **Phase 3 (선택)**: + Entman
   - 깊이 있는 이해
   - 연구자용
   - 복잡도 증가

---

## 핵심 원칙

1. **Confidence Score 필수**
   - 모든 GPT 해석에 confidence 표시
   - 0-1 스케일
   - 투명성 확보

2. **Competition 중심**
   - 대조가 가장 명확
   - Strength 비율로 표시
   - 데이터 기반 (valence 분포)

3. **청중 맞춤형**
   - 민주세력을 위한 설계
   - Quick summary
   - Communication tip

4. **검증 가능성**
   - 모든 주장에 evidence
   - 원본 perception 연결
   - 데이터로 확인 가능

5. **겸손함**
   - "진짜" 프레임이라 주장 안 함
   - "하나의 해석"임을 명시
   - Confidence로 불확실성 표현

---

## 결론

**최적 구현**: 방식 8 (Foundation + Competition)

**이유**:
- 가장 명확한 대조 (74% vs 26%)
- 데이터 기반 (valence 분포 반영)
- 즉시 이해 가능
- 민주세력에게 최적

**추가 가치**: 방식 10 (Democratic Audience)
- Quick summary
- Communication tip
- 실용적

**장기 목표**: 방식 9 (Full Integration)
- Entman layer 추가
- 깊이 있는 이해
- 연구자용

