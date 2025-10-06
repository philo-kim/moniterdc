# 세계관 해체 엔진 - 완전한 시스템 아키텍처

## 0. 시스템 목적 재확인

```
최종 목표:
왜곡된 인식이 어떻게 만들어지고 확산되는지 그 메커니즘을 폭로하여
사람들이 스스로 깨닫게 만드는 시스템

측정 지표:
- 사용자가 "아, 이렇게 조작하는구나" 깨닫는 순간
- 패턴을 스스로 인식하게 되는 학습 효과
- 다른 사람들에게 알리고 싶어하는 확산 욕구
```

---

## 1. 데이터 구조 - 3 Layer Architecture

### Layer 구분 철학

```
Layer 1 (Reality):
  - 물리적으로 존재하는 것
  - 콘텐츠, URL, 텍스트, 시간
  - 불변 (Immutable)

Layer 2 (Perception):
  - 콘텐츠가 만들어내는 효과
  - 주장, 인상, 감정
  - 추론 (Inferred)

Layer 3 (Worldview):
  - 인식들이 누적된 결과
  - 프레임, 메커니즘, 구조
  - 패턴 (Pattern)
```

### 1.1 Layer 1: Reality

```sql
-- 핵심 테이블: contents
-- 목적: 모든 소스의 원본 콘텐츠를 소스 독립적으로 저장
CREATE TABLE contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 소스 정보
    source_type TEXT NOT NULL,
    -- dc_gallery, youtube, article, instagram, namuwiki, twitter, etc

    source_url TEXT NOT NULL UNIQUE,
    source_id TEXT,  -- 소스별 고유 ID (DC갤 post_num, 유튜브 video_id 등)

    -- 콘텐츠
    title TEXT,
    body TEXT NOT NULL,

    -- 소스별 메타데이터 (JSONB로 유연하게)
    metadata JSONB,
    /*
    DC갤: {"gallery": "uspolitics", "post_num": 123, "view_count": 1000}
    유튜브: {"channel_id": "...", "video_id": "...", "view_count": 5000, "like_count": 100}
    기사: {"publisher": "SBS", "author": "홍길동", "category": "politics"}
    */

    -- 신뢰도 (소스 타입에 따라 기본값)
    base_credibility FLOAT,
    -- dc_gallery: 0.2, youtube: 0.3-0.6, article: 0.5-0.9, factcheck: 0.9

    -- 시간
    published_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ DEFAULT NOW(),

    -- 상태
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_contents_source_type ON contents(source_type);
CREATE INDEX idx_contents_published ON contents(published_at DESC);
CREATE INDEX idx_contents_url ON contents(source_url);
```

### 1.2 Layer 2: Perception

```sql
-- 핵심 테이블: perceptions
-- 목적: 콘텐츠가 만들어내는 "인상/주장"을 추출
CREATE TABLE perceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL REFERENCES contents(id) ON DELETE CASCADE,

    -- 이 콘텐츠가 만드는 인식
    perceived_subject TEXT NOT NULL,
    -- "민주당", "이재명", "윤석열", "중국", "미국" 등

    perceived_attribute TEXT NOT NULL,
    -- "친중", "부패", "무능", "국가수호자" 등

    perceived_valence TEXT NOT NULL,
    -- positive, negative, neutral

    -- 추출된 주장들
    claims TEXT[],
    -- ["민주당이 중국인 무비자를 허용했다", "조선족이 집단 도주했다"]

    -- 키워드
    keywords TEXT[],

    -- 감정 (emotional loading)
    emotions TEXT[],
    -- ["fear", "anger", "disgust"] - 사용된 감정 자극

    -- 임베딩 (유사 인식 검색용)
    perception_embedding vector(1536),

    -- 신뢰도 (content의 base_credibility 계승 + 분석 확신도)
    credibility FLOAT,
    confidence FLOAT,  -- GPT 분석 확신도

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_perceptions_content ON perceptions(content_id);
CREATE INDEX idx_perceptions_subject ON perceptions(perceived_subject);
CREATE INDEX idx_perceptions_valence ON perceptions(perceived_valence);
CREATE INDEX idx_perceptions_embedding ON perceptions
USING ivfflat (perception_embedding vector_cosine_ops);

-- 보조 테이블: perception_connections
-- 목적: 인식들 간의 연결 (시간적, 인과적, 주제적)
CREATE TABLE perception_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    from_perception_id UUID NOT NULL REFERENCES perceptions(id) ON DELETE CASCADE,
    to_perception_id UUID NOT NULL REFERENCES perceptions(id) ON DELETE CASCADE,

    connection_type TEXT NOT NULL,
    -- temporal: 시간적 순서 (A 다음 B)
    -- causal: 인과관계 (A 때문에 B)
    -- thematic: 주제적 유사 (A와 B는 같은 주제)
    -- supporting: 지지관계 (A가 B를 뒷받침)

    strength FLOAT DEFAULT 0.5,  -- 0-1

    -- 자동 감지 vs 수동 설정
    detected_by TEXT DEFAULT 'auto',  -- auto, manual

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(from_perception_id, to_perception_id, connection_type)
);

CREATE INDEX idx_perception_connections_from ON perception_connections(from_perception_id);
CREATE INDEX idx_perception_connections_to ON perception_connections(to_perception_id);
```

### 1.3 Layer 3: Worldview

```sql
-- 핵심 테이블: worldviews
-- 목적: 인식들이 누적되어 만들어낸 전체적 프레임
CREATE TABLE worldviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 세계관 정의
    title TEXT NOT NULL,  -- "민주당=친중=안보위협"
    frame TEXT NOT NULL,  -- "대상=속성=결과" 구조

    description TEXT,  -- 상세 설명

    -- 핵심 요소
    core_subject TEXT NOT NULL,  -- "민주당"
    core_attributes TEXT[] NOT NULL,  -- ["친중", "무능"]
    overall_valence TEXT NOT NULL,  -- positive, negative

    -- 구성 인식들
    perception_ids UUID[] NOT NULL,  -- 이 세계관을 구성하는 인식들

    -- 강도 측정 (다차원)
    strength_cognitive FLOAT,      -- 0-1, 인지적 강도
    strength_temporal FLOAT,       -- 0-1, 시간적 지속성
    strength_social FLOAT,         -- 0-1, 사회적 확산
    strength_structural FLOAT,     -- 0-1, 구조적 체계성
    strength_overall FLOAT,        -- 0-1, 종합 강도

    -- 형성 메커니즘
    formation_phases JSONB,
    /*
    [
      {
        "phase": "seed",
        "date": "2024-11-15",
        "description": "초기 주장 제시",
        "perception_count": 5,
        "key_claims": ["무비자 허용"]
      },
      {
        "phase": "growth",
        "date_start": "2024-12-01",
        "date_end": "2024-12-31",
        "tactics": ["repetition", "variation"],
        "perception_count": 19,
        "key_additions": ["조선족 도주", "중국 로비"]
      },
      {
        "phase": "peak",
        "date": "2025-01-15",
        "description": "크로스 플랫폼 확산",
        "perception_count": 65,
        "platforms": ["dc_gallery", "youtube", "instagram"]
      }
    ]
    */

    -- 심리적 메커니즘 (어떻게 작동하는가)
    cognitive_mechanisms JSONB,
    /*
    [
      {
        "type": "confirmation_bias",
        "description": "기존 편견 강화",
        "vulnerability": "사람들은 자신의 믿음을 확인하는 정보 선호"
      },
      {
        "type": "availability_heuristic",
        "description": "반복을 통한 중요성 부각",
        "vulnerability": "자주 본 정보를 더 중요하게 인식"
      },
      {
        "type": "emotional_loading",
        "emotions": ["fear", "anger"],
        "description": "공포/분노를 자극해 이성적 판단 방해"
      }
    ]
    */

    -- 구조적 허점
    structural_flaws JSONB,
    /*
    [
      {
        "type": "term_ambiguity",
        "term": "친중",
        "issue": "경제협력과 안보양보를 구분하지 않음",
        "examples": ["무비자=친중?", "교역=친중?"]
      },
      {
        "type": "logical_leap",
        "from": "친중",
        "to": "위험",
        "issue": "협력이 곧 위협이라는 논리 비약"
      },
      {
        "type": "selective_facts",
        "hidden": ["무비자는 윤석열 정부 정책"],
        "exaggerated": ["조선족 도주는 미확인 소문"]
      }
    ]
    */

    -- 해체 전략
    deconstruction JSONB,
    /*
    {
      "counter_narrative": "경제협력 ≠ 안보위협. 모든 정부가...",
      "key_rebuttals": [
        "용어 조작: 친중 정의 모호",
        "논리 비약: 협력≠위협",
        "선별적 사실: 실제는 윤석열 정부 정책"
      ],
      "suggested_response": "복사 가능한 답변 텍스트",
      "evidence_urls": ["SBS 팩트체크 URL", "나무위키 URL"]
    }
    */

    -- 통계
    total_perceptions INTEGER DEFAULT 0,
    total_contents INTEGER DEFAULT 0,
    source_diversity INTEGER DEFAULT 0,  -- 몇 개 플랫폼에 걸쳐있는가

    -- 시간
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,
    peak_date TIMESTAMPTZ,

    -- 추세
    trend TEXT,  -- rising, stable, falling, dead

    -- 임베딩 (유사 세계관 검색)
    worldview_embedding vector(1536),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_worldviews_subject ON worldviews(core_subject);
CREATE INDEX idx_worldviews_strength ON worldviews(strength_overall DESC);
CREATE INDEX idx_worldviews_trend ON worldviews(trend);
CREATE INDEX idx_worldviews_embedding ON worldviews
USING ivfflat (worldview_embedding vector_cosine_ops);
```

### 1.4 보조 테이블들

```sql
-- 반박 자료 (Claim-level)
CREATE TABLE rebuttals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 반박 대상
    target_type TEXT NOT NULL,  -- perception, worldview
    target_id UUID NOT NULL,

    -- 반박 내용
    title TEXT NOT NULL,
    content TEXT NOT NULL,

    -- 소스
    rebuttal_type TEXT NOT NULL,  -- factcheck, official, user_submitted
    source_url TEXT,

    -- 품질
    credibility FLOAT,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_rebuttals_target ON rebuttals(target_type, target_id);

-- 사용자 제출 반박에 대한 투표
CREATE TABLE rebuttal_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rebuttal_id UUID REFERENCES rebuttals(id) ON DELETE CASCADE,
    user_id TEXT,  -- 세션 ID 또는 사용자 ID
    vote INTEGER,  -- 1 (upvote) or -1 (downvote)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(rebuttal_id, user_id)
);
```

---

## 2. 데이터 흐름 (Data Flow)

### 2.1 수집 → 분석 → 패턴 감지

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: 외부 콘텐츠                                           │
│ (DC갤, 유튜브, 기사, 인스타 등)                              │
└─────────────────────────────────────────────────────────────┘
                          ↓

┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: Content Collection                                 │
│                                                             │
│ [Adapter] → fetch → parse → save to contents               │
│                                                             │
│ Result: 1 row in contents table                            │
└─────────────────────────────────────────────────────────────┘
                          ↓

┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: Perception Extraction                              │
│                                                             │
│ [GPT Analysis]                                              │
│   Input: content.title + content.body                       │
│   Output: {                                                 │
│     perceived_subject: "민주당",                            │
│     perceived_attribute: "친중",                            │
│     perceived_valence: "negative",                          │
│     claims: [...],                                          │
│     emotions: ["fear"]                                      │
│   }                                                         │
│                                                             │
│ [Embedding Generation]                                      │
│   perception_embedding = embed(subject + attribute)         │
│                                                             │
│ Result: 1+ rows in perceptions table                       │
└─────────────────────────────────────────────────────────────┘
                          ↓

┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: Connection Detection                               │
│                                                             │
│ [Find Related Perceptions]                                  │
│   - Same subject perceptions (temporal connection)          │
│   - Similar embedding (thematic connection)                 │
│   - Causal keywords detection (causal connection)           │
│                                                             │
│ Result: N rows in perception_connections                    │
└─────────────────────────────────────────────────────────────┘
                          ↓

┌─────────────────────────────────────────────────────────────┐
│ STAGE 4: Worldview Detection (주기적 실행)                  │
│                                                             │
│ [Clustering Algorithm]                                      │
│   Input: Recent perceptions (30-90 days)                   │
│   Process:                                                  │
│     1. Group by subject                                     │
│     2. Check valence consistency (>70%)                     │
│     3. Check temporal persistence (>30 days)                │
│     4. Check frequency (>10 perceptions)                    │
│                                                             │
│ [Mechanism Analysis]                                        │
│   - Cognitive mechanisms detection                          │
│   - Temporal pattern analysis                               │
│   - Structural analysis                                     │
│                                                             │
│ [Deconstruction Generation]                                 │
│   - Find structural flaws                                   │
│   - Generate counter narrative                              │
│                                                             │
│ Result: 1 row in worldviews table                          │
└─────────────────────────────────────────────────────────────┘
                          ↓

┌─────────────────────────────────────────────────────────────┐
│ OUTPUT: 사용자에게 표시                                      │
│ - 세계관 지도                                                │
│ - 해체 분석                                                  │
│ - 행동 가이드                                                │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 사용자 URL 입력 흐름

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: 사용자가 URL 입력 (DC갤 글)                          │
└─────────────────────────────────────────────────────────────┘
                          ↓

┌─────────────────────────────────────────────────────────────┐
│ 1. Check if already exists                                  │
│    SELECT * FROM contents WHERE source_url = ?              │
│                                                             │
│    EXISTS → Skip to step 3                                  │
│    NOT EXISTS → Collect content (step 2)                    │
└─────────────────────────────────────────────────────────────┘
                          ↓

┌─────────────────────────────────────────────────────────────┐
│ 2. Collect & Analyze (same as normal collection)            │
│    → contents → perceptions → connections                   │
└─────────────────────────────────────────────────────────────┘
                          ↓

┌─────────────────────────────────────────────────────────────┐
│ 3. Find Related Worldview                                   │
│                                                             │
│    Get perceptions for this content                         │
│    For each perception:                                     │
│      Check which worldview it belongs to                    │
│      (worldviews.perception_ids @> ARRAY[perception.id])    │
└─────────────────────────────────────────────────────────────┘
                          ↓

┌─────────────────────────────────────────────────────────────┐
│ 4. Display Results                                          │
│                                                             │
│    ✅ Content Analysis                                      │
│    - Extracted perceptions                                  │
│    - Detected claims                                        │
│                                                             │
│    🎯 Related Worldview                                     │
│    - Which worldview this contributes to                    │
│    - Role in the narrative                                  │
│                                                             │
│    ❌ Rebuttals                                             │
│    - Perception-level rebuttals                             │
│    - Worldview-level deconstruction                         │
│                                                             │
│    💡 Action Guide                                          │
│    - Suggested response                                     │
│    - Evidence links                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 엔진 인터페이스 설계

### 3.1 Content Collector (통합 수집 엔진)

```python
class ContentCollector:
    """
    모든 소스로부터 콘텐츠 수집
    """

    def __init__(self):
        self.adapters = {
            'dc_gallery': DCGalleryAdapter(),
            'youtube': YouTubeAdapter(),
            'article': ArticleAdapter(),
            'instagram': InstagramAdapter(),
            'namuwiki': NamuwikiAdapter()
        }

    async def collect(
        self,
        source_type: str,
        **params
    ) -> List[UUID]:
        """
        소스로부터 콘텐츠 수집하여 contents 테이블에 저장

        Returns:
            List[UUID]: 저장된 content_id들
        """
        adapter = self.adapters[source_type]

        # 1. Fetch
        raw_contents = await adapter.fetch(**params)

        content_ids = []
        for raw in raw_contents:
            # 2. Parse
            parsed = adapter.parse(raw)

            # 3. Check duplicate
            if await self.exists(parsed.url):
                continue

            # 4. Save
            content_id = await self.save_content(
                source_type=source_type,
                url=parsed.url,
                title=parsed.title,
                body=parsed.body,
                metadata=parsed.metadata,
                published_at=parsed.published_at,
                base_credibility=adapter.get_credibility()
            )

            content_ids.append(content_id)

        return content_ids

    async def save_content(self, **kwargs) -> UUID:
        """contents 테이블에 저장"""
        result = await db.table('contents').insert(kwargs).execute()
        return result.data[0]['id']
```

### 3.2 Perception Extractor (인식 추출 엔진)

```python
class PerceptionExtractor:
    """
    콘텐츠로부터 인식(perception) 추출
    """

    async def extract(self, content_id: UUID) -> List[UUID]:
        """
        콘텐츠 분석 → 인식 추출

        Returns:
            List[UUID]: 추출된 perception_id들
        """
        # 1. Get content
        content = await db.table('contents').select('*').eq('id', content_id).single()

        # 2. GPT 분석
        analysis = await self.analyze_with_gpt(content)

        # 3. 각 인식별로 저장
        perception_ids = []
        for perception_data in analysis['perceptions']:
            # 임베딩 생성
            embedding = await self.generate_embedding(
                f"{perception_data['subject']} {perception_data['attribute']}"
            )

            # 저장
            perception_id = await self.save_perception(
                content_id=content_id,
                perceived_subject=perception_data['subject'],
                perceived_attribute=perception_data['attribute'],
                perceived_valence=perception_data['valence'],
                claims=perception_data['claims'],
                keywords=perception_data['keywords'],
                emotions=perception_data.get('emotions', []),
                perception_embedding=embedding,
                credibility=content.data['base_credibility'],
                confidence=perception_data['confidence']
            )

            perception_ids.append(perception_id)

        return perception_ids

    async def analyze_with_gpt(self, content: Dict) -> Dict:
        """
        GPT로 콘텐츠 분석

        Returns:
            {
                "perceptions": [
                    {
                        "subject": "민주당",
                        "attribute": "친중",
                        "valence": "negative",
                        "claims": [...],
                        "keywords": [...],
                        "emotions": ["fear"],
                        "confidence": 0.9
                    }
                ]
            }
        """
        response = await openai.chat.completions.create(
            model="gpt-5-mini",
            messages=[{
                "role": "system",
                "content": PERCEPTION_EXTRACTION_PROMPT
            }, {
                "role": "user",
                "content": f"제목: {content['title']}\n\n본문: {content['body']}"
            }]
        )

        return parse_json(response)
```

### 3.3 Connection Detector (연결 감지 엔진)

```python
class ConnectionDetector:
    """
    인식들 간의 연결 감지
    """

    async def detect_connections(self, perception_id: UUID):
        """
        새 인식과 기존 인식들 간의 연결 감지
        """
        perception = await self.get_perception(perception_id)

        # 1. Temporal connections (같은 주제의 최근 인식들)
        await self.detect_temporal(perception)

        # 2. Thematic connections (벡터 유사도)
        await self.detect_thematic(perception)

        # 3. Causal connections (인과 관계 키워드)
        await self.detect_causal(perception)

    async def detect_temporal(self, perception: Dict):
        """
        시간적 연결: 같은 주제의 최근 인식들과 연결
        """
        # 같은 subject의 최근 30일 인식들
        recent = await db.table('perceptions')\
            .select('id')\
            .eq('perceived_subject', perception['perceived_subject'])\
            .gte('created_at', 'NOW() - INTERVAL 30 days')\
            .neq('id', perception['id'])\
            .execute()

        for other in recent.data:
            await self.save_connection(
                from_perception_id=other['id'],
                to_perception_id=perception['id'],
                connection_type='temporal',
                strength=0.5
            )

    async def detect_thematic(self, perception: Dict):
        """
        주제적 연결: 벡터 유사도 기반
        """
        # 유사한 임베딩의 인식들 검색
        similar = await db.rpc('search_similar_perceptions', {
            'query_embedding': perception['perception_embedding'],
            'similarity_threshold': 0.8,
            'limit': 10
        }).execute()

        for other in similar.data:
            if other['id'] == perception['id']:
                continue

            await self.save_connection(
                from_perception_id=other['id'],
                to_perception_id=perception['id'],
                connection_type='thematic',
                strength=other['similarity']
            )

    async def detect_causal(self, perception: Dict):
        """
        인과적 연결: "때문에", "따라서" 등의 키워드
        """
        # 이 인식의 claims에서 인과 관계 키워드 검색
        causal_keywords = ['때문에', '따라서', '그래서', '결과', '원인']

        for claim in perception['claims']:
            if any(keyword in claim for keyword in causal_keywords):
                # GPT로 인과관계 확인
                related = await self.find_causal_related(perception, claim)

                for other_id in related:
                    await self.save_connection(
                        from_perception_id=other_id,
                        to_perception_id=perception['id'],
                        connection_type='causal',
                        strength=0.7
                    )
```

### 3.4 Worldview Detector (세계관 감지 엔진)

```python
class WorldviewDetector:
    """
    인식들로부터 세계관 패턴 감지
    """

    async def detect_worldviews(self, time_window_days: int = 90):
        """
        주기적 실행: 최근 N일간의 인식들에서 세계관 패턴 감지
        """
        # 1. 최근 인식들 가져오기
        perceptions = await db.table('perceptions')\
            .select('*')\
            .gte('created_at', f'NOW() - INTERVAL {time_window_days} days')\
            .execute()

        # 2. 주체별로 그룹핑
        grouped = self.group_by_subject(perceptions.data)

        for subject, perception_list in grouped.items():
            # 3. 세계관 후보 검증
            if await self.is_worldview_candidate(perception_list):
                # 4. 기존 세계관 확인
                existing = await self.find_existing_worldview(subject)

                if existing:
                    # 업데이트
                    await self.update_worldview(existing['id'], perception_list)
                else:
                    # 새로 생성
                    await self.create_worldview(subject, perception_list)

    async def is_worldview_candidate(self, perceptions: List[Dict]) -> bool:
        """
        세계관 후보 조건 검증
        """
        # 조건 1: 빈도 (최소 10개 이상)
        if len(perceptions) < 10:
            return False

        # 조건 2: 방향성 일관성 (70% 이상 같은 valence)
        valences = [p['perceived_valence'] for p in perceptions]
        dominant_valence = max(set(valences), key=valences.count)
        consistency = valences.count(dominant_valence) / len(valences)

        if consistency < 0.7:
            return False

        # 조건 3: 시간적 지속성 (30일 이상)
        timestamps = [p['created_at'] for p in perceptions]
        time_span = (max(timestamps) - min(timestamps)).days

        if time_span < 30:
            return False

        return True

    async def create_worldview(
        self,
        subject: str,
        perceptions: List[Dict]
    ) -> UUID:
        """
        새 세계관 생성
        """
        # 1. 속성 집계
        attributes = self.aggregate_attributes(perceptions)

        # 2. 프레임 생성
        frame = await self.generate_frame(subject, attributes, perceptions)

        # 3. 메커니즘 분석
        mechanisms = await self.analyze_mechanisms(perceptions)

        # 4. 강도 계산
        strength = self.calculate_strength(perceptions, mechanisms)

        # 5. 해체 전략 생성
        deconstruction = await self.generate_deconstruction(
            frame, perceptions, mechanisms
        )

        # 6. 저장
        worldview_id = await db.table('worldviews').insert({
            'title': frame['title'],
            'frame': frame['frame'],
            'core_subject': subject,
            'core_attributes': attributes,
            'overall_valence': self.get_dominant_valence(perceptions),
            'perception_ids': [p['id'] for p in perceptions],
            'strength_cognitive': strength['cognitive'],
            'strength_temporal': strength['temporal'],
            'strength_social': strength['social'],
            'strength_structural': strength['structural'],
            'strength_overall': strength['overall'],
            'formation_phases': mechanisms['temporal']['phases'],
            'cognitive_mechanisms': mechanisms['cognitive'],
            'structural_flaws': deconstruction['structural_flaws'],
            'deconstruction': deconstruction,
            'total_perceptions': len(perceptions),
            # ... 기타 필드
        }).execute()

        return worldview_id.data[0]['id']
```

### 3.5 Mechanism Analyzer (메커니즘 분석 엔진)

```python
class MechanismAnalyzer:
    """
    세계관의 작동 메커니즘 분석
    """

    async def analyze(self, perceptions: List[Dict]) -> Dict:
        """
        인식들의 작동 메커니즘 분석

        Returns:
            {
                "cognitive": [...],    # 인지적 메커니즘
                "temporal": {...},     # 시간적 패턴
                "social": {...},       # 사회적 확산
                "structural": {...}    # 구조적 특징
            }
        """
        return {
            'cognitive': self.analyze_cognitive(perceptions),
            'temporal': self.analyze_temporal(perceptions),
            'social': self.analyze_social(perceptions),
            'structural': self.analyze_structural(perceptions)
        }

    def analyze_cognitive(self, perceptions: List[Dict]) -> List[Dict]:
        """
        어떤 심리적 기제를 이용하는가
        """
        mechanisms = []

        # 확증편향
        if self.uses_confirmation_bias(perceptions):
            mechanisms.append({
                'type': 'confirmation_bias',
                'description': '기존 편견을 강화하는 정보만 제시',
                'vulnerability': '사람들은 자신의 믿음을 확인하는 정보 선호'
            })

        # 가용성 휴리스틱
        if self.uses_availability_heuristic(perceptions):
            mechanisms.append({
                'type': 'availability_heuristic',
                'description': '반복을 통해 쉽게 떠오르게 만듦',
                'vulnerability': '자주 본 정보를 더 중요하게 인식'
            })

        # 감정 로딩
        all_emotions = []
        for p in perceptions:
            all_emotions.extend(p.get('emotions', []))

        if all_emotions:
            mechanisms.append({
                'type': 'emotional_loading',
                'emotions': list(set(all_emotions)),
                'description': '강한 감정 유발로 이성적 판단 방해'
            })

        return mechanisms

    def analyze_temporal(self, perceptions: List[Dict]) -> Dict:
        """
        시간에 따른 발전 패턴
        """
        timeline = sorted(perceptions, key=lambda p: p['created_at'])

        # 단계 구분
        phases = []

        # Seed phase (처음 5개)
        seed = timeline[:5]
        phases.append({
            'phase': 'seed',
            'date': seed[0]['created_at'],
            'perception_count': len(seed),
            'key_claims': self.extract_key_claims(seed)
        })

        # Growth phase (증가 구간)
        # Peak phase (최대 빈도)
        # Maintenance phase (유지)

        # ... 구현

        return {
            'phases': phases,
            'duration_days': (timeline[-1]['created_at'] - timeline[0]['created_at']).days
        }
```

### 3.6 Deconstruction Generator (해체 전략 생성 엔진)

```python
class DeconstructionGenerator:
    """
    세계관 해체 전략 생성
    """

    async def generate(
        self,
        frame: str,
        perceptions: List[Dict],
        mechanisms: Dict
    ) -> Dict:
        """
        세계관 해체 전략 생성

        Returns:
            {
                "structural_flaws": [...],
                "counter_narrative": "...",
                "key_rebuttals": [...],
                "suggested_response": "...",
                "evidence_urls": [...]
            }
        """
        # 1. 구조적 허점 찾기
        structural_flaws = self.find_structural_flaws(frame, perceptions)

        # 2. 팩트체크
        factual_errors = await self.factcheck(perceptions)

        # 3. 대안 내러티브 생성
        counter_narrative = await self.generate_counter_narrative(
            frame, structural_flaws, factual_errors
        )

        # 4. 핵심 반박 포인트
        key_rebuttals = self.extract_key_rebuttals(
            structural_flaws, factual_errors
        )

        # 5. 추천 답변 생성
        suggested_response = await self.generate_suggested_response(
            counter_narrative, key_rebuttals
        )

        # 6. 증거 자료 수집
        evidence_urls = await self.collect_evidence(perceptions)

        return {
            'structural_flaws': structural_flaws,
            'counter_narrative': counter_narrative,
            'key_rebuttals': key_rebuttals,
            'suggested_response': suggested_response,
            'evidence_urls': evidence_urls
        }
```

---

## 4. 기존 시스템과의 통합

### 4.1 현재 시스템 상태

```
현재:
- logic_repository 테이블 (228개 논리)
- 일부만 political_frame 있음
- dashboard 존재

문제:
- 구조가 프레임 기반 (문자열 매칭)
- 세계관 개념 없음
- 메커니즘 분석 없음
```

### 4.2 Migration 전략

```
Phase 1: 새 테이블 생성 (병행 운영)
- contents, perceptions, worldviews 생성
- 기존 logic_repository 유지

Phase 2: 데이터 마이그레이션
- logic_repository → contents
- 기존 논리들을 perception으로 재분석
- 세계관 자동 감지

Phase 3: 대시보드 전환
- 새 worldview-centric 대시보드
- 기존 대시보드 유지 (비교용)

Phase 4: 완전 전환
- 기존 테이블 deprecate
- 새 시스템만 운영
```

### 4.3 Migration Script 구조

```python
async def migrate_existing_data():
    """
    기존 logic_repository → 새 시스템
    """
    # 1. logic_repository 데이터 가져오기
    logics = await supabase.table('logic_repository').select('*').execute()

    for logic in logics.data:
        # 2. content로 변환
        content_id = await save_as_content(logic)

        # 3. perception으로 재분석
        perception_ids = await extract_perceptions(content_id)

        # 4. connection 감지
        for p_id in perception_ids:
            await detect_connections(p_id)

    # 5. 세계관 감지
    await detect_worldviews()
```

---

## 5. 구현 우선순위

### Phase 1: 핵심 인프라 (Week 1-2)
```
✅ 데이터베이스 스키마
  - contents, perceptions, worldviews 테이블
  - 인덱스, 제약조건

✅ 기본 엔진
  - ContentCollector (DC갤만)
  - PerceptionExtractor
  - 기본 GPT 프롬프트

✅ 테스트
  - 10개 DC갤 글로 테스트
  - perception 추출 검증
```

### Phase 2: 패턴 감지 (Week 3-4)
```
✅ 고급 엔진
  - ConnectionDetector
  - WorldviewDetector
  - MechanismAnalyzer

✅ 테스트
  - 기존 228개 논리로 테스트
  - 세계관 자동 감지 검증
```

### Phase 3: 해체 & UI (Week 5-6)
```
✅ 해체 엔진
  - DeconstructionGenerator
  - 반박 자료 수집

✅ 대시보드
  - 세계관 지도 뷰
  - 해체 분석 뷰
  - URL 입력 분석
```

### Phase 4: 확장 (Week 7-8)
```
✅ 다중 소스
  - 유튜브, 기사, 인스타 어댑터
  - 크로스 플랫폼 추적

✅ 고급 기능
  - 자동 알림
  - 공유 기능
  - 사용자 제출 반박
```

---

## 6. 성공 지표

### 기술적 지표
```
- 세계관 감지 정확도 >80%
- 메커니즘 분석 완성도 >85%
- 해체 전략 품질 >90%
```

### 사용자 지표
```
- "깨달음" 피드백 수집
- 공유 빈도
- 재방문율
```

### 최종 목표
```
사용자가:
1. 패턴을 인식하게 됨
2. 메커니즘을 이해하게 됨
3. 스스로 반박하게 됨
4. 다른 사람들에게 알리게 됨
```

---

이 아키텍처로 시작해도 될까요?