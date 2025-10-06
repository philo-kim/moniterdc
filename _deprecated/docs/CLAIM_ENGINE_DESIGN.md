# Claim-Based Worldview Engine 설계

## 핵심 철학

**세계관 엔진은 소스에 독립적이어야 한다**
- DC갤러리 글이든, 기사든, 유튜브든, 나무위키든
- 모두 같은 구조로 분석되고
- 같은 주장(Claim)에 연결되며
- 반박 자료도 같은 방식으로 관리됨

## 아키텍처 개요

```
┌─────────────────────────────────────────────────────────┐
│                    Worldview Engine                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Narratives (내러티브 계층)                                │
│      ↓                                                    │
│  Claims (검증 가능한 주장)                                 │
│      ↓                                                    │
│  Evidence (증거 - 모든 소스)                               │
│                                                           │
└─────────────────────────────────────────────────────────┘

┌──────────────────── Sources ────────────────────────┐
│  DC갤  │  기사  │  유튜브  │  나무위키  │  인스타  │
└─────────────────────────────────────────────────────┘
         ↓         ↓         ↓          ↓         ↓
    ┌────────────────────────────────────────────────┐
    │         All flow into Evidence table           │
    └────────────────────────────────────────────────┘
```

---

## 1. 핵심 데이터 구조

### 1.1 Claim (주장) - 최소 분석 단위

**정의:** 검증 가능한 명제

```sql
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 주장 내용
    statement TEXT NOT NULL,  -- "민주당이 중국인 무비자 입국을 허용했다"
    claim_type TEXT NOT NULL, -- factual, evaluative, predictive, causal

    -- 분류
    subjects TEXT[] NOT NULL,  -- ["민주당", "중국"]
    keywords TEXT[] NOT NULL,  -- ["무비자", "입국", "중국인"]

    -- 계층 구조
    parent_narrative_id UUID REFERENCES narratives(id),

    -- 임베딩 (유사 주장 검색)
    embedding vector(1536),

    -- 통계
    mention_count INTEGER DEFAULT 0,
    support_evidence_count INTEGER DEFAULT 0,
    refute_evidence_count INTEGER DEFAULT 0,
    credibility_score FLOAT,  -- 0-1, 얼마나 신뢰할 수 있는 주장인가

    -- 시간
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),

    -- 메타
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_claims_embedding ON claims
USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX idx_claims_subjects ON claims USING GIN(subjects);
CREATE INDEX idx_claims_parent_narrative ON claims(parent_narrative_id);
```

**Claim Types:**
- `factual`: 사실 주장 ("민주당이 무비자 허용")
- `evaluative`: 평가 주장 ("민주당은 무능하다")
- `predictive`: 예측 주장 ("민주당이 집권하면 경제 붕괴")
- `causal`: 인과 주장 ("무비자 때문에 조선족이 도주했다")

### 1.2 Evidence (증거) - 소스 독립적

**정의:** Claim을 지지하거나 반박하는 콘텐츠

```sql
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,

    -- 소스 정보 (모든 타입 지원)
    source_type TEXT NOT NULL,  -- dc_gallery, article, youtube, namuwiki, instagram, twitter, etc
    source_url TEXT NOT NULL,
    source_title TEXT,
    source_content TEXT,  -- 전체 내용

    -- 분석 결과
    stance TEXT NOT NULL,  -- support, refute, neutral
    confidence FLOAT,  -- 0-1, GPT의 분석 확신도

    -- 신뢰도
    credibility_score FLOAT,  -- 0-1, 소스의 신뢰도
    credibility_factors JSONB,  -- 신뢰도 계산 요소들

    -- 메타데이터 (소스별로 다름)
    metadata JSONB,  -- {
                     --   "dc": {"gallery": "uspolitics", "post_num": 123},
                     --   "youtube": {"channel": "...", "views": 1000},
                     --   "article": {"publisher": "...", "author": "..."}
                     -- }

    -- 임베딩
    embedding vector(1536),

    -- 시간
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_evidence_claim ON evidence(claim_id);
CREATE INDEX idx_evidence_source_type ON evidence(source_type);
CREATE INDEX idx_evidence_stance ON evidence(stance);
CREATE INDEX idx_evidence_embedding ON evidence
USING ivfflat (embedding vector_cosine_ops);
```

### 1.3 Narrative (내러티브) - 계층 구조

**정의:** Claims의 논리적 그룹, 큰 이야기

```sql
CREATE TABLE narratives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 내러티브 내용
    title TEXT NOT NULL,  -- "민주당=친중=안보위협"
    description TEXT,  -- 상세 설명

    -- 계층 구조
    level INTEGER NOT NULL,  -- 1=최상위, 2=중간, 3=세부
    parent_narrative_id UUID REFERENCES narratives(id),

    -- 주체
    primary_subjects TEXT[] NOT NULL,  -- ["민주당", "중국"]

    -- 임베딩
    embedding vector(1536),

    -- 통계
    total_claims INTEGER DEFAULT 0,
    total_evidence INTEGER DEFAULT 0,
    support_ratio FLOAT,  -- 지지 증거 비율

    -- 강도 (시간에 따라 변화)
    strength_score FLOAT,  -- 0-1, 얼마나 강하게 주장되는가
    trend TEXT,  -- rising, stable, falling

    -- 시간
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),

    -- 메타
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_narratives_parent ON narratives(parent_narrative_id);
CREATE INDEX idx_narratives_subjects ON narratives USING GIN(primary_subjects);
CREATE INDEX idx_narratives_level ON narratives(level);
```

**계층 구조 예시:**
```
Level 1: "민주당=국가위협" (메타 내러티브)
  │
  ├─ Level 2: "민주당=친중=안보위협"
  │   ├─ Claim: "민주당이 중국인 무비자 허용"
  │   ├─ Claim: "중국인 무비자로 조선족 도주"
  │   └─ Claim: "민주당이 간첩 의혹 무시"
  │
  └─ Level 2: "민주당=부패=사법리스크"
      ├─ Claim: "이재명 대장동 연루"
      └─ Claim: "이재명 위증교사"
```

---

## 2. 분석 파이프라인

### 2.1 콘텐츠 수집 (Source Adapters)

각 소스별 어댑터가 있지만, 모두 같은 인터페이스:

```python
class SourceAdapter:
    """모든 소스 어댑터의 기본 클래스"""

    async def fetch_content(self, url: str) -> Content:
        """콘텐츠 가져오기"""
        pass

    async def parse_content(self, raw: str) -> ParsedContent:
        """파싱"""
        pass

    def calculate_credibility(self, source: Source) -> float:
        """소스 신뢰도 계산"""
        pass
```

**구체적 어댑터:**
```python
class DCGalleryAdapter(SourceAdapter):
    source_type = "dc_gallery"

    def calculate_credibility(self, source):
        # DC갤은 낮은 신뢰도
        return 0.2

class NewsArticleAdapter(SourceAdapter):
    source_type = "article"

    def calculate_credibility(self, source):
        # 언론사별 신뢰도
        if source.publisher in ["연합뉴스", "한겨레"]:
            return 0.8
        elif source.publisher in ["조선일보", "중앙일보"]:
            return 0.7
        return 0.5

class YouTubeAdapter(SourceAdapter):
    source_type = "youtube"

    def calculate_credibility(self, source):
        # 채널 구독자, 조회수 등 고려
        if source.subscribers > 100000:
            return 0.6
        return 0.3
```

### 2.2 Claim 추출 (GPT)

```python
async def extract_claims(content: Content) -> List[Claim]:
    """
    콘텐츠에서 주장(Claims) 추출
    """

    response = await openai.chat.completions.create(
        model="gpt-5-mini",
        messages=[{
            "role": "system",
            "content": """당신은 정치 주장 분석 전문가입니다.

콘텐츠를 분석하여 **검증 가능한 주장(Claims)**을 추출하세요.

주장은 다음 기준을 만족해야 합니다:
1. 명확한 명제 (참/거짓 판단 가능)
2. 주체가 명확함
3. 구체적임 (추상적 평가 X)

예시:
✅ "민주당이 2024년 11월 중국인 무비자 입국을 허용했다" (factual)
✅ "중국인 무비자 정책으로 인해 조선족 100명이 도주했다" (causal)
❌ "민주당은 나쁘다" (너무 추상적)
❌ "정치가 엉망이다" (주체 불명확)

JSON 형식으로 반환:
{
  "claims": [
    {
      "statement": "주장 내용",
      "claim_type": "factual/evaluative/predictive/causal",
      "subjects": ["주체1", "주체2"],
      "keywords": ["키워드1", "키워드2"],
      "confidence": 0.9
    }
  ]
}"""
        }, {
            "role": "user",
            "content": f"제목: {content.title}\n\n내용: {content.text}"
        }]
    )

    return parse_claims(response)
```

### 2.3 Claim 매칭 (Vector Similarity)

새로운 주장이 기존 주장과 같은지 판단:

```python
async def find_or_create_claim(new_claim: Dict) -> UUID:
    """
    기존 Claim과 매칭하거나 새로 생성
    """

    # 1. 임베딩 생성
    embedding = await get_embedding(new_claim['statement'])

    # 2. 유사한 기존 Claim 검색
    similar_claims = supabase.rpc('search_similar_claims', {
        'query_embedding': embedding,
        'similarity_threshold': 0.85,
        'limit': 5
    }).execute()

    if similar_claims.data:
        # 가장 유사한 것 선택
        best_match = similar_claims.data[0]

        # GPT로 최종 확인
        is_same = await gpt_verify_claim_match(
            new_claim['statement'],
            best_match['statement']
        )

        if is_same:
            # 기존 Claim 업데이트
            supabase.table('claims').update({
                'mention_count': best_match['mention_count'] + 1,
                'last_seen': 'NOW()'
            }).eq('id', best_match['id']).execute()

            return best_match['id']

    # 3. 새 Claim 생성
    new_claim_record = supabase.table('claims').insert({
        'statement': new_claim['statement'],
        'claim_type': new_claim['claim_type'],
        'subjects': new_claim['subjects'],
        'keywords': new_claim['keywords'],
        'embedding': embedding,
        'mention_count': 1
    }).execute()

    # 4. Narrative 할당
    await assign_to_narrative(new_claim_record.data[0]['id'])

    return new_claim_record.data[0]['id']
```

### 2.4 Evidence 저장

```python
async def save_evidence(
    claim_id: UUID,
    content: Content,
    stance: str,
    confidence: float,
    adapter: SourceAdapter
):
    """
    증거 저장 (모든 소스 통합)
    """

    # 신뢰도 계산
    credibility = adapter.calculate_credibility(content.source)

    # 임베딩
    embedding = await get_embedding(content.text)

    # 저장
    evidence = supabase.table('evidence').insert({
        'claim_id': claim_id,
        'source_type': adapter.source_type,
        'source_url': content.url,
        'source_title': content.title,
        'source_content': content.text,
        'stance': stance,
        'confidence': confidence,
        'credibility_score': credibility,
        'metadata': content.metadata,
        'embedding': embedding,
        'published_at': content.published_at
    }).execute()

    # Claim 통계 업데이트
    await update_claim_stats(claim_id, stance)
```

### 2.5 Narrative 할당

```python
async def assign_to_narrative(claim_id: UUID):
    """
    Claim을 적절한 Narrative에 할당
    """

    claim = supabase.table('claims').select('*').eq('id', claim_id).single().execute()

    # 1. 주체 기반 후보 Narratives
    candidate_narratives = supabase.table('narratives').select('*').contains('primary_subjects', claim.data['subjects']).execute()

    if not candidate_narratives.data:
        # 새 Narrative 생성
        narrative_id = await create_narrative(claim.data)
    else:
        # 2. 임베딩 유사도로 최적 선택
        best_narrative = None
        best_similarity = 0

        for narrative in candidate_narratives.data:
            similarity = cosine_similarity(
                claim.data['embedding'],
                narrative['embedding']
            )
            if similarity > best_similarity:
                best_similarity = similarity
                best_narrative = narrative

        narrative_id = best_narrative['id']

    # Claim에 Narrative 할당
    supabase.table('claims').update({
        'parent_narrative_id': narrative_id
    }).eq('id', claim_id).execute()

    # Narrative 통계 업데이트
    await update_narrative_stats(narrative_id)
```

---

## 3. 크롤러 통합

### 3.1 통합 크롤러 아키텍처

```python
class UnifiedCrawler:
    """모든 소스를 처리하는 통합 크롤러"""

    def __init__(self):
        self.adapters = {
            'dc_gallery': DCGalleryAdapter(),
            'article': NewsArticleAdapter(),
            'youtube': YouTubeAdapter(),
            'namuwiki': NamuwikiAdapter(),
            'instagram': InstagramAdapter()
        }

    async def crawl(self, source_type: str, **params):
        """
        범용 크롤링 함수
        """
        adapter = self.adapters[source_type]

        # 1. 콘텐츠 수집
        contents = await adapter.fetch_contents(**params)

        for content in contents:
            # 2. Claim 추출
            claims = await self.extract_claims(content)

            for claim_data in claims:
                # 3. Claim 매칭/생성
                claim_id = await find_or_create_claim(claim_data)

                # 4. Evidence 저장
                await save_evidence(
                    claim_id=claim_id,
                    content=content,
                    stance='support',  # 기본값, GPT가 판단
                    confidence=claim_data['confidence'],
                    adapter=adapter
                )
```

### 3.2 소스별 실행

```python
# DC갤러리
await crawler.crawl('dc_gallery', gallery='uspolitics', limit=10)

# 기사
await crawler.crawl('article', keyword='민주당', days=7)

# 유튜브
await crawler.crawl('youtube', channel_id='...', max_videos=20)

# 나무위키
await crawler.crawl('namuwiki', page='민주당')

# 인스타그램
await crawler.crawl('instagram', hashtag='정치', limit=50)
```

**모두 같은 Claims/Evidence 테이블로!**

---

## 4. 반박 자료 통합

### 4.1 반박 크롤러

```python
class CounterEvidenceCrawler:
    """반박 자료 전용 크롤러"""

    async def crawl_fact_checks(self, claim_id: UUID):
        """
        팩트체크 사이트에서 반박 자료 수집
        """
        claim = get_claim(claim_id)

        # 팩트체크 사이트들
        sources = [
            'https://factcheck.sbs.co.kr',
            'https://factcheck.afpforum.com',
            'https://www.snopes.com'
        ]

        for source in sources:
            articles = await search_fact_check(source, claim.statement)

            for article in articles:
                # GPT로 관련성 확인
                is_relevant = await gpt_check_relevance(
                    claim.statement,
                    article.content
                )

                if is_relevant:
                    # 반박 증거로 저장
                    await save_evidence(
                        claim_id=claim_id,
                        content=article,
                        stance='refute',  # 반박!
                        confidence=0.9,
                        adapter=NewsArticleAdapter()
                    )
```

### 4.2 사용자 제출 반박

```python
async def submit_counter_evidence(
    claim_id: UUID,
    user_content: str,
    source_url: Optional[str] = None
):
    """
    사용자가 직접 반박 자료 제출
    """

    await save_evidence(
        claim_id=claim_id,
        content=Content(
            text=user_content,
            url=source_url or 'user_submitted',
            source={'type': 'user_submission'}
        ),
        stance='refute',
        confidence=0.5,  # 사용자 제출은 낮은 확신도
        adapter=UserSubmissionAdapter()
    )

    # 투표 시스템으로 credibility 조정
```

---

## 5. 대시보드 UI

### 5.1 Narrative 중심 뷰

```
[Narrative 계층]              [Claims]                  [Evidence]
┌──────────────────┐         ┌─────────────────┐      ┌──────────────┐
│Level 1: 민주당=위협│         │Claim #1:        │      │📱 DC갤 (45) │
│  ├─ L2: 친중=안보 │   →    │민주당 무비자 허용│  →  │📰 기사 (8)  │
│  │   ├─ 무비자    │         │                 │      │🎥 유튜브(3) │
│  │   ├─ 조선족도주│         │지지: 56건       │      │              │
│  │   └─ 간첩의혹  │         │반박: 3건        │      │❌ 반박:     │
│  └─ L2: 부패=사법 │         │신뢰도: 42%      │      │  팩트체크(2)│
│      ├─ 대장동    │         └─────────────────┘      │  나무위키(1)│
│      └─ 위증교사  │                                  └──────────────┘
└──────────────────┘

통계:
• 총 증거: 59건
• 신뢰도 분포: 낮음(45), 중간(8), 높음(3), 반박(3)
• 추세: 상승 ↗
```

### 5.2 Claim 상세 뷰

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Claim: "민주당이 중국인 무비자 입국을 허용했다"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 통계
• 총 언급: 56회
• 지지 증거: 53건 (95%)
• 반박 증거: 3건 (5%)
• 평균 신뢰도: 0.42 (낮음)

📅 시간 흐름
2024-11 ▓▓░░░ (5건)
2024-12 ▓▓▓▓░ (12건)
2025-01 ▓▓▓▓▓▓▓▓ (39건) ⬆️ 급증

🔍 증거 상세

지지 (53건):
┌────────────────────────────────────────────────────┐
│ 📱 DC갤러리 (45건) - 신뢰도: 낮음                   │
│   • [2025-01-15] "중국인 무비자로..." (uspolitics) │
│   • [2025-01-14] "조선족 무더기 입국..." (...)     │
│   • ... 43건 더보기                                 │
├────────────────────────────────────────────────────┤
│ 📰 기사 (5건) - 신뢰도: 중간                        │
│   • [2025-01-12] "중국인 관광객..." (TV조선)       │
│   • ... 4건 더보기                                  │
├────────────────────────────────────────────────────┤
│ 🎥 유튜브 (3건) - 신뢰도: 낮음                      │
│   • [2025-01-10] "민주당 친중 정책..." (채널명)    │
│   • ... 2건 더보기                                  │
└────────────────────────────────────────────────────┘

반박 (3건):
┌────────────────────────────────────────────────────┐
│ ✅ 팩트체크 (2건) - 신뢰도: 높음                    │
│   • [2025-01-13] "무비자는 윤석열 정부 정책"       │
│     (SBS 팩트체크) - 신뢰도: 0.9                   │
│   • [2025-01-11] "2019년부터 시행된 정책"          │
│     (AFP 팩트체크) - 신뢰도: 0.85                  │
├────────────────────────────────────────────────────┤
│ 📖 나무위키 (1건) - 신뢰도: 중간                    │
│   • [2025-01-10] "무비자 정책 연혁"               │
└────────────────────────────────────────────────────┘

💡 분석
• 주장은 광범위하게 퍼졌으나 신뢰도가 낮은 소스 위주
• 팩트체크 기관들이 명확히 반박
• 실제로는 윤석열 정부 정책임이 확인됨
• 결론: ❌ 허위/왜곡된 주장
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 소스별 필터링

```
[소스 선택]
☑️ DC갤러리 (218건)
☑️ 기사 (34건)
☑️ 유튜브 (12건)
☐ 나무위키 (5건)
☐ 인스타그램 (2건)

[Stance 필터]
☑️ 지지 (256건)
☑️ 반박 (15건)
☐ 중립 (0건)

[신뢰도 필터]
☐ 높음 (15건)
☑️ 중간 (34건)
☑️ 낮음 (232건)
```

---

## 6. 장점 요약

### ✅ 소스 독립적
```
DC갤, 기사, 유튜브, 나무위키, 인스타 등
→ 모두 같은 Claim/Evidence 구조
→ 추가 소스 쉽게 통합 가능
```

### ✅ 반박 관리 용이
```
Evidence.stance = support/refute
→ 같은 Claim에 지지/반박 모두 연결
→ 신뢰도 기반 판단 가능
```

### ✅ 확장 가능
```
새 소스 추가 = 새 Adapter 구현
→ 나머지는 동일한 파이프라인
```

### ✅ 데이터 기반 판단
```
Claim당 증거 수, 신뢰도, 시간 추세
→ 객관적 평가 가능
```

### ✅ 계층 구조
```
Narrative → Claims → Evidence
→ 큰 그림부터 세부까지 드릴다운
```

---

## 7. 다음 단계

1. **DB Migration**: claims, evidence, narratives 테이블 생성
2. **Core Engine**: Claim 추출, 매칭, Evidence 저장 로직
3. **Adapters**: DC갤, 기사, 유튜브 어댑터 구현
4. **Dashboard**: Claim 중심 UI 구현
5. **Counter-Evidence**: 팩트체크 크롤러, 사용자 제출 시스템

이 구조로 가면 진짜 확장 가능하고, 소스 독립적이며,
반박 자료까지 통합 관리 가능한 세계관 엔진이 됩니다.