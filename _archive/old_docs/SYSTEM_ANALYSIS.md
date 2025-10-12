# 담론 세계관 분석 시스템 - 실제 동작 분석

**분석 일시**: 2025-10-11
**목적**: 실제 동작 중인 시스템의 완전한 이해와 본질적 문제 진단

---

## 1. 시스템 현재 상태

### 데이터 현황
```
✅ Contents (원본 글): 458개
✅ Layered Perceptions (3층 분석): 501개
✅ Worldviews (세계관): 9개
✅ Perception-Worldview Links: 487개
```

### 세계관 분포
1. **독재와 사찰의 부활**: 137개 인식 (27%)
2. **기타**: 91개 인식 (18%)
3. **정치보복과 인권 침해**: 85개 인식 (17%)
4. **표현의 자유 억압**: 52개 인식 (10%)
5. **온라인 여론 조작**: 37개 인식 (7%)
6. **복지·보건 카르텔 해체**: 33개 인식 (7%)
7. **체제 취약성과 안보 위기**: 23개 인식 (5%)
8. **이민 정책과 범죄 증가**: 15개 인식 (3%)
9. **중국 산업 불신**: 14개 인식 (3%)

---

## 2. 실제 동작 흐름

### 2.1 데이터 수집 (Content Collection)
**위치**: `engines/collectors/content_collector.py`

```
DC Gallery → 크롤링 → Supabase (contents 테이블)
```

- DC Inside 정치 갤러리 크롤링
- 제목, 본문, URL, 게시일 저장
- 현재 458개 수집 완료

### 2.2 3층 분석 (Layered Perception Extraction)
**위치**: `engines/analyzers/layered_perception_extractor.py`

```python
Content → GPT-5 분석 → Layered Perception
```

**입력**: 원본 글 (제목 + 본문)
**처리**: GPT-5 모델로 3층 구조 분석
- **Layer 1 (Explicit)**: 명시적 주장
- **Layer 2 (Implicit)**: 암묵적 전제
- **Layer 3 (Deep)**: 무의식적 믿음
- **Reasoning Gaps**: 논리 비약 지점

**출력**: `layered_perceptions` 테이블에 저장

**실제 예시**:
```json
{
  "explicit_claims": [
    {
      "subject": "민주당",
      "predicate": "유심교체 정보를 불법으로 얻었다",
      "quote": "유심교체를 어떻게 알아"
    }
  ],
  "implicit_assumptions": [
    "민주당은 통신사를 협박해서 개인 사찰용 정보를 얻는다",
    "맘에 안드는 판사를 제거하기 위해 사찰한다"
  ],
  "reasoning_gaps": [
    {
      "from": "유심교체 정보를 알았다",
      "to": "통신사 협박으로 얻었다",
      "gap": "정상적 방법 가능성은 배제하고 즉시 불법으로 단정"
    }
  ],
  "deep_beliefs": [
    "민주당/좌파는 과거 독재정권처럼 사찰로 반대파를 제거한다",
    "지금의 작은 사찰이 곧 전면적 감시독재 사회로 발전한다"
  ],
  "worldview_hints": "과거 독재 → 현재 재현, 좌파 = 독재 본성"
}
```

### 2.3 세계관 구성 (Worldview Construction)
**위치**: `engines/analyzers/optimal_worldview_constructor.py`

```python
Layered Perceptions (샘플 100개) → GPT-5 분석 → 계층형 세계관 구조
```

**처리**:
1. 100개 perception 샘플링
2. GPT-5에게 공통 패턴 추출 요청
3. 계층형 구조 생성:
   - Category (대분류)
   - Subcategory (세부 세계관)
   - Narrative (서사 구조)
   - Metadata (구조 정보)

**실제 예시** (독재와 사찰의 부활):
```json
{
  "category": "정치 권력과 민주주의",
  "subcategory": "독재와 사찰의 부활",
  "description": "좌파 정권의 사찰과 사법 장악을 통한 독재 재현",
  "priority": "high",
  "metadata": {
    "merged_from": [
      "e0f974eb-3f0a-4ced-a83c-c92d576020f2",
      "9b9418e2-4e3e-4d78-817b-1ed17434a9b3"
    ],
    "estimated_count": 137
  }
}
```

### 2.4 매칭 (Perception → Worldview)
**위치**: `engines/analyzers/hybrid_perception_matcher.py`

```python
Hybrid Matching = Vector Similarity (70%) + Keyword Matching (30%)
```

**처리**:
1. Worldview의 narrative를 embedding
2. Perception의 deep_beliefs를 embedding
3. Cosine similarity 계산 (70% 가중치)
4. Keyword 매칭 (metadata의 key_concepts 기반, 30% 가중치)
5. 최종 점수 > 0.5이면 연결

**결과**: `perception_worldview_links` 테이블에 저장

### 2.5 대시보드 표시
**위치**: `dashboard/app/page.tsx`, `dashboard/app/worldviews/[id]/page.tsx`

```
Worldviews 조회 → Category별 그룹핑 → 계층형 UI 표시
세부 클릭 → Linked Perceptions → 원본 Contents 표시
```

**기능**:
- 카테고리별 세계관 목록
- 각 세계관의 인식 개수, 강도
- 세계관 상세: 3층 분석 결과, 원본 글 링크

---

## 3. 핵심 문제 진단

### 🔴 **문제 1: 세계관이 "주제 분류"가 되어버림**

**현상**:
```
독재와 사찰의 부활
정치보복과 인권 침해
표현의 자유 억압
온라인 여론 조작
...
```

→ 이것은 **Topic Categorization**이지, **Worldview**가 아님

**원인**:
1. GPT-5에게 "공통 패턴 추출"을 요청했지만, 실제로는 "주제 분류"를 반환
2. Narrative가 있지만, 실제로는 "주제에 대한 설명"일 뿐
3. Metadata에 구조가 있지만, 제대로 활용 안 됨

**진짜 세계관이란**:
```
❌ "독재와 사찰의 부활" (주제)
✅ "권력은 합법적 절차가 아니라 음모와 사찰로 작동한다" (세계 작동 원리에 대한 믿음)

❌ "중국 산업 불신" (주제)
✅ "외부 세력은 항상 위협이며, 개방은 필연적으로 안보 위협을 초래한다" (인과 논리)
```

### 🔴 **문제 2: 왜곡 패턴이 포착되지 않음**

**현상**:
- Reasoning Gaps는 추출되고 있음 (개별 perception에)
- 하지만 세계관 구성 시 이게 반영 안 됨
- "왜곡"이 아니라 "그들의 주장"만 정리됨

**실제 데이터 예시**:
```json
// Perception에는 이런 gap이 있음:
{
  "from": "유심교체 정보를 알았다",
  "to": "통신사 협박으로 얻었다",
  "gap": "정상적 방법 가능성은 배제하고 즉시 불법으로 단정"
}

// 하지만 Worldview에는 이게 반영 안 됨
{
  "description": "좌파 정권의 사찰과 사법 장악을 통한 독재 재현"
  // → 왜곡 패턴이 없음! 그냥 주제 설명
}
```

**원인**:
1. `optimal_worldview_constructor.py`에서 reasoning_gaps를 분석에 포함시키지 않음
2. GPT-5에게 "왜곡 패턴 추출"을 명시적으로 요청하지 않음
3. Worldview 구조에 "distortion_patterns" 필드가 없음

### 🔴 **문제 3: 통계 수치가 의미 없음**

**현상**:
```
strength_overall: 0.00  (모든 세계관이 0)
```

**원인**:
- 초기 생성 시에만 계산
- 업데이트 로직이 없음
- `worldview_updater.py`가 있지만 실행 안 됨

### 🔴 **문제 4: "기타" 카테고리가 18%**

**현상**:
- 91개 인식이 "기타"로 분류됨
- 매칭이 제대로 안 되고 있다는 신호

**원인**:
1. 샘플링 문제: 100개만 분석해서 세계관 생성
   - 나머지 400개는 커버 안 됨
2. 매칭 threshold 문제: 0.5 기준이 너무 높거나 낮음

---

## 4. 목적 달성 불가 이유

### 원래 목적 (README.md 기준):
```
"같은 사건을 보고도 완전히 다르게 해석하는 이유를 이해"
"표면 주장 ↔ 심층 믿음의 연결고리 시각화"
"왜 그렇게 생각하는지의 논리 연쇄 재구성"
```

### 현재 시스템이 하는 것:
```
✅ 3층 분석: 잘 되고 있음 (perception 단위)
❌ 세계관 발견: 주제 분류만 됨
❌ 왜곡 패턴: 포착 안 됨
❌ 해석 차이: 구조화 안 됨
```

### 결과:
- **개별 글 분석**은 훌륭함 (Layered Perception)
- **전체 패턴 발견**이 실패 (Worldview = Topic이 됨)
- **왜곡 이해**가 안 됨 (가장 핵심인데 누락)

---

## 5. 실제로 필요한 것 vs 현재 있는 것

### 필요한 것:
```
1. 논리 구조 추출: ✅ (Layered Perception이 잘 함)

2. 왜곡 패턴 발견: ❌
   - Reasoning Gaps는 있는데, 이걸 분석 안 함
   - "대안 배제", "악의 단정", "극단 비약" 같은 패턴을 찾아야 함

3. 세계관 = 왜곡 패턴의 집합: ❌
   - 현재: "독재와 사찰" (주제)
   - 필요: "모든 권력 행위를 음모로 해석하는 구조" (논리 패턴)

4. 실시간 모니터링: ❌
   - 한 번 구성하고 끝
   - 업데이트 로직이 있지만 실행 안 됨
```

### 현재 있는 것:
```
✅ 훌륭한 Perception 분석기 (GPT-5 기반)
✅ 계층형 데이터 구조 (Contents → Perceptions → Worldviews)
✅ 하이브리드 매칭 (Vector + Keyword)
✅ 잘 만들어진 대시보드

❌ 세계관 = 주제 분류 (목적 오해)
❌ 왜곡 패턴 미분석 (핵심 누락)
❌ 정적 시스템 (실시간 추적 없음)
```

---

## 6. 해결 방향

### A. 즉시 개선 가능 (기존 코드 수정)

1. **Worldview Constructor 수정**
   - Reasoning Gaps를 분석에 포함
   - "공통 왜곡 패턴" 추출하도록 프롬프트 변경
   - Worldview 구조에 `distortion_patterns` 추가

2. **전체 데이터 재분석**
   - 100개 샘플이 아니라 전체 501개 분석
   - 또는 더 대표적인 샘플링 전략

3. **매칭 개선**
   - "기타" 비율 낮추기
   - Threshold 조정 또는 다단계 매칭

### B. 구조적 재설계 (권장)

**WORLDVIEW_STRATEGY.md 기반으로**:

```
Phase 1: ✅ Perception 추출 (이미 잘 되고 있음)

Phase 2: ❌ 왜곡 패턴 분석 (새로 구현 필요)
  - Reasoning Gaps clustering
  - 반복되는 왜곡 유형 발견
  - "대안 배제 70%", "악의 단정 65%" 같은 통계

Phase 3: ❌ 세계관 = 왜곡 패턴 (재정의 필요)
  - 주제가 아니라 "논리 구조"
  - 예: "권력 음모론적 세계관" = "대안 배제 → 악의 단정 → 음모 확대"

Phase 4: ⚠️  실시간 모니터링 (자동화 필요)
  - 매일 새 글 처리
  - 추세 변화 감지
  - 새 패턴 발견 알림
```

---

## 7. 다음 단계 권장사항

### Option A: 빠른 개선 (1-2일)
1. Worldview Constructor 프롬프트 수정
2. 전체 데이터 재분석
3. 결과 확인 및 반복

### Option B: 근본적 재설계 (1주일)
1. 왜곡 패턴 분석 엔진 구현 (`distortion_pattern_analyzer.py`)
2. 세계관 정의 재구성 (주제 → 논리 구조)
3. 실시간 파이프라인 구축
4. 대시보드에 왜곡 패턴 표시

### 추천: **Option B**
- 현재 시스템의 기반(Perception)은 훌륭함
- 하지만 목적 달성을 위해서는 구조적 변경 필요
- WORLDVIEW_STRATEGY.md에 정확한 로드맵 있음

---

## 8. 시스템 강점 (보존할 것)

1. **LayeredPerceptionExtractor**: 매우 정교함
   - 3층 분석이 실제로 작동
   - Reasoning Gaps 포착 능력
   - GPT-5 활용이 적절함

2. **데이터 구조**: 잘 설계됨
   - Contents → Perceptions → Worldviews 계층
   - 링크 테이블로 다대다 관계 표현

3. **대시보드**: 사용자 경험 좋음
   - 계층형 UI
   - 3층 분석 결과 시각화
   - 원문 링크 제공

4. **하이브리드 매칭**: 현명한 선택
   - Vector + Keyword 조합
   - 유연한 threshold

---

## 9. 결론

**현재 상태**: 훌륭한 "담론 분석 시스템"이지만, "세계관 분석"은 아님

**핵심 문제**:
- Worldview가 Topic이 되어버림
- 왜곡 패턴이 포착되지 않음
- 이해 목적 달성 불가

**해결 방향**:
- Perception은 그대로 (잘 되고 있음)
- Worldview 재정의 (주제 → 논리 구조)
- 왜곡 패턴 분석 추가 (핵심)
- 실시간 모니터링 구축

**예상 작업**: 1주일 집중 작업으로 근본적 개선 가능

**가장 중요한 인사이트**:
> 이미 **최고의 데이터**(Layered Perceptions)를 가지고 있음.
> 문제는 이 데이터를 **어떻게 해석**하느냐.
> 지금은 "무엇을 말하는가"만 정리함.
> 필요한 것은 "어떻게 왜곡하는가" 분석.

---

**다음**: 이 분석을 바탕으로 어떤 방향으로 개선할지 결정 필요
