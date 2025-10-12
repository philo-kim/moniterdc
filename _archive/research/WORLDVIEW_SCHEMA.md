# 세계관 데이터 구조 설계

## 목표
"독재와 사찰의 부활" 세계관을 데이터로 표현했을 때,
사용자가 **이 렌즈로 세상을 보는 방식**을 이해할 수 있어야 함

---

## 제안 스키마

```typescript
interface Worldview {
  // 기본 정보
  id: string
  title: string  // "독재와 사찰의 부활"

  // 🎯 세계관의 핵심 구조
  frame: {
    // 1. 이 세계관이 보는 세상의 구조
    narrative_structure: {
      // 주인공과 악당
      agents: {
        protagonist: {  // 누가 피해자/희생자인가
          label: string  // "국민", "보수", "우파"
          attributes: string[]  // ["무고한", "억압받는", "각성해야 할"]
        }
        antagonist: {  // 누가 가해자/위협인가
          label: string  // "민주당", "좌파", "친북 세력"
          attributes: string[]  // ["권위주의적", "기만적", "독재적"]
        }
        enablers?: {  // 조력자/공범
          label: string  // "주류 미디어", "통신사", "국가기관"
          role: string  // "좌파 정권의 도구"
        }
      }

      // 인과 시나리오 (이야기 구조)
      causal_scenario: {
        trigger: string  // "좌파 정권의 권력 장악"
        mechanism: string[]  // ["사찰 동원", "사법부 장악", "언론 통제"]
        outcome: string  // "전면적 독재 사회"
        timeframe: string  // "이미 진행 중, 곧 완성"
      }

      // 역사적 패러다임
      historical_pattern: {
        reference: string  // "1970-80년대 독재 정권"
        mapping: string  // "과거 독재가 좌파 형태로 재현"
        evidence_interpretation: string  // "작은 사찰 → 과거 독재의 전조"
      }
    }

    // 2. 해석 패턴 (같은 사건을 어떻게 다르게 보는가)
    interpretation_patterns: [
      {
        domain: string  // "정보 유출"
        baseline_interpretation: string  // 일반: "정보 유출 논란"
        worldview_interpretation: string  // 이 관점: "독재적 사찰의 시작"

        inference_chain: {
          observed_fact: string  // "민주당이 유심교체 정보 알았음"
          assumption: string[]  // ["통신사 협박", "불법 수집"]
          conclusion: string  // "조직적 사찰 체계 구축 중"
          slippery_slope: string  // "작은 사찰 → 전면 감시"
        }

        emotional_valence: "fear" | "anger" | "disgust"  // "fear"
        urgency_level: "high" | "medium" | "low"  // "high"
      },
      {
        domain: "외교 정책",
        baseline_interpretation: "중국과의 협력",
        worldview_interpretation: "국가 매각/홍콩화",
        inference_chain: {...}
      }
      // ... 여러 도메인
    ]

    // 3. 심층 전제 (Deep Presuppositions)
    deep_presuppositions: {
      ontological: [  // 세상의 본질에 대한 믿음
        "정치는 선과 악의 투쟁이다",
        "좌파는 본질적으로 전체주의 성향을 가진다",
        "역사는 반복된다"
      ],

      epistemological: [  // 무엇이 진실인가에 대한 믿음
        "주류 미디어는 좌파에 포섭되어 진실을 왜곡한다",
        "표면적 사건 뒤에는 숨겨진 의도가 있다",
        "작은 징후가 큰 계획의 일부다"
      ],

      moral: [  // 무엇이 선/악인가
        "자유와 권리는 지켜야 할 최고 가치다",
        "권력 추구를 위한 불법은 용납할 수 없다",
        "국가 정체성을 지키는 것이 중요하다"
      ]
    }

    // 4. 감정적 동인 (Emotional Drivers)
    emotional_core: {
      primary_emotion: "fear"  // 두려움
      threat_perception: {
        what: "개인의 자유와 국가 정체성 상실"
        how_imminent: "이미 시작됨, 빠르게 진행 중"
        catastrophic_endpoint: "중국식 감시 독재 사회"
      },

      moral_outrage: {
        violated_values: ["자유", "정의", "투명성"]
        perpetrators: ["민주당", "좌파 정권"]
        demand_for_action: "강력한 저항과 폭로"
      }
    }

    // 5. 언어적 특징 (Linguistic Markers)
    linguistic_patterns: {
      key_metaphors: [
        {
          source: "독재 정권",
          target: "현 좌파 정권",
          mapping: "사찰 = 독재의 도구"
        },
        {
          source: "질병/감염",
          target: "좌파 이념",
          mapping: "친북 세력 = 바이러스"
        }
      ],

      recurring_phrases: [
        "과거 독재의 재현",
        "권력 유지를 위해",
        "마지막 보루",
        "독재의 전조"
      ],

      moral_language: {
        virtue_words: ["자유", "저항", "각성", "진실"],
        vice_words: ["사찰", "탄압", "기만", "매국"]
      }
    }
  }

  // 📊 관측 데이터 (통계)
  observational_data: {
    // 빈도 기반
    most_mentioned_subjects: [
      {entity: "민주당", count: 60, role: "antagonist"},
      {entity: "이재명", count: 21, role: "antagonist"},
      {entity: "좌파", count: 120, role: "antagonist"}
    ],

    keyword_frequency: {
      "권력": 176,
      "좌파": 120,
      "사찰": 67,
      "독재": 54
    },

    temporal_markers: {
      past_references: ["과거 독재", "70-80년대"] ,
      present_framing: ["이미 시작", "진행 중"],
      future_prediction: ["머지않아", "곧 전면화"]
    }
  }

  // 🔗 연결
  perception_ids: string[]  // 137개 perception
  representative_perception_ids: string[]  // 대표 3-5개

  // 📈 메타데이터
  metadata: {
    strength: number  // 세계관 강도
    coherence: number  // 일관성 점수
    created_at: timestamp
    last_updated: timestamp
  }
}
```

---

## 예시: "독재와 사찰의 부활" 실제 데이터

```json
{
  "title": "독재와 사찰의 부활",

  "frame": {
    "narrative_structure": {
      "agents": {
        "protagonist": {
          "label": "국민 / 보수 진영",
          "attributes": ["감시당하는", "권리를 빼앗기는", "각성해야 할"]
        },
        "antagonist": {
          "label": "민주당 / 좌파 정권",
          "attributes": ["권위주의적", "사찰을 동원하는", "독재를 추구하는"]
        },
        "enablers": {
          "label": "통신사, 주류 미디어, 국가기관",
          "role": "좌파 정권의 압력에 굴복해 도구가 됨"
        }
      },

      "causal_scenario": {
        "trigger": "좌파 정권의 권력 장악 욕구",
        "mechanism": [
          "1단계: 개인정보 사찰 (통신사 협박)",
          "2단계: 사법부 장악 시도 (판사 표적화)",
          "3단계: 반대파 제압 (법적 탄압)",
          "4단계: 전면적 감시 체제"
        ],
        "outcome": "중국식 감시 독재 사회 / 홍콩화",
        "timeframe": "이미 1-2단계 진행 중, 빠르게 악화"
      },

      "historical_pattern": {
        "reference": "1970-80년대 군사 독재",
        "mapping": "과거 우파 독재 → 현재 좌파 독재 (형태만 다름)",
        "evidence_interpretation": "유심교체 정보 수집 = 과거 사찰의 현대판"
      }
    },

    "interpretation_patterns": [
      {
        "domain": "정보 유출 사건",
        "baseline_interpretation": "정치적 논란이 있는 정보 유출",
        "worldview_interpretation": "통신사 협박을 통한 조직적 사찰의 시작",

        "inference_chain": {
          "observed_fact": "민주당이 판사의 유심교체 정보를 알았음",
          "assumption": [
            "통신사를 협박했다",
            "법적 절차 없이 불법 수집했다",
            "이 판사만이 아닐 것이다"
          ],
          "conclusion": "체계적 사찰 네트워크가 작동 중",
          "slippery_slope": "작은 사찰 → 광범위 감시 → 독재 체제"
        },

        "emotional_valence": "fear",
        "urgency_level": "high"
      },

      {
        "domain": "외교 정책",
        "baseline_interpretation": "중국과의 경제 협력 확대",
        "worldview_interpretation": "국가를 중국에 매각하는 매국 행위 / 홍콩화",

        "inference_chain": {
          "observed_fact": "중국인 무비자 입국, 친중 정책",
          "assumption": [
            "이재명은 친중 성향",
            "중국의 영향력 확대를 허용",
            "국가 안보보다 개인 이익 우선"
          ],
          "conclusion": "한국이 중국의 속국이 되는 과정",
          "slippery_slope": "경제 의존 → 정치적 압력 → 홍콩식 통제"
        },

        "emotional_valence": "anger",
        "urgency_level": "high"
      }
    ],

    "deep_presuppositions": {
      "ontological": [
        "정치는 자유와 통제의 투쟁이다",
        "좌파 이념은 본질적으로 전체주의를 지향한다",
        "권력은 필연적으로 부패하고 확장하려 한다",
        "역사는 반복되며, 과거 패턴이 재현된다"
      ],

      "epistemological": [
        "표면적 사건 뒤에는 숨겨진 의도와 계획이 있다",
        "주류 미디어는 진실을 보도하지 않는다",
        "작은 징후들은 큰 음모의 일부다",
        "직접적 증거가 없어도 패턴으로 추론할 수 있다"
      ],

      "moral": [
        "개인의 자유와 프라이버시는 신성불가침이다",
        "권력자의 불법은 절대 용납할 수 없다",
        "국가 정체성과 주권을 지켜야 한다",
        "진실을 밝히고 저항하는 것이 의무다"
      ]
    },

    "emotional_core": {
      "primary_emotion": "fear",

      "threat_perception": {
        "what": "개인의 자유, 사생활, 그리고 국가 정체성의 상실",
        "how_imminent": "이미 시작됨 (사찰 징후), 빠르게 진행 중",
        "catastrophic_endpoint": "중국식 감시 독재 사회 / 홍콩의 운명"
      },

      "moral_outrage": {
        "violated_values": ["자유", "법치", "정의", "투명성", "주권"],
        "perpetrators": ["민주당", "이재명", "좌파 정권", "친북 세력"],
        "demand_for_action": "폭로, 저항, 법적 처벌, 정권 교체"
      },

      "identity_defense": {
        "in_group": "자유를 아는 국민, 각성한 시민",
        "out_group": "좌파, 친북, 종북, 깨시민(무지한 좌파 지지자)",
        "boundary_maintenance": "경계를 명확히 하고 저항해야 함"
      }
    },

    "linguistic_patterns": {
      "key_metaphors": [
        {
          "source": "1970-80년대 독재",
          "target": "현 좌파 정권",
          "mapping": "과거 사찰 = 현재 개인정보 수집"
        },
        {
          "source": "질병/바이러스",
          "target": "좌파 이념/친북",
          "mapping": "감염 확산 = 세력 확장"
        },
        {
          "source": "홍콩의 운명",
          "target": "한국의 미래",
          "mapping": "중국 장악 과정 = 한국이 겪을 일"
        }
      ],

      "recurring_phrases": [
        "과거 독재의 재현",
        "권력을 유지하기 위해",
        "마지막 보루 (사법부)",
        "독재의 전조/예고편",
        "이미 시작됐다",
        "빙산의 일각"
      ],

      "moral_language": {
        "virtue_words": ["자유", "각성", "저항", "진실", "폭로", "수호"],
        "vice_words": ["사찰", "탄압", "기만", "매국", "독재", "비호"]
      }
    }
  },

  "observational_data": {
    "most_mentioned_subjects": [
      {"entity": "좌파", "count": 120, "role": "antagonist"},
      {"entity": "민주당", "count": 60, "role": "antagonist"},
      {"entity": "이재명", "count": 21, "role": "antagonist"},
      {"entity": "사법부", "count": 11, "role": "target"}
    ],

    "keyword_frequency": {
      "권력": 176,
      "좌파": 120,
      "국가": 92,
      "통제": 74,
      "사찰": 67,
      "독재": 54,
      "탄압": 39
    },

    "temporal_markers": {
      "past_references": ["과거 독재", "70-80년대", "군사정권"],
      "present_framing": ["이미 시작", "진행 중", "재현되고 있다"],
      "future_prediction": ["머지않아", "곧 전면화", "독재 사회로"]
    }
  }
}
```

---

## 이 구조의 장점

### 1. 진짜 "세계관"을 담음
- 단순 요약이 아니라 **해석 체계 전체**
- 어떻게 보고, 왜 그렇게 보는지

### 2. 사용자 이해 가능
```
사용자: "독재와 사찰의 부활이 뭔데?"

페이지:
  이 관점을 가진 사람들은:
  - 민주당/좌파를 "권위주의적 독재 추구자"로 본다
  - 작은 사찰 징후를 "독재 체제 구축의 시작"으로 해석한다
  - 과거 독재가 좌파 형태로 재현된다고 믿는다
  - 두려워하는 것: 개인 자유 상실, 중국식 감시 사회

  같은 사건도 이렇게 다르게 본다:
  [유심교체] 일반: 정보 유출 / 이 관점: 조직적 사찰
  [친중 정책] 일반: 외교 선택 / 이 관점: 국가 매각

사용자: "아, 이 렌즈로 보면 모든 게 '독재로 가는 과정'으로 보이는구나"
```

### 3. 데이터 기반
- GPT 요약 아님
- 실제 137개 perception에서 추출
- 검증 가능

### 4. 확장 가능
- 다른 세계관도 같은 구조
- 세계관 간 비교 가능
- 시간에 따른 변화 추적 가능

---

## 다음 질문

이 구조가 "세계관"을 제대로 담는다고 생각하세요?

수정하거나 추가해야 할 부분이 있나요?
