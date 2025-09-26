#!/usr/bin/env python3
"""
Logic Defense 크롤러 v3.0 - LangChain RAG 통합 버전
기존 크롤링 기능 + LangChain RAG 시스템 통합
"""

import os
import sys
import asyncio
import json
import random
from datetime import datetime, timezone
from typing import List, Dict, Optional
from dotenv import load_dotenv

import aiohttp
from bs4 import BeautifulSoup
from supabase import create_client, Client
from openai import AsyncOpenAI
import logging

# RAG 시스템 임포트
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_system.rag_logic_system import get_rag_system, RAGLogicSystem

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 환경변수
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# DC갤러리 설정
GALLERIES = {
    'uspolitics': {
        'id': 'uspolitics',
        'name': '미국정치',
        'logic_type': 'attack',
        'url': 'https://gall.dcinside.com/mgallery/board/lists',
        'is_mgallery': True
    },
    'minjoo': {
        'id': 'minjudang',
        'name': '민주당',
        'logic_type': 'defense',
        'url': 'https://gall.dcinside.com/mgallery/board/lists',
        'is_mgallery': True
    }
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
]

class RAGCrawler:
    """LangChain RAG 통합 크롤러"""
    
    def __init__(self):
        """초기화"""
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.rag_system: RAGLogicSystem = get_rag_system()
        self.session = None
        
        logger.info("RAG Crawler initialized with LangChain integration")
    
    async def __aenter__(self):
        """비동기 컨텍스트 진입"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 종료"""
        if self.session:
            await self.session.close()
    
    def get_headers(self) -> dict:
        """랜덤 헤더 생성"""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://gall.dcinside.com/'
        }
    
    async def fetch_concept_posts(self, gallery_id: str, pages: int = 5) -> List[Dict]:
        """개념글 수집"""
        posts = []
        gallery_info = GALLERIES.get(gallery_id)
        
        if not gallery_info:
            logger.error(f"Unknown gallery: {gallery_id}")
            return posts
        
        for page in range(1, pages + 1):
            try:
                url = f"{gallery_info['url']}?id={gallery_info['id']}&page={page}&exception_mode=recommend"
                
                async with self.session.get(url, headers=self.get_headers()) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch page {page} from {gallery_id}: {response.status}")
                        continue
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 게시글 추출
                    for tr in soup.select('tr.us-post'):
                        try:
                            # 게시글 정보 파싱
                            num_elem = tr.select_one('.gall_num')
                            if not num_elem or num_elem.text == '공지':
                                continue
                            
                            post_num = num_elem.text.strip()
                            title_elem = tr.select_one('.gall_tit a')
                            
                            if not title_elem:
                                continue
                            
                            title = title_elem.text.strip()
                            post_url = title_elem.get('href', '')
                            
                            if not post_url.startswith('http'):
                                post_url = f"https://gall.dcinside.com{post_url}"
                            
                            author_elem = tr.select_one('.gall_writer')
                            author = author_elem.get('data-nick', '') if author_elem else 'anonymous'
                            
                            # 조회수, 추천수
                            count_elem = tr.select_one('.gall_count')
                            views = int(count_elem.text.strip()) if count_elem else 0
                            
                            recommend_elem = tr.select_one('.gall_recommend')
                            recommends = int(recommend_elem.text.strip()) if recommend_elem else 0
                            
                            posts.append({
                                'gallery_id': gallery_info['id'],
                                'gallery_name': gallery_info['name'],
                                'logic_type': gallery_info['logic_type'],
                                'post_num': post_num,
                                'title': title,
                                'url': post_url,
                                'author': author,
                                'views': views,
                                'recommends': recommends
                            })
                            
                        except Exception as e:
                            logger.error(f"Error parsing post: {e}")
                            continue
                    
                    logger.info(f"Fetched {len(posts)} posts from {gallery_id} page {page}")
                    
                # Rate limiting
                await asyncio.sleep(random.uniform(1.5, 2.5))
                
            except Exception as e:
                logger.error(f"Error fetching page {page} from {gallery_id}: {e}")
                continue
        
        return posts
    
    async def fetch_post_content(self, post_url: str) -> Optional[str]:
        """게시글 본문 가져오기"""
        try:
            async with self.session.get(post_url, headers=self.get_headers()) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # 본문 추출
                content_elem = soup.select_one('.write_div') or soup.select_one('.writing_view_box')
                
                if content_elem:
                    # 텍스트만 추출
                    content = content_elem.get_text(separator='\n', strip=True)
                    return content[:2000]  # 최대 2000자
                
                return None
                
        except Exception as e:
            logger.error(f"Error fetching content from {post_url}: {e}")
            return None
    
    async def process_with_rag(self, posts: List[Dict]) -> List[Dict]:
        """RAG 시스템으로 게시글 처리"""
        processed_results = []
        
        for post in posts:
            try:
                # 본문 가져오기
                content = await self.fetch_post_content(post['url'])
                if not content:
                    content = post['title']  # 본문이 없으면 제목만 사용
                
                # RAG 시스템으로 분석
                result = await self.rag_system.analyze_logic(
                    text=content,
                    metadata={
                        'logic_type': post['logic_type'],
                        'source_gallery': post['gallery_id'],
                        'url': post['url'],
                        'author': post['author'],
                        'title': post['title'],
                        'views': post['views'],
                        'recommends': post['recommends']
                    }
                )
                
                # 공격 논리인 경우 자동으로 방어 논리 찾기
                if post['logic_type'] == 'attack':
                    counter_logic = await self.rag_system.find_counter_logic(content)
                    result['counter_logic'] = counter_logic
                
                processed_results.append({
                    'post': post,
                    'analysis': result
                })
                
                logger.info(f"Processed with RAG: {post['title'][:50]}...")
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing post with RAG: {e}")
                continue
        
        return processed_results
    
    async def find_attack_defense_matches(self):
        """공격-방어 논리 자동 매칭"""
        try:
            # 최근 24시간 내 공격 논리 조회
            from datetime import timedelta
            cutoff_date = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
            
            attacks = self.supabase.table('logic_repository') \
                .select("*") \
                .eq('logic_type', 'attack') \
                .gte('created_at', cutoff_date) \
                .execute()
            
            matches = []
            for attack in attacks.data:
                # RAG 시스템으로 방어 논리 찾기
                counter = await self.rag_system.find_counter_logic(
                    attack['original_content'] or attack['core_argument']
                )
                
                if counter['similar_defenses']:
                    best_defense = counter['similar_defenses'][0]
                    
                    # 매칭 결과 저장
                    match_data = {
                        'attack_id': attack['id'],
                        'defense_id': best_defense['metadata'].get('db_id'),
                        'match_confidence': 0.85,  # 신뢰도 계산 로직 추가 필요
                        'match_reason': counter['answer'][:500],
                        'created_at': datetime.now(timezone.utc).isoformat()
                    }
                    
                    self.supabase.table('logic_matches').insert(match_data).execute()
                    matches.append(match_data)
                    
                    logger.info(f"Found match for attack: {attack['core_argument'][:50]}...")
            
            return matches
            
        except Exception as e:
            logger.error(f"Error finding matches: {e}")
            return []
    
    async def generate_daily_report(self) -> Dict:
        """일일 분석 리포트 생성"""
        try:
            # 1. 트렌딩 토픽
            trending = await self.rag_system.get_trending_topics(1)
            
            # 2. 오늘의 주요 공격 논리
            today = datetime.now(timezone.utc).date().isoformat()
            attacks = self.supabase.table('logic_repository') \
                .select("*") \
                .eq('logic_type', 'attack') \
                .gte('created_at', f"{today}T00:00:00Z") \
                .order('threat_level', desc=True) \
                .limit(5) \
                .execute()
            
            # 3. 효과적인 방어 논리
            defenses = self.supabase.table('logic_repository') \
                .select("*") \
                .eq('logic_type', 'defense') \
                .gte('effectiveness_score', 8) \
                .order('effectiveness_score', desc=True) \
                .limit(5) \
                .execute()
            
            report = {
                'date': today,
                'trending_topics': trending[:5],
                'top_attacks': [
                    {
                        'core_argument': a['core_argument'],
                        'threat_level': a['threat_level'],
                        'keywords': a['keywords']
                    }
                    for a in attacks.data
                ],
                'effective_defenses': [
                    {
                        'core_argument': d['core_argument'],
                        'effectiveness_score': d['effectiveness_score'],
                        'usage_count': d.get('usage_count', 0)
                    }
                    for d in defenses.data
                ],
                'total_analyzed': len(attacks.data) + len(defenses.data),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # 리포트 저장
            self.supabase.table('daily_reports').insert(report).execute()
            
            logger.info(f"Daily report generated for {today}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            return {}
    
    async def run(self):
        """메인 실행 함수"""
        logger.info("Starting RAG Crawler...")
        
        # 1. 개념글 수집
        all_posts = []
        for gallery_id in GALLERIES.keys():
            posts = await self.fetch_concept_posts(gallery_id, pages=3)
            all_posts.extend(posts)
            logger.info(f"Collected {len(posts)} posts from {gallery_id}")
        
        # 2. RAG 시스템으로 처리
        if all_posts:
            processed = await self.process_with_rag(all_posts)
            logger.info(f"Processed {len(processed)} posts with RAG")
            
            # 3. 공격-방어 매칭
            matches = await self.find_attack_defense_matches()
            logger.info(f"Found {len(matches)} attack-defense matches")
        
        # 4. 일일 리포트 생성
        report = await self.generate_daily_report()
        if report:
            logger.info("Daily report generated successfully")
        
        logger.info("RAG Crawler completed successfully")

# 실행
async def main():
    """메인 함수"""
    async with RAGCrawler() as crawler:
        await crawler.run()

if __name__ == "__main__":
    asyncio.run(main())
