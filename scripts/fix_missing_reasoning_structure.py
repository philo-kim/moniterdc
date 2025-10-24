#!/usr/bin/env python3
"""
누락된 reasoning structure 필드 채우기
"""

import os
import asyncio
from supabase import create_client
from engines.analyzers.reasoning_structure_extractor import ReasoningStructureExtractor

# Supabase 설정
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

async def main():
    print('=' * 80)
    print('누락된 Reasoning Structure 필드 채우기')
    print('=' * 80)
    print()

    # 누락된 perception 찾기
    perceptions = supabase.table('layered_perceptions').select('*').execute()

    missing = []
    for p in perceptions.data:
        if not p.get('mechanisms') or not p.get('logic_chain'):
            missing.append(p)

    print(f'누락된 perception: {len(missing)}개')
    print()

    if not missing:
        print('✓ 모든 perception에 reasoning structure 존재')
        return

    # ReasoningStructureExtractor 초기화
    extractor = ReasoningStructureExtractor()

    # 각 perception 처리
    for i, perception in enumerate(missing, 1):
        print(f'{i}/{len(missing)} - Perception ID: {perception["id"][:8]}...')

        try:
            # Content 가져오기
            content = supabase.table('contents').select('*').eq('id', perception['content_id']).execute()
            if not content.data:
                print(f'  ✗ Content not found')
                continue

            content_data = content.data[0]

            # Reasoning structure 추출 (extract 메서드 사용)
            perception_id = await extractor.extract(content_data)

            # 추출된 perception 가져오기
            updated = supabase.table('layered_perceptions').select('mechanisms, actor, logic_chain').eq('id', perception_id).execute()

            if updated.data:
                result = updated.data[0]
                print(f'  ✓ 완료: {len(result.get("mechanisms", []))}개 mechanism, {len(result.get("logic_chain", []))}개 logic step')
            else:
                print(f'  ✓ 완료')

        except Exception as e:
            print(f'  ✗ 실패: {str(e)[:100]}')

    print()
    print('=' * 80)
    print('완료')
    print('=' * 80)

if __name__ == '__main__':
    asyncio.run(main())
