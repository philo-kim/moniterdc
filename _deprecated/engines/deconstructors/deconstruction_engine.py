#!/usr/bin/env python3
"""
DeconstructionEngine - 세계관 해체 엔진

FlawDetector + CounterNarrativeGenerator를 통합하여
완전한 해체 전략 생성 및 DB 저장
"""

from typing import Dict, Optional
from uuid import UUID
from datetime import datetime
from engines.utils.supabase_client import get_supabase
from engines.utils.logger import get_logger
from .flaw_detector import FlawDetector
from .counter_narrative_generator import CounterNarrativeGenerator

logger = get_logger(__name__)


class DeconstructionEngine:
    """
    Complete deconstruction engine

    Workflow:
    1. Detect structural flaws
    2. Generate counter-narrative
    3. Save to worldviews.deconstruction field
    4. Optionally save to rebuttals table
    """

    def __init__(self):
        self.supabase = get_supabase()
        self.flaw_detector = FlawDetector()
        self.counter_generator = CounterNarrativeGenerator()

    async def deconstruct(self, worldview_id: str, save_to_db: bool = True) -> Dict:
        """
        Perform complete deconstruction of a worldview

        Args:
            worldview_id: Worldview UUID
            save_to_db: Whether to save result to database

        Returns:
            Complete deconstruction dict
        """
        try:
            logger.info(f"Starting deconstruction for worldview {worldview_id}")

            # 1. Get worldview
            response = self.supabase.table('worldviews')\
                .select('*')\
                .eq('id', worldview_id)\
                .execute()

            if not response.data:
                logger.error(f"Worldview {worldview_id} not found")
                return {}

            worldview = response.data[0]

            # 2. Use existing analysis from worldview
            # (causal_chains, opposition_framework, emotional_logic, implicit_assumptions)

            # Extract flaws from implicit_assumptions
            logger.info("Extracting structural flaws...")
            existing_deconstruction = worldview.get('deconstruction', {})
            flaws = [
                {
                    'type': 'implicit_assumption',
                    'description': assumption.get('assumption', ''),
                    'evidence': assumption.get('evidence', ''),
                    'impact': assumption.get('impact', '')
                }
                for assumption in worldview.get('structural_flaws', [])
            ]

            # 3. Generate counter-narrative based on worldview data
            logger.info("Generating counter-narrative...")
            counter_narrative = await self.counter_generator.generate_from_worldview(
                worldview
            )

            # 4. Build complete deconstruction
            deconstruction = {
                'flaws': flaws,
                'counter_narrative': counter_narrative.get('counter_narrative', ''),
                'key_rebuttals': counter_narrative.get('key_rebuttals', []),
                'suggested_response': counter_narrative.get('suggested_response', ''),
                'evidence_needed': counter_narrative.get('evidence_needed', []),
                'action_guide': counter_narrative.get('action_guide', {}),
                'generated_at': datetime.now().isoformat()
            }

            # 5. Save to database
            if save_to_db:
                await self._save_deconstruction(worldview_id, deconstruction)

            logger.info(f"Deconstruction complete for {worldview.get('title')}")
            return deconstruction

        except Exception as e:
            logger.error(f"Error in deconstruction: {e}")
            return {}

    async def _save_deconstruction(self, worldview_id: str, deconstruction: Dict) -> bool:
        """
        Save deconstruction to worldviews table

        Args:
            worldview_id: Worldview UUID
            deconstruction: Deconstruction dict

        Returns:
            True if successful
        """
        try:
            # Update worldviews.deconstruction field
            response = self.supabase.table('worldviews')\
                .update({
                    'deconstruction': deconstruction,
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('id', worldview_id)\
                .execute()

            if response.data:
                logger.info(f"Saved deconstruction for worldview {worldview_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error saving deconstruction: {e}")
            return False

    async def create_rebuttal(
        self,
        worldview_id: str,
        deconstruction: Dict
    ) -> Optional[UUID]:
        """
        Create a rebuttal record in rebuttals table

        Args:
            worldview_id: Worldview UUID
            deconstruction: Deconstruction dict

        Returns:
            Rebuttal UUID if created
        """
        try:
            # Check if rebuttal already exists
            existing = self.supabase.table('rebuttals')\
                .select('id')\
                .eq('worldview_id', worldview_id)\
                .execute()

            if existing.data:
                logger.info(f"Rebuttal already exists for worldview {worldview_id}")
                return UUID(existing.data[0]['id'])

            # Create new rebuttal
            rebuttal_data = {
                'worldview_id': worldview_id,
                'counter_narrative': deconstruction.get('counter_narrative', ''),
                'key_points': deconstruction.get('key_rebuttals', []),
                'structural_flaws': deconstruction.get('flaws', []),
                'suggested_response': deconstruction.get('suggested_response', ''),
                'evidence_urls': []  # To be populated by user or future automation
            }

            response = self.supabase.table('rebuttals')\
                .insert(rebuttal_data)\
                .execute()

            if response.data:
                rebuttal_id = UUID(response.data[0]['id'])
                logger.info(f"Created rebuttal {rebuttal_id} for worldview {worldview_id}")
                return rebuttal_id

            return None

        except Exception as e:
            logger.error(f"Error creating rebuttal: {e}")
            return None

    async def deconstruct_all_worldviews(self, force: bool = False) -> Dict:
        """
        Deconstruct all worldviews in database

        Args:
            force: If True, regenerate even if deconstruction exists

        Returns:
            Summary statistics
        """
        try:
            # Get all worldviews
            response = self.supabase.table('worldviews')\
                .select('id, title, deconstruction')\
                .execute()

            worldviews = response.data
            total = len(worldviews)

            logger.info(f"Found {total} worldviews to deconstruct")

            stats = {
                'total': total,
                'processed': 0,
                'skipped': 0,
                'failed': 0
            }

            for worldview in worldviews:
                worldview_id = worldview['id']

                # Skip if already has deconstruction (unless force)
                if not force and worldview.get('deconstruction'):
                    logger.info(f"Skipping {worldview['title']} (already has deconstruction)")
                    stats['skipped'] += 1
                    continue

                # Deconstruct
                result = await self.deconstruct(worldview_id, save_to_db=True)

                if result:
                    stats['processed'] += 1
                    logger.info(f"[{stats['processed']}/{total}] Deconstructed: {worldview['title']}")
                else:
                    stats['failed'] += 1
                    logger.error(f"Failed to deconstruct: {worldview['title']}")

            logger.info(f"Deconstruction complete: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error in batch deconstruction: {e}")
            return {'error': str(e)}

    async def update_worldview_flaws(self, worldview_id: str) -> bool:
        """
        Update only the structural_flaws field (faster than full deconstruction)

        Args:
            worldview_id: Worldview UUID

        Returns:
            True if successful
        """
        try:
            # Get worldview
            response = self.supabase.table('worldviews')\
                .select('*')\
                .eq('id', worldview_id)\
                .execute()

            if not response.data:
                return False

            worldview = response.data[0]

            # Get perceptions
            perception_ids = worldview.get('perception_ids', [])
            response = self.supabase.table('perceptions')\
                .select('*')\
                .in_('id', perception_ids)\
                .execute()

            perceptions = response.data

            # Detect flaws
            flaws = await self.flaw_detector.detect_flaws(worldview, perceptions)

            # Update only structural_flaws
            response = self.supabase.table('worldviews')\
                .update({
                    'structural_flaws': flaws,
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('id', worldview_id)\
                .execute()

            return bool(response.data)

        except Exception as e:
            logger.error(f"Error updating worldview flaws: {e}")
            return False
