"""
Analysis Pipeline - Orchestrates the entire analysis flow
Content → Perception → Connection → (Future: Worldview)
"""

import logging
from typing import List, Dict
from uuid import UUID

from engines.collectors import ContentCollector
from engines.extractors.perception_extractor_simple import SimplePerceptionExtractor
from engines.detectors import ConnectionDetector
from engines.utils.supabase_client import get_supabase

logger = logging.getLogger(__name__)

class AnalysisPipeline:
    """Orchestrates the complete worldview analysis pipeline"""

    def __init__(self, use_simple_extractor: bool = False):
        """
        Initialize pipeline

        Args:
            use_simple_extractor: If True, use rule-based extractor (fallback for testing without API)
        """
        self.collector = ContentCollector()
        self.supabase = get_supabase()

        if use_simple_extractor:
            self.extractor = SimplePerceptionExtractor()
        else:
            # Use real OpenAI-based extractor
            from engines.extractors import PerceptionExtractor
            self.extractor = PerceptionExtractor()

        self.detector = ConnectionDetector()

    async def run_collection(
        self,
        source_type: str,
        **params
    ) -> Dict:
        """
        Run content collection phase

        Args:
            source_type: Type of source (e.g., 'dc_gallery')
            **params: Source-specific parameters

        Returns:
            Dictionary with results
        """
        logger.info(f"Starting collection from {source_type}")

        content_ids = await self.collector.collect(source_type, **params)

        logger.info(f"Collected {len(content_ids)} contents")

        return {
            'phase': 'collection',
            'source_type': source_type,
            'content_ids': content_ids,
            'count': len(content_ids)
        }

    async def run_extraction(
        self,
        content_ids: List[UUID]
    ) -> Dict:
        """
        Run perception extraction phase

        Args:
            content_ids: List of content UUIDs to process

        Returns:
            Dictionary with results
        """
        logger.info(f"Starting extraction for {len(content_ids)} contents")

        perception_map = {}  # content_id -> perception_ids
        all_perception_ids = []

        for content_id in content_ids:
            perception_ids = await self.extractor.extract(content_id)
            perception_map[str(content_id)] = perception_ids
            all_perception_ids.extend(perception_ids)

        logger.info(f"Extracted {len(all_perception_ids)} perceptions")

        return {
            'phase': 'extraction',
            'perception_map': perception_map,
            'perception_ids': all_perception_ids,
            'count': len(all_perception_ids)
        }

    async def run_connection(
        self,
        perception_ids: List[UUID]
    ) -> Dict:
        """
        Run connection detection phase

        Args:
            perception_ids: List of perception UUIDs to process

        Returns:
            Dictionary with results
        """
        logger.info(f"Starting connection detection for {len(perception_ids)} perceptions")

        connection_map = {}  # perception_id -> connection_ids
        all_connection_ids = []

        for perception_id in perception_ids:
            connection_ids = await self.detector.detect_connections(perception_id)
            connection_map[str(perception_id)] = connection_ids
            all_connection_ids.extend(connection_ids)

        # Deduplicate connections
        unique_connection_ids = list(set(all_connection_ids))

        logger.info(f"Detected {len(unique_connection_ids)} unique connections")

        return {
            'phase': 'connection',
            'connection_map': connection_map,
            'connection_ids': unique_connection_ids,
            'count': len(unique_connection_ids)
        }

    async def run_full_pipeline(
        self,
        source_type: str,
        **params
    ) -> Dict:
        """
        Run the complete pipeline: Collection → Extraction → Connection

        Args:
            source_type: Type of source (e.g., 'dc_gallery')
            **params: Source-specific parameters

        Returns:
            Complete results dictionary
        """
        logger.info("Starting full analysis pipeline")

        results = {
            'source_type': source_type,
            'params': params,
            'stages': {}
        }

        # Stage 1: Collection
        logger.info("=== Stage 1: Content Collection ===")
        collection_result = await self.run_collection(source_type, **params)
        results['stages']['collection'] = collection_result

        if not collection_result['content_ids']:
            logger.warning("No contents collected, stopping pipeline")
            return results

        # Stage 2: Extraction
        logger.info("=== Stage 2: Perception Extraction ===")
        extraction_result = await self.run_extraction(collection_result['content_ids'])
        results['stages']['extraction'] = extraction_result

        if not extraction_result['perception_ids']:
            logger.warning("No perceptions extracted, stopping pipeline")
            return results

        # Stage 3: Connection
        logger.info("=== Stage 3: Connection Detection ===")
        connection_result = await self.run_connection(extraction_result['perception_ids'])
        results['stages']['connection'] = connection_result

        # Summary
        results['summary'] = {
            'contents_collected': collection_result['count'],
            'perceptions_extracted': extraction_result['count'],
            'connections_detected': connection_result['count']
        }

        logger.info(f"Pipeline complete: {results['summary']}")

        return results

    async def get_pipeline_stats(self) -> Dict:
        """Get overall pipeline statistics"""
        try:
            # Count contents
            content_count = self.supabase.table('contents').select('id', count='exact').execute()

            # Count perceptions
            perception_count = self.supabase.table('perceptions').select('id', count='exact').execute()

            # Count connections
            connection_count = self.supabase.table('perception_connections').select('id', count='exact').execute()

            # Count worldviews (if any)
            worldview_count = self.supabase.table('worldviews').select('id', count='exact').execute()

            return {
                'total_contents': content_count.count,
                'total_perceptions': perception_count.count,
                'total_connections': connection_count.count,
                'total_worldviews': worldview_count.count
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
