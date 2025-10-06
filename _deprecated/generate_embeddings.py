#!/usr/bin/env python3
"""
임베딩이 없는 논리 데이터에 벡터 임베딩 생성
"""
import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client
from openai import AsyncOpenAI
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_missing_embeddings():
    """임베딩이 없는 데이터에 임베딩 생성"""

    # 클라이언트 초기화
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )

    openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # 임베딩이 없는 데이터 조회
    try:
        result = supabase.table('logic_repository').select(
            'id, original_title, original_content, core_argument, keywords'
        ).is_('vector_embedding', 'null').limit(50).execute()

        records = result.data
        logger.info(f"📊 임베딩이 없는 레코드 {len(records)}개 발견")

        if not records:
            logger.info("✅ 모든 레코드에 임베딩이 이미 존재합니다")
            return

        processed = 0

        for record in records:
            try:
                # 텍스트 결합
                title = record.get('original_title', '')
                content = record.get('original_content', '')
                core_argument = record.get('core_argument', '')
                keywords = record.get('keywords', [])

                combined_text = f"{title}\n{content}\n{core_argument}\n{' '.join(keywords) if keywords else ''}"
                combined_text = combined_text.strip()

                if not combined_text:
                    logger.warning(f"빈 텍스트 스킵: {record['id']}")
                    continue

                # 임베딩 생성
                response = await openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=combined_text[:8000]  # 토큰 제한
                )

                embedding = response.data[0].embedding

                # 데이터베이스 업데이트
                update_result = supabase.table('logic_repository').update({
                    'vector_embedding': embedding
                }).eq('id', record['id']).execute()

                if update_result.data:
                    processed += 1
                    logger.info(f"✅ 임베딩 생성 완료 ({processed}): {title[:50]}...")
                else:
                    logger.error(f"❌ 임베딩 저장 실패: {record['id']}")

            except Exception as e:
                logger.error(f"임베딩 생성 실패 ({record['id']}): {e}")
                continue

        logger.info(f"🎉 총 {processed}개 임베딩 생성 완료!")

    except Exception as e:
        logger.error(f"임베딩 생성 프로세스 실패: {e}")

if __name__ == "__main__":
    asyncio.run(generate_missing_embeddings())