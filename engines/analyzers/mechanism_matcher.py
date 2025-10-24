"""
MechanismMatcher - 메커니즘 기반 매칭

Perception을 Worldview에 연결
메커니즘 기반 매칭:
- Actor 일치 (50%)
- Mechanism 일치 (30%)
- Logic pattern 일치 (20%)

기존 임베딩 기반 매칭보다 정확하고 해석 가능
"""

import json
from typing import Dict, List, Tuple
from engines.utils.supabase_client import get_supabase


class MechanismMatcher:
    """Match perceptions to worldviews based on reasoning mechanisms"""

    def __init__(self):
        self.supabase = get_supabase()

    async def match_all_perceptions(self, threshold: float = 0.4) -> int:
        """
        Match all perceptions to worldviews

        Args:
            threshold: Minimum score to create a link (0-1)

        Returns:
            Number of links created
        """

        print("\n" + "="*80)
        print("메커니즘 기반 매칭 시작")
        print("="*80)

        # 1. Load all perceptions with reasoning structures
        perceptions = self.supabase.table('layered_perceptions')\
            .select('id, content_id, mechanisms, actor, logic_chain, consistency_pattern')\
            .not_.is_('mechanisms', 'null')\
            .execute().data

        perceptions = [p for p in perceptions if p.get('mechanisms') and len(p.get('mechanisms', [])) > 0]

        print(f"\n✅ {len(perceptions)}개 perception 로드")

        # 2. Load all active worldviews
        worldviews = self.supabase.table('worldviews')\
            .select('id, title, frame')\
            .neq('archived', True)\
            .execute().data

        print(f"✅ {len(worldviews)}개 worldview 로드")

        # 3. Clear existing links (for re-matching)
        print("\n기존 links 삭제 중...")
        self.supabase.table('perception_worldview_links').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()

        # 4. Match each perception
        print(f"\n매칭 시작 (threshold={threshold})...")

        links_created = 0

        for i, perception in enumerate(perceptions):
            matches = await self._find_matches(perception, worldviews, threshold)

            for match in matches:
                await self._create_link(
                    perception['id'],
                    match['worldview_id'],
                    match['score']
                )
                links_created += 1

            if (i + 1) % 50 == 0:
                print(f"  진행: {i+1}/{len(perceptions)} ({links_created} links)")

        print(f"\n✅ {links_created}개 링크 생성 완료")
        print(f"   평균: {links_created/len(perceptions):.2f} links/perception")

        # 5. Update worldview statistics
        await self._update_worldview_stats(worldviews)

        return links_created

    async def match_single_perception(self, perception_id: str, threshold: float = 0.4) -> List[str]:
        """
        Match a single perception to worldviews

        Args:
            perception_id: UUID of perception
            threshold: Minimum score to create a link

        Returns:
            List of matched worldview IDs
        """

        # Load perception
        perception = self.supabase.table('layered_perceptions')\
            .select('id, content_id, mechanisms, actor, logic_chain, consistency_pattern')\
            .eq('id', perception_id)\
            .execute().data

        if not perception:
            raise ValueError(f"Perception {perception_id} not found")

        perception = perception[0]

        # Load worldviews
        worldviews = self.supabase.table('worldviews')\
            .select('id, title, frame')\
            .neq('archived', True)\
            .execute().data

        # Find matches
        matches = await self._find_matches(perception, worldviews, threshold)

        # Create links
        matched_worldview_ids = []
        for match in matches:
            await self._create_link(
                perception['id'],
                match['worldview_id'],
                match['score']
            )
            matched_worldview_ids.append(match['worldview_id'])

        return matched_worldview_ids

    async def _find_matches(self, perception: Dict, worldviews: List[Dict], threshold: float) -> List[Dict]:
        """
        Find matching worldviews for a perception

        Args:
            perception: Perception dict
            worldviews: List of worldview dicts
            threshold: Minimum score

        Returns:
            List of matches with scores
        """

        matches = []

        for wv in worldviews:
            score = self._calculate_match_score(perception, wv)

            if score >= threshold:
                matches.append({
                    'worldview_id': wv['id'],
                    'worldview_title': wv['title'],
                    'score': score
                })

        # Sort by score (descending)
        matches.sort(key=lambda x: x['score'], reverse=True)

        # Return top 3 matches
        return matches[:3]

    def _calculate_match_score(self, perception: Dict, worldview: Dict) -> float:
        """
        Calculate match score between perception and worldview

        Claude 실험 결과: Mechanism 중심 가중치 추천
        - 일반: Actor 50%, Mechanism 30%, Logic 20%
        - 극단적 사건: Actor 30%, Mechanism 50%, Logic 20% (Mechanism 중심)

        Returns:
            Score between 0 and 1
        """

        # Parse worldview frame
        try:
            frame = json.loads(worldview.get('frame', '{}'))
        except:
            # Old format worldview
            return 0.0

        # 1. Actor matching
        actor_score = self._match_actor(perception, frame)

        # 2. Mechanism matching
        mechanism_score = self._match_mechanisms(perception, frame)

        # 3. Logic pattern matching
        logic_score = self._match_logic_pattern(perception, frame)

        # Adaptive weighting (Claude 실험 기반)
        # 메커니즘이 많을수록 Mechanism 중심 가중치 사용
        num_mechanisms = len(perception.get('mechanisms', []))
        if num_mechanisms >= 4:
            # 극단적 사건 (많은 메커니즘) → Mechanism 중심
            total_score = 0.3 * actor_score + 0.5 * mechanism_score + 0.2 * logic_score
        else:
            # 일반적 경우 → Actor 중심
            total_score = 0.5 * actor_score + 0.3 * mechanism_score + 0.2 * logic_score

        return total_score

    def _match_actor(self, perception: Dict, frame: Dict) -> float:
        """
        Match actor field

        Returns:
            1.0 if actors match, 0.0 otherwise
        """

        perception_actor = perception.get('actor', {}).get('subject', '')

        # Handle both dict and string format for worldview actor
        worldview_actor_data = frame.get('actor', '')
        if isinstance(worldview_actor_data, dict):
            worldview_actor = worldview_actor_data.get('subject', '')
        else:
            worldview_actor = worldview_actor_data

        if not perception_actor or not worldview_actor:
            return 0.0

        # Extract keywords from worldview actor
        # e.g., "중국/좌파 세력" → ["중국", "좌파", "세력"]
        actor_keywords = []
        for part in worldview_actor.replace('/', ' ').replace('(', ' ').replace(')', ' ').replace('·', ' ').replace(',', ' ').split():
            if part.strip():
                actor_keywords.append(part.strip())

        # Check if any keyword is in perception actor
        for keyword in actor_keywords:
            if keyword in perception_actor:
                return 1.0

        # Partial match for similar terms
        similar_pairs = [
            ('민주', '민주당'),
            ('좌파', '진보'),
            ('중국', '중국계'),
            ('경찰', '공권력'),
            ('정부', '정권'),
            ('언론', '미디어')
        ]

        for term1, term2 in similar_pairs:
            if (term1 in perception_actor and term2 in worldview_actor) or \
               (term2 in perception_actor and term1 in worldview_actor):
                return 0.8

        return 0.0

    def _match_mechanisms(self, perception: Dict, frame: Dict) -> float:
        """
        Match mechanisms

        Returns:
            Ratio of matching mechanisms (0-1)
        """

        perception_mechs = set(perception.get('mechanisms', []))
        worldview_mechs = set(frame.get('core_mechanisms', []))

        if not perception_mechs or not worldview_mechs:
            return 0.0

        # Intersection over union
        intersection = perception_mechs & worldview_mechs
        union = perception_mechs | worldview_mechs

        return len(intersection) / len(union) if union else 0.0

    def _match_logic_pattern(self, perception: Dict, frame: Dict) -> float:
        """
        Match logic pattern

        Returns:
            Score based on logic chain similarity (0-1)
        """

        perception_chain = perception.get('logic_chain', [])
        worldview_pattern = frame.get('logic_pattern', {})

        if not perception_chain or not worldview_pattern:
            return 0.0

        # Convert to text for matching
        perception_text = ' '.join(perception_chain)
        worldview_text = (
            worldview_pattern.get('trigger', '') + ' ' +
            worldview_pattern.get('conclusion', '')
        )

        # Simple keyword overlap
        perception_keywords = set(perception_text.split())
        worldview_keywords = set(worldview_text.split())

        if not perception_keywords or not worldview_keywords:
            return 0.0

        intersection = perception_keywords & worldview_keywords
        union = perception_keywords | worldview_keywords

        return len(intersection) / len(union) if union else 0.0

    async def _create_link(self, perception_id: str, worldview_id: str, score: float):
        """Create perception_worldview_link"""

        link_data = {
            'perception_id': perception_id,
            'worldview_id': worldview_id,
            'relevance_score': score
        }

        try:
            self.supabase.table('perception_worldview_links').insert(link_data).execute()
        except Exception as e:
            # Ignore duplicate errors
            if 'duplicate' not in str(e).lower():
                print(f"  ⚠️  Link 생성 실패: {e}")

    async def _update_worldview_stats(self, worldviews: List[Dict]):
        """Update worldview statistics (total_perceptions count)"""

        print("\n세계관 통계 업데이트 중...")

        for wv in worldviews:
            # Count links
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

            if count > 0:
                print(f"  {wv['title'][:60]}: {count}개")
