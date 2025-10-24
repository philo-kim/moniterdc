"""
OptimalWorldviewConstructor - 최적화된 세계관 구성 엔진

시뮬레이션 결과 기반 최적 설계:
1. 계층형 구조 (대분류 → 세부)
2. 예시 중심 Narrative
3. 계층형 Metadata
4. Hybrid 매칭 (Vector 70% + Keyword 30%)
"""

from openai import AsyncOpenAI
import os
import json
import numpy as np
from typing import Dict, List, Tuple
from uuid import UUID
from engines.utils.supabase_client import get_supabase

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class OptimalWorldviewConstructor:
    """Construct hierarchical worldviews from layered perceptions"""

    def __init__(self):
        self.supabase = get_supabase()

    async def construct_all(self) -> Dict:
        """
        전체 세계관 구성 프로세스

        Returns:
            구성 결과 통계
        """

        print("\n" + "="*70)
        print("세계관 구성 시작")
        print("="*70)

        # 1. 모든 layered_perceptions 로드
        perceptions = await self._load_all_perceptions()
        print(f"\n✅ {len(perceptions)}개 perception 로드 완료")

        # 2. 계층형 세계관 추출
        worldview_hierarchy = await self._extract_hierarchical_worldviews(perceptions)
        print(f"\n✅ {len(worldview_hierarchy)}개 대분류 세계관 추출")

        # 3. 세계관 저장
        saved_worldviews = await self._save_worldviews(worldview_hierarchy)
        print(f"\n✅ {len(saved_worldviews)}개 세계관 저장 완료")

        # 4. Perception ↔ Worldview 매칭 (Hybrid)
        links_created = await self._match_perceptions_to_worldviews(
            perceptions,
            saved_worldviews
        )
        print(f"\n✅ {links_created}개 연결 생성")

        # 5. 통계 계산
        stats = await self._calculate_statistics(saved_worldviews)

        return stats

    async def _load_all_perceptions(self) -> List[Dict]:
        """모든 layered_perceptions 로드"""

        lps = self.supabase.table('layered_perceptions')\
            .select('id, content_id, deep_beliefs, implicit_assumptions, worldview_hints, explicit_claims')\
            .execute().data

        # Content titles 추가
        for lp in lps:
            content = self.supabase.table('contents')\
                .select('title')\
                .eq('id', lp['content_id'])\
                .execute().data

            if content:
                lp['title'] = content[0]['title']

        return lps

    async def _extract_hierarchical_worldviews(self, perceptions: List[Dict]) -> List[Dict]:
        """
        계층형 세계관 추출

        대분류 3-4개 → 각 대분류마다 세부 2-3개
        """

        # 샘플링 (GPT 토큰 제한 고려)
        sample_size = min(100, len(perceptions))
        sample_perceptions = perceptions[:sample_size]

        # 분석 데이터 준비
        analysis_data = []
        for lp in sample_perceptions:
            analysis_data.append({
                'title': lp.get('title', '')[:100],
                'deep_beliefs': lp.get('deep_beliefs', [])[:3],
                'implicit_assumptions': lp.get('implicit_assumptions', [])[:2],
                'worldview_hints': lp.get('worldview_hints', '')
            })

        prompt = f"""
다음은 DC Gallery 정치 글 {len(analysis_data)}개의 분석 결과입니다.

{json.dumps(analysis_data[:30], ensure_ascii=False, indent=1)}

이 데이터를 분석해서 **계층형 세계관 구조**를 만들어주세요.

요구사항:
1. **3-4개 대분류** (주요 주제 축)
2. 각 대분류마다 **2-3개 세부 세계관**
3. 각 세부 세계관은:
   - 예시 중심 Narrative (DC 해석 vs 일반 해석 대비)
   - 계층형 Metadata (core, interpretation_frame, emotional_drivers)

JSON 형식:
{{
  "hierarchy": [
    {{
      "category": "대분류명 (예: 민주당/좌파에 대한 인식)",
      "description": "대분류 설명",
      "subcategories": [
        {{
          "title": "세부 세계관명 (예: 독재 재현)",
          "narrative": {{
            "summary": "한 줄 요약",
            "examples": [
              {{
                "case": "구체적 사례 (예: 유심교체 정보)",
                "dc_interpretation": "DC Gallery의 해석",
                "normal_interpretation": "일반적 해석",
                "gap": "해석 차이의 핵심"
              }}
            ],
            "logic_chain": "논리 흐름 (A → B → C)",
            "historical_context": "역사적 참조"
          }},
          "metadata": {{
            "core": {{
              "primary_subject": "주요 대상",
              "primary_attribute": "핵심 속성",
              "primary_action": "핵심 행동"
            }},
            "interpretation_frame": {{
              "historical_lens": {{
                "reference_period": "참조 시기",
                "reference_events": ["사건1", "사건2"],
                "projection_logic": "투영 논리"
              }},
              "causal_chain": ["단계1", "단계2", "단계3"],
              "slippery_slope": {{
                "trigger": "시작점",
                "escalation": "확대 경로",
                "endpoint": "최종 결과"
              }}
            }},
            "emotional_drivers": {{
              "primary": "주 감정",
              "secondary": ["부 감정들"],
              "urgency_level": "긴급도"
            }},
            "key_concepts": ["개념1", "개념2", "개념3"]
          }}
        }}
      ]
    }}
  ]
}}
"""

        print("\n계층형 세계관 추출 중 (GPT-5)...")

        response = await client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are an expert in political discourse analysis. Always respond in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        hierarchy = result.get('hierarchy', [])

        # 결과 출력
        for cat in hierarchy:
            print(f"\n📂 {cat['category']}")
            for subcat in cat.get('subcategories', []):
                print(f"  └─ {subcat['title']}")

        return hierarchy

    async def _save_worldviews(self, hierarchy: List[Dict]) -> List[Dict]:
        """
        세계관을 worldviews 테이블에 저장

        계층 구조를 평탄화하되, category 정보 유지
        """

        saved_worldviews = []

        for category in hierarchy:
            category_name = category['category']
            category_desc = category.get('description', '')

            for subcat in category.get('subcategories', []):

                worldview_data = {
                    'title': f"{category_name} > {subcat['title']}",

                    # Frame을 JSON으로 저장
                    'frame': json.dumps({
                        'category': category_name,
                        'subcategory': subcat['title'],
                        'narrative': subcat.get('narrative', {}),
                        'metadata': subcat.get('metadata', {})
                    }, ensure_ascii=False),

                    'description': subcat['narrative'].get('summary', ''),

                    # Core fields
                    'core_subject': subcat['metadata']['core'].get('primary_subject', ''),
                    'core_attributes': subcat['metadata'].get('key_concepts', []),
                    'overall_valence': 'negative',  # DC Gallery는 대부분 부정적

                    # Empty arrays for now (will be filled during matching)
                    'perception_ids': [],
                    'total_perceptions': 0,
                }

                # Save
                result = self.supabase.table('worldviews').insert(worldview_data).execute()

                if result.data:
                    saved = result.data[0]
                    saved['subcategory_data'] = subcat  # 매칭용 데이터 보존
                    saved_worldviews.append(saved)

        return saved_worldviews

    async def _match_perceptions_to_worldviews(
        self,
        perceptions: List[Dict],
        worldviews: List[Dict]
    ) -> int:
        """
        Hybrid 매칭 (Vector 70% + Keyword 30%)

        각 perception을 가장 적합한 worldview(s)에 연결
        """

        print("\n" + "="*70)
        print("Perception ↔ Worldview 매칭 (Hybrid)")
        print("="*70)

        # 1. Worldview embeddings 계산
        print("\n1. Worldview embeddings 계산 중...")
        worldview_embeddings = []

        for wv in worldviews:
            # Narrative 텍스트 추출
            frame_data = json.loads(wv['frame'])
            narrative = frame_data.get('narrative', {})

            narrative_text = f"{narrative.get('summary', '')} "
            narrative_text += ' '.join([
                ex.get('dc_interpretation', '')
                for ex in narrative.get('examples', [])
            ])

            # Embedding 계산
            emb_response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=narrative_text
            )

            worldview_embeddings.append({
                'id': wv['id'],
                'title': wv['title'],
                'embedding': emb_response.data[0].embedding,
                'metadata': frame_data.get('metadata', {})
            })

        # 2. Perception 매칭
        print(f"\n2. {len(perceptions)}개 perception 매칭 중...")

        links_created = 0
        batch_size = 10

        for i in range(0, len(perceptions), batch_size):
            batch = perceptions[i:i+batch_size]

            for lp in batch:
                # Perception 텍스트
                lp_text = ' '.join(lp.get('deep_beliefs', []))

                if not lp_text.strip():
                    continue

                # Vector similarity
                lp_emb_response = await client.embeddings.create(
                    model="text-embedding-3-small",
                    input=lp_text
                )
                lp_embedding = lp_emb_response.data[0].embedding

                # Calculate scores
                best_matches = []

                for wv_emb in worldview_embeddings:
                    # Vector similarity
                    vector_sim = self._cosine_similarity(lp_embedding, wv_emb['embedding'])

                    # Keyword matching
                    keyword_score = self._keyword_match_score(lp, wv_emb['metadata'])

                    # Hybrid score (70% vector + 30% keyword)
                    hybrid_score = 0.7 * vector_sim + 0.3 * keyword_score

                    if hybrid_score > 0.5:  # Threshold
                        best_matches.append({
                            'worldview_id': wv_emb['id'],
                            'score': hybrid_score
                        })

                # Create links (top 2 matches)
                best_matches.sort(key=lambda x: x['score'], reverse=True)

                for match in best_matches[:2]:
                    await self._create_link(
                        lp['id'],
                        match['worldview_id'],
                        match['score']
                    )
                    links_created += 1

            print(f"\r  진행: {min(i+batch_size, len(perceptions))}/{len(perceptions)}", end='', flush=True)

        print(f"\n\n✅ {links_created}개 링크 생성 완료")

        return links_created

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Cosine similarity"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _keyword_match_score(self, perception: Dict, metadata: Dict) -> float:
        """
        키워드 매칭 점수 (0-1)

        Metadata의 key_concepts와 perception의 deep_beliefs 비교
        """

        lp_text = ' '.join(perception.get('deep_beliefs', []) +
                          perception.get('implicit_assumptions', []))

        if not lp_text:
            return 0.0

        key_concepts = metadata.get('key_concepts', [])
        core = metadata.get('core', {})

        # 검색 키워드
        keywords = key_concepts + [
            core.get('primary_subject', ''),
            core.get('primary_attribute', '')
        ]

        matches = 0
        for keyword in keywords:
            if keyword and keyword in lp_text:
                matches += 1

        # Normalize (0-1)
        return min(matches / max(len(keywords), 1), 1.0)

    async def _create_link(self, perception_id: str, worldview_id: str, score: float):
        """Create perception_worldview_link"""

        # Check if table exists
        try:
            link_data = {
                'perception_id': perception_id,
                'worldview_id': worldview_id,
                'relevance_score': score
            }

            self.supabase.table('perception_worldview_links').insert(link_data).execute()
        except Exception as e:
            # Table might not exist, create manually
            if 'does not exist' in str(e):
                # Create table first
                await self._ensure_links_table_exists()
                # Retry
                self.supabase.table('perception_worldview_links').insert(link_data).execute()

    async def _ensure_links_table_exists(self):
        """Ensure perception_worldview_links table exists"""

        # Read migration SQL
        migration_path = '/Users/taehyeonkim/dev/minjoo/moniterdc/supabase/migrations/203_create_perception_worldview_links.sql'

        with open(migration_path, 'r') as f:
            sql = f.read()

        # Execute (this is a simplified version, actual execution needs admin privileges)
        print("\n⚠️  perception_worldview_links 테이블이 없습니다.")
        print(f"   다음 SQL을 수동으로 실행하세요:\n")
        print(sql)

    async def _calculate_statistics(self, worldviews: List[Dict]) -> Dict:
        """통계 계산"""

        print("\n" + "="*70)
        print("통계 계산")
        print("="*70)

        # 각 worldview의 perception 개수 계산
        for wv in worldviews:
            try:
                links = self.supabase.table('perception_worldview_links')\
                    .select('perception_id', count='exact')\
                    .eq('worldview_id', wv['id'])\
                    .execute()

                count = links.count if links.count else 0

                # Update worldview
                self.supabase.table('worldviews')\
                    .update({'total_perceptions': count})\
                    .eq('id', wv['id'])\
                    .execute()

                print(f"  {wv['title'][:60]}: {count}개")

            except Exception as e:
                print(f"  ⚠️  통계 계산 실패: {e}")

        return {
            'total_worldviews': len(worldviews),
            'status': 'completed'
        }
