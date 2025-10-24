#!/usr/bin/env python3
"""
계층적 세계관 매칭
- 상위 세계관: mechanism-based matching
- 하위 세계관: semantic matching (title similarity + parent link)
"""

import os
import json
import asyncio
from supabase import create_client

# Supabase 설정
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def calculate_semantic_similarity(perception, child_worldview):
    """
    Perception과 하위 세계관의 의미적 유사도 계산

    Score = 0.6 * subject_match + 0.3 * action_match + 0.1 * object_match
    """
    # Parse child worldview frame
    try:
        if isinstance(child_worldview.get('frame'), str):
            frame = json.loads(child_worldview['frame'])
        else:
            frame = child_worldview.get('frame', {})
    except:
        frame = {}

    # Get perception actor
    perception_actor = perception.get('actor', {})
    p_subject = perception_actor.get('subject', '')
    p_methods = perception_actor.get('methods', [])

    # Handle list type for subject
    if isinstance(p_subject, list):
        p_subject = ' '.join(p_subject) if p_subject else ''

    # Get child worldview components
    wv_subject = frame.get('subject', '')
    wv_action = frame.get('action', '')
    wv_object = frame.get('object', '')

    # 1. Subject matching (60%)
    subject_score = 0.0
    if p_subject and wv_subject:
        # Extract keywords
        p_keywords = set(p_subject.replace('/', ' ').split())
        wv_keywords = set(wv_subject.replace('/', ' ').split())

        # Check overlap
        if p_keywords & wv_keywords:
            subject_score = 1.0

    # 2. Action matching (30%)
    action_score = 0.0
    if p_methods and wv_action:
        # Check if any method is in action
        for method in p_methods:
            if method in wv_action:
                action_score = 1.0
                break

    # 3. Object matching (10%) - 덜 중요
    object_score = 0.3  # 기본 스코어

    # Combined score
    total = 0.6 * subject_score + 0.3 * action_score + 0.1 * object_score

    return total


async def main():
    print('=' * 80)
    print('계층적 세계관 매칭')
    print('=' * 80)
    print()

    # 1. Load perceptions
    perceptions = supabase.table('layered_perceptions')\
        .select('id, content_id, mechanisms, actor, logic_chain')\
        .execute().data

    perceptions = [p for p in perceptions if p.get('mechanisms') and len(p.get('mechanisms', [])) > 0]
    print(f'✓ Perceptions: {len(perceptions)}개')

    # 2. Load worldviews
    worldviews = supabase.table('worldviews')\
        .select('id, title, level, parent_worldview_id, frame')\
        .eq('version', 2)\
        .eq('archived', False)\
        .execute().data

    parent_worldviews = [w for w in worldviews if w['level'] == 1]
    child_worldviews = [w for w in worldviews if w['level'] == 2]

    print(f'✓ 상위 세계관: {len(parent_worldviews)}개')
    print(f'✓ 하위 세계관: {len(child_worldviews)}개')
    print()

    # 3. Clear existing links
    print('기존 링크 삭제 중...')
    supabase.table('perception_worldview_links').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print('✓ 완료')
    print()

    # 4. Match perceptions to child worldviews
    print('하위 세계관 매칭 시작...')
    print(f'  threshold: 0.4')
    print()

    links_created = 0
    threshold = 0.4

    # Group children by parent
    children_by_parent = {}
    for child in child_worldviews:
        parent_id = child['parent_worldview_id']
        if parent_id not in children_by_parent:
            children_by_parent[parent_id] = []
        children_by_parent[parent_id].append(child)

    for i, perception in enumerate(perceptions):
        matches = []

        # For each parent worldview, check its children
        for parent in parent_worldviews:
            children = children_by_parent.get(parent['id'], [])

            for child in children:
                score = calculate_semantic_similarity(perception, child)

                if score >= threshold:
                    matches.append({
                        'worldview_id': child['id'],
                        'worldview_title': child['title'],
                        'score': score
                    })

        # Sort by score and take top 3
        matches.sort(key=lambda x: x['score'], reverse=True)
        matches = matches[:3]

        # Create links
        for match in matches:
            supabase.table('perception_worldview_links').insert({
                'perception_id': perception['id'],
                'worldview_id': match['worldview_id'],
                'relevance_score': match['score']
            }).execute()
            links_created += 1

        if (i + 1) % 50 == 0:
            print(f'  진행: {i+1}/{len(perceptions)} ({links_created} links)')

    print()
    print(f'✓ {links_created}개 링크 생성')
    print(f'  평균: {links_created/len(perceptions):.2f} links/perception')
    print()

    # 5. Update worldview statistics
    print('세계관 통계 업데이트 중...')

    for wv in child_worldviews:
        links = supabase.table('perception_worldview_links')\
            .select('perception_id')\
            .eq('worldview_id', wv['id'])\
            .execute().data

        perception_ids = [link['perception_id'] for link in links]

        supabase.table('worldviews').update({
            'perception_ids': perception_ids
        }).eq('id', wv['id']).execute()

    print('✓ 완료')
    print()

    # 6. Summary
    print('=' * 80)
    print('매칭 결과')
    print('=' * 80)
    print()

    for parent in parent_worldviews:
        children = children_by_parent.get(parent['id'], [])
        print(f'{parent["title"]}')

        total_perceptions = 0
        for child in children:
            links = supabase.table('perception_worldview_links')\
                .select('id')\
                .eq('worldview_id', child['id'])\
                .execute().data

            total_perceptions += len(links)
            print(f'  → {child["title"][:50]}... ({len(links)}개)')

        print(f'  소계: {total_perceptions}개')
        print()

    print('=' * 80)


if __name__ == '__main__':
    asyncio.run(main())
