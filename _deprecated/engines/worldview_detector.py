"""
Worldview Detector - Layer 3 Engine
Detects worldview patterns from connected perceptions
"""

import logging
from typing import Dict, List, Optional, Set
from uuid import UUID
from datetime import datetime, timedelta
from collections import defaultdict
import json

from openai import AsyncOpenAI
import os

from engines.utils.supabase_client import get_supabase
from engines.utils.embedding_utils import EmbeddingGenerator
from engines.analyzers.mechanism_analyzer import MechanismAnalyzer

logger = logging.getLogger(__name__)

class WorldviewDetector:
    """Detects worldview patterns from perception clusters"""

    def __init__(self):
        self.supabase = get_supabase()
        self.openai = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.embedding_generator = EmbeddingGenerator()
        self.mechanism_analyzer = MechanismAnalyzer()

        # Minimum perceptions to form a worldview
        self.min_perceptions = 3

        # Minimum connection strength
        self.min_connection_strength = 0.5

    async def detect_worldviews(self) -> List[UUID]:
        """
        Detect all worldview patterns from existing perceptions

        Returns:
            List of created worldview UUIDs
        """
        logger.info("Starting worldview detection...")

        # Step 1: Find perception clusters
        clusters = await self._find_perception_clusters()
        logger.info(f"Found {len(clusters)} perception clusters")

        # Step 2: Analyze each cluster for worldview patterns
        worldview_ids = []
        for i, cluster in enumerate(clusters, 1):
            logger.info(f"Analyzing cluster {i}/{len(clusters)} ({len(cluster)} perceptions)")

            worldview_id = await self._analyze_cluster(cluster)
            if worldview_id:
                worldview_ids.append(worldview_id)

        logger.info(f"Detected {len(worldview_ids)} worldviews")
        return worldview_ids

    async def _find_perception_clusters(self) -> List[List[str]]:
        """
        Find clusters of connected perceptions using graph traversal

        Returns:
            List of perception ID clusters
        """
        # Get all perceptions
        response = self.supabase.table('perceptions').select('id').execute()
        all_perception_ids = [p['id'] for p in response.data]

        # Build adjacency list from connections
        adjacency = defaultdict(set)

        response = self.supabase.table('perception_connections')\
            .select('from_perception_id, to_perception_id, strength')\
            .gte('strength', self.min_connection_strength)\
            .execute()

        for conn in response.data:
            from_id = conn['from_perception_id']
            to_id = conn['to_perception_id']
            adjacency[from_id].add(to_id)
            adjacency[to_id].add(from_id)  # Bidirectional

        # Find connected components using BFS
        visited = set()
        clusters = []

        def bfs(start_id):
            cluster = []
            queue = [start_id]
            visited.add(start_id)

            while queue:
                current_id = queue.pop(0)
                cluster.append(current_id)

                for neighbor_id in adjacency[current_id]:
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        queue.append(neighbor_id)

            return cluster

        for perception_id in all_perception_ids:
            if perception_id not in visited:
                cluster = bfs(perception_id)
                if len(cluster) >= self.min_perceptions:
                    clusters.append(cluster)

        return clusters

    async def _analyze_cluster(self, perception_ids: List[str]) -> Optional[UUID]:
        """
        Analyze a perception cluster to detect worldview pattern

        Args:
            perception_ids: List of perception IDs in the cluster

        Returns:
            Created worldview UUID or None
        """
        try:
            # Fetch all perceptions in cluster
            response = self.supabase.table('perceptions')\
                .select('*')\
                .in_('id', perception_ids)\
                .execute()

            perceptions = response.data

            if not perceptions:
                return None

            # Extract patterns using GPT-4
            worldview_data = await self._extract_worldview_pattern(perceptions)

            if not worldview_data:
                return None

            # Check if worldview already exists
            should_update, existing_id = await self.should_update_vs_create(
                worldview_data['core_subject'],
                worldview_data['frame'],
                perceptions
            )

            if should_update and existing_id:
                # Update existing worldview
                logger.info(f"Updating existing worldview {existing_id}")
                success = await self.update_worldview(existing_id, perception_ids)
                return existing_id if success else None

            # Calculate strengths
            strengths = await self._calculate_strengths(perceptions, perception_ids)

            # Analyze mechanisms
            mechanisms = self.mechanism_analyzer.analyze_mechanisms(perceptions)

            # Save worldview to database
            worldview_id = await self._save_worldview(
                perception_ids,
                perceptions,
                worldview_data,
                strengths,
                mechanisms
            )

            return worldview_id

        except Exception as e:
            logger.error(f"Error analyzing cluster: {e}")
            return None

    async def _extract_worldview_pattern(self, perceptions: List[Dict]) -> Optional[Dict]:
        """
        Use GPT-4 to extract worldview pattern from perceptions

        Args:
            perceptions: List of perception dictionaries

        Returns:
            Worldview pattern data
        """
        try:
            # Prepare perception summary for GPT
            perception_summary = []
            for p in perceptions:
                perception_summary.append({
                    'subject': p['perceived_subject'],
                    'attribute': p['perceived_attribute'],
                    'valence': p['perceived_valence'],
                    'claims': p['claims'],
                    'keywords': p['keywords']
                })

            prompt = f"""다음은 정치 콘텐츠에서 추출된 연결된 인식들입니다. 이 인식들이 형성하는 세계관(worldview)을 분석하세요.

인식들:
{json.dumps(perception_summary, ensure_ascii=False, indent=2)}

다음 정보를 JSON 형식으로 추출하세요:

1. **title**: 이 세계관을 한 문장으로 요약
2. **frame**: 핵심 프레임 (예: "민주당 = 친중 매국 세력")
3. **core_subject**: 핵심 대상
4. **core_attributes**: 핵심 속성들 (배열)
5. **narrative**: 이 세계관이 말하는 이야기 (2-3 문장)

응답 형식:
{{
  "title": "...",
  "frame": "...",
  "core_subject": "...",
  "core_attributes": ["...", "..."],
  "narrative": "..."
}}"""

            response = await self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 정치 담론 분석 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1000
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.error(f"Error extracting worldview pattern: {e}")
            return None

    async def _calculate_strengths(
        self,
        perceptions: List[Dict],
        perception_ids: List[str]
    ) -> Dict[str, float]:
        """
        Calculate worldview strength metrics

        Args:
            perceptions: List of perceptions
            perception_ids: List of perception IDs

        Returns:
            Dictionary of strength scores
        """
        # 1. Cognitive Strength: 인식의 일관성
        cognitive_strength = self._calculate_cognitive_strength(perceptions)

        # 2. Temporal Strength: 시간적 지속성
        temporal_strength = await self._calculate_temporal_strength(perceptions)

        # 3. Social Strength: 다양한 소스
        social_strength = await self._calculate_social_strength(perceptions)

        # 4. Structural Strength: 연결 강도
        structural_strength = await self._calculate_structural_strength(perception_ids)

        # Overall strength
        overall = (
            cognitive_strength * 0.3 +
            temporal_strength * 0.2 +
            social_strength * 0.2 +
            structural_strength * 0.3
        )

        return {
            'cognitive': cognitive_strength,
            'temporal': temporal_strength,
            'social': social_strength,
            'structural': structural_strength,
            'overall': overall
        }

    def _calculate_cognitive_strength(self, perceptions: List[Dict]) -> float:
        """Calculate cognitive consistency strength"""
        if not perceptions:
            return 0.0

        # Count consistent subjects and valences
        subjects = [p['perceived_subject'] for p in perceptions]
        valences = [p['perceived_valence'] for p in perceptions]

        if not subjects or not valences:
            return 0.0

        # Most common subject
        subject_counts = defaultdict(int)
        for s in subjects:
            subject_counts[s] += 1

        max_subject_count = max(subject_counts.values()) if subject_counts else 0
        subject_consistency = max_subject_count / len(subjects) if len(subjects) > 0 else 0

        # Valence consistency
        valence_counts = defaultdict(int)
        for v in valences:
            valence_counts[v] += 1

        max_valence_count = max(valence_counts.values()) if valence_counts else 0
        valence_consistency = max_valence_count / len(valences) if len(valences) > 0 else 0

        return (subject_consistency + valence_consistency) / 2

    async def _calculate_temporal_strength(self, perceptions: List[Dict]) -> float:
        """Calculate temporal persistence strength"""
        if not perceptions:
            return 0.0

        # Get content creation times
        content_ids = [p['content_id'] for p in perceptions]
        response = self.supabase.table('contents')\
            .select('created_at')\
            .in_('id', content_ids)\
            .execute()

        if not response.data:
            return 0.0

        dates = [datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) for c in response.data]
        dates.sort()

        # Calculate time span
        time_span = (dates[-1] - dates[0]).days

        # More days = stronger temporal persistence
        # Max out at 30 days
        strength = min(time_span / 30.0, 1.0)

        return strength

    async def _calculate_social_strength(self, perceptions: List[Dict]) -> float:
        """Calculate social spread strength (source diversity)"""
        if not perceptions:
            return 0.0

        # Count unique sources
        content_ids = [p['content_id'] for p in perceptions]
        response = self.supabase.table('contents')\
            .select('source_type, source_id')\
            .in_('id', content_ids)\
            .execute()

        if not response.data:
            return 0.0

        unique_sources = len(set(c['source_id'] for c in response.data))

        # More unique sources = stronger social spread
        # Normalize (assume max 10 sources)
        strength = min(unique_sources / 10.0, 1.0)

        return strength

    async def _calculate_structural_strength(self, perception_ids: List[str]) -> float:
        """Calculate structural strength (connection density)"""
        if len(perception_ids) < 2:
            return 0.0

        # Count connections within this cluster
        response = self.supabase.table('perception_connections')\
            .select('strength')\
            .in_('from_perception_id', perception_ids)\
            .in_('to_perception_id', perception_ids)\
            .execute()

        if not response.data:
            return 0.0

        # Calculate average connection strength
        avg_strength = sum(float(c['strength']) for c in response.data) / len(response.data)

        # Calculate density (actual connections / possible connections)
        actual_connections = len(response.data)
        possible_connections = len(perception_ids) * (len(perception_ids) - 1) / 2
        density = actual_connections / possible_connections if possible_connections > 0 else 0

        return (avg_strength + density) / 2

    async def _save_worldview(
        self,
        perception_ids: List[str],
        perceptions: List[Dict],
        worldview_data: Dict,
        strengths: Dict[str, float],
        mechanisms: Dict
    ) -> Optional[UUID]:
        """Save worldview to database"""
        try:
            import math

            # Check for NaN values in strengths
            for key, value in strengths.items():
                if math.isnan(value) or math.isinf(value):
                    logger.warning(f"Invalid strength value for {key}: {value}, setting to 0")
                    strengths[key] = 0.0

            # Determine overall valence from perceptions
            valence_counts = defaultdict(int)
            for p in perceptions:
                valence_counts[p['perceived_valence']] += 1

            overall_valence = max(valence_counts.items(), key=lambda x: x[1])[0] if valence_counts else 'neutral'

            # Generate embedding for worldview
            embedding_text = f"{worldview_data['title']} {worldview_data['frame']} {worldview_data.get('narrative', '')}"
            embedding = await self.embedding_generator.generate(embedding_text)

            # Prepare worldview record
            worldview_record = {
                'title': worldview_data['title'],
                'frame': worldview_data['frame'],
                'core_subject': worldview_data['core_subject'],
                'core_attributes': worldview_data['core_attributes'],
                'overall_valence': overall_valence,
                'perception_ids': perception_ids,
                'strength_cognitive': strengths['cognitive'],
                'strength_temporal': strengths['temporal'],
                'strength_social': strengths['social'],
                'strength_structural': strengths['structural'],
                'strength_overall': strengths['overall'],
                'worldview_embedding': embedding,
                'total_perceptions': len(perception_ids),
                'formation_phases': mechanisms.get('formation_phases', []),
                'cognitive_mechanisms': mechanisms.get('cognitive_mechanisms', []),
                'structural_flaws': mechanisms.get('structural_flaws', [])
            }

            response = self.supabase.table('worldviews').insert(worldview_record).execute()

            if response.data:
                worldview_id = UUID(response.data[0]['id'])
                logger.info(f"Saved worldview: {worldview_id} - {worldview_data['title']}")

                # Record initial strength snapshot
                await self.record_strength_snapshot(worldview_id)

                # Set initial trend
                await self.update_worldview_trend(worldview_id)

                return worldview_id

            return None

        except Exception as e:
            logger.error(f"Error saving worldview: {e}")
            return None

    async def get_worldview_stats(self) -> Dict:
        """Get worldview statistics"""
        try:
            response = self.supabase.table('worldviews').select('*').execute()

            if not response.data:
                return {'total': 0}

            worldviews = response.data

            return {
                'total': len(worldviews),
                'avg_strength': sum(w['strength_overall'] for w in worldviews) / len(worldviews),
                'by_subject': self._group_by_subject(worldviews),
                'strongest': max(worldviews, key=lambda w: w['strength_overall'])['title']
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

    def _group_by_subject(self, worldviews: List[Dict]) -> Dict[str, int]:
        """Group worldviews by core subject"""
        counts = defaultdict(int)
        for w in worldviews:
            counts[w['core_subject']] += 1
        return dict(counts)

    async def find_existing_worldview(self, subject: str, frame: str = None) -> Optional[Dict]:
        """
        Find existing worldview for subject (and optionally frame)

        Args:
            subject: Core subject to search for
            frame: Optional frame to match

        Returns:
            Worldview dict if found, None otherwise
        """
        try:
            query = self.supabase.table('worldviews')\
                .select('*')\
                .eq('core_subject', subject)

            if frame:
                query = query.eq('frame', frame)

            response = query.execute()

            if response.data and len(response.data) > 0:
                # Return most recent worldview if multiple exist
                return sorted(response.data, key=lambda w: w['updated_at'], reverse=True)[0]

            return None

        except Exception as e:
            logger.error(f"Error finding existing worldview: {e}")
            return None

    async def update_worldview(self, worldview_id: UUID, new_perception_ids: List[str]) -> bool:
        """
        Update existing worldview with new perceptions

        Args:
            worldview_id: Worldview to update
            new_perception_ids: New perception IDs to add

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing worldview
            response = self.supabase.table('worldviews')\
                .select('*')\
                .eq('id', str(worldview_id))\
                .execute()

            if not response.data:
                logger.error(f"Worldview {worldview_id} not found")
                return False

            worldview = response.data[0]
            existing_ids = worldview.get('perception_ids', [])

            # Combine perception IDs (avoid duplicates)
            all_perception_ids = list(set(existing_ids + new_perception_ids))

            # Fetch all perceptions
            perceptions_response = self.supabase.table('perceptions')\
                .select('*')\
                .in_('id', all_perception_ids)\
                .execute()

            if not perceptions_response.data:
                logger.error("No perceptions found")
                return False

            perceptions = perceptions_response.data

            # Recalculate strengths
            strengths = await self._calculate_strengths(perceptions, all_perception_ids)

            # Recalculate mechanisms
            mechanisms = self.mechanism_analyzer.analyze_mechanisms(perceptions)

            # Clean NaN values from strengths
            import math
            for key in ['cognitive', 'temporal', 'social', 'structural', 'overall']:
                if math.isnan(strengths[key]) or math.isinf(strengths[key]):
                    logger.warning(f"Invalid strength value for {key}: {strengths[key]}, setting to 0")
                    strengths[key] = 0.0

            # Update worldview record
            update_data = {
                'perception_ids': all_perception_ids,
                'total_perceptions': len(all_perception_ids),
                'strength_cognitive': strengths['cognitive'],
                'strength_temporal': strengths['temporal'],
                'strength_social': strengths['social'],
                'strength_structural': strengths['structural'],
                'strength_overall': strengths['overall'],
                'formation_phases': mechanisms.get('formation_phases', []),
                'cognitive_mechanisms': mechanisms.get('cognitive_mechanisms', []),
                'structural_flaws': mechanisms.get('structural_flaws', []),
                'updated_at': datetime.now().isoformat()
            }

            response = self.supabase.table('worldviews')\
                .update(update_data)\
                .eq('id', str(worldview_id))\
                .execute()

            if response.data:
                logger.info(f"Updated worldview {worldview_id}: {len(existing_ids)} → {len(all_perception_ids)} perceptions")

                # Record strength snapshot for trend analysis
                await self.record_strength_snapshot(worldview_id)

                # Update trend
                await self.update_worldview_trend(worldview_id)

                return True

            return False

        except Exception as e:
            logger.error(f"Error updating worldview: {e}")
            return False

    async def should_update_vs_create(self, subject: str, frame: str, new_perceptions: List[Dict]) -> tuple[bool, Optional[UUID]]:
        """
        Decide whether to update existing worldview or create new one

        Args:
            subject: Core subject
            frame: Frame
            new_perceptions: New perceptions to add

        Returns:
            (should_update, worldview_id_if_exists)
        """
        try:
            # Find existing worldview with same subject and frame
            existing = await self.find_existing_worldview(subject, frame)

            if not existing:
                return (False, None)

            # If worldview exists with same frame, update it
            return (True, UUID(existing['id']))

        except Exception as e:
            logger.error(f"Error in should_update_vs_create: {e}")
            return (False, None)

    async def record_strength_snapshot(self, worldview_id: UUID) -> bool:
        """
        Record current strength snapshot for trend analysis

        Args:
            worldview_id: Worldview to record

        Returns:
            True if successful
        """
        try:
            # Get current worldview state
            response = self.supabase.table('worldviews')\
                .select('*')\
                .eq('id', str(worldview_id))\
                .execute()

            if not response.data:
                return False

            worldview = response.data[0]

            # Record snapshot
            snapshot_data = {
                'worldview_id': str(worldview_id),
                'strength_cognitive': worldview['strength_cognitive'],
                'strength_temporal': worldview['strength_temporal'],
                'strength_social': worldview['strength_social'],
                'strength_structural': worldview['strength_structural'],
                'strength_overall': worldview['strength_overall'],
                'perception_count': worldview['total_perceptions'],
                'content_count': worldview['total_contents']
            }

            response = self.supabase.table('worldview_strength_history')\
                .insert(snapshot_data)\
                .execute()

            return bool(response.data)

        except Exception as e:
            logger.error(f"Error recording strength snapshot: {e}")
            return False

    async def calculate_trend(self, worldview_id: UUID) -> str:
        """
        Calculate worldview trend based on strength history

        Args:
            worldview_id: Worldview to analyze

        Returns:
            Trend: 'rising', 'stable', 'falling', 'dead'
        """
        try:
            # Get strength history (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()

            response = self.supabase.table('worldview_strength_history')\
                .select('*')\
                .eq('worldview_id', str(worldview_id))\
                .gte('recorded_at', thirty_days_ago)\
                .order('recorded_at', desc=False)\
                .execute()

            if not response.data or len(response.data) < 2:
                # Not enough history, check current strength
                worldview_response = self.supabase.table('worldviews')\
                    .select('strength_overall')\
                    .eq('id', str(worldview_id))\
                    .execute()

                if worldview_response.data:
                    current_strength = worldview_response.data[0]['strength_overall']
                    if current_strength >= 0.6:
                        return 'stable'
                    elif current_strength >= 0.3:
                        return 'falling'
                    else:
                        return 'dead'

                return 'dead'

            history = response.data

            # Calculate trend from first to last measurement
            first_strength = history[0]['strength_overall']
            last_strength = history[-1]['strength_overall']
            change = last_strength - first_strength

            # Calculate recent rate of change (last week)
            recent_history = [h for h in history if h['recorded_at'] >= (datetime.now() - timedelta(days=7)).isoformat()]
            if len(recent_history) >= 2:
                recent_change = recent_history[-1]['strength_overall'] - recent_history[0]['strength_overall']
            else:
                recent_change = change

            # Determine trend
            if last_strength < 0.1:
                return 'dead'
            elif recent_change > 0.1:  # Significant recent increase
                return 'rising'
            elif recent_change < -0.1:  # Significant recent decrease
                return 'falling'
            elif abs(change) < 0.05 and last_strength >= 0.3:  # Stable over time
                return 'stable'
            elif change > 0.05:  # Overall increase
                return 'rising'
            elif change < -0.05:  # Overall decrease
                return 'falling'
            else:
                return 'stable'

        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return 'stable'

    async def update_worldview_trend(self, worldview_id: UUID) -> bool:
        """
        Update worldview with calculated trend

        Args:
            worldview_id: Worldview to update

        Returns:
            True if successful
        """
        try:
            # Calculate trend
            trend = await self.calculate_trend(worldview_id)

            # Update worldview
            response = self.supabase.table('worldviews')\
                .update({'trend': trend, 'updated_at': datetime.now().isoformat()})\
                .eq('id', str(worldview_id))\
                .execute()

            if response.data:
                logger.info(f"Updated worldview {worldview_id} trend: {trend}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error updating worldview trend: {e}")
            return False
