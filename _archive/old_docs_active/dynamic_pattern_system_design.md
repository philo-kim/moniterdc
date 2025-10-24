# 동적 패턴 관리 시스템 설계

## 목표

표면/암묵/심층이 각각 다른 속도로 변화하는 "살아있는 세계관 생태계" 구현

## 핵심 원리

- **표면층**: 구체적 사건 → 빠르게 들어오고 나감 (휘발성 높음)
- **암묵층**: 해석 틀/전제 → 중간 속도로 변화
- **심층**: 근본 믿음 → 거의 불변

## 기존 구조 유지

```
새 글 수집
    ↓
LayeredPerceptionExtractor (기존)
    → explicit_claims[], implicit_assumptions[], deep_beliefs[]
    ↓
ReasoningStructureExtractor (기존)
    → mechanisms[], actor, logic_chain[]
    ↓
MechanismMatcher (기존)
    → perception_worldview_links 생성
```

## 추가할 부분

### 1. PatternManager (NEW)

```python
class PatternManager:
    """패턴 생명주기 관리"""

    def integrate_perception(self, worldview_id, perception):
        """새 perception을 세계관의 패턴 풀에 통합"""

        for layer in ['surface', 'implicit', 'deep']:
            items = perception[f'{layer}_items']

            for item in items:
                # 기존 패턴과 매칭
                matched = self.find_similar_pattern(
                    worldview_id, layer, item
                )

                if matched:
                    # 기존 패턴 강화
                    self.reinforce_pattern(matched)
                else:
                    # 새 패턴 추가
                    self.create_pattern(worldview_id, layer, item)

    def find_similar_pattern(self, worldview_id, layer, item):
        """층별로 다른 유사도 기준 적용"""

        threshold = {
            'surface': 0.85,   # 엄격 (구체적이라)
            'implicit': 0.70,  # 중간 (패턴이라)
            'deep': 0.60       # 관대 (근본이라)
        }[layer]

        # 임베딩 유사도 계산
        # ...

    def decay_patterns(self, worldview_id):
        """시간 경과로 패턴 약화"""

        # 층별로 다른 decay rate
        # ...

    def cleanup_dead_patterns(self, worldview_id):
        """죽은 패턴 제거"""

        # ...
```

### 2. 데이터베이스 스키마 추가

```sql
-- 세계관별 패턴 풀
CREATE TABLE worldview_patterns (
  id UUID PRIMARY KEY,
  worldview_id UUID REFERENCES worldviews(id),
  layer TEXT NOT NULL,  -- 'surface' | 'implicit' | 'deep'
  text TEXT NOT NULL,

  -- 동적 상태
  strength FLOAT DEFAULT 1.0,
  status TEXT DEFAULT 'active',  -- 'active' | 'fading' | 'dead'

  -- 임베딩 (유사도 계산용)
  embedding vector(1536),

  -- 생명주기
  first_seen TIMESTAMP DEFAULT now(),
  last_seen TIMESTAMP DEFAULT now(),
  appearance_count INT DEFAULT 1,

  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),

  UNIQUE(worldview_id, layer, text)
);

CREATE INDEX idx_active_patterns
ON worldview_patterns(worldview_id, layer, status)
WHERE status = 'active';

CREATE INDEX idx_pattern_embedding
ON worldview_patterns USING ivfflat (embedding vector_cosine_ops)
WHERE status = 'active';
```

### 3. Cron Jobs

```python
# scripts/daily_pattern_update.py
@daily
def daily_update():
    # 1. 어제 새 글 처리
    new_contents = get_yesterday_contents()

    for content in new_contents:
        perception = extract_and_analyze(content)
        worldviews = match_worldviews(perception)

        for wv in worldviews:
            PatternManager().integrate_perception(wv.id, perception)

    # 2. 모든 세계관의 패턴 decay
    for wv in all_worldviews:
        PatternManager().decay_patterns(wv.id)
        PatternManager().cleanup_dead_patterns(wv.id)

# scripts/weekly_pattern_review.py
@weekly
def weekly_review():
    # 암묵층 안정성 재계산
    # ...

# scripts/monthly_evolution.py
@monthly
def monthly_evolution():
    # 심층 변화 감지
    # 세계관 진화 체크
    # ...
```

## 수정이 필요한 기존 파일

### 1. LayeredPerceptionExtractor

**현재**: 3층을 문자열 배열로 반환
```python
{
  "explicit_claims": ["claim1", "claim2"],
  "implicit_assumptions": ["assumption1"],
  "deep_beliefs": ["belief1"]
}
```

**변경 불필요**: 이미 개별 항목으로 분리되어 있어서 OK

### 2. MechanismMatcher

**추가**: perception 매칭 후 PatternManager 호출
```python
def match_and_link(self, perception):
    # 기존 로직: worldview 매칭 + link 생성
    links = self._create_links(perception)

    # 추가: 패턴 통합
    for link in links:
        PatternManager().integrate_perception(
            link.worldview_id,
            perception
        )

    return links
```

### 3. WorldviewEvolutionEngine

**변경 불필요**: 월 1회 실행으로 계속 유지

## 구현 순서

1. ✅ 데이터베이스 스키마 추가 (worldview_patterns 테이블)
2. ✅ PatternManager 엔진 작성
3. ✅ MechanismMatcher에 PatternManager 호출 추가
4. ✅ Daily cron job 작성
5. ✅ Weekly/Monthly cron job 작성
6. ✅ 테스트 및 검증

## 테스트 시나리오

### 시나리오 1: 새 사건 등장 → 표면층에 추가
```
Day 1: "OO 사건 발생" 글 5개 등장
→ surface_patterns에 "OO 사건" 추가 (강도 1.0)

Day 2: "OO 사건" 글 3개 더 등장
→ 패턴 강화 (강도 1.5)

Day 3-7: "OO 사건" 언급 없음
→ 점점 약화 (강도 0.7 → 0.5 → 0.3)

Day 8: 완전 소멸
→ 패턴 제거됨
```

### 시나리오 2: 전제 반복 → 암묵층 강화
```
Week 1-4: "조직적 댓글부대 존재" 계속 등장
→ implicit_patterns에서 강도 증가 (1.0 → 3.5 → 6.0)

Week 5: 언급 감소
→ 약화 시작 (6.0 → 5.4)

Week 8: 다시 활발히 언급
→ 재강화 (5.4 → 7.2)
```

### 시나리오 3: 근본 믿음 → 심층 거의 불변
```
Month 1-6: "외세의 한국 조종" 지속적 등장
→ deep_patterns에서 강도 max (10.0)

Month 7-9: 언급 약간 감소
→ 거의 변화 없음 (10.0 → 9.8)

6개월 후: 여전히 유지
→ 핵심 믿음으로 계속 존재
```

## 예상 결과

세계관 상세 페이지에서:

```
표면층 (7일):
  🔥 "OO 사건" (강도 3.5, 5일간 계속)
  ✨ "XX 사건" (강도 1.2, 2일 전 등장)
  📉 "△△ 사건" (강도 0.4, 소멸 예정)

암묵층 (30일):
  💪 "조직적 댓글부대" (강도 7.2, 안정)
  🔼 "정부 묵인" (강도 4.1, 강화 중)

심층 (90일):
  💎 "외세 조종" (강도 10.0, 핵심)
  💎 "민주주의 위협" (강도 9.2, 핵심)
```
