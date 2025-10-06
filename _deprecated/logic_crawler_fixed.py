#!/usr/bin/env python3
"""
완전히 새로운 Logic Defense 크롤러 - 실제 DB 스키마에 맞춤
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

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 환경변수
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# DC갤러리 설정 (공격 논리만 수집)
GALLERIES = {
    'uspolitics': {
        'id': 'uspolitics',
        'name': '미국정치',
        'logic_type': 'attack',
        'url': 'https://gall.dcinside.com/mgallery/board/lists',
        'is_mgallery': True
    }
    # 방어 논리는 이제 사용자가 대시보드에서 직접 작성
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

class FixedLogicCrawler:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8'
        }
        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_page(self, url: str) -> Optional[str]:
        """페이지 HTML 가져오기"""
        try:
            await asyncio.sleep(random.uniform(0.5, 1.0))
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
        return None

    def parse_concept_post(self, post_elem, gallery: Dict) -> Optional[Dict]:
        """개념글 데이터 파싱"""
        try:
            # 게시글 번호
            num_elem = post_elem.select_one('.gall_num')
            if not num_elem or num_elem.text.strip() in ['공지', 'AD']:
                return None

            try:
                post_num = int(num_elem.text.strip())
            except ValueError:
                return None

            # 제목과 링크
            title_elem = post_elem.select_one('.gall_tit a')
            if not title_elem:
                return None

            title = title_elem.text.strip()
            href = title_elem.get('href', '')

            # URL 생성
            if gallery.get('is_mgallery', False):
                if href.startswith('/'):
                    post_url = f"https://gall.dcinside.com{href}"
                else:
                    post_url = href
            else:
                post_url = f"https://gall.dcinside.com{href}"

            # 작성자
            writer_elem = post_elem.select_one('.gall_writer')
            author = writer_elem.get('data-nick', 'Unknown') if writer_elem else 'Unknown'

            return {
                'post_num': post_num,
                'title': title,
                'author': author,
                'post_url': post_url,
                'gallery_id': gallery['id'],
                'logic_type': gallery['logic_type']
            }

        except Exception as e:
            logger.error(f"Error parsing post: {str(e)}")
            return None

    async def fetch_concept_posts(self, gallery_key: str, max_pages: int = 15) -> List[Dict]:
        """개념글 수집"""
        gallery = GALLERIES.get(gallery_key)
        if not gallery:
            return []

        posts = []
        logger.info(f"🎯 {gallery['name']} 개념글 수집 시작...")

        for page in range(1, max_pages + 1):
            try:
                # 개념글 페이지 URL
                url = f"{gallery['url']}?id={gallery['id']}&page={page}&exception_mode=recommend"

                html = await self.fetch_page(url)
                if not html:
                    continue

                soup = BeautifulSoup(html, 'html.parser')
                post_elements = soup.select('tr.us-post')  # 개념글

                page_posts = []
                for post_elem in post_elements:
                    post_data = self.parse_concept_post(post_elem, gallery)
                    if post_data:
                        page_posts.append(post_data)

                posts.extend(page_posts)
                logger.info(f"📄 페이지 {page}: {len(page_posts)}개")

                if not page_posts:  # 더 이상 개념글이 없으면 중단
                    break

            except Exception as e:
                logger.error(f"Error crawling page {page}: {str(e)}")
                continue

        logger.info(f"✅ {gallery['name']}: 총 {len(posts)}개 개념글 수집")
        return posts

    async def fetch_post_content(self, post_url: str) -> Optional[str]:
        """게시글 본문 가져오기"""
        try:
            html = await self.fetch_page(post_url)
            if not html:
                return None

            soup = BeautifulSoup(html, 'html.parser')

            # 본문 찾기
            content_elem = soup.select_one('.write_div') or soup.select_one('.writing_view_box')
            if content_elem:
                content = content_elem.get_text(strip=True, separator='\n')
                return content  # 전체 본문 저장 (맥락 파악 위해)

        except Exception as e:
            logger.error(f"Error fetching content from {post_url}: {str(e)}")

        return None

    async def analyze_logic_with_gpt5(self, title: str, content: str) -> Optional[Dict]:
        """GPT-5로 논리 분석"""
        if not content or len(content.strip()) < 20:
            return None

        try:
            # GPT-5 temperature 기본값(1) 사용
            response = await self.openai_client.chat.completions.create(
                model=os.getenv('GPT_ANALYSIS_MODEL', 'gpt-5-mini'),
                messages=[
                    {
                        'role': 'system',
                        'content': '''당신은 한국 정치 논리 분석 전문가입니다. DC갤러리 개념글을 분석하여 **이 글이 어떤 정치적 프레임/내러티브를 구성하는지** 파악하세요.

**핵심 목적**: 이 글이 어떤 **왜곡된 세계관**을 만들어내는 데 기여하는가?

정치적 프레임/내러티브 예시:
- "민주당=친중=국가안보위협" → 중국인무비자, 중국인도망, 간첩의혹, 친중외교 등의 글들이 이 프레임 구성
- "이재명=범죄자=민주당붕괴" → 김혜경쇼핑, 대장동의혹, 위증교사 등의 글들이 이 프레임 구성
- "윤석열=국가수호자" → 안보강화, 북한대응, 동맹강화 등의 글들이 이 프레임 구성
- "한국언론=편파=조작" → KBS편파, MBC왜곡, 언론개혁필요 등의 글들이 이 프레임 구성

다음 JSON 구조로만 응답하세요:
{
  "core_argument": "핵심 주장을 한 문장으로",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "ai_classification": "공격적/방어적/중립적",
  "evidence_quality": 5,
  "threat_level": 3,
  "effectiveness_score": 7,
  "political_frame": "이 글이 구성하는 정치적 프레임/내러티브 (예: 민주당=친중=안보위협, 이재명=범죄자, 윤석열=국가수호자, 한국언론=편파)",
  "context_issue": "구체적 이슈/사건 (예: 중국인무비자, 김혜경쇼핑, KBS편파보도)",
  "distortion_pattern": "사용된 왜곡 기법 (예: 맥락제거, 과장, 인신공격, 허위연관)"
}

**중요**:
- political_frame: 여러 글들이 공유할 수 있는 **큰 내러티브/세계관**
- context_issue: 이 글이 다루는 **구체적 사건/이슈**
- 같은 political_frame을 가진 글들은 다른 context_issue를 다루더라도 같은 왜곡된 세계관을 구성함

단순 욕설/조롱만 있고 구체적 주장이 없으면 null을 반환하세요.'''
                    },
                    {
                        'role': 'user',
                        'content': f'제목: {title}\n\n본문: {content}'
                    }
                ]
                # temperature 파라미터 제거 (GPT-5는 기본값만 지원)
            )

            analysis_text = response.choices[0].message.content.strip()

            # JSON 추출
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif analysis_text.lower() == 'null':
                return None

            try:
                return json.loads(analysis_text)
            except json.JSONDecodeError:
                logger.warning(f"JSON 파싱 실패: {analysis_text[:100]}...")
                return None

        except Exception as e:
            logger.error(f"논리 분석 실패 ({title[:30]}): {str(e)}")
            return None

    async def save_to_logic_repository(self, post: Dict, content: str, analysis: Dict):
        """실제 DB 스키마에 맞춰 저장"""
        try:
            # 실제 logic_repository 테이블 컬럼에 맞춰 데이터 구성
            logic_data = {
                'logic_type': post['logic_type'],  # attack/defense
                'source_gallery': post['gallery_id'],  # uspolitics/minjudang
                'ai_classification': analysis.get('ai_classification', '분석필요'),
                'core_argument': analysis.get('core_argument', ''),
                'keywords': analysis.get('keywords', []),
                'evidence_quality': analysis.get('evidence_quality', 5),
                'threat_level': analysis.get('threat_level', 3),
                'original_title': post['title'],
                'original_content': content,  # 전체 본문 저장 (맥락 파악 위해)
                'original_url': post['post_url'],
                'original_post_num': post['post_num'],
                'effectiveness_score': analysis.get('effectiveness_score', 5),
                'political_frame': analysis.get('political_frame'),  # 정치적 프레임/내러티브
                'context_issue': analysis.get('context_issue'),  # 관련 사건/이슈
                'distortion_pattern': analysis.get('distortion_pattern'),  # 왜곡 패턴
                'usage_count': 0,
                'success_count': 0,
                'is_active': True,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }

            # Supabase에 저장
            result = self.supabase.table('logic_repository').insert(logic_data).execute()

            if result.data:
                logger.info(f"✅ 논리 저장 성공: {post['title'][:30]}...")
                return result.data[0]['id']
            else:
                logger.error(f"❌ 논리 저장 실패: {post['title'][:30]}...")
                return None

        except Exception as e:
            logger.error(f"저장 오류 ({post['title'][:30]}): {str(e)}")
            return None

    async def create_embedding(self, title: str, content: str, core_argument: str) -> Optional[List[float]]:
        """임베딩 생성"""
        try:
            # 제목 + 본문 + 핵심논리를 결합해서 임베딩
            combined_text = f"{title}\n\n{content}\n\n핵심논리: {core_argument}"

            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=combined_text[:8000]  # 토큰 제한
            )

            return response.data[0].embedding

        except Exception as e:
            logger.error(f"임베딩 생성 실패: {str(e)}")
            return None

    async def save_embedding(self, logic_id: str, embedding: List[float]):
        """임베딩을 logic_repository.vector_embedding 컬럼에 저장"""
        try:
            # logic_repository 테이블의 vector_embedding 컬럼에 직접 업데이트
            result = self.supabase.table('logic_repository').update({
                'vector_embedding': embedding
            }).eq('id', logic_id).execute()

            if result.data:
                logger.info(f"✅ 임베딩 저장 완료: {logic_id}")
            else:
                logger.error(f"❌ 임베딩 저장 실패: {logic_id}")

        except Exception as e:
            logger.error(f"임베딩 저장 실패 ({logic_id}): {str(e)}")

    async def process_posts(self, posts: List[Dict], batch_size: int = 10):
        """게시글들 처리"""
        logger.info(f"📖 {len(posts)}개 게시글 처리 시작...")

        processed = 0
        for i in range(0, len(posts), batch_size):
            batch = posts[i:i+batch_size]

            for post in batch:
                try:
                    # 1. 본문 가져오기
                    content = await self.fetch_post_content(post['post_url'])
                    if not content:
                        continue

                    # 2. 논리 분석
                    analysis = await self.analyze_logic_with_gpt5(post['title'], content)
                    if not analysis:
                        continue

                    # 3. DB 저장
                    logic_id = await self.save_to_logic_repository(post, content, analysis)
                    if not logic_id:
                        continue

                    # 4. 임베딩 생성 및 저장
                    embedding = await self.create_embedding(
                        post['title'], content, analysis.get('core_argument', '')
                    )
                    if embedding:
                        await self.save_embedding(logic_id, embedding)

                    processed += 1
                    logger.info(f"✅ 처리 완료 {processed}: {post['title'][:30]}...")

                except Exception as e:
                    logger.error(f"게시글 처리 실패 ({post['title'][:30]}): {str(e)}")

            logger.info(f"📦 배치 {(i//batch_size)+1} 완료")

        return processed

    async def run(self):
        """메인 실행"""
        logger.info("🚀 Fixed Logic Defense 크롤러 시작!")

        total_processed = 0

        # 미국정치 갤러리 처리 (공격 논리 수집)
        gallery_key = 'uspolitics'
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 {GALLERIES[gallery_key]['name']} 갤러리")
        logger.info(f"{'='*60}")

        try:
            # 개념글 수집
            posts = await self.fetch_concept_posts(gallery_key, max_pages=5)

            if posts:
                # 처리 (20개)
                processed = await self.process_posts(posts[:20])
                total_processed += processed
                logger.info(f"🎉 {GALLERIES[gallery_key]['name']}: {processed}개 완료")
            else:
                logger.warning(f"{GALLERIES[gallery_key]['name']}: 개념글 없음")

        except Exception as e:
            logger.error(f"{gallery_key} 처리 실패: {str(e)}")

        logger.info(f"\n🎉 총 {total_processed}개 논리 분석 완료!")

async def main():
    if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
        logger.error("❌ 환경변수 누락")
        sys.exit(1)

    async with FixedLogicCrawler() as crawler:
        await crawler.run()

if __name__ == "__main__":
    asyncio.run(main())