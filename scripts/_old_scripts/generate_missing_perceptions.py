#!/usr/bin/env python3
"""
누락된 2개 content의 perception 생성
"""

import os
import asyncio
from supabase import create_client
import sys
sys.path.append('/Users/taehyeonkim/dev/minjoo/moniterdc')

from engines.analyzers.reasoning_structure_extractor import ReasoningStructureExtractor

# Supabase 설정
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

async def main():
    print('=' * 80)
    print('누락된 Perception 생성')
    print('=' * 80)
    print()

    missing_content_ids = [
        '416eb8f5-2438-4e97-a94a-863bc673fa1f',
        '7e2b00d1-5f5e-4586-b55e-2039829b9313'
    ]

    extractor = ReasoningStructureExtractor()

    for i, content_id in enumerate(missing_content_ids, 1):
        print(f'{i}/{len(missing_content_ids)} - Content ID: {content_id[:8]}...')

        # Get content
        content = supabase.table('contents').select('*').eq('id', content_id).execute()

        if not content.data:
            print(f'  ✗ Content not found')
            continue

        content_data = content.data[0]

        try:
            # Extract perception
            perception_id = await extractor.extract(content_data)
            print(f'  ✓ Perception 생성: {perception_id}')

        except Exception as e:
            print(f'  ✗ 실패: {str(e)[:100]}')

    print()
    print('=' * 80)
    print('완료')
    print('=' * 80)

if __name__ == '__main__':
    asyncio.run(main())
