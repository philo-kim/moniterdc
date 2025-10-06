#!/usr/bin/env python3
"""
스마트 크롤러 - 중복 방지 로직 포함
게시글 번호와 시간 기반으로 효율적 수집
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from supabase import create_client
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timezone, timedelta
import logging
import re

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartCrawler:
    def __init__(self):
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_KEY')
        )
        self.openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.existing_posts = set()  # 이미 수집된 게시글 번호들

    def load_existing_posts(self, gallery_id: str) -> set:
        """이미 수집된 게시글 번호들 로드"""
        try:
            result = self.supabase.table('logic_repository').select(
                'original_post_num'
            ).eq(
                'source_gallery', gallery_id
            ).not_.is_(
                'original_post_num', 'null'
            ).execute()

            existing = {str(row['original_post_num']) for row in result.data if row['original_post_num']}
            logger.info(f"📋 {gallery_id}: 기존 수집 게시글 {len(existing)}개")
            return existing

        except Exception as e:
            logger.error(f"기존 게시글 로드 실패: {e}")
            return set()

    def get_last_crawl_time(self, gallery_id: str) -> datetime:
        """마지막 크롤링 시간 확인"""
        try:
            result = self.supabase.table('logic_repository').select(
                'created_at'
            ).eq(
                'source_gallery', gallery_id
            ).order(
                'created_at', desc=True
            ).limit(1).execute()

            if result.data:
                last_time = datetime.fromisoformat(result.data[0]['created_at'].replace('Z', '+00:00'))
                logger.info(f"📅 {gallery_id}: 마지막 수집 {last_time.strftime('%m-%d %H:%M')}")
                return last_time
            else:
                # 처음 수집하는 경우 1시간 전부터
                return datetime.now(timezone.utc) - timedelta(hours=1)

        except Exception as e:
            logger.error(f"마지막 크롤링 시간 확인 실패: {e}")
            return datetime.now(timezone.utc) - timedelta(hours=1)

    def extract_post_number(self, post_elem) -> tuple:
        """게시글에서 번호와 제목 추출"""
        try:
            # 게시글 번호
            num_elem = post_elem.select_one('.gall_num')
            if not num_elem or num_elem.text.strip() in ['공지', 'AD', '']:
                return None, None

            try:
                post_num = int(num_elem.text.strip())
            except ValueError:
                return None, None

            # 제목
            title_elem = post_elem.select_one('.gall_tit a')
            if not title_elem:
                return None, None

            title = title_elem.get_text(strip=True)
            if not title or len(title) < 10:  # 너무 짧은 제목 제외
                return None, None

            return post_num, title

        except Exception as e:
            logger.error(f"게시글 파싱 실패: {e}")
            return None, None

    async def get_post_content(self, session: aiohttp.ClientSession, post_url: str) -> str:
        """게시글 본문 가져오기 (선택사항)"""
        try:
            await asyncio.sleep(0.5)  # 요청 간격
            async with session.get(post_url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # DC갤러리 본문 추출
                    content_elem = soup.select_one('.write_div, .writing_view_box')
                    if content_elem:
                        return content_elem.get_text(strip=True)[:1000]  # 1000자 제한

        except Exception as e:
            logger.error(f"본문 가져오기 실패: {e}")

        return ""

    async def analyze_with_gpt5(self, title: str, content: str = "") -> dict:
        """GPT-5로 논리 분석"""
        try:
            text_to_analyze = f"제목: {title}\n내용: {content[:500]}" if content else title

            # GPT-5 Responses API 사용
            response = await self.openai_client.responses.create(
                input=f"""정치 게시글을 분석하여 JSON 형식으로 응답해주세요:

{text_to_analyze}

다음 형식으로 응답:
{{
  "core_argument": "핵심 논증 요약",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "ai_classification": "공격적|방어적|중립적",
  "threat_level": 1-10,
  "effectiveness_score": 1-10,
  "category": "정치|경제|사회|외교|기타"
}}""",
                model="gpt-5",
                reasoning={
                    "effort": "low"
                },
                text={
                    "verbosity": "low"
                }
            )

            # Responses API는 다른 응답 구조를 가짐
            response_text = response.output_text if hasattr(response, 'output_text') else ""
            logger.info(f"GPT 응답 길이: {len(response_text) if response_text else 0}, 내용: '{response_text}'")

            if not response_text or response_text.strip() == "":
                logger.warning(f"GPT-5가 빈 응답을 반환했습니다. 기본값 사용: {title[:30]}...")
                return {
                    "core_argument": title[:100],
                    "keywords": title.split()[:3],
                    "ai_classification": "분석필요",
                    "threat_level": 5,
                    "effectiveness_score": 5,
                    "category": "기타"
                }

            return json.loads(response_text)

        except Exception as e:
            logger.error(f"GPT 분석 실패: {e}")
            return {
                "core_argument": title[:100],
                "keywords": title.split()[:3],
                "ai_classification": "분석필요",
                "threat_level": 5,
                "effectiveness_score": 5,
                "category": "기타"
            }

    async def crawl_gallery(self, gallery_config: dict, max_posts: int = 20):
        """갤러리 크롤링 (중복 방지 포함)"""
        gallery_id = gallery_config['id']
        gallery_name = gallery_config['name']
        logic_type = gallery_config['logic_type']

        logger.info(f"🎯 {gallery_name} 갤러리 크롤링 시작")

        # 1. 기존 게시글 번호 로드
        existing_posts = self.load_existing_posts(gallery_id)

        # 2. 마지막 크롤링 시간 확인
        last_crawl = self.get_last_crawl_time(gallery_id)

        new_posts = []
        processed_count = 0

        async with aiohttp.ClientSession(headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }) as session:

            # 최신 3페이지만 체크
            for page in range(1, 4):
                try:
                    if gallery_config.get('is_mgallery'):
                        url = f"https://gall.dcinside.com/mgallery/board/lists?id={gallery_id}&page={page}&exception_mode=recommend"
                    else:
                        url = f"https://gall.dcinside.com/board/lists?id={gallery_id}&page={page}&exception_mode=recommend"

                    await asyncio.sleep(0.5)  # 요청 간격
                    async with session.get(url, timeout=10) as response:
                        if response.status != 200:
                            logger.warning(f"HTTP {response.status}: {url}")
                            continue

                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        posts = soup.select('tr.ub-content')

                        logger.info(f"📄 {page}페이지: {len(posts)}개 게시글 발견")

                        for post in posts:
                            if processed_count >= max_posts:
                                break

                            post_num, title = self.extract_post_number(post)
                            if not post_num or not title:
                                continue

                            # 중복 체크
                            if str(post_num) in existing_posts:
                                logger.debug(f"⏭️ 중복 스킵: {post_num}")
                                continue

                            logger.info(f"🆕 새 게시글 {post_num}: {title[:50]}...")

                            # GPT 분석
                            analysis = await self.analyze_with_gpt5(title)

                            # 게시글 URL 생성
                            if gallery_config.get('is_mgallery'):
                                post_url = f"https://gall.dcinside.com/mgallery/board/view/?id={gallery_id}&no={post_num}&exception_mode=recommend"
                            else:
                                post_url = f"https://gall.dcinside.com/board/view/?id={gallery_id}&no={post_num}&exception_mode=recommend"

                            # DB 저장 데이터 준비
                            data = {
                                'logic_type': logic_type,
                                'source_gallery': gallery_id,
                                'original_post_num': post_num,
                                'original_title': title,
                                'original_url': post_url,
                                'original_content': "",  # 필요시 본문도 가져올 수 있음
                                'core_argument': analysis['core_argument'],
                                'keywords': analysis['keywords'][:5],
                                'ai_classification': analysis['ai_classification'],
                                'threat_level': min(10, max(1, analysis['threat_level'])),
                                'effectiveness_score': min(10, max(1, analysis['effectiveness_score'])),
                                'category': analysis.get('category', '기타'),
                                'usage_count': 0,
                                'success_count': 0,
                                'is_active': True
                            }

                            # DB에 저장
                            try:
                                result = self.supabase.table('logic_repository').insert(data).execute()
                                if result.data:
                                    processed_count += 1
                                    existing_posts.add(str(post_num))  # 중복 방지 업데이트
                                    logger.info(f"✅ 저장 완료: {post_num}")

                            except Exception as e:
                                logger.error(f"저장 실패 {post_num}: {e}")

                        if processed_count >= max_posts:
                            break

                except Exception as e:
                    logger.error(f"페이지 {page} 처리 실패: {e}")

        logger.info(f"🎉 {gallery_name}: {processed_count}개 새 게시글 수집 완료")
        return processed_count

async def main():
    """메인 실행 함수"""
    crawler = SmartCrawler()

    # 갤러리 설정
    galleries = [
        {
            'id': 'uspolitics',
            'name': '미국정치',
            'logic_type': 'attack',
            'is_mgallery': True
        },
        {
            'id': 'minjudang',
            'name': '민주당',
            'logic_type': 'defense',
            'is_mgallery': True
        }
    ]

    total_collected = 0

    for gallery in galleries:
        try:
            count = await crawler.crawl_gallery(gallery, max_posts=10)
            total_collected += count
        except Exception as e:
            logger.error(f"{gallery['name']} 갤러리 실패: {e}")

    logger.info(f"🏁 전체 수집 완료: {total_collected}개 새 게시글")

    # 수집 결과 확인
    try:
        result = crawler.supabase.table('logic_repository').select('*').order('created_at', desc=True).limit(5).execute()
        logger.info("📊 최근 수집 결과:")
        for logic in result.data:
            logger.info(f"  - {logic['source_gallery']}: {logic['original_title'][:50]}... (위험도: {logic['threat_level']}/10)")
    except Exception as e:
        logger.error(f"결과 확인 실패: {e}")

if __name__ == "__main__":
    asyncio.run(main())