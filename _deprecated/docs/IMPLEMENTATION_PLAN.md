# 세계관 해체 엔진 - 구현 계획

## 전체 개요

### 목표
3개 Phase를 통해 세계관 해체 엔진을 점진적으로 구현

### 기간
- Phase 1: 2주 (핵심 인프라)
- Phase 2: 2주 (패턴 감지)
- Phase 3: 2주 (해체 & UI)
- 총 6주

### 현재 상태
```
✅ 기존 시스템:
- logic_repository (228개 데이터)
- dashboard (Next.js)
- crawler (DC갤러리)

🔄 진행 중:
- recluster_by_frame.py 실행 중
- dashboard npm run dev 실행 중

📋 설계 완료:
- SYSTEM_ARCHITECTURE.md
- 3-Layer 구조 정의
- 6개 엔진 설계
```

---

## Phase 1: 핵심 인프라 (Week 1-2)

### 목표
기존 시스템과 병행하면서 새 3-Layer 시스템의 기반 구축

### Week 1: 데이터베이스 & 기본 수집

#### Day 1-2: 데이터베이스 마이그레이션

**작업:**
```
1. 새 스키마 생성
   - 001_create_contents_table.sql
   - 002_create_perceptions_table.sql
   - 003_create_perception_connections_table.sql
   - 004_create_worldviews_table.sql
   - 005_create_rebuttals_table.sql

2. 인덱스 & 제약조건
   - 벡터 검색 인덱스
   - 외래키 제약
   - 유니크 제약

3. RPC 함수들
   - search_similar_perceptions()
   - search_similar_worldviews()
   - increment_worldview_stats()
```

**파일 생성:**
- `supabase/migrations/100_create_contents.sql`
- `supabase/migrations/101_create_perceptions.sql`
- `supabase/migrations/102_create_perception_connections.sql`
- `supabase/migrations/103_create_worldviews.sql`
- `supabase/migrations/104_create_rebuttals.sql`
- `supabase/migrations/105_create_rpc_functions.sql`

**검증:**
```bash
# 마이그레이션 실행
supabase db push --include-all

# 테이블 확인
supabase db inspect

# 테스트 데이터 삽입
python3 test_new_schema.py
```

#### Day 3-4: Content Collector 구현

**작업:**
```
1. Source Adapter 인터페이스
   - base_adapter.py
   - dc_gallery_adapter.py

2. ContentCollector 클래스
   - content_collector.py
   - 중복 체크 로직
   - 메타데이터 파싱
   - 신뢰도 계산

3. 유틸리티
   - embedding_utils.py (OpenAI 임베딩)
   - supabase_client.py (클라이언트 wrapper)
```

**파일 생성:**
```
engines/
├── __init__.py
├── adapters/
│   ├── __init__.py
│   ├── base_adapter.py
│   └── dc_gallery_adapter.py
├── collectors/
│   ├── __init__.py
│   └── content_collector.py
└── utils/
    ├── __init__.py
    ├── embedding_utils.py
    └── supabase_client.py
```

**검증:**
```python
# test_content_collector.py
from engines.collectors.content_collector import ContentCollector

collector = ContentCollector()

# DC갤 10개 글 수집 테스트
content_ids = await collector.collect(
    source_type='dc_gallery',
    gallery='uspolitics',
    limit=10
)

print(f"Collected {len(content_ids)} contents")
```

#### Day 5: Perception Extractor 구현

**작업:**
```
1. GPT 프롬프트 설계
   - PERCEPTION_EXTRACTION_PROMPT
   - 주체, 속성, valence, claims, emotions 추출
   - JSON 응답 파싱

2. PerceptionExtractor 클래스
   - GPT 분석 로직
   - 임베딩 생성
   - perceptions 테이블 저장
   - 에러 핸들링

3. 배치 처리
   - 여러 content 동시 분석
   - Rate limiting
```

**파일 생성:**
```
engines/
└── extractors/
    ├── __init__.py
    ├── perception_extractor.py
    └── prompts.py
```

**프롬프트 예시:**
```python
PERCEPTION_EXTRACTION_PROMPT = """
당신은 정치 콘텐츠 분석 전문가입니다.

주어진 콘텐츠를 분석하여 다음을 추출하세요:

1. perceived_subject: 누구에 대한 이야기인가? (민주당, 이재명, 윤석열 등)
2. perceived_attribute: 어떤 속성을 부여하는가? (친중, 부패, 무능 등)
3. perceived_valence: 긍정/부정/중립?
4. claims: 구체적 주장들 (배열)
5. keywords: 핵심 키워드들
6. emotions: 자극하는 감정들 (fear, anger, disgust 등)

JSON 형식으로 응답:
{
  "perceptions": [
    {
      "subject": "...",
      "attribute": "...",
      "valence": "positive/negative/neutral",
      "claims": ["...", "..."],
      "keywords": ["...", "..."],
      "emotions": ["fear", "anger"],
      "confidence": 0.9
    }
  ]
}

한 콘텐츠에서 여러 주체에 대한 인식이 있을 수 있습니다.
"""
```

**검증:**
```python
# test_perception_extractor.py
from engines.extractors.perception_extractor import PerceptionExtractor

extractor = PerceptionExtractor()

# 하나의 content 분석
content_id = "uuid-here"
perception_ids = await extractor.extract(content_id)

print(f"Extracted {len(perception_ids)} perceptions")

# 결과 확인
for p_id in perception_ids:
    perception = await get_perception(p_id)
    print(f"Subject: {perception['perceived_subject']}")
    print(f"Attribute: {perception['perceived_attribute']}")
    print(f"Valence: {perception['perceived_valence']}")
```

### Week 2: 연결 & 통합 테스트

#### Day 6-7: Connection Detector 구현

**작업:**
```
1. ConnectionDetector 클래스
   - detect_temporal() - 시간적 연결
   - detect_thematic() - 주제적 연결 (벡터 유사도)
   - detect_causal() - 인과적 연결 (키워드)

2. 벡터 검색 최적화
   - ivfflat 인덱스 활용
   - 임계값 튜닝

3. 배치 연결 감지
   - 새 perception 추가 시 자동 실행
```

**파일 생성:**
```
engines/
└── detectors/
    ├── __init__.py
    └── connection_detector.py
```

**검증:**
```python
# test_connection_detector.py
detector = ConnectionDetector()

# 특정 perception의 연결 감지
await detector.detect_connections(perception_id)

# 연결 확인
connections = await get_connections(perception_id)
print(f"Found {len(connections)} connections")
for conn in connections:
    print(f"Type: {conn['connection_type']}, Strength: {conn['strength']}")
```

#### Day 8: 통합 파이프라인 구현

**작업:**
```
1. Pipeline 클래스
   - collect_and_analyze()
   - content → perception → connection 자동 흐름

2. 스케줄러
   - 주기적 크롤링
   - 에러 복구

3. 로깅 & 모니터링
   - 진행 상황 추적
   - 성공/실패 통계
```

**파일 생성:**
```
engines/
└── pipeline/
    ├── __init__.py
    ├── analysis_pipeline.py
    └── scheduler.py
```

**파이프라인 예시:**
```python
class AnalysisPipeline:
    """
    콘텐츠 수집 → 분석 → 연결 감지 자동 파이프라인
    """

    def __init__(self):
        self.collector = ContentCollector()
        self.extractor = PerceptionExtractor()
        self.detector = ConnectionDetector()

    async def run(self, source_type: str, **params):
        """
        전체 파이프라인 실행
        """
        logger.info(f"Starting pipeline for {source_type}")

        # 1. Collect
        content_ids = await self.collector.collect(source_type, **params)
        logger.info(f"Collected {len(content_ids)} contents")

        # 2. Extract perceptions
        all_perception_ids = []
        for content_id in content_ids:
            perception_ids = await self.extractor.extract(content_id)
            all_perception_ids.extend(perception_ids)

            # 3. Detect connections
            for p_id in perception_ids:
                await self.detector.detect_connections(p_id)

        logger.info(f"Extracted {len(all_perception_ids)} perceptions")
        logger.info("Pipeline completed")

        return {
            'contents': len(content_ids),
            'perceptions': len(all_perception_ids)
        }
```

#### Day 9-10: 기존 데이터 마이그레이션

**작업:**
```
1. Migration Script
   - logic_repository → contents
   - 기존 228개 논리 변환
   - perception 재추출

2. 검증
   - 데이터 무결성 확인
   - 누락 데이터 체크
   - 통계 비교

3. 병행 운영 설정
   - 기존 시스템 유지
   - 새 시스템 동시 실행
```

**파일 생성:**
```
migrations/
├── migrate_existing_data.py
└── verify_migration.py
```

**마이그레이션 스크립트:**
```python
# migrate_existing_data.py
async def migrate_logic_repository():
    """
    기존 logic_repository → 새 시스템
    """
    logger.info("Starting migration...")

    # 1. 기존 데이터 가져오기
    logics = await supabase.table('logic_repository').select('*').execute()
    logger.info(f"Found {len(logics.data)} existing logics")

    # 2. Contents로 변환
    for logic in logics.data:
        # content 생성
        content_id = await create_content_from_logic(logic)

        # perception 재추출
        perception_ids = await extractor.extract(content_id)

        # connection 감지
        for p_id in perception_ids:
            await detector.detect_connections(p_id)

        logger.info(f"Migrated logic {logic['id']}")

    logger.info("Migration completed")

async def create_content_from_logic(logic: Dict) -> UUID:
    """
    logic_repository 행 → content 변환
    """
    return await supabase.table('contents').insert({
        'source_type': 'dc_gallery',
        'source_url': logic['original_url'],
        'source_id': logic['original_post_num'],
        'title': logic['original_title'],
        'body': logic['original_content'],
        'metadata': {
            'gallery': logic['source_gallery'],
            'migrated_from': 'logic_repository',
            'original_id': logic['id']
        },
        'base_credibility': 0.2,
        'published_at': logic['created_at']
    }).execute()
```

**검증:**
```bash
# 마이그레이션 실행
python3 migrations/migrate_existing_data.py

# 검증
python3 migrations/verify_migration.py

# 출력 예시:
# ✅ Migrated 228 logics
# ✅ Created 228 contents
# ✅ Extracted 342 perceptions
# ✅ Detected 1,234 connections
```

---

## Phase 2: 패턴 감지 (Week 3-4)

### 목표
인식들로부터 세계관 패턴을 자동 감지하고 메커니즘 분석

### Week 3: Worldview Detector

#### Day 11-12: Worldview Detector 구현

**작업:**
```
1. WorldviewDetector 클래스
   - is_worldview_candidate() - 후보 검증
   - create_worldview() - 세계관 생성
   - update_worldview() - 기존 세계관 업데이트

2. 감지 로직
   - 주체별 그룹핑
   - 방향성 일관성 확인 (>70%)
   - 시간적 지속성 확인 (>30일)
   - 빈도 확인 (>10회)

3. Frame 생성
   - GPT로 프레임 자동 생성
   - "주체=속성=결과" 구조
```

**파일 생성:**
```
engines/
└── detectors/
    └── worldview_detector.py
```

**핵심 로직:**
```python
class WorldviewDetector:
    async def detect_worldviews(self, time_window_days: int = 90):
        """
        주기적 실행: 세계관 패턴 감지
        """
        # 1. 최근 perceptions 가져오기
        perceptions = await self.get_recent_perceptions(time_window_days)

        # 2. 주체별 그룹핑
        grouped = self.group_by_subject(perceptions)

        for subject, perception_list in grouped.items():
            # 3. 후보 검증
            if not await self.is_worldview_candidate(perception_list):
                continue

            # 4. 기존 세계관 확인
            existing = await self.find_existing_worldview(subject)

            if existing:
                await self.update_worldview(existing['id'], perception_list)
            else:
                await self.create_worldview(subject, perception_list)

    async def is_worldview_candidate(self, perceptions: List[Dict]) -> bool:
        """
        세계관 후보 조건
        """
        # 조건 1: 빈도 (>10)
        if len(perceptions) < 10:
            return False

        # 조건 2: 방향성 일관성 (>70%)
        valences = [p['perceived_valence'] for p in perceptions]
        dominant = max(set(valences), key=valences.count)
        consistency = valences.count(dominant) / len(valences)
        if consistency < 0.7:
            return False

        # 조건 3: 시간적 지속성 (>30일)
        timestamps = [p['created_at'] for p in perceptions]
        span = (max(timestamps) - min(timestamps)).days
        if span < 30:
            return False

        return True
```

**GPT 프롬프트:**
```python
FRAME_GENERATION_PROMPT = """
여러 인식들을 분석하여 이들이 만드는 전체 프레임을 추출하세요.

인식들:
{perceptions_summary}

다음 형식으로 응답:
{
  "title": "민주당=친중=안보위협",
  "frame": "대상=속성=결과",
  "description": "이 세계관은 민주당이 중국과 결탁하여..."
}
"""
```

#### Day 13-14: Mechanism Analyzer 구현

**작업:**
```
1. MechanismAnalyzer 클래스
   - analyze_cognitive() - 인지적 메커니즘
   - analyze_temporal() - 시간적 패턴
   - analyze_social() - 사회적 확산
   - analyze_structural() - 구조적 특징

2. 심리 메커니즘 감지
   - 확증편향 (confirmation bias)
   - 가용성 휴리스틱 (availability heuristic)
   - 감정 로딩 (emotional loading)

3. 시간 패턴 분석
   - Seed → Growth → Peak → Maintenance
   - 가속 포인트 감지
```

**파일 생성:**
```
engines/
└── analyzers/
    ├── __init__.py
    └── mechanism_analyzer.py
```

**핵심 로직:**
```python
class MechanismAnalyzer:
    def analyze_cognitive(self, perceptions: List[Dict]) -> List[Dict]:
        """
        심리적 메커니즘 감지
        """
        mechanisms = []

        # 확증편향: 일관된 부정적 인식
        if self.uses_confirmation_bias(perceptions):
            mechanisms.append({
                'type': 'confirmation_bias',
                'description': '기존 편견을 강화하는 정보만 제시',
                'vulnerability': '사람들은 자신의 믿음을 확인하는 정보 선호'
            })

        # 가용성 휴리스틱: 반복
        repetition_rate = len(perceptions) / self.get_unique_claims(perceptions)
        if repetition_rate > 2:
            mechanisms.append({
                'type': 'availability_heuristic',
                'description': f'{repetition_rate:.1f}배 반복을 통해 중요성 부각',
                'vulnerability': '자주 본 정보를 더 중요하게 인식'
            })

        # 감정 로딩
        all_emotions = [e for p in perceptions for e in p.get('emotions', [])]
        if all_emotions:
            mechanisms.append({
                'type': 'emotional_loading',
                'emotions': list(set(all_emotions)),
                'description': '공포/분노 등 강한 감정으로 이성적 판단 방해'
            })

        return mechanisms

    def analyze_temporal(self, perceptions: List[Dict]) -> Dict:
        """
        시간 패턴 분석
        """
        timeline = sorted(perceptions, key=lambda p: p['created_at'])

        phases = []

        # Seed (처음 20%)
        seed_count = max(5, len(timeline) // 5)
        seed = timeline[:seed_count]
        phases.append({
            'phase': 'seed',
            'date': seed[0]['created_at'],
            'perception_count': len(seed),
            'description': '초기 주장 제시'
        })

        # Growth (중간 60%)
        growth = timeline[seed_count:int(len(timeline)*0.8)]
        phases.append({
            'phase': 'growth',
            'date_start': growth[0]['created_at'],
            'date_end': growth[-1]['created_at'],
            'perception_count': len(growth),
            'tactics': self.detect_tactics(growth)
        })

        # Peak (마지막 20%)
        peak = timeline[int(len(timeline)*0.8):]
        phases.append({
            'phase': 'peak',
            'date': peak[0]['created_at'],
            'perception_count': len(peak),
            'platforms': self.get_platforms(peak)
        })

        return {
            'phases': phases,
            'duration_days': (timeline[-1]['created_at'] - timeline[0]['created_at']).days
        }
```

### Week 4: 강도 측정 & 통합

#### Day 15-16: 강도 측정 구현

**작업:**
```
1. Strength Calculator
   - cognitive_strength() - 인지적 강도
   - temporal_strength() - 시간적 지속성
   - social_strength() - 사회적 확산
   - structural_strength() - 구조적 체계성
   - overall_strength() - 종합 강도

2. 가중치 조정
   - 각 차원별 중요도
   - 전체 점수 계산

3. 추세 분석
   - Rising/Stable/Falling/Dead
   - 최근 변화율
```

**파일 생성:**
```
engines/
└── analyzers/
    └── strength_calculator.py
```

**강도 계산:**
```python
class StrengthCalculator:
    def calculate(self, perceptions: List[Dict], connections: List[Dict]) -> Dict:
        """
        다차원 강도 측정
        """
        return {
            'cognitive': self.cognitive_strength(perceptions),
            'temporal': self.temporal_strength(perceptions),
            'social': self.social_strength(perceptions),
            'structural': self.structural_strength(perceptions, connections),
            'overall': self.overall_strength(...)
        }

    def cognitive_strength(self, perceptions: List[Dict]) -> float:
        """
        인지적 강도: 얼마나 강한 인상인가

        요소:
        - 방향성 일관성 (모두 부정적?)
        - 감정 강도 (공포, 분노?)
        - 반복 빈도
        """
        # 방향성 일관성
        valences = [p['perceived_valence'] for p in perceptions]
        dominant = max(set(valences), key=valences.count)
        consistency = valences.count(dominant) / len(valences)

        # 감정 로딩
        strong_emotions = ['fear', 'anger', 'disgust']
        emotion_count = sum(
            1 for p in perceptions
            for e in p.get('emotions', [])
            if e in strong_emotions
        )
        emotion_ratio = emotion_count / len(perceptions)

        # 반복
        unique_claims = len(set(c for p in perceptions for c in p['claims']))
        total_claims = sum(len(p['claims']) for p in perceptions)
        repetition = 1 - (unique_claims / total_claims) if total_claims > 0 else 0

        return (consistency * 0.4 + emotion_ratio * 0.3 + repetition * 0.3)

    def temporal_strength(self, perceptions: List[Dict]) -> float:
        """
        시간적 지속성: 얼마나 오래 지속되는가
        """
        timestamps = [p['created_at'] for p in perceptions]
        span_days = (max(timestamps) - min(timestamps)).days

        # 90일 기준으로 정규화
        return min(span_days / 90, 1.0)

    def social_strength(self, perceptions: List[Dict]) -> float:
        """
        사회적 확산: 얼마나 넓게 퍼졌는가
        """
        # 플랫폼 다양성
        platforms = set()
        for p in perceptions:
            content = get_content(p['content_id'])
            platforms.add(content['source_type'])

        platform_diversity = len(platforms) / 5  # 5개 플랫폼 기준

        # 빈도
        frequency = min(len(perceptions) / 50, 1.0)  # 50개 기준

        return (platform_diversity * 0.5 + frequency * 0.5)

    def structural_strength(self, perceptions: List[Dict], connections: List[Dict]) -> float:
        """
        구조적 체계성: 얼마나 체계적으로 연결되었는가
        """
        # 연결 밀도
        max_connections = len(perceptions) * (len(perceptions) - 1) / 2
        connection_density = len(connections) / max_connections if max_connections > 0 else 0

        return connection_density

    def overall_strength(self, cognitive, temporal, social, structural) -> float:
        """
        종합 강도 (가중 평균)
        """
        return (
            cognitive * 0.3 +
            temporal * 0.3 +
            social * 0.2 +
            structural * 0.2
        )
```

#### Day 17-18: 자동 감지 스케줄러

**작업:**
```
1. 주기적 실행
   - 매일 자정: 세계관 감지
   - 매시간: 새 콘텐츠 수집
   - 실시간: connection 감지

2. 통합 테스트
   - 전체 파이프라인 검증
   - 성능 측정
   - 에러 핸들링

3. 모니터링
   - 진행 상황 대시보드
   - 에러 알림
```

**파일 생성:**
```
engines/
└── scheduler/
    ├── __init__.py
    ├── worldview_scheduler.py
    └── monitor.py
```

**스케줄러:**
```python
# worldview_scheduler.py
import schedule
import time

class WorldviewScheduler:
    def __init__(self):
        self.detector = WorldviewDetector()
        self.pipeline = AnalysisPipeline()

    def setup(self):
        """
        스케줄 설정
        """
        # 매일 자정: 세계관 감지
        schedule.every().day.at("00:00").do(self.run_worldview_detection)

        # 매 시간: DC갤 수집
        schedule.every().hour.do(self.run_collection)

        # 매 10분: 통계 업데이트
        schedule.every(10).minutes.do(self.update_stats)

    async def run_worldview_detection(self):
        logger.info("Running worldview detection...")
        await self.detector.detect_worldviews(time_window_days=90)
        logger.info("Worldview detection completed")

    async def run_collection(self):
        logger.info("Running content collection...")
        await self.pipeline.run(
            source_type='dc_gallery',
            gallery='uspolitics',
            limit=20
        )
        logger.info("Collection completed")

    def run(self):
        """
        스케줄러 실행
        """
        self.setup()

        logger.info("Scheduler started")
        while True:
            schedule.run_pending()
            time.sleep(1)

# 실행
if __name__ == '__main__':
    scheduler = WorldviewScheduler()
    scheduler.run()
```

#### Day 19-20: Phase 2 통합 테스트

**검증 체크리스트:**
```
✅ 세계관 자동 감지
   - 기존 228개 논리에서 세계관 추출
   - 예상: 5-10개 주요 세계관

✅ 메커니즘 분석
   - 각 세계관의 cognitive mechanisms 확인
   - temporal patterns 확인

✅ 강도 측정
   - strength_overall > 0.7인 세계관 확인
   - 강도 순으로 정렬

✅ 성능
   - 228개 논리 재분석: < 30분
   - 새 콘텐츠 10개 분석: < 2분
```

---

## Phase 3: 해체 & UI (Week 5-6)

### 목표
세계관 해체 전략 생성 및 사용자 인터페이스 구현

### Week 5: Deconstruction Engine

#### Day 21-22: 구조적 허점 감지

**작업:**
```
1. FlawDetector 클래스
   - detect_term_ambiguity() - 용어 모호성
   - detect_logical_leap() - 논리 비약
   - detect_false_dichotomy() - 이분법
   - detect_selective_facts() - 선별적 사실

2. 팩트체크 통합
   - 자동 팩트체크 검색
   - 신뢰도 평가

3. GPT 분석
   - 구조적 오류 요약
```

**파일 생성:**
```
engines/
└── deconstructors/
    ├── __init__.py
    ├── flaw_detector.py
    └── factchecker.py
```

#### Day 23-24: 대안 내러티브 생성

**작업:**
```
1. CounterNarrativeGenerator
   - GPT로 대안 내러티브 생성
   - 핵심 반박 포인트 추출
   - 추천 답변 생성

2. 증거 수집
   - 팩트체크 기사 링크
   - 공식 자료 링크
   - 나무위키 링크

3. 행동 가이드
   - 4단계 행동 전략
   - 복사 가능한 템플릿
```

**파일 생성:**
```
engines/
└── deconstructors/
    ├── counter_narrative_generator.py
    └── action_guide_generator.py
```

**GPT 프롬프트:**
```python
COUNTER_NARRATIVE_PROMPT = """
주어진 왜곡된 세계관에 대한 대안 내러티브를 생성하세요.

왜곡된 세계관:
{worldview_frame}

구조적 허점:
{structural_flaws}

팩트체크 결과:
{factcheck_results}

다음을 생성하세요:
1. 대안 내러티브 (같은 사실을 다른 관점에서)
2. 핵심 반박 포인트 (3-5개)
3. 사용자가 복사할 수 있는 간결한 답변 (2-3문장)

JSON 형식:
{
  "counter_narrative": "...",
  "key_rebuttals": ["...", "...", "..."],
  "suggested_response": "...",
  "evidence_urls": ["...", "..."]
}
"""
```

#### Day 25: DeconstructionEngine 통합

**작업:**
```
1. DeconstructionEngine 클래스
   - 모든 컴포넌트 통합
   - worldview → deconstruction 자동 생성

2. 자동 실행
   - 새 세계관 감지 시 자동 해체 생성
   - 기존 세계관 업데이트 시 재생성

3. 검증
   - 모든 세계관에 대한 해체 전략 확인
```

### Week 6: 대시보드 UI

#### Day 26-27: 세계관 지도 뷰

**작업:**
```
1. API 엔드포인트
   - GET /api/worldviews (목록)
   - GET /api/worldviews/:id (상세)
   - GET /api/worldviews/:id/deconstruction (해체)

2. React 컴포넌트
   - WorldviewMap.tsx (메인 뷰)
   - WorldviewCard.tsx (개별 카드)
   - StrengthMeter.tsx (강도 표시)

3. 시각화
   - 강도 막대 그래프
   - 추세 표시 (↗↘→)
   - 플랫폼 아이콘
```

**파일 생성:**
```
dashboard/
├── app/
│   └── api/
│       └── worldviews/
│           ├── route.ts
│           └── [id]/
│               ├── route.ts
│               └── deconstruction/
│                   └── route.ts
└── components/
    ├── WorldviewMap.tsx
    ├── WorldviewCard.tsx
    └── StrengthMeter.tsx
```

**UI 예시:**
```tsx
// WorldviewMap.tsx
export default function WorldviewMap() {
  const { data: worldviews } = useSWR('/api/worldviews')

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">
        🗺️ 세계관 지도
      </h1>

      <div className="mb-4">
        <Badge>활성 세계관 {worldviews?.length}</Badge>
      </div>

      <div className="space-y-4">
        {worldviews?.map(worldview => (
          <WorldviewCard key={worldview.id} worldview={worldview} />
        ))}
      </div>
    </div>
  )
}
```

#### Day 28-29: 해체 분석 뷰

**작업:**
```
1. DeconstructionView 컴포넌트
   - 형성 과정 타임라인
   - 메커니즘 설명
   - 구조적 허점
   - 대안 내러티브
   - 행동 가이드

2. 인터랙티브 요소
   - 답변 복사 버튼
   - 공유 버튼
   - 증거 링크
```

**파일 생성:**
```
dashboard/
└── components/
    ├── DeconstructionView.tsx
    ├── FormationTimeline.tsx
    ├── MechanismExplainer.tsx
    └── ActionGuide.tsx
```

#### Day 30: URL 입력 분석 & 최종 통합

**작업:**
```
1. URL 분석 기능
   - 입력 폼
   - 실시간 분석
   - 결과 표시

2. 최종 통합 테스트
   - 전체 사용자 플로우
   - 성능 최적화
   - 에러 핸들링

3. 배포 준비
   - 환경 변수 설정
   - 로깅 설정
   - 모니터링 설정
```

**파일 생성:**
```
dashboard/
└── components/
    ├── URLAnalyzer.tsx
    └── AnalysisResult.tsx
```

---

## 파일 구조 전체 정리

```
moniterdc/
├── engines/                        # 새로운 엔진들
│   ├── __init__.py
│   ├── adapters/                   # Source adapters
│   │   ├── __init__.py
│   │   ├── base_adapter.py
│   │   └── dc_gallery_adapter.py
│   ├── collectors/                 # Content collection
│   │   ├── __init__.py
│   │   └── content_collector.py
│   ├── extractors/                 # Perception extraction
│   │   ├── __init__.py
│   │   ├── perception_extractor.py
│   │   └── prompts.py
│   ├── detectors/                  # Pattern detection
│   │   ├── __init__.py
│   │   ├── connection_detector.py
│   │   └── worldview_detector.py
│   ├── analyzers/                  # Analysis engines
│   │   ├── __init__.py
│   │   ├── mechanism_analyzer.py
│   │   └── strength_calculator.py
│   ├── deconstructors/            # Deconstruction engines
│   │   ├── __init__.py
│   │   ├── flaw_detector.py
│   │   ├── factchecker.py
│   │   ├── counter_narrative_generator.py
│   │   └── action_guide_generator.py
│   ├── pipeline/                   # Integration
│   │   ├── __init__.py
│   │   ├── analysis_pipeline.py
│   │   └── deconstruction_engine.py
│   ├── scheduler/                  # Automation
│   │   ├── __init__.py
│   │   ├── worldview_scheduler.py
│   │   └── monitor.py
│   └── utils/                      # Utilities
│       ├── __init__.py
│       ├── embedding_utils.py
│       └── supabase_client.py
│
├── supabase/
│   └── migrations/
│       ├── 100_create_contents.sql
│       ├── 101_create_perceptions.sql
│       ├── 102_create_perception_connections.sql
│       ├── 103_create_worldviews.sql
│       ├── 104_create_rebuttals.sql
│       └── 105_create_rpc_functions.sql
│
├── migrations/                     # Data migration
│   ├── migrate_existing_data.py
│   └── verify_migration.py
│
├── tests/                          # Tests
│   ├── test_content_collector.py
│   ├── test_perception_extractor.py
│   ├── test_connection_detector.py
│   ├── test_worldview_detector.py
│   └── test_integration.py
│
├── dashboard/                      # UI
│   ├── app/
│   │   ├── api/
│   │   │   └── worldviews/
│   │   ├── worldview-map/
│   │   └── analyze/
│   └── components/
│       ├── WorldviewMap.tsx
│       ├── WorldviewCard.tsx
│       ├── DeconstructionView.tsx
│       ├── FormationTimeline.tsx
│       ├── MechanismExplainer.tsx
│       ├── ActionGuide.tsx
│       ├── URLAnalyzer.tsx
│       └── AnalysisResult.tsx
│
├── scripts/                        # Utility scripts
│   ├── run_pipeline.py
│   ├── run_scheduler.py
│   └── manual_analysis.py
│
├── SYSTEM_ARCHITECTURE.md
├── IMPLEMENTATION_PLAN.md
└── README.md
```

---

## 일일 체크리스트

### Phase 1 체크리스트

#### Week 1
- [ ] Day 1-2: DB 마이그레이션
  - [ ] 5개 SQL 파일 작성
  - [ ] supabase db push 실행
  - [ ] 테스트 데이터 삽입 검증

- [ ] Day 3-4: Content Collector
  - [ ] base_adapter.py 구현
  - [ ] dc_gallery_adapter.py 구현
  - [ ] content_collector.py 구현
  - [ ] 10개 글 수집 테스트

- [ ] Day 5: Perception Extractor
  - [ ] GPT 프롬프트 작성
  - [ ] perception_extractor.py 구현
  - [ ] 추출 결과 검증

#### Week 2
- [ ] Day 6-7: Connection Detector
  - [ ] connection_detector.py 구현
  - [ ] 3가지 연결 유형 테스트

- [ ] Day 8: Pipeline
  - [ ] analysis_pipeline.py 구현
  - [ ] 전체 흐름 테스트

- [ ] Day 9-10: Migration
  - [ ] migrate_existing_data.py 실행
  - [ ] 228개 논리 변환 검증

### Phase 2 체크리스트

#### Week 3
- [ ] Day 11-12: Worldview Detector
  - [ ] worldview_detector.py 구현
  - [ ] 후보 검증 로직 테스트

- [ ] Day 13-14: Mechanism Analyzer
  - [ ] mechanism_analyzer.py 구현
  - [ ] 4가지 차원 분석 검증

#### Week 4
- [ ] Day 15-16: Strength Calculator
  - [ ] strength_calculator.py 구현
  - [ ] 강도 측정 검증

- [ ] Day 17-18: Scheduler
  - [ ] worldview_scheduler.py 구현
  - [ ] 자동 실행 테스트

- [ ] Day 19-20: Integration
  - [ ] 전체 Phase 2 테스트
  - [ ] 세계관 5-10개 감지 확인

### Phase 3 체크리스트

#### Week 5
- [ ] Day 21-22: Flaw Detector
  - [ ] flaw_detector.py 구현
  - [ ] factchecker.py 구현

- [ ] Day 23-24: Counter Narrative
  - [ ] counter_narrative_generator.py 구현
  - [ ] action_guide_generator.py 구현

- [ ] Day 25: Deconstruction
  - [ ] deconstruction_engine.py 통합
  - [ ] 자동 생성 테스트

#### Week 6
- [ ] Day 26-27: Worldview Map UI
  - [ ] API 엔드포인트 3개
  - [ ] React 컴포넌트 3개

- [ ] Day 28-29: Deconstruction UI
  - [ ] DeconstructionView 구현
  - [ ] 인터랙티브 요소

- [ ] Day 30: Final
  - [ ] URL 분석 기능
  - [ ] 최종 통합 테스트
  - [ ] 배포 준비

---

## 성공 기준

### Phase 1 완료 조건
```
✅ 228개 기존 논리가 새 시스템에 마이그레이션됨
✅ Contents, Perceptions, Connections 테이블에 데이터 있음
✅ 새 DC갤 글 10개 수집/분석 성공
✅ 파이프라인이 자동으로 작동
```

### Phase 2 완료 조건
```
✅ 5-10개 주요 세계관 자동 감지됨
✅ 각 세계관의 메커니즘 분석 완료
✅ 강도 측정 (0-1 점수) 정상 작동
✅ 스케줄러가 주기적으로 실행됨
```

### Phase 3 완료 조건
```
✅ 모든 세계관에 해체 전략 생성됨
✅ 대시보드에서 세계관 지도 확인 가능
✅ URL 입력하면 실시간 분석 결과 표시
✅ 복사 가능한 반박 답변 제공
```

---

## 다음 단계

이 계획서를 기반으로:

1. **즉시 시작**: Phase 1 Day 1 (DB 마이그레이션)
2. **진행 추적**: 매일 체크리스트 업데이트
3. **문제 발생 시**: 이 계획서를 참조하여 문맥 유지

시작할까요?