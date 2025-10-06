"""
전체 파이프라인 재실행 - 81개 글로 제대로 분석
"""
import asyncio
from engines.utils.supabase_client import get_supabase
from engines.extractors.perception_extractor import PerceptionExtractor
from engines.analyzers.simple_worldview_detector import SimpleWorldviewDetector
from engines.deconstructors.deconstruction_engine import DeconstructionEngine

async def main():
    supabase = get_supabase()

    print('=' * 80)
    print('전체 파이프라인 재실행 (81개 본문 있는 글)')
    print('=' * 80)

    # Clean old data
    print('\n[Step 1] 기존 분석 데이터 삭제...')
    supabase.table('worldviews').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    supabase.table('perceptions').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print('✅ 삭제 완료')

    # Get all contents
    print('\n[Step 2] Contents 조회...')
    contents = supabase.table('contents').select('id').execute()
    content_ids = [c['id'] for c in contents.data]
    print(f'✅ {len(content_ids)}개 contents')

    # Extract perceptions
    print('\n[Step 3] Perception 추출...')
    extractor = PerceptionExtractor()

    all_perception_ids = []
    for i, content_id in enumerate(content_ids, 1):
        if i % 10 == 0:
            print(f'  진행: {i}/{len(content_ids)}')

        perception_ids = await extractor.extract(content_id)
        all_perception_ids.extend(perception_ids)

    print(f'✅ 총 {len(all_perception_ids)}개 perceptions 생성')

    # Detect worldviews
    print('\n[Step 4] Worldview 탐지...')
    detector = SimpleWorldviewDetector()
    worldview_ids = await detector.detect_worldviews()
    print(f'✅ {len(worldview_ids)}개 worldviews 탐지')

    # Show worldviews
    for wv_id in worldview_ids:
        wv = supabase.table('worldviews').select('title, frame, total_perceptions').eq('id', str(wv_id)).execute()
        if wv.data:
            w = wv.data[0]
            print(f"  - {w['title']}")
            print(f"    Frame: {w['frame']}")
            print(f"    Perceptions: {w['total_perceptions']}개")

    # Deconstruction
    print('\n[Step 5] Deconstruction 실행...')
    engine = DeconstructionEngine()

    for i, wv_id in enumerate(worldview_ids, 1):
        wv = supabase.table('worldviews').select('title').eq('id', str(wv_id)).execute()
        title = wv.data[0]['title'] if wv.data else 'Unknown'

        print(f'  [{i}/{len(worldview_ids)}] {title}...')
        result = await engine.deconstruct(str(wv_id), save_to_db=True)
        flaws_count = len(result.get('flaws', []))
        narrative_len = len(result.get('counter_narrative', ''))
        print(f'    ✅ {flaws_count}개 결함, {narrative_len}자 대안 서사')

    print('\n' + '=' * 80)
    print('✅ 완료!')
    print('=' * 80)

    # Final stats
    final_perceptions = supabase.table('perceptions').select('id', count='exact').execute()
    final_worldviews = supabase.table('worldviews').select('id', count='exact').execute()

    print(f'\n최종 통계:')
    print(f'  - Contents: {len(content_ids)}개')
    print(f'  - Perceptions: {final_perceptions.count}개')
    print(f'  - Worldviews: {final_worldviews.count}개')

if __name__ == '__main__':
    asyncio.run(main())
