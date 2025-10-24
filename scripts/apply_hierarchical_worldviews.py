#!/usr/bin/env python3
"""
생성된 계층적 세계관을 DB에 적용

1. 기존 7개 worldview의 제목과 level 업데이트
2. 46개 하위 worldview 삽입 (parent_worldview_id 연결)
3. perception_worldview_links는 기존 유지 (상위 연결 그대로)
"""

import os
import json
import sys
from supabase import create_client

# Supabase 설정
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def main():
    """메인 실행 함수"""

    # 1. 생성된 결과 파일 찾기
    import glob
    files = glob.glob('_hierarchical_worldviews_*.json')
    if not files:
        print("❌ 결과 파일을 찾을 수 없습니다.")
        print("먼저 generate_hierarchical_worldviews.py를 실행하세요.")
        return

    latest_file = max(files)
    print(f"📁 파일 로드: {latest_file}")
    print()

    with open(latest_file, 'r', encoding='utf-8') as f:
        results = json.load(f)

    print(f"✅ {len(results)}개 세계관 로드")
    print()

    # 2. 각 세계관 처리
    for result in results:
        old_wv_id = result['old_worldview_id']
        old_title = result['old_title']
        parent = result['parent']
        children = result['children']

        print("=" * 80)
        print(f"처리 중: {old_title[:60]}...")
        print("=" * 80)
        print()

        # 3. 기존 worldview 업데이트 (상위로 전환)
        print(f"📝 상위로 업데이트: {parent['title']}")

        update_data = {
            'title': parent['title'],
            'level': 1,
            'version': 2  # v2.0 표시
        }

        # theme_keywords를 frame에 추가
        current = supabase.table('worldviews').select('frame').eq('id', old_wv_id).single().execute()
        frame = current.data.get('frame', {}) if current.data else {}

        # frame이 문자열이면 파싱
        if isinstance(frame, str):
            try:
                frame = json.loads(frame)
            except:
                frame = {}

        frame['theme_keywords'] = parent.get('theme_keywords', [])
        update_data['frame'] = frame

        supabase.table('worldviews').update(update_data).eq('id', old_wv_id).execute()
        print(f"✅ 상위 세계관 업데이트 완료")
        print()

        # 4. 하위 worldview 삽입
        if not children:
            print("⚠️  하위 세계관 없음")
            print()
            continue

        print(f"📝 {len(children)}개 하위 세계관 삽입 중...")

        for i, child in enumerate(children, 1):
            child_data = {
                'title': child.get('title', ''),
                'description': f"구체적 사례: {child.get('subject', '')} - {child.get('action', '')}",
                'parent_worldview_id': old_wv_id,
                'level': 2,
                'version': 2,
                'frame': {
                    'subject': child.get('subject', ''),
                    'object': child.get('object', ''),
                    'action': child.get('action', '')
                },
                'core_subject': child.get('subject', ''),
                'core_attributes': [],
                'overall_valence': 'negative',  # 기본값
                'perception_ids': [],
                'formation_phases': [],
                'cognitive_mechanisms': [],
                'structural_flaws': [],
                'deconstruction': {},
                'total_perceptions': 0,
                'total_contents': 0,
                'source_diversity': 0,
                'evolution_history': [],
                'archived': False
            }

            try:
                supabase.table('worldviews').insert(child_data).execute()
                print(f"  {i}. {child.get('title', '')[:60]}... ✓")
            except Exception as e:
                print(f"  {i}. ❌ 실패: {str(e)[:50]}")

        print()
        print(f"✅ {len(children)}개 하위 세계관 삽입 완료")
        print()

    print("=" * 80)
    print("전체 작업 완료")
    print("=" * 80)
    print()
    print("다음 단계:")
    print("1. Dashboard에서 계층 구조 확인")
    print("2. mechanism_matcher로 perception 재연결 (필요시)")
    print()


if __name__ == '__main__':
    main()
