#!/usr/bin/env python3
"""
2개의 빈 perception 삭제
(mechanisms, logic_chain, explicit_claims 모두 비어있음)
"""

import os
from supabase import create_client

# Supabase 설정
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print('=' * 80)
print('빈 Perception 삭제')
print('=' * 80)
print()

# 빈 perception 찾기
perceptions = supabase.table('layered_perceptions').select('*').execute()

empty = []
for p in perceptions.data:
    mechanisms = p.get('mechanisms', [])
    logic_chain = p.get('logic_chain', [])
    explicit_claims = p.get('explicit_claims', [])

    if (not mechanisms or mechanisms == []) and \
       (not logic_chain or logic_chain == []) and \
       (not explicit_claims or explicit_claims == []):
        empty.append(p)

print(f'빈 perception: {len(empty)}개')

for p in empty:
    print(f'  - ID: {p["id"]}')
    print(f'    content_id: {p.get("content_id", "None")}')

print()

if empty:
    confirm = input(f'{len(empty)}개 빈 perception을 삭제하시겠습니까? (yes/no): ')
    if confirm.lower() == 'yes':
        for p in empty:
            # perception_worldview_links 먼저 삭제
            supabase.table('perception_worldview_links').delete().eq('perception_id', p['id']).execute()
            # perception 삭제
            supabase.table('layered_perceptions').delete().eq('id', p['id']).execute()
            print(f'  ✓ 삭제: {p["id"][:8]}...')

        print()
        print(f'✓ {len(empty)}개 삭제 완료')
    else:
        print('취소됨')
else:
    print('✓ 빈 perception 없음')

print()
print('=' * 80)
