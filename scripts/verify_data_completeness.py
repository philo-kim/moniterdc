#!/usr/bin/env python3
"""
데이터 완결성 검증 및 누락된 분석 단계 확인
"""

import os
from supabase import create_client

# Supabase 설정
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print('=' * 80)
print('데이터 완결성 검증')
print('=' * 80)
print()

# 1. Contents 확인
contents = supabase.table('contents').select('id').execute()
print(f'1. Contents: {len(contents.data)}개')

# 2. Layered Perceptions 확인
perceptions = supabase.table('layered_perceptions').select('id, content_id, mechanisms, actor, logic_chain').execute()
print(f'2. Layered Perceptions: {len(perceptions.data)}개')

# 3. 누락된 perception 체크
content_ids = {c['id'] for c in contents.data}
perception_content_ids = {p['content_id'] for p in perceptions.data}
missing_perceptions = content_ids - perception_content_ids
print(f'   ✓ Content 대비 커버리지: {len(perception_content_ids)}/{len(content_ids)} ({len(perception_content_ids)/len(content_ids)*100:.1f}%)')
if missing_perceptions:
    print(f'   ⚠ 누락된 perception: {len(missing_perceptions)}개')
else:
    print(f'   ✓ 모든 content에 perception 존재')

# 4. Reasoning structure 필드 확인
no_mechanisms = [p for p in perceptions.data if not p.get('mechanisms')]
no_actor = [p for p in perceptions.data if not p.get('actor')]
no_logic_chain = [p for p in perceptions.data if not p.get('logic_chain')]

print(f'3. Reasoning Structure (v2.0 필드):')
print(f'   - mechanisms 누락: {len(no_mechanisms)}개')
print(f'   - actor 누락: {len(no_actor)}개')
print(f'   - logic_chain 누락: {len(no_logic_chain)}개')

if no_mechanisms or no_actor or no_logic_chain:
    print(f'   ⚠ reasoning_structure_extractor 실행 필요')
else:
    print(f'   ✓ 모든 perception에 reasoning structure 존재')

# 5. Worldviews 확인
worldviews = supabase.table('worldviews').select('id, title, level, parent_worldview_id, version').eq('archived', False).execute()
parent_worldviews = [w for w in worldviews.data if w['level'] == 1]
child_worldviews = [w for w in worldviews.data if w['level'] == 2]

print(f'4. Worldviews:')
print(f'   - 상위 세계관 (level 1): {len(parent_worldviews)}개')
print(f'   - 하위 세계관 (level 2): {len(child_worldviews)}개')
print(f'   - Version 2 세계관: {len([w for w in worldviews.data if w["version"] == 2])}개')

# 6. Perception-Worldview Links 확인
links = supabase.table('perception_worldview_links').select('perception_id, worldview_id').execute()
print(f'5. Perception-Worldview Links: {len(links.data)}개')

# 링크된 perception 개수
linked_perception_ids = {link['perception_id'] for link in links.data}
print(f'   - 링크된 perception: {len(linked_perception_ids)}개 ({len(linked_perception_ids)/len(perceptions.data)*100:.1f}%)')
print(f'   - 링크 안된 perception: {len(perceptions.data) - len(linked_perception_ids)}개')

# 어느 worldview에 링크되어 있는지
linked_worldview_ids = {link['worldview_id'] for link in links.data}
parent_with_links = [w for w in parent_worldviews if w['id'] in linked_worldview_ids]
child_with_links = [w for w in child_worldviews if w['id'] in linked_worldview_ids]

print(f'   - 상위 세계관에 링크: {len(parent_with_links)}/{len(parent_worldviews)}개')
print(f'   - 하위 세계관에 링크: {len(child_with_links)}/{len(child_worldviews)}개')

if len(child_with_links) == 0 and len(child_worldviews) > 0:
    print(f'   ⚠ 하위 세계관에 링크 없음 - mechanism_matcher 실행 필요')

print()
print('=' * 80)
print('필요한 작업 확인')
print('=' * 80)
print()

needed_tasks = []

if missing_perceptions:
    needed_tasks.append('1. layered_perception_extractor 실행 (누락된 content 분석)')

if no_mechanisms or no_actor or no_logic_chain:
    needed_tasks.append('2. reasoning_structure_extractor 실행 (v2.0 필드 채우기)')

if len(child_with_links) == 0 and len(child_worldviews) > 0:
    needed_tasks.append('3. mechanism_matcher 실행 (하위 세계관에 perception 링크)')

if not needed_tasks:
    print('✓ 모든 데이터가 완결되어 있습니다!')
else:
    print('필요한 작업:')
    for task in needed_tasks:
        print(f'  {task}')

print()
print('=' * 80)
