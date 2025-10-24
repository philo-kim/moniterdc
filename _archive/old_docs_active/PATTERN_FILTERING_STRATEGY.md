# Pattern Filtering Strategy

## 문제 정의

**현재 상황**:
- 간단한 규칙 필터링: 효율 36% (8/22개만 잡음)
- 실제 나쁜 패턴: 16.1% (22/137개)
- 놓친 나쁜 패턴: 14개 (10.9%)

**핵심 문제**:
규칙 기반만으로는 불충분. 하지만 모든 패턴을 Claude로 평가하는 것은 비용/시간 문제.

---

## 최적 전략: 2단계 하이브리드 필터링

### Phase 1: 빠른 규칙 기반 필터 (Fast Filter)
**목적**: 명백한 나쁜 패턴을 즉시 제거 (비용 0)

**개선된 규칙** (기존보다 강화):

```python
def fast_filter(text: str) -> tuple[bool, str]:
    """
    Returns: (should_keep, reason_if_filtered)
    """
    text_clean = text.strip()

    # 1. 길이 체크 (더 엄격하게)
    if len(text_clean) < 10:
        return (False, "길이 < 10")

    # 2. 지시대명사로 시작 (확장)
    pronouns = ['이는', '이것은', '이것이', '그것은', '그것이',
                '이', '그', '저', '여기', '거기']
    for p in pronouns:
        if text_clean.startswith(p + ' ') or text_clean.startswith(p + '은') or text_clean.startswith(p + '는'):
            return (False, f"지시대명사 시작: {p}")

    # 3. 대명사 주어 (확장)
    vague_subjects = ['우리가', '우리는', '이들은', '이들이', '그들은', '그들이',
                      '엄마들이', '좌파들이', '보수들이']  # 막연한 집단명
    for s in vague_subjects:
        if text_clean.startswith(s):
            return (False, f"막연한 주어: {s}")

    # 4. 당위문/규범문
    normative = ['해야 한다', '해야한다', '하자', '드리자',
                 '말아야', '않을 것이다', '안 될', '되어야']
    for n in normative:
        if n in text_clean:
            return (False, f"당위문: {n}")

    # 5. 막연한 평가/감정
    vague_eval = ['웃기다', '다행', '부당', '적절', '나쁜', '좋은',
                  '이상하다', '복잡하다', '어렵다', '쉽다']
    # 단, 구체적 주어가 있으면 허용
    has_concrete_subject = any(text_clean.startswith(subj) for subj in
                               ['민주당', '국민의힘', '윤석열', '이재명',
                                '경찰', '검찰', '법원', '정부', '국회'])

    if not has_concrete_subject:
        for v in vague_eval:
            if v in text_clean:
                return (False, f"막연한 평가: {v}")

    # 6. 불완전한 문장 (서술어 없음)
    if not any(end in text_clean for end in ['다', '까', '냐', '요', '음']):
        return (False, "불완전한 문장")

    # 7. 특수문자/이니셜만 (ㅉ, ㅁㅈ 등)
    if len([c for c in text_clean if c.isalnum()]) < len(text_clean) * 0.8:
        return (False, "특수문자 과다")

    return (True, "")
```

**예상 효과**:
- 기존 8개 → 15~18개 정도 걸러낼 것으로 예상 (70-80% 효율)
- 여전히 완벽하지 않음 (4~7개 놓칠 것)

---

### Phase 2: LLM 기반 품질 검증 (Smart Filter)

**핵심 아이디어**: 모든 패턴이 아니라 **의심스러운 패턴만** Claude로 검증

**트리거 조건** (Phase 1 통과했지만 의심스러운 경우):

```python
def needs_llm_check(text: str) -> bool:
    """Phase 1 통과했지만 의심스러운 패턴"""

    # 1. 주어가 모호한 경우
    ambiguous_subjects = ['해당', '관련', '일부', '많은', '몇몇']
    if any(text.startswith(s) for s in ambiguous_subjects):
        return True

    # 2. 지시대명사가 중간에 있는 경우
    if any(word in text for word in ['이 상황', '이 정보', '이 사건', '그 일']):
        return True

    # 3. 막연한 예측
    if any(word in text for word in ['것이다', '될 것', '할 것', '않을 것']):
        return True

    # 4. 짧은 편 (10-15자)
    if 10 <= len(text) < 15:
        return True

    return False
```

**LLM 평가 프롬프트** (배치로 처리):

```python
def batch_llm_check(patterns: list[str]) -> dict[str, bool]:
    """
    의심스러운 패턴들을 배치로 Claude에게 검증

    Returns: {pattern: should_keep}
    """

    prompt = f"""다음은 표면층 패턴 후보들입니다.
각각에 대해 "정보가치가 있는가?"를 판단하세요.

판단 기준:
- ✅ 유지: 구체적 주어 + 구체적 행동/사건
- ❌ 제거: 주어 불명확, 내용 모호, 단순 평가

패턴 목록:
{chr(10).join([f"{i+1}. {p}" for i, p in enumerate(patterns)])}

JSON으로 응답:
{{"results": [{{"id": 1, "keep": true/false, "reason": "..."}}, ...]}}
"""

    # Claude API 호출
    # ...
```

---

## 구현 전략

### 옵션 A: 생성 시점 필터링 (현재 방식)

```python
def create_pattern(self, worldview_id: str, layer: str, text: str) -> str:
    # Phase 1: Fast filter
    should_keep, reason = fast_filter(text)
    if not should_keep:
        logger.debug(f"Fast filter: {reason} - {text}")
        return None

    # Phase 2: LLM check (표면층만, 의심스러운 경우만)
    if layer == 'surface' and needs_llm_check(text):
        # 배치 처리를 위해 임시 저장하고 나중에 검증
        # 또는 일정 개수 모이면 배치 검증
        pass

    # 패턴 생성
    # ...
```

**장점**: 나쁜 패턴이 DB에 안 들어감
**단점**: 생성 시점에 LLM 호출 필요 (느림)

### 옵션 B: 후처리 필터링 (추천)

```python
# 1. 일단 Fast filter만으로 생성
def create_pattern(self, worldview_id: str, layer: str, text: str) -> str:
    should_keep, reason = fast_filter(text)
    if not should_keep:
        return None
    # 생성
    # ...

# 2. 주기적으로 배치 검증 (하루 1회 등)
def cleanup_low_quality_patterns(self, worldview_id: str):
    """의심스러운 패턴들을 배치로 검증하고 제거"""

    # 표면층의 약한 패턴들 (strength < 3.0)
    weak_patterns = self.get_weak_patterns(worldview_id, 'surface', threshold=3.0)

    # 의심스러운 패턴만 필터
    suspicious = [p for p in weak_patterns if needs_llm_check(p['text'])]

    if not suspicious:
        return

    # 배치로 Claude 검증 (최대 50개씩)
    for batch in chunks(suspicious, 50):
        results = batch_llm_check([p['text'] for p in batch])

        # 나쁜 패턴 제거
        for pattern, should_keep in results.items():
            if not should_keep:
                self.archive_pattern(pattern['id'])
```

**장점**:
- 생성은 빠름 (Fast filter만)
- LLM 검증은 배치로 효율적
- 약한 패턴만 검증 (강한 패턴은 이미 검증됨)

**단점**: 나쁜 패턴이 잠시 DB에 존재

---

## 비용 분석

### Fast Filter
- 비용: $0
- 속도: 즉시
- 효율: ~75%

### LLM Filter
- 대상: 전체의 ~20% (의심스러운 패턴만)
- 배치 크기: 50개
- 비용: $0.003/1K tokens × 50개 × 20 tokens = $0.003/batch
- 455 perceptions → ~100 suspicious patterns → 2 batches → **$0.006 total**

### 결론
- 하이브리드 접근으로 **90%+ 효율** 달성 가능
- 비용은 거의 무시 가능 ($0.006)
- 옵션 B (후처리)가 실용적

---

## 실행 계획

1. **Fast filter 강화** - 규칙 추가/개선
2. **Fast filter 테스트** - 137개 샘플로 효율 측정
3. **LLM filter 구현** - needs_llm_check + batch_llm_check
4. **통합 테스트** - 전체 파이프라인 검증
5. **배포** - 후처리 방식으로 적용

---

## 성공 기준

- **최종 나쁜 패턴 비율 < 3%** (현재 10.9%)
- **좋은 패턴 보존율 > 95%**
- **처리 속도**: 생성 시점 영향 최소화
- **비용**: perception당 $0.01 이하
