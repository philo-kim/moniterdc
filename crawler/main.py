"""
DC Gallery Crawler
정치 갤러리 실시간 크롤링 모듈
"""

import os
import sys
import json
import time
import random
import asyncio
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, quote

import aiohttp
from bs4 import BeautifulSoup
from supabase import create_client, Client
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경변수 로드
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# DC갤러리 설정
DC_GALLERIES = {
    'minjoo': {
        'id': 'minjoo_party',
        'name': '민주당 갤러리',
        'base_url': 'https://gall.dcinside.com/board/lists',
        'gallery_type': 'minjoo'
    },
    'kukmin': {
        'id': 'president_park2', 
        'name': '국민의힘 갤러리',
        'base_url': 'https://gall.dcinside.com/board/lists',
        'gallery_type': 'kukmin'
    },
    'politics': {
        'id': 'politics',
        'name': '정치 갤러리',
        'base_url': 'https://gall.dcinside.com/board/lists',
        'gallery_type': 'politics'
    }
}

# User-Agent 로테이션
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]


class DCGalleryCrawler:
    """DC갤러리 크롤러 클래스"""
    
    def __init__(self):
        """크롤러 초기화"""
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.session: Optional[aiohttp.ClientSession] = None
        self.crawl_stats = {
            'total_posts': 0,
            'new_posts': 0,
            'updated_posts': 0,
            'errors': 0
        }
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = aiohttp.ClientSession(headers=headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
        """페이지 HTML 가져오기"""
        for attempt in range(retries):
            try:
                # Rate limiting
                await asyncio.sleep(random.uniform(1, 2))
                
                async with self.session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching {url} (attempt {attempt + 1}/{retries})")
            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)}")
            
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def parse_post_list(self, html: str, gallery_info: Dict) -> List[Dict]:
        """게시글 목록 파싱"""
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        # 개념글 박스 찾기
        concept_posts = soup.select('.us-post')  # 개념글
        general_posts = soup.select('.ub-content')  # 일반글
        
        all_posts = concept_posts[:5] + general_posts[:10]  # 개념글 5개 + 일반글 10개
        
        for post_elem in all_posts:
            try:
                post_data = self.extract_post_data(post_elem, gallery_info)
                if post_data:
                    posts.append(post_data)
            except Exception as e:
                logger.error(f"Error parsing post: {str(e)}")
                continue
        
        return posts
    
    def extract_post_data(self, post_elem, gallery_info: Dict) -> Optional[Dict]:
        """게시글 데이터 추출"""
        try:
            # 게시글 번호
            post_num_elem = post_elem.select_one('.gall_num')
            if not post_num_elem or post_num_elem.text == '공지':
                return None
            post_num = int(post_num_elem.text.strip())
            
            # 제목과 링크
            title_elem = post_elem.select_one('.gall_tit a')
            if not title_elem:
                return None
            
            title = title_elem.text.strip()
            post_url = urljoin('https://gall.dcinside.com', title_elem.get('href', ''))
            
            # 작성자
            author_elem = post_elem.select_one('.gall_writer')
            author = author_elem.get('data-nick', 'Unknown') if author_elem else 'Unknown'
            author_ip = author_elem.get('data-ip', '') if author_elem else ''
            
            # 조회수, 추천수, 댓글수
            count_elem = post_elem.select_one('.gall_count')
            views = int(count_elem.text.strip()) if count_elem else 0
            
            recommend_elem = post_elem.select_one('.gall_recommend')
            recommends = int(recommend_elem.text.strip()) if recommend_elem else 0
            
            reply_elem = post_elem.select_one('.reply_num')
            comments_count = 0
            if reply_elem:
                reply_text = reply_elem.text.strip()
                if reply_text and reply_text[1:-1].isdigit():
                    comments_count = int(reply_text[1:-1])
            
            # 이미지 여부
            has_image = bool(post_elem.select_one('.icon_img'))
            
            return {
                'gallery_id': gallery_info['id'],
                'gallery_type': gallery_info['gallery_type'],
                'post_num': post_num,
                'title': title,
                'author': author,
                'author_ip': author_ip,
                'views': views,
                'recommends': recommends,
                'comments_count': comments_count,
                'has_image': has_image,
                'post_url': post_url,
                'crawled_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting post data: {str(e)}")
            return None
    
    async def fetch_post_content(self, post_url: str) -> Optional[str]:
        """게시글 본문 가져오기"""
        html = await self.fetch_page(post_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        content_elem = soup.select_one('.write_div')
        
        if content_elem:
            # 이미지, 스크립트 등 제거
            for elem in content_elem.select('img, script, style'):
                elem.decompose()
            return content_elem.get_text(strip=True)[:5000]  # 최대 5000자
        
        return None
    
    async def save_posts(self, posts: List[Dict]) -> Dict[str, int]:
        """게시글 저장 (UPSERT)"""
        stats = {'new': 0, 'updated': 0, 'errors': 0}
        
        for post in posts:
            try:
                # 기존 게시글 확인
                existing = self.supabase.table('posts').select('id').eq(
                    'gallery_id', post['gallery_id']
                ).eq(
                    'post_num', post['post_num']
                ).execute()
                
                if existing.data:
                    # 업데이트
                    self.supabase.table('posts').update({
                        'views': post['views'],
                        'recommends': post['recommends'],
                        'comments_count': post['comments_count'],
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    }).eq('id', existing.data[0]['id']).execute()
                    stats['updated'] += 1
                else:
                    # 새 게시글 - 내용도 가져오기
                    if post['recommends'] > 5 or post['comments_count'] > 10:
                        content = await self.fetch_post_content(post['post_url'])
                        post['content'] = content
                    
                    # 삽입
                    self.supabase.table('posts').insert(post).execute()
                    stats['new'] += 1
                    
                    # 분석 작업 큐에 추가
                    if post.get('recommends', 0) > 10:
                        await self.queue_for_analysis(post)
                    
            except Exception as e:
                logger.error(f"Error saving post: {str(e)}")
                stats['errors'] += 1
        
        return stats
    
    async def queue_for_analysis(self, post: Dict):
        """AI 분석을 위한 작업 큐에 추가"""
        try:
            job_data = {
                'job_type': 'analyze',
                'job_status': 'queued',
                'payload': {
                    'post_id': post.get('id'),
                    'gallery_id': post['gallery_id'],
                    'post_num': post['post_num'],
                    'title': post['title'],
                    'content': post.get('content', ''),
                    'recommends': post['recommends']
                },
                'priority': min(10, max(1, post['recommends'] // 10))  # 추천수 기반 우선순위
            }
            
            self.supabase.table('job_queue').insert(job_data).execute()
            logger.info(f"Queued post {post['post_num']} for analysis")
            
        except Exception as e:
            logger.error(f"Error queuing for analysis: {str(e)}")
    
    async def crawl_gallery(self, gallery_key: str) -> Dict[str, Any]:
        """특정 갤러리 크롤링"""
        gallery_info = DC_GALLERIES.get(gallery_key)
        if not gallery_info:
            logger.error(f"Unknown gallery: {gallery_key}")
            return {'error': f'Unknown gallery: {gallery_key}'}
        
        logger.info(f"Crawling {gallery_info['name']}...")
        
        # 갤러리 목록 페이지 URL
        list_url = f"{gallery_info['base_url']}?id={gallery_info['id']}"
        
        # 페이지 가져오기
        html = await self.fetch_page(list_url)
        if not html:
            logger.error(f"Failed to fetch {gallery_info['name']}")
            return {'error': 'Failed to fetch page'}
        
        # 게시글 파싱
        posts = self.parse_post_list(html, gallery_info)
        logger.info(f"Found {len(posts)} posts in {gallery_info['name']}")
        
        # 저장
        stats = await self.save_posts(posts)
        
        return {
            'gallery': gallery_key,
            'posts_found': len(posts),
            **stats
        }
    
    async def crawl_all(self) -> Dict[str, Any]:
        """모든 갤러리 크롤링"""
        results = {}
        
        for gallery_key in DC_GALLERIES.keys():
            try:
                result = await self.crawl_gallery(gallery_key)
                results[gallery_key] = result
                
                # 갤러리 간 딜레이
                await asyncio.sleep(random.uniform(2, 3))
                
            except Exception as e:
                logger.error(f"Error crawling {gallery_key}: {str(e)}")
                results[gallery_key] = {'error': str(e)}
        
        # 시스템 로그 저장
        self.log_crawl_results(results)
        
        return results
    
    def log_crawl_results(self, results: Dict):
        """크롤링 결과 로깅"""
        try:
            total_new = sum(r.get('new', 0) for r in results.values())
            total_updated = sum(r.get('updated', 0) for r in results.values())
            total_errors = sum(r.get('errors', 0) for r in results.values())
            
            log_data = {
                'log_level': 'info',
                'component': 'crawler',
                'message': f"Crawl completed: {total_new} new, {total_updated} updated, {total_errors} errors",
                'details': results
            }
            
            self.supabase.table('system_logs').insert(log_data).execute()
            
        except Exception as e:
            logger.error(f"Error logging results: {str(e)}")


async def main():
    """메인 실행 함수"""
    logger.info("Starting DC Gallery crawler...")
    
    try:
        async with DCGalleryCrawler() as crawler:
            results = await crawler.crawl_all()
            
            # 결과 출력
            print("\n=== Crawl Results ===")
            for gallery, stats in results.items():
                if 'error' in stats:
                    print(f"{gallery}: ERROR - {stats['error']}")
                else:
                    print(f"{gallery}: {stats.get('new', 0)} new, "
                          f"{stats.get('updated', 0)} updated, "
                          f"{stats.get('errors', 0)} errors")
            
            # GitHub Actions 출력 (CI/CD용)
            if os.getenv('GITHUB_ACTIONS'):
                print(f"::set-output name=result::{json.dumps(results)}")
            
            return results
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # 환경변수 체크
    if not all([SUPABASE_URL, SUPABASE_KEY]):
        logger.error("Missing required environment variables")
        sys.exit(1)
    
    # 크롤러 실행
    asyncio.run(main())
