# 세계관 데이터 구조 설계 (Framing Theory 기반)

## 이론적 기반

### Framing Theory (Entman, 1993)

**Frame = 현실을 조직하고 해석하는 개념적 렌즈**

Frame의 4가지 기능:
1. **Define problems** - 무엇이 문제인가
2. **Diagnose causes** - 왜 일어났는가
3. **Make moral judgments** - 누가 책임이 있는가
4. **Suggest remedies** - 무엇을 해야 하는가

### Collective Action Frames (Benford & Snow, 2000)

세 가지 핵심 framing 작업:
1. **Diagnostic framing** - 문제 식별 (무엇이 잘못되었는가)
2. **Prognostic framing** - 해결책 제시 (무엇을 해야 하는가)
3. **Motivational framing** - 행동 동기 (왜 지금 행동해야 하는가)

Frame이 효과적이려면:
- **Narrative fidelity** - 기존 경험/믿음과 일관성
- **Experiential commensurability** - 개인 경험과 공명
- **Cultural resonance** - 문화적 맥락에서 의미 있음

---

## 세계관 = Frame 데이터 구조

```typescript
interface WorldviewFrame {
  id: string
  title: string  // "독재와 사찰의 부활"

  // ============================================
  // 1. FRAME DEFINITION (프레임 정의)
  // ============================================

  frame_core: {
    // 1.1 문제 정의 (Problem Definition)
    problem_definition: {
      what: string  // "좌파 정권이 독재 체제를 구축하고 있다"
      scope: string  // "국가 전체 / 사회 시스템"
      severity: "critical" | "serious" | "concerning"  // "critical"
      urgency: string  // "이미 진행 중, 빠르게 악화"
    }

    // 1.2 인과 진단 (Causal Attribution)
    causal_diagnosis: {
      root_cause: string  // "좌파의 권력 유지 욕구"
      responsible_agents: [
        {
          agent: string  // "민주당", "이재명", "좌파 세력"
          role: "primary" | "enabler" | "beneficiary"
          culpability: string  // "의도적으로 독재 추구"
        }
      ]
      mechanism: string[]  // ["사찰 동원", "사법 장악", "언론 통제"]
      evidence_selection: string[]  // 어떤 사실을 증거로 선택하는가
    }

    // 1.3 도덕적 평가 (Moral Evaluation)
    moral_evaluation: {
      victims: string[]  // ["국민", "보수", "판사", "자유"]
      perpetrators: string[]  // ["민주당", "좌파", "친북 세력"]
      violated_values: string[]  // ["자유", "법치", "정의"]
      moral_framing: string  // "선 vs 악", "자유 vs 억압"
    }

    // 1.4 처방 (Treatment Recommendation)
    prognostic_framing: {
      solution: string  // "정권 교체 / 법적 처벌"
      required_action: string[]  // ["폭로", "저항", "각성"]
      actors_for_change: string[]  // ["국민", "보수", "언론"]
      feasibility: string  // "가능하지만 시간이 촉박함"
    }

    // 1.5 행동 동기 (Motivational Appeal)
    motivational_framing: {
      why_act_now: string  // "늦으면 돌이킬 수 없다"
      stakes: string  // "개인의 자유와 국가의 운명"
      identity_appeal: string  // "자유를 아는 각성한 시민"
      emotional_driver: "fear" | "anger" | "hope"  // "fear"
    }
  }

  // ============================================
  // 2. SELECTION & SALIENCE (선택과 강조)
  // ============================================

  frame_operations: {
    // 2.1 현실의 어떤 측면을 선택하는가
    selective_attention: {
      attended_domains: string[]  // ["정치 권력", "사법", "정보 통신"]
      ignored_domains: string[]  // ["경제 정책", "복지", "교육"]

      attended_actors: [
        {
          actor: string  // "민주당"
          attributes_highlighted: string[]  // ["권위주의적", "사찰 동원"]
          attributes_ignored: string[]  // ["정책 성과", "지지율"]
        }
      ]

      attended_events: [
        {
          event_type: string  // "정보 유출"
          frame_as: string  // "독재적 사찰"
          alternative_frames: string[]  // ["행정 실수", "정치적 논란"]
        }
      ]
    }

    // 2.2 무엇을 두드러지게 만드는가
    salience_mechanisms: {
      repetition: string[]  // 반복되는 구절
      emotional_amplification: string  // 감정 증폭 방식
      metaphors: [
        {
          source_domain: string  // "과거 독재"
          target_domain: string  // "현 좌파 정권"
          mapping: string  // "사찰 = 독재의 도구"
        }
      ]
      exemplars: [  // 전형적 사례
        {
          case: string  // "유심교체 사찰"
          why_exemplary: string  // "독재적 사찰의 명확한 증거"
        }
      ]
    }
  }

  // ============================================
  // 3. INTERPRETATION SCHEMAS (해석 도식)
  // ============================================

  interpretation_schemas: {
    // 3.1 Master Frame (상위 프레임)
    master_frame: {
      name: string  // "독재 재현 프레임"
      core_narrative: string  // "과거가 반복된다"
      historical_template: string  // "70-80년대 독재"
      projected_trajectory: string  // "작은 사찰 → 전면 독재"
    }

    // 3.2 구체적 해석 패턴
    interpretation_rules: [
      {
        input: {
          domain: string  // "정보 유출"
          baseline_fact: string  // "민주당이 유심교체 정보 알았음"
        }

        frame_transformation: {
          problem: string  // "사찰"
          cause: string  // "통신사 협박"
          culprit: string  // "민주당"
          trajectory: string  // "독재로 가는 과정"
        }

        inference_chain: {
          observed: string  // "정보를 알았다"
          assumed: string[]  // ["불법 수집", "조직적", "광범위"]
          concluded: string  // "사찰 체계 구축 중"
          extrapolated: string  // "전면 감시 사회로 향함"
        }

        alternative_frames_rejected: [
          {
            frame: string  // "행정 착오"
            why_rejected: string  // "우연으로 보기엔 너무 정교함"
          }
        ]
      }
    ]

    // 3.3 Bridging (연결 전략)
    bridging_to_existing_beliefs: {
      cultural_narratives: string[]  // ["독재의 역사", "자유 투쟁"]
      personal_experiences: string[]  // ["과거 경험", "현재 불안"]
      shared_values: string[]  // ["자유", "정의"]
    }
  }

  // ============================================
  // 4. DEEP STRUCTURE (심층 구조)
  // ============================================

  deep_structure: {
    // 4.1 존재론적 전제 (Ontological)
    worldview_assumptions: {
      nature_of_reality: string[]  // ["정치는 권력 투쟁", "역사는 반복"]
      nature_of_actors: string[]  // ["좌파는 본질적으로 전체주의적"]
      causality_belief: string  // "의도 중심 인과론 (사건 뒤에 의도가 있다)"
    }

    // 4.2 인식론적 전제 (Epistemological)
    knowledge_assumptions: {
      truth_criteria: string  // "표면 너머의 진실을 봐야 함"
      evidence_standard: string  // "작은 징후도 큰 계획의 일부"
      information_trust: [
        {source: "주류 미디어", trust: "low", reason: "좌파 포섭됨"},
        {source: "독립 미디어", trust: "high", reason: "진실 추구"}
      ]
    }

    // 4.3 가치 체계 (Axiological)
    value_hierarchy: [
      {value: "개인 자유", priority: "highest"},
      {value: "법치", priority: "high"},
      {value: "국가 주권", priority: "high"}
    ]
  }

  // ============================================
  // 5. EMOTIONAL & IDENTITY DIMENSIONS
  // ============================================

  affective_dimension: {
    primary_emotions: [
      {
        emotion: "fear",
        target: "개인 자유 상실",
        intensity: "high"
      },
      {
        emotion: "anger",
        target: "좌파의 기만",
        intensity: "high"
      }
    ]

    threat_perception: {
      threat_type: "existential",  // 실존적 위협
      threat_source: "좌파 정권",
      threat_target: "개인 자유 + 국가 정체성",
      imminence: "진행 중",
      reversibility: "아직 가능하지만 시간 촉박"
    }

    collective_identity: {
      in_group: {
        label: "각성한 시민 / 자유 수호자",
        characteristics: ["진실을 아는", "저항하는"]
      },
      out_group: {
        label: "좌파 / 깨시민",
        characteristics: ["세뇌된", "기만하는", "독재 추구"]
      },
      boundary_markers: string[]  // 내집단/외집단 구분 기준
    }
  }

  // ============================================
  // 6. LINGUISTIC MANIFESTATION (언어적 표현)
  // ============================================

  linguistic_patterns: {
    signature_phrases: string[]  // "과거 독재의 재현", "권력 유지를 위해"

    metaphor_systems: [
      {
        type: "journey",  // 여정
        expression: "독재로 가는 길"
      },
      {
        type: "disease",  // 질병
        expression: "좌파 이념이 사회를 병들게"
      }
    ]

    lexical_choices: {
      prefer: ["사찰", "독재", "탄압", "매국"],
      avoid: ["정책", "협력", "개혁"]
    }

    narrative_templates: [
      "과거 [X독재]가 지금 [Y형태]로 재현되고 있다",
      "[주체]가 [수단]으로 [목적]을 추구한다"
    ]
  }

  // ============================================
  // 7. EMPIRICAL GROUNDING (실증적 근거)
  // ============================================

  observational_data: {
    // 실제 137개 perception에서 관측된 데이터
    frequency_analysis: {
      top_subjects: [{entity: string, count: number, role: string}]
      top_keywords: {[key: string]: number}
      temporal_markers: {
        past: string[]
        present: string[]
        future: string[]
      }
    }

    pattern_clusters: [
      {
        cluster_id: number
        size: number
        theme: string
        representative_perception_ids: string[]
      }
    ]

    representative_cases: [
      {
        perception_id: string
        why_representative: string  // 왜 이 perception이 대표적인가
        typicality_score: number
      }
    ]
  }

  // ============================================
  // 8. FRAME RESONANCE (프레임 공명)
  // ============================================

  resonance_factors: {
    narrative_fidelity: {
      score: number  // 0-1
      explanation: string  // 기존 서사와 얼마나 일관되는가
    }

    experiential_commensurability: {
      score: number
      explanation: string  // 개인 경험과 얼마나 공명하는가
    }

    cultural_resonance: {
      score: number
      cultural_themes: string[]  // ["반공", "자유 투쟁"]
      historical_references: string[]  // ["70년대 독재", "민주화"]
    }
  }

  // ============================================
  // METADATA
  // ============================================

  metadata: {
    perception_ids: string[]  // 137개
    representative_perception_ids: string[]  // 3-5개
    created_at: timestamp
    last_updated: timestamp
    coherence_score: number  // 프레임 일관성
    strength_score: number  // 프레임 강도
  }
}
```

---

## 예시: "독재와 사찰의 부활" Frame

```json
{
  "title": "독재와 사찰의 부활",

  "frame_core": {
    "problem_definition": {
      "what": "좌파 정권이 사찰과 사법 장악을 통해 독재 체제를 구축하고 있다",
      "scope": "국가 권력 구조 전체 / 시민 자유 전반",
      "severity": "critical",
      "urgency": "이미 시작됨, 빠르게 진행 중, 임계점 근접"
    },

    "causal_diagnosis": {
      "root_cause": "좌파의 본질적 권위주의 성향과 권력 유지 욕구",
      "responsible_agents": [
        {
          "agent": "민주당 / 이재명",
          "role": "primary",
          "culpability": "의도적으로 독재 추구, 과거 패턴 반복"
        },
        {
          "agent": "통신사, 주류 미디어, 국가기관",
          "role": "enabler",
          "culpability": "압력에 굴복해 도구가 됨"
        }
      ],
      "mechanism": [
        "개인정보 불법 수집 (사찰)",
        "사법부 장악 시도 (판사 표적화)",
        "반대파 법적 탄압",
        "언론 통제"
      ],
      "evidence_selection": [
        "유심교체 정보 파악 사건",
        "법사위 강행 처리",
        "친중 정책",
        "과거 문재인 정부 사례"
      ]
    },

    "moral_evaluation": {
      "victims": ["국민", "보수 진영", "판사", "개인의 자유와 권리"],
      "perpetrators": ["민주당", "좌파 정권", "친북 세력"],
      "violated_values": ["자유", "법치", "정의", "투명성", "국가 주권"],
      "moral_framing": "자유 수호 vs 독재 추구 / 선 vs 악"
    },

    "prognostic_framing": {
      "solution": "정권 교체, 법적 처벌, 시스템 개혁",
      "required_action": ["진실 폭로", "시민 각성", "저항", "법적 대응"],
      "actors_for_change": ["각성한 국민", "보수 진영", "독립 언론"],
      "feasibility": "가능하지만 시간이 촉박함, 지금 행동해야 함"
    },

    "motivational_framing": {
      "why_act_now": "늦으면 돌이킬 수 없다, 홍콩처럼 될 수 있다",
      "stakes": "개인의 자유, 사생활, 국가 정체성, 자녀의 미래",
      "identity_appeal": "자유를 아는 각성한 시민으로서의 의무",
      "emotional_driver": "fear"
    }
  },

  "frame_operations": {
    "selective_attention": {
      "attended_domains": ["정치 권력", "사법", "정보 통신", "외교"],
      "ignored_domains": ["경제 성과", "복지 정책", "환경"],

      "attended_actors": [
        {
          "actor": "민주당",
          "attributes_highlighted": ["권위주의적", "사찰 동원", "독재 추구"],
          "attributes_ignored": ["정책 성과", "지지율", "입법 활동"]
        }
      ],

      "attended_events": [
        {
          "event_type": "개인정보 유출",
          "frame_as": "조직적 사찰의 증거",
          "alternative_frames": ["행정 실수", "정보 공유 과정의 문제"]
        }
      ]
    },

    "salience_mechanisms": {
      "repetition": ["과거 독재의 재현", "권력 유지를 위해", "독재의 전조"],
      "emotional_amplification": "두려움 자극 (홍콩화, 감시 사회)",
      "metaphors": [
        {
          "source_domain": "1970-80년대 독재 정권",
          "target_domain": "현 좌파 정권",
          "mapping": "과거 사찰 = 현재 개인정보 수집"
        }
      ],
      "exemplars": [
        {
          "case": "유심교체 사찰 사건",
          "why_exemplary": "통신사 협박을 통한 불법 사찰의 명확한 증거"
        }
      ]
    }
  },

  "interpretation_schemas": {
    "master_frame": {
      "name": "독재 재현 프레임",
      "core_narrative": "과거 독재가 좌파 형태로 반복되고 있다",
      "historical_template": "1970-80년대 군사 독재의 사찰과 탄압",
      "projected_trajectory": "작은 사찰 → 광범위 감시 → 전면 독재 체제"
    },

    "interpretation_rules": [
      {
        "input": {
          "domain": "정보 유출",
          "baseline_fact": "민주당이 판사의 유심교체 정보를 알았음"
        },

        "frame_transformation": {
          "problem": "불법 사찰",
          "cause": "통신사 협박/압력",
          "culprit": "민주당",
          "trajectory": "사법부 장악을 위한 독재 구축 과정"
        },

        "inference_chain": {
          "observed": "유심교체 정보를 알았다",
          "assumed": [
            "통신사를 협박했다",
            "법적 절차 없이 수집했다",
            "다른 판사들도 감시 중",
            "이건 빙산의 일각"
          ],
          "concluded": "조직적 사찰 네트워크가 작동 중",
          "extrapolated": "사법부 장악 → 독재 완성"
        },

        "alternative_frames_rejected": [
          {
            "frame": "행정 정보 공유",
            "why_rejected": "이렇게 디테일한 개인정보는 일반 공유 범위 초과"
          },
          {
            "frame": "우연한 유출",
            "why_rejected": "특정 판사만 타겟, 너무 정교함"
          }
        ]
      }
    ],

    "bridging_to_existing_beliefs": {
      "cultural_narratives": ["독재의 역사", "민주화 투쟁", "자유 수호"],
      "personal_experiences": ["과거 독재 경험", "현재 불안감"],
      "shared_values": ["자유", "법치", "정의"]
    }
  },

  "deep_structure": {
    "worldview_assumptions": {
      "nature_of_reality": [
        "정치는 자유와 통제의 투쟁이다",
        "역사는 반복된다 (과거 패턴 재현)",
        "권력은 필연적으로 부패하고 확장하려 한다"
      ],
      "nature_of_actors": [
        "좌파는 본질적으로 전체주의적 성향을 가진다",
        "권력자는 권력 유지를 위해 수단을 가리지 않는다"
      ],
      "causality_belief": "의도 중심 인과론 - 사건 뒤에는 숨겨진 의도가 있다"
    },

    "knowledge_assumptions": {
      "truth_criteria": "표면 너머의 진실을 봐야 한다 (음모론적 인식론)",
      "evidence_standard": "작은 징후도 큰 계획의 일부로 해석",
      "information_trust": [
        {
          "source": "주류 미디어",
          "trust": "low",
          "reason": "좌파에 포섭되어 진실 왜곡"
        },
        {
          "source": "독립 미디어/커뮤니티",
          "trust": "high",
          "reason": "진실 추구, 검열 없음"
        }
      ]
    },

    "value_hierarchy": [
      {"value": "개인 자유", "priority": "highest"},
      {"value": "법치", "priority": "high"},
      {"value": "국가 주권", "priority": "high"},
      {"value": "진실/투명성", "priority": "high"}
    ]
  },

  "affective_dimension": {
    "primary_emotions": [
      {
        "emotion": "fear",
        "target": "개인 자유와 사생활 상실",
        "intensity": "high"
      },
      {
        "emotion": "anger",
        "target": "좌파의 기만과 사찰",
        "intensity": "high"
      }
    ],

    "threat_perception": {
      "threat_type": "existential",
      "threat_source": "좌파 정권",
      "threat_target": "개인 자유 + 국가 정체성",
      "imminence": "이미 시작, 빠르게 진행",
      "reversibility": "아직 가능하지만 시간 촉박"
    },

    "collective_identity": {
      "in_group": {
        "label": "각성한 시민 / 자유 수호자",
        "characteristics": ["진실을 아는", "저항하는", "자유를 수호하는"]
      },
      "out_group": {
        "label": "좌파 / 깨시민 / 종북",
        "characteristics": ["세뇌된", "기만하는", "독재 추구", "무지한"]
      },
      "boundary_markers": ["진실 인식", "저항 여부", "자유 가치 수호"]
    }
  }
}
```

---

## 이 구조의 장점

### 1. **학문적 근거**
- Framing Theory의 검증된 구조
- 단순 요약이 아니라 이론적 프레임워크

### 2. **Frame의 작동 방식 표현**
- 무엇을 선택하고 (selection)
- 무엇을 두드러지게 하고 (salience)
- 어떻게 해석하는지 (interpretation)

### 3. **다층적 구조**
- 표면: problem definition, solutions
- 중간: interpretation rules, metaphors
- 심층: ontological/epistemological assumptions

### 4. **행동 지향적**
- Diagnostic (문제) + Prognostic (해결) + Motivational (동기)
- "왜 이렇게 보는가"뿐 아니라 "왜 행동하는가"

### 5. **실증 데이터와 연결**
- 이론적 구조 + 실제 137개 perception 데이터
- 검증 가능

---

## Framing Theory 기반의 핵심 차이

### Before (내 첫 제안):
- 요소들의 나열 (주체, 키워드, 패턴...)
- 정적 구조

### After (Framing Theory):
- **Frame의 작동 방식** (how it works)
- **동적 과정** (현실 → 선택 → 해석 → 행동)

**Frame = "이 렌즈를 쓰면 세상이 이렇게 보이고, 그래서 이렇게 행동하게 된다"**

이게 맞나요?
