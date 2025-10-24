"""
BeliefNormalizer - 유사한 믿음들을 통합

문제: GPT가 같은 믿음을 다르게 표현 → 889개 중 887개가 1회 등장
해결: 유사한 믿음들을 하나의 "정규화된 믿음"으로 통합
"""

from openai import AsyncOpenAI
import os
import json
from typing import Dict, List, Tuple
from engines.utils.supabase_client import get_supabase

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class BeliefNormalizer:
    """Normalize similar beliefs into canonical forms"""

    def __init__(self):
        self.supabase = get_supabase()

    async def normalize_all_beliefs(self, batch_size: int = 50) -> Dict:
        """
        Normalize all beliefs in belief_patterns table

        Args:
            batch_size: How many beliefs to process in one GPT call

        Returns:
            Dict with normalization stats
        """

        # 1. Get all beliefs
        print("\n📊 1. 기존 믿음 가져오기...")
        beliefs = self.supabase.table('belief_patterns')\
            .select('id, belief, frequency, example_content_ids')\
            .execute().data

        print(f"✅ 총 {len(beliefs)}개 믿음")

        # 2. Cluster similar beliefs
        print("\n🔍 2. 유사 믿음 클러스터링...")
        clusters = await self._cluster_beliefs(beliefs, batch_size)

        print(f"✅ {len(clusters)}개 클러스터 생성")

        # 3. Update database
        print("\n💾 3. 데이터베이스 업데이트...")
        stats = await self._update_clusters(clusters)

        return stats

    async def _cluster_beliefs(self, beliefs: List[Dict], batch_size: int) -> List[Dict]:
        """
        Cluster similar beliefs using GPT

        Returns:
            List of clusters, each with:
            - canonical_belief: 정규화된 믿음 (대표 문장)
            - belief_ids: 이 클러스터에 속한 belief_pattern id들
            - total_frequency: 합산 빈도
            - example_content_ids: 통합된 예시 content_id들
        """

        clusters = []
        processed = set()

        # Process in batches
        for i in range(0, len(beliefs), batch_size):
            batch = [b for b in beliefs[i:i+batch_size] if b['id'] not in processed]

            if not batch:
                continue

            print(f"\r  배치 {i//batch_size + 1}: {len(batch)}개 처리 중...", end='', flush=True)

            # Ask GPT to cluster this batch
            batch_clusters = await self._cluster_batch(batch)

            # Mark as processed
            for cluster in batch_clusters:
                for bid in cluster['belief_ids']:
                    processed.add(bid)

            clusters.extend(batch_clusters)

        print(f"\n  ✅ 전체 클러스터링 완료")

        return clusters

    async def _cluster_batch(self, batch: List[Dict]) -> List[Dict]:
        """
        Cluster a batch of beliefs
        """

        belief_list = "\n".join([
            f"{i+1}. [{b['id']}] {b['belief']} (빈도: {b['frequency']})"
            for i, b in enumerate(batch)
        ])

        prompt = f"""
다음은 DC Gallery 유저들의 "심층 믿음"들입니다.
이들 중 **의미가 유사한 것들을 그룹화**하고, 각 그룹의 **대표 문장**을 만드세요.

믿음 목록:
{belief_list}

**그룹화 기준:**
1. 핵심 메시지가 같으면 그룹화 (표현이 달라도)
   예: "민주당은 독재를 한다" + "민주당은 과거 독재정권과 같다" → 같은 그룹

2. 구체성 수준이 다르면 그룹화
   예: "좌파는 폭력적이다" + "극좌는 물리적 충돌을 선호한다" → 같은 그룹

3. 인과관계가 같으면 그룹화
   예: "작은 사찰이 독재로 발전" + "초기 권력남용이 전면 억압으로" → 같은 그룹

**대표 문장 작성 기준:**
- 가장 구체적이고 명확한 표현 선택
- 정치적 용어 유지 (민주당, 좌파 등)
- 원문의 뉘앙스 보존

JSON 형식:
{{
  "clusters": [
    {{
      "canonical_belief": "정규화된 믿음 (대표 문장)",
      "belief_ids": ["uuid1", "uuid2", ...],
      "reasoning": "왜 이들을 묶었는지 간단 설명"
    }}
  ]
}}

⚠️ 중요:
- 혼자만 있는 믿음도 클러스터 1개로 출력 (belief_ids에 자기 id만)
- 모든 입력 믿음이 결과에 정확히 1번씩 나타나야 함
"""

        response = await client.chat.completions.create(
            model="gpt-4o",  # 복잡한 작업이므로 gpt-4o 사용
            messages=[
                {"role": "system", "content": "You are an expert in discourse analysis and text clustering."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
            timeout=120.0  # 2분 타임아웃
        )

        result = json.loads(response.choices[0].message.content)

        # Calculate total frequency for each cluster
        clusters = []
        for cluster in result['clusters']:
            # Get beliefs in this cluster
            cluster_beliefs = [b for b in batch if b['id'] in cluster['belief_ids']]

            # Sum frequency
            total_freq = sum(b['frequency'] for b in cluster_beliefs)

            # Merge example_content_ids
            example_ids = []
            for b in cluster_beliefs:
                if b.get('example_content_ids'):
                    example_ids.extend(b['example_content_ids'])

            # Remove duplicates
            example_ids = list(set(example_ids))

            clusters.append({
                'canonical_belief': cluster['canonical_belief'],
                'belief_ids': cluster['belief_ids'],
                'total_frequency': total_freq,
                'example_content_ids': example_ids[:10]  # Keep max 10 examples
            })

        return clusters

    async def _update_clusters(self, clusters: List[Dict]) -> Dict:
        """
        Update belief_patterns table with cluster information

        Strategy:
        - Delete old individual beliefs
        - Insert new normalized beliefs
        """

        print(f"\n  기존 {len(clusters)}개 클러스터를 정규화된 믿음으로 변환...")

        # 1. Delete all existing beliefs
        self.supabase.table('belief_patterns').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print(f"  ✅ 기존 믿음 삭제 완료")

        # 2. Insert normalized beliefs
        normalized_beliefs = []

        for i, cluster in enumerate(clusters, 1):
            total_contents = len(self.supabase.table('layered_perceptions').select('id').execute().data)
            percentage = (cluster['total_frequency'] / total_contents * 100) if total_contents > 0 else 0

            normalized_beliefs.append({
                'belief': cluster['canonical_belief'],
                'frequency': cluster['total_frequency'],
                'percentage': round(percentage, 2),
                'example_content_ids': cluster['example_content_ids'],
                'cluster_id': None,  # Set to None instead of integer
                'cluster_name': f"cluster_{i}"
            })

        # Batch insert
        if normalized_beliefs:
            self.supabase.table('belief_patterns').insert(normalized_beliefs).execute()

        print(f"  ✅ {len(normalized_beliefs)}개 정규화된 믿음 저장 완료")

        # 3. Generate stats
        total_original = sum(len(c['belief_ids']) for c in clusters)
        reduction_rate = (1 - len(clusters) / total_original) * 100 if total_original > 0 else 0

        stats = {
            'original_count': total_original,
            'normalized_count': len(clusters),
            'reduction_rate': reduction_rate,
            'top_10': sorted(normalized_beliefs, key=lambda x: x['frequency'], reverse=True)[:10]
        }

        return stats

    async def show_normalization_preview(self, sample_size: int = 100):
        """
        Show a preview of what normalization would do (without saving)
        """

        beliefs = self.supabase.table('belief_patterns')\
            .select('id, belief, frequency')\
            .limit(sample_size)\
            .execute().data

        print(f"\n📊 정규화 미리보기 ({sample_size}개 샘플)")
        print("="*80)

        clusters = await self._cluster_beliefs(beliefs, batch_size=20)

        print(f"\n결과:")
        print(f"  원본: {len(beliefs)}개")
        print(f"  정규화 후: {len(clusters)}개")
        print(f"  축소율: {(1 - len(clusters)/len(beliefs)) * 100:.1f}%")

        print(f"\n상위 5개 클러스터:")
        top5 = sorted(clusters, key=lambda x: x['total_frequency'], reverse=True)[:5]
        for i, c in enumerate(top5, 1):
            print(f"\n{i}. {c['canonical_belief']}")
            print(f"   빈도: {c['total_frequency']}회")
            print(f"   통합된 믿음 수: {len(c['belief_ids'])}개")
