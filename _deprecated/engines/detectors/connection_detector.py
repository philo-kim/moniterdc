"""
Connection Detector - Detects connections between perceptions
Temporal, Causal, Thematic, Social connections
"""

import logging
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime, timedelta

from engines.utils.supabase_client import get_supabase

logger = logging.getLogger(__name__)

class ConnectionDetector:
    """Detects and creates connections between perceptions"""

    def __init__(self):
        self.supabase = get_supabase()

        # Similarity threshold for vector search
        self.similarity_threshold = 0.7

    async def detect_connections(self, perception_id: UUID) -> List[UUID]:
        """
        Detect connections for a given perception

        Args:
            perception_id: UUID of the perception to analyze

        Returns:
            List of created connection UUIDs
        """
        try:
            # Fetch the perception
            response = self.supabase.table('perceptions').select('*').eq('id', str(perception_id)).execute()

            if not response.data:
                logger.error(f"Perception not found: {perception_id}")
                return []

            perception = response.data[0]

            connection_ids = []

            # Detect temporal connections
            temporal_conns = await self._detect_temporal(perception)
            connection_ids.extend(temporal_conns)

            # Detect thematic connections (same subject)
            thematic_conns = await self._detect_thematic(perception)
            connection_ids.extend(thematic_conns)

            # Detect semantic connections (vector similarity)
            semantic_conns = await self._detect_semantic(perception)
            connection_ids.extend(semantic_conns)

            logger.info(f"Detected {len(connection_ids)} connections for perception {perception_id}")
            return connection_ids

        except Exception as e:
            logger.error(f"Error detecting connections: {e}")
            return []

    async def _detect_temporal(self, perception: Dict) -> List[UUID]:
        """Detect temporal connections (perceptions within 7 days)"""
        try:
            perception_id = perception['id']
            created_at = datetime.fromisoformat(perception['created_at'].replace('Z', '+00:00'))

            # Find perceptions within 7 days
            time_window_start = created_at - timedelta(days=7)
            time_window_end = created_at + timedelta(days=7)

            response = self.supabase.table('perceptions')\
                .select('id')\
                .neq('id', perception_id)\
                .gte('created_at', time_window_start.isoformat())\
                .lte('created_at', time_window_end.isoformat())\
                .limit(50)\
                .execute()

            connection_ids = []
            for related in response.data:
                conn_id = await self._create_connection(
                    from_id=perception_id,
                    to_id=related['id'],
                    connection_type='temporal',
                    strength=0.5
                )
                if conn_id:
                    connection_ids.append(conn_id)

            return connection_ids

        except Exception as e:
            logger.error(f"Error detecting temporal connections: {e}")
            return []

    async def _detect_thematic(self, perception: Dict) -> List[UUID]:
        """Detect thematic connections (same subject)"""
        try:
            perception_id = perception['id']
            subject = perception['perceived_subject']

            # Find perceptions with same subject
            response = self.supabase.table('perceptions')\
                .select('id')\
                .eq('perceived_subject', subject)\
                .neq('id', perception_id)\
                .limit(20)\
                .execute()

            connection_ids = []
            for related in response.data:
                conn_id = await self._create_connection(
                    from_id=perception_id,
                    to_id=related['id'],
                    connection_type='thematic',
                    strength=0.7
                )
                if conn_id:
                    connection_ids.append(conn_id)

            return connection_ids

        except Exception as e:
            logger.error(f"Error detecting thematic connections: {e}")
            return []

    async def _detect_semantic(self, perception: Dict) -> List[UUID]:
        """Detect semantic connections (vector similarity)"""
        try:
            perception_id = perception['id']
            embedding = perception.get('perception_embedding')

            if not embedding:
                return []

            # Use RPC function for vector similarity search
            response = self.supabase.rpc(
                'search_similar_perceptions',
                {
                    'query_embedding': embedding,
                    'similarity_threshold': self.similarity_threshold,
                    'max_results': 10
                }
            ).execute()

            connection_ids = []
            for related in response.data:
                # Skip self
                if related['id'] == perception_id:
                    continue

                conn_id = await self._create_connection(
                    from_id=perception_id,
                    to_id=related['id'],
                    connection_type='semantic',
                    strength=related.get('similarity', 0.8)
                )
                if conn_id:
                    connection_ids.append(conn_id)

            return connection_ids

        except Exception as e:
            logger.error(f"Error detecting semantic connections: {e}")
            return []

    async def _create_connection(
        self,
        from_id: str,
        to_id: str,
        connection_type: str,
        strength: float
    ) -> Optional[UUID]:
        """Create a connection between two perceptions"""
        try:
            # Check if connection already exists
            existing = self.supabase.table('perception_connections')\
                .select('id')\
                .eq('from_perception_id', from_id)\
                .eq('to_perception_id', to_id)\
                .eq('connection_type', connection_type)\
                .execute()

            if existing.data:
                return None  # Already exists

            # Create new connection
            connection_data = {
                'from_perception_id': from_id,
                'to_perception_id': to_id,
                'connection_type': connection_type,
                'strength': strength,
                'detected_by': 'auto'
            }

            response = self.supabase.table('perception_connections').insert(connection_data).execute()

            if response.data:
                conn_id = response.data[0]['id']
                logger.info(f"Created {connection_type} connection: {conn_id}")
                return UUID(conn_id)

            return None

        except Exception as e:
            logger.error(f"Error creating connection: {e}")
            return None
