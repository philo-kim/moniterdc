# 담론 세계관 분석 시스템 재구축 로드맵

**작성일**: 2025-10-10
**목적**: 현실 왜곡 인과 패턴을 추적하는 시스템 구축

---

## 핵심 깨달음

### 기존 시스템의 문제
- **만든 것**: 사실과 표현 모음집 (단어장)
- **필요한 것**: 인과 관계 왜곡 패턴 추적 시스템

### 세계관의 본질
**세계관 = 반복적으로 사용되는 인과 해석 패턴 (현실 왜곡 장치)**

예시:
- **사실**: 민주당이 지귀연 유심 교체 정보를 알고 있었다
- **현실**: 국회 업무상 필요한 정보 확인 (여러 경로 가능)
- **왜곡**: "통신사 협박 → 사찰 → 권력 유지 메커니즘"
- **일반화**: "민주당은 언제나 사찰로 정적을 제거한다"
- **새 사건 해석**: 조희대 대법원장 국감 → "또 판사 사찰하려는 것"

---

## 현재 상태

### 데이터베이스
- Contents: 458개 (DC갤러리 원문)
- Perceptions: 88개 (추출된 인식)
- Worldviews: 9개 (기존 clustering 결과)

### 기존 세계관 (현재 DB)
1. 독재와 사찰의 부활
2. 이민 정책과 범죄 증가
3. 중국 산업 불신
4. 체제 취약성과 안보 위기
5. 기타
6. 온라인 여론 조작
7. 정치보복과 인권 침해
8. 복지·보건 카르텔 해체
9. 표현의 자유 억압

### 문제점
- 세계관 = 주제 분류 (토픽 모델링)
- 인과 관계 패턴 없음
- 새로운 사건에 대한 예측/해석 불가능

---

## 시스템 재설계

### 목표 시스템 구조

```
Layer 0: Raw Content (DC 게시글)
  ↓
Layer 1: Perception Extraction
  - 사실 추출
  - 감정/어조 추출
  - 주장 추출
  ↓
Layer 2: Causal Pattern Detection  ← 새로 필요
  - 인과 관계 추출 (A → B 관계)
  - 왜곡 논리 추출 ("왜냐하면 X는 Y하기 때문")
  - 증거 선택 패턴 (어떤 사실을 선택/배제하는가)
  ↓
Layer 3: Worldview Construction
  - 반복되는 인과 패턴 = 세계관
  - 패턴 일반화 ("민주당은 언제나 ~한다")
  ↓
Layer 4: Event Interpretation Engine  ← 새로 필요
  - 새 사건 입력
  - 기존 패턴으로 해석
  - 답변 생성
```

---

## Phase 1: 정리 및 현황 파악 (1일)

### 1-1. 파일 정리
- [ ] 불필요한 검증 파일 삭제
- [ ] 핵심 문서만 유지
- [ ] 기존 코드 정리 (engines/ 디렉토리)

### 1-2. 데이터 구조 분석
- [ ] 현재 Perception 구조 상세 분석
- [ ] 실제 DC 게시글 샘플 분석
- [ ] 인과 관계 추출 가능성 검토

### 1-3. 핵심 문서 작성
- [ ] `SYSTEM_ARCHITECTURE.md` - 새로운 시스템 설계
- [ ] `CAUSAL_PATTERN_SPEC.md` - 인과 패턴 정의
- [ ] `DATA_SCHEMA.md` - DB 스키마 변경안

---

## Phase 2: Layer 0→1 재검토 (2일)

### 목표
**원문에서 사실/주장/감정을 정확히 추출하는가?**

### 2-1. 현재 Perception Extractor 분석
- [ ] `engines/analyzers/layered_perception_extractor.py` 코드 리뷰
- [ ] 실제 추출 결과 vs 원문 비교 (10개 샘플)
- [ ] 문제점 도출

### 2-2. 개선 필요 사항
- [ ] 원문 표현 보존 강화
- [ ] 인과 관계 암시 추출 추가
- [ ] 프롬프트 개선

### 2-3. 검증
- [ ] 개선된 extractor로 20개 재추출
- [ ] GPT 평가 (원문 vs 추출 결과)
- [ ] 목표: 평균 8/10 이상

---

## Phase 3: Layer 1→2 설계 - 인과 패턴 추출 (3일)

### 핵심: 새로운 레이어
**"Causal Pattern Detector"**

### 3-1. 인과 패턴 정의
```json
{
  "pattern_id": "uuid",
  "pattern_type": "causal_distortion",
  "structure": {
    "trigger": "민주당이 X 정보를 알고 있다",
    "inference": "통신사 협박을 통해 얻었다",
    "assumption": "정상적 경로는 불가능하다",
    "generalization": "민주당은 언제나 불법적 방법을 쓴다",
    "motivation": "사찰을 통한 정적 제거"
  },
  "evidence_selection": {
    "included": ["지귀연 유심 교체 정보 획득"],
    "excluded": ["국회 정보 요청권", "합법적 조사 경로"],
    "distortion": "선택적 증거 강조"
  },
  "recurrence": {
    "past_events": ["지귀연 사건"],
    "current_events": ["조희대 국감"],
    "prediction": "앞으로도 계속"
  }
}
```

### 3-2. Pattern Detector 구현
- [ ] `engines/analyzers/causal_pattern_detector.py` 작성
- [ ] GPT 프롬프트 설계
- [ ] 88개 perception에서 패턴 추출
- [ ] DB 스키마 추가 (causal_patterns 테이블)

### 3-3. 검증
- [ ] 추출된 패턴 품질 평가
- [ ] 패턴 간 중복/연관성 분석
- [ ] 목표: 10-15개 핵심 인과 패턴

---

## Phase 4: Layer 2→3 재구축 - 세계관 = 패턴 집합 (2일)

### 목표
**세계관 = 반복적으로 사용되는 인과 패턴들의 집합**

### 4-1. 세계관 재정의
```json
{
  "worldview_id": "uuid",
  "title": "독재와 사찰의 부활",
  "core_belief": "민주당은 불법 사찰로 권력을 유지한다",
  "causal_patterns": [
    {
      "pattern_id": "...",
      "weight": 0.9,
      "frequency": 15
    }
  ],
  "interpretation_logic": {
    "when_sees": "민주당의 권한 행사",
    "interprets_as": "사찰의 시도",
    "because": "과거 패턴 (지귀연 사건)"
  }
}
```

### 4-2. Worldview Constructor 재작성
- [ ] `engines/analyzers/causal_worldview_constructor.py` 작성
- [ ] 패턴 기반 clustering
- [ ] 세계관별 해석 로직 생성

### 4-3. 기존 9개 세계관 재구축
- [ ] 각 세계관의 핵심 인과 패턴 추출
- [ ] 해석 로직 명시화
- [ ] DB 업데이트

---

## Phase 5: Layer 4 구현 - 이벤트 해석 엔진 (2일)

### 목표
**새로운 사건이 발생했을 때, 저들이 어떻게 해석할지 예측**

### 5-1. Event Interpreter 설계
```python
class EventInterpreter:
    def interpret(self, event: str, worldview_id: str) -> str:
        """
        새 사건을 특정 세계관으로 해석

        1. 사건 분석 (주체, 행위, 대상)
        2. 관련 인과 패턴 검색
        3. 패턴 적용
        4. 과거 증거 인용
        5. 답변 생성
        """
```

### 5-2. 구현
- [ ] `engines/interpreters/event_interpreter.py` 작성
- [ ] 패턴 매칭 로직
- [ ] 답변 생성 프롬프트

### 5-3. 테스트 케이스
```python
test_cases = [
    {
        "event": "조희대 대법원장 국정감사 추진",
        "worldview": "독재와 사찰의 부활",
        "expected_interpretation": "또 판사 사찰하려는 것. 지귀연 때처럼 통신사 협박해서..."
    },
    # ... 10개 테스트 케이스
]
```

---

## Phase 6: End-to-End 검증 (2일)

### 6-1. 실제 질문 테스트
- [ ] 20개 실제 정치 이슈 준비
- [ ] 각 세계관별 해석 생성
- [ ] GPT 평가: Authenticity, 특정성

### 6-2. 목표 기준
- [ ] Authenticity: 평균 8/10 이상
- [ ] 특정성: 평균 8/10 이상
- [ ] 실제 DC 게시글과 비교했을 때 구별 불가능

### 6-3. 비교 평가
```
실제 DC 게시글 vs 시스템 생성 답변
→ GPT가 구별할 수 없으면 성공
```

---

## Phase 7: 시스템 통합 및 API (2일)

### 7-1. DB 마이그레이션
- [ ] causal_patterns 테이블 생성
- [ ] worldviews 테이블 구조 변경
- [ ] 데이터 마이그레이션 스크립트

### 7-2. API Endpoint
```python
POST /api/interpret
{
  "event": "새로운 정치 이슈",
  "worldview": "독재와 사찰의 부활"
}

Response:
{
  "interpretation": "답변",
  "causal_pattern": "사용된 패턴",
  "evidence": ["과거 사건들"],
  "confidence": 0.85
}
```

### 7-3. 대시보드 업데이트
- [ ] 인과 패턴 시각화
- [ ] 이벤트 해석 인터페이스
- [ ] 패턴 변화 추적

---

## Phase 8: 실시간 모니터링 (1일)

### 8-1. 새 게시글 처리
- [ ] 새 게시글 → Perception 추출
- [ ] 새 인과 패턴 감지
- [ ] 기존 세계관 업데이트

### 8-2. 패턴 진화 추적
- [ ] 시간에 따른 패턴 변화
- [ ] 새로운 세계관 출현 감지
- [ ] 알림 시스템

---

## 성공 기준

### 정량적
1. **Layer 0→1**: 원문 보존도 8/10 이상
2. **Layer 2**: 10-15개 핵심 인과 패턴 추출
3. **Layer 4**: Authenticity 8/10, 특정성 8/10 이상
4. **구별 불가능**: GPT가 실제 게시글 vs 생성 답변 구별 못함

### 정성적
1. **민주 세력의 이해도 향상**: "저들이 왜 저렇게 생각하는지" 이해 가능
2. **대응 전략 수립**: 어떤 근거를 제시해야 프레임을 깰 수 있는지 파악
3. **패턴 예측**: 새로운 이슈에 대해 저들의 반응 예측 가능

---

## 위험 요소 및 대응

### 위험 1: 인과 패턴 추출 정확도
- **대응**: GPT-4o 사용, 프롬프트 반복 개선, 샘플 검증

### 위험 2: 과도한 일반화
- **대응**: 패턴별 증거 카운트, confidence score 부여

### 위험 3: 시스템 복잡도 증가
- **대응**: 단계별 검증, 각 레이어 독립 테스트

---

## 다음 단계

**즉시 시작**: Phase 1 (파일 정리 및 현황 파악)

1. 불필요한 검증 파일 삭제
2. 핵심 문서 작성
3. 현재 데이터 상세 분석

**예상 일정**: 총 15일 (3주)

**최종 목표**:
> "조희대 국감 추진" 입력 → "또 판사 사찰하려는 거야. 지귀연 유심 교체 어떻게 알았는지 봐봐" 출력
