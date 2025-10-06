#!/usr/bin/env python3
"""
간단한 크롤러 - 복잡한 RAG 없이 기본 기능 테스트
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from supabase import create_client
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def simple_crawl_and_save():
    print("🕷️ 간단한 크롤러 시작...")

    # 클라이언트 초기화
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )

    openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # DC 갤러리 크롤링
    print("📡 DC 갤러리 크롤링 중...")
    async with aiohttp.ClientSession() as session:
        url = "https://gall.dcinside.com/mgallery/board/lists?id=uspolitics"
        async with session.get(url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'html.parser')
            posts = soup.find_all('tr', class_='ub-content')[:3]  # 3개만

            print(f"✅ {len(posts)}개 게시물 발견")

            for i, post in enumerate(posts):
                try:
                    # 제목 추출
                    title_elem = post.find('td', class_='gall_tit')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    print(f"📝 {i+1}. {title[:50]}...")

                    # OpenAI로 분석
                    response = await openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "다음 제목을 분석해서 JSON으로 응답: {\"core_argument\": \"핵심논리\", \"keywords\": [\"키워드들\"], \"ai_classification\": \"공격적/방어적/중립적\", \"threat_level\": 1-10점수, \"effectiveness_score\": 1-10점수}"},
                            {"role": "user", "content": title}
                        ],
                        temperature=0.3,
                        max_tokens=200
                    )

                    # JSON 파싱 시도
                    try:
                        analysis = json.loads(response.choices[0].message.content)
                    except:
                        analysis = {
                            "core_argument": title[:100],
                            "keywords": [title.split()[0] if title.split() else "키워드"],
                            "ai_classification": "분석필요",
                            "threat_level": 5,
                            "effectiveness_score": 5
                        }

                    # 데이터베이스에 저장
                    data = {
                        'logic_type': 'attack',
                        'source_gallery': 'uspolitics',
                        'ai_classification': analysis.get('ai_classification', '분석필요'),
                        'core_argument': analysis.get('core_argument', title)[:500],
                        'keywords': analysis.get('keywords', [])[:5],
                        'threat_level': min(10, max(1, analysis.get('threat_level', 5))),
                        'effectiveness_score': min(10, max(1, analysis.get('effectiveness_score', 5))),
                        'original_title': title,
                        'original_content': title,  # 일단 제목으로
                        'original_url': url,
                        'is_active': True
                    }

                    result = supabase.table('logic_repository').insert(data).execute()

                    if result.data:
                        print(f"✅ 저장 성공: {analysis.get('core_argument', title)[:30]}...")
                    else:
                        print(f"❌ 저장 실패")

                except Exception as e:
                    print(f"⚠️ 게시물 {i+1} 처리 오류: {str(e)[:100]}")
                    continue

    # 저장된 데이터 확인
    print("\n📊 저장된 데이터 확인...")
    try:
        result = supabase.table('logic_repository').select('*').order('created_at', desc=True).limit(5).execute()
        print(f"✅ 총 {len(result.data)}개 최근 데이터:")
        for item in result.data:
            print(f"  - {item['core_argument'][:50]}... (위협도: {item['threat_level']}/10)")
    except Exception as e:
        print(f"❌ 데이터 확인 실패: {e}")

    print("\n🎉 간단한 크롤러 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(simple_crawl_and_save())