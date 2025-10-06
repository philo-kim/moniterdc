#!/usr/bin/env python3
"""
DC Gallery Logic Crawler - Worldview Analysis Version
세계관 분석: 주체 중심 접근
"""

import os
import asyncio
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client
from openai import AsyncOpenAI
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WorldviewCrawler:
    """세계관 분석 크롤러"""

    def __init__(self):
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_KEY')
        )
        self.openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    async def analyze_worldview_with_gpt(self, title: str, content: str) -> Optional[Dict]:
        """
        세계관 분석: 주체, 속성, 관계 추출
        """
        if not content or len(content.strip()) < 20:
            return None

        try:
            response = await self.openai_client.chat.completions.create(
                model=os.getenv('GPT_ANALYSIS_MODEL', 'gpt-5-mini'),
                messages=[
                    {
                        'role': 'system',
                        'content': '''당신은 한국 정치 세계관 분석 전문가입니다.

**목적**: DC갤러리 글이 구성하는 **세계관**을 분석하세요.

세계관은 다음으로 구성됩니다:
1. **주체들** (actors): 누구에 대한 이야기인가?
2. **속성/평가** (attributes): 그들을 어떻게 규정하는가?
3. **관계** (relations): 주체들 간의 연결은?

예시:
- 글: "중국인 무비자로 조선족 무더기 입국, 민주당이 허용"
  → 주체1: 민주당 (평가: 친중정책 추진)
  → 주체2: 중국/조선족 (평가: 안보위협)
  → 관계: 민주당이 중국인 유입을 허용함

- 글: "윤석열 대통령 한미정상회담, 동맹 강화"
  → 주체1: 윤석열 (평가: 외교성과, 동맹강화)
  → 주체2: 미국 (평가: 우방)
  → 관계: 윤석열이 미국과 동맹을 강화함

다음 JSON으로 응답하세요:
{
  "core_argument": "핵심 주장 한 문장",
  "subjects": [
    {
      "name": "주체 이름 (예: 민주당, 이재명, 윤석열, 중국, 미국)",
      "attributes": ["속성1", "속성2"],
      "sentiment": "positive/negative/neutral"
    }
  ],
  "relations": [
    {
      "subject1": "주체1",
      "relation_type": "관계 유형 (예: 결탁, 공격, 옹호, 허용)",
      "subject2": "주체2"
    }
  ],
  "keywords": ["키워드1", "키워드2"],
  "context_issue": "구체적 사건/이슈",
  "threat_level": 5,
  "evidence_quality": 5
}

**중요**:
- subjects: 최대 3개까지, 핵심 주체만
- attributes: 각 주체당 1-3개, 간결하게
- sentiment: 이 글에서 해당 주체를 긍정적/부정적/중립적으로 묘사하는지
- relations: 주체들 간의 연결을 명시

단순 욕설/조롱만 있으면 null 반환.'''
                    },
                    {
                        'role': 'user',
                        'content': f'제목: {title}\n\n본문: {content[:1000]}'
                    }
                ]
            )

            analysis_text = response.choices[0].message.content.strip()

            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif analysis_text.lower() == 'null':
                return None

            return json.loads(analysis_text)

        except Exception as e:
            logger.error(f"세계관 분석 실패: {str(e)}")
            return None

    async def fetch_post_content(self, post_url: str) -> Optional[str]:
        """게시글 본문 가져오기"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': 'Mozilla/5.0'}
                async with session.get(post_url, headers=headers, timeout=10) as response:
                    if response.status != 200:
                        return None

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    content_div = soup.select_one('.write_div')
                    if not content_div:
                        return None

                    content = content_div.get_text(strip=True, separator='\n')
                    return content

        except Exception as e:
            logger.error(f"Error fetching {post_url}: {str(e)}")
            return None

    async def save_to_repository(self, post: Dict, content: str, analysis: Dict):
        """저장"""
        try:
            logic_data = {
                'logic_type': post['logic_type'],
                'source_gallery': post['gallery_id'],
                'ai_classification': '공격적' if analysis.get('threat_level', 0) > 5 else '중립적',
                'core_argument': analysis.get('core_argument', ''),
                'keywords': analysis.get('keywords', []),
                'evidence_quality': analysis.get('evidence_quality', 5),
                'threat_level': analysis.get('threat_level', 3),
                'original_title': post['title'],
                'original_content': content,
                'original_url': post['post_url'],
                'original_post_num': post['post_num'],
                'effectiveness_score': analysis.get('evidence_quality', 5),
                'context_issue': analysis.get('context_issue'),
                'worldview_data': {  # 새로운 필드
                    'subjects': analysis.get('subjects', []),
                    'relations': analysis.get('relations', [])
                },
                'usage_count': 0,
                'success_count': 0,
                'is_active': True,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }

            result = self.supabase.table('logic_repository').insert(logic_data).execute()

            if result.data:
                logger.info(f"✅ 논리 저장: {post['title'][:30]}...")

                # 주체별 클러스터 생성/업데이트
                await self.update_subject_clusters(result.data[0]['id'], analysis)

                return result.data[0]['id']

        except Exception as e:
            logger.error(f"저장 실패: {str(e)}")
            return None

    async def update_subject_clusters(self, logic_id: str, analysis: Dict):
        """주체별 클러스터 업데이트"""
        subjects = analysis.get('subjects', [])

        for subject in subjects:
            subject_name = subject.get('name')
            if not subject_name:
                continue

            # 주체 클러스터 찾기 또는 생성
            cluster_result = self.supabase.table('subject_clusters').select('*').eq('subject_name', subject_name).execute()

            if cluster_result.data:
                cluster_id = cluster_result.data[0]['id']
            else:
                # 새 주체 클러스터 생성
                new_cluster = self.supabase.table('subject_clusters').insert({
                    'subject_name': subject_name,
                    'total_mentions': 0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                    'common_attributes': [],
                    'first_seen': datetime.now(timezone.utc).isoformat(),
                    'last_seen': datetime.now(timezone.utc).isoformat()
                }).execute()

                cluster_id = new_cluster.data[0]['id']

            # 주체-논리 연결
            self.supabase.table('subject_logic_mapping').insert({
                'subject_cluster_id': cluster_id,
                'logic_id': logic_id,
                'sentiment': subject.get('sentiment', 'neutral'),
                'attributes': subject.get('attributes', [])
            }).execute()

            # 클러스터 통계 업데이트
            sentiment = subject.get('sentiment', 'neutral')
            self.supabase.rpc('increment_subject_cluster_stats', {
                'cluster_id': cluster_id,
                'sentiment_type': sentiment
            }).execute()

    async def crawl_gallery(self, gallery_id: str, logic_type: str, limit: int = 10):
        """갤러리 크롤링"""
        logger.info(f"🔍 크롤링 시작: {gallery_id} ({logic_type})")

        base_url = f'https://gall.dcinside.com/board/lists/?id={gallery_id}'

        try:
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': 'Mozilla/5.0'}
                async with session.get(base_url, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch {base_url}")
                        return

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    posts = soup.select('.gall_list tbody tr.ub-content')[:limit]

                    for post_elem in posts:
                        try:
                            title_elem = post_elem.select_one('.gall_tit a')
                            if not title_elem:
                                continue

                            title = title_elem.get_text(strip=True)
                            post_num = title_elem['href'].split('no=')[1].split('&')[0]
                            post_url = f'https://gall.dcinside.com/board/view/?id={gallery_id}&no={post_num}'

                            # 중복 체크
                            existing = self.supabase.table('logic_repository').select('id').eq('original_post_num', post_num).execute()
                            if existing.data:
                                continue

                            # 본문 가져오기
                            content = await self.fetch_post_content(post_url)
                            if not content:
                                continue

                            # 세계관 분석
                            analysis = await self.analyze_worldview_with_gpt(title, content)
                            if not analysis:
                                continue

                            # 저장
                            post_data = {
                                'gallery_id': gallery_id,
                                'logic_type': logic_type,
                                'title': title,
                                'post_num': post_num,
                                'post_url': post_url
                            }

                            await self.save_to_repository(post_data, content, analysis)
                            await asyncio.sleep(1)

                        except Exception as e:
                            logger.error(f"게시글 처리 실패: {str(e)}")
                            continue

        except Exception as e:
            logger.error(f"크롤링 실패: {str(e)}")


async def main():
    crawler = WorldviewCrawler()

    # 공격 논리 수집 (미정갤)
    await crawler.crawl_gallery('uspolitics', 'attack', limit=5)

    logger.info("✅ 크롤링 완료")


if __name__ == '__main__':
    asyncio.run(main())