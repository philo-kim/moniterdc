# 세계관 엔진 - 최종 설계

## 핵심 통찰

### 문제의 본질
```
DC갤러리는 개별 거짓말을 퍼뜨리는 게 아니라
"왜곡된 세계관"을 구축한다

개별 반박 ≠ 효과적
왜냐하면 사람들은 "전체 이미지"를 기억하기 때문
```

### 세계관이란?
```
여러 주장들이 시간에 걸쳐 누적되어 만들어내는
"전체적 인식의 틀"

예: "민주당 = 친중 = 국가를 위험하게 만든다"
    ↑
    12개의 서로 다른 사건을 연결해서 만든 "큰 그림"
```

### 대응의 차이
```
❌ 개별 대응: "이건 거짓, 저건 거짓" (끝없는 모래주머니)
✅ 세계관 대응: "이 프레임 자체가 조작" (댐 무너뜨리기)
```

---

## 1. 데이터 구조

### 1.1 Worldview (세계관) - 최상위 개념

```sql
CREATE TABLE worldviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 세계관 정의
    title TEXT NOT NULL,  -- "민주당=친중=안보위협"
    description TEXT,  -- 상세 설명

    -- 핵심 요소
    core_subjects TEXT[] NOT NULL,  -- ["민주당", "중국"]
    core_frame TEXT NOT NULL,  -- "대상=속성=결과" 구조

    -- 구조
    narrative_tree JSONB,  -- 세계관의 계층 구조
    /*
    {
      "root": "민주당=친중=위험",
      "branches": [
        {
          "narrative": "친중 정책 추진",
          "claims": ["무비자", "조선족", ...]
        },
        {
          "narrative": "안보 위협 발생",
          "claims": ["간첩", "유출", ...]
        }
      ],
      "connections": [
        {"from": "무비자", "to": "간첩", "type": "cause"}
      ]
    }
    */

    -- 강도 측정
    strength_score FLOAT,  -- 0-1, 얼마나 강하게 구축되었는가
    strength_factors JSONB,  -- {
                              --   "diversity": 0.8,  // 다양한 각도
                              --   "persistence": 0.9,  // 시간적 지속
                              --   "frequency": 0.85,  // 반복 빈도
                              --   "cross_platform": 0.7  // 크로스 플랫폼
                              -- }

    -- 통계
    total_narratives INTEGER DEFAULT 0,
    total_claims INTEGER DEFAULT 0,
    total_instances INTEGER DEFAULT 0,

    -- 시간 추적
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,
    peak_period TIMESTAMPTZ,  -- 가장 활발했던 시기

    -- 추세
    trend TEXT,  -- rising, stable, falling, dead

    -- 임베딩 (유사 세계관 검색)
    embedding vector(1536),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_worldviews_subjects ON worldviews USING GIN(core_subjects);
CREATE INDEX idx_worldviews_trend ON worldviews(trend);
CREATE INDEX idx_worldviews_strength ON worldviews(strength_score DESC);
```

### 1.2 Narrative (내러티브) - 세계관의 구성 요소

```sql
CREATE TABLE narratives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worldview_id UUID REFERENCES worldviews(id) ON DELETE CASCADE,

    -- 내러티브 정의
    title TEXT NOT NULL,  -- "민주당이 친중 정책을 추진한다"
    description TEXT,

    -- 역할
    narrative_role TEXT,  -- premise (전제), evidence (증거), conclusion (결론)

    -- 순서 (세계관 내 위치)
    sequence_order INTEGER,  -- 1, 2, 3... (논리 전개 순서)

    -- 통계
    claim_count INTEGER DEFAULT 0,
    instance_count INTEGER DEFAULT 0,

    -- 시간
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_narratives_worldview ON narratives(worldview_id);
CREATE INDEX idx_narratives_role ON narratives(narrative_role);
```

### 1.3 Claim (주장) - 내러티브의 구체적 증거

```sql
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    narrative_id UUID REFERENCES narratives(id) ON DELETE CASCADE,

    -- 주장 내용
    statement TEXT NOT NULL,  -- "민주당이 중국인 무비자 입국을 허용했다"
    claim_type TEXT,  -- factual, evaluative, causal

    -- 분류
    keywords TEXT[],
    subjects TEXT[],

    -- 검증
    is_true BOOLEAN,  -- true, false, null (불명확)
    verification_source TEXT,  -- 검증 출처

    -- 임베딩
    embedding vector(1536),

    -- 통계
    instance_count INTEGER DEFAULT 0,

    -- 시간
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_claims_narrative ON claims(narrative_id);
CREATE INDEX idx_claims_is_true ON claims(is_true);
CREATE INDEX idx_claims_embedding ON claims
USING ivfflat (embedding vector_cosine_ops);
```

### 1.4 Instance (인스턴스) - 실제 콘텐츠

```sql
CREATE TABLE instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,

    -- 소스 정보
    source_type TEXT NOT NULL,  -- dc_gallery, youtube, article, instagram, etc
    source_url TEXT NOT NULL UNIQUE,
    source_title TEXT,
    source_content TEXT,

    -- 메타데이터
    metadata JSONB,  -- 소스별 특수 정보

    -- 신뢰도
    credibility FLOAT,

    -- 시간
    published_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_instances_claim ON instances(claim_id);
CREATE INDEX idx_instances_source_type ON instances(source_type);
CREATE INDEX idx_instances_published ON instances(published_at DESC);
```

### 1.5 Worldview Rebuttal (세계관 반박)

```sql
CREATE TABLE worldview_rebuttals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worldview_id UUID REFERENCES worldviews(id) ON DELETE CASCADE,

    -- 반박 내용
    title TEXT NOT NULL,
    content TEXT NOT NULL,  -- 세계관 전체의 논리적 오류 설명

    -- 반박 전략
    rebuttal_type TEXT,  -- frame_error (프레임 오류),
                         -- logic_error (논리 오류),
                         -- fact_error (사실 오류),
                         -- context_removal (맥락 제거)

    key_points TEXT[],  -- 핵심 반박 포인트
    /*
    [
      "친중 정의가 모호함 (경제협력 vs 안보양보)",
      "인과관계 비약 (협력이 곧 위협은 아님)",
      "선별적 사실 (윤석열 정부도 중국 협력)"
    ]
    */

    -- 증거
    evidence_urls TEXT[],  -- 뒷받침 자료들

    -- 추천 답변
    suggested_response TEXT,  -- 사용자가 복사할 수 있는 답변

    -- 품질
    credibility FLOAT,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_worldview_rebuttals_worldview ON worldview_rebuttals(worldview_id);
```

### 1.6 Claim Rebuttal (개별 주장 반박)

```sql
CREATE TABLE claim_rebuttals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,

    -- 반박 내용
    title TEXT NOT NULL,
    content TEXT NOT NULL,

    -- 소스
    source_type TEXT,  -- factcheck, official, user_submitted
    source_url TEXT,

    -- 품질
    credibility FLOAT,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_claim_rebuttals_claim ON claim_rebuttals(claim_id);
```

### 1.7 Claim Connection (주장 간 연결)

```sql
CREATE TABLE claim_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    from_claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,
    to_claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,

    -- 연결 유형
    connection_type TEXT,  -- cause (인과), support (지지),
                          -- temporal (시간적 순서), contrast (대조)

    strength FLOAT,  -- 0-1, 연결 강도

    -- 누가 이 연결을 만들었나
    detected_by TEXT,  -- auto (자동 감지), manual (수동 설정)

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(from_claim_id, to_claim_id, connection_type)
);

CREATE INDEX idx_claim_connections_from ON claim_connections(from_claim_id);
CREATE INDEX idx_claim_connections_to ON claim_connections(to_claim_id);
```

---

## 2. 핵심 엔진

### 2.1 세계관 추출 엔진

```python
class WorldviewExtractor:
    """주장들에서 세계관 자동 추출"""

    async def extract_worldview(self, claims: List[Claim]) -> Worldview:
        """
        개별 주장들에서 그들이 만들려는 "큰 그림" 추출

        단계:
        1. 주장들의 공통 패턴 찾기
        2. 주장들 간의 논리적 연결 파악
        3. GPT로 전체 세계관 요약
        4. 세계관 구조 생성
        """

        # 1. 공통 요소 추출
        common_subjects = self.find_common_subjects(claims)
        common_sentiment = self.analyze_sentiment_pattern(claims)

        # 2. 주장들 간 연결 파악
        connections = await self.detect_connections(claims)

        # 3. GPT로 세계관 요약
        worldview_summary = await self.gpt_summarize_worldview(
            claims, connections
        )

        # 4. 세계관 구조 생성
        narrative_tree = self.build_narrative_tree(
            claims, connections, worldview_summary
        )

        # 5. 강도 계산
        strength = self.calculate_worldview_strength(
            claims, connections, timeline
        )

        return Worldview(
            title=worldview_summary['title'],
            core_subjects=common_subjects,
            narrative_tree=narrative_tree,
            strength_score=strength
        )

    async def gpt_summarize_worldview(
        self,
        claims: List[Claim],
        connections: List[Connection]
    ) -> Dict:
        """
        GPT로 세계관 요약
        """

        response = await openai.chat.completions.create(
            model="gpt-5-mini",
            messages=[{
                "role": "system",
                "content": """당신은 정치 세계관 분석 전문가입니다.

여러 개별 주장들을 분석하여 이들이 만들어내는
**전체적인 세계관/프레임**을 추출하세요.

세계관은:
- 대상 = 속성 = 결과 구조
- 예: "민주당 = 친중 = 안보위협"

주어진 주장들:
{claims_list}

연결 관계:
{connections}

다음을 추출하세요:
1. 전체 세계관 (한 문장)
2. 핵심 프레임 구조
3. 하위 내러티브들
4. 이 세계관이 전달하려는 핵심 메시지

JSON 형식으로 반환:
{
  "title": "민주당=친중=안보위협",
  "core_frame": "대상=속성=결과",
  "core_message": "민주당은 중국과 결탁해 한국을 위험하게 만든다",
  "narratives": [
    {
      "title": "친중 정책 추진",
      "role": "premise",
      "claims": ["claim_1", "claim_2"]
    },
    {
      "title": "안보 위협 발생",
      "role": "conclusion",
      "claims": ["claim_3", "claim_4"]
    }
  ]
}"""
            }]
        )

        return parse_json(response)

    def calculate_worldview_strength(
        self,
        claims: List[Claim],
        connections: List[Connection],
        timeline: List[datetime]
    ) -> float:
        """
        세계관 강도 계산

        고려 요소:
        1. 다양성 (diversity): 여러 각도에서 공격하는가?
        2. 지속성 (persistence): 시간적으로 지속되는가?
        3. 빈도 (frequency): 얼마나 자주 반복되는가?
        4. 연결성 (connectivity): 주장들이 논리적으로 연결되는가?
        5. 크로스 플랫폼 (cross_platform): 여러 채널에 걸쳐있는가?
        """

        # 1. 다양성: 주장들이 다양한 주제를 다루는가
        diversity = len(set([c.keywords[0] for c in claims])) / len(claims)

        # 2. 지속성: 첫 등장부터 최근까지 기간
        time_span = (timeline[-1] - timeline[0]).days
        persistence = min(time_span / 90, 1.0)  # 90일 기준

        # 3. 빈도: 인스턴스 수
        frequency = min(len(claims) / 50, 1.0)  # 50개 기준

        # 4. 연결성: 연결 비율
        max_connections = len(claims) * (len(claims) - 1) / 2
        connectivity = len(connections) / max_connections if max_connections > 0 else 0

        # 5. 크로스 플랫폼: 소스 다양성
        source_types = set([inst.source_type for c in claims for inst in c.instances])
        cross_platform = len(source_types) / 5  # 5개 플랫폼 기준

        # 가중 평균
        strength = (
            diversity * 0.2 +
            persistence * 0.25 +
            frequency * 0.25 +
            connectivity * 0.15 +
            cross_platform * 0.15
        )

        return min(strength, 1.0)
```

### 2.2 세계관 반박 생성 엔진

```python
class WorldviewRebuttalGenerator:
    """세계관 전체를 반박하는 논리 생성"""

    async def generate_rebuttal(self, worldview: Worldview) -> WorldviewRebuttal:
        """
        세계관의 논리적 허점을 찾아 반박 생성
        """

        # 1. 개별 주장들의 팩트체크
        claim_facts = await self.factcheck_claims(worldview.claims)

        # 2. 논리 구조 분석
        logic_analysis = await self.analyze_logic_structure(
            worldview.narrative_tree
        )

        # 3. GPT로 세계관 반박 생성
        rebuttal = await self.gpt_generate_worldview_rebuttal(
            worldview, claim_facts, logic_analysis
        )

        return rebuttal

    async def gpt_generate_worldview_rebuttal(
        self,
        worldview: Worldview,
        claim_facts: List[Dict],
        logic_analysis: Dict
    ) -> WorldviewRebuttal:
        """
        GPT로 세계관 반박 생성
        """

        response = await openai.chat.completions.create(
            model="gpt-5-mini",
            messages=[{
                "role": "system",
                "content": """당신은 정치 논리 반박 전문가입니다.

주어진 세계관의 **전체적인 논리 구조**를 분석하고
개별 사실이 아닌 **프레임 자체의 오류**를 지적하세요.

세계관: {worldview_title}

구조:
{narrative_tree}

개별 사실 검증:
{claim_facts}

논리 분석:
{logic_analysis}

다음을 생성하세요:
1. 이 세계관의 핵심 논리 구조
2. 구조적 오류 (프레임 오류, 논리 비약, 선별적 사실 등)
3. 핵심 반박 포인트 (3-5개)
4. 사용자가 사용할 수 있는 간결한 반박 답변

JSON 형식:
{
  "title": "친중=위험 공식의 구조적 오류",
  "rebuttal_type": "frame_error",
  "key_points": [
    "친중 정의가 모호함 (경제협력 vs 안보양보)",
    "인과관계 비약 (협력 ≠ 위협)",
    "선별적 사실 제시 (윤석열 정부도 중국 협력)"
  ],
  "content": "상세 설명...",
  "suggested_response": "간결한 답변..."
}"""
            }]
        )

        return parse_worldview_rebuttal(response)
```

### 2.3 형성 과정 추적 엔진

```python
class WorldviewFormationTracker:
    """세계관이 시간에 따라 어떻게 구축되는지 추적"""

    def track_formation(self, worldview_id: UUID) -> FormationTimeline:
        """
        세계관 형성 과정 추적

        반환:
        - 시간순 이벤트
        - 각 단계에서의 강도 변화
        - 주요 전환점
        """

        # 1. 모든 인스턴스를 시간순으로
        instances = get_instances_chronological(worldview_id)

        # 2. 시간 구간별 그룹핑 (주 단위)
        weekly_groups = group_by_week(instances)

        # 3. 각 구간의 특징 분석
        timeline = []
        for week, instances in weekly_groups:
            phase = self.analyze_phase(instances)
            timeline.append({
                'date': week,
                'instance_count': len(instances),
                'new_claims': phase.new_claims,
                'phase_type': phase.type,  # seed, growth, peak, maintenance
                'strength': phase.strength
            })

        # 4. 주요 전환점 식별
        turning_points = self.identify_turning_points(timeline)

        return FormationTimeline(
            phases=timeline,
            turning_points=turning_points
        )

    def analyze_phase(self, instances: List[Instance]) -> Phase:
        """
        특정 시기의 특징 분석
        """

        # 새로운 주장이 나타났는가?
        new_claims = [i.claim for i in instances if i.claim.first_seen == i.published_at]

        # 단계 판단
        if len(new_claims) > 0 and len(instances) < 5:
            phase_type = 'seed'  # 씨앗 단계
        elif len(instances) > previous_week * 1.5:
            phase_type = 'growth'  # 성장 단계
        elif len(instances) > 20:
            phase_type = 'peak'  # 정점 단계
        else:
            phase_type = 'maintenance'  # 유지 단계

        return Phase(
            type=phase_type,
            new_claims=new_claims,
            strength=calculate_phase_strength(instances)
        )
```

---

## 3. 통합 파이프라인

### 3.1 콘텐츠 수집 → 세계관 업데이트

```python
async def process_content(content: Content):
    """
    새 콘텐츠를 수집하고 세계관 업데이트
    """

    # 1. 주장 추출
    claims = await extract_claims(content)

    for claim_data in claims:
        # 2. 기존 Claim 매칭
        claim = await find_or_create_claim(claim_data)

        # 3. Instance 저장
        instance = await save_instance(claim.id, content)

        # 4. Narrative 할당
        narrative = await assign_to_narrative(claim)

        # 5. Worldview 할당/업데이트
        worldview = await assign_to_worldview(narrative)

        # 6. 연결 감지 (이 주장과 관련된 다른 주장들)
        await detect_and_save_connections(claim, worldview)

        # 7. 세계관 강도 재계산
        await update_worldview_strength(worldview.id)

        # 8. 세계관이 강하게 구축되면 자동 반박 생성
        if worldview.strength_score > 0.7:
            await generate_worldview_rebuttal(worldview.id)
```

### 3.2 자동 세계관 발견

```python
async def discover_worldviews():
    """
    주기적으로 실행: 새로운 세계관 패턴 발견
    """

    # 1. 최근 N일간의 모든 주장 수집
    recent_claims = get_recent_claims(days=30)

    # 2. 주제별 그룹핑
    claim_groups = group_by_subjects(recent_claims)

    for subject, claims in claim_groups:
        # 3. 주장들 간 유사도 계산
        similarity_matrix = calculate_claim_similarities(claims)

        # 4. 클러스터링 (밀접하게 연결된 주장들)
        clusters = cluster_by_similarity(similarity_matrix, threshold=0.7)

        for cluster in clusters:
            # 5. 이미 세계관이 있는지 확인
            existing = find_existing_worldview(cluster.claims)

            if not existing:
                # 6. 새 세계관 추출
                worldview = await WorldviewExtractor().extract_worldview(
                    cluster.claims
                )

                # 7. 저장
                await save_worldview(worldview)
```

---

## 4. 대시보드 UI

### 4.1 메인 뷰: 세계관 목록

```
┌───────────────────────────────────────────────────────────────┐
│ 🌍 DC갤러리가 구성하는 왜곡된 세계관                          │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ 📊 활성 세계관 (강도 0.7 이상)                                │
│                                                               │
│ 1. 민주당=친중=안보위협                                        │
│    ▓▓▓▓▓▓▓▓▓░ 강도 0.89 (매우 강함)                         │
│    • 89개 인스턴스 (DC갤 56, 유튜브 23, 인스타 10)            │
│    • 3개월간 지속적 구축 ↗                                    │
│    • 최근 7일: 급증 +34건                                     │
│    ⚠️  [세계관 반박 보기]                                     │
│                                                               │
│ 2. 이재명=범죄자=민주당붕괴                                    │
│    ▓▓▓▓▓▓▓░░░ 강도 0.74 (강함)                              │
│    • 67개 인스턴스 (DC갤 45, 유튜브 15, 기사 7)               │
│    • 최근 2주간 급증 (사법리스크)                             │
│    ⚠️  [세계관 반박 보기]                                     │
│                                                               │
│ 3. 윤석열=국가수호자=한미동맹                                  │
│    ▓▓▓▓▓░░░░ 강도 0.56 (중간)                               │
│    • 42개 인스턴스                                            │
│    • 성장 중 →                                                │
│                                                               │
│ ────────────────────────────────────────────────────────      │
│                                                               │
│ 📈 형성 중인 세계관 (강도 0.3-0.7)                            │
│                                                               │
│ • 한국언론=편파=조작 (0.45, 23건)                             │
│ • 검찰=정치도구 (0.38, 18건)                                  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 4.2 세계관 상세 뷰

```
┌───────────────────────────────────────────────────────────────┐
│ 🎯 세계관: "민주당=친중=안보위협"                             │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ 📊 개요                                                       │
│ • 강도: 0.89 (매우 강함)                                      │
│ • 기간: 2024-11-15 ~ 현재 (3개월)                            │
│ • 총 89건 (DC갤 56, 유튜브 23, 인스타 10)                    │
│ • 추세: 상승 ↗ (최근 7일 +34건)                              │
│                                                               │
│ ────────────────────────────────────────────────────────      │
│                                                               │
│ 🏗️  구조: 이 세계관이 어떻게 만들어지는가                     │
│                                                               │
│     [민주당 = 친중 = 안보위협]                                │
│              │                                                │
│       ┌──────┴──────┐                                        │
│       │             │                                        │
│   [친중 정책]    [안보 위협]                                  │
│       │             │                                        │
│   ┌───┼───┐     ┌───┼───┐                                   │
│   │   │   │     │   │   │                                   │
│ 무비자 조선족 중국   간첩 군사   정보                          │
│  허용  비호  로비   유입 정보   유출                          │
│ (12건)(8건)(6건) (14건)(5건) (3건)                           │
│                                                               │
│ 💡 논리 흐름:                                                 │
│ 1. 전제: "민주당이 친중 정책을 추진한다"                      │
│ 2. 증거: 무비자, 조선족 비호, 중국 로비                      │
│ 3. 결론: "따라서 안보가 위협받는다"                           │
│ 4. 증거: 간첩 유입, 군사정보 유출                            │
│                                                               │
│ ────────────────────────────────────────────────────────      │
│                                                               │
│ 📈 형성 과정: 세계관이 어떻게 구축되었는가                    │
│                                                               │
│  2024-11 ░░░▓▓ 씨앗 단계 (5건)                               │
│          "무비자 허용" 주장 시작                              │
│                                                               │
│  2024-12 ░▓▓▓▓▓▓ 성장 단계 (19건)                            │
│          "조선족 도주" 추가 → 친중 프레임 강화                │
│                                                               │
│  2025-01 ▓▓▓▓▓▓▓▓▓▓▓ 정점 단계 (65건)                       │
│          "간첩 의혹" 추가 → 안보위협 연결                     │
│          크로스 플랫폼 확산 (유튜브, 인스타)                  │
│                                                               │
│ 🔄 주요 전환점:                                               │
│ • 2024-12-03: "조선족 도주" 소문으로 급증                     │
│ • 2025-01-15: 유튜브 채널 3개가 동시 확산                    │
│                                                               │
│ ────────────────────────────────────────────────────────      │
│                                                               │
│ ❌ 세계관 반박: 프레임의 구조적 오류                          │
│                                                               │
│ 이 세계관의 핵심 오류:                                        │
│                                                               │
│ 1. 🔴 용어 조작: "친중"의 정의가 모호                         │
│    • 경제 협력 ≠ 안보 양보                                    │
│    • 모든 정부가 중국과 경제 협력 필수                        │
│                                                               │
│ 2. 🔴 논리 비약: 협력 → 위협의 인과관계 없음                  │
│    • 경제와 안보는 분리 가능                                  │
│    • 윤석열 정부도 중국과 교역 1위 유지                       │
│                                                               │
│ 3. 🔴 선별적 사실: 민주당 정책만 부각                         │
│    • 무비자: 실제로는 윤석열 정부 B-2 정책                   │
│    • 한중 교역: 정부 불문 경제적 필수                         │
│                                                               │
│ 4. 🔴 허위 연결: 무관한 사건들을 억지로 연결                  │
│    • "조선족 도주"는 미확인 소문                              │
│    • "간첩 의혹"과 무비자 정책은 무관                         │
│                                                               │
│ 💬 추천 반박 답변:                                            │
│                                                               │
│ "경제 협력과 안보는 별개입니다. 모든 정부가 중국과            │
│  경제 협력을 하며, 이것이 곧 안보 위협을 의미하지             │
│  않습니다. 실제로 무비자 정책은 윤석열 정부의 B-2             │
│  환승무비자 재개이며, 한중 교역은 경제적 필수입니다.          │
│  개별 사실들을 왜곡해 '친중=위협'이라는 허위 프레임을         │
│  만들어내고 있습니다."                                        │
│                                                               │
│ [📋 답변 복사]                                                │
│                                                               │
│ 📚 증거 자료:                                                 │
│ • SBS 팩트체크: "무비자는 윤석열 정부 정책" (신뢰도 0.9)     │
│ • 나무위키: "무비자 정책 연혁" (신뢰도 0.7)                  │
│ • 외교부 공식 자료: "한중 경제협력 현황" (신뢰도 0.95)       │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 4.3 개별 콘텐츠 확인 뷰

```
사용자가 DC갤 URL 입력:

┌───────────────────────────────────────────────────────────────┐
│ 🔍 콘텐츠 분석 결과                                           │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ 📱 원본: DC Inside 미국정치 갤러리                            │
│ 제목: "중국인 무비자로 조선족 무더기 입국ㄷㄷ"                │
│                                                               │
│ ────────────────────────────────────────────────────────      │
│                                                               │
│ 🎯 이 글이 속한 세계관:                                       │
│                                                               │
│ "민주당=친중=안보위협" (강도 0.89)                            │
│                                                               │
│ 이 글의 역할:                                                 │
│ • 내러티브: "친중 정책 추진"의 증거                           │
│ • 주장: "조선족 비호" (이 주장으로 8번째 등장)                │
│                                                               │
│ ────────────────────────────────────────────────────────      │
│                                                               │
│ ⚠️  판정: 왜곡됨                                              │
│                                                               │
│ 이유:                                                         │
│ 1. "조선족 무더기 도주"는 확인되지 않은 소문                  │
│ 2. 무비자 정책은 민주당이 아닌 윤석열 정부 정책              │
│                                                               │
│ ────────────────────────────────────────────────────────      │
│                                                               │
│ 💡 패턴 분석:                                                 │
│                                                               │
│ 이와 유사한 주장이 최근 3개월간 8건 더 발견됨:                │
│ • 2024-12-15: "조선족이 집단으로..."                          │
│ • 2024-12-20: "무비자 틈타 입국..."                           │
│ • ... (8건 모두 보기)                                         │
│                                                               │
│ → 반복적으로 같은 허위 주장이 확산되고 있음                   │
│                                                               │
│ ────────────────────────────────────────────────────────      │
│                                                               │
│ ❌ 반박 자료:                                                 │
│                                                               │
│ 개별 주장 반박:                                               │
│ • SBS 팩트체크: "조선족 집단 도주는 허위" (2025-01-05)       │
│                                                               │
│ 세계관 반박:                                                  │
│ • "친중=위협" 프레임의 구조적 오류 [보기]                     │
│                                                               │
│ 💬 추천 답변:                                                 │
│ "이 주장은 확인되지 않은 소문이며, 무비자 정책은              │
│  실제로 윤석열 정부의 B-2 환승무비자 재개 정책입니다.        │
│  SBS 팩트체크에서 이미 허위로 판정되었습니다."                │
│                                                               │
│ [📋 답변 복사]  [🔗 반박 자료 공유]                          │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 5. 핵심 차별점

### ✅ 1. 큰 그림 보여주기
```
개별 거짓말이 아니라
"전체적으로 어떤 이미지를 만들려고 하는가"
```

### ✅ 2. 형성 과정 추적
```
세계관이 시간에 따라 어떻게 구축되는지
씨앗 → 성장 → 정점 단계별 시각화
```

### ✅ 3. 구조적 반박
```
개별 사실 반박이 아닌
프레임 자체의 논리적 오류 지적
```

### ✅ 4. 강도 측정
```
얼마나 강하게 구축되었는가
다양성, 지속성, 빈도, 연결성 종합 평가
```

### ✅ 5. 사용자 행동 지원
```
복사 가능한 반박 답변 제공
팩트체크 자료 링크
전체 맥락 이해 지원
```

---

## 6. 구현 우선순위

### Phase 1: 핵심 엔진
1. ✅ 데이터베이스 스키마
2. WorldviewExtractor (세계관 추출)
3. 기본 크롤러 (DC갤)
4. Claim 매칭 로직

### Phase 2: 시각화
1. 세계관 목록 대시보드
2. 세계관 상세 뷰 (구조 + 형성 과정)
3. URL 입력 분석 기능

### Phase 3: 반박 시스템
1. WorldviewRebuttalGenerator
2. 팩트체크 자동 수집
3. 사용자 제출 반박

### Phase 4: 확장
1. 크로스 플랫폼 (유튜브, 인스타)
2. 자동 알림 (새 세계관 감지)
3. 공유 기능

---

## 최종 요약

### 이 시스템이 해결하는 문제:

```
❌ 개별 거짓말 반박 (끝없는 모래주머니)
✅ 왜곡된 세계관 구조 폭로 (댐 무너뜨리기)
```

### 사용자가 얻는 것:

```
1. 인식: "아, 이들이 이런 이미지를 만들려고 하는구나"
2. 이해: "이렇게 시간에 걸쳐 구축되는구나"
3. 대응: "전체 논리가 이렇게 허점이 있구나"
4. 무기: 복사 가능한 반박 답변 + 증거 자료
```

이제 이 설계로 구현을 시작할까요?