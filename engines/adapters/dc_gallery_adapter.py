"""
DC Gallery adapter for content collection
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, List
from datetime import datetime
import logging

from .base_adapter import BaseAdapter, ParsedContent

logger = logging.getLogger(__name__)

class DCGalleryAdapter(BaseAdapter):
    """Adapter for DC Inside galleries"""

    @property
    def source_type(self) -> str:
        return 'dc_gallery'

    async def fetch(self, gallery: str, limit: int = 10, concept_only: bool = True, is_mgallery: bool = True) -> List[Dict]:
        """
        Fetch posts from DC gallery (multiple pages)

        Args:
            gallery: Gallery ID (e.g., 'uspolitics')
            limit: Maximum number of posts to fetch
            concept_only: If True, fetch only concept posts (개념글)
            is_mgallery: If True, use mgallery URL format

        Returns:
            List of raw post dictionaries
        """
        board_path = 'mgallery' if is_mgallery else 'board'

        if concept_only:
            base_url = f'https://gall.dcinside.com/{board_path}/board/lists?id={gallery}&exception_mode=recommend'
        else:
            base_url = f'https://gall.dcinside.com/{board_path}/board/lists?id={gallery}'

        all_posts = []
        page = 1
        posts_per_page = 50  # 개념글 페이지당 약 50개

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }

                while len(all_posts) < limit:
                    # 페이지별 URL
                    page_url = f"{base_url}&page={page}"

                    async with session.get(page_url, headers=headers) as response:
                        if response.status != 200:
                            logger.error(f"Failed to fetch {page_url}: {response.status}")
                            break

                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')

                        if concept_only:
                            post_elements = soup.select('tr.us-post')
                        else:
                            post_elements = soup.select('.gall_list tbody tr.ub-content')

                        if not post_elements:
                            # 더 이상 글이 없으면 중단
                            break

                        for post_elem in post_elements:
                            if len(all_posts) >= limit:
                                break

                            try:
                                title_elem = post_elem.select_one('.gall_tit a')
                                if not title_elem:
                                    continue

                                title = title_elem.get_text(strip=True)
                                href = title_elem['href']
                                post_num = href.split('no=')[1].split('&')[0]
                                post_url = f'https://gall.dcinside.com/{board_path}/board/view/?id={gallery}&no={post_num}'

                                all_posts.append({
                                    'gallery': gallery,
                                    'post_num': post_num,
                                    'url': post_url,
                                    'title': title
                                })

                            except Exception as e:
                                logger.error(f"Error parsing post element: {e}")
                                continue

                        page += 1

                        # Rate limiting
                        await asyncio.sleep(0.5)

                logger.info(f"Fetched {len(all_posts)} posts from {gallery} ({page-1} pages)")
                return all_posts

        except Exception as e:
            logger.error(f"Error fetching DC gallery {gallery}: {e}")
            return all_posts  # Return what we got so far

    async def fetch_post_content(self, post_url: str) -> str:
        """Fetch full content of a post"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }

                async with session.get(post_url, headers=headers, timeout=10) as response:
                    if response.status != 200:
                        return ""

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    content_div = soup.select_one('.write_div')
                    if not content_div:
                        return ""

                    content = content_div.get_text(strip=True, separator='\n')
                    return content

        except Exception as e:
            logger.error(f"Error fetching content from {post_url}: {e}")
            return ""

    def parse(self, raw: Dict) -> ParsedContent:
        """
        Parse raw DC gallery post

        Args:
            raw: Raw post dictionary with 'url', 'title', 'gallery', 'post_num'

        Returns:
            ParsedContent object
        """
        return ParsedContent(
            url=raw['url'],
            source_id=raw['post_num'],
            title=raw['title'],
            body=raw.get('body', ''),  # Body will be fetched separately
            metadata={
                'gallery': raw['gallery'],
                'post_num': raw['post_num']
            },
            published_at=None  # DC gallery doesn't provide timestamp in list view
        )

    def get_credibility(self) -> float:
        """DC gallery has low credibility (anonymous forum)"""
        return 0.2