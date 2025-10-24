"""
Content Collector - Unified content collection from all sources
"""

import logging
from typing import List, Dict
from uuid import UUID
from datetime import datetime, timezone

from engines.adapters.base_adapter import BaseAdapter
from engines.adapters.dc_gallery_adapter import DCGalleryAdapter
from engines.utils.supabase_client import get_supabase

logger = logging.getLogger(__name__)

class ContentCollector:
    """Unified content collector for all sources"""

    def __init__(self):
        self.supabase = get_supabase()

        # Register adapters
        self.adapters: Dict[str, BaseAdapter] = {
            'dc_gallery': DCGalleryAdapter(),
            # Will add more: 'youtube', 'article', 'instagram', etc.
        }

    async def collect(self, source_type: str, **params) -> List[UUID]:
        """
        Collect content from specified source

        Args:
            source_type: Type of source ('dc_gallery', 'youtube', etc.)
            **params: Source-specific parameters

        Returns:
            List of created content IDs
        """
        if source_type not in self.adapters:
            raise ValueError(f"Unknown source type: {source_type}")

        adapter = self.adapters[source_type]
        logger.info(f"Collecting from {source_type} with params: {params}")

        # 1. Fetch raw content
        raw_contents = await adapter.fetch(**params)
        logger.info(f"Fetched {len(raw_contents)} items from {source_type}")

        content_ids = []

        for raw in raw_contents:
            try:
                # 2. Parse content
                parsed = adapter.parse(raw)

                # 3. Check if already exists
                if await self.exists(parsed.url):
                    logger.info(f"Content already exists: {parsed.url}")
                    continue

                # 4. For DC gallery, fetch full content + metadata
                if source_type == 'dc_gallery':
                    post_data = await adapter.fetch_post_content(parsed.url)
                    if not post_data.get('body'):
                        logger.warning(f"Failed to fetch content for {parsed.url}")
                        continue

                    parsed.body = post_data['body']

                    # Update published_at if available
                    if post_data.get('published_at'):
                        # Parse ISO format string to datetime
                        from dateutil import parser as date_parser
                        try:
                            parsed.published_at = date_parser.parse(post_data['published_at'])
                        except:
                            parsed.published_at = None

                    # Add metadata
                    if not parsed.metadata:
                        parsed.metadata = {}

                    parsed.metadata.update({
                        'author': post_data.get('author'),
                        'view_count': post_data.get('view_count'),
                        'comment_count': post_data.get('comment_count'),
                        'recommend_count': post_data.get('recommend_count')
                    })

                # 5. Save content
                content_id = await self.save_content(
                    source_type=source_type,
                    url=parsed.url,
                    source_id=parsed.source_id,
                    title=parsed.title,
                    body=parsed.body,
                    metadata=parsed.metadata,
                    published_at=parsed.published_at,
                    base_credibility=adapter.get_credibility()
                )

                content_ids.append(content_id)
                logger.info(f"Saved content: {content_id}")

            except Exception as e:
                logger.error(f"Error processing content: {e}")
                import traceback
                traceback.print_exc()
                continue

        logger.info(f"Collected {len(content_ids)} new contents from {source_type}")
        return content_ids

    async def exists(self, url: str) -> bool:
        """
        Check if content with this URL already exists

        Args:
            url: Source URL

        Returns:
            True if exists, False otherwise
        """
        try:
            result = self.supabase.table('contents')\
                .select('id')\
                .eq('source_url', url)\
                .execute()

            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Error checking existence: {e}")
            return False

    async def save_content(
        self,
        source_type: str,
        url: str,
        source_id: str,
        title: str,
        body: str,
        metadata: Dict,
        published_at: datetime = None,
        base_credibility: float = 0.5
    ) -> UUID:
        """
        Save content to database

        Returns:
            UUID of created content
        """
        data = {
            'source_type': source_type,
            'source_url': url,
            'source_id': source_id,
            'title': title,
            'body': body,
            'metadata': metadata,
            'base_credibility': base_credibility,
            'published_at': published_at.isoformat() if published_at else None,
            'collected_at': datetime.now(timezone.utc).isoformat(),
            'is_active': True
        }

        result = self.supabase.table('contents').insert(data).execute()
        return result.data[0]['id']